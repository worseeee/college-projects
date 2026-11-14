p = -1:0.1:1;
t = [-0.9602,-0.5770,-0.0729,0.3771,0.6405,0.6600,0.4609,0.1336,-0.2013,-0.4344,-0.5000,-0.3930,-0.1647,0.0988,0.3072,0.3960,0.3449,0.1816,-0.312,-0.2189,-0.3201];

% 设计网络：1个输入，5个隐层神经元(tansig)，1个输出神经元(purelin)
% 'trainlm' 是 Levenberg-Marquardt 算法，BP 中收敛最快的算法之一
net = newff(minmax(p), [5, 1], {'tansig', 'purelin'}, 'trainlm');

net.trainParam.epochs = 500;
net.trainParam.goal = 1e-5;
net = train(net, p, t);
y = sim(net, p);

plot(p, t, 'ro', p, y, 'b-');
legend('原始数据', 'BP逼近曲线');