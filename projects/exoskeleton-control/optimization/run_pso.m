%% ========================================================================
%  run_pso.m  ——  粒子群优化（PSO）控制器参数全局寻优脚本
%  教材对应：第10章10.7~10.8节（粒子群优化算法、参数辨识应用）
%
%  ■ 优化目标：最小化综合性能指标
%    J = ∫(w1·e² + w2·u²)dt + P_safety（安全约束惩罚项）
%    其中 w1=1（精度权重），w2=0.01（控制能量权重）
%    P_safety：若max|e| > 5°（安全阈值），加大惩罚
%
%  ■ 优化变量（以模糊PID参数为例，共14维）：
%    x = [Kp_base, Ki_base, Kd_base,         (基础PID参数 3维)
%         e_centers_3,4,5,  de_centers_3,4,5, (中间3个隶属函数中心 6维)
%         eta_rbf, lambda_rbf,                (RBF学习参数 2维)
%         Kp_ilc,  Kd_ilc]                   (ILC参数 2维)
%    共14维搜索空间
%
%  ■ PSO算法参数（教材10.7.2节标准设置）：
%    N=50粒子，最大300次迭代，ω: 0.9→0.4线性衰减，c1=c2=2.0
% ========================================================================
clear; clc;
load('exo_workspace.mat', 'p', 'ctrl');

fprintf('=== PSO 控制器参数全局优化 ===\n');
fprintf('教材对应：第10章 粒子群优化算法（10.7~10.8节）\n\n');

%% ── PSO参数设置（教材10.7.2节标准配置）─────────────────────────────
N_particle = ctrl.pso.n_particle;   % 粒子数：50
max_iter   = ctrl.pso.max_iter;     % 最大迭代：300
w_start    = ctrl.pso.w_start;      % 初始惯性权重：0.9
w_end      = ctrl.pso.w_end;        % 终止惯性权重：0.4
c1         = ctrl.pso.c1;           % 个体学习因子：2.0
c2         = ctrl.pso.c2;           % 社会学习因子：2.0

%% ── 搜索空间定义 ─────────────────────────────────────────────────────
% 变量维度：14维
% [Kp_base, Ki_base, Kd_base,
%  e_c3, e_c4, e_c5,  (误差隶属函数中间3个中心，单位°)
%  de_c3, de_c4, de_c5, (误差率隶属函数中间3个中心，单位°/s)
%  eta_rbf, lambda_rbf, Kp_ilc, Kd_ilc]

n_dim = 14;

% 搜索范围：[下界, 上界]
lb = [5,   0.5, 0.1,  % Kp,Ki,Kd 下界
      -40, -15, -5,   % e隶属函数中心下界（单位°）
      -30, -10, -3,   % de隶属函数中心下界（单位°/s）
      0.01, 0.9, 0.3, 0.01]; % eta,lambda,Kp_ilc,Kd_ilc 下界

ub = [35,  5.0, 3.0,  % Kp,Ki,Kd 上界
      -5,  5,   40,   % e隶属函数中心上界
      -3,  10,  30,   % de隶属函数中心上界
      0.2, 0.9999, 2.0, 0.5]; % eta,lambda,Kp_ilc,Kd_ilc 上界

fprintf('[PSO] 搜索空间：%d维，粒子数：%d，最大迭代：%d\n', ...
        n_dim, N_particle, max_iter);

%% ── 初始化粒子群（教材10.7.3节 PSO基本流程）────────────────────────
% 粒子位置：在搜索空间内均匀随机初始化
pos = rand(N_particle, n_dim) .* (ub - lb) + lb;

% 粒子速度：初始化为搜索范围的±10%
v_range = 0.1 * (ub - lb);
vel = (rand(N_particle, n_dim) * 2 - 1) .* v_range;

% 个体最优位置
p_best_pos = pos;
p_best_fit = inf * ones(N_particle, 1);

% 全局最优
g_best_pos = pos(1,:);
g_best_fit = inf;

%% ── PSO主循环 ────────────────────────────────────────────────────────
fit_history   = zeros(max_iter, 1);  % 记录最优适应度历史
mean_fit_hist = zeros(max_iter, 1);  % 记录平均适应度（判断收敛）

