#include <reg51.h>
#include <intrins.h>

#define uchar unsigned char
#define uint unsigned int

#define FOSC 11059200L
#define BAUD 1200
#define T1H (256 - (FOSC/12/32/BAUD))
#define T1L (256 - (FOSC/12/32/BAUD))

uchar num = 0;
uchar received = 0;
uchar code LED[4] = {0xff, 0xfe, 0xfd, 0xfc};

void delay(uint t) {
    uint i, j;
    for(i = 0; i < t; i++)
        for(j = 0; j < 120; j++);
}

void UART_Init() {
    TMOD = 0x20;
    TH1 = T1H;
    TL1 = T1L;
    TR1 = 1;
    SCON = 0x50;
    ES = 1;
    EA = 1;
}

void UART_Send(uchar dat) {
    SBUF = dat;
    while(!TI);
    TI = 0;
}

void main() {
    UART_Init();
    while(1) {
        UART_Send(num);
			  P0 = LED[num];
        num = (num + 1) % 4;
        delay(1000);
    }
}

void UART_ISR() interrupt 4 {
    if(RI) { 
        RI = 0;
        received = SBUF;
    }
}
