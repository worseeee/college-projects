#include "monitor.h"
#include "lcd.h"
#include <stdio.h>
#include <math.h>

void LCD_Draw_ProgressBar(u16 x, u16 y, u16 w, u16 h, u16 val, u16 max, u16 color)
{
    u16 fill_w;
    
    if (val > max) val = max;
    fill_w = (u16)((u32)val * w / max);
    
    POINT_COLOR = WHITE;
    LCD_DrawRectangle(x, y, x + w, y + h);
    
    if (fill_w > 0)
        LCD_Fill(x + 1, y + 1, x + fill_w - 1, y + h - 1, color);
    
    if (fill_w < w - 1)
        LCD_Fill(x + fill_w + 1, y + 1, x + w - 1, y + h - 1, BLACK);
}

void LCD_Show_StatusBar(void)
{
    const u8 *mode_str[] = {
        (u8 *)"MONITOR ",
        (u8 *)"SETTING ",
        (u8 *)"HISTORY "
    };
    const u8 *alarm_str[] = {
        (u8 *)"NORMAL  ", 
        (u8 *)"WARNING ",
        (u8 *)"ALARM   ",
        (u8 *)"CRITICAL"
    };
    const u16 alarm_color[] = {GREEN, YELLOW, RED, MAGENTA};
    
    u8 buf[40];
    u16 w = lcddev.width;
    
    LCD_Fill(0, 0, w - 1, 24, DARKBLUE);
    
    BACK_COLOR = DARKBLUE;
    
    POINT_COLOR = WHITE;
    LCD_ShowString(5, 4, 90, 16, 16, (u8 *)mode_str[g_sys.work_mode]);
    
    POINT_COLOR = alarm_color[g_sys.alarm_level];
    LCD_ShowString(100, 4, 80, 16, 16, (u8 *)alarm_str[g_sys.alarm_level]);
    
    if (g_sys.alarm_muted)
    {
        POINT_COLOR = YELLOW;
        LCD_ShowString(185, 4, 40, 16, 16, (u8 *)"MUTE");
    }
    
    POINT_COLOR = CYAN;
    sprintf((char *)buf, "N:%lu", g_sys.sample_count);
    LCD_ShowString(230, 4, 80, 16, 16, buf);
    
    POINT_COLOR = GRAY;
    if (g_sys.work_mode == MODE_SETTING)
    {
        sprintf((char *)buf, "K0:Next(%d/4) K1:+ K2:-", g_sys.setting_target + 1);
    }
    else
    {
        sprintf((char *)buf, "K0:Mode WK:Mute       ");
    }
    LCD_ShowString(320, 4, w - 320, 16, 16, buf);
    
    BACK_COLOR = BLACK;
}

void LCD_Show_Monitor_Full(void)
{
    LCD_Fill(0, 25, lcddev.width - 1, lcddev.height - 1, BLACK);
    
    POINT_COLOR = WHITE;
    LCD_ShowString(20, 30, 250, 24, 24, (u8 *)"== Temperature ==");
    LCD_ShowString(20, 120, 250, 24, 24, (u8 *)"== Light Level ==");
    
    POINT_COLOR = GRAY;
    LCD_ShowString(20, 210, 250, 16, 16, (u8 *)"--- DAC Verify ---");
    
    POINT_COLOR = WHITE;
    LCD_DrawRectangle(20, 95, 320, 109);    
    LCD_DrawRectangle(20, 180, 320, 194);   
    
    LCD_Show_Monitor_Update();
}

