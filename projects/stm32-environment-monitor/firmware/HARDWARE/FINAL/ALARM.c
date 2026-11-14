#include "monitor.h"
#include "stm32f4xx.h"
#include <math.h>

u8 Check_Alarm_Level(void)
{
    u8 temp_status = 0;     
    u8 light_status = 0;
    
    float temp  = g_sys.temperature;
    u16   light = g_sys.light_percent;
    
    float temp_high = g_sys.temp_high_threshold;
    float temp_low  = g_sys.temp_low_threshold;
    u16   light_low = g_sys.light_low_threshold;
    u16   light_high = g_sys.light_high_threshold;
    
    float temp_warn_high = temp_high - (temp_high - temp_low) * WARNING_MARGIN;
    float temp_warn_low  = temp_low  + (temp_high - temp_low) * WARNING_MARGIN;
    
    if (temp > temp_high || temp < temp_low)
    {
        temp_status = 2;   
    }
    else if (temp > temp_warn_high || temp < temp_warn_low)
    {
        temp_status = 1;    
    }
    
    u16 light_warn_margin = (u16)((light_high - light_low) * WARNING_MARGIN);
    
    if (light < light_low || light > light_high)
    {
        light_status = 2;   
    }
    else if (light < (light_low + light_warn_margin) || 
             light > (light_high - light_warn_margin))
    {
        light_status = 1;   
    }
    
    if (temp_status == 2 && light_status == 2)
        return LEVEL_CRITICAL;
    else if (temp_status == 2 || light_status == 2)
        return LEVEL_ALARM;
    else if (temp_status == 1 || light_status == 1)
        return LEVEL_WARNING;
    else
        return LEVEL_NORMAL;
}

void Alarm_Control(u8 level)
{
    u8 prev_level = g_sys.alarm_level;
    g_sys.alarm_level = level;
    
    if (level != prev_level)
    {
        g_sys.alarm_muted = 0;
    }
    
    if (level == LEVEL_NORMAL)
    {
        TIM_Cmd(TIM4, DISABLE);
        TIM_SetCounter(TIM4, 0);
        LED1 = 1;
        Beep = 0;
    }
    else
    {
        if (prev_level == LEVEL_NORMAL)
        {
            TIM_SetCounter(TIM4, 0);
            TIM_Cmd(TIM4, ENABLE);
        }
    }
}

void Alarm_Mute(void)
{
    g_sys.alarm_muted = 1;
    Beep = 0;
}
