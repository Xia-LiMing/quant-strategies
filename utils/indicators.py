"""
技术指标计算工具库
=================
包含：KDJ、MACD、布林带、均线、量比

Author: Xia LiMing
Date: 2026-05
"""

import pandas as pd
import numpy as np


def calc_kdj(high: pd.Series, low: pd.Series, close: pd.Series,
             n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
    """计算KDJ指标"""
    low_n = low.rolling(n).min()
    high_n = high.rolling(n).max()
    rsv = (close - low_n) / (high_n - low_n + 1e-10) * 100

    K = rsv.ewm(com=m1 - 1, adjust=False).mean()
    D = K.ewm(com=m2 - 1, adjust=False).mean()
    J = 3 * K - 2 * D

    return pd.DataFrame({"K": K, "D": D, "J": J})


def calc_macd(close: pd.Series, fast: int = 12, slow: int = 26,
              signal: int = 9) -> pd.DataFrame:
    """计算MACD指标"""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = (dif - dea) * 2
    return pd.DataFrame({"DIF": dif, "DEA": dea, "MACD": macd})


def calc_boll(close: pd.Series, n: int = 20, k: float = 2.0) -> pd.DataFrame:
    """计算布林带"""
    mid = close.rolling(n).mean()
    std = close.rolling(n).std()
    upper = mid + k * std
    lower = mid - k * std
    return pd.DataFrame({"UPPER": upper, "MID": mid, "LOWER": lower})


def calc_ma(close: pd.Series, windows: list = None) -> pd.DataFrame:
    """计算多周期均线"""
    if windows is None:
        windows = [5, 10, 20, 60, 120, 250]
    result = {}
    for w in windows:
        result[f"MA{w}"] = close.rolling(w).mean()
    return pd.DataFrame(result)


def is_golden_cross_macd(macd_df: pd.DataFrame) -> bool:
    """判断MACD是否金叉（DIF上穿DEA）"""
    if len(macd_df) < 2:
        return False
    prev = macd_df.iloc[-2]
    curr = macd_df.iloc[-1]
    return prev["DIF"] < prev["DEA"] and curr["DIF"] >= curr["DEA"]


def is_ma_bullish(ma_df: pd.DataFrame,
                  order: list = None) -> bool:
    """判断均线是否多头排列"""
    if order is None:
        order = ["MA5", "MA10", "MA20", "MA60"]
    last = ma_df.iloc[-1]
    for i in range(len(order) - 1):
        if pd.isna(last[order[i]]) or pd.isna(last[order[i + 1]]):
            return False
        if last[order[i]] <= last[order[i + 1]]:
            return False
    return True


def main_wave_signal(close: pd.Series, high: pd.Series,
                     low: pd.Series, volume: pd.Series) -> dict:
    """
    主升浪综合信号判断
    条件：均线多头 + MACD金叉 + 量能放大
    """
    macd = calc_macd(close)
    ma = calc_ma(close)
    vol_ratio = volume.iloc[-5:].mean() / (volume.mean() + 1e-10)

    golden = is_golden_cross_macd(macd)
    ma_bull = is_ma_bullish(ma)
    vol_ok = vol_ratio >= 1.5

    score = sum([golden, ma_bull, vol_ok])
    signal = "强" if score == 3 else ("中" if score == 2 else "弱")

    return {
        "macd_golden_cross": golden,
        "ma_bullish": ma_bull,
        "volume_ratio": round(vol_ratio, 2),
        "score": score,
        "signal": signal,
    }
