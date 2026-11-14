#ifndef __DAC_H
#define __DAC_H

#include "stm32f4xx.h"

void DaC_Init(void);
float Set_Vol(u16 vol);
float Get_DAC(ADC_TypeDef* ADCx);

#endif
