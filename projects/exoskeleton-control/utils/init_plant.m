%% ========================================================================
%  init_plant.m  ——  膝关节外骨骼系统参数初始化脚本
%  项目：银龄护航 · 下肢外骨骼多层次混合智能控制系统
%  教材对应：《智能控制》刘金琨第4版 · 第1章(被控对象建模思想)
%  实验对应：实验一(MATLAB基础)、实验二(Simulink建模)
% ========================================================================
clear all; close all; clc;
fprintf('=== 银龄护航外骨骼控制系统 · 参数初始化 ===\n\n');

%% ── 1. 膝关节动力学模型参数 ──────────────────────────────────────────
% 对应教材2.3节：被控对象的数学模型建立是控制器设计的前提
p.J  = 0.5;    % [kg·m²] 等效转动惯量（含大腿段）
p.B  = 0.8;    % [N·m·s/rad] 关节粘性阻尼系数
p.K  = 15.0;   % [N·m] 重力矩系数（K·sin(θ) 为重力矩）
p.g  = 9.81;   % [m/s²] 重力加速度

% Stribeck 摩擦模型参数（非线性摩擦，是系统不确定性主要来源之一）
p.Fc = 1.2;    % [N·m] Coulomb摩擦力矩幅值
p.Fv = 0.3;    % [N·m·s/rad] 粘性摩擦系数
p.Fs = 2.0;    % [N·m] 静摩擦力矩（Stribeck峰值）
p.vs = 0.05;   % [rad/s] Stribeck速度阈值

% 控制量约束（安全限幅，康复场景核心安全指标）
p.u_max =  25.0;   % [N·m] 最大驱动力矩（正方向：屈膝助力）
p.u_min = -25.0;   % [N·m] 最小驱动力矩

fprintf('[Plant] 关节动力学参数：J=%.2f, B=%.2f, K=%.2f\n', p.J, p.B, p.K);

%% ── 2. 时变不确定性参数 ──────────────────────────────────────────────
% 教材第5章(自适应模糊控制)强调：时变参数是驱动自适应控制需求的根本原因

% 2.1 肌肉疲劳模型：患者主动力矩随时间指数衰减
p.tau_patient_max = 5.0;   % [N·m] 初始患者主动力矩幅值
p.fatigue_tau     = 60.0;  % [s]   疲劳时间常数（训练60s后衰减到37%）
% τ_patient(t) = tau_patient_max · exp(-t/fatigue_tau) · sin(ω·t)

% 2.2 参数摄动：惯量J在±30%范围缓慢时变（模拟不同体型患者）
p.J_perturb_amp   = 0.30;  % 摄动幅值比例 (±30%)
p.J_perturb_freq  = 0.02;  % [Hz] 慢变频率

% 2.3 痉挛脉冲：随机时刻注入短暂高幅值扰动
p.spasm_amp       = 8.0;   % [N·m] 痉挛力矩幅值
p.spasm_duration  = 0.3;   % [s]   痉挛持续时间
p.spasm_interval  = 15.0;  % [s]   平均痉挛间隔（泊松过程）

% 2.4 传感器噪声（编码器精度限制）
p.noise_angle     = 0.001; % [rad] 角度测量噪声标准差（≈0.06°）
p.noise_velocity  = 0.005; % [rad/s] 角速度噪声标准差

fprintf('[Disturbance] 不确定性模型：疲劳τ=%.0fs, 痉挛幅值=%.1f N·m\n', ...
        p.fatigue_tau, p.spasm_amp);

%% ── 3. 期望轨迹生成：Minimum Jerk轨迹 ───────────────────────────────
% Minimum Jerk轨迹最小化关节加加速度，符合人体自然运动特性
% 参考：Flash & Hogan (1985) 人类运动最优轨迹理论

p.T_period  = 4.0;   % [s] 单周期时长（0°→90°→0°）
p.theta_max = pi/2;  % [rad] 最大关节角度（90°）
p.theta_min = 0.0;   % [rad] 最小关节角度（0°）
p.sim_time  = 80.0;  % [s] 总仿真时间（含多个康复周期）
p.dt        = 0.001; % [s] 仿真步长（1ms，满足控制实时性要求）

% 生成期望轨迹（供compare_results.m使用的参考序列）
t_vec = 0 : p.dt : p.sim_time;
p.traj.t     = t_vec;
p.traj.theta_d = zeros(size(t_vec));
p.traj.dtheta_d = zeros(size(t_vec));
p.traj.ddtheta_d = zeros(size(t_vec));

for k = 1:length(t_vec)
    [th, dth, ddth] = min_jerk_traj(t_vec(k), p.T_period, ...
                                     p.theta_min, p.theta_max);
    p.traj.theta_d(k)   = th;
    p.traj.dtheta_d(k)  = dth;
    p.traj.ddtheta_d(k) = ddth;
end

fprintf('[Trajectory] Minimum Jerk轨迹生成完毕，仿真时长=%.0fs\n', p.sim_time);

%% ── 4. 控制器参数 ────────────────────────────────────────────────────
% ---- 第一层：基准PID ----（实验三 PID控制参数）
ctrl.pid.Kp = 18.0;
ctrl.pid.Ki =  2.5;
ctrl.pid.Kd =  0.8;
ctrl.pid.umax = p.u_max;

