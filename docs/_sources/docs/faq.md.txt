 # Frequently Asked Questions


<details>
  <summary>Where is my trained model?</summary>

  After [training](./guides/model_training.md) a model,
  the trained model files (`.tflite` and `.h5`) are added to the `.mltk.zip` [model archive](./guides/model_archive.md) file
  which is created in the same directory as the [model specification](./guides/model_specification.md) file.

  Additionally, all intermediate training files can be found at: `~/.mltk/models/<model name>`   
  where `<model name>` is the name of the trained file.

  For example, say we have the [model specification](./guides/model_specification.md) file:

  ```
  ~/workspace/my_model.py
  ```

  And we run the command:

  ```shell
  cd ~/workspace
  mltk train my_model
  ```

  Then after training completes, we'll have:

  ```
  ~/workspace/my_model.py           <-- Model specification file
  ~/workspace/my_model.mltk.zip     <-- Model archive, contains trained .tflite and .h5 model files
  ```

  And also, all intermediate training logs can be found at: `~/.mltk/models/my_model`
</details>


<details>
  <summary>How do I run my model on an embedded device?</summary>

  After [training](./guides/model_training.md) a model, `.tflite` model
  file is generated (See the FAQ "Where is my trained model?" for more details).

  This file is programmed to the embedded device which is then loaded
  and executed by the [Tensorflow-Lite Micro](https://github.com/tensorflow/tflite-micro) (TFLM) interpreter.

  The `.tflite` can be thought of as a binary blob. It simply needs to be converted to
  a `uint8_t` C array which can then be directly given to the TFLM interpreter.

  There are several different ways to deploy your model to an embedded device, including:

  <h3>Simplicity Studio</h3>
  
  From your [Simplicity Studio](./cpp_development/simplicity_studio.md) project, replace the default model 
  by renaming your `.tflite` file to `1_<your model named>.tflite` and copy it into the `config/tflite` folder 
  of the Simplicity Studio project. (Simplicity Studio sorts the models alphabetically in ascending order, adding `1_` 
  forces the model to come first). After a new .tflite file is added to the  project Simplicity Studio will automatically use the 
  [flatbuffer converter tool](https://docs.silabs.com/gecko-platform/latest/machine-learning/tensorflow/flatbuffer-conversion)
  to convert a .tflite file into a C file which is added to the project.

  Refer to the online [documentation](https://docs.silabs.com/gecko-platform/latest/machine-learning/tensorflow/guide-replace-model#updating-or-replacing-the--tflite-file-in-a-project) for more details.

  <h3>CMake</h3>
 
  The MLTK features several [example applications](./cpp_development/examples/index.md).
  These applications can be built with [VS Code](./cpp_development/vscode.md) or the CMake [command line](./cpp_development/command_line.md).

  Supported applications such as:  
  - [Model Profiler](./cpp_development/examples/model_profiler.md)
  - [Audio Classifier](./cpp_development/examples/audio_classifier.md)

  Allow for defining [build options](./cpp_development/build_options.md) that specify the path to the `.tflite` model file.

  e.g., to `<mltk repo root>/user_options.cmake`, add:

  ```
  mltk_set(MODEL_PROFILER_MODEL "~/workspace/my_model.tflite")
  mltk_set(AUDIO_CLASSIFIER_MODEL "~/workspace/my_model.tflite")
  ```


  <h3>Command line</h3>
  
  The MLTK features several [example applications](./cpp_development/examples/index.md).

  Supported applications such as:  
  - [Model Profiler](./cpp_development/examples/model_profiler.md)
  - [Audio Classifier](./cpp_development/examples/audio_classifier.md)

  Allow for overriding the default `.tflite` model built into the application.
  When the application starts, it checks the end of flash memory for a `.tflite` model file. If found, the model
  at the end of flash is used instead of the default model.

  To write the model to flash, use the command:

  ```shell
  mltk update_params <model name> --device
  ```

  Refer to the command's help for more details:

  ```shell
  mltk update_params --help
  ```

</details>


<details>
  <summary>Why is the model not working on the embedded device?</summary>

  ...

</details>



<details>
  <summary>The Keras (.h5) model works fine during evaluation but the TF-Lite (.tflite) doesn't?</summary>

  ...
</details>


<details>
  <summary>How can I reduce my model size?</summary>

  ...

</details>


<details>
  <summary>Linux: Why isn't the GPU working?</summary>

  ...

</details>