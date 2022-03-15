#pragma once 

#include <stdint.h>
#include <stdbool.h>


#ifdef __cplusplus
extern "C" {
#endif

#include "platform_api_config.h"


#ifndef PLATFORM_GOTO_SLEEP
#define PLATFORM_GOTO_SLEEP()
#endif




void platform_init();
bool platform_set_cpu_clock_hz(uint32_t clock_hz);
uint32_t platform_get_cpu_clock_hz();
uint32_t platform_get_timestamp_ms();

void platform_sleep_ms(uint32_t ms);
void platform_sleep_us(uint32_t us);

void platform_jlink_stream_init(uint32_t *trigger_address_ptr, uint32_t *trigger_value_ptr, uint32_t context_address);
void platform_jlink_stream_set_interrupt_enabled(bool enabled);


#ifndef platform_get_cpu_cycle
uint32_t platform_get_cpu_cycle();
#endif 
#ifndef platform_get_timestamp_us
uint32_t platform_get_timestamp_us();
#endif 
#ifndef platform_gpio_init_input
void platform_gpio_init_input(int gpio);
#endif 
#ifndef platform_gpio_get_input
bool platform_gpio_get_input(int gpio);
#endif 
#ifndef platform_gpio_init_output
void platform_gpio_init_output(int gpio, bool inital_value);
#endif
#ifndef platform_gpio_set_output
void platform_gpio_set_output(int gpio, bool value);
#endif

#ifndef platform_force_wakeup_after_us
#define platform_force_wakeup_after_us(x)
#endif



#ifdef __cplusplus
}
#endif