%% ========================================================================
%  expert_pid_sfunc.m  ——  专家PID控制器 S-Function（修正版）
%  教材对应：《智能控制》第2章 2.1~2.3节（专家系统 + 专家PID控制）
%  实验对应：实验四（专家PID控制实验）
%
%  ■ 修正说明：
%    使用 Dwork 替代已废弃的 NumDworkDiscStates 属性
%
%  输入：u(1)=误差e [rad], u(2)=误差变化率Δe [rad/s]
%  输出：y(1)=控制力矩τ [N·m]
%  状态：Dwork(1)=上一时刻控制量, Dwork(2)=误差积分, Dwork(3)=上上时刻误差
% ========================================================================
function expert_pid_sfunc(block)
    setup(block);
end

%% ========================================================================
%  setup：S-Function初始化配置
% ========================================================================
function setup(block)
    % ---- 参数定义 ----
    % [Kp, Ki, Kd, M1, M2, eps, k1, k2, umax, ts]
    block.NumDialogPrms = 10;
    
    % ---- 连续状态 ----
    block.NumContStates = 0;
    
    % ---- 离散状态（使用Dwork替代） ----
    % ✅ 关键修正：不再使用 block.NumDworkDiscStates
    % 改用 Dwork 数组，通过 RegBlockMethod 在 DoPostPropSetup 中配置
    
    % ---- 输入端口配置 ----
    block.NumInputPorts  = 2;
    block.InputPort(1).Dimensions = 1;      % e (误差)
    block.InputPort(2).Dimensions = 1;      % de (误差变化率)
    block.InputPort(1).DirectFeedthrough = true;
    block.InputPort(2).DirectFeedthrough = true;
    block.InputPort(1).SamplingMode = 'Sample';
    block.InputPort(2).SamplingMode = 'Sample';
    
    % ---- 输出端口配置 ----
    block.NumOutputPorts = 1;
    block.OutputPort(1).Dimensions = 1;     % τ_motor
    block.OutputPort(1).SamplingMode = 'Sample';
    
    % ---- 采样时间 ----
    ts = block.DialogPrm(10).Data;
    block.SampleTimes = [ts 0];  % 离散采样
    
    % ---- 注册回调函数 ----
    block.SimStateCompliance = 'DefaultSimState';
    block.RegBlockMethod('PostPropagationSetup', @DoPostPropSetup);  % ✅ 新增
    block.RegBlockMethod('InitializeConditions', @InitCond);
    block.RegBlockMethod('Outputs',              @Output);
    block.RegBlockMethod('Update',               @Update);
    block.RegBlockMethod('Terminate',            @Terminate);
end

%% ========================================================================
%  DoPostPropSetup：配置Dwork（替代离散状态）
% ========================================================================
function DoPostPropSetup(block)
    % ✅ 关键修正：在此处定义Dwork作为状态变量
    
    % Dwork 1: 上一时刻控制量 u_prev
    block.NumDworks = 3;
    
    block.Dwork(1).Name            = 'u_prev';
    block.Dwork(1).Dimensions      = 1;
    block.Dwork(1).DatatypeID      = 0;  % double
    block.Dwork(1).Complexity      = 'Real';
    block.Dwork(1).UsedAsDiscState = true;  % ✅ 标记为离散状态
    
    % Dwork 2: 误差积分 I_term
    block.Dwork(2).Name            = 'I_term';
    block.Dwork(2).Dimensions      = 1;
    block.Dwork(2).DatatypeID      = 0;
    block.Dwork(2).Complexity      = 'Real';
    block.Dwork(2).UsedAsDiscState = true;
    
    % Dwork 3: 上上时刻误差 e_prev2
    block.Dwork(3).Name            = 'e_prev2';
    block.Dwork(3).Dimensions      = 1;
    block.Dwork(3).DatatypeID      = 0;
    block.Dwork(3).Complexity      = 'Real';
    block.Dwork(3).UsedAsDiscState = true;
end

%% ========================================================================
%  InitializeConditions：初始化状态
% ========================================================================
function InitCond(block)
    block.Dwork(1).Data = 0;  % u_prev = 0
    block.Dwork(2).Data = 0;  % I_term = 0
    block.Dwork(3).Data = 0;  % e_prev2 = 0
end

