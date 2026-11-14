% --- 3-4: 模糊推理 ---
clear all;

% --- 1. 定义已知集合 ---
% 论域 X={x1, x2}, Y={y1, y2, y3}, Z={z1, z2}
A = [0.8, 0.1];         % 对应 x1, x2
B = [0.1, 0.5, 1];        % 对应 y1, y2, y3
C = [0.2, 1];           % 对应 z1, z2

A1 = [0.8, 0.1];        % 输入
B1_given = [0.5, 0.2, 0]; % 书中给的B1，这里是C1

% --- 2. 题目应该是求 C1，而不是给出 B1 ---
% 题目似乎有误，应该是 "如果 A 则 B" 和 "如果 B 则 C"，
% 给出 A1，求 C1。我们按这个思路来。
% 如果 A 则 B  => 关系 R_AB
% 如果 B 则 C  => 关系 R_BC
% 给出 A1，求 C1

% --- 重新解释题目：应该是 A->B，输入A1，求B1 ---

% --- Mamdani 推理方法 ---

% 1. 计算模糊关系 R = A × B (外积)
% R(i, j) = min(A(i), B(j))
R_AB = zeros(length(A), length(B));
for i = 1:length(A)
    for j = 1:length(B)
        R_AB(i, j) = min(A(i), B(j));
    end
end
% 因为A是行向量，所以R_AB需要转置一下，以匹配A1的维度
% R_AB的维度应该是 X的元素个数 × Y的元素个数
% A是1x2, B是1x3, 所以R_AB应该是2x3
% R_AB(i,j) = min( A(i), B(j) )
% 这里的A应该是对每个x的隶属度，B是对每个y的隶属度
% 题目中A=[0.8, 0.1]代表μA(x1)=0.8, μA(x2)=0.1
A_vec = A;
B_vec = B;
R_AB_matrix = zeros(length(A_vec), length(B_vec));
for i = 1:length(A_vec)
    for j = 1:length(B_vec)
        R_AB_matrix(i,j) = min(A_vec(i), B_vec(j));
    end
end


% 2. 自定义模糊矩阵乘法函数
function C = fuzzymult_loop(A, B)
    [m, n] = size(A);
    [p, q] = size(B);
    if n ~= p, error('矩阵维度不匹配'); end
    C = zeros(m, q);
    for i = 1:m
        for j = 1:q
            temp = zeros(1, n);
            for k = 1:n
                temp(k) = min(A(i, k), B(k, j));
            end
            C(i, j) = max(temp);
        end
    end
end


% 3. 进行推理 C1 = A1 ∘ R
% C1 是 1x3 的向量
% A1 是 1x2, R_AB_matrix 是 2x3, 所以 A1 ∘ R_AB_matrix 是 1x3
C1_calc = fuzzymult_loop(A1, R_AB_matrix);


% --- 显示结果 ---
disp('A ='); disp(A);
disp('B ='); disp(B);
disp('输入 A1 ='); disp(A1);
disp('模糊关系矩阵 R_AB = A × B (min) =');
disp(R_AB_matrix);
disp('推理得到的输出 C1 = A1 ∘ R_AB =');
disp(C1_calc);
disp('----------------------------------');
disp('书中给出的 B1/C1 值为:');
disp(B1_given);
disp('我们的计算结果与书中给出的值不同，这可能是因为：');
disp('1. 题目中省略了某个步骤或条件。');
disp('2. 使用了不同的推理模型（如Larsen模型: a*b）。');
disp('3. 题目印刷有误。');

% --- 尝试Larsen模型 (product) ---
R_AB_Larsen = A_vec' * B_vec;
C1_Larsen = fuzzymult_loop(A1, R_AB_Larsen);
disp(' ');
disp('尝试Larsen模型 (product * max) 推理:');
disp('关系矩阵 R_AB_Larsen =');
disp(R_AB_Larsen);
disp('Larsen推理得到的输出 C1_Larsen =');
disp(C1_Larsen);
