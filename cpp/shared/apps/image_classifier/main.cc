#include <stdio.h>

#include "platform_api.h"
#include "cpputils/heap.hpp"
#include "cpputils/string.hpp"
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tflite_micro_model/tflite_micro_model.hpp"
#include "tflite_micro_model/tflite_micro_utils.hpp"
#include "arducam/arducam.h"

#include "jlink_stream/jlink_stream.hpp"

#include "image_classifier_generated_model.tflite.h"


using namespace mltk;


static tflite::AllOpsResolver op_resolver;
static TfliteMicroModel model;
static logging::Logger* logger = nullptr;


static bool dump_image(const TfliteTensorView* img_tensor, const uint8_t* image_data, uint32_t image_length, arducam_data_format_t data_format);
static void print_classification_result(const TfliteTensorView* output_tensor);


/*************************************************************************************************/
extern "C" int main( int argc, char* argv[])
{
    sl_status_t status;
    TfliteModelParameters model_parameters;
    float img_scaler = 0;
    bool normalize_mean_std = false;

    logger = &get_logger();
    logger->flags(logging::Newline);
    logger->level(logging::Debug);

    logger->info("Starting Image Classifier");

    // Attempt to retrieve the model parameters from the .tflite flatbuffer
    if(!TfliteMicroModel::get_model_parameters_in_flatbuffer(MODEL_DATA, model_parameters))
    {
        logger->warn("No model parameters found in flatbuffer");
    }
    else 
    {
        model_parameters.get("samplewise_norm.rescale", img_scaler);
        if(img_scaler != 0)
        {
            logger->info("Image data scaler = %f", img_scaler);
        }
        model_parameters.get("samplewise_norm.mean_and_std", normalize_mean_std);
        if(normalize_mean_std)
        {
            logger->info("Using samplewise mean & STD normalization");
        }
    }

    uint32_t tensor_arena_size = get_tensor_arena_size(MODEL_DATA, logger);
    uint8_t* tensor_arena = (uint8_t*)HEAP_MALLOC(tensor_arena_size);
    if(tensor_arena == nullptr)
    {
        logger->error("Failed to allocate tensor arena of size: %d", tensor_arena_size);
        return -1;
    }
#ifndef __arm__
    // For non-embedded, malloc() a large buffer to ensure the model fits
    // We still keep the HEAP_MALLOC() above so the heap stats are consistent with embedded
    tensor_arena_size = 4*1024*1024;
    tensor_arena = (uint8_t*)malloc(tensor_arena_size);
#endif

    // This is for debugging
    // It allows for retrieving the image via Python script
    if(jlink_stream::register_stream("image", jlink_stream::Write))
    {
        logger->error("Registered image stream");
    }

    // Register the accelerator if the TFLM lib was built with one
    mltk_tflite_micro_register_accelerator();


    if(!model.load(
        MODEL_DATA, op_resolver,
        tensor_arena, tensor_arena_size
    ))
    {
        logger->error("Failed to load model");
        return -1;
    }

    model.print_summary(logger);

    // Retrieve the input tensor's size so we can determine how large of a image buffer to allocate
    TfliteTensorView* input_tensor = model.input(0);
    const auto input_size = input_tensor->shape().flat_size();
    const TfliteTensorView* output_tensor = model.output(0);

    if(img_scaler != 0 || normalize_mean_std)
    {
        if(input_tensor->type != kTfLiteFloat32)
        {
            logger->error("If using image scaling or samplewise mean/STD normalization, then the model input type must be float32");
            return -1;
        }
    }


    // Initialize the camera
    arducam_config_t cam_config = ARDUCAM_DEFAULT_CONFIG;
    cam_config.image_resolution.width = input_tensor->dims->data[2];
    cam_config.image_resolution.height = input_tensor->dims->data[1];
    cam_config.data_format = input_tensor->dims->data[3] == 1 ? ARDUCAM_DATA_FORMAT_GRAYSCALE : ARDUCAM_DATA_FORMAT_RGB888;
   
    // Calculate the size required to buffer an image
    // NOTE: The buffer size may be different than the image size
    const uint32_t length_per_image = arducam_calculate_image_buffer_length(
        cam_config.data_format, 
        cam_config.image_resolution.width, 
        cam_config.image_resolution.height
    );

    // Allocate a "ping-pong" buffer (i.e. 2) for the image
    const uint32_t image_buffer_count = 2;
    const uint32_t image_buffer_length = length_per_image*image_buffer_count;
    uint8_t* image_buffer = (uint8_t*)HEAP_MALLOC(image_buffer_length);
    if(image_buffer == nullptr)
    {
        logger->error("Failed to allocate camera buffer, size: %d", image_buffer_length);
        return -1;
    }

    // Initialize the camera
    status = arducam_init(&cam_config, image_buffer, image_buffer_length);
    if(status != SL_STATUS_OK)
    {
        logger->error("Failed to initialize the camera, err: %u", status);
        return -1;
    }


    HeapStats heap_stats;
    heap_get_stats(&heap_stats);
    logger->info("Heap usage: %sB", cpputils::format_units(heap_stats.used));

    // Start the image capturing DMA background
    status = arducam_start_capture();
    if(status != SL_STATUS_OK)
    {
        logger->error("Failed to start camera capture, err: %u", status);
        return -1;
    }


    logger->info("Image loop starting ...");
    for(;;)
    {
        uint8_t* image_data;
        uint32_t image_size;

        status = arducam_get_next_image(&image_data, &image_size);
        if(status == SL_STATUS_IN_PROGRESS)
        {
            // NOTE: Unfortunately, the camera doesn't not have a way to interrupt the MCU
            //       once an image is ready. So we must periodically poll the camera to check
            //       its status. This can be done by continuously calling arducam_get_next_image()
            //       OR arducam_poll() from a timer interrupt handler.
            continue;
        }
        else if(status != SL_STATUS_OK)
        {
          logger->error("Failed to retrieve image, err: %u", status);
          break;
        }

        // Scale the image, e.g. img_float32 = img_uint8 * scaler
        // If specified by the model's parameters 
        if(img_scaler != 0)
        {
            scale_tensor(img_scaler, image_data, input_tensor->data.f, image_size);
        }
        // Normalize the image, e.g. img_norm = (img - mean(img)) / std(img)
        // If specified by the model's parameters 
        else if(normalize_mean_std)
        {
            samplewise_mean_std_tensor(image_data, input_tensor->data.f, image_size);
        }
        else
        {
            // Otherwise, a buffer was allocated from the TFLM tensor arena
            // so we must copy from the image buffer into the allocated tensor buffer
            memcpy(input_tensor->data.uint8, image_data, image_size);
            //logger->dump_hex(image_data, image_size, "image");
        }

        // Dump the image if a Python script is connected
        dump_image(input_tensor, image_data, image_size, cam_config.data_format);

        // Release the image now that it has been copied to the input tensor
        arducam_release_image();

        // Run inference with the new image
        // NOTE: If arducam_poll() is periodically called in an interrupt handler,
        //       then the next image should begin buffering in the background
        //       while we run inference on the current image
        if(!model.invoke())
        {
          logger->error("Failed to run inference");
          break;
        }

        // Print the results
        print_classification_result(output_tensor);
    }

    arducam_stop_capture();

    logger->info("done");

    return 0;
}


