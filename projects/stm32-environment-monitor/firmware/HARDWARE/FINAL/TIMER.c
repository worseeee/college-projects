#include "monitor.h"
#include "stm32f4xx.h"

void Timer_Init(void)
{
    TIM_TimeBaseInitTypeDef TIM_TimeBaseInitStruct;
    NVIC_InitTypeDef NVIC_InitStruct;
    
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM3, ENABLE);
    
    TIM_TimeBaseInitStruct.TIM_Period        = 4999;    
    TIM_TimeBaseInitStruct.TIM_Prescaler     = 8399;    
    TIM_TimeBaseInitStruct.TIM_ClockDivision = TIM_CKD_DIV1;
    TIM_TimeBaseInitStruct.TIM_CounterMode   = TIM_CounterMode_Up;
    TIM_TimeBaseInit(TIM3, &TIM_TimeBaseInitStruct);
    
    NVIC_InitStruct.NVIC_IRQChannel                   = TIM3_IRQn;
    NVIC_InitStruct.NVIC_IRQChannelPreemptionPriority = 1;
    NVIC_InitStruct.NVIC_IRQChannelSubPriority        = 0;
    NVIC_InitStruct.NVIC_IRQChannelCmd                = ENABLE;
    NVIC_Init(&NVIC_InitStruct);
    
    TIM_ITConfig(TIM3, TIM_IT_Update, ENABLE);
    TIM_Cmd(TIM3, ENABLE);
    
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM4, ENABLE);
    
    TIM_TimeBaseInitStruct.TIM_Period    = 999;     
    TIM_TimeBaseInitStruct.TIM_Prescaler = 8399;
    TIM_TimeBaseInit(TIM4, &TIM_TimeBaseInitStruct);
    
    NVIC_InitStruct.NVIC_IRQChannel                   = TIM4_IRQn;
    NVIC_InitStruct.NVIC_IRQChannelPreemptionPriority = 1;
    NVIC_InitStruct.NVIC_IRQChannelSubPriority        = 1;
    NVIC_InitStruct.NVIC_IRQChannelCmd                = ENABLE;
    NVIC_Init(&NVIC_InitStruct);
    
    TIM_ITConfig(TIM4, TIM_IT_Update, ENABLE);
    // TIM4????, ???????
    TIM_Cmd(TIM4, DISABLE);
}

void TIM3_IRQHandler(void)
{
    if (TIM_GetITStatus(TIM3, TIM_IT_Update) == SET)
    {
        g_sys.sample_flag = 1;
        g_sys.sample_count++;
        
        if (g_sys.alarm_level == LEVEL_NORMAL)
        {
            LED0 = !LED0;
        }
    }
    TIM_ClearITPendingBit(TIM3, TIM_IT_Update);
}

void TIM4_IRQHandler(void)
{
    static u8 beep_counter = 0;
    
    if (TIM_GetITStatus(TIM4, TIM_IT_Update) == SET)
    {
        switch (g_sys.alarm_level)
        {
            case LEVEL_WARNING:
                LED0 = !LED0;
                LED1 = 1;       
                Beep = 0;
                break;
                
            case LEVEL_ALARM:
                LED0 = !LED0;
                LED1 = !LED1;
                if (!g_sys.alarm_muted)
                {
                    beep_counter++;
                    Beep = (beep_counter % 5 == 0) ? 1 : 0;
                }
                break;
                
            case LEVEL_CRITICAL:
                LED0 = 0;   
                LED1 = 0;   
                if (!g_sys.alarm_muted)
                    Beep = 1;
                break;
                
            default:
                break;
        }
    }
    TIM_ClearITPendingBit(TIM4, TIM_IT_Update);
}
