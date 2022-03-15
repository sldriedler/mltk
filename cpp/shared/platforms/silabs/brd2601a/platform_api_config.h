#pragma once 

#include <stdint.h>
#include "em_device.h"
#include "em_burtc.h"
#include "em_gpio.h"
#include "em_emu.h"
#include "em_letimer.h"


extern uint32_t __mlmodel_start;
extern uint32_t __mlmodel_end;

#define MODEL_DATA_SECTION __attribute__((section(".mlmodel")))
#define MODEL_DATA_BASE_ADDRESS ((uint8_t*)&__mlmodel_start)
#define MODEL_DATA_LENGTH ((uint32_t)&__mlmodel_end - (uint32_t)&__mlmodel_start)


#define PLATFORM_SRAM_START_ADDRESS                 (SRAM_BASE)
#define PLATFORM_SRAM_END_ADDRESS                   (PLATFORM_SRAM_START_ADDRESS + SRAM_SIZE)
#define PLATFORM_IS_SRAM_ADDRESS(addr)              ((((uint32_t)addr) >= PLATFORM_SRAM_START_ADDRESS) && (((uint32_t)addr) < PLATFORM_SRAM_END_ADDRESS))

#define PLATFORM_FLASH_START_ADDRESS                (FLASH_BASE)
#define PLATFORM_FLASH_END_ADDRESS                  (PLATFORM_FLASH_START_ADDRESS + FLASH_SIZE)
#define PLATFORM_IS_FLASH_ADDRESS(addr)             ((((uint32_t)addr) >= PLATFORM_FLASH_START_ADDRESS) && (((uint32_t)addr) < PLATFORM_FLASH_END_ADDRESS))

#define PLATFORM_GOTO_SLEEP() \
DWT->CTRL &= ~DWT_CTRL_CYCCNTENA_Msk; \
EMU_EnterEM1(); \
DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk


#define ENERGY_PROFILER_MODE_GPIO       gpioPortA,6 /* input, expansion header pin 11 */
#define ENERGY_PROFILER_STATUS_GPIO     gpioPortA,7 /* output, expansion header pin 13 */

#define ENERGY_PROFILER_GPIO_HIGH       true
#define ENERGY_PROFILER_GPIO_LOW        false



#define DWT_CYCCNT_REG ((const volatile uint32_t*)0xE0001004UL) // DWT->CYCCNT


#define platform_get_cpu_cycle() _platform_get_cpu_cycle()
static inline uint32_t _platform_get_cpu_cycle() 
{
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    return *DWT_CYCCNT_REG; 
}


#define platform_get_timestamp_us() (BURTC->CNT * (1000000/32768))


#define platform_gpio_init_input(gpio, active_level) _platform_gpio_init_input(gpio, active_level)
static inline void _platform_gpio_init_input(GPIO_Port_TypeDef port, unsigned int pin, unsigned int active_level)
{
    GPIO_PinModeSet(port, pin, gpioModeInputPull, !active_level);
    GPIO_ExtIntConfig(port, pin, pin, true, true, true);
}

#define platform_gpio_get_input(gpio) GPIO_PinInGet(gpio)
#define platform_gpio_init_output(gpio, initial_level) GPIO_PinModeSet(gpio, gpioModePushPull, initial_level)
#define platform_gpio_set_output(gpio, level) level ? GPIO_PinOutSet(gpio) : GPIO_PinOutClear(gpio)


#define platform_force_wakeup_after_us(us) \
{ \
    while (LETIMER0->SYNCBUSY & (LETIMER_SYNCBUSY_STOP | LETIMER_SYNCBUSY_START)) {} \
    if(us == -1) { \
         LETIMER0->CMD = LETIMER_CMD_STOP; \
    } \
    else \
    { \
        LETIMER_CounterSet(LETIMER0, us * (1000000/32768)); \
        LETIMER0->IF_CLR = LETIMER_IF_UF; \
        LETIMER0->CMD = LETIMER_CMD_START; \
    } \
}
