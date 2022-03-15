#include <cstdio>
#include <cstdlib>

#include "platform_api.h"
#include "tensorflow/lite/micro/examples/micro_speech/audio_provider.h"
#include "tensorflow/lite/micro/examples/micro_speech/command_responder.h"
#include "tensorflow/lite/micro/examples/micro_speech/feature_provider.h"
#include "recognize_commands.hpp"
#include "cpputils/heap.hpp"
#include "cpputils/string.hpp"

#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tflite_micro_model/tflite_micro_model.hpp"
#include "tflite_micro_model/tflite_micro_utils.hpp"
#include "micro_model_settings.hpp"
#include "cli_opts.hpp"
#include "audio_classifier_generated_model.tflite.h"


using namespace mltk;


static tflite::AllOpsResolver op_resolver;
static int8_t *feature_buffer = nullptr;

static TfliteMicroModel* model = nullptr;
static FeatureProvider* feature_provider = nullptr;
static RecognizeCommands* recognizer = nullptr;
static logging::Logger* logger = nullptr;
static int32_t previous_time = 0;

static bool init();
static bool load_command_recognizer();
static bool run_audio_loop();
static void print_ready_msg(tflite::ErrorReporter* error_reporter);
extern TfLiteStatus InitAudioRecording(tflite::ErrorReporter* error_reporter);

CliOpts cli_opts;
TfliteMicroModel model_instance;


/*************************************************************************************************/
extern "C" int main( int argc, char* argv[])
{
    // Parse the CLI options (if applicable)
    parse_cli_opts(argc, argv);

    logger = &get_logger();
    logger->flags(logging::Newline);

    logger->level(cli_opts.log_level);
    logger->info("Starting Audio Classifier");

    // If not model was given on the command-line
    // then use the default model
    if(cli_opts.model_flatbuffer == nullptr)
    {
      logger->info("Using default model");
      cli_opts.model_flatbuffer = MODEL_DATA;
    }


    uint32_t tensor_arena_size = get_tensor_arena_size(cli_opts.model_flatbuffer, logger);
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

    
    // Register the accelerator if the TFLM lib was built with one
    mltk_tflite_micro_register_accelerator();

    model = &model_instance;

    if(!model->load(
        cli_opts.model_flatbuffer, op_resolver,
        tensor_arena, tensor_arena_size
    ))
    {
        logger->error("Failed to load model");
        return -1;
    }

    // If no log level was given on the command-line
    // then update the log level if one was provided in model parameters
    if(!cli_opts.log_level_provided)
    {
      const char* model_log_level;
      if(model->parameters.get("log_level", model_log_level))
      {
         logger->level(model_log_level);
      }
    }

    model->print_summary(logger);

    if(InitializeMicroModelSettings(model) != kTfLiteOk)
    {
        logger->error("Failed to init model settings");
        return -1;
    }

    feature_buffer = static_cast<int8_t*>(malloc(kFeatureElementCount));
    if(feature_buffer == nullptr)
    {
        logger->error("Failed to malloc feature_buffer");
        return -1;
    }

    static FeatureProvider static_feature_provider(kFeatureElementCount,
                                                    feature_buffer);
    feature_provider = &static_feature_provider;


    // Retrieve the command recognizer parameters from the model if they exist
    // AND they weren't given on the command-line.
    // Otherwise, just use the defaults
    if(!cli_opts.average_window_duration_ms_provided)
    {
      model->parameters.get("average_window_duration_ms", cli_opts.average_window_duration_ms);
    }
    if(!cli_opts.detection_threshold_provided)
    {
      model->parameters.get("detection_threshold", cli_opts.detection_threshold);
    }
    if(!cli_opts.suppression_ms_provided)
    {
      model->parameters.get("suppression_ms", cli_opts.suppression_ms);
    }
    if(!cli_opts.minimum_count_provided)
    {
       model->parameters.get("minimum_count", cli_opts.minimum_count);
    }
    if(!cli_opts.volume_db_provided)
    {
      model->parameters.get("volume_db", cli_opts.volume_db);
    }
    if(!cli_opts.sensitivity_provided)
    {
      model->parameters.get("sensitivity", cli_opts.sensitivity);
    }
    if(!cli_opts.simulated_latency_ms_provided)
    {
      model->parameters.get("latency_ms", cli_opts.simulated_latency_ms);
    }
    if(!cli_opts.dump_audio)
    {
      model->parameters.get("dump_audio", cli_opts.dump_audio);
    }
    if(!cli_opts.dump_spectrograms)
    {
      model->parameters.get("dump_spectrograms", cli_opts.dump_spectrograms);
    }

    static RecognizeCommands static_recognizer(
      model->error_reporter(),
      cli_opts.average_window_duration_ms,
      cli_opts.detection_threshold,
      cli_opts.suppression_ms,
      cli_opts.minimum_count
    );
    recognizer = &static_recognizer;


    TfLiteStatus init_status = InitAudioRecording(model->error_reporter());
    if (init_status != kTfLiteOk) 
    {
      logger->error("Failed to initialize audio recording");
      return -1;
    }


    HeapStats heap_stats;
    heap_get_stats(&heap_stats);
    logger->info("Heap usage: %sB", cpputils::format_units(heap_stats.used));


    logger->info("Audio loop starting ...");
    for(;;)
    {
      // Run a single iteration of the audio loop
      if(!run_audio_loop())
      {
        return -1;
      }

      // If we're not on an embedded platform
      // then simulate the amount of time a loop iteration would take on an embedded platform.
      // This will give a better idea of how well the model is able to detect keywords.
      simulate_loop_latency();
    }
    

    logger->info("done");

    return 0;
}



