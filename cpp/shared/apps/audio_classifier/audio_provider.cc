/* 
Copyright 2019 The TensorFlow Authors. All Rights Reserved.
Copyright 2020 Silicon Laboratories Inc. www.silabs.com

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This file has been modified by Silicon Labs. 
==============================================================================*/

#include <algorithm>
#include <cstdlib>
#include <cstdint>
#include <cmath>

#include "tensorflow/lite/micro/examples/micro_speech/audio_provider.h"
#include "micro_model_settings.hpp"
#include "mltk_tflite_micro_helper.hpp"
#include "cli_opts.hpp"

#include "sl_mic.h"
#include "sl_status.h"



namespace {
  int16_t *g_audio_output_data;
  int16_t *g_mic_sample_data;
  const int16_t *g_mic_sample_end;
  float g_volume_scaler = 0;
  int32_t g_last_dumped_timestamp = 0;
   int32_t g_mic_sample_length_ms = 0;
  int32_t g_mic_sample_length = 0;
  int32_t g_audio_output_length = 0;
  int8_t g_n_channels = 1; // mono
  int g_init_status = -1;
}  // namespace


static int dump_audio_chunk(const int16_t* chunk, size_t length);
extern "C" uint32_t sl_mic_get_timestamp();



TfLiteStatus InitAudioRecording(tflite::ErrorReporter* error_reporter) {
  if(g_init_status != -1)
  {
    return (TfLiteStatus)g_init_status;
  }

  g_init_status = kTfLiteError;

  if(cli_opts.volume_db != 0)
  {
    g_volume_scaler = powf(10.0f, cli_opts.volume_db/20.0f);
  }
  MLTK_INFO("Volume: %.1fdB", cli_opts.volume_db);


  g_audio_output_length = kFeatureSliceDurationSampleCount * g_n_channels;
  g_audio_output_data = static_cast<int16_t*>(malloc(g_audio_output_length * sizeof(int16_t)));
  if(g_audio_output_data == nullptr)
  {
    MLTK_ERROR("Failed to malloc g_audio_output_data buffer (%d bytes)", g_audio_output_length * sizeof(int16_t));
    return kTfLiteError;
  }

  if(cli_opts.dump_audio || cli_opts.dump_spectrograms)
  {
    // If we're dumping audio or spectrograms then use a 1s buffer to help with stability
    // in transferring from the embedded device to the PC
    g_mic_sample_length_ms = 1000;
  }
  else
  {
    // Otherwise, just use a 500ms buffer to reduce memory usage
    g_mic_sample_length_ms = 500;
  }


  const int n_frames_per_sample = g_mic_sample_length_ms * (kAudioSampleFrequency / 1000);
  g_mic_sample_length = n_frames_per_sample * g_n_channels;
  g_mic_sample_data = static_cast<int16_t*>(malloc(g_mic_sample_length * sizeof(int16_t)));
  if(g_mic_sample_data == nullptr)
  {
    MLTK_ERROR("Failed to malloc g_mic_sample_data buffer (%d ms @ %sHz -> %d bytes)", g_mic_sample_length_ms, kAudioSampleFrequency, g_mic_sample_length*sizeof(int16_t));
    return kTfLiteError;
  }
  memset(g_mic_sample_data, 0, g_mic_sample_length*sizeof(int16_t));
  g_mic_sample_end = g_mic_sample_data + g_mic_sample_length;

  if(sl_mic_init(kAudioSampleFrequency, g_n_channels) != SL_STATUS_OK)
  {
    return kTfLiteError;
  }

  // The sl_mic library uses "ping-ponging" hence we divide by 2
  if(sl_mic_start_streaming(g_mic_sample_data, n_frames_per_sample/2, nullptr) != SL_STATUS_OK)
  {
    MLTK_ERROR("sl_mic_start_streaming() failed");
    return kTfLiteError;
  }

  // Wait a moment for the audio stream to initialize
  platform_sleep_ms(g_mic_sample_length_ms);

  g_last_dumped_timestamp = LatestAudioTimestamp();
  g_init_status = kTfLiteOk;

  return kTfLiteOk;
}

