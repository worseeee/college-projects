#include "temp.h"
#include "stm32f4xx.h"
#include <stdio.h>

void AdCtemp_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct;
	ADC_CommonInitTypeDef ADC_CommonInitStruct;
	ADC_InitTypeDef ADC_InitStruct;
	
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOF, ENABLE);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC1, ENABLE);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC3, ENABLE);
	
	RCC_APB2PeriphResetCmd(RCC_APB2Periph_ADC1,ENABLE); 
	RCC_APB2PeriphResetCmd(RCC_APB2Periph_ADC1,DISABLE);
	RCC_APB2PeriphResetCmd(RCC_APB2Periph_ADC3,ENABLE); 
	RCC_APB2PeriphResetCmd(RCC_APB2Periph_ADC3,DISABLE);
	
	GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AN;
	GPIO_InitStruct.GPIO_Pin = GPIO_Pin_7;
	GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_NOPULL;
	GPIO_InitStruct.GPIO_Speed = GPIO_High_Speed;
	
	GPIO_Init(GPIOF, &GPIO_InitStruct);
	
	ADC_CommonInitStruct.ADC_Mode = ADC_Mode_Independent;
	ADC_CommonInitStruct.ADC_TwoSamplingDelay = ADC_TwoSamplingDelay_5Cycles;
	ADC_CommonInitStruct.ADC_DMAAccessMode = ADC_DMAAccessMode_Disabled;
	ADC_CommonInitStruct.ADC_Prescaler = ADC_Prescaler_Div4;
	
	ADC_CommonInit(&ADC_CommonInitStruct);
	
	ADC_InitStruct.ADC_Resolution = ADC_Resolution_10b;
	ADC_InitStruct.ADC_ScanConvMode = DISABLE;
	ADC_InitStruct.ADC_ContinuousConvMode = DISABLE;
	ADC_InitStruct.ADC_ExternalTrigConvEdge = ADC_ExternalTrigConvEdge_None;
	ADC_InitStruct.ADC_DataAlign = ADC_DataAlign_Right;
	ADC_InitStruct.ADC_NbrOfConversion = 1;
	
	ADC_Init(ADC1, &ADC_InitStruct);
	
	ADC_InitStruct.ADC_Resolution = ADC_Resolution_8b;
	ADC_InitStruct.ADC_ScanConvMode = DISABLE;
	ADC_InitStruct.ADC_ContinuousConvMode = DISABLE;
	ADC_InitStruct.ADC_ExternalTrigConvEdge = ADC_ExternalTrigConvEdge_None;
	ADC_InitStruct.ADC_DataAlign = ADC_DataAlign_Right;
	ADC_InitStruct.ADC_NbrOfConversion = 1;
	
	ADC_Init(ADC3, &ADC_InitStruct);
	
	ADC_Cmd(ADC1, ENABLE);
	ADC_Cmd(ADC3, ENABLE);
	
	ADC_TempSensorVrefintCmd(ENABLE);
	
	ADC_RegularChannelConfig(ADC1, ADC_Channel_16, 1, ADC_SampleTime_480Cycles);
	ADC_RegularChannelConfig(ADC3, ADC_Channel_5, 1, ADC_SampleTime_480Cycles);
}


float Get_Temp(ADC_TypeDef* ADCx)
{
	ADC_SoftwareStartConv(ADCx);
	
	while (!ADC_GetFlagStatus(ADCx, ADC_FLAG_EOC));
	u16 value = ADC_GetConversionValue(ADCx);
	float V_sense = (float)(value * 3.3f / 1024.0f);
	float temp = (V_sense - 0.76f) / 0.0025f + 25.0f;

	return temp;
}

u16 Get_Light(ADC_TypeDef* ADCx)
{
	ADC_SoftwareStartConv(ADCx);
	
	u16 light;
	
	while (!ADC_GetFlagStatus(ADCx, ADC_FLAG_EOC));
	u16 value = ADC_GetConversionValue(ADCx);
	if (value > 250)
		value = 250;
	light = (u16)(100 - (value / 2.5));
	
	return light;
}

