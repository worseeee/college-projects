% 1. 定义输入和目标向量
P = [0 0 1 1; 0 1 0 1]; 
T = [0 1 1 1];

% 2. 创建感知器
% newp 的参数：[输入的最小值 最大值], 神经元个数
net = newp([0 1; 0 1], 1);

% 3. 设置训练步数并训练
net.trainParam.epochs = 2; % 尝试较小的步数
net = train(net, P, T);
Y2 = sim(net, P);

% 4. 增加步数再次训练对比
net.trainParam.epochs = 20; 
net = train(net, P, T);
Y20 = sim(net, P);

% 5. 可视化
plotpv(P, T);
plotpc(net.iw{1,1}, net.b{1});