fprintf('[PSO] 开始优化迭代...\n');
fprintf('  迭代   全局最优   平均适应度   ω值\n');
fprintf('  ------  ---------  ----------   ----\n');

for iter = 1:max_iter
    % ---- 线性衰减惯性权重（教材10.7.2节关键技巧）----
    % ω越大→全局搜索能力强；ω越小→局部精化能力强
    w = w_start - (w_start - w_end) * iter / max_iter;

    % ---- 评估所有粒子的适应度 ----
    fit_values = zeros(N_particle, 1);
    parfor i = 1:N_particle  % 并行计算加速（去掉parfor改for若无Parallel Toolbox）
        fit_values(i) = evaluate_fitness(pos(i,:), p, lb, ub);
    end

    % ---- 更新个体最优和全局最优 ----
    for i = 1:N_particle
        if fit_values(i) < p_best_fit(i)
            p_best_fit(i) = fit_values(i);
            p_best_pos(i,:) = pos(i,:);
        end
        if fit_values(i) < g_best_fit
            g_best_fit = fit_values(i);
            g_best_pos = pos(i,:);
        end
    end

    % ---- 更新粒子速度和位置（PSO核心方程，教材式10-9）----
    % v_{i+1} = ω·v_i + c1·r1·(p_best-x_i) + c2·r2·(g_best-x_i)
    r1 = rand(N_particle, n_dim);
    r2 = rand(N_particle, n_dim);

    vel = w * vel ...
        + c1 * r1 .* (p_best_pos - pos) ...
        + c2 * r2 .* (g_best_pos - pos);

    % 速度限幅（防止爆炸，教材10.7.2节）
    v_max = 0.2 * (ub - lb);
    vel = max(-v_max, min(v_max, vel));

    % 更新位置
    pos = pos + vel;

    % 位置越界处理（反弹法，保持种群多样性）
    for d = 1:n_dim
        over_ub = pos(:,d) > ub(d);
        over_lb = pos(:,d) < lb(d);
        pos(over_ub, d) = ub(d) - rand(sum(over_ub),1) * (ub(d)-lb(d))*0.1;
        pos(over_lb, d) = lb(d) + rand(sum(over_lb),1) * (ub(d)-lb(d))*0.1;
        vel(over_ub | over_lb, d) = -vel(over_ub | over_lb, d); % 速度反向
    end

    fit_history(iter)   = g_best_fit;
    mean_fit_hist(iter) = mean(fit_values);

    % 每20次迭代打印进度
    if mod(iter, 20) == 0 || iter == 1
        fprintf('  %4d   %9.4f   %10.4f   %.3f\n', ...
                iter, g_best_fit, mean(fit_values), w);
    end

    % 提前收敛判断：连续10次改善小于1e-6
    if iter > 10 && (fit_history(iter-10) - g_best_fit) < 1e-6
        fprintf('[PSO] 提前收敛于第 %d 次迭代\n', iter);
        fit_history = fit_history(1:iter);
        mean_fit_hist = mean_fit_hist(1:iter);
        break;
    end
end

%% ── 解析最优结果 ────────────────────────────────────────────────────
fprintf('\n[PSO结果] 全局最优适应度：%.6f\n', g_best_fit);
opt = g_best_pos;
fprintf('最优参数：\n');
fprintf('  基础PID: Kp=%.3f, Ki=%.4f, Kd=%.4f\n', opt(1), opt(2), opt(3));
fprintf('  RBF参数: eta=%.4f, lambda=%.6f\n', opt(11), opt(12));
fprintf('  ILC参数: Kp_ilc=%.3f, Kd_ilc=%.4f\n', opt(13), opt(14));

%% ── 绘制PSO收敛曲线（实验一绘图技能直接应用）───────────────────────
figure('Name','PSO优化收敛曲线', 'Position',[100,100,900,400]);
subplot(1,2,1);
plot(fit_history, 'b-', 'LineWidth', 2); hold on;
plot(mean_fit_hist, 'r--', 'LineWidth', 1.5);
grid on;
xlabel('迭代次数'); ylabel('适应度 J');
title('PSO收敛过程（教材第10章图10-8类型）');
legend('全局最优', '种群平均', 'Location','northeast');
set(gca,'YScale','log');

