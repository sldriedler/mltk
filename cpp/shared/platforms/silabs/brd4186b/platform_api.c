#include <stdint.h>
#include <stddef.h>
#include <assert.h>

#include "em_device.h"
#include "em_cmu.h"
#include "em_burtc.h"
#include "platform_api.h"


static uint32_t clock_frequency_hz = 0;
static void (*platform_mvp_irq_handler)(void);


void platform_init()
{
    // Enable the CPU cycle counter
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    DWT->CYCCNT = 0;

    BURTC_Init_TypeDef init = BURTC_INIT_DEFAULT;
    init.start = false;
    init.debugRun = false;
    init.clkDiv = burtcClkDiv_1;
    CMU_ClockSelectSet(cmuClock_BURTC, cmuSelect_LFXO);
    CMU_ClockEnable(cmuClock_BURTC, true);
    BURTC_Init(&init);
    BURTC->CNT = 0;
    BURTC_Start();

    LETIMER_Init_TypeDef timer_cfg = LETIMER_INIT_DEFAULT;
    timer_cfg.enable = false;

    CMU_ClockEnable(cmuClock_LETIMER0, true);
    CMU_ClockSelectSet(cmuClock_LETIMER0, cmuSelect_LFXO);
    LETIMER_Init(LETIMER0, &timer_cfg);
    LETIMER0->IEN_SET = LETIMER_IEN_UF;
    

    EMU_EM01Init_TypeDef em01_init = EMU_EM01INIT_DEFAULT;
    em01_init.vScaleEM01LowPowerVoltageEnable = true;
    EMU_EM01Init(&em01_init);

    NVIC_EnableIRQ(GPIO_ODD_IRQn);
    NVIC_EnableIRQ(GPIO_EVEN_IRQn);
    NVIC_EnableIRQ(LETIMER0_IRQn);

    // Disable the display
    GPIO_PinModeSet(gpioPortC, 9, gpioModePushPull, 0);
    // Disable the sensor
    GPIO_PinModeSet(gpioPortD, 3, gpioModePushPull, 0);
    // Enable the VCOM port 
    GPIO_PinModeSet(gpioPortB, 0, gpioModePushPull, 1);
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


// NOTE: These GPIO IRQ handlers don't do anything
//       We trigger an interrupt on the rising/falling edges
//       of the input GPIO so the CPU wakes up from the "wfe" instruction
void GPIO_ODD_IRQHandler()
{
    const uint32_t gpio_status = GPIO_IntGetEnabled();
    GPIO->IF_CLR =  gpio_status;
}

void GPIO_EVEN_IRQHandler()
{
    const uint32_t gpio_status = GPIO_IntGetEnabled();
    GPIO->IF_CLR =  gpio_status;
}

void platform_set_mvp_irq_handler(void (*handler)(void))
{
  platform_mvp_irq_handler = handler;
}

void MVP_IRQHandler(void)
{
  assert(platform_mvp_irq_handler != NULL);
  platform_mvp_irq_handler();
}

void LETIMER0_IRQHandler(void)
{
    LETIMER0->IF_CLR = LETIMER_IF_UF;
}