#include <stdio.h>
int main()
{
   int a,b,c;
   do
      scanf("%d%d%d",&a,&b,&c);
   while(a<=0 || b<=0 || c<=0);
   if(a==b) printf("C");
   else if(a==c) printf("B");  
   else printf("A");    
}