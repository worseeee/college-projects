#ifndef __MONITOR_H
#define __MONITOR_H

#include "sys.h"
#include "stm32f4xx.h"

#define MODE_MONITOR    0   
#define MODE_SETTING    1   
#define MODE_HISTORY    2  
#define MODE_COUNT      3   

#define LEVEL_NORMAL    0   
#define LEVEL_WARNING   1   
#define LEVEL_ALARM     2  
#define LEVEL_CRITICAL  3  

#define DEFAULT_TEMP_HIGH   40.0f   
#define DEFAULT_TEMP_LOW    15.0f   
#define DEFAULT_LIGHT_LOW   20     
#define DEFAULT_LIGHT_HIGH  95      

#define HISTORY_SIZE    60  
#define GRAPH_X_START   40  
#define GRAPH_Y_START   50  
#define GRAPH_WIDTH     380 
#define GRAPH_HEIGHT    100 

#define SAMPLE_INTERVAL_MS  500     
#define WARNING_MARGIN      0.10f   

#define LED0    PFout(9)
#define LED1    PFout(10)
#define Beep    PFout(8)
#define KEY_0   PEin(4)
#define KEY_1   PEin(3)
#define KEY_2   PEin(2)
#define WK_UP   PAin(0)

typedef struct {
    float   temperature;        
    u16     light_percent;      
    u16     light_raw;          
    
    float   temp_high_threshold;    
    float   temp_low_threshold;     
    u16     light_low_threshold;    
    u16     light_high_threshold;   
    
    u8      work_mode;          
    u8      alarm_level;        
    u8      alarm_muted;        
    u8      setting_target;     
    
    float   temp_history[HISTORY_SIZE];     
    u16     light_history[HISTORY_SIZE];    
    u8      history_index;      
    u8      history_count;      
    
    u8      sample_flag;        
    u8      display_refresh;    
    u32     sample_count;       
    
    float   dac_voltage;        
    float   adc_readback;       
} SystemState_t;

extern SystemState_t g_sys;
extern volatile u8 KEY0_flag, KEY1_flag, KEY2_flag, WKUP_flag;

void System_Init(void);
void Sensor_ADC_Init(void);
void DAC_Threshold_Init(void);
void Timer_Init(void);
void EXTI_KEY_Init(void);
void LED_BEEP_Init(void);

float Get_Temperature(void);
u16 Get_Light_Percent(void);
u16 Get_ADC_Value(ADC_TypeDef *ADCx, u8 channel);

void Set_DAC_Voltage(float voltage);
float Get_DAC_Readback(void);

u8 Check_Alarm_Level(void);
void Alarm_Control(u8 level);
void Alarm_Mute(void);

void LCD_Show_Monitor_Full(void);
void LCD_Show_Monitor_Update(void);
void LCD_Show_Setting(void);
void LCD_Show_History(void);
void LCD_Show_StatusBar(void);
void LCD_Draw_TempGraph(void);
void LCD_Draw_LightGraph(void);
void LCD_Draw_ProgressBar(u16 x, u16 y, u16 w, u16 h, u16 val, u16 max, u16 color);

void System_SelfTest(void);
void Process_Keys(void);
void Update_History(void);

#endif
