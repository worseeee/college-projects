#include "stm32f4xx.h"
#include "delay.h"
#include "lcd.h"
#include "usart.h"
#include "monitor.h"
#include <math.h>

SystemState_t g_sys;
static u8 last_mode = 0xFF;
static u8 full_redraw = 1;      

void System_Init(void)
{
    NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);
    
    delay_init(168);
    
    uart_init(115200);
    
		LED_BEEP_Init();
		Sensor_ADC_Init();      
    DAC_Threshold_Init();   
    EXTI_KEY_Init();        
    Timer_Init();           
    
    LCD_Init();
    LCD_Display_Dir(1);    
    POINT_COLOR = WHITE;
    BACK_COLOR  = BLACK;
    LCD_Clear(BLACK);
    
    g_sys.temperature           = 25.0f;
    g_sys.light_percent         = 50;
    g_sys.temp_high_threshold   = DEFAULT_TEMP_HIGH;
    g_sys.temp_low_threshold    = DEFAULT_TEMP_LOW;
    g_sys.light_low_threshold   = DEFAULT_LIGHT_LOW;
    g_sys.light_high_threshold  = DEFAULT_LIGHT_HIGH;
    g_sys.work_mode             = MODE_MONITOR;
    g_sys.alarm_level           = LEVEL_NORMAL;
    g_sys.alarm_muted           = 0;
    g_sys.setting_target        = 0;
    g_sys.history_index         = 0;
    g_sys.history_count         = 0;
    g_sys.sample_flag           = 0;
    g_sys.display_refresh       = 1;
    g_sys.sample_count          = 0;
}

void System_SelfTest(void)
{
    u8 i;
    
    POINT_COLOR = CYAN;
    LCD_ShowString(100, 100, 300, 24, 24, (u8 *)"System Self-Test...");
    
    for (i = 0; i < 2; i++)
    {
        LED0 = 0; LED1 = 0; Beep = 1;
        delay_ms(200);
        LED0 = 1; LED1 = 1; Beep = 0;
        delay_ms(200);
    }
    
    g_sys.temperature   = Get_Temperature();
    g_sys.light_percent = Get_Light_Percent();
    
    Set_DAC_Voltage(1.65f);
    delay_ms(50);
    Get_DAC_Readback();
    
    u8 buf[50];
    POINT_COLOR = GREEN;
    sprintf((char *)buf, "Temp: %.1f C  Light: %d%%", g_sys.temperature, g_sys.light_percent);
    LCD_ShowString(60, 140, 400, 24, 24, buf);
    
    sprintf((char *)buf, "DAC: %.2fV  ADC: %.2fV", g_sys.dac_voltage, g_sys.adc_readback);
    LCD_ShowString(60, 170, 400, 24, 24, buf);
    
    if (fabs(g_sys.dac_voltage - g_sys.adc_readback) < 0.15f)
        LCD_ShowString(60, 200, 300, 24, 24, (u8 *)"Self-Test: ALL PASS!");
    else
        LCD_ShowString(60, 200, 300, 24, 24, (u8 *)"Self-Test: DAC WARN!");
    
    delay_ms(2000);
    LCD_Clear(BLACK);
    
    printf("System Init OK. Temp=%.1f, Light=%d%%\r\n", g_sys.temperature, g_sys.light_percent);
}

