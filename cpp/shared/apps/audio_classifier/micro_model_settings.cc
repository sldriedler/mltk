
#include "mltk_tflite_micro_helper.hpp"
#include "micro_model_settings.hpp"


#define GET_PARAM(key, val) \
if(!model->parameters.get(key, val)) \
{ \
    MLTK_ERROR("Model parameter missing: %s", key); \
    return kTfLiteError; \
}
#define GET_INT(key, val) GET_PARAM(key, val); MLTK_INFO("%s = %d", key, val)
#define GET_FLOAT(key, val) GET_PARAM(key, val); MLTK_INFO("%s = %f", key, val)


int kAudioSampleFrequency = 0;
int kAudioSampleLengthMs = 0;
int kFeatureElementCount = 0;
int kFeatureSliceStrideMs = 0;
int kFeatureSliceCount = 0;
int kFeatureSliceSize = 0;
int kFeatureSliceDurationMs = 0;
int kFeatureSliceDurationSampleCount = 0;
int kCategoryCount = 0;
mltk::StringList kCategoryLabels;
FrontendConfig kFrontendConfig;


/*************************************************************************************************/
TfLiteStatus InitializeMicroModelSettings(const mltk::TfliteMicroModel* model)
{
    MLTK_INFO("\nAudioFeatureGenerator settings:");
    GET_INT("fe.sample_rate_hz", kAudioSampleFrequency);
    GET_INT("fe.window_step_ms", kFeatureSliceStrideMs);
    GET_INT("fe.window_size_ms", kFeatureSliceDurationMs);
    GET_INT("fe.filterbank_n_channels", kFeatureSliceSize);
    GET_INT("fe.sample_length_ms", kAudioSampleLengthMs);

    kFeatureSliceCount = ((kAudioSampleLengthMs - kFeatureSliceDurationMs) / kFeatureSliceStrideMs) + 1;
    kFeatureElementCount = kFeatureSliceSize * kFeatureSliceCount;
    kFeatureSliceDurationSampleCount = (kFeatureSliceDurationMs * kAudioSampleFrequency) / 1000;

    const int sample_count = (kAudioSampleFrequency * kFeatureSliceDurationMs) / 1000;
    // The size of the input time series data we pass to the FFT to produce the
    // frequency information. This has to be a power of two
    if(sample_count > 8192 || sample_count < 32)
    {
        MLTK_ERROR("Invalid sample count: %d", sample_count);
        return kTfLiteError;
    }

    if(!model->parameters.get("classes", kCategoryLabels))
    {
        MLTK_ERROR("Model parameter missing: classes");
        return kTfLiteError;
    }

    kCategoryCount = kCategoryLabels.size();

    kFrontendConfig.window.size_ms = kFeatureSliceDurationMs;
    kFrontendConfig.window.step_size_ms = kFeatureSliceStrideMs;
    kFrontendConfig.filterbank.num_channels = kFeatureSliceSize;
   
    GET_FLOAT("fe.filterbank_lower_band_limit", kFrontendConfig.filterbank.lower_band_limit);
    GET_FLOAT("fe.filterbank_upper_band_limit", kFrontendConfig.filterbank.upper_band_limit);
    GET_INT("fe.noise_reduction_enable", kFrontendConfig.noise_reduction.enable_noise_reduction);
    GET_INT("fe.noise_reduction_smoothing_bits", kFrontendConfig.noise_reduction.smoothing_bits);
    GET_FLOAT("fe.noise_reduction_even_smoothing", kFrontendConfig.noise_reduction.even_smoothing);
    GET_FLOAT("fe.noise_reduction_odd_smoothing", kFrontendConfig.noise_reduction.odd_smoothing);
    GET_FLOAT("fe.noise_reduction_min_signal_remaining", kFrontendConfig.noise_reduction.min_signal_remaining);
    GET_INT("fe.pcan_enable", kFrontendConfig.pcan_gain_control.enable_pcan);
    GET_FLOAT("fe.pcan_strength", kFrontendConfig.pcan_gain_control.strength);
    GET_FLOAT("fe.pcan_offset", kFrontendConfig.pcan_gain_control.offset);
    GET_INT("fe.pcan_gain_bits", kFrontendConfig.pcan_gain_control.gain_bits);
    GET_INT("fe.log_scale_enable", kFrontendConfig.log_scale.enable_log);
    GET_INT("fe.log_scale_shift", kFrontendConfig.log_scale.scale_shift);

    return kTfLiteOk;
}
