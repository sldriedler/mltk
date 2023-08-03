"""keyword_spotting_on_off_v3
*******************************

This model is a CNN classifier to detect the keywords:

- on
- off

This model specification script is designed to work with the
`Keyword Spotting On/Off <https://siliconlabs.github.io/mltk/mltk/tutorials/keyword_spotting_on_off.html>`_ tutorial.

- Source code: `keyword_spotting_on_off_v3.py <https://github.com/siliconlabs/mltk/blob/master/mltk/models/siliconlabs/keyword_spotting_on_off_v3.py>`_
- Pre-trained model: `keyword_spotting_on_off_v3.mltk.zip <https://github.com/SiliconLabs/mltk/raw/master/mltk/models/siliconlabs/keyword_spotting_on_off_v3.mltk.zip>`_


Dataset
---------

This model was trained using several different datasets:

- `mltk.datasets.audio.on_off <https://siliconlabs.github.io/mltk/docs/python_api/datasets/audio/on_off.html>`_ - Synthetically generated keywords: on, off
- `mltk.datasets.audio.speech_commands_v2 <https://siliconlabs.github.io/mltk/docs/python_api/datasets/audio/speech_commands_v2.html>`_ - Human generated keywords: on, off
- `mltk.datasets.audio.mlcommons.ml_commons_keyword <https://siliconlabs.github.io/mltk/docs/python_api/datasets/audio/ml_commons/keywords.html>`_ - Large collection of keywords, random subset used for *unknown* class
- `mltk.datasets.audio.background_noise.esc50 <https://siliconlabs.github.io/mltk/docs/python_api/datasets/audio/background_noise/esc50.html>`_ - Collection of various noises, random subset used for *unknown* class
- `mltk.datasets.audio.background_noise.ambient <https://siliconlabs.github.io/mltk/docs/python_api/datasets/audio/background_noise/ambient.html>`_ - Collection of various background noises, mixed into other samples for augmentation
- `mltk.datasets.audio.background_noise.brd2601 <https://siliconlabs.github.io/mltk/docs/python_api/datasets/audio/background_noise/brd2601.html>`_ - "Silence" recorded by BRD2601 microphone, mixed into other samples to make them "sound" like they came from the BRD2601's microphone
- `mltk.datasets.audio.mit_ir_survey <https://siliconlabs.github.io/mltk/docs/python_api/datasets/audio/mit_ir_survey.html>`_ Impulse responses that are randomly convolved with the samples. This makes the samples sound if they were recorded in different environments.


.. hint::

   Uncomment the line:

   .. highlight:: python
   .. code-block:: python

      #data_dump_dir = my_model.create_log_dir('dataset_dump')

   To dump the augmented audio samples and corresponding spectrograms.
   This is useful to see how the augmentations affect the samples during training.
   WARNING: This will generate A LOT of file dumps, so be sure to disable during actual model training.


Dataset Summary
^^^^^^^^^^^^^^^^^

::

    Dataset subset: training, found 29155 samples:
               on: 9071
              off: 9034
        _unknown_: 11050
    Dataset subset: validation, found 5135 samples:
               on: 1595
              off: 1590
        _unknown_: 1950

    Class weights:
               on = 1.07
              off = 1.08
        _unknown_ = 0.88


Preprocessing
^^^^^^^^^^^^^^

The audio samples are converted to a spectrogram using the :py:class:`mltk.core.preprocess.audio.audio_feature_generator.AudioFeatureGenerator`.
The following setting are used:

- sample_rate: 16kHz
- sample_length: 1s
- window size: 30ms
- window step: 10ms
- n_channels: 104
- upper_band_limit: 7500.0
- lower_band_limit:125.0
- noise_reduction_enable: True
- noise_reduction_min_signal_remaining: 0.40
- dc_notch_filter_enable: True
- dc_notch_filter_coefficient: 0.95
- quantize_dynamic_scale_enable: True
- quantize_dynamic_scale_range_db: 40.0


Model Architecture
--------------------

The model is based on the `Temporal efficient neural network (TENet) <https://arxiv.org/pdf/2010.09960.pdf>`_ model architecture.

    A network for processing spectrogram data using temporal and depthwise convolutions. The network treats the [T, F] spectrogram as a timeseries shaped [T, 1, F].


More details at `mltk.models.shared.tenet.TENet <https://siliconlabs.github.io/mltk/docs/python_api/models/common_models.html#tenet>`_


Model Summary
--------------

.. code-block:: shell

    mltk summarize keyword_spotting_on_off_v3 --tflite

    +-------+-------------------+-----------------+-----------------+------------------------------------------------------+
    | Index | OpCode            | Input(s)        | Output(s)       | Config                                               |
    +-------+-------------------+-----------------+-----------------+------------------------------------------------------+
    | 0     | conv_2d           | 98x1x104 (int8) | 98x1x40 (int8)  | Padding:Same stride:1x1 activation:None              |
    |       |                   | 3x1x104 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 1     | conv_2d           | 98x1x40 (int8)  | 98x1x120 (int8) | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 2     | depthwise_conv_2d | 98x1x120 (int8) | 49x1x120 (int8) | Multiplier:1 padding:Same stride:2x2 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 3     | conv_2d           | 49x1x120 (int8) | 49x1x40 (int8)  | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 4     | conv_2d           | 98x1x40 (int8)  | 49x1x40 (int8)  | Padding:Same stride:2x2 activation:Relu              |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 5     | add               | 49x1x40 (int8)  | 49x1x40 (int8)  | Activation:Relu                                      |
    |       |                   | 49x1x40 (int8)  |                 |                                                      |
    | 6     | conv_2d           | 49x1x40 (int8)  | 49x1x120 (int8) | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 7     | depthwise_conv_2d | 49x1x120 (int8) | 49x1x120 (int8) | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 8     | conv_2d           | 49x1x120 (int8) | 49x1x40 (int8)  | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 9     | add               | 49x1x40 (int8)  | 49x1x40 (int8)  | Activation:Relu                                      |
    |       |                   | 49x1x40 (int8)  |                 |                                                      |
    | 10    | conv_2d           | 49x1x40 (int8)  | 49x1x120 (int8) | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 11    | depthwise_conv_2d | 49x1x120 (int8) | 49x1x120 (int8) | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 12    | conv_2d           | 49x1x120 (int8) | 49x1x40 (int8)  | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 13    | add               | 49x1x40 (int8)  | 49x1x40 (int8)  | Activation:Relu                                      |
    |       |                   | 49x1x40 (int8)  |                 |                                                      |
    | 14    | conv_2d           | 49x1x40 (int8)  | 49x1x120 (int8) | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 15    | depthwise_conv_2d | 49x1x120 (int8) | 49x1x120 (int8) | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 16    | conv_2d           | 49x1x120 (int8) | 49x1x40 (int8)  | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 17    | add               | 49x1x40 (int8)  | 49x1x40 (int8)  | Activation:Relu                                      |
    |       |                   | 49x1x40 (int8)  |                 |                                                      |
    | 18    | conv_2d           | 49x1x40 (int8)  | 49x1x120 (int8) | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 19    | depthwise_conv_2d | 49x1x120 (int8) | 25x1x120 (int8) | Multiplier:1 padding:Same stride:2x2 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 20    | conv_2d           | 25x1x120 (int8) | 25x1x40 (int8)  | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 21    | conv_2d           | 49x1x40 (int8)  | 25x1x40 (int8)  | Padding:Same stride:2x2 activation:Relu              |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 22    | add               | 25x1x40 (int8)  | 25x1x40 (int8)  | Activation:Relu                                      |
    |       |                   | 25x1x40 (int8)  |                 |                                                      |
    | 23    | conv_2d           | 25x1x40 (int8)  | 25x1x120 (int8) | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 24    | depthwise_conv_2d | 25x1x120 (int8) | 25x1x120 (int8) | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 25    | conv_2d           | 25x1x120 (int8) | 25x1x40 (int8)  | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 26    | add               | 25x1x40 (int8)  | 25x1x40 (int8)  | Activation:Relu                                      |
    |       |                   | 25x1x40 (int8)  |                 |                                                      |
    | 27    | conv_2d           | 25x1x40 (int8)  | 25x1x120 (int8) | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 28    | depthwise_conv_2d | 25x1x120 (int8) | 25x1x120 (int8) | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 29    | conv_2d           | 25x1x120 (int8) | 25x1x40 (int8)  | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 30    | add               | 25x1x40 (int8)  | 25x1x40 (int8)  | Activation:Relu                                      |
    |       |                   | 25x1x40 (int8)  |                 |                                                      |
    | 31    | conv_2d           | 25x1x40 (int8)  | 25x1x120 (int8) | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 32    | depthwise_conv_2d | 25x1x120 (int8) | 25x1x120 (int8) | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 33    | conv_2d           | 25x1x120 (int8) | 25x1x40 (int8)  | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 34    | add               | 25x1x40 (int8)  | 25x1x40 (int8)  | Activation:Relu                                      |
    |       |                   | 25x1x40 (int8)  |                 |                                                      |
    | 35    | conv_2d           | 25x1x40 (int8)  | 25x1x120 (int8) | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 36    | depthwise_conv_2d | 25x1x120 (int8) | 13x1x120 (int8) | Multiplier:1 padding:Same stride:2x2 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 37    | conv_2d           | 13x1x120 (int8) | 13x1x40 (int8)  | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 38    | conv_2d           | 25x1x40 (int8)  | 13x1x40 (int8)  | Padding:Same stride:2x2 activation:Relu              |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 39    | add               | 13x1x40 (int8)  | 13x1x40 (int8)  | Activation:Relu                                      |
    |       |                   | 13x1x40 (int8)  |                 |                                                      |
    | 40    | conv_2d           | 13x1x40 (int8)  | 13x1x120 (int8) | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 41    | depthwise_conv_2d | 13x1x120 (int8) | 13x1x120 (int8) | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 42    | conv_2d           | 13x1x120 (int8) | 13x1x40 (int8)  | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 43    | add               | 13x1x40 (int8)  | 13x1x40 (int8)  | Activation:Relu                                      |
    |       |                   | 13x1x40 (int8)  |                 |                                                      |
    | 44    | conv_2d           | 13x1x40 (int8)  | 13x1x120 (int8) | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 45    | depthwise_conv_2d | 13x1x120 (int8) | 13x1x120 (int8) | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 46    | conv_2d           | 13x1x120 (int8) | 13x1x40 (int8)  | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 47    | add               | 13x1x40 (int8)  | 13x1x40 (int8)  | Activation:Relu                                      |
    |       |                   | 13x1x40 (int8)  |                 |                                                      |
    | 48    | conv_2d           | 13x1x40 (int8)  | 13x1x120 (int8) | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 49    | depthwise_conv_2d | 13x1x120 (int8) | 13x1x120 (int8) | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 50    | conv_2d           | 13x1x120 (int8) | 13x1x40 (int8)  | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 51    | add               | 13x1x40 (int8)  | 13x1x40 (int8)  | Activation:Relu                                      |
    |       |                   | 13x1x40 (int8)  |                 |                                                      |
    | 52    | conv_2d           | 13x1x40 (int8)  | 13x1x120 (int8) | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 53    | depthwise_conv_2d | 13x1x120 (int8) | 7x1x120 (int8)  | Multiplier:1 padding:Same stride:2x2 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 54    | conv_2d           | 7x1x120 (int8)  | 7x1x40 (int8)   | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 55    | conv_2d           | 13x1x40 (int8)  | 7x1x40 (int8)   | Padding:Same stride:2x2 activation:Relu              |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 56    | add               | 7x1x40 (int8)   | 7x1x40 (int8)   | Activation:Relu                                      |
    |       |                   | 7x1x40 (int8)   |                 |                                                      |
    | 57    | conv_2d           | 7x1x40 (int8)   | 7x1x120 (int8)  | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 58    | depthwise_conv_2d | 7x1x120 (int8)  | 7x1x120 (int8)  | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 59    | conv_2d           | 7x1x120 (int8)  | 7x1x40 (int8)   | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 60    | add               | 7x1x40 (int8)   | 7x1x40 (int8)   | Activation:Relu                                      |
    |       |                   | 7x1x40 (int8)   |                 |                                                      |
    | 61    | conv_2d           | 7x1x40 (int8)   | 7x1x120 (int8)  | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 62    | depthwise_conv_2d | 7x1x120 (int8)  | 7x1x120 (int8)  | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 63    | conv_2d           | 7x1x120 (int8)  | 7x1x40 (int8)   | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 64    | add               | 7x1x40 (int8)   | 7x1x40 (int8)   | Activation:Relu                                      |
    |       |                   | 7x1x40 (int8)   |                 |                                                      |
    | 65    | conv_2d           | 7x1x40 (int8)   | 7x1x120 (int8)  | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 66    | depthwise_conv_2d | 7x1x120 (int8)  | 7x1x120 (int8)  | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 67    | conv_2d           | 7x1x120 (int8)  | 7x1x40 (int8)   | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 68    | add               | 7x1x40 (int8)   | 7x1x40 (int8)   | Activation:Relu                                      |
    |       |                   | 7x1x40 (int8)   |                 |                                                      |
    | 69    | conv_2d           | 7x1x40 (int8)   | 7x1x120 (int8)  | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 70    | depthwise_conv_2d | 7x1x120 (int8)  | 4x1x120 (int8)  | Multiplier:1 padding:Same stride:2x2 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 71    | conv_2d           | 4x1x120 (int8)  | 4x1x40 (int8)   | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 72    | conv_2d           | 7x1x40 (int8)   | 4x1x40 (int8)   | Padding:Same stride:2x2 activation:Relu              |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 73    | add               | 4x1x40 (int8)   | 4x1x40 (int8)   | Activation:Relu                                      |
    |       |                   | 4x1x40 (int8)   |                 |                                                      |
    | 74    | conv_2d           | 4x1x40 (int8)   | 4x1x120 (int8)  | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 75    | depthwise_conv_2d | 4x1x120 (int8)  | 4x1x120 (int8)  | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 76    | conv_2d           | 4x1x120 (int8)  | 4x1x40 (int8)   | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 77    | add               | 4x1x40 (int8)   | 4x1x40 (int8)   | Activation:Relu                                      |
    |       |                   | 4x1x40 (int8)   |                 |                                                      |
    | 78    | conv_2d           | 4x1x40 (int8)   | 4x1x120 (int8)  | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 79    | depthwise_conv_2d | 4x1x120 (int8)  | 4x1x120 (int8)  | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 80    | conv_2d           | 4x1x120 (int8)  | 4x1x40 (int8)   | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 81    | add               | 4x1x40 (int8)   | 4x1x40 (int8)   | Activation:Relu                                      |
    |       |                   | 4x1x40 (int8)   |                 |                                                      |
    | 82    | conv_2d           | 4x1x40 (int8)   | 4x1x120 (int8)  | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 83    | depthwise_conv_2d | 4x1x120 (int8)  | 4x1x120 (int8)  | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 84    | conv_2d           | 4x1x120 (int8)  | 4x1x40 (int8)   | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 85    | add               | 4x1x40 (int8)   | 4x1x40 (int8)   | Activation:Relu                                      |
    |       |                   | 4x1x40 (int8)   |                 |                                                      |
    | 86    | conv_2d           | 4x1x40 (int8)   | 4x1x120 (int8)  | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 87    | depthwise_conv_2d | 4x1x120 (int8)  | 2x1x120 (int8)  | Multiplier:1 padding:Same stride:2x2 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 88    | conv_2d           | 2x1x120 (int8)  | 2x1x40 (int8)   | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 89    | conv_2d           | 4x1x40 (int8)   | 2x1x40 (int8)   | Padding:Same stride:2x2 activation:Relu              |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 90    | add               | 2x1x40 (int8)   | 2x1x40 (int8)   | Activation:Relu                                      |
    |       |                   | 2x1x40 (int8)   |                 |                                                      |
    | 91    | conv_2d           | 2x1x40 (int8)   | 2x1x120 (int8)  | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 92    | depthwise_conv_2d | 2x1x120 (int8)  | 2x1x120 (int8)  | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 93    | conv_2d           | 2x1x120 (int8)  | 2x1x40 (int8)   | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 94    | add               | 2x1x40 (int8)   | 2x1x40 (int8)   | Activation:Relu                                      |
    |       |                   | 2x1x40 (int8)   |                 |                                                      |
    | 95    | conv_2d           | 2x1x40 (int8)   | 2x1x120 (int8)  | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 96    | depthwise_conv_2d | 2x1x120 (int8)  | 2x1x120 (int8)  | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 97    | conv_2d           | 2x1x120 (int8)  | 2x1x40 (int8)   | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 98    | add               | 2x1x40 (int8)   | 2x1x40 (int8)   | Activation:Relu                                      |
    |       |                   | 2x1x40 (int8)   |                 |                                                      |
    | 99    | conv_2d           | 2x1x40 (int8)   | 2x1x120 (int8)  | Padding:Valid stride:1x1 activation:Relu             |
    |       |                   | 1x1x40 (int8)   |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 100   | depthwise_conv_2d | 2x1x120 (int8)  | 2x1x120 (int8)  | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    |       |                   | 9x1x120 (int8)  |                 |                                                      |
    |       |                   | 120 (int32)     |                 |                                                      |
    | 101   | conv_2d           | 2x1x120 (int8)  | 2x1x40 (int8)   | Padding:Valid stride:1x1 activation:None             |
    |       |                   | 1x1x120 (int8)  |                 |                                                      |
    |       |                   | 40 (int32)      |                 |                                                      |
    | 102   | add               | 2x1x40 (int8)   | 2x1x40 (int8)   | Activation:Relu                                      |
    |       |                   | 2x1x40 (int8)   |                 |                                                      |
    | 103   | average_pool_2d   | 2x1x40 (int8)   | 1x1x40 (int8)   | Padding:Valid stride:1x2 filter:1x2 activation:None  |
    | 104   | reshape           | 1x1x40 (int8)   | 40 (int8)       | Type=none                                            |
    |       |                   | 2 (int32)       |                 |                                                      |
    | 105   | fully_connected   | 40 (int8)       | 3 (int8)        | Activation:None                                      |
    |       |                   | 40 (int8)       |                 |                                                      |
    |       |                   | 3 (int32)       |                 |                                                      |
    | 106   | softmax           | 3 (int8)        | 3 (int8)        | Type=softmaxoptions                                  |
    +-------+-------------------+-----------------+-----------------+------------------------------------------------------+
    Total MACs: 6.116 M
    Total OPs: 12.380 M
    Name: keyword_spotting_on_off_v3
    Version: 2
    Description: Keyword spotting classifier to detect: on, off
    Classes: on, off, _unknown_
    Runtime memory size (RAM): 97.312 k
    hash: ec453c2e09670f7971bb728f4de7d122
    date: 2023-06-19T21:46:38.660Z
    fe.sample_rate_hz: 16000
    fe.fft_length: 512
    fe.sample_length_ms: 1000
    fe.window_size_ms: 30
    fe.window_step_ms: 10
    fe.filterbank_n_channels: 104
    fe.filterbank_upper_band_limit: 7500.0
    fe.filterbank_lower_band_limit: 125.0
    fe.noise_reduction_enable: True
    fe.noise_reduction_smoothing_bits: 10
    fe.noise_reduction_even_smoothing: 0.02500000037252903
    fe.noise_reduction_odd_smoothing: 0.05999999865889549
    fe.noise_reduction_min_signal_remaining: 0.4000000059604645
    fe.pcan_enable: False
    fe.pcan_strength: 0.949999988079071
    fe.pcan_offset: 80.0
    fe.pcan_gain_bits: 21
    fe.log_scale_enable: True
    fe.log_scale_shift: 6
    fe.activity_detection_enable: False
    fe.activity_detection_alpha_a: 0.5
    fe.activity_detection_alpha_b: 0.800000011920929
    fe.activity_detection_arm_threshold: 0.75
    fe.activity_detection_trip_threshold: 0.800000011920929
    fe.dc_notch_filter_enable: True
    fe.dc_notch_filter_coefficient: 0.949999988079071
    fe.quantize_dynamic_scale_enable: True
    fe.quantize_dynamic_scale_range_db: 40.0
    average_window_duration_ms: 300
    detection_threshold_list: [242, 242, 255]
    suppression_ms: 700
    minimum_count: 2
    volume_gain: 0.0
    latency_ms: 10
    verbose_model_output_logs: False
    .tflite file size: 533.3kB


Model Profiling Report
-----------------------

.. code-block:: shell

   # Profile on physical EFR32xG24 using MVP accelerator
   mltk profile keyword_spotting_on_off_v3 --device --accelerator MVP

    Profiling Summary
    Name: keyword_spotting_on_off_v3
    Accelerator: MVP
    Input Shape: 1x98x1x104
    Input Data Type: int8
    Output Shape: 1x3
    Output Data Type: int8
    Flash, Model File Size (bytes): 531.7k
    RAM, Runtime Memory Size (bytes): 84.8k
    Operation Count: 12.6M
    Multiply-Accumulate Count: 6.1M
    Layer Count: 107
    Unsupported Layer Count: 0
    Accelerator Cycle Count: 5.3M
    CPU Cycle Count: 1.0M
    CPU Utilization (%): 17.5
    Clock Rate (hz): 78.0M
    Time (s): 75.0m
    Ops/s: 168.1M
    MACs/s: 81.5M
    Inference/s: 13.3

    Model Layers
    +-------+-------------------+--------+--------+------------+------------+----------+--------------------------+--------------+------------------------------------------------------+
    | Index | OpCode            | # Ops  | # MACs | Acc Cycles | CPU Cycles | Time (s) | Input Shape              | Output Shape | Options                                              |
    +-------+-------------------+--------+--------+------------+------------+----------+--------------------------+--------------+------------------------------------------------------+
    | 0     | conv_2d           | 2.5M   | 1.2M   | 928.8k     | 11.3k      | 11.8m    | 1x98x1x104,40x3x1x104,40 | 1x98x1x40    | Padding:Same stride:1x1 activation:None              |
    | 1     | conv_2d           | 976.1k | 470.4k | 390.2k     | 5.3k       | 5.0m     | 1x98x1x40,120x1x1x40,120 | 1x98x1x120   | Padding:Valid stride:1x1 activation:Relu             |
    | 2     | depthwise_conv_2d | 123.5k | 52.9k  | 96.4k      | 78.7k      | 1.6m     | 1x98x1x120,1x9x1x120,120 | 1x49x1x120   | Multiplier:1 padding:Same stride:2x2 activation:Relu |
    | 3     | conv_2d           | 472.4k | 235.2k | 186.4k     | 5.3k       | 2.4m     | 1x49x1x120,40x1x1x120,40 | 1x49x1x40    | Padding:Valid stride:1x1 activation:None             |
    | 4     | conv_2d           | 162.7k | 78.4k  | 66.7k      | 5.2k       | 870.0u   | 1x98x1x40,40x1x1x40,40   | 1x49x1x40    | Padding:Same stride:2x2 activation:Relu              |
    | 5     | add               | 2.0k   | 0      | 6.9k       | 2.7k       | 120.0u   | 1x49x1x40,1x49x1x40      | 1x49x1x40    | Activation:Relu                                      |
    | 6     | conv_2d           | 488.0k | 235.2k | 195.2k     | 5.3k       | 2.5m     | 1x49x1x40,120x1x1x40,120 | 1x49x1x120   | Padding:Valid stride:1x1 activation:Relu             |
    | 7     | depthwise_conv_2d | 123.5k | 52.9k  | 94.5k      | 78.5k      | 1.6m     | 1x49x1x120,1x9x1x120,120 | 1x49x1x120   | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 8     | conv_2d           | 472.4k | 235.2k | 186.4k     | 5.3k       | 2.4m     | 1x49x1x120,40x1x1x120,40 | 1x49x1x40    | Padding:Valid stride:1x1 activation:None             |
    | 9     | add               | 2.0k   | 0      | 6.9k       | 2.6k       | 120.0u   | 1x49x1x40,1x49x1x40      | 1x49x1x40    | Activation:Relu                                      |
    | 10    | conv_2d           | 488.0k | 235.2k | 195.2k     | 5.3k       | 2.5m     | 1x49x1x40,120x1x1x40,120 | 1x49x1x120   | Padding:Valid stride:1x1 activation:Relu             |
    | 11    | depthwise_conv_2d | 123.5k | 52.9k  | 94.5k      | 78.5k      | 1.6m     | 1x49x1x120,1x9x1x120,120 | 1x49x1x120   | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 12    | conv_2d           | 472.4k | 235.2k | 186.4k     | 5.3k       | 2.4m     | 1x49x1x120,40x1x1x120,40 | 1x49x1x40    | Padding:Valid stride:1x1 activation:None             |
    | 13    | add               | 2.0k   | 0      | 6.9k       | 2.6k       | 90.0u    | 1x49x1x40,1x49x1x40      | 1x49x1x40    | Activation:Relu                                      |
    | 14    | conv_2d           | 488.0k | 235.2k | 195.2k     | 5.3k       | 2.5m     | 1x49x1x40,120x1x1x40,120 | 1x49x1x120   | Padding:Valid stride:1x1 activation:Relu             |
    | 15    | depthwise_conv_2d | 123.5k | 52.9k  | 94.5k      | 78.5k      | 1.6m     | 1x49x1x120,1x9x1x120,120 | 1x49x1x120   | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 16    | conv_2d           | 472.4k | 235.2k | 186.4k     | 5.3k       | 2.4m     | 1x49x1x120,40x1x1x120,40 | 1x49x1x40    | Padding:Valid stride:1x1 activation:None             |
    | 17    | add               | 2.0k   | 0      | 6.9k       | 2.6k       | 120.0u   | 1x49x1x40,1x49x1x40      | 1x49x1x40    | Activation:Relu                                      |
    | 18    | conv_2d           | 488.0k | 235.2k | 195.7k     | 5.3k       | 2.5m     | 1x49x1x40,120x1x1x40,120 | 1x49x1x120   | Padding:Valid stride:1x1 activation:Relu             |
    | 19    | depthwise_conv_2d | 63.0k  | 27.0k  | 47.9k      | 40.6k      | 840.0u   | 1x49x1x120,1x9x1x120,120 | 1x25x1x120   | Multiplier:1 padding:Same stride:2x2 activation:Relu |
    | 20    | conv_2d           | 241.0k | 120.0k | 94.9k      | 5.3k       | 1.2m     | 1x25x1x120,40x1x1x120,40 | 1x25x1x40    | Padding:Valid stride:1x1 activation:None             |
    | 21    | conv_2d           | 83.0k  | 40.0k  | 34.2k      | 5.2k       | 480.0u   | 1x49x1x40,40x1x1x40,40   | 1x25x1x40    | Padding:Same stride:2x2 activation:Relu              |
    | 22    | add               | 1.0k   | 0      | 3.5k       | 2.6k       | 90.0u    | 1x25x1x40,1x25x1x40      | 1x25x1x40    | Activation:Relu                                      |
    | 23    | conv_2d           | 249.0k | 120.0k | 99.9k      | 5.3k       | 1.3m     | 1x25x1x40,120x1x1x40,120 | 1x25x1x120   | Padding:Valid stride:1x1 activation:Relu             |
    | 24    | depthwise_conv_2d | 63.0k  | 27.0k  | 46.4k      | 40.5k      | 810.0u   | 1x25x1x120,1x9x1x120,120 | 1x25x1x120   | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 25    | conv_2d           | 241.0k | 120.0k | 94.9k      | 5.3k       | 1.2m     | 1x25x1x120,40x1x1x120,40 | 1x25x1x40    | Padding:Valid stride:1x1 activation:None             |
    | 26    | add               | 1.0k   | 0      | 3.5k       | 2.6k       | 60.0u    | 1x25x1x40,1x25x1x40      | 1x25x1x40    | Activation:Relu                                      |
    | 27    | conv_2d           | 249.0k | 120.0k | 99.9k      | 5.3k       | 1.3m     | 1x25x1x40,120x1x1x40,120 | 1x25x1x120   | Padding:Valid stride:1x1 activation:Relu             |
    | 28    | depthwise_conv_2d | 63.0k  | 27.0k  | 46.4k      | 40.5k      | 810.0u   | 1x25x1x120,1x9x1x120,120 | 1x25x1x120   | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 29    | conv_2d           | 241.0k | 120.0k | 94.9k      | 5.3k       | 1.3m     | 1x25x1x120,40x1x1x120,40 | 1x25x1x40    | Padding:Valid stride:1x1 activation:None             |
    | 30    | add               | 1.0k   | 0      | 3.5k       | 2.6k       | 60.0u    | 1x25x1x40,1x25x1x40      | 1x25x1x40    | Activation:Relu                                      |
    | 31    | conv_2d           | 249.0k | 120.0k | 99.9k      | 5.3k       | 1.3m     | 1x25x1x40,120x1x1x40,120 | 1x25x1x120   | Padding:Valid stride:1x1 activation:Relu             |
    | 32    | depthwise_conv_2d | 63.0k  | 27.0k  | 46.4k      | 40.5k      | 810.0u   | 1x25x1x120,1x9x1x120,120 | 1x25x1x120   | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 33    | conv_2d           | 241.0k | 120.0k | 94.9k      | 5.3k       | 1.2m     | 1x25x1x120,40x1x1x120,40 | 1x25x1x40    | Padding:Valid stride:1x1 activation:None             |
    | 34    | add               | 1.0k   | 0      | 3.5k       | 2.6k       | 90.0u    | 1x25x1x40,1x25x1x40      | 1x25x1x40    | Activation:Relu                                      |
    | 35    | conv_2d           | 249.0k | 120.0k | 99.9k      | 5.3k       | 1.3m     | 1x25x1x40,120x1x1x40,120 | 1x25x1x120   | Padding:Valid stride:1x1 activation:Relu             |
    | 36    | depthwise_conv_2d | 32.8k  | 14.0k  | 23.8k      | 21.6k      | 420.0u   | 1x25x1x120,1x9x1x120,120 | 1x13x1x120   | Multiplier:1 padding:Same stride:2x2 activation:Relu |
    | 37    | conv_2d           | 125.3k | 62.4k  | 49.2k      | 5.3k       | 690.0u   | 1x13x1x120,40x1x1x120,40 | 1x13x1x40    | Padding:Valid stride:1x1 activation:None             |
    | 38    | conv_2d           | 43.2k  | 20.8k  | 17.7k      | 5.2k       | 270.0u   | 1x25x1x40,40x1x1x40,40   | 1x13x1x40    | Padding:Same stride:2x2 activation:Relu              |
    | 39    | add               | 520.0  | 0      | 1.8k       | 2.6k       | 60.0u    | 1x13x1x40,1x13x1x40      | 1x13x1x40    | Activation:Relu                                      |
    | 40    | conv_2d           | 129.5k | 62.4k  | 51.9k      | 5.3k       | 720.0u   | 1x13x1x40,120x1x1x40,120 | 1x13x1x120   | Padding:Valid stride:1x1 activation:Relu             |
    | 41    | depthwise_conv_2d | 32.8k  | 14.0k  | 22.4k      | 21.6k      | 420.0u   | 1x13x1x120,1x9x1x120,120 | 1x13x1x120   | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 42    | conv_2d           | 125.3k | 62.4k  | 49.2k      | 5.3k       | 690.0u   | 1x13x1x120,40x1x1x120,40 | 1x13x1x40    | Padding:Valid stride:1x1 activation:None             |
    | 43    | add               | 520.0  | 0      | 1.8k       | 2.6k       | 60.0u    | 1x13x1x40,1x13x1x40      | 1x13x1x40    | Activation:Relu                                      |
    | 44    | conv_2d           | 129.5k | 62.4k  | 51.9k      | 5.3k       | 720.0u   | 1x13x1x40,120x1x1x40,120 | 1x13x1x120   | Padding:Valid stride:1x1 activation:Relu             |
    | 45    | depthwise_conv_2d | 32.8k  | 14.0k  | 22.4k      | 21.6k      | 390.0u   | 1x13x1x120,1x9x1x120,120 | 1x13x1x120   | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 46    | conv_2d           | 125.3k | 62.4k  | 49.2k      | 5.3k       | 690.0u   | 1x13x1x120,40x1x1x120,40 | 1x13x1x40    | Padding:Valid stride:1x1 activation:None             |
    | 47    | add               | 520.0  | 0      | 1.8k       | 2.6k       | 60.0u    | 1x13x1x40,1x13x1x40      | 1x13x1x40    | Activation:Relu                                      |
    | 48    | conv_2d           | 129.5k | 62.4k  | 51.9k      | 5.3k       | 720.0u   | 1x13x1x40,120x1x1x40,120 | 1x13x1x120   | Padding:Valid stride:1x1 activation:Relu             |
    | 49    | depthwise_conv_2d | 32.8k  | 14.0k  | 22.4k      | 21.6k      | 420.0u   | 1x13x1x120,1x9x1x120,120 | 1x13x1x120   | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 50    | conv_2d           | 125.3k | 62.4k  | 49.2k      | 5.3k       | 660.0u   | 1x13x1x120,40x1x1x120,40 | 1x13x1x40    | Padding:Valid stride:1x1 activation:None             |
    | 51    | add               | 520.0  | 0      | 1.8k       | 2.6k       | 30.0u    | 1x13x1x40,1x13x1x40      | 1x13x1x40    | Activation:Relu                                      |
    | 52    | conv_2d           | 129.5k | 62.4k  | 52.0k      | 5.3k       | 690.0u   | 1x13x1x40,120x1x1x40,120 | 1x13x1x120   | Padding:Valid stride:1x1 activation:Relu             |
    | 53    | depthwise_conv_2d | 17.6k  | 7.6k   | 11.8k      | 12.1k      | 210.0u   | 1x13x1x120,1x9x1x120,120 | 1x7x1x120    | Multiplier:1 padding:Same stride:2x2 activation:Relu |
    | 54    | conv_2d           | 67.5k  | 33.6k  | 26.7k      | 5.3k       | 390.0u   | 1x7x1x120,40x1x1x120,40  | 1x7x1x40     | Padding:Valid stride:1x1 activation:None             |
    | 55    | conv_2d           | 23.2k  | 11.2k  | 9.7k       | 5.2k       | 180.0u   | 1x13x1x40,40x1x1x40,40   | 1x7x1x40     | Padding:Same stride:2x2 activation:Relu              |
    | 56    | add               | 280.0  | 0      | 992.0      | 2.6k       | 30.0u    | 1x7x1x40,1x7x1x40        | 1x7x1x40     | Activation:Relu                                      |
    | 57    | conv_2d           | 69.7k  | 33.6k  | 28.1k      | 5.3k       | 420.0u   | 1x7x1x40,120x1x1x40,120  | 1x7x1x120    | Padding:Valid stride:1x1 activation:Relu             |
    | 58    | depthwise_conv_2d | 17.6k  | 7.6k   | 10.3k      | 12.1k      | 210.0u   | 1x7x1x120,1x9x1x120,120  | 1x7x1x120    | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 59    | conv_2d           | 67.5k  | 33.6k  | 26.7k      | 5.3k       | 390.0u   | 1x7x1x120,40x1x1x120,40  | 1x7x1x40     | Padding:Valid stride:1x1 activation:None             |
    | 60    | add               | 280.0  | 0      | 992.0      | 2.6k       | 30.0u    | 1x7x1x40,1x7x1x40        | 1x7x1x40     | Activation:Relu                                      |
    | 61    | conv_2d           | 69.7k  | 33.6k  | 28.0k      | 5.3k       | 420.0u   | 1x7x1x40,120x1x1x40,120  | 1x7x1x120    | Padding:Valid stride:1x1 activation:Relu             |
    | 62    | depthwise_conv_2d | 17.6k  | 7.6k   | 10.3k      | 12.1k      | 210.0u   | 1x7x1x120,1x9x1x120,120  | 1x7x1x120    | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 63    | conv_2d           | 67.5k  | 33.6k  | 26.7k      | 5.3k       | 390.0u   | 1x7x1x120,40x1x1x120,40  | 1x7x1x40     | Padding:Valid stride:1x1 activation:None             |
    | 64    | add               | 280.0  | 0      | 992.0      | 2.6k       | 30.0u    | 1x7x1x40,1x7x1x40        | 1x7x1x40     | Activation:Relu                                      |
    | 65    | conv_2d           | 69.7k  | 33.6k  | 28.1k      | 5.3k       | 420.0u   | 1x7x1x40,120x1x1x40,120  | 1x7x1x120    | Padding:Valid stride:1x1 activation:Relu             |
    | 66    | depthwise_conv_2d | 17.6k  | 7.6k   | 10.3k      | 12.1k      | 210.0u   | 1x7x1x120,1x9x1x120,120  | 1x7x1x120    | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 67    | conv_2d           | 67.5k  | 33.6k  | 26.7k      | 5.3k       | 390.0u   | 1x7x1x120,40x1x1x120,40  | 1x7x1x40     | Padding:Valid stride:1x1 activation:None             |
    | 68    | add               | 280.0  | 0      | 992.0      | 2.6k       | 30.0u    | 1x7x1x40,1x7x1x40        | 1x7x1x40     | Activation:Relu                                      |
    | 69    | conv_2d           | 69.7k  | 33.6k  | 28.1k      | 5.3k       | 390.0u   | 1x7x1x40,120x1x1x40,120  | 1x7x1x120    | Padding:Valid stride:1x1 activation:Relu             |
    | 70    | depthwise_conv_2d | 10.1k  | 4.3k   | 5.8k       | 7.4k       | 120.0u   | 1x7x1x120,1x9x1x120,120  | 1x4x1x120    | Multiplier:1 padding:Same stride:2x2 activation:Relu |
    | 71    | conv_2d           | 38.6k  | 19.2k  | 15.3k      | 5.3k       | 240.0u   | 1x4x1x120,40x1x1x120,40  | 1x4x1x40     | Padding:Valid stride:1x1 activation:None             |
    | 72    | conv_2d           | 13.3k  | 6.4k   | 5.6k       | 5.2k       | 120.0u   | 1x7x1x40,40x1x1x40,40    | 1x4x1x40     | Padding:Same stride:2x2 activation:Relu              |
    | 73    | add               | 160.0  | 0      | 572.0      | 2.6k       | 30.0u    | 1x4x1x40,1x4x1x40        | 1x4x1x40     | Activation:Relu                                      |
    | 74    | conv_2d           | 39.8k  | 19.2k  | 16.1k      | 5.3k       | 240.0u   | 1x4x1x40,120x1x1x40,120  | 1x4x1x120    | Padding:Valid stride:1x1 activation:Relu             |
    | 75    | depthwise_conv_2d | 10.1k  | 4.3k   | 4.3k       | 7.3k       | 90.0u    | 1x4x1x120,1x9x1x120,120  | 1x4x1x120    | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 76    | conv_2d           | 38.6k  | 19.2k  | 15.3k      | 5.3k       | 270.0u   | 1x4x1x120,40x1x1x120,40  | 1x4x1x40     | Padding:Valid stride:1x1 activation:None             |
    | 77    | add               | 160.0  | 0      | 572.0      | 2.6k       | 30.0u    | 1x4x1x40,1x4x1x40        | 1x4x1x40     | Activation:Relu                                      |
    | 78    | conv_2d           | 39.8k  | 19.2k  | 16.1k      | 5.3k       | 270.0u   | 1x4x1x40,120x1x1x40,120  | 1x4x1x120    | Padding:Valid stride:1x1 activation:Relu             |
    | 79    | depthwise_conv_2d | 10.1k  | 4.3k   | 4.3k       | 7.3k       | 120.0u   | 1x4x1x120,1x9x1x120,120  | 1x4x1x120    | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 80    | conv_2d           | 38.6k  | 19.2k  | 15.3k      | 5.3k       | 270.0u   | 1x4x1x120,40x1x1x120,40  | 1x4x1x40     | Padding:Valid stride:1x1 activation:None             |
    | 81    | add               | 160.0  | 0      | 572.0      | 2.6k       | 30.0u    | 1x4x1x40,1x4x1x40        | 1x4x1x40     | Activation:Relu                                      |
    | 82    | conv_2d           | 39.8k  | 19.2k  | 16.1k      | 5.3k       | 270.0u   | 1x4x1x40,120x1x1x40,120  | 1x4x1x120    | Padding:Valid stride:1x1 activation:Relu             |
    | 83    | depthwise_conv_2d | 10.1k  | 4.3k   | 4.3k       | 7.3k       | 120.0u   | 1x4x1x120,1x9x1x120,120  | 1x4x1x120    | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 84    | conv_2d           | 38.6k  | 19.2k  | 15.3k      | 5.3k       | 270.0u   | 1x4x1x120,40x1x1x120,40  | 1x4x1x40     | Padding:Valid stride:1x1 activation:None             |
    | 85    | add               | 160.0  | 0      | 572.0      | 2.6k       | 30.0u    | 1x4x1x40,1x4x1x40        | 1x4x1x40     | Activation:Relu                                      |
    | 86    | conv_2d           | 39.8k  | 19.2k  | 16.1k      | 5.3k       | 270.0u   | 1x4x1x40,120x1x1x40,120  | 1x4x1x120    | Padding:Valid stride:1x1 activation:Relu             |
    | 87    | depthwise_conv_2d | 5.0k   | 2.2k   | 2.1k       | 4.2k       | 60.0u    | 1x4x1x120,1x9x1x120,120  | 1x2x1x120    | Multiplier:1 padding:Same stride:2x2 activation:Relu |
    | 88    | conv_2d           | 19.3k  | 9.6k   | 7.7k       | 5.3k       | 150.0u   | 1x2x1x120,40x1x1x120,40  | 1x2x1x40     | Padding:Valid stride:1x1 activation:None             |
    | 89    | conv_2d           | 6.6k   | 3.2k   | 2.8k       | 5.2k       | 90.0u    | 1x4x1x40,40x1x1x40,40    | 1x2x1x40     | Padding:Same stride:2x2 activation:Relu              |
    | 90    | add               | 80.0   | 0      | 292.0      | 2.6k       | 60.0u    | 1x2x1x40,1x2x1x40        | 1x2x1x40     | Activation:Relu                                      |
    | 91    | conv_2d           | 19.9k  | 9.6k   | 8.1k       | 5.3k       | 150.0u   | 1x2x1x40,120x1x1x40,120  | 1x2x1x120    | Padding:Valid stride:1x1 activation:Relu             |
    | 92    | depthwise_conv_2d | 5.0k   | 2.2k   | 1.4k       | 4.1k       | 60.0u    | 1x2x1x120,1x9x1x120,120  | 1x2x1x120    | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 93    | conv_2d           | 19.3k  | 9.6k   | 7.7k       | 5.3k       | 150.0u   | 1x2x1x120,40x1x1x120,40  | 1x2x1x40     | Padding:Valid stride:1x1 activation:None             |
    | 94    | add               | 80.0   | 0      | 292.0      | 2.6k       | 30.0u    | 1x2x1x40,1x2x1x40        | 1x2x1x40     | Activation:Relu                                      |
    | 95    | conv_2d           | 19.9k  | 9.6k   | 8.1k       | 5.3k       | 180.0u   | 1x2x1x40,120x1x1x40,120  | 1x2x1x120    | Padding:Valid stride:1x1 activation:Relu             |
    | 96    | depthwise_conv_2d | 5.0k   | 2.2k   | 1.4k       | 4.1k       | 60.0u    | 1x2x1x120,1x9x1x120,120  | 1x2x1x120    | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 97    | conv_2d           | 19.3k  | 9.6k   | 7.7k       | 5.3k       | 180.0u   | 1x2x1x120,40x1x1x120,40  | 1x2x1x40     | Padding:Valid stride:1x1 activation:None             |
    | 98    | add               | 80.0   | 0      | 292.0      | 2.6k       | 30.0u    | 1x2x1x40,1x2x1x40        | 1x2x1x40     | Activation:Relu                                      |
    | 99    | conv_2d           | 19.9k  | 9.6k   | 8.1k       | 5.3k       | 180.0u   | 1x2x1x40,120x1x1x40,120  | 1x2x1x120    | Padding:Valid stride:1x1 activation:Relu             |
    | 100   | depthwise_conv_2d | 5.0k   | 2.2k   | 1.4k       | 4.1k       | 60.0u    | 1x2x1x120,1x9x1x120,120  | 1x2x1x120    | Multiplier:1 padding:Same stride:1x1 activation:Relu |
    | 101   | conv_2d           | 19.3k  | 9.6k   | 7.7k       | 5.3k       | 150.0u   | 1x2x1x120,40x1x1x120,40  | 1x2x1x40     | Padding:Valid stride:1x1 activation:None             |
    | 102   | add               | 80.0   | 0      | 292.0      | 2.6k       | 60.0u    | 1x2x1x40,1x2x1x40        | 1x2x1x40     | Activation:Relu                                      |
    | 103   | average_pool_2d   | 120.0  | 0      | 114.0      | 3.8k       | 30.0u    | 1x2x1x40                 | 1x1x1x40     | Padding:Valid stride:1x2 filter:1x2 activation:None  |
    | 104   | reshape           | 0      | 0      | 0          | 640.0      | 30.0u    | 1x1x1x40,2               | 1x40         | Type=none                                            |
    | 105   | fully_connected   | 243.0  | 120.0  | 214.0      | 2.1k       | 30.0u    | 1x40,3x40,3              | 1x3          | Activation:None                                      |
    | 106   | softmax           | 15.0   | 0      | 0          | 3.0k       | 30.0u    | 1x3                      | 1x3          | Type=softmaxoptions                                  |
    +-------+-------------------+--------+--------+------------+------------+----------+--------------------------+--------------+------------------------------------------------------+

Model Diagram
------------------

.. code-block:: shell

   mltk view keyword_spotting_on_off_v3 --tflite

.. raw:: html

    <div class="model-diagram">
        <a href="../../../../_images/models/keyword_spotting_on_off_v3.tflite.png" target="_blank">
            <img src="../../../../_images/models/keyword_spotting_on_off_v3.tflite.png" />
            <p>Click to enlarge</p>
        </a>
    </div>


Commands
--------------

.. code-block:: shell

   # Do a "dry run" test training of the model
   mltk train keyword_spotting_on_off_v3-test

   # Train the model
   mltk train keyword_spotting_on_off_v3

   # Evaluate the trained model .tflite model
   mltk evaluate keyword_spotting_on_off_v3 --tflite

   # Profile the model in the MVP hardware accelerator simulator
   mltk profile keyword_spotting_on_off_v3 --accelerator MVP --estimates

   # Profile the model on a physical development board
   mltk profile keyword_spotting_on_off_v3  --accelerator MVP --device

   # Run the model in the audio classifier on the local PC
   mltk classify_audio keyword_spotting_on_off_v3 --verbose

   # Run the model in the audio classifier on the physical device
   mltk classify_audio keyword_spotting_on_off_v3 --device --verbose --accelerator MVP


Model Specification
---------------------

..  literalinclude:: ../../../../../../../mltk/models/siliconlabs/keyword_spotting_on_off_v3.py
    :language: python
    :lines: 645-

"""
# pylint: disable=redefined-outer-name

