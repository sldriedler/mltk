Gecko SDK MVP-Accelerated Tensorflow Kernels
===============================================

This library allows for accelerating several Tensorflow-Lite Micro [kernels](https://github.com/tensorflow/tflite-micro/tree/main/tensorflow/lite/micro/kernels) using the MVP hardware accelerator.

These kernels where taken from:  
- __mvp_driver__ - https://github.com/SiliconLabs/gecko_sdk/tree/gsdk_4.0/platform/driver/mvp
- __kernels__ - https://github.com/SiliconLabs/gecko_sdk/tree/gsdk_4.0/util/third_party/tensorflow_extra/siliconlabs

They were slightly modified to enable their usage with the MVP hardware simulator and the MLTK.
