
#include <stdint.h>

#include "em_device.h"
#include "em_rtcc.h"
#include "em_emu.h"


extern uint32_t __mlmodel_start;
extern uint32_t __mlmodel_end;

#define MODEL_DATA_SECTION __attribute__((section(".mlmodel")))
#define MODEL_DATA_ADDRESS ((uint8_t*)&__mlmodel_start);
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


#define DWT_CYCCNT_REG ((const volatile uint32_t*)0xE0001004UL) // DWT->CYCCNT


#define platform_get_cpu_cycle() _platform_get_cpu_cycle()
static inline uint32_t _platform_get_cpu_cycle() 
{
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    return *DWT_CYCCNT_REG; 
}

#define platform_get_timestamp_us() (RTCC->CNT * (1000000/32768))