void LCD_Show_Monitor_Update(void)
{
    u8 buf[60];
    
    if (g_sys.temperature > g_sys.temp_high_threshold || 
        g_sys.temperature < g_sys.temp_low_threshold)
        POINT_COLOR = RED;
    else
        POINT_COLOR = GREEN;
    
    sprintf((char *)buf, "%.1f C     ", g_sys.temperature);
    BACK_COLOR = BLACK;
    LCD_ShowString(20, 60, 150, 24, 24, buf);
    
    POINT_COLOR = GRAY;
    sprintf((char *)buf, "[%.0f~%.0f C]   ", 
            g_sys.temp_low_threshold, g_sys.temp_high_threshold);
    LCD_ShowString(180, 64, 200, 16, 16, buf);
    
    u16 temp_val = (u16)((g_sys.temperature + 10.0f) * 4.0f);
    if (temp_val > 240) temp_val = 240;
    u16 fill_w = (u16)((u32)temp_val * 298 / 240);
    u16 tc = (g_sys.temperature > g_sys.temp_high_threshold) ? RED : 
             (g_sys.temperature < g_sys.temp_low_threshold)  ? BLUE : GREEN;
    
    if (fill_w > 0)
        LCD_Fill(21, 96, 21 + fill_w - 1, 108, tc);
    if (fill_w < 298)
        LCD_Fill(21 + fill_w, 96, 319, 108, BLACK);
    
    if (g_sys.light_percent < g_sys.light_low_threshold || 
        g_sys.light_percent > g_sys.light_high_threshold)
        POINT_COLOR = RED;
    else
        POINT_COLOR = GREEN;
    
    sprintf((char *)buf, "%d%%     ", g_sys.light_percent);
    LCD_ShowString(20, 150, 100, 24, 24, buf);
    
    POINT_COLOR = GRAY;
    sprintf((char *)buf, "[%d%%~%d%%] RAW:%d    ", 
            g_sys.light_low_threshold, g_sys.light_high_threshold, g_sys.light_raw);
    LCD_ShowString(130, 154, 340, 16, 16, buf);
    
    u16 lw = (u16)((u32)g_sys.light_percent * 298 / 100);
    u16 lc = (g_sys.light_percent < g_sys.light_low_threshold || 
              g_sys.light_percent > g_sys.light_high_threshold) ? RED : CYAN;
    
    if (lw > 0)
        LCD_Fill(21, 181, 21 + lw - 1, 193, lc);
    if (lw < 298)
        LCD_Fill(21 + lw, 181, 319, 193, BLACK);
    
    POINT_COLOR = YELLOW;
    sprintf((char *)buf, "Set:%.2fV Read:%.2fV ", g_sys.dac_voltage, g_sys.adc_readback);
    LCD_ShowString(20, 230, 320, 16, 16, buf);
    
    if (fabs(g_sys.dac_voltage - g_sys.adc_readback) < 0.15f)
    {
        POINT_COLOR = GREEN;
        LCD_ShowString(330, 230, 60, 16, 16, (u8 *)"[OK]  ");
    }
    else
    {
        POINT_COLOR = RED;
        LCD_ShowString(330, 230, 60, 16, 16, (u8 *)"[FAIL]");
    }
}

void LCD_Show_Setting(void)
{
    u8 buf[60];
    
    LCD_Fill(0, 25, lcddev.width - 1, lcddev.height - 1, BLACK);
    
    POINT_COLOR = WHITE;
    LCD_ShowString(20, 35, 400, 24, 24, (u8 *)"== Threshold Settings ==");
    
    POINT_COLOR = CYAN;
    LCD_ShowString(20, 65, 450, 16, 16, 
        (u8 *)"KEY1:Increase  KEY2:Decrease  KEY0:Next/Exit");
    
    POINT_COLOR = (g_sys.setting_target == 0) ? YELLOW : WHITE;
    sprintf((char *)buf, "%s Temp HIGH : %.1f C       ", 
            (g_sys.setting_target == 0) ? ">>" : "  ", 
            g_sys.temp_high_threshold);
    LCD_ShowString(20, 95, 430, 24, 24, buf);
    
    POINT_COLOR = (g_sys.setting_target == 1) ? YELLOW : WHITE;
    sprintf((char *)buf, "%s Temp LOW  : %.1f C       ", 
            (g_sys.setting_target == 1) ? ">>" : "  ", 
            g_sys.temp_low_threshold);
    LCD_ShowString(20, 125, 430, 24, 24, buf);
    
    POINT_COLOR = (g_sys.setting_target == 2) ? YELLOW : WHITE;
    sprintf((char *)buf, "%s Light LOW : %d%%          ", 
            (g_sys.setting_target == 2) ? ">>" : "  ", 
            g_sys.light_low_threshold);
    LCD_ShowString(20, 155, 430, 24, 24, buf);
    
    POINT_COLOR = (g_sys.setting_target == 3) ? YELLOW : WHITE;
    sprintf((char *)buf, "%s Light HIGH: %d%%          ", 
            (g_sys.setting_target == 3) ? ">>" : "  ", 
            g_sys.light_high_threshold);
    LCD_ShowString(20, 185, 430, 24, 24, buf);
    
    POINT_COLOR = GRAY;
    sprintf((char *)buf, "Setting %d / 4  (Press K0 at 4/4 to exit)", 
            g_sys.setting_target + 1);
    LCD_ShowString(20, 225, 450, 16, 16, buf);
    
    POINT_COLOR = CYAN;
    float ref_voltage = g_sys.temp_high_threshold / 50.0f * 3.3f;
    if (ref_voltage > 3.3f) ref_voltage = 3.3f;
    sprintf((char *)buf, "DAC Ref Output: %.2fV      ", ref_voltage);
    LCD_ShowString(20, 250, 400, 16, 16, buf);
    
    Set_DAC_Voltage(ref_voltage);
}

