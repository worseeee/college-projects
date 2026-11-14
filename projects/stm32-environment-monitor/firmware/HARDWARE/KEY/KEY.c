#include "key.h"
#include "stm32f4xx.h"
#include "delay.h"

void KEY_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct;
	
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOE, ENABLE);
	
	GPIO_InitStruct.GPIO_Mode = GPIO_Mode_IN;
	GPIO_InitStruct.GPIO_Pin = GPIO_Pin_4;
	GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_UP;
	GPIO_InitStruct.GPIO_Speed = GPIO_Fast_Speed;
	
	GPIO_Init(GPIOE, &GPIO_InitStruct);
	
	GPIO_InitStruct.GPIO_Mode = GPIO_Mode_IN;
	GPIO_InitStruct.GPIO_Pin = GPIO_Pin_3;
	GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_UP;
	GPIO_InitStruct.GPIO_Speed = GPIO_Fast_Speed;
	
	GPIO_Init(GPIOE, &GPIO_InitStruct);
	
	GPIO_InitStruct.GPIO_Mode = GPIO_Mode_IN;
	GPIO_InitStruct.GPIO_Pin = GPIO_Pin_2;
	GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_UP;
	GPIO_InitStruct.GPIO_Speed = GPIO_Fast_Speed;
	
	GPIO_Init(GPIOE, &GPIO_InitStruct);
	
	GPIO_InitStruct.GPIO_Mode = GPIO_Mode_IN;
	GPIO_InitStruct.GPIO_Pin = GPIO_Pin_0;
	GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_DOWN;
	GPIO_InitStruct.GPIO_Speed = GPIO_Fast_Speed;
	
	GPIO_Init(GPIOA, &GPIO_InitStruct);
	
}

u8 KEY_Scan(void)
{
	if (KEY_0 == 0)
	{
		delay_ms(10);
		if (KEY_0 == 0)
		{
			while (KEY_0 == 0);
			return 4;
		}
	}
	
	if (KEY_1 == 0)
	{
		delay_ms(10);
		if (KEY_1 == 0)
		{
			while (KEY_1 == 0);
			return 3;
		}
	}
	
	if (KEY_2 == 0)
	{
		delay_ms(10);
		if (KEY_2 == 0)
		{
			while (KEY_2 == 0);
			return 2;
		}
	}
	
	if (WK_UP == 1)
	{
		delay_ms(10);
		if (WK_UP == 1)
		{
			while (WK_UP == 1);
			return 1;
		}
	}
		
	return 0;
}
