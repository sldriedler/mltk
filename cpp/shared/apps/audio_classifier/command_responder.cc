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
#include <cmath>
#include "tensorflow/lite/micro/examples/micro_speech/command_responder.h"
#include "cli_opts.hpp"

#ifdef __arm__
#include "sl_led.h"
#include "sl_simple_led_instances.h"

#if SL_SIMPLE_LED_COUNT >= 1
#define red_led_on() sl_led_turn_on(&sl_led_led0)
#define red_led_off() sl_led_turn_off(&sl_led_led0)
#endif // SL_SIMPLE_LED_COUNT >= 1

#if SL_SIMPLE_LED_COUNT >= 2
#define green_led_off() sl_led_turn_off(&sl_led_led1)
#define green_led_toggle() sl_led_toggle(&sl_led_led1)
#endif // SL_SIMPLE_LED_COUNT >= 2
#endif // __arm__

#ifndef red_led_on
#define red_led_on() 
#define red_led_off()
#endif 

#ifndef green_led_off
#define green_led_off()
#define green_led_toggle()
#endif


static int32_t detected_timeout = 0;
static int32_t activity_timestamp = 0;
static int32_t activity_toggle_timestamp = 0;
static uint8_t previous_score = 0;
static int32_t previous_score_timestamp = 0;
static const char* previous_found_command = nullptr;


// The default implementation writes out the name of the recognized command
// to the error console. Real applications will want to take some custom
// action instead, and should implement their own versions of this function.
void RespondToCommand(tflite::ErrorReporter* error_reporter,
                      int32_t current_time, const char* found_command,
                      uint8_t score, bool is_new_command) {

  if (is_new_command) {
    TF_LITE_REPORT_ERROR(error_reporter, "Heard %s (%d) @%dms", found_command,
                         score, current_time);
    red_led_on();    
    green_led_off();
    detected_timeout = current_time + cli_opts.suppression_ms;               
  }
  else if(detected_timeout != 0 && current_time >= detected_timeout)
  {
    detected_timeout = 0;
    previous_score = score;
    previous_found_command = found_command;
    previous_score_timestamp = current_time;
    red_led_off(); 
  }


  if(detected_timeout == 0) 
  { 
    if(previous_score == 0)
    {
      previous_found_command = found_command;
      previous_score = score;
      previous_score_timestamp = current_time;
      return;
    }

    const int32_t time_delta = current_time - previous_score_timestamp;
    const int8_t score_delta = (int8_t)(score - previous_score);
    const float diff = (time_delta > 0) ? std::fabs(score_delta) / time_delta : 0.0f;

    previous_score = score;
    previous_score_timestamp = current_time;

    if(diff >= cli_opts.sensitivity || (previous_found_command != found_command))
    {
      previous_found_command = found_command;
      activity_timestamp = current_time + 500;  
    }
    else if(current_time >= activity_timestamp)
    {
      activity_timestamp = 0;
      green_led_off();
    }

    if(activity_timestamp != 0)
    {
      if(current_time - activity_toggle_timestamp >= 100)
      {
        activity_toggle_timestamp = current_time;
        green_led_toggle();
      }
      
    }
  }

}