void LCD_Show_History(void)
{
    u8 buf[50];
    
    LCD_Fill(0, 25, lcddev.width - 1, lcddev.height - 1, BLACK);
    
    POINT_COLOR = WHITE;
    LCD_ShowString(GRAPH_X_START, 30, 200, 16, 16, (u8 *)"Temperature Trend");
    LCD_Draw_TempGraph();
    
    POINT_COLOR = WHITE;
    LCD_ShowString(GRAPH_X_START, 160, 200, 16, 16, (u8 *)"Light Level Trend");
    LCD_Draw_LightGraph();
    
    if (g_sys.history_count > 0)
    {
        float temp_sum = 0;
        u32 light_sum = 0;
        float temp_max_val = -100, temp_min_val = 200;
        u8 i;
        
        for (i = 0; i < g_sys.history_count; i++)
        {
            temp_sum += g_sys.temp_history[i];
            light_sum += g_sys.light_history[i];
            if (g_sys.temp_history[i] > temp_max_val) 
                temp_max_val = g_sys.temp_history[i];
            if (g_sys.temp_history[i] < temp_min_val) 
                temp_min_val = g_sys.temp_history[i];
        }
        
        POINT_COLOR = YELLOW;
        sprintf((char *)buf, "Avg:%.1fC  Max:%.1fC  Min:%.1fC", 
                temp_sum / g_sys.history_count, temp_max_val, temp_min_val);
        LCD_ShowString(20, 280, 450, 16, 16, buf);
        
        sprintf((char *)buf, "Avg Light:%d%%   Points:%d/%d   ", 
                (u16)(light_sum / g_sys.history_count),
                g_sys.history_count, HISTORY_SIZE);
        LCD_ShowString(20, 300, 450, 16, 16, buf);
    }
    else
    {
        POINT_COLOR = GRAY;
        LCD_ShowString(100, 150, 300, 24, 24, (u8 *)"No history data yet...");
    }
}

void LCD_Draw_TempGraph(void)
{
    u16 x_start = GRAPH_X_START;
    u16 y_start = GRAPH_Y_START;
    u16 width   = GRAPH_WIDTH;
    u16 height  = GRAPH_HEIGHT;
    
    u8 i;
    u16 x1, y1, x2, y2;
    float temp_min = 10.0f, temp_max = 50.0f;
    
    POINT_COLOR = GRAY;
    LCD_DrawLine(x_start, y_start, x_start, y_start + height);          
    LCD_DrawLine(x_start, y_start + height, x_start + width, y_start + height); 
    
    POINT_COLOR = RED;
    u16 y_high = y_start + height - (u16)((g_sys.temp_high_threshold - temp_min) / (temp_max - temp_min) * height);
    LCD_DrawLine(x_start, y_high, x_start + width, y_high);
    
    POINT_COLOR = BLUE;
    u16 y_low = y_start + height - (u16)((g_sys.temp_low_threshold - temp_min) / (temp_max - temp_min) * height);
    LCD_DrawLine(x_start, y_low, x_start + width, y_low);
    
    if (g_sys.history_count < 2) return;
    
    POINT_COLOR = GREEN;
    for (i = 0; i < g_sys.history_count - 1; i++)
    {
        float val1 = g_sys.temp_history[i];
        float val2 = g_sys.temp_history[i + 1];
        
        if (val1 < temp_min) val1 = temp_min;
        if (val1 > temp_max) val1 = temp_max;
        if (val2 < temp_min) val2 = temp_min;
        if (val2 > temp_max) val2 = temp_max;
        
        x1 = x_start + (u16)((u32)i * width / HISTORY_SIZE);
        y1 = y_start + height - (u16)((val1 - temp_min) / (temp_max - temp_min) * height);
        x2 = x_start + (u16)((u32)(i + 1) * width / HISTORY_SIZE);
        y2 = y_start + height - (u16)((val2 - temp_min) / (temp_max - temp_min) * height);
        
        LCD_DrawLine(x1, y1, x2, y2);
    }
}

void LCD_Draw_LightGraph(void)
{
    u16 x_start = GRAPH_X_START;
    u16 y_start = 175;          
    u16 width   = GRAPH_WIDTH;
    u16 height  = GRAPH_HEIGHT;
    
    u8 i;
    u16 x1, y1, x2, y2;
    
    POINT_COLOR = GRAY;
    LCD_DrawLine(x_start, y_start, x_start, y_start + height);
    LCD_DrawLine(x_start, y_start + height, x_start + width, y_start + height);
    
    POINT_COLOR = RED;
    u16 y_low = y_start + height - (u16)((u32)g_sys.light_low_threshold * height / 100);
    LCD_DrawLine(x_start, y_low, x_start + width, y_low);
    
    if (g_sys.history_count < 2) return;
    
    POINT_COLOR = CYAN;
    for (i = 0; i < g_sys.history_count - 1; i++)
    {
        x1 = x_start + (u16)((u32)i * width / HISTORY_SIZE);
        y1 = y_start + height - (u16)((u32)g_sys.light_history[i] * height / 100);
        x2 = x_start + (u16)((u32)(i + 1) * width / HISTORY_SIZE);
        y2 = y_start + height - (u16)((u32)g_sys.light_history[i + 1] * height / 100);
        
        LCD_DrawLine(x1, y1, x2, y2);
    }
}
