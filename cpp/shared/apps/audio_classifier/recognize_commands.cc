/* Copyright 2017 The TensorFlow Authors. All Rights Reserved.

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

#include "recognize_commands.hpp"
#include "micro_model_settings.hpp"
#include "mltk_tflite_micro_helper.hpp"
#include "micro_model_settings.hpp"
#include "cli_opts.hpp"

#include <limits>


static bool printed_verbose_header = false;
static int prev_time_ms = 0;



RecognizeCommands::RecognizeCommands(tflite::ErrorReporter* error_reporter,
                                     int32_t average_window_duration_ms,
                                     uint8_t detection_threshold,
                                     int32_t suppression_ms,
                                     int32_t minimum_count)
    : error_reporter_(error_reporter),
      average_window_duration_ms_(average_window_duration_ms),
      detection_threshold_(detection_threshold),
      suppression_ms_(suppression_ms),
      minimum_count_(minimum_count),
      previous_results_(error_reporter) {
  previous_top_label_ = "silence";
  previous_top_label_time_ = 0;

  MLTK_INFO("\nClassifier settings:");
  MLTK_INFO("average_window_duration_ms = %dms", average_window_duration_ms);
  MLTK_INFO("detection_threshold = %d of 255", detection_threshold);
  MLTK_INFO("suppression_ms = %dms", suppression_ms);
  MLTK_INFO("minimum_count = %d", minimum_count);
  MLTK_INFO("sensitivity = %f", cli_opts.sensitivity);
}

TfLiteStatus RecognizeCommands::ProcessLatestResults(
    const TfLiteTensor* latest_results, const int32_t current_time_ms,
    const char** found_command, uint8_t* score, bool* is_new_command) {
  auto& logger = mltk::get_logger();

  if ((latest_results->dims->size != 2) ||
      (latest_results->dims->data[0] != 1) ||
      (latest_results->dims->data[1] != kCategoryCount)) {
    TF_LITE_REPORT_ERROR(
        error_reporter_,
        "The results for recognition should contain %d elements, but there are "
        "%d in an %d-dimensional shape",
        kCategoryCount, latest_results->dims->data[1],
        latest_results->dims->size);
    return kTfLiteError;
  }

  if (latest_results->type != kTfLiteInt8) {
    TF_LITE_REPORT_ERROR(
        error_reporter_,
        "The results for recognition should be int8_t elements, but are %d",
        latest_results->type);
    return kTfLiteError;
  }

  if ((!previous_results_.empty()) &&
      (current_time_ms < previous_results_.front().time_)) {
    TF_LITE_REPORT_ERROR(
        error_reporter_,
        "Results must be fed in increasing time order, but received a "
        "timestamp of %d that was earlier than the previous one of %d",
        current_time_ms, previous_results_.front().time_);
    return kTfLiteError;
  }

  // Add the latest results to the head of the queue.
  previous_results_.push_back({current_time_ms, latest_results->data.int8});

  // Prune any earlier results that are too old for the averaging window.
  const int64_t time_limit = current_time_ms - average_window_duration_ms_;
  while ((!previous_results_.empty()) &&
         previous_results_.front().time_ < time_limit) {
    previous_results_.pop_front();
  }

  // If there are too few results, assume the result will be unreliable and
  // bail.
  const int64_t how_many_results = previous_results_.size();
  const int64_t earliest_time = previous_results_.front().time_;
  const int64_t samples_duration = current_time_ms - earliest_time;
  if ((how_many_results < minimum_count_) ||
      (samples_duration < (average_window_duration_ms_ / 4))) {
    *found_command = previous_top_label_;
    *score = 0;
    *is_new_command = false;
    int diff = current_time_ms - prev_time_ms;
    prev_time_ms = current_time_ms;
    if(current_time_ms > 8000)
    {
      logger.debug("[%9d] (%7d) Sample underflow, adjust --window, --count or use a smaller ML model", current_time_ms, diff);
    }
    return kTfLiteOk;
  }

  // Calculate the average score across all the results in the window.
  int32_t average_scores[kCategoryCount];
  for (int offset = 0; offset < previous_results_.size(); ++offset) {
    PreviousResultsQueue::Result previous_result =
        previous_results_.from_front(offset);
    const int8_t* scores = previous_result.scores;
    for (int i = 0; i < kCategoryCount; ++i) {
      if (offset == 0) {
        average_scores[i] = scores[i] + 128;
      } else {
        average_scores[i] += scores[i] + 128;
      }
    }
  }
  for (int i = 0; i < kCategoryCount; ++i) {
    average_scores[i] /= how_many_results;
  }

  // Find the current highest scoring category.
  int current_top_index = 0;
  int32_t current_top_score = 0;
  for (int i = 0; i < kCategoryCount; ++i) {
    if (average_scores[i] > current_top_score) {
      current_top_score = average_scores[i];
      current_top_index = i;
    }
  }
  const char* current_top_label = kCategoryLabels[current_top_index];

  // If we've recently had another label trigger, assume one that occurs too
  // soon afterwards is a bad result.
  int64_t time_since_last_top;
  // if ((previous_top_label_ == kCategoryLabels[0]) ||
  //     (previous_top_label_time_ == std::numeric_limits<int32_t>::min())) {
  //   time_since_last_top = std::numeric_limits<int32_t>::max();
  // } else {
    time_since_last_top = current_time_ms - previous_top_label_time_;
  //}
  if ((current_top_score > detection_threshold_) &&
      (current_top_label[0] != '_') &&
      (time_since_last_top > suppression_ms_)) {
    previous_top_label_ = current_top_label;
    previous_top_label_time_ = current_time_ms;
    *is_new_command = true;
  } else {
    *is_new_command = false;
  }

  if(logger.level() == logging::Debug)
  {
    char buffer[256];
    char *ptr;
    int diff = current_time_ms - prev_time_ms;
    prev_time_ms = current_time_ms;

    if(!printed_verbose_header)
    {
      printed_verbose_header = true;
      ptr = buffer;
      ptr += sprintf(ptr, "[Timestamp] (latency) ");
      for(auto cls : model_instance.details().classes())
      {
        ptr += sprintf(ptr, "%s ", cls);
      }
      logger.write_buffer(logging::Debug, buffer, ptr - buffer);
    }

    ptr = buffer;
    ptr += sprintf(ptr, "[%9d] (%7d) ", current_time_ms, diff);
    for (int i = 0; i < kCategoryCount; ++i) {
      ptr += sprintf(ptr, "%3d ", average_scores[i]);
    }
    logger.write_buffer(logging::Debug, buffer, ptr - buffer);
  }

  *found_command = current_top_label;
  *score = current_top_score;

  return kTfLiteOk;
}
