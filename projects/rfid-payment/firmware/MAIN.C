#include <reg52.h>
#include <intrins.h>
#include <string.h>
#include "mfrc522.h"
#include "lcd1602.h"

#define uchar unsigned char
#define uint unsigned int

sbit SPK   = P1^5;
sbit KEY_1 = P3^2; 
sbit KEY_2 = P3^3; 
sbit KEY_3 = P3^4; 
sbit KEY_4 = P3^5; 
sbit KEY_5 = P3^6; 
sbit KEY_6 = P3^7; 

uchar num_tens = 0; 
uchar num_units = 0; 
uchar code DefaultKey[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}; 
uchar idata RevBuffer[30];       
uchar idata MLastSelectedSnr[4]; 

void DelayMs_Main(uint ms);
void Beep_Success();
void Beep_Fail();
void Update_Display_Num();
uchar Key_Scan();
void RFID_Init_Write(uchar val); 
void RFID_Subtract_From_Card(uchar input_sub); 

void DelayMs_Main(uint ms) {
    uint i, j;
    for(i = 0; i < ms; i++) for(j = 0; j < 110; j++);
}
void Beep_Success() { SPK = 0; DelayMs_Main(100); SPK = 1; }
void Beep_Fail() {
    uchar i;
    for(i=0; i<3; i++) { SPK = 0; DelayMs_Main(50); SPK = 1; DelayMs_Main(50); }
}
void Update_Display_Num() {
    DisplayOneChar(11, 1, num_tens + '0');
    DisplayOneChar(12, 1, num_units + '0');
}

uchar Key_Scan() {
    if(KEY_1==0){ DelayMs_Main(50); if(KEY_1==0){ while(!KEY_1); return 1; } }
    if(KEY_2==0){ DelayMs_Main(50); if(KEY_2==0){ while(!KEY_2); return 2; } }
    if(KEY_3==0){ DelayMs_Main(50); if(KEY_3==0){ while(!KEY_3); return 3; } }
    if(KEY_4==0){ DelayMs_Main(50); if(KEY_4==0){ while(!KEY_4); return 4; } }
    if(KEY_5==0){ DelayMs_Main(50); if(KEY_5==0){ while(!KEY_5); return 5; } }
    if(KEY_6==0){ DelayMs_Main(50); if(KEY_6==0){ while(!KEY_6); return 6; } }
    return 0;
}

void RFID_Init_Write(uchar val) {
    uchar status;
    uchar write_data[16];
    uchar i;
    for(i=0; i<16; i++) write_data[i] = 0x00;
    write_data[1] = val / 10; 
    write_data[2] = val % 10; 

    status = PcdRequest(PICC_REQIDL, RevBuffer);
    if(status != MI_OK) status = PcdRequest(PICC_REQIDL, RevBuffer);
    if(status != MI_OK) { DisplayListChar(0, 1, "No Card!        "); Beep_Fail(); return; }
    if(PcdAnticoll(MLastSelectedSnr) != MI_OK) return;
    if(PcdSelect(MLastSelectedSnr) != MI_OK) return;

    if(PcdAuthState(PICC_AUTHENT1A, 1, DefaultKey, MLastSelectedSnr) == MI_OK) {
        if(PcdWrite(1, write_data) == MI_OK) {
            DisplayListChar(0, 1, "Init Write OK!  "); Beep_Success();
        }
    }
    PcdHalt();
}

void RFID_Subtract_From_Card(uchar input_sub) {
    uchar status;
    uchar card_data[16];
    int current_val; 
    int final_result;

    DisplayListChar(0, 1, "Reading Card... ");
    
    status = PcdRequest(PICC_REQIDL, RevBuffer);
    if(status != MI_OK) { DisplayListChar(0, 1, "No Card!        "); Beep_Fail(); return; }
    PcdAnticoll(MLastSelectedSnr);
    PcdSelect(MLastSelectedSnr);

    if(PcdAuthState(PICC_AUTHENT1A, 1, DefaultKey, MLastSelectedSnr) == MI_OK) {
        status = PcdRead(1, card_data);
        if(status == MI_OK) {
            current_val = (card_data[1] * 10) + card_data[2];
            
            final_result = current_val - input_sub;
            if(final_result < 0) final_result = 0;

            card_data[1] = (uchar)(final_result / 10);
            card_data[2] = (uchar)(final_result % 10);
            
            if(PcdWrite(1, card_data) == MI_OK) {
                DisplayListChar(0, 1, "Sub Success!    ");
                Beep_Success();
                DisplayOneChar(14, 1, (uchar)(final_result/10) + '0');
                DisplayOneChar(15, 1, (uchar)(final_result%10) + '0');
            }
        } else {
            DisplayListChar(0, 1, "Read Fail!      "); Beep_Fail();
        }
    } else {
        DisplayListChar(0, 1, "Auth Fail!      "); Beep_Fail();
    }
    PcdHalt();
}

void main() {
    uchar key_num;
    DelayMs_Main(100);
    LCDInit();      
    SPK = 1;        
    PcdReset();         
    PcdAntennaOn();     
    M500PcdConfigISOType('A'); 

    DisplayListChar(0, 0, "RFID Deduct Sys ");
    DisplayListChar(0, 1, "Input: 00  Res:--");
    Update_Display_Num();

    while(1) {
        key_num = Key_Scan();
        if(key_num != 0) {
            switch(key_num) {
                case 1: if(num_units < 9) num_units++; else num_units = 0; break;
                case 2: if(num_units > 0) num_units--; else num_units = 9; break;
                case 3: if(num_tens < 9) num_tens++; else num_tens = 0; break;
                case 4: if(num_tens > 0) num_tens--; else num_tens = 9; break;
                case 5: 
                    RFID_Subtract_From_Card(num_tens * 10 + num_units);
                    break;
                case 6: 
                    RFID_Init_Write(num_tens * 10 + num_units);
                    break;
            }
            Update_Display_Num();
        }
    }
}