TfLiteStatus GetAudioSamples(tflite::ErrorReporter* error_reporter,
                             int start_ms, int duration_ms,
                             int* audio_samples_size, int16_t** audio_samples) {
  // This function copies duration_ms samples from the g_audio_capture buffer to the 
  // audio_output buffer.

  TfLiteStatus init_status = InitAudioRecording(error_reporter);
  if (init_status != kTfLiteOk) {
    return init_status;
  }

  // This should only be called when the main thread notices that the latest
  // audio sample data timestamp has changed, so that there's new data in the
  // capture ring buffer. The ring buffer will eventually wrap around and
  // overwrite the data, but the assumption is that the main thread is checking
  // often enough and the buffer is large enough that this call will be made
  // before that happens.

  const int duration_sample_count = std::min(kFeatureSliceDurationSampleCount, duration_ms * (kAudioSampleFrequency / 1000)); 
  int start_offset = start_ms * (kAudioSampleFrequency / 1000); 
  const int capture_index = (start_offset*g_n_channels) % g_mic_sample_length;

  // This code currently only supports a single channel
  assert(g_n_channels == 1);

  int16_t* dst = g_audio_output_data;
  const int16_t *src = &g_mic_sample_data[capture_index];
  for (int i = duration_sample_count; i > 0; --i) {
    if(g_volume_scaler == 0)
    {
      *dst++ = *src++;
    }
    else
    {
      const int32_t s_scaled = (int32_t)(*src++ * g_volume_scaler);
      *dst++ = std::min((int32_t)INT16_MAX, std::max((int32_t)INT16_MIN, s_scaled));
    }
    if(src >= g_mic_sample_end)
    {
      src = g_mic_sample_data;
    }
  }

  *audio_samples_size = duration_sample_count;
  *audio_samples = g_audio_output_data;

  return kTfLiteOk;
}

int32_t LatestAudioTimestamp() {
  return sl_mic_get_timestamp();
}





void dump_audio(tflite::ErrorReporter* error_reporter)
{
  if(InitAudioRecording(error_reporter) != kTfLiteOk)
  {
    return;
  }

  const int32_t audio_timestamp = LatestAudioTimestamp();
  const int32_t elapsed_time = audio_timestamp - g_last_dumped_timestamp;
  const int32_t start_offset = (g_last_dumped_timestamp * (kAudioSampleFrequency / 1000)) * g_n_channels;
  const int32_t end_offset = (audio_timestamp * (kAudioSampleFrequency / 1000)) * g_n_channels;
  int32_t start_index = start_offset % g_mic_sample_length;
  int32_t write_size = std::min(end_offset - start_offset, g_mic_sample_length);

  if(write_size == 0)
  {
    return;
  }
  if(elapsed_time > g_mic_sample_length_ms)
  {
    MLTK_WARN("Audio buffer overflow, elapsed time (%dms) > audio buffer size (%dms)", elapsed_time, g_mic_sample_length_ms);
  }

  int32_t total_written = 0;

  while(write_size > 0)
  {
    int32_t length_to_end = std::min(write_size, g_mic_sample_length - start_index);
    int length_written = dump_audio_chunk(&g_mic_sample_data[start_index], length_to_end);
    if(length_written == -1)
    {
      g_last_dumped_timestamp = audio_timestamp;
      break;
    }

    if(length_written == 0)
    {
      break;
    }
    total_written += length_written;
    start_index = (start_index + length_written) % g_mic_sample_length;
    write_size -= length_written;
  }

  g_last_dumped_timestamp += (total_written * 1000) / (kAudioSampleFrequency * g_n_channels);
}


#ifdef __arm__

#include "jlink_stream/jlink_stream.hpp"

static bool registered_audio_stream = false;
static bool client_connected = false;

static int dump_audio_chunk(const int16_t* chunk, size_t length)
{
  if(!registered_audio_stream)
  {
    registered_audio_stream = true;
    if(jlink_stream::register_stream("audio_dump", jlink_stream::Write))
    {
      MLTK_DEBUG("Registered audio_dump stream");
    }
    else
    {
      MLTK_ERROR("Failed to register audio dump stream");
    }
  }

  if(!client_connected)
  {
    jlink_stream::is_connected("audio_dump", &client_connected);
    if(!client_connected)
    {
      return -1;
    }
  }

  uint32_t bytes_written;
  jlink_stream::write("audio_dump", chunk, length*sizeof(int16_t), &bytes_written);
  return bytes_written / sizeof(int16_t);
}

#else // __arm__

#include <cstdlib>
#include <cstdio>

static int audio_counter = 0;


static int dump_audio_chunk(const int16_t* chunk, size_t length)
{
  char path[1024];
  const char* audio_dir = cli_opts.dump_audio_dir.c_str();
  if(audio_dir == nullptr)
  {
    return -1;
  }

  snprintf(path, sizeof(path), "%s/%d.int16.bin", audio_dir, audio_counter++);

  auto fp = fopen(path, "wb");
  if(fp != nullptr)
  {
    fwrite(chunk, sizeof(int16_t), length, fp);
    fclose(fp);
  }
  return length;
}

#endif // __arm__