/*************************************************************************************************/
static void print_classification_result(const TfliteTensorView* output_tensor)
{
    char buffer[512];
    char*ptr = buffer;
    static uint32_t last_timestamp = 0;

    if(output_tensor->type == kTfLiteFloat32)
    {
        for(int i = 0; i < output_tensor->shape().flat_size(); i++)
        {
            ptr += sprintf(ptr, "%3.2f ", output_tensor->data.f[i]);
        }
    }
    else if(output_tensor->type == kTfLiteInt8)
    {
        for(int i = 0; i < output_tensor->shape().flat_size(); i++)
        {
            ptr += sprintf(ptr, "%4d ", output_tensor->data.int8[i]);
        }
    }
    else 
    {
        return;
    }

    uint32_t now = platform_get_timestamp_ms();
    uint32_t elapsed_time = now - last_timestamp;
    last_timestamp = now;

    logger->info("%6d (%4d): %s", now, elapsed_time, buffer);
}

/*************************************************************************************************/
static bool dump_image(const TfliteTensorView* img_tensor, const uint8_t* image_data, uint32_t image_length, arducam_data_format_t data_format)
{
    bool connected = false;

    // Check if the Python script has connected
    jlink_stream::is_connected("image", &connected);
    if(!connected)
    {
        return false;
    }

    const auto shape =  img_tensor->shape();
    uint8_t header[10];
    header[0] = (image_length >> 0) & 0xFF; // data_length
    header[1] = (image_length >> 8) & 0xFF;
    header[2] = (image_length >> 16) & 0xFF;
    header[3] = (image_length >> 24) & 0xFF;
    header[4] = (shape.dims[2] >> 0) & 0xFF; // width
    header[5] = (shape.dims[2] >> 8) & 0xFF;
    header[6] = (shape.dims[1] >> 0) & 0xFF; // height
    header[7] = (shape.dims[1] >> 8) & 0xFF;
    header[8] = shape.dims[3] & 0xFF;        // channels
    header[9] = (uint8_t)data_format;        // data format
    
    jlink_stream::write_all("image", header, sizeof(header));
    jlink_stream::write_all("image", image_data, image_length);

    return true;
}