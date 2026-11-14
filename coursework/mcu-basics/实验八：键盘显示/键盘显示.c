#include <reg51.h>
#include <intrins.h>

unsigned char code dis_tab[17] = {0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f, 0x77, 0x7c, 0x39, 0x5e, 0x79, 0x71, 0};
unsigned char LED[8] = {0, 0, 16, 0, 0, 1, 1, 9};
unsigned char i, bit_data;

void mDelay(unsigned int delay)
{
	unsigned int i;
	for(; delay > 0; delay --)
	{
		for(i = 0; i < 114; i ++)
		{
			;
		}
	}
}

void display_imp()
{
	bit_data = 0xfe;
	for(i = 0; i < 8; i ++)
	{
		P2 = 0xff;
		P1 = dis_tab[LED[i]];
		P2 = bit_data;
		mDelay(5);
		bit_data = _crol_(bit_data , 1);
	}
}

unsigned char Matrix_key(void)
{
	unsigned char key, temp1, temp2;
	key = 0xff;
	P3 = 0x0f;
	if((P3 & 0x0f) != 0x0f)
	{
		mDelay(5);
		P3 = 0x0f;
		temp1 = P3 & 0x0f;
		if(temp1 != 0x0f)
		{
			P3 = 0xf0;
			temp2 = P3 & 0xf0;
			switch(temp1 | temp2)
      {
        case 0xee : key = 0; break;	
        case 0xde : key = 1; break;		
        case 0xbe : key = 2; break;		
        case 0x7e : key = 3; break;                      
        case 0xed : key = 4; break;
        case 0xdd : key = 5; break;
        case 0xbd : key = 6; break;
        case 0x7d : key = 7; break;
        case 0xeb : key = 8; break;
        case 0xdb : key = 9; break;
        case 0xbb : key = 10; break;
        case 0x7b : key = 11; break;
        case 0xe7 : key = 12; break;
        case 0xd7 : key = 13; break;
        case 0xb7 : key = 14; break;
        case 0x77 : key = 15; break;
        default: key = 0xff; break;
      }
    }
  }
  return(key);
}

void main(void)
{
	unsigned char key_value;
	while(1)
	{
		key_value = Matrix_key();
		switch(key_value)
		{
			case 0: LED[0] = 0; break;
			case 1: LED[0] = 1; break;
			case 2: LED[0] = 2; break;
			case 3: LED[0] = 3; break;
			case 4: LED[0] = 4; break;
			case 5: LED[0] = 5; break;
			case 6: LED[0] = 6; break;
			case 7: LED[0] = 7; break;
			case 8: LED[0] = 8; break;
			case 9: LED[0] = 9; break;
			case 10: LED[0] = 0; LED[1] = 1; break;
			case 11: LED[0] = 1; LED[1] = 1; break;
			case 12: LED[0] = 2; LED[1] = 1; break;
			case 13: LED[0] = 3; LED[1] = 1; break;
			case 14: LED[0] = 4; LED[1] = 1; break;
			case 15: LED[0] = 5; LED[1] = 1; break;
			default: break;
		}
		display_imp();
	}
}
