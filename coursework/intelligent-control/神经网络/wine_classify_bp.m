%% 任务4：自选应用实例 - 基于BP神经网络的 UCI 葡萄酒品种分类
% WINE_CLASSIFY_BP 基于BP模式识别网络的UCI葡萄酒品种分类
%   本脚本加载经典Wine数据集（13维特征，3分类），利用patternnet进行训练，
%   采用早停机制防止过拟合，并通过混淆矩阵评估测试集分类准确率。
clear; clc; close all;

%% 1. 加载数据集 (MATLAB自带经典数据集)
% X 为 13 x 178 的输入矩阵 (13个化学特征，178个样本)
% T 为 3 x 178 的目标矩阵 (3种葡萄酒类别，采用独热编码 One-Hot)
[X, T] = wine_dataset;

%% 2. 构建模式识别神经网络
hiddenLayerSize = 10; 
net = patternnet(hiddenLayerSize);

%% 3. 数据集随机划分
net.divideFcn = 'dividerand';
net.divideParam.trainRatio = 0.70;
net.divideParam.valRatio   = 0.15;
net.divideParam.testRatio  = 0.15;

%% 4. 配置训练参数
net.trainParam.epochs = 1000;      % 最大训练步数
net.trainParam.max_fail = 6;       % 验证集误差连续6次不降则早停(防止过拟合)
net.trainParam.showWindow = true;  % 显示训练面板

%% 5. 训练网络
[net, tr] = train(net, X, T);

%% 6. 仿真与测试集提取
% 提取网络对所有数据的预测概率输出 Y
Y = sim(net, X);

% 仅提取刚才划分出去的那 15% 的测试集数据进行客观评估
test_indices = tr.testInd;
T_test = T(:, test_indices); % 测试集真实标签
Y_test = Y(:, test_indices); % 测试集网络预测输出

%% 7. 性能评估与可视化
% 将概率转为确定的类别编号
[~, T_test_class] = max(T_test);
[~, Y_test_class] = max(Y_test);

% 计算测试集准确率
accuracy = sum(T_test_class == Y_test_class) / length(T_test_class) * 100;
disp('------------------------------------------------');
disp(['葡萄酒分类测试集准确率: ', num2str(accuracy), '%']);
disp('------------------------------------------------');

% 绘制测试集混淆矩阵 (非常适合放在实验报告中的高级图表)
figure;
plotconfusion(T_test, Y_test, '葡萄酒测试集分类混淆矩阵');