/*************************************************************************************************/
bool run_audio_loop() 
{
  auto error_reporter = model->error_reporter();

  if(cli_opts.dump_audio)
  {
    dump_audio(error_reporter);
#ifdef __arm__
    print_ready_msg(error_reporter);
    // If this is an embedded build and
    // we're dumping audio then don't run any other parts of the audio loop
    return true;
#endif 
  }


  auto input_tensor = model->input(0);

  int8_t* model_input_buffer = input_tensor->data.int8;
  

  // Fetch the spectrogram for the current time.
  const int32_t current_time = LatestAudioTimestamp();
  int how_many_new_slices = 0;
  TfLiteStatus feature_status = feature_provider->PopulateFeatureData(
      error_reporter, previous_time, current_time, &how_many_new_slices);
  if (feature_status != kTfLiteOk) {
    TF_LITE_REPORT_ERROR(error_reporter, "Feature generation failed");
    return false;
  }
  previous_time = current_time;
  // If no new audio samples have been received since last time, don't bother
  // running the network model.
  if (how_many_new_slices == 0 ) {
    return true;
  }

  print_ready_msg(error_reporter);

#ifdef __arm__
  // If this is an embedded build and
  // we're dumping spectrograms, then don't run inference
  if(cli_opts.dump_spectrograms)
  {
    return true;
  }
#endif

  // Copy feature buffer to input tensor
  for (int i = 0; i < kFeatureElementCount; i++) {
    model_input_buffer[i] = feature_buffer[i];
  }

  // Run the model on the spectrogram input and make sure it succeeds.
  if (!model->invoke()) {
    TF_LITE_REPORT_ERROR(error_reporter, "Invoke failed");
    return false;
  }

  // Obtain a pointer to the output tensor
  TfLiteTensor* output = model->output(0);
  // Determine whether a command was recognized based on the output of inference
  const char* found_command = nullptr;
  uint8_t score = 0;
  bool is_new_command = false;
  TfLiteStatus process_status = recognizer->ProcessLatestResults(
      output, current_time, &found_command, &score, &is_new_command);
  if (process_status != kTfLiteOk) {
    TF_LITE_REPORT_ERROR(error_reporter,
                         "RecognizeCommands::ProcessLatestResults() failed");
    return false;
  }
  // Do something based on the recognized command. The default implementation
  // just prints to the error console, but you should replace this with your
  // own function for a real application.
  RespondToCommand(error_reporter, current_time, found_command, score,
                   is_new_command);

  return true;
}


static void print_ready_msg(tflite::ErrorReporter* error_reporter)
{
  static bool printed_ready_msg = false;

  if(!printed_ready_msg)
  {
    printed_ready_msg = true;
    TF_LITE_REPORT_ERROR(error_reporter, "Ready");
  }
}