# Import the Tensorflow packages
# required to build the model layout
import os
import math
from typing import Tuple, Dict, List

import numpy as np
import tensorflow as tf
import mltk.core as mltk_core

# Import the AudioFeatureGeneratorSettings which we'll configure
from mltk.core.preprocess.audio.audio_feature_generator import AudioFeatureGeneratorSettings
from mltk.core.preprocess.utils import tf_dataset as tf_dataset_utils
from mltk.core.preprocess.utils import audio as audio_utils
from mltk.core.preprocess.utils import image as image_utils
from mltk.core.keras.callbacks import SteppedLearnRateScheduler
from mltk.utils.path import create_user_dir
from mltk.core.preprocess.utils import (split_file_list, shuffle_file_list_by_group)
from mltk.utils.python import install_pip_package
from mltk.models.shared import tenet
from mltk.datasets import audio as audio_datasets


##########################################################################################
# Instantiate the MltkModel instance
#

# @mltk_model
class MyModel(
    mltk_core.MltkModel,    # We must inherit the MltkModel class
    mltk_core.TrainMixin,   # We also inherit the TrainMixin since we want to train this model
    mltk_core.DatasetMixin, # We also need the DatasetMixin mixin to provide the relevant dataset properties
    mltk_core.EvaluateClassifierMixin,  # While not required, also inherit EvaluateClassifierMixin to help will generating evaluation stats for our classification model
):
    pass
