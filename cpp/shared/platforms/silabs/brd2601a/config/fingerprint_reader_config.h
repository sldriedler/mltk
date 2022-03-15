

// Function | R503 Wire Pin (Color)  | BRD2601A Header Pin |
//----------|------------------------|---------------------|
// TXD      | 3 (Yellow)             |  6                  |
// RXD      | 4 (Green)              |  4                  |
// Wakeup   | 5 (Blue)               |  10                 |
// 3.3V     | 1 & 6 (Red & White)    |  20                 |
// GND      | 2 (Black)              |  1                  |



#define FINGERPRINT_READER_USART_PERIPHERAL_NO             0

#define FINGERPRINT_READER_USART_RX_PORT                   gpioPortC        
#define FINGERPRINT_READER_USART_RX_PIN                    2

#define FINGERPRINT_READER_USART_TX_PORT                   gpioPortC        
#define FINGERPRINT_READER_USART_TX_PIN                    3

#define FINGERPRINT_READER_ACTIVITY_PORT                   gpioPortA      
#define FINGERPRINT_READER_ACTIVITY_PIN                    7


#define FINGERPRINT_READER_DUMP_SENSOR_INFO
//#define FINGERPRINT_READER_DEBUG_ENABLED