

mltk_set(TFLITE_MICRO_PROFILER_ENABLED ON)


# Find the necessary packages
find_package(mltk_logging REQUIRED)
find_package(mltk_profiling REQUIRED)
find_package(mltk_tflite_micro_model REQUIRED)



#####################################################
# Define the model_profiler executable
add_executable(mltk_model_profiler)  


target_sources(mltk_model_profiler
PRIVATE 
    main.cc
)

target_link_libraries(mltk_model_profiler
PRIVATE 
    mltk::tflite_micro_model
    ${MLTK_PLATFORM}
)


target_include_directories(mltk_model_profiler
PRIVATE 
    "${MLTK_BINARY_DIR}"
)

mltk_get(MLTK_RUN_MODEL_FROM_RAM)
if(MLTK_RUN_MODEL_FROM_RAM)
    mltk_info("Loading .tflite flatbuffer into RAM")
    target_compile_definitions(mltk_model_profiler
    PUBLIC 
        MLTK_RUN_MODEL_FROM_RAM
    )
endif()




# Generate the exe output files (if necessary for the build platform)
mltk_add_exe_targets(mltk_model_profiler)


#####################################################
# Convert the model .tflite to a C header file

# Use the default model if one wasn't provided on the command-line

mltk_get(MODEL_PROFILER_MODEL)
if(NOT MODEL_PROFILER_MODEL)
    # Support legacy variable name
    mltk_get(MODEL) 
    if(MODEL)
        set(MODEL_PROFILER_MODEL ${MODEL})
    endif()
endif()

if(NOT MODEL_PROFILER_MODEL)
    set(MODEL_PROFILER_MODEL "image_classification")
endif()
mltk_info("MODEL_PROFILER_MODEL=${MODEL_PROFILER_MODEL}")

mltk_load_python()

set(output_path "${MLTK_BINARY_DIR}/model_profiler_generated_model.tflite.h")
add_custom_target(mltk_model_profiler_generate_model
    COMMAND ${PYTHON_EXECUTABLE} ${MLTK_CPP_UTILS_DIR}/generate_model_header.py "${MODEL_PROFILER_MODEL}" --name "MODEL_DATA" --attributes "MODEL_DATA_SECTION" --output ${output_path}
    COMMENT "Generating model_profiler_generated_model.tflite.h from ${MODEL_PROFILER_MODEL}"
    BYPRODUCTS ${output_path}
)
add_dependencies(mltk_model_profiler mltk_model_profiler_generate_model)