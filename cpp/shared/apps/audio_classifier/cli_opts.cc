
#include <string>
#include <cstdio>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>

#include "platform_api.h"
#include "cli_opts.hpp"
#include "mltk_tflite_micro_helper.hpp"



static uint32_t last_loop_time = 0;
static bool simuated_latency_initialized = false;
static int latency_overflow_count = 0;


#ifndef __arm__

#include "cxxopts.hpp"

/*************************************************************************************************/
void parse_cli_opts(int argc, char* argv[])
{
    cxxopts::Options options("Audio Classifier", "Classify streaming audio from a microphone using the given ML model");
    options.add_options()
        ("v,verbose", "Enable verbose logging")
        ("l,latency", "Number of ms to simulate per execution loo", cxxopts::value<uint32_t>())
        ("m,model", "Path to .tflite model file. Use built-in, default model if omitted", cxxopts::value<std::string>())
        ("w,window_duration", "Controls the smoothing. Longer durations (in milliseconds) will give a higher confidence that the results are correct, but may miss some commands", cxxopts::value<uint32_t>())
        ("c,count", "The minimum number of inference results to average when calcuating the detection value", cxxopts::value<uint32_t>())
        ("t,threshold", "Minumum model output threshold for a class to be considered detected, 0-255. Higher values increase precision at the cost of recall", cxxopts::value<uint32_t>())
        ("s,suppression", "Amount of milliseconds to wait after a keyword is detected before detecting new keywords", cxxopts::value<uint32_t>())
        ("d,volume", "Increase/decrease microphone audio in dB. 0 = no change, <0 decresae, >0 increase", cxxopts::value<float>())
        ("x,dump_audio", "Dump the raw audio samples to the given directory", cxxopts::value<std::string>())
        ("z,dump_spectrograms", "Dump the generated spectorgrams to the given directory", cxxopts::value<std::string>())
        ("i,sensitivity", "Sensitivity of the activity indicator", cxxopts::value<float>())
        ("h,help", "Print usage")
    ;

    try 
    {
        auto result = options.parse(argc, argv);

        if (result.count("help"))
        {
            std::cout << options.help() << std::endl;
            exit(0);
        }

        if(result.count("verbose"))
        {
            cli_opts.log_level = logging::Debug;
            cli_opts.log_level_provided = true;
        }

        if(result.count("latency"))
        {
            cli_opts.simulated_latency_ms = result["latency"].as<uint32_t>();
            cli_opts.simulated_latency_ms_provided = true;
            
        }

        if(result.count("model"))
        {
            const char* path = result["model"].as<std::string>().c_str();
            auto fp = fopen(path,"rb");
            if(fp == nullptr)
            {
                MLTK_ERROR("Failed to open model file: %s", path);
                exit(-1);
            }

            fseek(fp, 0, SEEK_END); 
            auto file_size = ftell(fp); 
            fseek(fp, 0, SEEK_SET); 
            auto buffer = malloc(file_size); 
            auto result = fread(buffer, 1, file_size, fp);
            fclose(fp);
            if(result != file_size)
            {
                MLTK_ERROR("Failed to read model file: %s", path);
                exit(-1);
            }

            cli_opts.model_flatbuffer = (uint8_t*)buffer;
            cli_opts.model_flatbuffer_provided = true;
        }

        if(result.count("window_duration"))
        {
            cli_opts.average_window_duration_ms = result["window_duration"].as<uint32_t>();
            cli_opts.average_window_duration_ms_provided = true;
        }

        if(result.count("count"))
        {
            cli_opts.minimum_count = result["count"].as<uint32_t>();
            cli_opts.minimum_count_provided = true;
        }

        if(result.count("suppression"))
        {
            cli_opts.suppression_ms = result["suppression"].as<uint32_t>();
            cli_opts.suppression_ms_provided = true;
        }

        if(result.count("threshold"))
        {
            cli_opts.detection_threshold = result["threshold"].as<uint32_t>();
            cli_opts.detection_threshold_provided = true;
        }

        if(result.count("volume"))
        {
            cli_opts.volume_db = result["volume"].as<float>();
            cli_opts.volume_db_provided = true;
        }

        if(result.count("sensitivity"))
        {
            cli_opts.sensitivity = result["sensitivity"].as<float>();
            cli_opts.sensitivity_provided = true;
        }

        if(result.count("dump_audio"))
        {
            cli_opts.dump_audio = true;
            cli_opts.dump_audio_dir = result["dump_audio"].as<std::string>();
        }

        if(result.count("dump_spectrograms"))
        {
            cli_opts.dump_spectrograms = true;
            cli_opts.dump_spectrograms_dir = result["dump_spectrograms"].as<std::string>();
        }

    } 
    catch(std::exception &e) 
    {
        std::cout << e.what() << std::endl;
        std::cout << options.help() << std::endl;
        exit(-1);
    }
}

/*************************************************************************************************/
CliOpts::~CliOpts()
{
    if(model_flatbuffer_provided)
    {
        free((void*)model_flatbuffer);
    }
}

#endif // __arm__


/*************************************************************************************************/
void simulate_loop_latency()
{
    if(cli_opts.simulated_latency_ms == 0)
    {
#ifndef __arm__
        // We need to sleep for a little bit on Windows/Linux
        // to avoid thread starvation
        platform_sleep_ms(5);
#endif
        return;
    }
    
    if(!simuated_latency_initialized)
    {
        simuated_latency_initialized = true;
        MLTK_INFO("Simulated loop latency: %dms", cli_opts.simulated_latency_ms);
        last_loop_time = platform_get_timestamp_ms();
        return;
    }

    const uint32_t now = platform_get_timestamp_ms();
    const uint32_t elapsed = now - last_loop_time;
    
    if(elapsed <= cli_opts.simulated_latency_ms)
    {
        latency_overflow_count = 0;
        const int32_t remaining = (cli_opts.simulated_latency_ms - elapsed) - 7;
        if(remaining > 0)
        {
            platform_sleep_ms(remaining);
        }
    }
    else
    {
        latency_overflow_count++;
        if(latency_overflow_count == 4)
        {
            MLTK_WARN("\n*** Simulated latency is %dms, but audio loop took %dms", cli_opts.simulated_latency_ms, elapsed);
            MLTK_WARN("This likely means the model is taking too long to execute on your PC\n");
        }
    }

    last_loop_time = platform_get_timestamp_ms();
}

