%% ========================================================================
%  knee_joint_sfunc.m  ——  膝关节动力学 S-Function（Level-2）
%  教材对应：第1章（被控对象建模）+ 第5章（不确定性建模思想）
%  实验对应：实验二（Simulink S-Function建模）
%
%  输入端口（u）: u(1) = τ_motor [N·m]（控制量，来自控制器）
%  输出端口（y）: y(1) = θ [rad]（含噪声关节角度）
%                y(2) = dθ/dt [rad/s]（含噪声角速度）
%                y(3) = τ_patient [N·m]（患者力矩，供对比分析）
%  状态变量：x(1) = θ [rad], x(2) = dθ/dt [rad/s]
% ========================================================================
function knee_joint_sfunc(block)
    setup(block);
end

%% ── setup: 定义端口、状态、参数 ─────────────────────────────────────
function setup(block)
    % 参数列表：[J, B, K, Fc, Fv, Fs, vs, sim_time,
    %            fatigue_tau, tau_pt_max, spasm_amp, spasm_dur, spasm_intv,
    %            noise_angle, noise_vel, J_pert_amp, J_pert_freq]
    block.NumDialogPrms = 17;

    % 连续状态：θ, θ̇
    block.NumContStates = 2;

    % 输入端口：1个（τ_motor）
    block.NumInputPorts  = 1;
    block.InputPort(1).Dimensions = 1;
    block.InputPort(1).DirectFeedthrough = false;

    % 输出端口：3个
    block.NumOutputPorts = 3;
    block.OutputPort(1).Dimensions = 1; % θ（含噪）
    block.OutputPort(2).Dimensions = 1; % θ̇（含噪）
    block.OutputPort(3).Dimensions = 1; % τ_patient

    block.SampleTimes = [0 0]; % 连续时间系统

    block.SimStateCompliance = 'DefaultSimState';
    block.RegBlockMethod('InitializeConditions', @InitCond);
    block.RegBlockMethod('Outputs',              @Output);
    block.RegBlockMethod('Derivatives',          @Deriv);
end

%% ── 初始条件 ─────────────────────────────────────────────────────────
function InitCond(block)
    block.ContStates.Data = [0; 0]; % 初始：θ=0, θ̇=0（伸直位）
end

%% ── 输出方程（传感器输出，含噪声）───────────────────────────────────
function Output(block)
    theta  = block.ContStates.Data(1);
    dtheta = block.ContStates.Data(2);
    t      = block.CurrentTime;

    % 读取噪声参数
    noise_angle = block.DialogPrm(14).Data;
    noise_vel   = block.DialogPrm(15).Data;

    % 传感器输出（叠加高斯白噪声）
    block.OutputPort(1).Data = theta  + noise_angle * randn();
    block.OutputPort(2).Data = dtheta + noise_vel   * randn();

    % 患者力矩（记录用，不影响控制）
    tau_pt_max  = block.DialogPrm(10).Data;
    fatigue_tau = block.DialogPrm(9).Data;
    tau_patient = tau_pt_max * exp(-t/fatigue_tau) * sin(pi*t/2);
    block.OutputPort(3).Data = tau_patient;
end

%% ── 导数方程（连续动力学方程核心）──────────────────────────────────
function Deriv(block)
    % ---- 读取状态 ----
    theta  = block.ContStates.Data(1);
    dtheta = block.ContStates.Data(2);
    t      = block.CurrentTime;
    tau_motor = block.InputPort(1).Data;

    % ---- 读取模型参数 ----
    J_base   = block.DialogPrm(1).Data;
    B        = block.DialogPrm(2).Data;
    K        = block.DialogPrm(3).Data;
    Fc       = block.DialogPrm(4).Data;
    Fv       = block.DialogPrm(5).Data;
    Fs       = block.DialogPrm(6).Data;
    vs       = block.DialogPrm(7).Data;

    % ---- 时变参数：惯量摄动（教材第5章：不确定性来源）----
    J_pert_amp  = block.DialogPrm(16).Data;
    J_pert_freq = block.DialogPrm(17).Data;
    J = J_base * (1 + J_pert_amp * sin(2*pi*J_pert_freq*t));

    % ---- 重力矩（强非线性项）----
    tau_gravity = K * sin(theta);

    % ---- Stribeck摩擦力矩（非线性摩擦建模）----
    % τ_f = [Fc + (Fs-Fc)·exp(-(θ̇/vs)²)]·sgn(θ̇) + Fv·θ̇
    tau_friction = (Fc + (Fs-Fc)*exp(-(dtheta/vs)^2)) * sign(dtheta) ...
                 + Fv * dtheta;

    % ---- 患者主动力矩（疲劳衰减模型）----
    tau_pt_max  = block.DialogPrm(10).Data;
    fatigue_tau = block.DialogPrm(9).Data;
    tau_patient = tau_pt_max * exp(-t/fatigue_tau) * sin(pi*t/2);
    tau_patient = max(0, tau_patient); % 患者只能主动屈膝（正方向）

    % ---- 痉挛脉冲扰动（Poisson随机过程近似）----
    spasm_amp = block.DialogPrm(11).Data;
    spasm_dur = block.DialogPrm(12).Data;
    % 简化实现：固定间隔注入痉挛（Simulink中建议用Signal Builder精确控制）
    spasm_intv = block.DialogPrm(13).Data;
    t_in_intv  = mod(t, spasm_intv);
    if t_in_intv < spasm_dur
        tau_spasm = spasm_amp;
    else
        tau_spasm = 0;
    end

    % ---- 膝关节动力学方程（核心ODE）----
    % J·θ̈ = τ_motor + τ_patient - B·θ̇ - K·sin(θ) - τ_friction - τ_spasm
    tau_net = tau_motor + tau_patient - B*dtheta - tau_gravity ...
            - tau_friction + tau_spasm;
    ddtheta = tau_net / J;

    % ---- 关节角度物理限位（0°~135°）----
    if theta <= 0 && dtheta < 0
        ddtheta = max(0, ddtheta); % 防止超越最小角度
    end
    if theta >= deg2rad(135) && dtheta > 0
        ddtheta = min(0, ddtheta); % 防止超越最大角度
    end

    block.Derivatives.Data = [dtheta; ddtheta];
end