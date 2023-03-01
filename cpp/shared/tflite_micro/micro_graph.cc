/* Copyright 2021 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

#include "tensorflow/lite/micro/micro_graph.h"

#include "flatbuffers/flatbuffers.h"  // from @flatbuffers
#include "tensorflow/lite/c/common.h"
#include "tensorflow/lite/kernels/internal/compatibility.h"
#include "tensorflow/lite/micro/flatbuffer_utils.h"
#include "tensorflow/lite/micro/memory_helpers.h"
#include "tensorflow/lite/micro/micro_log.h"
#include "tensorflow/lite/micro/micro_profiler.h"
#include "tensorflow/lite/schema/schema_generated.h"

#include "mltk_tflite_micro_internal.hpp"

namespace tflite {
namespace {

const char* OpNameFromRegistration(const TfLiteRegistration* registration) {
  if (registration->builtin_code == BuiltinOperator_CUSTOM) {
    return registration->custom_name;
  } else {
    return EnumNameBuiltinOperator(BuiltinOperator(registration->builtin_code));
  }
}

}  // namespace

MicroGraph::MicroGraph(TfLiteContext* context, const Model* model,
                       MicroAllocator* allocator,
                       MicroResourceVariables* resource_variables)
    : context_(context),
      model_(model),
      allocator_(allocator),
      current_subgraph_index_(0),
      resource_variables_(resource_variables) {
  if (model != nullptr) {
    subgraphs_ = model->subgraphs();
  }
}

MicroGraph::~MicroGraph() {
  FREE_PROFILERS();
}

TfLiteStatus MicroGraph::InitSubgraphs() {
  int previous_subgraph_idx = current_subgraph_index_;

  for (size_t subgraph_idx = 0; subgraph_idx < subgraphs_->size();
       subgraph_idx++) {
    current_subgraph_index_ = subgraph_idx;
    uint32_t operators_size = NumSubgraphOperators(model_, subgraph_idx);
    for (size_t i = 0; i < operators_size; ++i) {
      TfLiteNode* node =
          &(subgraph_allocations_[subgraph_idx].node_and_registrations[i].node);
      const TfLiteRegistration* registration =
          subgraph_allocations_[subgraph_idx]
              .node_and_registrations[i]
              .registration;
      size_t init_data_size;
      const char* init_data;
      if (registration->builtin_code == BuiltinOperator_CUSTOM) {
        init_data = reinterpret_cast<const char*>(node->custom_initial_data);
        init_data_size = node->custom_initial_data_size;
      } else {
        init_data = reinterpret_cast<const char*>(node->builtin_data);
        init_data_size = 0;
      }
      if (registration->init) {
        node->user_data =
            registration->init(context_, init_data, init_data_size);
      }
    }
  }
  current_subgraph_index_ = previous_subgraph_idx;

  return kTfLiteOk;
}

TfLiteStatus MicroGraph::PrepareSubgraphs() {
  TfLiteStatus retval = kTfLiteOk;
  auto& logger = mltk::get_logger();
  int previous_subgraph_idx = current_subgraph_index_;

  for (size_t subgraph_idx = 0; subgraph_idx < subgraphs_->size();
       subgraph_idx++) {
    current_subgraph_index_ = subgraph_idx;
    uint32_t operators_size = NumSubgraphOperators(model_, subgraph_idx);
    ALLOCATE_PROFILERS(subgraph_idx, operators_size)
    for (size_t i = 0; i < operators_size; ++i) {
      TfLiteNode* node =
          &(subgraph_allocations_[subgraph_idx].node_and_registrations[i].node);
      const TfLiteRegistration* registration =
          subgraph_allocations_[subgraph_idx]
              .node_and_registrations[i]
              .registration;
      SET_CURRENT_KERNEL(i, registration->builtin_code);
      if (registration->prepare != nullptr) {
        TfLiteStatus prepare_status = registration->prepare(context_, node);
        if (prepare_status != kTfLiteOk) {
          logger.error("Op%d-%s not supported: Failed to prepare with status %d",
                      i, OpNameFromRegistration(registration), prepare_status);
          retval = kTfLiteError;
          continue;
        }
      }
      allocator_->FinishPrepareNodeAllocations(/*node_id=*/i);
      CLEAR_CURRENT_KERNEL()
      REGISTER_PROFILER(subgraph_idx, i, registration->builtin_code, context_, subgraph_allocations_[subgraph_idx].node_and_registrations[i])
    }
  }
  current_subgraph_index_ = previous_subgraph_idx;

  return retval;
}

TfLiteStatus MicroGraph::FreeSubgraphs() {
  int previous_subgraph_idx = current_subgraph_index_;

  for (size_t subgraph_idx = 0; subgraph_idx < subgraphs_->size();
       subgraph_idx++) {
    current_subgraph_index_ = subgraph_idx;
    uint32_t operators_size = NumSubgraphOperators(model_, subgraph_idx);
    for (size_t i = 0; i < operators_size; ++i) {
      TfLiteNode* node =
          &(subgraph_allocations_[subgraph_idx].node_and_registrations[i].node);
      const TfLiteRegistration* registration =
          subgraph_allocations_[subgraph_idx]
              .node_and_registrations[i]
              .registration;
      // registration is allocated outside the interpreter, so double check to
      // make sure it's not nullptr;
      if (registration != nullptr && registration->free != nullptr) {
        registration->free(context_, node->user_data);
      }
    }
  }
  current_subgraph_index_ = previous_subgraph_idx;

  return kTfLiteOk;
}

