#include <assert.h>
#include <cstdlib>
#include <cstdint>

#include "stacktrace/stacktrace.h"
#include "cpputils/heap.hpp"


extern "C" int __real_main(int argc, char **argv);


extern "C" int __wrap_main(int argc, char **argv)
{
    stacktrace_init();

    const uint32_t heap_size = 64*1024*1024;
    void* heap_base = malloc(heap_size);
    heap_set_buffer(heap_base, heap_size);

    return __real_main(argc, argv);
}

