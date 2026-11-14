/*12-24小时制*/
#include <stdio.h>

int main()
{
	int hour, min;
	
	scanf("%d:%d", &hour, &min);
	
	if (hour < 12)
	{
		printf("%d:%d AM", hour, min);
	}
	else
	{
		hour = hour - 12;
		printf("%d:%d PM", hour, min);
	}
	
	return 0;
}