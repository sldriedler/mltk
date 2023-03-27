/***************************************************************************//**
 * @file
 * @brief MVP Math Mul functions.
 *******************************************************************************
 * # License
 * <b>Copyright 2021 Silicon Laboratories Inc. www.silabs.com</b>
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
#include "sl_math_mvp.h"
#include "sl_mvp_util.h"
#include "sl_mvp_power.h"
#include "sl_mvp_program_area.h"
#include "sl_common.h"

#ifndef USE_MVP_PROGRAMBUILDER
#define USE_MVP_PROGRAMBUILDER    0
#endif

sl_status_t sl_math_mvp_vector_mult_f16(const float16_t *input_a, const float16_t *input_b, float16_t *output, size_t length)
{
  uint32_t len, remainder;
  uint32_t m, n, i, parallell;
  sl_status_t status = SL_STATUS_OK;
  sli_mvp_datatype_t data_type = SLI_MVP_DATATYPE_BINARY16;

  if (!input_a || !input_b || !output || !length) {
    return SL_STATUS_INVALID_PARAMETER;
  }

  // Check if MVP parallell processing is possible.
  len = length;
  parallell = 1;
  remainder = 0;
  if ((((uintptr_t)input_a & 3U) == 0U)
      && (((uintptr_t)input_b & 3U) == 0U)
      && (((uintptr_t)output & 3U) == 0U)
      && (len >= 2)) {
    parallell = 2;
    if (len & 1U ) {
      remainder++;
    }
    data_type = SLI_MVP_DATATYPE_COMPLEX_BINARY16;
    len /= 2;
  }

  if (len <= SLI_MVP_MAX_ROW_LENGTH) {
    m = 1;
    n = len;
  } else {
    i = len;
    while ((status = sli_mvp_util_factorize_number(i, 1024U, &m, &n)) != SL_STATUS_OK) {
      i--;
      remainder += parallell;
    }
  }
  #if USE_MVP_PROGRAMBUILDER
  const int vector_x = SLI_MVP_ARRAY(0);
  const int vector_y = SLI_MVP_ARRAY(1);
  const int vector_z = SLI_MVP_ARRAY(2);

  sli_mvp_program_context_t *p = sli_mvp_get_program_area_context();
  sli_mvp_pb_init_program(p);
  sli_mvp_pb_begin_program(p);

  sli_mvp_pb_config_matrix(p->p, vector_x, (void*)input_a, data_type, m, n, &status);
  sli_mvp_pb_config_matrix(p->p, vector_y, (void*)input_b, data_type, m, n, &status);
  sli_mvp_pb_config_matrix(p->p, vector_z, (void*)output, data_type, m, n, &status);
  sli_mvp_pb_begin_loop(p, m, &status); {
    sli_mvp_pb_begin_loop(p, n, &status); {
      sli_mvp_pb_compute(p,
                         SLI_MVP_OP(MULR2A),
                         SLI_MVP_ALU_X(SLI_MVP_R1) | SLI_MVP_ALU_Y(SLI_MVP_R2) | SLI_MVP_ALU_Z(SLI_MVP_R3),
                         SLI_MVP_LOAD(0, SLI_MVP_R1, vector_x, SLI_MVP_INCRDIM_WIDTH) | SLI_MVP_LOAD(1, SLI_MVP_R2, vector_y, SLI_MVP_INCRDIM_WIDTH),
                         SLI_MVP_STORE(SLI_MVP_R3, vector_z, SLI_MVP_INCRDIM_WIDTH),
                         &status);
    }
    sli_mvp_pb_end_loop(p);
    sli_mvp_pb_postloop_incr_dim(p, vector_x, SLI_MVP_INCRDIM_HEIGHT);
    sli_mvp_pb_postloop_incr_dim(p, vector_y, SLI_MVP_INCRDIM_HEIGHT);
    sli_mvp_pb_postloop_incr_dim(p, vector_z, SLI_MVP_INCRDIM_HEIGHT);
  }
  sli_mvp_pb_end_loop(p);

  // Check if any errors found during program generation.
  if (status != SL_STATUS_OK) {
    return status;
  }
  sli_mvp_pb_execute_program(p);
  #else
  sli_mvp_power_program_prepare();

  // Program array controllers.
  MVP->ARRAY[0].DIM0CFG = MVP->ARRAY[1].DIM0CFG = MVP->ARRAY[2].DIM0CFG =
    data_type << _MVP_ARRAYDIM0CFG_BASETYPE_SHIFT;
  MVP->ARRAY[0].DIM1CFG = MVP->ARRAY[1].DIM1CFG = MVP->ARRAY[2].DIM1CFG =
    ((m - 1) << _MVP_ARRAYDIM1CFG_SIZE_SHIFT) | (n << _MVP_ARRAYDIM1CFG_STRIDE_SHIFT);
  MVP->ARRAY[0].DIM2CFG = MVP->ARRAY[1].DIM2CFG = MVP->ARRAY[2].DIM2CFG =
    ((n - 1) << _MVP_ARRAYDIM2CFG_SIZE_SHIFT) | (1 << _MVP_ARRAYDIM2CFG_STRIDE_SHIFT);
  MVP->ARRAY[0].ADDRCFG = MVP_ARRAY_PTR(input_a);
  MVP->ARRAY[1].ADDRCFG = MVP_ARRAY_PTR(input_b);
  MVP->ARRAY[2].ADDRCFG = MVP_ARRAY_PTR(output);
  // Program loop controllers.
  MVP->LOOP[1].RST = 0;
  MVP->LOOP[0].CFG = (m - 1) << _MVP_LOOPCFG_NUMITERS_SHIFT;
  MVP->LOOP[1].CFG = ((n - 1) << _MVP_LOOPCFG_NUMITERS_SHIFT)
                     | ((SLI_MVP_LOOP_INCRDIM(SLI_MVP_ARRAY(0), SLI_MVP_INCRDIM_HEIGHT)
                         | SLI_MVP_LOOP_INCRDIM(SLI_MVP_ARRAY(1), SLI_MVP_INCRDIM_HEIGHT)
                         | SLI_MVP_LOOP_INCRDIM(SLI_MVP_ARRAY(2), SLI_MVP_INCRDIM_HEIGHT))
                        << _MVP_LOOPCFG_ARRAY0INCRDIM0_SHIFT);
  // Program instruction.
  MVP->INSTR[0].CFG0 = SLI_MVP_ALU_X(SLI_MVP_R1) | SLI_MVP_ALU_Y(SLI_MVP_R2) | SLI_MVP_ALU_Z(SLI_MVP_R3);
  MVP->INSTR[0].CFG1 = SLI_MVP_LOAD(0, SLI_MVP_R1, SLI_MVP_ARRAY(0), SLI_MVP_INCRDIM_WIDTH)
                       | SLI_MVP_LOAD(1, SLI_MVP_R2, SLI_MVP_ARRAY(1), SLI_MVP_INCRDIM_WIDTH)
                       | SLI_MVP_STORE(SLI_MVP_R3, SLI_MVP_ARRAY(2), SLI_MVP_INCRDIM_WIDTH);
  MVP->INSTR[0].CFG2 = (SLI_MVP_OP(MULR2A) << _MVP_INSTRCFG2_ALUOP_SHIFT)
                       | MVP_INSTRCFG2_ENDPROG | 3 | (3 << 2);

  // Start program.
  MVP->CMD = MVP_CMD_INIT | MVP_CMD_START;
  MVP_SIMULATOR_EXECUTE();

  #endif
  sli_mvp_wait_for_completion();
  // When factorization above is incomplete we handle "tail" elements here.
  i = length - remainder;
  while (remainder--) {
    output[i] = input_a[i] * input_b[i];
    i++;
  }

  return SL_STATUS_OK;
}
