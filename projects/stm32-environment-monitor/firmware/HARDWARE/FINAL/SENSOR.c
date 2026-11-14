#include "monitor.h"
#include "stm32f4xx.h"
#include "delay.h"

void Sensor_ADC_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    ADC_CommonInitTypeDef ADC_CommonInitStruct;
    ADC_InitTypeDef ADC_InitStruct;
    
    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);  
    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOF, ENABLE);  
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC1, ENABLE);    
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC3, ENABLE);    
    
    GPIO_InitStruct.GPIO_Mode  = GPIO_Mode_AN;
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStruct.GPIO_Pin   = GPIO_Pin_7;
    GPIO_InitStruct.GPIO_PuPd  = GPIO_PuPd_NOPULL;
    GPIO_InitStruct.GPIO_Speed = GPIO_High_Speed;
    GPIO_Init(GPIOF, &GPIO_InitStruct);
    
    GPIO_InitStruct.GPIO_Pin = GPIO_Pin_5;
    GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    ADC_CommonInitStruct.ADC_Mode             = ADC_Mode_Independent;
    ADC_CommonInitStruct.ADC_TwoSamplingDelay = ADC_TwoSamplingDelay_5Cycles;
    ADC_CommonInitStruct.ADC_DMAAccessMode    = ADC_DMAAccessMode_Disabled;
    ADC_CommonInitStruct.ADC_Prescaler        = ADC_Prescaler_Div4;
    ADC_CommonInit(&ADC_CommonInitStruct);
    
    ADC_InitStruct.ADC_Resolution           = ADC_Resolution_10b;
    ADC_InitStruct.ADC_ScanConvMode         = DISABLE;
    ADC_InitStruct.ADC_ContinuousConvMode   = DISABLE;
    ADC_InitStruct.ADC_ExternalTrigConvEdge = ADC_ExternalTrigConvEdge_None;
    ADC_InitStruct.ADC_DataAlign            = ADC_DataAlign_Right;
    ADC_InitStruct.ADC_NbrOfConversion      = 1;
    ADC_Init(ADC1, &ADC_InitStruct);
    
    ADC_InitStruct.ADC_Resolution = ADC_Resolution_12b;
    ADC_Init(ADC3, &ADC_InitStruct);
    
    ADC_TempSensorVrefintCmd(ENABLE);
    
    ADC_Cmd(ADC1, ENABLE);
    ADC_Cmd(ADC3, ENABLE);
}

u16 Get_ADC_Value(ADC_TypeDef *ADCx, u8 channel)
{
    u32 sum = 0;
    u8 i;
    const u8 AVERAGE_COUNT = 10;    
    
    for (i = 0; i < AVERAGE_COUNT; i++)
    {
        ADC_RegularChannelConfig(ADCx, channel, 1, ADC_SampleTime_480Cycles);
        
        ADC_SoftwareStartConv(ADCx);
        
        while (!ADC_GetFlagStatus(ADCx, ADC_FLAG_EOC));
        
        sum += ADC_GetConversionValue(ADCx);
    }
    
    return (u16)(sum / AVERAGE_COUNT);
}

float Get_Temperature(void)
{
    u16 adc_value;
    float v_sense, temperature;
    
    adc_value = Get_ADC_Value(ADC1, ADC_Channel_16);
    
    v_sense = (float)adc_value * 3.3f / 1024.0f;
    
    temperature = (v_sense - 0.76f) / 0.0025f + 25.0f;
    
    return temperature;
}

u16 Get_Light_Percent(void)
{
    u16 adc_value;
    u16 light;
    
    adc_value = Get_ADC_Value(ADC3, ADC_Channel_5);
    
    g_sys.light_raw = adc_value;
    
    if (adc_value > 4000)
        adc_value = 4000;
    
    light = (u16)(100 - (adc_value / 40));
    
    // ????
    if (light > 100) light = 100;
    
    return light;
}
