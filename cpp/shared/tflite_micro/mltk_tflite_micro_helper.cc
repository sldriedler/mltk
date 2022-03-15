#include <cstdarg>
#include <cassert>

#include "mltk_tflite_micro_internal.hpp"


namespace mltk
{

static Logger *mltk_logger =  nullptr;
bool model_profiler_enabled = false;
bool model_recorder_enabled = false;
const TfliteMicroAccelerator* _accelerator = nullptr;


/*************************************************************************************************/
TfLiteStatus allocate_scratch_buffer(TfLiteContext *ctx, unsigned size_bytes, int *scratch_buffer_index)
{
    auto status = ctx->RequestScratchBufferInArena(ctx, size_bytes, scratch_buffer_index);
    if(status != kTfLiteOk)
    {
        assert(!"Failed to allocate scratch buffer");
    }
    return status; 
}

/*************************************************************************************************/
#ifndef MLTK_DLL_IMPORT 
extern "C" void issue_unsupported_kernel_message(const char* fmt, ...)
{
  if(_current_kernel_index == -1 || _issued_unsupported_msg)
  {
    return;
  }

  _issued_unsupported_msg = true;

  char buffer[256];
  char op_name[92];
  const int l = snprintf(buffer, sizeof(buffer), "%s not supported: ", op_to_str(_current_kernel_index, (tflite::BuiltinOperator)_current_kernel_op_code));

  va_list args;
  va_start(args, fmt);
  vsnprintf(&buffer[l], sizeof(buffer)-l, fmt, args);
  va_end(args);

  get_logger().warn("%s", buffer);
}
#endif // MLTK_DLL_IMPORT

/*************************************************************************************************/
Logger& get_logger()
{
    if(mltk_logger == nullptr)
    {
        mltk_logger = logging::get("MLTK");
        if(mltk_logger == nullptr)
        {
            mltk_logger = logging::create("MLTK", LogLevel::Info);
            assert(mltk_logger != nullptr);
        }
    }

    return *mltk_logger;
}

/*************************************************************************************************/
bool set_log_level(LogLevel level)
{
    return get_logger().level(level);
}

/*************************************************************************************************/
#ifndef MLTK_DLL_IMPORT 
void mltk_tflite_micro_set_accelerator(const TfliteMicroAccelerator* accelerator)
{
    _accelerator = accelerator;
}
#endif


#ifndef TFLITE_MICRO_ACCELERATOR
/*************************************************************************************************/
void mltk_tflite_micro_register_accelerator()
{
    // This is just a placeholder if no accelerator is built into the binary / shared library
    // (i.e. each accelerator also defines this API and internally calls mltk_tflite_micro_set_accelerator())
    _accelerator = nullptr;
}
#endif

/*************************************************************************************************/
const TfliteMicroAccelerator* mltk_tflite_micro_get_registered_accelerator()
{
    return _accelerator;
}


/*************************************************************************************************/
int TfliteMicroErrorReporter::Report(const char* format, va_list args)
{
    auto& logger = get_logger();
    const auto orig_flags = logger.flags();
    logger.flags().clear(logging::Newline);
    logger.vwrite(logging::Error, format, args);
    logger.write(logging::Error, "\n");
    logger.flags(orig_flags);
    return 0;
}


} // namespace mltk