% --- chap3_2.m ---
clear all;
close all;

% --- 1. 定义论域 ---
x = 0:0.1:10; % 从 0 到 10，步长 0.1

% --- 2. 仿真 ---
M = 1; % 初始选择高斯型

if M == 1
    % 高斯型隶属函数
    % 公式: exp(-(x-c)² / (2*sigma²))
    c1 = 5; sigma1 = 2; % 中心和宽度
    y1 = gaussmf(x, [sigma1, c1]);
    
    c2 = 7; sigma2 = 1;
    y2 = gaussmf(x, [sigma2, c2]);
    
    figure;
    plot(x, y1, 'b-', x, y2, 'r--');
    title('高斯型隶属函数');
    legend('c=5, sigma=2', 'c=7, sigma=1');
    
elseif M == 2
    % 广义钟型隶属函数
    % 公式: 1 / (1 + |(x-c)/a|^2b)
    a1=2; b1=1; c1=5;
    y1 = gbellmf(x, [a1, b1, c1]);
    
    a2=2; b2=3; c2=5;
    y2 = gbellmf(x, [a2, b2, c2]);
    
    figure;
    plot(x, y1, 'b-', x, y2, 'r--');
    title('广义钟型隶属函数');
    legend('a=2, b=1, c=5', 'a=2, b=3, c=5');
    
elseif M == 3
    % S 型隶属函数
    % 公式: S(x; a, b)
    a1=1; b1=5;
    y1 = smf(x, [a1, b1]);
    
    a2=3; b2=7;
    y2 = smf(x, [a2, b2]);
    
    figure;
    plot(x, y1, 'b-', x, y2, 'r--');
    title('S 型隶属函数');
    legend('a=1, b=5', 'a=3, b=7');
    
elseif M == 4
    % 梯形隶属函数
    % 公式: trapmf(x, [a, b, c, d])
    y1 = trapmf(x, [1, 3, 7, 9]);
    y2 = trapmf(x, [2, 4, 6, 8]);
    
    figure;
    plot(x, y1, 'b-', x, y2, 'r--');
    title('梯形隶属函数');
    legend('params=[1,3,7,9]', 'params=[2,4,6,8]');
    
elseif M == 5
    % 三角形隶属函数
    % 公式: trimf(x, [a, b, c])
    y1 = trimf(x, [1, 5, 9]);
    y2 = trimf(x, [3, 5, 7]);
    
    figure;
    plot(x, y1, 'b-', x, y2, 'r--');
    title('三角形隶属函数');
    legend('params=[1,5,9]', 'params=[3,5,7]');
    
elseif M == 6
    % Z 型隶属函数
    % 公式: Z(x; a, b)
    a1=1; b1=5;
    y1 = zmf(x, [a1, b1]);
    
    a2=3; b2=7;
    y2 = zmf(x, [a2, b2]);
    
    figure;
    plot(x, y1, 'b-', x, y2, 'r--');
    title('Z 型隶属函数');
    legend('a=1, b=5', 'a=3, b=7');
end