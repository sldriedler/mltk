/* Copyright 2018 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/
#include <algorithm>


#include "tensorflow/lite/micro/examples/micro_speech/feature_provider.h"

#include "tensorflow/lite/micro/examples/micro_speech/audio_provider.h"
#include "tensorflow/lite/micro/examples/micro_speech/micro_features/micro_features_generator.h"
#include "micro_model_settings.hpp"
#include "cli_opts.hpp"


static int32_t previous_time_ms = 0;




static void dump_spectrogram(const int8_t* feature_buffer);



FeatureProvider::FeatureProvider(int feature_size, int8_t* feature_data)
    : feature_size_(feature_size),
      feature_data_(feature_data),
      is_first_run_(true) {
  // Initialize the feature data to default values.
  for (int n = 0; n < feature_size_; ++n) {
    feature_data_[n] = 0;
  }
}

FeatureProvider::~FeatureProvider() {}

TfLiteStatus FeatureProvider::PopulateFeatureData(
    tflite::ErrorReporter* error_reporter, int32_t unused,
    int32_t time_in_ms, int* how_many_new_slices) {

  *how_many_new_slices = 0;

  if (feature_size_ != kFeatureElementCount) {
    TF_LITE_REPORT_ERROR(error_reporter,
                         "Requested feature_data_ size %d doesn't match %d",
                         feature_size_, kFeatureElementCount);
    return kTfLiteError;
  }


  // If this is the first call, then initialize the micro feature generator
  if (is_first_run_) {
    TfLiteStatus init_status = InitializeMicroFeatures(error_reporter);
    if (init_status != kTfLiteOk) {
      return init_status;
    }

    // Also initialize the the microfrontend by supplying it
    // with a window's duration of zero-initialized audio.
    // This way, all subsequent processing just needs to process
    // kFeatureSliceStrideMs chunks of audio.
    size_t num_samples_read;
    const int window_size = (kFeatureSliceDurationMs * kAudioSampleFrequency) / 1000;
    int16_t dummy_audio[window_size];
    memset(dummy_audio, 0, window_size*sizeof(int16_t));
    GenerateMicroFeatures(
      error_reporter, 
      dummy_audio, 
      window_size, 
      kFeatureSliceSize,
      feature_data_, 
      &num_samples_read
    );

    previous_time_ms = time_in_ms;
    is_first_run_ = false;
    return kTfLiteOk;
  }


   // Ensure we have at least two step's worth of audio beforing processing
  if(time_in_ms - previous_time_ms < kFeatureSliceStrideMs*2)
  {
     return kTfLiteOk;
  }

  // Quantize the time into steps as long as each window stride, so we can
  // figure out which audio data we need to fetch.
  const int last_step = (previous_time_ms / kFeatureSliceStrideMs);
  const int current_step = (time_in_ms / kFeatureSliceStrideMs)-1; // -1 to round-down

  int slices_needed = current_step - last_step;

  // Don't read more than a spectrograms's worth of slices
  if (slices_needed > kFeatureSliceCount) {
    slices_needed = kFeatureSliceCount;
  }

  const int slices_to_keep = kFeatureSliceCount - slices_needed;
  const int slices_to_drop = kFeatureSliceCount - slices_to_keep;
  // If we can avoid recalculating some slices, just move the existing data
  // up in the spectrogram, to perform something like this:
  // last time = 80ms          current time = 120ms
  // +-----------+             +-----------+
  // | data@20ms |         --> | data@60ms |
  // +-----------+       --    +-----------+
  // | data@40ms |     --  --> | data@80ms |
  // +-----------+   --  --    +-----------+
  // | data@60ms | --  --      |  <empty>  |
  // +-----------+   --        +-----------+
  // | data@80ms | --          |  <empty>  |
  // +-----------+             +-----------+
  if (slices_to_keep > 0) {
    for (int dest_slice = 0; dest_slice < slices_to_keep; ++dest_slice) {
      int8_t* dest_slice_data =
          feature_data_ + (dest_slice * kFeatureSliceSize);
      const int src_slice = dest_slice + slices_to_drop;
      const int8_t* src_slice_data =
          feature_data_ + (src_slice * kFeatureSliceSize);
      for (int i = 0; i < kFeatureSliceSize; ++i) {
        dest_slice_data[i] = src_slice_data[i];
      }
    }
  }
  // Any slices that need to be filled in with feature data have their
  // appropriate audio data pulled, and features calculated for that slice.
  if (slices_needed > 0) 
  {
    int32_t current_time_ms = previous_time_ms;
    int8_t* new_slice_data = feature_data_ + (slices_to_keep * kFeatureSliceSize);

    // Process the required slices to generate the spectrogram
    for(int new_slice = 0; new_slice < slices_needed; ++new_slice, new_slice_data += kFeatureSliceSize) 
    {
      int16_t* audio_samples = nullptr;
      int audio_samples_size = 0;
      size_t num_samples_read;
  
      // Read a window step's worth of audio
      GetAudioSamples(
        error_reporter, 
        current_time_ms,
        kFeatureSliceStrideMs, 
        &audio_samples_size,
        &audio_samples
      );

      // Convert the audio into a feature "slice"
      // which is effectively a list of frequencies found in the audio
      TfLiteStatus generate_status = GenerateMicroFeatures(
        error_reporter, 
        audio_samples, 
        audio_samples_size, 
        kFeatureSliceSize,
        new_slice_data, 
        &num_samples_read
      );
      assert(num_samples_read == (kFeatureSliceStrideMs * kAudioSampleFrequency)/1000);

      // Increment the current time by the amount of audio samples processed
      current_time_ms += kFeatureSliceStrideMs;
    }

    // At this point:
    // current_time_ms = next position in audio buffer of unprocessed data
    // Store the time so that we begin processing at this point in the audio buffer
    // the next time PopulateFeatureData() is called.
    previous_time_ms = current_time_ms;


    // Wait until we have a complete spectrogram of slices
    // before we continue to the inference stage
    if(current_step >= kFeatureSliceCount)
    {
      *how_many_new_slices = slices_needed;
    }
  }

  if(cli_opts.dump_spectrograms && *how_many_new_slices > 0)
  {
    dump_spectrogram(feature_data_);
  }

  return kTfLiteOk;
}





#ifdef __arm__

#include "jlink_stream/jlink_stream.hpp"

static bool registered_spectrogram_stream = false;


static void dump_spectrogram(const int8_t* feature_buffer)
{
  if(!registered_spectrogram_stream)
  {
    registered_spectrogram_stream = true;
    if(jlink_stream::register_stream("spec_dump", jlink_stream::Write))
    {
      MLTK_DEBUG("Registered spec_dump stream");
    }
    else
    {
      MLTK_ERROR("Failed to register spectrogram dump stream");
    }
  }

  jlink_stream::write_all("spec_dump", "SPEC", 4);
  jlink_stream::write_all("spec_dump", feature_buffer, kFeatureElementCount);
}

#else // __arm__

#include <cstdlib>
#include <cstdio>

static int spectrogram_counter = 0;


static void dump_spectrogram(const int8_t* feature_buffer)
{
  const char* spectrogram_dir = cli_opts.dump_spectrograms_dir.c_str();
  if(spectrogram_dir == nullptr)
  {
    return;
  }
  char path[1024];
  snprintf(path, sizeof(path), "%s/%d.int8.npy.txt", spectrogram_dir, spectrogram_counter++);
  auto spectrogram_fp = fopen(path, "wb");
  if(spectrogram_fp != nullptr)
  {
    const int8_t* ptr = feature_buffer;
    for(int r = 0; r < kFeatureSliceCount; ++r)
    {
      for(int c = 0; c < kFeatureSliceSize; ++c)
      {
        char tmp[64];
        int l = sprintf(tmp, "%d,", *ptr++);
        if(c == kFeatureSliceSize-1)
        {
          tmp[l-1] = '\n';
        }
        fwrite(tmp, 1, l, spectrogram_fp);
      }
    }
    fclose(spectrogram_fp);
  }
}

#endif // __arm__