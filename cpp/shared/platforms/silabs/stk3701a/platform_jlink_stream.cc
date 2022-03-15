
#include "em_device.h"
#include "platform_api.h"


#define RAM_END_ADDRESS (RAM_MEM_BASE + RAM_MEM_SIZE)


#define CONTEXT_BASE_ADDRESS (RAM_END_ADDRESS-sizeof(uint32_t))
#define JLINK_STREAM_IRQ FPUEH_IRQn
#define JLINK_STREAM_IRQ_HANDLER FPUEH_IRQHandler


namespace jlink_stream 
{
    void process_command();
}


/*************************************************************************************************/
void platform_jlink_stream_init(uint32_t *trigger_address_ptr, uint32_t *trigger_value_ptr, uint32_t context_address)
{
    NVIC_ClearPendingIRQ(JLINK_STREAM_IRQ);
    NVIC_EnableIRQ(JLINK_STREAM_IRQ);

    *trigger_address_ptr = (uint32_t)&NVIC->STIR;
    *trigger_value_ptr   = (uint32_t)JLINK_STREAM_IRQ;

    volatile uint32_t *base_address = (volatile uint32_t*)CONTEXT_BASE_ADDRESS;
    *base_address = context_address;
}

/*************************************************************************************************/
void platform_jlink_stream_set_interrupt_enabled(bool enabled)
{
    if(enabled)
    {
        __DSB(); // Ensure all data is synchronized before re-enabling interrupts
        NVIC_EnableIRQ(JLINK_STREAM_IRQ);
    }
    else
    {
        NVIC_DisableIRQ(JLINK_STREAM_IRQ);
        __DSB(); // Ensure all data is synchronized before continuing with interrupts disabled
    }
}


/*************************************************************************************************
 * This interrupt is triggered from an external script. The script uses the ARM NVIC software interrupt (NVIC->STIR)
 * register to trigger this interrupt.
 */
void JLINK_STREAM_IRQ_HANDLER(void)
{
    NVIC_ClearPendingIRQ(JLINK_STREAM_IRQ);
    jlink_stream::process_command();
}

