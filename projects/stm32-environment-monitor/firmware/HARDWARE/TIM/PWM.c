#include "stm32f4xx.h"

void GPIOpwm_Init()
{
	GPIO_InitTypeDef GPIO_InitStruct;
	
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOF, ENABLE);
	
	GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF;
	GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
	GPIO_InitStruct.GPIO_Pin = GPIO_Pin_9;
	GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_UP;
	GPIO_InitStruct.GPIO_Speed = GPIO_High_Speed;
	
	GPIO_Init(GPIOF, &GPIO_InitStruct);
	
	GPIO_PinAFConfig(GPIOF, GPIO_PinSource9, GPIO_AF_TIM14);
	
	GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF;
	GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;
	GPIO_InitStruct.GPIO_Pin = GPIO_Pin_6;
	GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_UP;
	GPIO_InitStruct.GPIO_Speed = GPIO_High_Speed;
	
	GPIO_Init(GPIOF, &GPIO_InitStruct);
	
	GPIO_PinAFConfig(GPIOF, GPIO_PinSource6, GPIO_AF_TIM10);
}

void TIMpwm_TimeBaseInit()
{
	TIM_TimeBaseInitTypeDef TIM_TimeBaseInitStruct;
	
	RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM14, ENABLE);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_TIM10, ENABLE);
	
	TIM_TimeBaseInitStruct.TIM_Period = 499;
	TIM_TimeBaseInitStruct.TIM_Prescaler = 83;
	TIM_TimeBaseInitStruct.TIM_ClockDivision = TIM_CKD_DIV1;
	TIM_TimeBaseInitStruct.TIM_CounterMode = TIM_CounterMode_Up;
	
	TIM_TimeBaseInit(TIM14, &TIM_TimeBaseInitStruct);
	
	TIM_Cmd(TIM14, ENABLE);
	
	TIM_TimeBaseInitStruct.TIM_Period = 499;
	TIM_TimeBaseInitStruct.TIM_Prescaler = 83;
	TIM_TimeBaseInitStruct.TIM_ClockDivision = TIM_CKD_DIV1;
	TIM_TimeBaseInitStruct.TIM_CounterMode = TIM_CounterMode_Up;
	
	TIM_TimeBaseInit(TIM10, &TIM_TimeBaseInitStruct);
	
	TIM_Cmd(TIM10, ENABLE);
}

void TIMpwm_OC1Init()
{
	TIM_OCInitTypeDef TIM_OCInitStruct;
	
	TIM_OCInitStruct.TIM_OCMode = TIM_OCMode_PWM2;
	TIM_OCInitStruct.TIM_OutputState = TIM_OutputState_Enable;
	TIM_OCInitStruct.TIM_Pulse = 0;
	TIM_OCInitStruct.TIM_OCPolarity = TIM_OCPolarity_High;
	
	TIM_OC1Init(TIM14, &TIM_OCInitStruct);
	
	TIM_OC1PreloadConfig(TIM14, TIM_OCPreload_Enable);
	
	TIM_OCInitStruct.TIM_OCMode = TIM_OCMode_PWM2;
	TIM_OCInitStruct.TIM_OutputState = TIM_OutputState_Enable;
	TIM_OCInitStruct.TIM_Pulse = 0;
	TIM_OCInitStruct.TIM_OCPolarity = TIM_OCPolarity_High;
	
	TIM_OC1Init(TIM10, &TIM_OCInitStruct);
	
	TIM_OC1PreloadConfig(TIM10, TIM_OCPreload_Enable);
}
