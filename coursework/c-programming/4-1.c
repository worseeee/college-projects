/*水仙花数*/
#include <stdio.h>

int main()
{
	int N;
	
	scanf("%d", &N);
	
	int i = 1;
	int min = 1, max = 1;
	
	while (i < N)
	{
		min = 10 * min;
		i ++;
	}
	
	max = 10 * min;
	
	int num = min;
	
	while (min <= num && num < max)
	{
		int sum = 0;
		int temp = num;
		
		do
		{
			int j = 0;
			int pow = 1;
			int a = temp % 10;
			
			while (j < N)
			{
				pow *= a;
				j ++;
			}
			
			sum += pow;
			temp /= 10;
		}while (temp != 0);
	
		if (sum == num)
		{
			printf("%d\n", num);
		}
		
		num ++;
	}
	
	return 0;
}