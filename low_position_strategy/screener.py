"""
低位启动策略选股器
================
筛选条件：
  - 60日价格处于低位区间（20%分位以下）
  - 成交量放大 >= 1.5倍
  - 当日涨幅 1% ~ 7%
  - 市值区间 2亿 ~ 200亿
  - 排除ST股

Author: Xia LiMing
Date: 2026-05
"""

import pandas as pd
import numpy as np
from datetime import datetime


# ─────────────────────────────────────────
# 筛选参数（可按需调整）
# ─────────────────────────────────────────
PARAMS = {
    "lookback_days": 60,          # 回看天数
    "price_pct_threshold": 0.20,  # 价格分位数上限（低于20%分位视为低位）
    "volume_ratio_min": 1.5,      # 最小量比（近5日均量 / 60日均量）
    "pct_change_min": 0.01,       # 当日最小涨幅
    "pct_change_max": 0.07,       # 当日最大涨幅
    "mktcap_min": 2e8,            # 最小市值（2亿）
    "mktcap_max": 200e8,          # 最大市值（200亿）
}


def is_low_position(close_series: pd.Series, threshold: float = 0.20) -> bool:
    """判断最新收盘价是否处于60日低位区间"""
    if len(close_series) < 2:
        return False
    low = close_series.min()
    high = close_series.max()
    if high == low:
        return False
    pct = (close_series.iloc[-1] - low) / (high - low)
    return pct <= threshold


def calc_volume_ratio(volume_series: pd.Series, recent_days: int = 5) -> float:
    """计算量比：近N日均量 / 60日均量"""
    if len(volume_series) < recent_days + 1:
        return 0.0
    recent_avg = volume_series.iloc[-recent_days:].mean()
    long_avg = volume_series.mean()
    if long_avg == 0:
        return 0.0
    return recent_avg / long_avg


def screen_stock(
    code: str,
    close: pd.Series,
    volume: pd.Series,
    pct_change_today: float,
    market_cap: float,
    is_st: bool = False,
) -> dict:
    """
    对单只股票执行低位启动策略筛选

    Parameters
    ----------
    code            : 股票代码
    close           : 近60日收盘价序列
    volume          : 近60日成交量序列
    pct_change_today: 当日涨跌幅（小数形式，如0.03表示涨3%）
    market_cap      : 总市值（元）
    is_st           : 是否为ST股

    Returns
    -------
    dict: {"code", "passed", "reasons", "volume_ratio", "price_pct"}
    """
    p = PARAMS
    reasons = []

    # 排除ST
    if is_st:
        reasons.append("ST股排除")
        return {"code": code, "passed": False, "reasons": reasons}

    # 市值过滤
    if not (p["mktcap_min"] <= market_cap <= p["mktcap_max"]):
        reasons.append(f"市值不符：{market_cap/1e8:.1f}亿")
        return {"code": code, "passed": False, "reasons": reasons}

    # 涨幅过滤
    if not (p["pct_change_min"] <= pct_change_today <= p["pct_change_max"]):
        reasons.append(f"涨幅不符：{pct_change_today*100:.2f}%")
        return {"code": code, "passed": False, "reasons": reasons}

    # 低位判断
    low = close.min()
    high = close.max()
    price_pct = (close.iloc[-1] - low) / (high - low) if high != low else 1.0
    if not is_low_position(close, p["price_pct_threshold"]):
        reasons.append(f"价格非低位：{price_pct*100:.1f}%分位")
        return {"code": code, "passed": False, "reasons": reasons}

    # 量比判断
    vol_ratio = calc_volume_ratio(volume)
    if vol_ratio < p["volume_ratio_min"]:
        reasons.append(f"量能不足：量比={vol_ratio:.2f}")
        return {"code": code, "passed": False, "reasons": reasons}

    return {
        "code": code,
        "passed": True,
        "reasons": ["符合低位启动条件"],
        "volume_ratio": round(vol_ratio, 2),
        "price_pct": round(price_pct * 100, 1),
        "pct_change": round(pct_change_today * 100, 2),
        "market_cap_yi": round(market_cap / 1e8, 1),
    }


def batch_screen(stock_data: list) -> pd.DataFrame:
    """
    批量筛选

    Parameters
    ----------
    stock_data : list of dict，每个dict包含:
        code, close(Series), volume(Series),
        pct_change_today, market_cap, is_st

    Returns
    -------
    DataFrame：通过筛选的标的
    """
    results = []
    for s in stock_data:
        r = screen_stock(**s)
        if r["passed"]:
            results.append(r)

    if not results:
        print(f"[{datetime.now().strftime('%Y-%m-%d')}] 今日无符合低位启动条件的标的")
        return pd.DataFrame()

    df = pd.DataFrame(results)
    df = df.sort_values("volume_ratio", ascending=False)
    print(f"[{datetime.now().strftime('%Y-%m-%d')}] 共筛选出 {len(df)} 只标的：")
    print(df[["code", "pct_change", "volume_ratio", "price_pct", "market_cap_yi"]].to_string(index=False))
    return df


# ─────────────────────────────────────────
# 示例用法
# ─────────────────────────────────────────
if __name__ == "__main__":
    # 模拟数据示例（实际使用时替换为妙想API数据）
    np.random.seed(42)
    demo_data = [
        {
            "code": "603466",  # 风语筑
            "close": pd.Series(np.random.uniform(9, 12, 60)),
            "volume": pd.Series(np.random.uniform(1e6, 3e6, 60)),
            "pct_change_today": 0.035,
            "market_cap": 25e8,
            "is_st": False,
        },
        {
            "code": "002681",  # 奋达科技
            "close": pd.Series(np.random.uniform(6, 8, 60)),
            "volume": pd.Series(np.random.uniform(5e5, 2e6, 60)),
            "pct_change_today": 0.025,
            "market_cap": 18e8,
            "is_st": False,
        },
    ]
    batch_screen(demo_data)
