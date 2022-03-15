#pragma once

#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tflite_micro_model/tflite_micro_model.hpp"
#include "microfrontend/lib/frontend_util.h"


extern int kAudioSampleFrequency;
extern int kAudioSampleLengthMs;
extern int kFeatureElementCount;
extern int kFeatureSliceStrideMs;
extern int kFeatureSliceCount;
extern int kFeatureSliceSize;
extern int kFeatureSliceDurationMs;
extern int kFeatureSliceDurationSampleCount;
extern int kCategoryCount;
extern mltk::StringList kCategoryLabels;
extern FrontendConfig kFrontendConfig;


TfLiteStatus InitializeMicroModelSettings(const mltk::TfliteMicroModel* model);

extern mltk::TfliteMicroModel model_instance;