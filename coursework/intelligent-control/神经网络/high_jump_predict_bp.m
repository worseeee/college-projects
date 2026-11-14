%% 任务3：历届男子跳高成绩预测 BP神经网络
% HIGH_JUDM_PREDICT_BP 基于BP神经网络的历届男子跳高成绩预测
%   本脚本通过1-14届跳高成绩训练一维BP网络，实现第15届成绩的趋势预测。
%   包含曲线拟合、外推预测以及结果的可视化分析。
clear; clc; close all;

%% 1. 构造训练数据与测试数据 
% 训练集输入 P_train: 届数序号 1 到 14
P_train = 1:14; 

% 训练集目标 T_train: 前 14 届的历史成绩
T_train = [1.81, 1.90, 1.93, 1.97, 2.03, 2.08, 2.12, 2.16, 2.18, 2.22, 2.25, 2.28, 2.32, 2.35];

% 测试集输入 P_test: 预测第 15 届
P_test = 15; 

%% 2. 数据归一化 
% 将序号(1~15)和成绩统一映射到 [-1, 1] 之间，方便网络学习趋势
[P_train_norm, ps_input] = mapminmax(P_train, -1, 1);
[T_train_norm, ps_output] = mapminmax(T_train, -1, 1);

%% 3. 创建与配置 BP 神经网络
hiddenLayerSize = 5; 
net = feedforwardnet(hiddenLayerSize, 'trainlm');

% 激活函数配置
net.layers{1}.transferFcn = 'tansig';
net.layers{2}.transferFcn = 'tansig';

% 训练参数配置
net.trainParam.epochs = 1000;
net.trainParam.goal = 1e-6; 
net.trainParam.min_grad = 1e-7; 

%% 4. 训练网络
[net, tr] = train(net, P_train_norm, T_train_norm);

%% 5. 仿真与反归一化 
% 步骤 A: 把要预测的序号 "15" 用之前的规则进行归一化
P_test_norm = mapminmax('apply', P_test, ps_input);

% 步骤 B: 投入网络预测出归一化后的成绩
T_sim_norm = sim(net, P_test_norm);

% 步骤 C: 将网络吐出的数值反归一化，还原为真实的跳高成绩
T_sim = mapminmax('reverse', T_sim_norm, ps_output);

%% 6. 为了展示网络是否真正学到了规律，我们让它回测所有 1-14 的历史数据
T_history_fit_norm = sim(net, P_train_norm);
T_history_fit = mapminmax('reverse', T_history_fit_norm, ps_output);

%% 7. 结果展示与绘图分析
disp('------------------------------------------------');
disp(['预测的第 15 届男子跳高成绩为: ', num2str(T_sim), ' 米']);

% 绘制拟合与预测曲线图
figure;
hold on;
% 画出历史真实数据 (黑色圆圈)
plot(P_train, T_train, 'ko', 'MarkerSize', 8, 'LineWidth', 1.5);
% 画出神经网络拟合的历史曲线 (蓝色实线)
plot(P_train, T_history_fit, 'b-', 'LineWidth', 2);
% 画出第 15 届的预测点 (红色五角星)
plot(P_test, T_sim, 'rp', 'MarkerSize', 12, 'MarkerFaceColor', 'r');

grid on;
title('历届男子跳高成绩 BP 神经网络拟合与预测');
xlabel('届数序号');
ylabel('跳高成绩 (米)');
legend('历史真实成绩', '神经网络拟合曲线', '第15届预测成绩', 'Location', 'NorthWest');