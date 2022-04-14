# C++ Development

The MLTK contains both Python scripts _and_ C++ libraries/examples.

The C++ libraries allow for sharing source code between a host PC during model training
and an embedded target during model inference.

The C++ [examples](./examples/index.md) demonstrate executing the various libraries on the host PC _or_
on an embedded target.


## Development Modes

The MLTK supports three modes of C++ development:  
- [Simplicity Studio](./simplicity_studio.md) - Allows for building C++ applications for Silicon Lab's embedded targets using Silicon Lab's Simplicity Studio
- [Visual Studio Code](./vscode.md) - Allows for building C++ applications for Windows/Linux/Embedded using Microsoft VSCode
- [Command-line](./command_line.md) - Allows for building C++ applications from the command-line using CMake


## Source Code

All of the C++ source code may be found on Github at: [__mltk__/cpp](../cpp)

This directory has the following structure:  
- [__mltk__/cpp/tflite_micro_wrapper](../cpp/tflite_micro_wrapper) - Tensorflow-Lite Micro Python wrapper, this allows for executing the Tensorflow-Lite Micro interpreter from a Python script
- [__mltk__/cpp/audio_feature_generator_wrapper](../cpp/audio_feature_generator_wrapper) - The AudioFeatureGenerator Python wrapper, this allows for executing the spectrogram generation algorithms from a Python script
- [__mltk__/cpp/mvp_wrapper](../cpp/mvp_wrapper) - MVP hardware accelerator Python wrapper, this allows for executing the MVP-accelerated Tensorflow-Lite Micro kernels from a Python script
- [__mltk__/cpp/shared](../cpp/shared) - All of the C++ libraries and source code
- [__mltk__/cpp/shared/apps](../cpp/shared/apps) - Example applications and demos
- [__mltk__/cpp/shared/platforms](../cpp/shared/platforms) - Supported hardware platforms
- [__mltk__/cpp/tools](../cpp/tools) - Tools used by the C++ build scripts


## Examples

Refer to the [Examples Documentation](./examples/index.md) for more details about the applications that come with the MLTK.



```{eval-rst}
.. toctree::
   :maxdepth: 1
   :hidden:

   ./vscode
   ./simplicity_studio
   ./command_line
   ./build_options
   ./examples/index
```