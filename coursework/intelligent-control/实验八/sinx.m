%% 1. 数据准备
% 训练集 (根据实验要求自定义)
trainP = 0:0.05:1; 
trainT = sin(trainP);

% 测试集 (用于验证模型的泛化能力)
testP = [0.2, 0.4, 0.6, 0.8];
testT = sin(testP);

%% 2. 网络设计
% 设定隐层节点数，对于 sin 函数，5-10个节点足以
hiddenLayerSize = 5; 

% 创建 BP 神经网络
% minmax(trainP): 输入范围
% [hiddenLayerSize, 1]: 隐层 8 个神经元，输出层 1 个
% {'tansig', 'purelin'}: 隐层用 S 型函数，输出层用线性函数（回归常用组合）
% 'trainlm': 莱文贝格-马夸特算法，收敛速度最快
net = newff(minmax(trainP), [hiddenLayerSize, 1], {'tansig', 'purelin'}, 'trainlm');

%% 3. 训练参数设置
net.trainParam.epochs = 1000;      % 最大训练次数
net.trainParam.goal = 1e-6;        % 训练目标误差
net.trainParam.lr = 0.01;          % 学习率

%% 4. 训练网络
[net, tr] = train(net, trainP, trainT);

%% 5. 仿真测试
% 对训练集和测试集分别进行仿真
yTrain = sim(net, trainP);
yTest = sim(net, testP);

% 为了画出平滑的拟合曲线，生成更多的点进行验证
xRange = 0:0.01:1.1;
yRange = sim(net, xRange);

%% 6. 结果可视化
figure;
plot(xRange, sin(xRange), 'k-', 'LineWidth', 1.5); hold on; % 理论正弦曲线
plot(trainP, trainT, 'ro', 'MarkerSize', 8, 'LineWidth', 2); % 训练点
plot(testP, yTest, 'bx', 'MarkerSize', 10, 'LineWidth', 2);  % 测试预测点
plot(xRange, yRange, 'b--', 'LineWidth', 1);               % 网络预测全曲线

xlabel('Input x');
ylabel('Output y = sin(x)');
title('BP神经网络拟合 sin(x) 函数');
legend('理论曲线', '训练样本', '测试集预测点', '网络预测全曲线');
grid on;

% 输出测试集的误差分析
error = testT - yTest;
fprintf('测试集平均绝对误差 (MAE): %f\n', mean(abs(error)));