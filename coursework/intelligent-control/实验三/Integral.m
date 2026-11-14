G0=tf(1,[1,3,3,1]); 
I=[0.1 0.3 0.5 0.7];
figure, 	hold on
for i=1:length(I)
   C=tf(I(i),[1 0]);
   G=feedback(C*G0,1);
   step(G);   %阶跃响应 
   pause(1);
end