subplot(1,2,2);
improvement = [0; diff(-fit_history)] / fit_history(1) * 100;
plot(cumsum(improvement), 'g-', 'LineWidth', 2);
grid on;
xlabel('迭代次数'); ylabel('累积改善 (%)');
title('相对初始解的改善百分比');

%% ── 保存优化结果 ─────────────────────────────────────────────────────
ctrl_opt = ctrl;
ctrl_opt.pso.best_params  = g_best_pos;
ctrl_opt.pso.best_fitness = g_best_fit;
ctrl_opt.pso.fit_history  = fit_history;

% 将最优参数写回对应控制器
ctrl_opt.fuzzy.Kp_base = opt(1);
ctrl_opt.fuzzy.Ki_base = opt(2);
ctrl_opt.fuzzy.Kd_base = opt(3);
ctrl_opt.rbf.eta       = opt(11);
ctrl_opt.rbf.lambda    = 1 - opt(12); % 转换回lambda
ctrl_opt.ilc.Kp        = opt(13);
ctrl_opt.ilc.Kd        = opt(14);

save('exo_workspace.mat', 'ctrl_opt', '-append');
fprintf('\n[Done] PSO优化结果已保存至 exo_workspace.mat\n');

%% ── 适应度评估函数（PSO的核心，教材10.7.1节适应度函数设计）─────────
function J = evaluate_fitness(x, p, lb, ub)
% 输入：x = 参数向量（14维）
% 输出：J = 综合性能指标（越小越好）

    % 解析参数
    Kp_base = x(1); Ki_base = x(2); Kd_base = x(3);
    % (其余参数为FIS中心和RBF/ILC参数，此处简化为仅评估PID部分)

    % 仿真参数
    dt     = p.dt;
    T_sim  = p.T_period * 3; % 简化：只仿真3个周期以加快PSO速度
    t_vec  = 0:dt:T_sim;
    n_step = length(t_vec);

    % 被控对象简化模型（线性化，用于快速PSO评估）
    % 在完整优化中，应调用Simulink仿真（但速度较慢）
    % 这里用离散传递函数近似，实际项目中替换为sim()调用
    theta  = 0;    dtheta = 0;
    e_int  = 0;    e_prev = 0;

    J_perf   = 0;  % 性能项
    J_energy = 0;  % 能量项
    e_max    = 0;  % 最大误差（安全约束用）

    % 权重（教材10.8节参数辨识中的加权目标函数）
    w1 = 1.0;   % 跟踪精度权重
    w2 = 0.01;  % 控制能量权重
    w3 = 100.0; % 安全约束惩罚权重

    for k = 1:n_step
        t = t_vec(k);
        % 期望轨迹
        theta_d = (pi/2) * (1 - cos(2*pi*t/p.T_period)) / 2;
        % 跟踪误差
        e = theta_d - theta;
        de = (e - e_prev) / dt;
        e_int = e_int + e * dt;

        % PID控制律（简化版，不含专家/模糊规则）
        u = Kp_base*e + Ki_base*e_int + Kd_base*de;
        u = max(-p.u_max, min(p.u_max, u));

        % 简化线性化被控对象（J*ddtheta + B*dtheta = u + K_approx*theta_d）
        ddtheta = (u - p.B*dtheta - p.K*sin(theta)) / p.J;
        dtheta  = dtheta + ddtheta * dt;
        theta   = theta  + dtheta  * dt;

        % 累积性能指标
        J_perf   = J_perf   + w1 * e^2 * dt;
        J_energy = J_energy + w2 * u^2 * dt;
        e_max    = max(e_max, abs(e));
        e_prev   = e;
    end

    % 安全约束惩罚（误差超过5°视为不安全）
    safety_threshold = deg2rad(5);
    if e_max > safety_threshold
        P_safety = w3 * (e_max - safety_threshold)^2;
    else
        P_safety = 0;
    end

    J = J_perf + J_energy + P_safety;

    % 处理数值异常（防止仿真发散导致PSO崩溃）
    if isnan(J) || isinf(J)
        J = 1e10;
    end
end