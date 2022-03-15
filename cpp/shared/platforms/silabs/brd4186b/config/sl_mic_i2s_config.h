/***************************************************************************//**
 * @file
 * @brief MIC_I2S config
 *******************************************************************************
 * # License
 * <b>Copyright 2020 Silicon Laboratories Inc. www.silabs.com</b>
 *******************************************************************************
 *
 * The licensor of this software is Silicon Laboratories Inc. Your use of this
 * software is governed by the terms of Silicon Labs Master Software License
 * Agreement (MSLA) available at
 * www.silabs.com/about-us/legal/master-software-license-agreement. This
 * software is distributed to you in Source Code format and is governed by the
 * sections of the MSLA applicable to Source Code.
 *
 ******************************************************************************/

#ifndef SL_MIC_I2S_CONFIG_H
#define SL_MIC_I2S_CONFIG_H


#define SL_MIC_I2S_PERIPHERAL                    USART0
#define SL_MIC_I2S_PERIPHERAL_NO                 0

// EXP header 6
#define SL_MIC_I2S_RX_PORT                       gpioPortC
#define SL_MIC_I2S_RX_PIN                        2

// EXP header 8
#define SL_MIC_I2S_CLK_PORT                      gpioPortC
#define SL_MIC_I2S_CLK_PIN                       3

// EXP header 10
#define SL_MIC_I2S_CS_PORT                       gpioPortC
#define SL_MIC_I2S_CS_PIN                        0


#endif // SL_MIC_I2S_CONFIG_H
