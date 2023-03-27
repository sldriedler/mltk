/***************************************************************************//**
 * @file
 * @brief MVP Math Vector Negate function.
 *******************************************************************************
 * # License
 * <b>Copyright 2023 Silicon Laboratories Inc. www.silabs.com</b>
 *******************************************************************************
 *
 * SPDX-License-Identifier: Zlib
 *
 * The licensor of this software is Silicon Laboratories Inc.
 *
 * This software is provided 'as-is', without any express or implied
 * warranty. In no event will the authors be held liable for any damages
 * arising from the use of this software.
 *
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely, subject to the following restrictions:
 *
 * 1. The origin of this software must not be misrepresented; you must not
 *    claim that you wrote the original software. If you use this software
 *    in a product, an acknowledgment in the product documentation would be
 *    appreciated but is not required.
 * 2. Altered source versions must be plainly marked as such, and must not be
 *    misrepresented as being the original software.
 * 3. This notice may not be removed or altered from any source distribution.
 *
 ******************************************************************************/
#include "sl_mvp.h"
#include "sl_mvp_power.h"
#include "sl_mvp_util.h"
#include "sl_mvp_program_area.h"
#include "sl_math_mvp_vector_negate.h"

#ifndef USE_MVP_PROGRAMBUILDER
#define USE_MVP_PROGRAMBUILDER    0
#endif

