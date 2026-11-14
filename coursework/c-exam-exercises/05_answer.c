#include <stdio.h>
int main()
{
   float a;
   do
      scanf("%f",&a);
   while(a<0);
   
   if(a<=50) printf("%.2f",a);
   else if(a<=150) printf("%.2f",a*0.9);  
   else printf("%.2f",a*0.8);    
}