void Process_Keys(void)
{
    if (KEY0_flag)
    {
        KEY0_flag = 0;
        
        if (g_sys.work_mode == MODE_SETTING)
        {
            g_sys.setting_target++;
            
            if (g_sys.setting_target >= 4)
            {
                g_sys.setting_target = 0;
                g_sys.work_mode = MODE_HISTORY;
                LCD_Clear(BLACK);   
            }
        }
        else
        {
            g_sys.work_mode = (g_sys.work_mode + 1) % MODE_COUNT;
            g_sys.setting_target = 0;
            LCD_Clear(BLACK);       
        }
        
        g_sys.display_refresh = 1;
    }
    
    if (KEY1_flag)
    {
        KEY1_flag = 0;
        
        if (g_sys.work_mode == MODE_SETTING)
        {
            switch (g_sys.setting_target)
            {
                case 0:
                    g_sys.temp_high_threshold += 1.0f;
                    if (g_sys.temp_high_threshold > 80.0f) 
                        g_sys.temp_high_threshold = 80.0f;
                    break;
                case 1:
                    g_sys.temp_low_threshold += 1.0f;
                    if (g_sys.temp_low_threshold >= g_sys.temp_high_threshold - 5.0f)
                        g_sys.temp_low_threshold = g_sys.temp_high_threshold - 5.0f;
                    break;
                case 2:
                    g_sys.light_low_threshold += 5;
                    if (g_sys.light_low_threshold >= g_sys.light_high_threshold - 10)
                        g_sys.light_low_threshold = g_sys.light_high_threshold - 10;
                    break;
                case 3:
                    g_sys.light_high_threshold += 5;
                    if (g_sys.light_high_threshold > 100)
                        g_sys.light_high_threshold = 100;
                    break;
            }
            g_sys.display_refresh = 1;
        }
    }
    
    if (KEY2_flag)
    {
        KEY2_flag = 0;
        
        if (g_sys.work_mode == MODE_SETTING)
        {
            switch (g_sys.setting_target)
            {
                case 0:
                    g_sys.temp_high_threshold -= 1.0f;
                    if (g_sys.temp_high_threshold <= g_sys.temp_low_threshold + 5.0f)
                        g_sys.temp_high_threshold = g_sys.temp_low_threshold + 5.0f;
                    break;
                case 1:
                    g_sys.temp_low_threshold -= 1.0f;
                    if (g_sys.temp_low_threshold < -20.0f)
                        g_sys.temp_low_threshold = -20.0f;
                    break;
                case 2:
                    if (g_sys.light_low_threshold >= 5)
                        g_sys.light_low_threshold -= 5;
                    else
                        g_sys.light_low_threshold = 0;
                    break;
                case 3:
                    g_sys.light_high_threshold -= 5;
                    if (g_sys.light_high_threshold <= g_sys.light_low_threshold + 10)
                        g_sys.light_high_threshold = g_sys.light_low_threshold + 10;
                    break;
            }
            g_sys.display_refresh = 1;
        }
    }
    
    if (WKUP_flag)
    {
        WKUP_flag = 0;
        Alarm_Mute();
        g_sys.display_refresh = 1;
    }
}

void Update_History(void)
{
    g_sys.temp_history[g_sys.history_index]  = g_sys.temperature;
    g_sys.light_history[g_sys.history_index] = g_sys.light_percent;
    
    g_sys.history_index = (g_sys.history_index + 1) % HISTORY_SIZE;
    
    if (g_sys.history_count < HISTORY_SIZE)
        g_sys.history_count++;
}

int main(void)
{
    System_Init();
    System_SelfTest();
    
    while (1)
    {
        Process_Keys();
        
        if (g_sys.sample_flag)
        {
            g_sys.sample_flag = 0;
            
            g_sys.temperature   = Get_Temperature();
            g_sys.light_percent = Get_Light_Percent();
            Get_DAC_Readback();
            Update_History();
            
            u8 alarm = Check_Alarm_Level();
            Alarm_Control(alarm);
            
            g_sys.display_refresh = 1;
        }
        
        if (g_sys.display_refresh)
        {
            g_sys.display_refresh = 0;
            
            if (last_mode != g_sys.work_mode)
            {
                last_mode = g_sys.work_mode;
                full_redraw = 1;
            }
            
            LCD_Show_StatusBar();
            
            if (full_redraw)
            {
                full_redraw = 0;
                switch (g_sys.work_mode)
                {
                    case MODE_MONITOR:  LCD_Show_Monitor_Full();  break;
                    case MODE_SETTING:  LCD_Show_Setting();       break;
                    case MODE_HISTORY:  LCD_Show_History();       break;
                }
            }
            else
            {
                switch (g_sys.work_mode)
                {
                    case MODE_MONITOR:  LCD_Show_Monitor_Update(); break;
                    case MODE_SETTING:  LCD_Show_Setting();        break;
                    case MODE_HISTORY:  break;
                }
            }
        }
        
        delay_ms(5);
    }
}