# Instantiate our custom model object
# The rest of this script simply configures the properties
# of our custom model object
my_model = MyModel()

##########################################################################################
# General Settings

# For better tracking, the version should be incremented any time a non-trivial change is made
# NOTE: The version is optional and not used directly used by the MLTK
my_model.version = 2
# Provide a brief description about what this model models
# This description goes in the "description" field of the .tflite model file
my_model.description = 'Keyword spotting classifier to detect: on, off'


##########################################################################################
# Training Basic Settings

# This specifies the number of times we run the training.
# We just set this to a large value since we're using SteppedLearnRateScheduler
# to control when training completes
my_model.epochs = 9999
# Specify how many samples to pass through the model
# before updating the training gradients.
# Typical values are 10-64
# NOTE: Larger values require more memory and may not fit on your GPU
my_model.batch_size = 100



##########################################################################################
# Training callback Settings
#


# The MLTK enables the tf.keras.callbacks.ModelCheckpoint by default.
my_model.checkpoint['monitor'] =  'val_accuracy'


# We use a custom learn rate schedule that is defined in:
# https://github.com/google-research/google-research/tree/master/kws_streaming
my_model.train_callbacks = [
    tf.keras.callbacks.TerminateOnNaN(),
    SteppedLearnRateScheduler([
        (100,   .001),
        (100,   .002),
        (100,   .003),
        (100,   .004),
        (10000, .005),
        (10000, .002),
        (5000, .0005),
        (5000, 1e-5),
        (5000,  1e-6),
        (5000,  1e-7),
    ] )
]

