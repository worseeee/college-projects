% --- 3-2: 模糊矩阵运算 ---
clear all;

% --- 1. 定义矩阵 ---
P = [0.6 0.9; 0.2 0.7];
Q = [0.5 0.7; 0.1 0.4];
R = [0.2 0.3; 0.7 0.7];
S = [0.1 0.2; 0.6 0.5];

% --- 2. 自定义模糊矩阵乘法函数 ---
% MATLAB 没有内置模糊矩阵乘法，需要自己写
fuzzymult = @(A, B) max(min(A', repmat(B, [size(A, 2), 1])), [], 2)';
% 为了更清晰，我们写一个循环版本
function C = fuzzymult_loop(A, B)
    [m, n] = size(A);
    [p, q] = size(B);
    if n ~= p
        error('矩阵维度不匹配');
    end
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

% --- 3. 计算 ---

% (1) (P ∘ Q) ∘ R
PQ = fuzzymult_loop(P, Q);
Result1 = fuzzymult_loop(PQ, R);

% (2) (P ∪ Q) ∘ S
P_union_Q = max(P, Q);
Result2 = fuzzymult_loop(P_union_Q, S);

% (3) (P ∘ S) ∪ (Q ∘ S)
PS = fuzzymult_loop(P, S);
QS = fuzzymult_loop(Q, S);
Result3 = max(PS, QS);

% --- 4. 显示结果 ---
disp('(1) (P ∘ Q) ∘ R =');
disp(Result1);

disp('(2) (P ∪ Q) ∘ S =');
disp(Result2);

disp('(3) (P ∘ S) ∪ (Q ∘ S) =');
disp(Result3);
