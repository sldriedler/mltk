
if(MLTK_PLATFORM STREQUAL "mltk_platform_brd4186b")
    mltk_info("Audio Classifier app NOT currently supported by BRD4186A platform since it doesn't have a supported microphone")
    return()
endif()



# Find the necessary packages
find_package(mltk_logging REQUIRED)
find_package(mltk_profiling REQUIRED)
find_package(mltk_tflite_micro_model REQUIRED)
find_package(mltk_microfrontend REQUIRED)



#####################################################
# Define the audio_classifier executable
add_executable(mltk_audio_classifier)  


target_sources(mltk_audio_classifier
PRIVATE 
    main.cc
    cli_opts.cc
    audio_provider.cc 
    command_responder.cc
    feature_provider.cc 
    micro_features_generator.cc 
    recognize_commands.cc
    micro_model_settings.cc
)

target_link_libraries(mltk_audio_classifier
PRIVATE 
    mltk::tflite_micro_model
    mltk::microfrontend
    ${MLTK_PLATFORM}
)


target_include_directories(mltk_audio_classifier
PRIVATE 
    .
    "${MLTK_BINARY_DIR}"
)

mltk_get(MLTK_PLATFORM_IS_EMBEDDED)
if(NOT MLTK_PLATFORM_IS_EMBEDDED)
    find_package(mltk_cxxopts REQUIRED)
    target_link_libraries(mltk_audio_classifier
    PRIVATE 
        mltk::cxxopts
    )
endif()


unset(_defines)
mltk_get(VERBOSE)
if(VERBOSE)
    mltk_info("Enabling verbose logs")
    set(_defines ${_defines} VERBOSE)
endif()

mltk_get(WINDOW_MS)
if(WINDOW_MS)
    mltk_info("WINDOW_MS=${WINDOW_MS}")
    set(_defines ${_defines} WINDOW_MS=${WINDOW_MS})
endif()

mltk_get(THRESHOLD)
if(THRESHOLD)
    mltk_info("THRESHOLD=${THRESHOLD}")
    set(_defines ${_defines} THRESHOLD=${THRESHOLD})
endif()

mltk_get(SUPPRESSION_MS)
if(SUPPRESSION_MS)
    mltk_info("SUPPRESSION_MS=${SUPPRESSION_MS}")
    set(_defines ${_defines} SUPPRESSION_MS=${SUPPRESSION_MS})
endif()

mltk_get(COUNT)
if(COUNT)
    mltk_info("COUNT=${COUNT}")
    set(_defines ${_defines} COUNT=${COUNT})
endif()

mltk_get(VOLUME_DB)
if(VOLUME_DB)
    mltk_info("VOLUME_DB=${VOLUME_DB}")
    set(_defines ${_defines} VOLUME_DB=${VOLUME_DB})
endif()

mltk_get(LATENCY_MS)
if(LATENCY_MS)
    mltk_info("LATENCY_MS=${LATENCY_MS}")
    set(_defines ${_defines} LATENCY_MS=${LATENCY_MS})
endif()

if(_defines)
    target_compile_definitions(mltk_audio_classifier
    PRIVATE
        ${_defines}
    )
endif()


# Generate the exe output files (if necessary for the build platform)
mltk_add_exe_targets(mltk_audio_classifier)

#####################################################
# Convert the model .tflite to a C header file

# Use the default model if one wasn't provided on the command-line
mltk_get(AUDIO_CLASSIFIER_MODEL)
if(NOT AUDIO_CLASSIFIER_MODEL)
    set(AUDIO_CLASSIFIER_MODEL "tflite_micro_speech")
endif()
mltk_info("AUDIO_CLASSIFIER_MODEL=${AUDIO_CLASSIFIER_MODEL}")

mltk_load_python()

set(output_path "${MLTK_BINARY_DIR}/audio_classifier_generated_model.tflite.h")
add_custom_target(mltk_audio_classifier_generate_model
    COMMAND ${PYTHON_EXECUTABLE} ${MLTK_CPP_UTILS_DIR}/generate_model_header.py "${AUDIO_CLASSIFIER_MODEL}" --name "MODEL_DATA" --attributes "MODEL_DATA_SECTION" --output ${output_path}
    COMMENT "Generating audio_classifier_generated_model.tflite.h from ${AUDIO_CLASSIFIER_MODEL}"
    BYPRODUCTS ${output_path}
)
add_dependencies(mltk_audio_classifier mltk_audio_classifier_generate_model)