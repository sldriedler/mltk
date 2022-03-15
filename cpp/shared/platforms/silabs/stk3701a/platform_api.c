#include <stdint.h>

#include "em_device.h"
#include "em_cmu.h"
#include "em_rtcc.h"
#include "platform_api.h"



static uint32_t clock_frequency_hz = 0;



void platform_init()
{
    // Enable the CPU cycle counter
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    DWT->CYCCNT = 0;

    RTCC_Init_TypeDef init = RTCC_INIT_DEFAULT;
    init.enable = true;
    init.debugRun = true; // We want the timer to run while the CPU is halted so we can record audio
    init.presc = rtccCntPresc_1;
    CMU_ClockSelectSet(cmuClock_RTCC, cmuSelect_LFXO);
    CMU_ClockEnable(cmuClock_RTCC, true);
    RTCC_Init(&init);
    RTCC->CNT = 0;
}



bool platform_set_cpu_clock_hz(uint32_t clock_hz)
{
    return false;
}

uint32_t platform_get_cpu_clock_hz()
{
    if(clock_frequency_hz == 0)
    {
        clock_frequency_hz = CMU_ClockFreqGet(cmuClock_CORE);
    }
    return clock_frequency_hz;
}

uint32_t platform_get_timestamp_ms()
{
    return platform_get_timestamp_us() / 1000;
}

void platform_sleep_us(uint32_t us)
{
    #define CPU_CYCLES_PER_MICROSECOND ((platform_get_cpu_clock_hz() / 1000000UL))
    const uint32_t start_time = DWT->CYCCNT + 7;

    us *= CPU_CYCLES_PER_MICROSECOND;

    while((DWT->CYCCNT - start_time) < us)
    {
    }
}

void platform_sleep_ms(uint32_t ms)
{
    const uint32_t start_time = platform_get_timestamp_ms();
    while((platform_get_timestamp_ms() - start_time) < ms)
    {
    }
}