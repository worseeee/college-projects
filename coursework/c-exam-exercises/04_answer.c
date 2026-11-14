#include <stdio.h>
int main()
{
   int a;
   do
      scanf("%d",&a);
   while(a<0);
   
   if(a<=120)
       printf("%d",90*a);
   else
       printf("%d",120*90+(a-120)*180);
}
