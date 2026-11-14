/*念数字*/
#include <stdio.h>

int main()
{
	int N, num;
	scanf("%d", &N);
	
	if (N < 0)
	{
		num = -N;
		printf("fu ");
	}
	
	else
	{
		num = N;
	}
	
	int m = 1, cnt = 1;
	int t = num;
	do
	{
		m *= 10;
		cnt ++;
		t /= 10;
	}while (t > 9);
	
	int count = 0;
	do
	{
		int n = num / m;
		num %= m;
		m /= 10;
		switch (n)
		{
			case 0:
				printf("ling");
				count ++;
				break;
			case 1:
				printf("yi");
				count ++;
				break;
			case 2:
				printf("er");
				count ++;
				break;
			case 3:
				printf("san");
				count ++;
				break;
			case 4:
				printf("si");
				count ++;
				break;
			case 5:
				printf("wu");
				count ++;
				break;
			case 6:
				printf("liu");
				count ++;
				break;
			case 7:
				printf("qi");
				count ++;
				break;
			case 8:
				printf("ba");
				count ++;
				break;
			case 9:
				printf("jiu");
				count ++;
				break;
		}
		
		if (count % cnt == 0)
		{
			printf("\n");
		}
		
		else
		{
			printf(" ");
		}	
	} while(m > 0);
	
	return 0;
}