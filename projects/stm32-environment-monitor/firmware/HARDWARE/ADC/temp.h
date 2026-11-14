#ifndef __ADC_H
#define __ADC_H

#include "stm32f4xx.h"

void AdCtemp_Init(void);
float Get_Temp(ADC_TypeDef* ADCx);
u16 Get_Light(ADC_TypeDef* ADCx);

#endif
