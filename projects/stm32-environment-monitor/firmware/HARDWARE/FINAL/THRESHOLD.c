#include "monitor.h"
#include "stm32f4xx.h"

void DAC_Threshold_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    DAC_InitTypeDef DAC_InitStruct;
    
    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_DAC, ENABLE);
    
    GPIO_InitStruct.GPIO_Mode  = GPIO_Mode_AN;
    GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStruct.GPIO_Pin   = GPIO_Pin_4;
    GPIO_InitStruct.GPIO_PuPd  = GPIO_PuPd_DOWN;
    GPIO_InitStruct.GPIO_Speed = GPIO_High_Speed;
    GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    DAC_InitStruct.DAC_Trigger        = DAC_Trigger_None;       
    DAC_InitStruct.DAC_WaveGeneration = DAC_WaveGeneration_None;
    DAC_InitStruct.DAC_OutputBuffer   = DAC_OutputBuffer_Disable;
    DAC_Init(DAC_Channel_1, &DAC_InitStruct);
    
    DAC_Cmd(DAC_Channel_1, ENABLE);
    
    Set_DAC_Voltage(1.65f);
}

void Set_DAC_Voltage(float voltage)
{
    u16 dac_value;
    
    if (voltage < 0.0f) voltage = 0.0f;
    if (voltage > 3.3f) voltage = 3.3f;
    
    dac_value = (u16)(voltage / 3.3f * 255.0f);
    
    DAC_SetChannel1Data(DAC_Align_8b_R, dac_value);
    
    g_sys.dac_voltage = voltage;
}

float Get_DAC_Readback(void)
{
    u16 adc_value;
    float voltage;
    
    adc_value = Get_ADC_Value(ADC1, ADC_Channel_5);
    
    voltage = (float)adc_value * 3.3f / 1024.0f;
    
    g_sys.adc_readback = voltage;
    
    return voltage;
}
