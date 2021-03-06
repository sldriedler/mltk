# AudioFeatureGenerator Python Wrapper

This is a C++ Python wrapper that allows for executing the Gecko SDK AudioFeatureGenerator component from a Python script.

This is useful as it allows for using the _exact_ same spectrogram generation algorithms between the Python model training scripts
and embedded device at runtime.


This wrapper is made accessible to a Python script via the [AudioFeatureGenerator](mltk.core.preprocess.audio.audio_feature_generator.AudioFeatureGenerator) python API.
This Python API loads the C++ Python wrapper shared library into the Python runtime.

Refer to the AudioFeatureGenerator [documentation](../../../../docs/audio/audio_feature_generator.md) for more details


## Source Code

- [Python wrapper](../../cpp/audio_feature_generator_wrapper) - This makes the AudioFeatureGenerator C++ library accessible to Python
- [C++ library](../../cpp/shared/gecko_sdk/audio_feature_generation) - The C++ library, this invokes the Microfrontend to generate spectrograms
- [Microfrontend](../../cpp/shared/microfrontend) - Google-provided audio processing library to generate spectrograms
- [Python API](../../mltk/core/preprocess/audio/audio_feature_generator) - Python package that loads this C++ wrapper 


## Additional Links

- [Python API documentation](mltk.core.preprocess.audio.audio_feature_generator.AudioFeatureGenerator)
- [Gecko SDK documentation](https://docs.silabs.com/gecko-platform/latest/machine-learning/api/group-ml-audio-feature-generation)
- [C++ Development documentation](../../../../docs/cpp_development/index.md)


## Building the Wrapper

### Pre-built

This wrapper comes pre-built when installing the MLTK Python package, e.g.:

```shell 
pip install silabs-mltk
```


### Automatic Build

This wrapper is automatically built when installing from source, e.g.:

```shell
git clone https://github.com/siliconlabs/mltk.git
cd mltk
pip install -e .
```

### Manual build via MLTK command

To manually build this wrapper, issue the MLTK command:

```shell
mltk build audio_feature_generator_wrapper
```


### Manual build via CMake

This wrapper can also be built via CMake using [Visual Studio Code](../../../../docs/cpp_development/vscode.md) or the [Command Line](../../../../docs/cpp_development/command_line.md).

To build the wrapper, the [build_options.cmake](../../../../docs/cpp_development/build_options.md) file needs to be modified.

Create the file `<mltk repo root>/user_options.cmake` and add:

```
mltk_set(MLTK_TARGET mltk_audio_feature_generator_wrapper)
```

```{note}
You must remove this option and clean the build directory before building the example applications
```

Then configure the CMake project using the Window/Linux GCC toolchain and build the target: `mltk_audio_feature_generator_wrapper`.