sl_status_t sl_math_mvp_vector_negate_f16(const float16_t *input,
                                          float16_t *output,
                                          size_t num_elements)
{
  uint32_t m, n;
  sli_mvp_datatype_t data_type;
  size_t len, remainder, parallel, i;

  if (!input || !output || !num_elements) {
    return SL_STATUS_INVALID_PARAMETER;
  }

  // Check if MVP parallel processing is possible.
  len = num_elements;
  parallel = 1U;
  remainder = 0U;
  data_type = SLI_MVP_DATATYPE_BINARY16;
  if (sli_mvp_util_is_pointer_word_aligned((float16_t*)input)
      && sli_mvp_util_is_pointer_word_aligned(output)
      && (len >= 2U)) {
    parallel = 2U;
    if (len & 1U ) {
      remainder++;
    }
    data_type = SLI_MVP_DATATYPE_COMPLEX_BINARY16;
    len /= 2U;
  }

  // Factorize len into m * n.
  if (len <= SLI_MVP_MAX_ROW_LENGTH) {
    m = 1U;
    n = len;
  } else {
    i = len;
    while (sli_mvp_util_factorize_number(i, 1024U, &m, &n) != SL_STATUS_OK) {
      i--;
      remainder += parallel;
    }
  }

#if USE_MVP_PROGRAMBUILDER
  // This is the reference MVP program for the optimized setup below.

  sl_status_t status = SL_STATUS_OK;
  const int vector_x = SLI_MVP_ARRAY(0);
  const int vector_z = SLI_MVP_ARRAY(1);

  sli_mvp_program_context_t *p = sli_mvp_get_program_area_context();
  sli_mvp_pb_init_program(p);
  sli_mvp_pb_begin_program(p);

  sli_mvp_pb_config_matrix(p->p, vector_x, (void*)input, data_type, m, n, &status);
  sli_mvp_pb_config_matrix(p->p, vector_z, (void*)output, data_type, m, n, &status);

  sli_mvp_pb_begin_loop(p, m, &status); {
    sli_mvp_pb_begin_loop(p, n, &status); {
      sli_mvp_pb_compute(p,
                         SLI_MVP_OP(COPY),                    // COPY: Z = A
                         SLI_MVP_ALUIN_A(SLI_MVP_R0, SLI_MVP_ALUIN_REALNEGATE | SLI_MVP_ALUIN_IMAGNEGATE)
                         | SLI_MVP_ALU_Z(SLI_MVP_R1),
                         SLI_MVP_LOAD(0, SLI_MVP_R0, vector_x, SLI_MVP_INCRDIM_WIDTH),
                         SLI_MVP_STORE(SLI_MVP_R1, vector_z, SLI_MVP_INCRDIM_WIDTH),
                         &status);
    }
    sli_mvp_pb_end_loop(p);
    sli_mvp_pb_postloop_incr_dim(p, vector_x, SLI_MVP_INCRDIM_HEIGHT);
    sli_mvp_pb_postloop_incr_dim(p, vector_z, SLI_MVP_INCRDIM_HEIGHT);
  }
  sli_mvp_pb_end_loop(p);
  sli_mvp_pb_execute_program(p);
#else

  sli_mvp_power_program_prepare();

  // Program array controllers.
  MVP->ARRAY[0].DIM0CFG = MVP->ARRAY[1].DIM0CFG =
    data_type << _MVP_ARRAYDIM0CFG_BASETYPE_SHIFT;
  MVP->ARRAY[0].DIM1CFG = MVP->ARRAY[1].DIM1CFG =
    ((m - 1) << _MVP_ARRAYDIM1CFG_SIZE_SHIFT) | (n << _MVP_ARRAYDIM1CFG_STRIDE_SHIFT);
  MVP->ARRAY[0].DIM2CFG = MVP->ARRAY[1].DIM2CFG =
    ((n - 1) << _MVP_ARRAYDIM2CFG_SIZE_SHIFT) | (1 << _MVP_ARRAYDIM2CFG_STRIDE_SHIFT);
  MVP->ARRAY[0].ADDRCFG = MVP_ARRAY_PTR(input);
  MVP->ARRAY[1].ADDRCFG = MVP_ARRAY_PTR(output);

  // Program loop controllers.
  MVP->LOOP[1].RST = 0;
  MVP->LOOP[0].CFG = (m - 1) << _MVP_LOOPCFG_NUMITERS_SHIFT;
  MVP->LOOP[1].CFG = ((n - 1) << _MVP_LOOPCFG_NUMITERS_SHIFT)
                     | ((SLI_MVP_LOOP_INCRDIM(SLI_MVP_ARRAY(0), SLI_MVP_INCRDIM_HEIGHT)
                         | SLI_MVP_LOOP_INCRDIM(SLI_MVP_ARRAY(1), SLI_MVP_INCRDIM_HEIGHT))
                        << _MVP_LOOPCFG_ARRAY0INCRDIM0_SHIFT);

  // Program instruction.
  MVP->INSTR[0].CFG0 = SLI_MVP_ALUIN_A(SLI_MVP_R0, SLI_MVP_ALUIN_REALNEGATE | SLI_MVP_ALUIN_IMAGNEGATE)
                       | SLI_MVP_ALU_Z(SLI_MVP_R1);
  MVP->INSTR[0].CFG1 = SLI_MVP_LOAD(0, SLI_MVP_R0, SLI_MVP_ARRAY(0), SLI_MVP_INCRDIM_WIDTH)
                       | SLI_MVP_STORE(SLI_MVP_R1, SLI_MVP_ARRAY(1), SLI_MVP_INCRDIM_WIDTH);
  MVP->INSTR[0].CFG2 = (SLI_MVP_OP(COPY) << _MVP_INSTRCFG2_ALUOP_SHIFT)
                       | MVP_INSTRCFG2_ENDPROG
                       | MVP_INSTRCFG2_LOOP0BEGIN
                       | MVP_INSTRCFG2_LOOP0END
                       | MVP_INSTRCFG2_LOOP1BEGIN
                       | MVP_INSTRCFG2_LOOP1END;

  // Start program.
  MVP->CMD = MVP_CMD_INIT | MVP_CMD_START;
  MVP_SIMULATOR_EXECUTE();

#endif

  // When factorization above is incomplete we handle "tail" elements here.
  i = num_elements - remainder;
  while (remainder--) {
    output[i] = - input[i];
    i++;
  }

  sli_mvp_wait_for_completion();

  return SL_STATUS_OK;
}
