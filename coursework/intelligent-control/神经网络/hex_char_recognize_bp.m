%% 任务1：十六进制字符识别 BP神经网络
% HEX_CHAR_RECOGNIZE_BP 基于BP神经网络的十六进制点阵字符识别
%   本脚本通过5x3点阵输入，利用BP网络实现0-F字符的二进制编码识别。
%   作者: 刘胜炜
%   日期: 2026-05-31
clear; clc; close all;

% 1. 构造输入矩阵 X (15 x 16)
char_0 = [1;1;1;1;1; 1;0;0;0;1; 1;1;1;1;1]; 
char_1 = [0;0;0;0;0; 1;1;1;1;1; 0;0;0;0;0]; 
char_2 = [1;0;0;1;1; 1;0;1;0;1; 1;1;0;0;1];
char_3 = [1;0;0;0;1; 1;0;1;0;1; 1;1;0;1;1];
char_4 = [1;1;1;0;0; 0;0;1;0;0; 1;1;1;1;1];
char_5 = [1;1;1;0;1; 1;0;1;0;1; 1;0;1;1;1];
char_6 = [1;1;1;1;1; 1;0;1;0;1; 1;0;1;1;1];
char_7 = [1;0;0;0;0; 1;0;0;0;0; 1;1;1;1;1];
char_8 = [1;1;1;1;1; 1;0;1;0;1; 1;1;1;1;1];
char_9 = [1;1;1;0;1; 1;0;1;0;1; 1;1;1;1;1];
char_A = [0;1;1;1;1; 1;0;0;1;0; 0;1;1;1;1];
char_B = [1;1;1;1;1; 1;0;1;0;1; 1;1;0;1;1];
char_C = [1;1;1;1;1; 1;0;0;0;1; 1;0;0;0;1];
char_D = [1;1;1;1;1; 1;0;0;0;1; 0;1;1;1;0];
char_E = [1;1;1;1;1; 1;0;1;0;1; 1;0;0;0;1];
char_F = [1;1;1;1;1; 1;0;1;0;0; 1;0;0;0;0];

X = [char_0, char_1, char_2, char_3, char_4, char_5, char_6, char_7, char_8, char_9, char_A, char_B, char_C, char_D, char_E, char_F];

% 2. 构造目标矩阵 T (4 x 16)
T = zeros(4, 16);
for i = 0:15
    T(:, i+1) = str2num(dec2bin(i, 4)')'; 
end

% 3. 创建 BP 神经网络
hiddenLayerSize = 10;
net = feedforwardnet(hiddenLayerSize, 'trainlm');
net.layers{1}.transferFcn = 'tansig';
net.layers{2}.transferFcn = 'logsig';

% ==================== 【终极大杀器】 ====================
% 1. 关闭 MATLAB 自动的输入输出归一化预处理，防止改变 0 和 1 的本质！
net.inputs{1}.processFcns = {};
net.outputs{2}.processFcns = {};

% 2. 关闭默认的随机样本划分，强迫网络记住这 16 个死规律！
net.divideFcn = ''; 
% ========================================================

% 配置训练参数
net.trainParam.epochs = 1000; % 最大训练步数
net.trainParam.goal = 1e-3;   % 训练目标误差
net.trainParam.min_grad = 1e-7; % 防止极小梯度早停

% 4. 训练网络
[net, tr] = train(net, X, T);

% 5. 仿真/测试网络
Y = sim(net, X);

% 6. 将输出转化为严格的 0 或 1 
Y_rounded = round(Y);

% 7. 评估并显示结果
disp('真实目标 T:');
disp(T);
disp('网络预测输出 Y_rounded:');
disp(Y_rounded);

% 计算准确率
isCorrect = isequal(T, Y_rounded);
if isCorrect
    disp('太棒了！16个字符全部识别正确！');
else
    disp('仍有错误，请检查。');
end