##########################################################################################
# TF-Lite converter settings
#

# These are the settings used to quantize the model
# We want all the internal ops as well as
# model input/output to be int8
my_model.tflite_converter['optimizations'] = [tf.lite.Optimize.DEFAULT]
my_model.tflite_converter['supported_ops'] = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
my_model.tflite_converter['inference_input_type'] = np.int8
my_model.tflite_converter['inference_output_type'] = np.int8
# Automatically generate a representative dataset from the validation data
my_model.tflite_converter['representative_dataset'] = 'generate'



##########################################################################################
# Define the model architecture
#

def my_model_builder(model: MyModel) -> tf.keras.Model:
    """Build the Keras model
    """
    input_shape = model.input_shape
    # NOTE: This model requires the input shape: <time, 1, features>
    #       while the embedded device expects: <time, features, 1>
    #       Since the <time> axis is still row-major, we can swap the <features> with 1 without issue
    time_size, feature_size, _ = input_shape
    input_shape = (time_size, 1, feature_size)

    keras_model = tenet.TENet12(
        input_shape=input_shape,
        classes=model.n_classes,
        channels=40,
        blocks=6,
    )

    keras_model.compile(
        loss='categorical_crossentropy',
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001, epsilon=1e-8),
        metrics= ['accuracy']
    )

    return keras_model

