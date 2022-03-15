

// Function | R503 Wire Pin (Color)  | STK3701A Header Pin |
//----------|------------------------|---------------------|
// TXD      | 3 (Yellow)             |  6                  |
// RXD      | 4 (Green)              |  4                  |
// Wakeup   | 5 (Blue)               |  10                 |
// 3.3V     | 1 & 6 (Red & White)    |  20                 |
// GND      | 2 (Black)              |  1                  |



#define FINGERPRINT_READER_USART_PERIPHERAL_NO             0

#define FINGERPRINT_READER_USART_RX_PORT                   gpioPortE        
#define FINGERPRINT_READER_USART_RX_PIN                    11
#define FINGERPRINT_READER_USART_RX_LOC                    0

#define FINGERPRINT_READER_USART_TX_PORT                   gpioPortE       
#define FINGERPRINT_READER_USART_TX_PIN                    10
#define FINGERPRINT_READER_USART_TX_LOC                    0

#define FINGERPRINT_READER_ACTIVITY_PORT                   gpioPortE      
#define FINGERPRINT_READER_ACTIVITY_PIN                    13

#define FINGERPRINT_READER_DUMP_SENSOR_INFO
//#define FINGERPRINT_READER_DEBUG_ENABLED