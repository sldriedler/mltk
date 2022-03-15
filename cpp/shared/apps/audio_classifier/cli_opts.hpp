#pragma once 

#include <cstdint>
#include "logging/logging.hpp"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#ifndef __arm__
#include <string>
#endif

#ifdef VERBOSE
#define LOG_LEVEL Debug
#define LOG_LEVEL_PROVIDED true
#else 
#define LOG_LEVEL Info
#define LOG_LEVEL_PROVIDED false
#endif

#ifndef WINDOW_MS
#define WINDOW_MS 1000
#define WINDOW_MS_PROVIDED false
#else 
#define WINDOW_MS_PROVIDED true
#endif

#ifndef THRESHOLD
#define THRESHOLD 185
#define THRESHOLD_PROVIDED false 
#else 
#define THRESHOLD_PROVIDED true
#endif

#ifndef SUPPRESSION_MS
#define SUPPRESSION_MS 1500
#define SUPPRESSION_MS_PROVIDED false
#else 
#define SUPPRESSION_MS_PROVIDED true
#endif 

#ifndef COUNT
#define COUNT 3
#define COUNT_PROVIDED false
#else 
#define COUNT_PROVIDED true
#endif

#ifndef VOLUME_DB
#define VOLUME_DB 0
#define VOLUME_DB_PROVIDED false
#else 
#define VOLUME_DB_PROVIDED true
#endif

#ifndef LATENCY_MS
#ifdef __arm__
#define LATENCY_MS 0
#else 
#define LATENCY_MS 100
#endif
#define LATENCY_MS_PROVIDED false
#else 
#define LATENCY_MS_PROVIDED true
#endif

#ifndef SENSITIVITY
#define SENSITIVITY .5f
#define SENSITIVITY_PROVIDED false
#else 
#define SENSITIVITY_PROVIDED true
#endif


struct CliOpts
{
    logging::Level log_level = logging::Level::LOG_LEVEL;
    int32_t average_window_duration_ms = WINDOW_MS;
    uint8_t detection_threshold = THRESHOLD;
    int32_t suppression_ms = SUPPRESSION_MS;
    int32_t minimum_count = COUNT;
    int32_t simulated_latency_ms = LATENCY_MS;
    float volume_db = VOLUME_DB;
    float sensitivity = SENSITIVITY;
    const uint8_t* model_flatbuffer = nullptr;
    bool log_level_provided = LOG_LEVEL_PROVIDED;
    bool average_window_duration_ms_provided = WINDOW_MS_PROVIDED;
    bool detection_threshold_provided = THRESHOLD_PROVIDED;
    bool suppression_ms_provided = SUPPRESSION_MS_PROVIDED;
    bool minimum_count_provided = COUNT_PROVIDED;
    bool simulated_latency_ms_provided = LATENCY_MS_PROVIDED;
    bool volume_db_provided = VOLUME_DB_PROVIDED;
    bool sensitivity_provided = SENSITIVITY_PROVIDED;
    bool model_flatbuffer_provided = false;
    bool dump_audio = false;
    bool dump_spectrograms = false;

#ifndef __arm__
    std::string dump_audio_dir;
    std::string dump_spectrograms_dir;
#endif

#ifndef __arm__
    ~CliOpts();
#endif
};


extern CliOpts cli_opts;



#ifdef __arm__
#define parse_cli_opts(argc, argv)
#else
void parse_cli_opts(int argc, char* argv[]);
#endif
void simulate_loop_latency();
void dump_audio(tflite::ErrorReporter* error_reporter);