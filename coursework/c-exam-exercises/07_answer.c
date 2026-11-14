#include <stdio.h>
int main()
{
   int x; float y;
   do
      scanf("%d",&x);
   while(x<0);
   
   if(x<=50) y=0.53*x;
   else y=0.53*50+(x-50)*(0.53+0.05);  
   printf("%.2f",y);    
}
