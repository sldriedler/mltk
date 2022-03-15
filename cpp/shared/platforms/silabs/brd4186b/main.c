#include <stdint.h>
#include <stdlib.h>

#include "platform_api.h"
#include "sl_system_init.h"


extern const uint32_t __init_array_start;
extern const uint32_t __init_array_end;
extern const uint8_t __HeapBase;
extern const uint8_t __HeapLimit;


extern void main(int, char**);
extern void heap_set_buffer(void* buffer, uint32_t length);



/*************************************************************************************************/
void _start(void)
{
    // Configure the MLTK malloc memory util
    heap_set_buffer((uint8_t*)&__HeapBase, (uint32_t)(&__HeapLimit - &__HeapBase));

    sl_system_init();
    platform_init();

    // Initialize any global static C++ constructors
    for(const uint32_t *p = &__init_array_start; p < &__init_array_end; ++p)
    {
        void (**constructor_ptr)() = (void*)p;

        (*constructor_ptr)();
    }

    main(0, NULL);

    for(;;)
    {
        PLATFORM_GOTO_SLEEP();
    }
}