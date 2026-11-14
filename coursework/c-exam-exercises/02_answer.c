#include <stdio.h>
int main()
{
   int score;
   do
      scanf("%d",&score);
   while(score>100 || score<0);
   
   if(score>=85)
       printf("A");
   else 
       if(score>=60) 
	       printf("B");  
       else 
	       printf("F");
}
