"""
东方财富妙想 Skills API 数据接口封装
=====================================
支持：行情数据、财务数据、资金流向查询

Author: Xia LiMing
Date: 2026-05
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta


# API配置（从环境变量读取，不硬编码密钥）
MX_APIKEY = os.environ.get("MX_APIKEY", "")
BASE_URL = "https://mkapi2.dfcfs.com/finskillshub"


def _request(endpoint: str, params: dict) -> dict:
    """通用HTTP请求封装"""
    params["apikey"] = MX_APIKEY
    url = f"{BASE_URL}{endpoint}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[API Error] {endpoint}: {e}")
        return {}


def get_daily_kline(code: str, days: int = 60) -> list:
    """
    获取个股日K线数据

    Parameters
    ----------
    code : 股票代码，如 "603986"
    days : 获取天数

    Returns
    -------
    list of dict: [{date, open, high, low, close, volume, amount}, ...]
    """
    end = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - timedelta(days=days * 2)).strftime("%Y%m%d")
    data = _request("/kline/daily", {
        "code": code,
        "start_date": start,
        "end_date": end,
        "adjust": "qfq",  # 前复权
    })
    return data.get("data", [])[-days:]


def get_capital_flow(code: str, days: int = 5) -> list:
    """
    获取主力资金流向

    Parameters
    ----------
    code : 股票代码
    days : 查询天数

    Returns
    -------
    list of dict: [{date, main_net_inflow, super_net_inflow, ...}, ...]
    """
    data = _request("/capital/flow", {
        "code": code,
        "days": days,
    })
    return data.get("data", [])


def get_financial_data(code: str) -> dict:
    """
    获取最新财务数据（营收、净利润、FCF等）

    Parameters
    ----------
    code : 股票代码

    Returns
    -------
    dict: 财务指标字典
    """
    data = _request("/financial/summary", {
        "code": code,
        "period": "annual",
        "count": 3,
    })
    return data.get("data", {})


def get_market_cap(code: str) -> float:
    """获取最新总市值（元）"""
    data = _request("/quote/realtime", {"code": code})
    return float(data.get("data", {}).get("market_cap", 0))


# ─────────────────────────────────────────
# 示例用法
# ─────────────────────────────────────────
if __name__ == "__main__":
    # 查询风语筑(603466)近60日K线
    print("查询风语筑(603466)近期数据...")
    klines = get_daily_kline("603466", days=10)
    for k in klines[-3:]:
        print(f"  {k.get('date')} 收盘:{k.get('close')} 成交量:{k.get('volume')}")

    # 查询主力资金流向
    print("\n主力资金流向（近5日）：")
    flows = get_capital_flow("603466", days=5)
    for f in flows:
        print(f"  {f.get('date')} 主力净流入: {f.get('main_net_inflow')}万")
