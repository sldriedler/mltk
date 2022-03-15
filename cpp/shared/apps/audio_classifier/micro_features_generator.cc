/* Copyright 2019 The TensorFlow Authors. All Rights Reserved.

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

#include "tensorflow/lite/micro/examples/micro_speech/micro_features/micro_features_generator.h"

#include <cmath>
#include <cstring>

#include "microfrontend/lib/frontend.h"
#include "microfrontend/lib/frontend_util.h"
#include "micro_model_settings.hpp"

// Configure FFT to output 16 bit fixed point.
#define FIXED_POINT 16
// Feature range min and max, used for determining valid range to quantize from
#define SL_ML_AUDIO_FEATURE_GENERATION_QUANTIZE_FEATURE_RANGE_MIN      0
#define SL_ML_AUDIO_FEATURE_GENERATION_QUANTIZE_FEATURE_RANGE_MAX      666    



namespace {

FrontendState g_micro_features_state;
bool g_is_first_time = true;

}  // namespace


TfLiteStatus InitializeMicroFeatures(tflite::ErrorReporter* error_reporter) {
  
  if (!FrontendPopulateState(&kFrontendConfig, &g_micro_features_state,
                             kAudioSampleFrequency)) {
    TF_LITE_REPORT_ERROR(error_reporter, "FrontendPopulateState() failed");
    return kTfLiteError;
  }
  g_is_first_time = true;
  return kTfLiteOk;
}

// This is not exposed in any header, and is only used for testing, to ensure
// that the state is correctly set up before generating results.
void SetMicroFeaturesNoiseEstimates(const uint32_t* estimate_presets) {
  for (int i = 0; i < g_micro_features_state.filterbank.num_channels; ++i) {
    g_micro_features_state.noise_reduction.estimate[i] = estimate_presets[i];
  }
}

TfLiteStatus GenerateMicroFeatures(tflite::ErrorReporter* error_reporter,
                                   const int16_t* input, int input_size,
                                   int output_size, int8_t* output,
                                   size_t* num_samples_read) {
  //const int16_t* frontend_input;
  // if (g_is_first_time) {
  //   frontend_input = input;
  //   g_is_first_time = false;
  // } else {
  //   frontend_input = input + 160;
  // }
  FrontendOutput frontend_output = FrontendProcessSamples(
      &g_micro_features_state, input, input_size, num_samples_read);
  if(frontend_output.size == 0)
  {
    return kTfLiteError;
  }

  for (size_t i = 0; i < frontend_output.size; ++i) {
    // This was taken from the GSDK Audio Feature Generator:
    // sli_ml_audio_feature_generation_get_features_quantized()
    const int32_t value_scale = 256; 
    const uint16_t range_min = SL_ML_AUDIO_FEATURE_GENERATION_QUANTIZE_FEATURE_RANGE_MIN;
    const uint16_t range_max = SL_ML_AUDIO_FEATURE_GENERATION_QUANTIZE_FEATURE_RANGE_MAX;
    const int32_t value_div = range_max - range_min;
    int32_t value = (((frontend_output.values[i] - range_min) * value_scale) + (value_div / 2))
                    / value_div;
    value -= 128;
    if (value < -128) {
      value = -128;
    }
    if (value > 127) {
      value = 127;
    }
    output[i] = (int8_t)value;
  }

  return kTfLiteOk;
}
