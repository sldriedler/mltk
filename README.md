Silicon Labs Machine Learning Toolkit (MLTK)
==============================================

```{warning} 
This package is considered __EXPERIMENTAL__ for internal use only and is not authorized for use in production.
Silicon Labs does not offer any warranties and disclaims all implied warranties concerning this software.
This package is made available as a self-serve reference supported only by the on-line documentation.
There are no support services for this software at this time.
```

This is a Python package with command-line utilities and scripts to aid the development 
of machine learning models for Silicon Lab's embedded platforms.

The features of this Python package include:
- [Command-line](./docs/command_line.md) - Execute all ML operations from simple command-line interface
- [Python API](./docs/python_api/python_api.md) - Execute all ML operations from a Python script
- [Model Profiler](./docs/guides/model_profiler.md) - Determine how efficient an ML model will execute on an embedded platform
- [Model Training](./docs/guides/model_training.md) - Train an ML model using [Google Tensorflow](https://www.tensorflow.org/)
- [Model Evaluation](./docs/guides/model_evaluation.md) - Evaluate a trained ML model's accuracy and other metrics
- [Model Summary](./docs/guides/model_summary.md) - Generate a summary of the model's contents
- [Model Visualization](./docs/guides/model_visualizer.md) - Interactively view the ML model's structure 
- [Model Quantization](./docs/guides/model_quantization.md) - Reduce the memory footprint of an ML model by using the [Tensorflow-Lite Converter](https://www.tensorflow.org/lite/convert)
- [Model Parameters](./docs/guides/model_parameters.md) - Embed custom parameters into the generated model file
- [Audio Feature Generator](./docs/audio/audio_feature_generator.md) - Library and tools to convert streaming audio into spectrograms
- [Audio Utilities](./docs/audio/audio_utilities.md) - Utilities to aid the development of audio classification models
- [Python C++ Wrappers](./docs/other/repository_overview.md) - Execute C++ libraries (including [Tensorflow-Lite Micro](https://github.com/tensorflow/tflite-micro)) from a Python interface


Refer to [Why MLTK?](./docs/why_mltk.md) for more details on the benefits of using the MLTK.


## Overview

```{eval-rst}
.. raw:: html

   <iframe src="./_static/overview/index.html" height="100%" width="100%" frameborder="0" class="overview-iframe" allowfullscreen></iframe>
```


## Installation

Install the pre-build Python package:

```shell
# Windows
pip  install --extra-index-url https://test.pypi.org/simple silabs-mltk

# Linux
pip3 install --extra-index-url https://test.pypi.org/simple silabs-mltk
```

Build and install Python package from [Github](https://github.com/siliconlabs/mltk):

```shell
# Windows
pip  install git+https://github.com/siliconlabs/mltk.git

# Linux
pip3 install git+https://github.com/siliconlabs/mltk.git
```

Refer to [Installation Guide](./docs/installation.md) for more details on how to install the MLTK.


## Other Information

- [Quick Reference](./docs/other/quick_reference.md)
- [Settings File](./docs/other/settings_file.md)
- [Model Specification](./docs/guides/model_specification.md)
- [Model Archive File](./docs/guides/model_archive.md)
- [Model Search Path](./docs/guides/model_search_path.md)
- [Environment Variables](./docs/other/environment_variables.md)
- [C++ Development with VSCode](./docs/other/cpp_development_with_vscode.md)

## License

SPDX-License-Identifier: Zlib

The licensor of this software is Silicon Laboratories Inc.

This software is provided 'as-is', without any express or implied
warranty. In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not
   claim that you wrote the original software. If you use this software
   in a product, an acknowledgment in the product documentation would be
   appreciated but is not required.
2. Altered source versions must be plainly marked as such, and must not be
   misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.