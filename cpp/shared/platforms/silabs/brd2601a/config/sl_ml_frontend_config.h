/***************************************************************************//**
 * @file
 * @brief FFT Configuration
 *******************************************************************************
 * # License
 * <b>Copyright 2021 Silicon Laboratories Inc. www.silabs.com</b>
 *******************************************************************************
 *
 * The licensor of this software is Silicon Laboratories Inc.  Your use of this
 * software is governed by the terms of Silicon Labs Master Software License
 * Agreement (MSLA) available at
 * www.silabs.com/about-us/legal/master-software-license-agreement.  This
 * software is distributed to you in Source Code format and is governed by the
 * sections of the MSLA applicable to Source Code.
 *
 ******************************************************************************/

#ifndef SL_ML_FRONTEND_CONFIG_H
#define SL_ML_FRONTEND_CONFIG_H

// <<< Use Configuration Wizard in Context Menu >>>

//   <o>FFT length             
//   <32U=> 32   
//   <64U=> 64
//   <128U=> 128 
//   <256U=> 256
//   <512U=> 512
//   <1024U=> 1024
//   <2048U=> 2048
//   <4096U=> 4096
//   <8192U=> 8192           
//   <i> Specifies the length of the RFFT        
//   <i> Only supports lengths of a power of 2    
//   <i> Default: 256U                     
#define SL_ML_FRONTEND_CONFIG_RFFT_LEN			256U

// <<< end of configuration section >>>


#endif // SL_ML_FRONTEND_CONFIG_H
