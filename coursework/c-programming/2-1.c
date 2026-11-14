/*厘米换算英尺英寸*/
#include <stdio.h>

int main()
{
	int length = 0;
	
	scanf("%d", &length);
	
	int foot = length / 30.48;
	int inch = (length / 30.48 - foot) * 12;
	
	printf("%d %d\n", foot, inch);
	
	return 0;
}