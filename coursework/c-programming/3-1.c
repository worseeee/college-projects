/*三天打鱼两天晒网*/
#include <stdio.h>

int main()
{
	int N = 0;
	
	scanf("%d", &N);
	
	int n = N % 5;
	
	switch(n)
	{
		case 0:
			printf("Drying in day %d\n", N);
			break;
	
		case 4:
			printf("Drying in day %d\n", N);
			break;
			
		default:
			printf("Fishing in day %d\n", N);
			break;
	}
	
	return 0;
}


/*#include <stdio.h>
 
int main()
{
	int i;
	scanf("%d", &i);	
	if(i%5 <= 3 && i%5 != 0)
	     printf("Fishing in day %d", i);
	else 
	     printf("Drying in day %d", i);
	return 0;
}*/