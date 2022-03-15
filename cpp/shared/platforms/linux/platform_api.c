#include <sys/time.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <errno.h>  

#include "platform_api.h"


#ifndef MLTK_CPU_CLOCK
#error Must add command-line #define MLTK_CPU_CLOCK
#endif


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
//     struct timeval te;

//     gettimeofday(&te, NULL); // get current time

//     const uint64_t us = te.tv_sec*1000000ULL + te.tv_usec;

//     return (uint32_t)((platform_clock_hz * us) / 1000000);
// }

uint32_t platform_get_timestamp_ms()
{
    struct timeval te;

    gettimeofday(&te, NULL); // get current time

    return te.tv_sec*1000ULL + te.tv_usec / 1000UL;
}

uint32_t platform_get_timestamp_us()
{
    struct timeval te;

    gettimeofday(&te, NULL); // get current time

    return (uint32_t)(te.tv_sec*1000000ULL + te.tv_usec);
}

void platform_sleep_ms(uint32_t ms)
{
    struct timespec ts;
    int res;

    if (ms < 0)
    {
        errno = EINVAL;
        return;
    }

    ts.tv_sec = ms / 1000;
    ts.tv_nsec = (ms % 1000) * 1000000;

    do {
        res = nanosleep(&ts, &ts);
    } while (res && errno == EINTR);
}