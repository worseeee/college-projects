G0=tf(1,[1,3,3,1]); 
D=[0.1 0.3  0.5 1 2 3];
N=10;
figure, 	hold on
for i=1:length(D)
   s=tf('s');
   C=D(i)*s/((1/N)*s+1);
   G=feedback(D(i)*G0,1);
   step(G);   %阶跃响应 
   pause(1);
end
