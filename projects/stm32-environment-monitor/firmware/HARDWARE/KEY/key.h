#ifndef __KEY_H
#define __KEY_H

#include "sys.h"
#include "stm32f4xx.h"

#define WK_UP PAin(0)
//#define WK_UP GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_0)
#define KEY_0 PEin(4)
#define KEY_1 PEin(3)
#define KEY_2 PEin(2)

void KEY_Init(void);

u8 KEY_Scan(void);
#endif
