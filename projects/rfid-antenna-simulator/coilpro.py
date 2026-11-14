"""
coilpro.py
仿真计算模块 — 提供线圈电感、电阻计算、匹配评估，以及矢量化的频率响应计算。
主要改进点：
- 使用物理公式（电感近似、欧姆定律）并明确单位换算；
- 使用 numpy 矢量化频率响应计算以提升性能；
- 增加输入检查与容错（避免除零）。
"""

import math
import numpy as np

# 常量
MU0 = 4 * math.pi * 1e-7  # 真空磁导率 (H/m)
EPS0 = 8.854187817e-12    # 真空介电常数 (F/m)
# 常温材料电阻率 (Ω·m)
MATERIAL_RESISTIVITY = {
    '银': 1.59e-8,
    '铜': 1.724e-8,
    '金': 2.44e-8,
    '铝': 2.65e-8,
    '钨': 5.6e-8
}


def calculate_inductance(turns: int, mean_length_cm: float, shape: str = 'square') -> float:
    """
    近似计算空气芯平面线圈电感（返回 microHenry）。
    近似公式：L ≈ (N^2 * μ0 * A) / l （H），其中 A 为线圈有效面积，l 为平均绕线长度（m）。
    - turns: 匝数
    - mean_length_cm: 线圈“平均边长”或直径（cm）
    - shape: 'square' 或 'circular'
    返回：L（uH）
    注意：该公式为近似，用于工程估算；更精确需数值求解/电磁仿真。
    """
    n = max(1, int(turns))
    l_m = max(1e-6, mean_length_cm / 100.0)  # cm -> m, 防止零
    if shape.lower().startswith('c'):
        # 以 mean_length_cm 作为直径近似
        radius = l_m / 2.0
        area = math.pi * radius * radius
        path = 2 * math.pi * radius
    else:
        # 以 mean_length_cm 作为边长
        area = l_m * l_m
        path = 4.0 * l_m

    # 防止 path 为零
    if path <= 0:
        return 0.0
    L_h = (n**2) * MU0 * area / path
    return L_h * 1e6  # H -> uH


def calculate_resistance(turns: int, mean_length_cm: float, width_mm: float,
                         thickness_um: float, material: str = '铜') -> float:
    """
    计算线圈直流电阻（Ω），基于 R = rho * total_length / cross_section_area
    - width_mm: 线宽 (mm)
    - thickness_um: 铜箔厚度 (um)
    - mean_length_cm: 线圈边长或直径（cm），使用周长近似
    返回：R（Ω）
    """
    rho = MATERIAL_RESISTIVITY.get(material, MATERIAL_RESISTIVITY['铜'])
    l_m = max(1e-6, mean_length_cm / 100.0)
    # 假设方形周长：4 * l_m，若圆形也取近似周长（调用处可自行调整）
    total_length = max(1e-6, turns * 4.0 * l_m)
    width_m = max(1e-6, width_mm / 1000.0)
    thickness_m = max(1e-9, thickness_um / 1e6)
    area = width_m * thickness_m
    if area <= 0:
        return float('inf')
    R = rho * total_length / area
    return R


def Pro_cir_calc1(c1_pf: float, c2_pf: float, L_uH: float, R_ohm: float, z0: float = 50.0) -> str:
    """
    简单的匹配电路评估（单端）
    - c1_pf, c2_pf: pF
    - L_uH: uH
    - R_ohm: Ω
    返回字符串状态（包括谐振频率与 Q）
    """
    try:
        L = max(1e-12, L_uH * 1e-6)
        R = R_ohm if R_ohm != 0 else 1e-3
        C_series = max(1e-15, c2_pf * 1e-12)  # 以串联 C2 为主决定谐振
        omega = 2.0 * math.pi
        # 谐振频率
        f_res = 1.0 / (2.0 * math.pi * math.sqrt(L * C_series))
        X_L = 2.0 * math.pi * f_res * L
        Q = X_L / R if R > 0 else float('inf')

        status = f"谐振频率: {f_res/1e6:.3f} MHz | Q值: {Q:.2f}\n"
        if 0.9*z0 < R < 1.1*z0:
            status += "结果：阻抗接近参考阻抗，匹配较好。"
        else:
            status += f"结果：实部阻抗 {R:.2f}Ω，若需 50Ω，建议调整匹配元件。"
        return status
    except Exception as e:
        return f"计算出错: {e}"


def Pro_cir_calc2(c1_pf: float, c2_pf: float, L_uH: float, R_ohm: float, z0: float = 50.0) -> str:
    """
    差动电路的近似评估（以阻抗加倍近似）
    """
    res = Pro_cir_calc1(c1_pf, c2_pf, L_uH, R_ohm * 2.0, z0)
    return res.replace("单端", "差动")


def compute_freq_response(R_ohm: float, L_uH: float, C_pf: float,
                          f_min: float = 5e6, f_max: float = 30e6,
                          num_points: int = 1000, Z0: float = 50.0):
    """
    矢量化计算频率响应：
    - R_ohm: 线圈电阻（Ω）
    - L_uH: 线圈电感（uH）
    - C_pf: 等效电容（pF） —— 用于串联谐振模型
    - 返回：freqs, Z_mag, G_mag, S11_mag（均为 numpy 数组）
    说明：
    - 采用串联 R-L-C 模型：Z = R + j(ωL - 1/(ωC))
    - |G| = |1/Z|， S11 = |(Z - Z0)/(Z + Z0)|
    - 使用 numpy 矢量化以加速大点数计算。
    """
    import numpy as _np
    f_min = max(1.0, f_min)
    f_max = max(f_min + 1.0, f_max)
    num = max(10, int(num_points))
    freqs = _np.linspace(f_min, f_max, num)
    omega = 2.0 * _np.pi * freqs
    L = max(1e-12, L_uH * 1e-6)   # uH -> H
    C = max(1e-15, C_pf * 1e-12)  # pF -> F, 防止除零

    # Z (向量)
    Z = R_ohm + 1j * (omega * L - 1.0 / (omega * C))
    # 防止非常小的复数导致不稳定
    small_mask = _np.absolute(Z) < 1e-12
    Z[small_mask] = complex(1e-12, 0.0)

    Z_mag = _np.abs(Z)
    G_mag = _np.abs(1.0 / Z)
    S11 = _np.abs((Z - Z0) / (Z + Z0))
    return freqs, Z_mag, G_mag, S11
