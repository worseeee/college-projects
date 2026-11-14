/*猜数字游戏*/
#include <stdio.h>

int main()
{
	int ram, N;
	scanf("%d %d", &ram, &N);
	
//	int i = 0, cnt = 0;
//	while (i < N)
//	{
//		int num;
//		scanf("%d", &num);
//		
//		if (num > ram)
//		{
//			cnt += 1;
//			printf("Too big\n");
//		}
//		
//		else if (num < ram)
//		{
//			cnt += 1;
//			printf("Too small\n");
//		}
//		
//		else if (num == ram)
//		{
//			cnt += 1;
//			if (cnt == 1)
//			{
//				printf("Bingo!\n");
//			}
//			
//			else if (cnt <= 3)
//			{
//				printf("Lucky You!\n");
//			}
//			
//			else if (cnt <= N)
//			{
//				printf("Good Guess!\n");
//			}
//			
//			else
//			{
//				printf("Game Over\n");
//			}
//		}
//		
//		else
//		{
//			printf("Game Over\n");
//		}
//		
//	}
	int cnt = 0;
	int finished = 0;
	do
	{
		int num;
		scanf("%d", &num);
		cnt ++;
		
		if (num < 0)
		{
			finished = 1;
		}
		else if (num > ram)
		{
			printf("Too big\n");
		}
		else if (num < ram)
		{
			printf("Too small\n");
		}
		else
		{
			if (cnt == 1)
			{
				printf("Bingo!\n");
				finished = 1;
			}
			else if (cnt <= 3)
			{
				printf("Lucky You!\n");
				finished = 1;
			}
			else
			{
				printf("Good Guess!\n");
				finished = 1;
			}
		}
	} while (!finished);
	
	printf("Game Over\n");
	
	return 0;
}