my_model.build_model_function = my_model_builder
# TENet uses a custom layer, be sure to add it to the keras_custom_objects
# so that we can load the corresponding .h5 model file
my_model.keras_custom_objects['MultiScaleTemporalConvolution'] = tenet.MultiScaleTemporalConvolution


##########################################################################################
# Specify AudioFeatureGenerator Settings
# See https://siliconlabs.github.io/mltk/docs/audio/audio_feature_generator.html
#
frontend_settings = AudioFeatureGeneratorSettings()

frontend_settings.sample_rate_hz = 16000
frontend_settings.sample_length_ms = 1000                       # A 1s buffer should be enough to capture the keywords
frontend_settings.window_size_ms = 30
frontend_settings.window_step_ms = 10
frontend_settings.filterbank_n_channels = 104                   # We want this value to be as large as possible
                                                                # while still allowing for the ML model to execute efficiently on the hardware
frontend_settings.filterbank_upper_band_limit = 7500.0
frontend_settings.filterbank_lower_band_limit = 125.0           # The dev board mic seems to have a lot of noise at lower frequencies

frontend_settings.noise_reduction_enable = True                 # Enable the noise reduction block to help ignore background noise in the field
frontend_settings.noise_reduction_smoothing_bits = 10
frontend_settings.noise_reduction_even_smoothing =  0.025
frontend_settings.noise_reduction_odd_smoothing = 0.06
frontend_settings.noise_reduction_min_signal_remaining = 0.40   # This value is fairly large (which makes the background noise reduction small)
                                                                # But it has been found to still give good results
                                                                # i.e. There is still some background noise reduction,
                                                                # but the actual signal is still (mostly) untouched