TfLiteStatus MicroGraph::InvokeSubgraph(int subgraph_idx) {
  auto& logger = mltk::get_logger();
  int previous_subgraph_idx = current_subgraph_index_;
  current_subgraph_index_ = subgraph_idx;

  if (static_cast<size_t>(subgraph_idx) >= subgraphs_->size()) {
    MicroPrintf("Accessing subgraph %d but only %d subgraphs found",
                subgraph_idx, subgraphs_->size());
    return kTfLiteError;
  }
  INVOKE_PROCESSING_CALLBACK();
  START_INFERENCE_PROFILER(subgraph_idx)
  uint32_t operators_size = NumSubgraphOperators(model_, subgraph_idx);
  for (size_t i = 0; i < operators_size; ++i) {
    TfLiteNode* node =
        &(subgraph_allocations_[subgraph_idx].node_and_registrations[i].node);
    const TfLiteRegistration* registration = subgraph_allocations_[subgraph_idx]
                                                 .node_and_registrations[i]
                                                 .registration;

// This ifdef is needed (even though ScopedMicroProfiler itself is a no-op with
// -DTF_LITE_STRIP_ERROR_STRINGS) because the function OpNameFromRegistration is
// only defined for builds with the error strings.
#if !defined(TF_LITE_STRIP_ERROR_STRINGS)
    ScopedMicroProfiler scoped_profiler(
        OpNameFromRegistration(registration),
        reinterpret_cast<MicroProfilerInterface*>(context_->profiler));
#endif

    TFLITE_DCHECK(registration->invoke);
    TFLITE_MICRO_RECORD_INPUTS(i, context_, node)
    START_OP_PROFILER(subgraph_idx, i, registration->builtin_code)
    TfLiteStatus invoke_status = registration->invoke(context_, node);
    STOP_OP_PROFILER(subgraph_idx, i)
    TFLITE_MICRO_RECORD_OUTPUTS(i, context_, node)

    // All TfLiteTensor structs used in the kernel are allocated from temp
    // memory in the allocator. This creates a chain of allocations in the
    // temp section. The call below resets the chain of allocations to
    // prepare for the next call.
    allocator_->ResetTempAllocations();

    if (invoke_status == kTfLiteError) {
      logger.error("Op%d-%s not supported: Failed to invoke with status %d",
                  i, OpNameFromRegistration(registration), invoke_status);
      return kTfLiteError;
    } else if (invoke_status != kTfLiteOk) {
      return invoke_status;
    }

    INVOKE_PROCESSING_CALLBACK();
  }
  STOP_INFERENCE_PROFILER(subgraph_idx)
  current_subgraph_index_ = previous_subgraph_idx;
  return kTfLiteOk;
}

TfLiteStatus MicroGraph::ResetVariableTensors() {
  for (size_t subgraph_idx = 0; subgraph_idx < subgraphs_->size();
       subgraph_idx++) {
    const SubGraph* subgraph = (*subgraphs_)[subgraph_idx];
    for (size_t i = 0; i < subgraph->tensors()->size(); ++i) {
      auto* tensor = subgraph->tensors()->Get(i);
      if (tensor->is_variable()) {
        size_t buffer_size;
        TF_LITE_ENSURE_STATUS(TfLiteEvalTensorByteLength(
            &subgraph_allocations_[subgraph_idx].tensors[i], &buffer_size));

        int value = 0;
        if (tensor->type() == tflite::TensorType_INT8) {
          value = tensor->quantization()->zero_point()->Get(0);
        }
        memset(subgraph_allocations_[subgraph_idx].tensors[i].data.raw, value,
               buffer_size);
      }
    }
  }
  if (resource_variables_ != nullptr) {
    resource_variables_->ResetAll();
  }

  return kTfLiteOk;
}

int MicroGraph::NumSubgraphs() { return model_->subgraphs()->size(); }

void MicroGraph::SetSubgraphAllocations(
    SubgraphAllocations* subgraph_allocations) {
  subgraph_allocations_ = subgraph_allocations;
}

size_t MicroGraph::NumSubgraphInputs(int subgraph_idx) {
  return model_->subgraphs()->Get(subgraph_idx)->inputs()->size();
}

TfLiteEvalTensor* MicroGraph::GetSubgraphInput(int subgraph_idx,
                                               int input_idx) {
  int tensor_idx =
      model_->subgraphs()->Get(subgraph_idx)->inputs()->Get(input_idx);
  return &subgraph_allocations_[subgraph_idx].tensors[tensor_idx];
}

size_t MicroGraph::NumSubgraphOutputs(int subgraph_idx) {
  return model_->subgraphs()->Get(subgraph_idx)->outputs()->size();
}

TfLiteEvalTensor* MicroGraph::GetSubgraphOutput(int subgraph_idx,
                                                int output_idx) {
  int tensor_idx =
      model_->subgraphs()->Get(subgraph_idx)->outputs()->Get(output_idx);
  return &subgraph_allocations_[subgraph_idx].tensors[tensor_idx];
}

}  // namespace tflite
