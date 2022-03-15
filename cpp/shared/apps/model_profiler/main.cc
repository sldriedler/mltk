#include <cstdio>

#include "platform_api.h"

#include "cpputils/heap.hpp"
#include "cpputils/string.hpp"
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tflite_micro_model/tflite_micro_model.hpp"
#include "tflite_micro_model/tflite_micro_utils.hpp"


#include "model_profiler_generated_model.tflite.h"


using namespace mltk;


tflite::AllOpsResolver op_resolver;



extern "C" int main( int argc, char* argv[])
{
    auto& logger = get_logger();
    logger.flags(logging::Newline);

    logger.info("Starting Model Profiler");

    // Register the accelerator if the TFLM lib was built with one
    mltk_tflite_micro_register_accelerator();

#ifdef MLTK_RUN_MODEL_FROM_RAM
    uint8_t* tflite_buffer = (uint8_t*)HEAP_MALLOC(sizeof(MODEL_DATA));
    if(tflite_buffer == nullptr)
    {
        logger.error("Cannot load .tflite into RAM. Failed to allocate %d bytes for buffer", sizeof(MODEL_DATA));
        return -1;
    }
    memcpy(tflite_buffer, MODEL_DATA, sizeof(MODEL_DATA));
    logger.info("Loaded .tflite into RAM");
#else 
    const uint8_t* tflite_buffer = MODEL_DATA;
#endif // MLTK_RUN_MODEL_FROM_RAM

    uint32_t tensor_arena_size = get_tensor_arena_size(tflite_buffer, &logger);
    uint8_t* tensor_arena = (uint8_t*)HEAP_MALLOC(tensor_arena_size);
    if(tensor_arena == nullptr)
    {
        logger.error("Failed to allocate tensor arena of size: %d", tensor_arena_size);
        return -1;
    }
#ifndef __arm__
    // For non-embedded, malloc() a large buffer to ensure the model fits
    // We still keep the HEAP_MALLOC() above so the heap stats are consistent with embedded
    tensor_arena_size = 4*1024*1024;
    tensor_arena = (uint8_t*)malloc(tensor_arena_size);
#endif

    TfliteMicroModel model;

    model.enable_profiler();
#ifdef TFLITE_MICRO_RECORDER_ENABLED
    model.enable_recorder();
#endif

    if(!model.load(
        tflite_buffer, op_resolver,
        tensor_arena, tensor_arena_size
    ))
    {
        logger.error("Failed to load model");
        return -1;
    }

    HeapStats heap_stats;
    heap_get_stats(&heap_stats);
    logger.info("Heap usage: %sB", cpputils::format_units(heap_stats.used));


    model.print_summary(&logger);

    auto profiler = model.profiler();
    profiling::print_metrics(profiler, &logger);

    if(!model.invoke())
    {
        logger.error("Failed to run inference");
        return -1;
    }

    profiling::print_stats(profiler, &logger);

#ifdef TFLITE_MICRO_RECORDER_ENABLED
    logger.info("Recording results:");
    auto& recorded_data = model.recorded_data();
    int layer_idx = 0;
    for(auto& layer : recorded_data)
    {
        logger.info("Layer %d:", layer_idx);
        logger.info("  Input sizes (bytes):");
        for(auto& input : layer.inputs)
        {
            logger.info("    %d", input.length);
        }
        logger.info("  Output sizes (bytes):", layer_idx);
        for(auto& output : layer.outputs)
        {
            logger.info("    %d", output.length);
        }
        ++layer_idx;
    }
    recorded_data.clear();
#endif
    

    logger.info("done");

    return 0;
}