frontend_settings.dc_notch_filter_enable = True                 # Enable the DC notch filter, to help remove the DC signal from the dev board's mic
frontend_settings.dc_notch_filter_coefficient = 0.95

frontend_settings.quantize_dynamic_scale_enable = True          # Enable dynamic quantization, this dynamically converts the uint16 spectrogram to int8
frontend_settings.quantize_dynamic_scale_range_db = 40.0

# Add the Audio Feature generator settings to the model parameters
# This way, they are included in the generated .tflite model file
# See https://siliconlabs.github.io/mltk/docs/guides/model_parameters.html
my_model.model_parameters.update(frontend_settings)


##########################################################################################
# Specify the other dataset settings
#

my_model.input_shape = frontend_settings.spectrogram_shape + (1,)

# Add the keywords plus a _unknown_ meta class
my_model.classes = ['on','off', '_unknown_']
unknown_class_id = my_model.classes.index('_unknown_')

# Ensure the class weights are balanced during training
# https://towardsdatascience.com/why-weight-the-importance-of-training-on-balanced-datasets-f1e54688e7df
my_model.class_weights = 'balanced'



validation_split = 0.15

# Uncomment this to dump the augmented audio samples to the log directory
# DO NOT forget to disable this before training the model as it will generate A LOT of data
#data_dump_dir = my_model.create_log_dir('dataset_dump')

# This is the directory where the dataset will be extracted
dataset_dir = create_user_dir('datasets/on_off')


##########################################################################################
# Create the audio augmentation pipeline
#

# Install the other 3rd party packages required from preprocessing
install_pip_package('audiomentations')

import librosa
import audiomentations


def audio_pipeline_with_augmentations(
    path_batch:np.ndarray,
    label_batch:np.ndarray,
    seed:np.ndarray
) -> np.ndarray:
    """Augment a batch of audio clips and generate spectrograms

    This does the following, for each audio file path in the input batch:
    1. Read audio file
    2. Convolve the sample with a random impulse response
    3. For "unknown" samples, randomly replace with a cropped "known" sample
    4. Adjust its length to fit within the specified length
    5. Apply random augmentations to the audio sample using audiomentations
    6. Convert to the specified sample rate (if necessary)
    7. Generate a spectrogram from the augmented audio sample
    8. Dump the augmented audio and spectrogram (if necessary)

    NOTE: This will be execute in parallel across *separate* subprocesses.

    Arguments:
        path_batch: Batch of audio file paths
        label_batch: Batch of corresponding labels
        seed: Batch of seeds to use for random number generation,
            This ensures that the "random" augmentations are reproducible

    Return:
        Generated batch of spectrograms from augmented audio samples
    """
    batch_length = path_batch.shape[0]
    height, width = frontend_settings.spectrogram_shape
    x_shape = (batch_length, height, 1, width)
    x_batch = np.empty(x_shape, dtype=np.int8)

    # This is the amount of padding we add to the beginning of the sample
    # This allows for "warming up" the noise reduction block
    padding_length_ms = 1000
    padded_frontend_settings = frontend_settings.copy()
    padded_frontend_settings.sample_length_ms += padding_length_ms


    # Load the Impulse Response dataset into RAM once
    # and store in a global variable
    ir_dataset = globals().get('ir_dataset', None)
    if not ir_dataset:
        ir_dataset = audio_datasets.mit_ir_survey.load_dataset(f'{dataset_dir}/_ir_responses_')
        globals()['ir_dataset'] = ir_dataset


    # For each audio sample path in the current batch
    for i, (audio_path, labels) in enumerate(zip(path_batch, label_batch)):
        class_id = np.argmax(labels)
        rstate = np.random.RandomState(seed[i])
        rn = rstate.random()

        # For "unknown" samples,
        # Randomly convert a small percentage of them to "silence" or cropped "known" samples
        current_sample_is_in_unknown_class = class_id == unknown_class_id
        using_silence_as_unknown = current_sample_is_in_unknown_class and rn < 0.03
        use_cropped_sample_as_unknown = current_sample_is_in_unknown_class and not using_silence_as_unknown and rn < 0.15


        # If we should convert this "unknown" sample to silence
        if using_silence_as_unknown:
            original_sample_rate = frontend_settings.sample_rate_hz
            sample = np.zeros((original_sample_rate,), dtype=np.float32)
            audio_path = f'silence-{i}.wav'.encode('utf-8')

        # If we should convert his "unknown" sample to a cropped "known" sample
        elif use_cropped_sample_as_unknown:
            # Find a "known" sample in the current batch
            # Later, we'll crop this sample and use it as an "unknown" sample
            use_cropped_sample_as_unknown = False
            choices = list(range(batch_length))
            rstate.shuffle(choices)
            for choice_index in choices:
                if np.argmax(label_batch[choice_index]) == unknown_class_id:
                    continue

                audio_path = path_batch[choice_index]
                use_cropped_sample_as_unknown = True
                break

        # Read the audio file if it is not "silence"
        if not using_silence_as_unknown:
            try:
                sample, original_sample_rate = audio_utils.read_audio_file(audio_path, return_numpy=True, return_sample_rate=True)
            except Exception as e:
                raise RuntimeError(f'Failed to read: {audio_path}, err: {e}')

            # Applying an Impulse Response (IR)
            # This makes the sample sound like it was capture in a different environment
            # See https://siliconlabs.github.io/mltk/docs/python_api/datasets/audio/mit_ir_survey.html
            if len(sample) < original_sample_rate * 3.0 and rstate.random() < 0.80:
                sample = audio_datasets.mit_ir_survey.apply_random_ir(sample, ir_dataset, seed=seed[i])


        # Create a buffer to hold the padded sample
        padding_length = int((original_sample_rate * padding_length_ms) / 1000)
        padded_sample_length = int((original_sample_rate * padded_frontend_settings.sample_length_ms) / 1000)
        padded_sample = np.zeros((padded_sample_length,), dtype=np.float32)

        # If we want to crop a "known" sample and use it as an unknown sample
        if use_cropped_sample_as_unknown:
            audio_path = f'cropped-{i}.wav'.encode('utf-8')

            # Trim any silence from the "known" sample
            trimmed_sample, _ = librosa.effects.trim(sample, top_db=15)
            # Randomly insert a small percentage of the trimmed sample into padded sample buffer.
            # Note that the entire trimmed sample is actually added to the padded sample buffer
            # However, only the part of the sample that is after padding_length_ms will actually be used.
            # Everything before will eventually be dropped
            trimmed_sample_length = len(trimmed_sample)

            # Ensure the trimmed sample is no longer than 700ms
            if trimmed_sample_length < .7 * original_sample_rate:
                cropped_sample_percent = np.random.uniform(.20, .50)
                cropped_sample_length = int(trimmed_sample_length * cropped_sample_percent)
                # Add the beginning of the sample to the end of the padded sample buffer.
                # This simulates the sample streaming into the audio buffer,
                # but not being fully streamed in when an inference is invoked on the device.
                # In this case, we want the partial sample to be considered "unknown".
                padded_sample[-cropped_sample_length:] += trimmed_sample[:cropped_sample_length]


        else:
            # Adjust the audio clip to the length defined in the frontend_settings
            out_length = int((original_sample_rate * frontend_settings.sample_length_ms) / 1000)
            sample = audio_utils.adjust_length(
                sample,
                out_length=out_length,
                trim_threshold_db=30,
                offset=np.random.uniform(0, 1)
            )
            padded_sample[padding_length:padding_length+len(sample)] += sample



        # Initialize the global audio augmentations instance
        # NOTE: We want this to be global so that we only initialize it once per subprocess
        audio_augmentations = globals().get('audio_augmentations', None)
        if audio_augmentations is None:
            audio_augmentations = audiomentations.Compose(
                p=1.0,
                transforms=[
                audiomentations.Gain(min_gain_in_db=0.95, max_gain_in_db=1.2, p=1.0),
                audiomentations.AddBackgroundNoise(
                    f'{dataset_dir}/_background_noise_/ambient',
                    min_snr_in_db=-1, # The lower the SNR, the louder the background noise
                    max_snr_in_db=35,
                    noise_rms="relative",
                    lru_cache_size=50,
                    p=0.80
                ),
                audiomentations.AddBackgroundNoise(
                    f'{dataset_dir}/_background_noise_/brd2601',
                    min_absolute_rms_in_db=-75.0,
                    max_absolute_rms_in_db=-60.0,
                    noise_rms="absolute",
                    lru_cache_size=50,
                    p=1.0
                ),
                #audiomentations.AddGaussianSNR(min_snr_in_db=25, max_snr_in_db=40, p=0.25),
            ])
            globals()['audio_augmentations'] = audio_augmentations

        # Apply random augmentations to the audio sample
        augmented_sample = audio_augmentations(padded_sample, original_sample_rate)

        # Convert the sample rate (if necessary)
        if original_sample_rate != frontend_settings.sample_rate_hz:
            augmented_sample = audio_utils.resample(
                augmented_sample,
                orig_sr=original_sample_rate,
                target_sr=frontend_settings.sample_rate_hz
            )

        # Ensure the sample values are within (-1,1)
        augmented_sample = np.clip(augmented_sample, -1.0, 1.0)

        # Generate a spectrogram from the augmented audio sample
        spectrogram = audio_utils.apply_frontend(
            sample=augmented_sample,
            settings=padded_frontend_settings,
            dtype=np.int8
        )

        # The input audio sample was padded with padding_length_ms of background noise
        # Drop the padded background noise from the final spectrogram used for training
        spectrogram = spectrogram[-height:, :]
        # The output spectrogram is 2D, add a channel dimension to make it 3D:
        # (height, width, channels=1)

        # Convert the spectrogram dimension from
        # <time, features> to
        # <time, 1, features>
        spectrogram = np.expand_dims(spectrogram, axis=-2)

        x_batch[i] = spectrogram

        # Dump the augmented audio sample AND corresponding spectrogram (if necessary)
        data_dump_dir = globals().get('data_dump_dir', None)
        if data_dump_dir:
            try:
                from cv2 import cv2
            except:
                import cv2

            fn = os.path.basename(audio_path.decode('utf-8'))

            audio_dump_path = f'{data_dump_dir}/{class_id}-{fn[:-4]}-{seed[0]}.wav'
            spectrogram_dumped = np.squeeze(spectrogram, axis=-2)
            # Transpose to put the time on the x-axis
            spectrogram_dumped = np.transpose(spectrogram_dumped)
            # Convert from int8 to uint8
            spectrogram_dumped = np.clip(spectrogram_dumped +128, 0, 255)
            spectrogram_dumped = spectrogram_dumped.astype(np.uint8)
            # Increase the size of the spectrogram to make it easier to see as a jpeg
            spectrogram_dumped = cv2.resize(spectrogram_dumped, (height*3,width*3))

            valid_sample_length = int((frontend_settings.sample_length_ms * frontend_settings.sample_rate_hz) / 1000)
            valid_augmented_sample = augmented_sample[-valid_sample_length:]
            audio_dump_path = audio_utils.write_audio_file(
                audio_dump_path,
                valid_augmented_sample,
                sample_rate=frontend_settings.sample_rate_hz
            )
            image_dump_path = audio_dump_path.replace('.wav', '.jpg')
            jpg_data = cv2.applyColorMap(spectrogram_dumped, cv2.COLORMAP_HOT)
            cv2.imwrite(image_dump_path, jpg_data)


    return x_batch