% ---- 第二层：专家PID ----（教材第2章 专家PID，实验四）
ctrl.expert.M1     = deg2rad(8);   % [rad] 大误差阈值（8°）
ctrl.expert.M2     = deg2rad(3);   % [rad] 中误差阈值（3°）
ctrl.expert.eps    = deg2rad(0.5); % [rad] 精细区阈值（0.5°）
ctrl.expert.k1     = 1.5;          % 强化增益系数
ctrl.expert.k2     = 0.6;          % 抑制系数
ctrl.expert.umax   = p.u_max;
% 继承PID基础参数（专家PID在PID基础上添加规则逻辑）
ctrl.expert.Kp = ctrl.pid.Kp;
ctrl.expert.Ki = ctrl.pid.Ki;
ctrl.expert.Kd = ctrl.pid.Kd;

% ---- 第三层：模糊PID ----（教材第3-4章 模糊控制）
ctrl.fuzzy.fis_file = 'knee_fuzzy_pid.fis';  % FIS文件名
ctrl.fuzzy.Kp_base = 15.0;  % 基础PID参数（模糊控制器输出增量）
ctrl.fuzzy.Ki_base =  2.0;
ctrl.fuzzy.Kd_base =  0.5;
ctrl.fuzzy.umax = p.u_max;

% ---- 第四层：RBF神经网络 ----（教材第7、9章）
ctrl.rbf.n_input  = 3;   % 输入维度：[θ_d, θ, ė]
ctrl.rbf.n_hidden = 11;  % 隐层节点数
ctrl.rbf.n_output = 1;   % 输出：不确定性估计
ctrl.rbf.eta      = 0.05; % 学习率
ctrl.rbf.lambda   = 0.99; % 遗忘因子（防止权值漂移）
ctrl.rbf.umax     = p.u_max;

% ---- 第五层：PSO参数 ----（教材第10章）
ctrl.pso.n_particle = 50;    % 粒子数量
ctrl.pso.max_iter   = 300;   % 最大迭代次数
ctrl.pso.w_start    = 0.9;   % 初始惯性权重
ctrl.pso.w_end      = 0.4;   % 终止惯性权重
ctrl.pso.c1         = 2.0;   % 个体学习因子
ctrl.pso.c2         = 2.0;   % 社会学习因子

% ---- 第六层：ILC参数 ----（教材第11章）
ctrl.ilc.Kp    = 0.8;   % ILC比例增益
ctrl.ilc.Kd    = 0.05;  % ILC微分增益
ctrl.ilc.gamma = 0.95;  % 跨周期衰减系数（渐进康复策略）
ctrl.ilc.n_iter = 20;   % 迭代周期数

fprintf('[Controllers] 六层控制器参数初始化完毕\n');

%% ── 5. 评估指标初始化 ────────────────────────────────────────────────
metrics.layer_names = {'L1-PID', 'L2-ExpertPID', 'L3-FuzzyPID', ...
                       'L4-RBF', 'L5-PSO-Optimized', 'L6-ILC'};
metrics.scenarios   = {'正常工况', '肌肉疲劳', '痉挛脉冲'};
metrics.RMSE        = zeros(6, 3);
metrics.PeakError   = zeros(6, 3);
metrics.Overshoot   = zeros(6, 3);
metrics.SettleTime  = zeros(6, 3);
metrics.Energy      = zeros(6, 3);
metrics.Robust      = zeros(6, 1);

%% ── 6. 保存工作区变量 ────────────────────────────────────────────────
save('exo_workspace.mat', 'p', 'ctrl', 'metrics');
fprintf('\n[Done] 所有参数已保存至 exo_workspace.mat\n');
fprintf('下一步：运行 design_fis.m 生成模糊控制器FIS文件\n');

%% ── 局部函数：Minimum Jerk轨迹生成 ──────────────────────────────────
function [theta, dtheta, ddtheta] = min_jerk_traj(t, T, th_min, th_max)
% Minimum Jerk 轨迹（Flash & Hogan 1985）
% 在半周期内从 th_min 平滑运动至 th_max，然后返回
% 数学形式：θ(τ) = θ_0 + Δθ·(10τ³ - 15τ⁴ + 6τ⁵)，τ=t/T_half ∈[0,1]

    T_half = T / 2;           % 半周期
    delta  = th_max - th_min; % 运动幅度
    t_mod  = mod(t, T);       % 当前周期内时刻

    if t_mod <= T_half
        % 上行段：th_min → th_max
        tau = t_mod / T_half;
        th0 = th_min; dth = delta;
        dir = 1;
    else
        % 下行段：th_max → th_min
        tau = (t_mod - T_half) / T_half;
        th0 = th_max; dth = -delta;
        dir = -1;
    end

    % Minimum Jerk 多项式及其导数
    f    =   10*tau^3 - 15*tau^4 +  6*tau^5;
    df   =  (30*tau^2 - 60*tau^3 + 30*tau^4) / T_half;
    ddf  = (60*tau    - 180*tau^2 + 120*tau^3) / T_half^2;

    theta    = th0 + dth * f;
    dtheta   = dth * df;
    ddtheta  = dth * ddf;
end