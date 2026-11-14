#include "dac.h"
#include "stm32f4xx.h"

void DaC_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct;
	ADC_CommonInitTypeDef ADC_CommonInitStruct;
	ADC_InitTypeDef ADC_InitStruct;
	DAC_InitTypeDef DAC_InitType;
	
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
	RCC_APB1PeriphClockCmd(RCC_APB1Periph_DAC, ENABLE);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC1, ENABLE);
	
	GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AN;
	GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
	GPIO_InitStruct.GPIO_Pin = GPIO_Pin_4;
	GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_DOWN;
	GPIO_InitStruct.GPIO_Speed = GPIO_High_Speed;
	
	GPIO_Init(GPIOA, &GPIO_InitStruct);
	
	GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AN;
	GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
	GPIO_InitStruct.GPIO_Pin = GPIO_Pin_5;
	GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_UP;
	GPIO_InitStruct.GPIO_Speed = GPIO_High_Speed;
	
	GPIO_Init(GPIOA, &GPIO_InitStruct);
	
	DAC_InitType.DAC_Trigger = DAC_Trigger_None;
	DAC_InitType.DAC_WaveGeneration = DAC_WaveGeneration_None;
	DAC_InitType.DAC_LFSRUnmask_TriangleAmplitude = DAC_LFSRUnmask_Bit0;
	DAC_InitType.DAC_OutputBuffer = DAC_OutputBuffer_Disable;
	DAC_Init(DAC_Channel_1, &DAC_InitType);
	
	DAC_Cmd(DAC_Channel_1, ENABLE);
	
	ADC_CommonInitStruct.ADC_Mode = ADC_Mode_Independent;
	ADC_CommonInitStruct.ADC_TwoSamplingDelay = ADC_TwoSamplingDelay_5Cycles;
	ADC_CommonInitStruct.ADC_DMAAccessMode = ADC_DMAAccessMode_Disabled;
	ADC_CommonInitStruct.ADC_Prescaler = ADC_Prescaler_Div4;
	
	ADC_CommonInit(&ADC_CommonInitStruct);
	
	ADC_InitStruct.ADC_Resolution = ADC_Resolution_8b;
	ADC_InitStruct.ADC_ScanConvMode = DISABLE;
	ADC_InitStruct.ADC_ContinuousConvMode = DISABLE;
	ADC_InitStruct.ADC_ExternalTrigConvEdge = ADC_ExternalTrigConvEdge_None;
	ADC_InitStruct.ADC_DataAlign = ADC_DataAlign_Right;
	ADC_InitStruct.ADC_NbrOfConversion = 1;
	ADC_Init(ADC1, &ADC_InitStruct);
	
	ADC_Cmd(ADC1, ENABLE);
	
}

float Set_Vol(u16 vol)
{
	float data = (float)vol / 100;
	data = data * 255.0f / 3.3f;
	DAC_SetChannel1Data(DAC_Align_8b_R, data);
	return data;
}

float Get_DAC(ADC_TypeDef* ADCx)
{
	ADC_RegularChannelConfig(ADC1, ADC_Channel_5, 1, ADC_SampleTime_480Cycles);
	ADC_SoftwareStartConv(ADCx);
	
	while (!ADC_GetFlagStatus(ADCx, ADC_FLAG_EOC));
	u16 V_ref = ADC_GetConversionValue(ADCx);
	float V_sense = (float)(V_ref * 3.3f / 255.0f);

	return V_sense;
}
