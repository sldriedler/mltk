#include <windows.h>
#include <pthread.h>
#include <stdint.h>

#include "platform_api.h"


#ifndef MLTK_CPU_CLOCK
#error Must add command-line #define MLTK_CPU_CLOCK
#endif

static LARGE_INTEGER frequency = {0ULL};
static uint32_t platform_clock_hz = MLTK_CPU_CLOCK;


bool platform_set_cpu_clock_hz(uint32_t clock_hz)
{
    platform_clock_hz = clock_hz;
    return true;
}

uint32_t platform_get_cpu_clock_hz()
{
    return platform_clock_hz;
}

// uint32_t platform_get_cpu_cycle()
// {
//     LARGE_INTEGER current_time;
//     if(frequency.QuadPart == 0ULL)
//     {
//         QueryPerformanceFrequency(&frequency);
//     }
    
//     QueryPerformanceCounter(&current_time);
//     const uint64_t us =  (uint64_t)((current_time.QuadPart * 1000000) / frequency.QuadPart);
//     return (uint32_t)((platform_clock_hz * us) / 1000000);
// }

uint32_t platform_get_timestamp_ms()
{
    SYSTEMTIME time;
    GetSystemTime(&time);
    return  (uint32_t)((time.wHour * 360000) + (time.wMinute * 60000) + (time.wSecond * 1000) + time.wMilliseconds);
}


uint32_t platform_get_timestamp_us()
{
    LARGE_INTEGER current_time;
    if(frequency.QuadPart == 0ULL)
    {
        QueryPerformanceFrequency(&frequency);
    }
    
    QueryPerformanceCounter(&current_time);
    return  (uint32_t)((current_time.QuadPart * 1000000) / frequency.QuadPart);
}


void platform_sleep_ms(uint32_t ms)
{
    const struct timespec delay = {0, (long)(ms * 1000*1000)};
    pthread_delay_np(&delay);
}