%% ========================================================================
%  Outputs：输出方程（专家PID核心逻辑）
% ========================================================================
function Output(block)
    % ---- 读取输入 ----
    e  = block.InputPort(1).Data;   % 当前误差 [rad]
    de = block.InputPort(2).Data;   % 误差变化率 [rad/s]
    
    % ---- 读取参数 ----
    Kp   = block.DialogPrm(1).Data;
    Ki   = block.DialogPrm(2).Data;
    Kd   = block.DialogPrm(3).Data;
    M1   = block.DialogPrm(4).Data;  % 大误差阈值（8° = 0.1396 rad）
    M2   = block.DialogPrm(5).Data;  % 中误差阈值（3° = 0.0524 rad）
    eps  = block.DialogPrm(6).Data;  % 精细区阈值（0.5° = 0.0087 rad）
    k1   = block.DialogPrm(7).Data;  % 强化增益 >1
    k2   = block.DialogPrm(8).Data;  % 抑制系数 <1
    umax = block.DialogPrm(9).Data;
    ts   = block.DialogPrm(10).Data;
    
    % ---- 读取状态 ----
    u_prev  = block.Dwork(1).Data;
    I_term  = block.Dwork(2).Data;
    e_prev2 = block.Dwork(3).Data;
    
    % ---- 计算e_prev（由e和de反推）----
    e_prev = e - de * ts;
    
    % ---- 计算差分量 ----
    delta_e      = e - e_prev;       % Δe(k)
    delta_e_prev = e_prev - e_prev2; % Δe(k-1)
    
    % ================================================================
    %  专家PID规则库（5条规则，教材第2章2.3.1节）
    %  ★ 关键改进：R5（精细区）优先级最高
    % ================================================================
    
    % ── 规则R5：精细区，|e| ≤ ε，积分主导（最高优先级）──
    if abs(e) <= eps
        % 误差极小，加强积分以消除稳态误差
        I_new = I_term + Ki * e * ts;
        u = Kp * e + I_new + Kd * delta_e / ts;
        
    % ── 规则R1：大误差，Bang-bang开环控制 ────────────────
    elseif abs(e) > M1
        u = umax * sign(e);
        
    % ── 规则R2：误差增大且较大，强化PID控制 ──────────────
    elseif (e * delta_e > 0) && (abs(e) > M2)
        delta_u = k1 * (Kp*delta_e + Ki*e*ts + Kd*(delta_e - delta_e_prev));
        u = u_prev + delta_u;
        
    % ── 规则R3：误差增大但较小，普通PID控制 ──────────────
    elseif (e * delta_e > 0) && (abs(e) <= M2)
        delta_u = Kp*delta_e + Ki*e*ts + Kd*(delta_e - delta_e_prev);
        u = u_prev + delta_u;
        
    % ── 规则R4：误差减小（趋零），保持控制量 ─────────────
    elseif (e * delta_e < 0) && (delta_e * delta_e_prev > 0 || e == 0)
        u = u_prev;
        
    % ── 规则R5b：误差处于极值（Δe过零点）──────────────────
    elseif (e * delta_e < 0) && (delta_e * delta_e_prev < 0)
        if abs(e) >= M2
            u = u_prev + k1 * Kp * e;
        else
            u = u_prev + k2 * Kp * e;
        end
        
    else
        % 默认：保持上一时刻输出
        u = u_prev;
    end
    
    % ---- 力矩变化率限幅（安全保障）----
    du_max = 5.0 * ts;  % 每采样周期最大变化量 [N·m]
    u = u_prev + max(-du_max, min(du_max, u - u_prev));
    
    % ---- 输出限幅（关节安全力矩约束）----
    u = max(-umax, min(umax, u));
    
    % ---- 输出控制量 ----
    block.OutputPort(1).Data = u;
end

%% ========================================================================
%  Update：更新离散状态
% ========================================================================
function Update(block)
    e    = block.InputPort(1).Data;
    de   = block.InputPort(2).Data;
    ts   = block.DialogPrm(10).Data;
    Ki   = block.DialogPrm(2).Data;
    eps  = block.DialogPrm(6).Data;
    
    e_prev = e - de * ts;
    
    % 更新积分项（仅在精细区累积，避免积分饱和）
    if abs(e) <= eps
        block.Dwork(2).Data = block.Dwork(2).Data + Ki * e * ts;
    end
    
    % 更新历史值
    block.Dwork(1).Data = block.OutputPort(1).Data;  % u_prev
    block.Dwork(3).Data = e_prev;                    % e_prev2
end

%% ========================================================================
%  Terminate：仿真结束清理（可选）
% ========================================================================
function Terminate(block)
    % 清理工作（此处无需特殊操作）
end