##########################################################################################
# Define the MltkDataset object
# NOTE: This class is optional but is useful for organizing the code
#
class MyDataset(mltk_core.MltkDataset):

    def __init__(self):
        super().__init__()
        self.pools = []
        self.summary = ''

    def summarize_dataset(self) -> str:
        """Return a string summary of the dataset"""
        s = self.summary
        s += mltk_core.MltkDataset.summarize_class_counts(my_model.class_counts)
        return s


    def load_dataset(
        self,
        subset: str,
        test:bool = False,
        **kwargs
    ) -> Tuple[tf.data.Dataset, None, tf.data.Dataset]:
        """Load the dataset subset

        This is called automatically by the MLTK before training
        or evaluation.

        Args:
            subset: The dataset subset to return: 'training' or 'evaluation'
            test: This is optional, it is used when invoking a training "dryrun", e.g.: mltk train audio_tf_dataset-test
                If this is true, then only return a small portion of the dataset for testing purposes

        Return:
            if subset == training:
                A tuple, (train_dataset, None, validation_dataset)
            else:
                validation_dataset
        """

        if subset == 'training':
            x = self.load_subset('training', test=test)
            validation_data = self.load_subset('validation', test=test)

            return x, None, validation_data

        else:
            x = self.load_subset('validation', test=test)
            return x

    def unload_dataset(self):
        """Unload the dataset by shutting down the processing pools"""
        for pool in self.pools:
            pool.shutdown()
        self.pools.clear()


    def load_subset(self, subset:str, test:bool) -> tf.data.Dataset:
        """Load the subset"""
        if subset in ('validation', 'evaluation'):
            split = (0, validation_split)
        elif subset == 'training':
            split = (validation_split, 1)
            data_dump_dir = globals().get('data_dump_dir', None)
            if data_dump_dir:
                print(f'\n\n*** Dumping augmented samples to: {data_dump_dir}\n\n')
        else:
            split = None
            my_model.class_counts = {}


        # Download the synthetic "direction_commands" dataset and extract into the dataset directory
        audio_datasets.on_off.download(dataset_dir, clean_dest_dir=True)
        # Download the Google speech commands dataset into the direction_commands dataset directory
        # This effectively combines the two datasets
        audio_datasets.speech_commands_v2.load_clean_data(dataset_dir, clean_dest_dir=False)

        # Download the mlcommons subset and extract into the dataset sub-directory: '_unknown/mlcommons_keywords'
        audio_datasets.mlcommons.ml_commons_keywords.download(f'{dataset_dir}/_unknown/mlcommons_keywords')

        # Download the mlcommons ESC-50 dataset and extract into the dataset sub-directory: '_unknown/esc-50'
        audio_datasets.background_noise.esc50.download(f'{dataset_dir}/_unknown/esc-50', sample_rate_hertz=frontend_settings.sample_rate_hz)

        # Download the MIT Impulse Response dataset into into the dataset sub-directory: '_ir_responses_'
        audio_datasets.mit_ir_survey.download(f'{dataset_dir}/_ir_responses_', sample_rate_hz=frontend_settings.sample_rate_hz)

        # Download the BRD2601 background microphone audio and add it to the _background_noise_/brd2601 of the dataset
        audio_datasets.background_noise.brd2601.download(f'{dataset_dir}/_background_noise_/brd2601', sample_rate_hertz=frontend_settings.sample_rate_hz)

        # Download other ambient background audio and add it to the _background_noise_/ambient of the dataset
        audio_datasets.background_noise.ambient.download(
            f'{dataset_dir}/_background_noise_/ambient',
            sample_rate_hertz=frontend_settings.sample_rate_hz
        )


        # Create a tf.data.Dataset from the extracted dataset directory
        max_samples_per_class = my_model.batch_size if test else -1
        class_counts = my_model.class_counts[subset] if subset else my_model.class_counts
        features_ds, labels_ds = tf_dataset_utils.load_audio_directory(
            directory=dataset_dir,
            classes=my_model.classes,
            onehot_encode=True, # We're using categorical cross-entropy so one-hot encode the labels
            shuffle=True,
            seed=42,
            max_samples_per_class=max_samples_per_class,
            unknown_class_percentage=0, # We manually populate the "known" class in the add_unknown_samples() callback
            split=split,
            return_audio_data=False, # We only want to return the file paths
            class_counts=class_counts,
            list_valid_filenames_in_directory_function=self.list_valid_filenames_in_directory,
            process_samples_function=self.add_unknown_samples
        )

        if subset:
            # The number of batches to process in each subprocess
            per_job_batch_multiplier = 1000
            per_job_batch_size = my_model.batch_size * per_job_batch_multiplier

            # We use an incrementing counter as the seed for the random augmentations
            # This helps to keep the training reproducible
            try:
                seed_counter = tf.data.Dataset.counter()
            except:
                seed_counter = tf.data.experimental.Counter()
            features_ds = features_ds.zip((features_ds, labels_ds, seed_counter))

            # Usage of tf_dataset_utils.parallel_process()
            # is optional, but can speed-up training as the data augmentations
            # are spread across the available CPU cores.
            # Each CPU core gets its own subprocess,
            # and and subprocess executes audio_augmentation_pipeline() on batches of the dataset.

            features_ds = features_ds.batch(per_job_batch_size // per_job_batch_multiplier, drop_remainder=True)
            labels_ds = labels_ds.batch(per_job_batch_size // per_job_batch_multiplier, drop_remainder=True)
            features_ds, pool = tf_dataset_utils.parallel_process(
                features_ds,
                audio_pipeline_with_augmentations,
                dtype=np.int8,
                #n_jobs=84 if subset == 'training' else 32, # These are the settings for a 256 CPU core cloud machine
                #n_jobs=72 if subset == 'training' else 32, # These are the settings for a 128 CPU core cloud machine
                #n_jobs=44 if subset == 'training' else 16, # These are the settings for a 96 CPU core cloud machine
                #n_jobs=50 if subset == 'training' else 25, # These are the settings for a 84 CPU core cloud machine
                #n_jobs=36 if subset == 'training' else 12, # These are the settings for a 64 CPU core cloud machine
                #n_jobs=28 if subset == 'training' else 16, # These are the settings for a 48 CPU core cloud machine
                #n_jobs=.65 if subset == 'training' else .35,
                n_jobs=8,
                name=subset,
            )
            self.pools.append(pool)
            features_ds = features_ds.unbatch()
            labels_ds = labels_ds.unbatch()

            # Pre-fetching batches can help with throughput
            features_ds = features_ds.prefetch(per_job_batch_size)

        # Combine the augmented audio samples with their corresponding labels
        ds = tf.data.Dataset.zip((features_ds, labels_ds))

        # Shuffle the data for each sample
        # A perfect shuffle would use n_samples but this can slow down training,
        # so we just shuffle batches of the data
        #ds = ds.shuffle(n_samples, reshuffle_each_iteration=True)
        if not test:
            ds = ds.shuffle(per_job_batch_size, reshuffle_each_iteration=True)

        # At this point we have a flat dataset of x,y tuples
        # Batch the data as necessary for training
        ds = ds.batch(my_model.batch_size)

        # Pre-fetch a couple training batches to aid throughput
        ds = ds.prefetch(2)

        return ds

    def list_valid_filenames_in_directory(
        self,
        base_directory:str,
        search_class:str,
        white_list_formats:List[str],
        split:float,
        follow_links:bool,
        shuffle_index_directory:str
    ) -> Tuple[str, List[str]]:
        """Return a list of valid file names for the given class

        This is called by the tf_dataset_utils.load_audio_directory() API.

        # This uses shuffle_file_list_by_group() helper function so that the same "voices"
        # are only present in a particular subset.
        """
        assert shuffle_index_directory is None, 'Shuffling the index is not supported by this dataset'

        file_list = []
        index_path = f'{base_directory}/.index/{search_class}.txt'

        # If the index file exists, then read it
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                for line in f:
                    file_list.append(line.strip())

        else:
            # Else find all files for the given class in the search directory
            class_base_dir = f'{base_directory}/{search_class}/'
            for root, _, files in os.walk(base_directory, followlinks=follow_links):
                root = root.replace('\\', '/') + '/'
                if not root.startswith(class_base_dir):
                    continue

                for fname in files:
                    if not fname.lower().endswith(white_list_formats):
                        continue
                    abs_path = os.path.join(root, fname)
                    if os.path.getsize(abs_path) == 0:
                        continue
                    rel_path = os.path.relpath(abs_path, base_directory)
                    file_list.append(rel_path.replace('\\', '/'))


                # Shuffle the voice groups
                # then flatten into list
                # This way, when the list is split into training and validation sets
                # the same voice only appears in one subset
                file_list = shuffle_file_list_by_group(file_list, get_sample_group_id_from_path)

                # Write the file list file
                mltk_core.get_mltk_logger().info(f'Generating index for "{search_class}" ({len(file_list)} samples): {index_path}')
                os.makedirs(os.path.dirname(index_path), exist_ok=True)
                with open(index_path, 'w') as f:
                    for p in file_list:
                        f.write(p + '\n')

        if len(file_list) == 0:
            raise RuntimeError(f'No samples found for class: {search_class}')


        n_files = len(file_list)
        if split[0] == 0:
            start = 0
            stop = math.ceil(split[1] * n_files)

            # We want to ensure the same person isn't in both subsets
            # So, ensure that the split point does NOT
            # split with file names with the same hash
            # recall: same hash = same person saying word

            # Get the hash of the other subset
            other_subset_hash = get_sample_group_id_from_path(file_list[stop])
            # Keep moving the 'stop' index back while
            # it's index matches the otherside
            while stop > 0 and get_sample_group_id_from_path(file_list[stop-1]) == other_subset_hash:
                stop -= 1

        else:
            start = math.ceil(split[0] * n_files)
            # Get the hash of the this subset
            this_subset_hash = get_sample_group_id_from_path(file_list[start])
            # Keep moving the 'start' index back while
            # it's index matches this side's
            while start > 0 and get_sample_group_id_from_path(file_list[start-1]) == this_subset_hash:
                start -= 1

            stop = n_files

        filenames = file_list[start:stop]

        return search_class, filenames

    def add_unknown_samples(
        self,
        directory:str,
        sample_paths:Dict[str,str], # A dictionary: <class name>, [<sample paths relative to directory>],
        split:Tuple[float,float],
        follow_links:bool,
        white_list_formats:List[str],
        shuffle:bool,
        seed:int,
        **kwargs
    ):
        """Generate a list of all possible "unknown" samples for this given subset.

        Then populate the "_unknown_" class with a random subset of the "unknown" samples.
        The subset should be the approximate size of the "known" samples

        """
        mlcommons_keywords_dir = f'{dataset_dir}/_unknown/mlcommons_keywords'
        esc50_dir = f'{dataset_dir}/_unknown/esc-50/audio'

        # Create a list of all possible "unknown" samples
        file_list = []

        # All all the mlcommons_keywords "unknown" samples that are not the "known" sample
        all_keywords = []
        for kw in os.listdir(mlcommons_keywords_dir):
            if kw in my_model.classes:
                continue
            d = f'{mlcommons_keywords_dir}/{kw}'
            if not os.path.isdir(d):
                continue

            for fn in os.listdir(d):
                if fn.endswith('.wav'):
                    all_keywords.append(f'_unknown/mlcommons_keywords/{kw}/{fn}')

        # Get a random subset of the "unknown" samples
        # We only select 11k so balance with the "known" classes
        rng = np.random.RandomState(seed)
        all_keywords = sorted(all_keywords)
        rng.shuffle(all_keywords)
        file_list.extend(all_keywords[:11000])

        # Add all the samples from the ESC-50 dataset which is 2k samples
        # This way, we have random keywords and random noises in the "unknown" class's sample list
        for fn in os.listdir(esc50_dir):
            if not fn.endswith('.wav'):
                continue
            file_list.append(f'_unknown/esc-50/audio/{fn}')

        # Sort the unknown samples by "voice"
        # This helps to ensure voices are only present in a given subset
        file_list = sorted(file_list)
        file_list = shuffle_file_list_by_group(file_list, get_sample_group_id_from_path)

        # Split the file list for the current subset
        sample_paths['_unknown_'] = split_file_list(file_list, split)



def get_sample_group_id_from_path(p:str) -> str:
    """Extract the "voice hash" from the sample path.

    This is used by shuffle_file_list_by_group() so that when we split
    the dataset for training and validation, the same "voice" only appears
    in one of the subsets.
    """
    fn = os.path.basename(p)
    fn = fn.replace('.wav', '').replace('.mp3', '')

    # If this sample is from the Google speech commands dataset
    #  c53b335a_nohash_1.wav -> c53b335a
    if '_nohash_' in fn:
        toks = fn.split('_')
        return toks[0]

    # If this sample is from an mlcommons dataset
    #  common_voice_en_20127845.wav -> 20127845
    if fn.startswith('common_voice_'):
        toks = fn.split('_')
        return toks[-1]

    # If this sample is from a silabs synthetic dataset
    # azure_af-ZA+AdriNeural+None+aww+medium+low+588b6ace.wav -> 588b6ace
    if fn.startswith(('gcp_', 'azure_', 'aws_')):
        toks = fn.split('+')
        return toks[-1]

    if '/esc-50/' in p:
        toks = fn.split('-')
        return toks[1]

    raise RuntimeError(f'Failed to get voice hash from {p}')


my_model.dataset = MyDataset()




#################################################
# Audio Classifier Settings
#
# These are additional parameters to include in
# the generated .tflite model file.
# The settings are used by the ble_audio_classifier app
# NOTE: Corresponding command-line options will override these values.

# Controls the smoothing.
# Drop all inference results that are older than <now> minus window_duration
# Longer durations (in milliseconds) will give a higher confidence that the results are correct, but may miss some commands
my_model.model_parameters['average_window_duration_ms'] = 300
# Define a specific detection threshold for each class
#my_model.model_parameters['detection_threshold'] = 235
my_model.model_parameters['detection_threshold_list'] = list(map(lambda x: int(x*255), [.95, .95, 1.0]))
# Amount of milliseconds to wait after a keyword is detected before detecting the SAME keyword again
# A different keyword may be detected immediately after
my_model.model_parameters['suppression_ms'] = 700
# The minimum number of inference results to average when calculating the detection value
my_model.model_parameters['minimum_count'] = 2
# Set the volume gain scaler (i.e. amplitude) to apply to the microphone data. If 0 or omitted, no scaler is applied
my_model.model_parameters['volume_gain'] = 0.0
# This the amount of time in milliseconds between audio processing loops
# Since we're using the audio detection block, we want this to be as short as possible
my_model.model_parameters['latency_ms'] = 10
# Enable verbose inference results
my_model.model_parameters['verbose_model_output_logs'] = False



##########################################################################################
# The following allows for running this model training script directly, e.g.:
# python keyword_spotting_on_off_v3.py
#
# Note that this has the same functionality as:
# mltk train keyword_spotting_on_off_v3
#
if __name__ == '__main__':
    from mltk import cli

    # Setup the CLI logger
    cli.get_logger(verbose=True)


    # If this is true then this will do a "dry run" of the model testing
    # If this is false, then the model will be fully trained
    test_mode_enabled = True

    # Train the model
    # This does the same as issuing the command:  mltk train keyword_spotting_on_off_v3-test --clean)
    train_results = mltk_core.train_model(my_model, clean=True, test=test_mode_enabled)
    print(train_results)

    # Evaluate the model against the quantized .h5 (i.e. float32) model
    # This does the same as issuing the command: mltk evaluate keyword_spotting_on_off_v3-test
    tflite_eval_results = mltk_core.evaluate_model(my_model, verbose=True, test=test_mode_enabled)
    print(tflite_eval_results)

    # Profile the model in the simulator
    # This does the same as issuing the command: mltk profile keyword_spotting_on_off_v3-test
    profiling_results = mltk_core.profile_model(my_model, test=test_mode_enabled)
    print(profiling_results)
