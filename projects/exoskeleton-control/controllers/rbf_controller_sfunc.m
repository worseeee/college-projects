%% ========================================================================
%  rbf_controller_sfunc.m  ——  RBF神经网络自适应前馈补偿器（修正版）
%  教材对应：第7章7.3节（RBF神经网络结构与算法）
%           第9章9.4节（RBF网络监督控制框架）
%
%  输入端口：u(1)=θ_d, u(2)=θ, u(3)=ė, u(4)=e
%  输出端口：y(1)=τ_RBF, y(2)=权值向量w（供监测）
% ========================================================================
function rbf_controller_sfunc(block)
    setup(block);
end

function setup(block)
    % 参数：[n_hidden, eta, lambda, umax, ts, c_data, sigma_data, w_init]
    block.NumDialogPrms = 8;
    
    % 输入端口
    block.NumInputPorts  = 4;
    for i = 1:4
        block.InputPort(i).Dimensions = 1;
        block.InputPort(i).DirectFeedthrough = true;
        block.InputPort(i).SamplingMode = 'Sample';
    end
    
    % 输出端口
    block.NumOutputPorts = 2;
    block.OutputPort(1).Dimensions = 1;   % τ_RBF
    block.OutputPort(2).Dimensions = 11;  % 权值向量
    block.OutputPort(1).SamplingMode = 'Sample';
    block.OutputPort(2).SamplingMode = 'Sample';
    
    % 采样时间
    ts = block.DialogPrm(5).Data;
    block.SampleTimes = [ts 0];
    
    % ✅ 修正：不使用 NumDworkDiscStates
    block.SimStateCompliance = 'DefaultSimState';
    block.RegBlockMethod('PostPropagationSetup', @DoPostPropSetup);
    block.RegBlockMethod('InitializeConditions', @InitCond);
    block.RegBlockMethod('Outputs',              @Output);
    block.RegBlockMethod('Update',               @Update);
end

%% ========================================================================
%  DoPostPropSetup：配置Dwork
% ========================================================================
function DoPostPropSetup(block)
    n_hidden = block.DialogPrm(1).Data;
    
    % Dwork: 权值向量 w (n_hidden × 1)
    block.NumDworks = 1;
    
    block.Dwork(1).Name            = 'weights';
    block.Dwork(1).Dimensions      = n_hidden;
    block.Dwork(1).DatatypeID      = 0;  % double
    block.Dwork(1).Complexity      = 'Real';
    block.Dwork(1).UsedAsDiscState = true;
end

function InitCond(block)
    n = block.DialogPrm(1).Data;
    w_init = block.DialogPrm(8).Data;
    
    if isscalar(w_init)
        block.Dwork(1).Data = 0.01 * randn(n, 1);
    else
        block.Dwork(1).Data = w_init(:);
    end
end

function Output(block)
    % 读取输入
    theta_d  = block.InputPort(1).Data;
    theta    = block.InputPort(2).Data;
    dtheta_e = block.InputPort(3).Data;
    
    % 读取参数
    n_hidden   = block.DialogPrm(1).Data;
    c_data     = block.DialogPrm(6).Data;
    sigma_data = block.DialogPrm(7).Data;
    umax       = block.DialogPrm(4).Data;
    
    % 读取权值
    w = block.Dwork(1).Data;
    
    % 构造输入向量
    x = [theta_d; theta; dtheta_e];
    
    % 计算高斯基函数
    phi = zeros(n_hidden, 1);
    c_mat = reshape(c_data, n_hidden, 3);
    
    for j = 1:n_hidden
        diff = x - c_mat(j,:)';
        phi(j) = exp(-norm(diff)^2 / (2 * sigma_data(j)^2));
    end
    
    % RBF输出
    tau_rbf = w' * phi;
    tau_rbf = max(-umax*0.5, min(umax*0.5, tau_rbf));
    
    block.OutputPort(1).Data = tau_rbf;
    block.OutputPort(2).Data = w;
end

function Update(block)
    e          = block.InputPort(4).Data;
    theta_d    = block.InputPort(1).Data;
    theta      = block.InputPort(2).Data;
    dtheta_e   = block.InputPort(3).Data;
    
    n_hidden   = block.DialogPrm(1).Data;
    eta        = block.DialogPrm(2).Data;
    lambda     = block.DialogPrm(3).Data;
    ts         = block.DialogPrm(5).Data;
    c_data     = block.DialogPrm(6).Data;
    sigma_data = block.DialogPrm(7).Data;
    
    x = [theta_d; theta; dtheta_e];
    w = block.Dwork(1).Data;
    c_mat = reshape(c_data, n_hidden, 3);
    
    % 计算基函数
    phi = zeros(n_hidden, 1);
    for j = 1:n_hidden
        diff = x - c_mat(j,:)';
        phi(j) = exp(-norm(diff)^2 / (2 * sigma_data(j)^2));
    end
    
    % 权值更新
    delta_w = ts * (eta * e * phi - lambda * w);
    w_new = w + delta_w;
    
    % 权值限幅
    w_max = 30.0;
    w_new = max(-w_max, min(w_max, w_new));
    
    block.Dwork(1).Data = w_new;
end