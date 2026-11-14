/*统计素数并求和*/
#include <stdio.h>

int main()
{
	int M, N;
	scanf("%d %d", &M, &N);
	
//	int num = M, sum = 0, count = 0;
//	while (M <= num && num <= N)
//	{
//		int cnt = 0;
//		int i = 2;
//		while (i < num)
//		{
//			if (num % i == 0)
//			{
//				i ++;
//			}
//			else
//			{
//				cnt += 1;
//				i ++;
//			} 
//		}
//		
//		if (cnt == num - 2)
//		{
//			count += 1;
//			sum += num;
//		}
//		
//		num ++;
//	}
	
	int i, j;
	int cnt = 0, sum = 0;
	
	if (M == 1)
	{
		M == 2;
	}
	for (i = M; i <= N; i ++)
	{
		int isPrime = 1;
		for (j = 2; j < i; j ++)
		{
			if (i % j == 0)
			{
				isPrime = 0;
				break;
			}
		}
		if (isPrime)
		{
			cnt ++;
			sum += i;
		}
	}
	
	printf("%d %d", cnt, sum);
	
	return 0;
}