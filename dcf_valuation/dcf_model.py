"""
DCF 三阶段估值模型
=================
支持：
  - 自定义三阶段增长率
  - WACC 计算
  - 内在价值 & 安全边际输出
  - 敏感性分析（WACC x 终端增长率）

Author: Xia LiMing
Date: 2026-05
"""

import numpy as np
import pandas as pd


def dcf_three_stage(
    fcf_base: float,
    growth_stage1: float,
    years_stage1: int,
    growth_stage2: float,
    years_stage2: int,
    growth_terminal: float,
    wacc: float,
    shares_outstanding: float,
    net_debt: float = 0.0,
    margin_of_safety: float = 0.30,
) -> dict:
    """
    三阶段DCF估值

    Parameters
    ----------
    fcf_base          : 基准自由现金流（元）
    growth_stage1     : 第一阶段年增长率（如0.25表示25%）
    years_stage1      : 第一阶段年数
    growth_stage2     : 第二阶段年增长率
    years_stage2      : 第二阶段年数
    growth_terminal   : 永续增长率
    wacc              : 加权平均资本成本
    shares_outstanding: 总股本（股）
    net_debt          : 净负债（元，负值表示净现金）
    margin_of_safety  : 安全边际（默认30%）

    Returns
    -------
    dict: 包含内在价值、安全边际价格等关键指标
    """
    fcf = fcf_base
    pv_sum = 0.0
    year = 0

    # 第一阶段
    for _ in range(years_stage1):
        year += 1
        fcf *= (1 + growth_stage1)
        pv_sum += fcf / (1 + wacc) ** year

    # 第二阶段
    for _ in range(years_stage2):
        year += 1
        fcf *= (1 + growth_stage2)
        pv_sum += fcf / (1 + wacc) ** year

    # 终值
    terminal_value = fcf * (1 + growth_terminal) / (wacc - growth_terminal)
    pv_terminal = terminal_value / (1 + wacc) ** year

    # 股权价值
    equity_value = pv_sum + pv_terminal - net_debt
    intrinsic_value_per_share = equity_value / shares_outstanding
    safety_price = intrinsic_value_per_share * (1 - margin_of_safety)

    return {
        "pv_fcf": round(pv_sum / 1e8, 2),           # 亿元
        "pv_terminal": round(pv_terminal / 1e8, 2),  # 亿元
        "equity_value": round(equity_value / 1e8, 2),
        "intrinsic_per_share": round(intrinsic_value_per_share, 2),
        "safety_price": round(safety_price, 2),
        "terminal_ratio": round(pv_terminal / (pv_sum + pv_terminal) * 100, 1),
    }


def sensitivity_analysis(
    fcf_base, growth_stage1, years_stage1,
    growth_stage2, years_stage2,
    shares_outstanding, net_debt=0,
    wacc_range=None, terminal_range=None,
) -> pd.DataFrame:
    """
    敏感性分析：WACC x 永续增长率 → 每股内在价值矩阵
    """
    if wacc_range is None:
        wacc_range = [0.08, 0.09, 0.10, 0.11, 0.12]
    if terminal_range is None:
        terminal_range = [0.02, 0.03, 0.04, 0.05]

    rows = {}
    for wacc in wacc_range:
        row = {}
        for g_t in terminal_range:
            if wacc <= g_t:
                row[f"g={g_t*100:.0f}%"] = "N/A"
                continue
            result = dcf_three_stage(
                fcf_base, growth_stage1, years_stage1,
                growth_stage2, years_stage2, g_t, wacc,
                shares_outstanding, net_debt,
            )
            row[f"g={g_t*100:.0f}%"] = result["intrinsic_per_share"]
        rows[f"WACC={wacc*100:.0f}%"] = row

    return pd.DataFrame(rows).T


# ─────────────────────────────────────────
# 示例：兆易创新 (603986) 估值
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("兆易创新 (603986) DCF 估值")
    print("=" * 50)

    result = dcf_three_stage(
        fcf_base=12e8,          # 基准FCF约12亿
        growth_stage1=0.20,     # 第一阶段：20%增速（5年）
        years_stage1=5,
        growth_stage2=0.12,     # 第二阶段：12%增速（5年）
        years_stage2=5,
        growth_terminal=0.03,   # 永续增长3%
        wacc=0.10,              # WACC 10%
        shares_outstanding=4.2e8,  # 总股本约4.2亿股
        net_debt=-20e8,         # 净现金约20亿
        margin_of_safety=0.30,
    )

    print(f"  FCF现值合计     : {result['pv_fcf']} 亿")
    print(f"  终值现值        : {result['pv_terminal']} 亿（占比{result['terminal_ratio']}%）")
    print(f"  股权价值        : {result['equity_value']} 亿")
    print(f"  每股内在价值    : {result['intrinsic_per_share']} 元")
    print(f"  安全边际买入价  : {result['safety_price']} 元（30%折扣）")

    print("\n--- 敏感性分析（每股内在价值，元）---")
    df_sens = sensitivity_analysis(
        fcf_base=12e8,
        growth_stage1=0.20, years_stage1=5,
        growth_stage2=0.12, years_stage2=5,
        shares_outstanding=4.2e8,
        net_debt=-20e8,
    )
    print(df_sens.to_string())
