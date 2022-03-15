
#include "platform_api.h"



// --------------------------------------
// BRD4001A expansion header pin mapping
//---------------------------------------
// Header Pin  | Function
//-------------|----------------
//          15 | I2C_SCL
//          16 | I2C_SDA
//           4 | SPI_MOSI
//           6 | SPI_MISO
//           8 | SPI_SCK
//          10 | SPI_CS
//           1 | GND
//          18 | 5V


// TODO: Verify these mappings work

#define ARDUCAM_I2C_PERIPHERAL_NO               0

#define ARDUCAM_I2C_SDA_PORT                    gpioPortC
#define ARDUCAM_I2C_SDA_PIN                     7

#define ARDUCAM_I2C_SCL_PORT                    gpioPortC
#define ARDUCAM_I2C_SCL_PIN                     5


#define ARDUCAM_USART_PERIPHERAL_NO             0

#define ARDUCAM_USART_CS_PORT                   gpioPortC     
#define ARDUCAM_USART_CS_PIN                    0

#define ARDUCAM_USART_CLK_PORT                  gpioPortC        
#define ARDUCAM_USART_CLK_PIN                   3

#define ARDUCAM_USART_RX_PORT                   gpioPortC        
#define ARDUCAM_USART_RX_PIN                    2

#define ARDUCAM_USART_TX_PORT                   gpioPortC        
#define ARDUCAM_USART_TX_PIN                    1


#define ARDUCAM_DELAY_US(us) platform_sleep_us(us)
#define ARDUCAM_DELAY_MS(ms) platform_sleep_ms(ms)