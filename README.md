# 量化策略集 | Quant Strategies

> A股量化投资策略研究与实现 —— 夏黎明 (Xia LiMing)

## 项目简介

本仓库汇集了个人在A股市场的量化投资策略实践，涵盖基本面估值、技术分析、选股策略与回测框架。

## 目录结构

```
quant-strategies/
├── dcf_valuation/          # DCF内在价值估值模型
│   ├── models/             # 估值模型代码
│   └── cases/              # 个股估值案例（兆易创新等）
├── technical_strategies/   # 技术分析策略
│   ├── kdj_macd/           # KDJ + MACD 组合信号
│   └── main_wave/          # 主升浪研判（主力资金追踪）
├── low_position_strategy/  # 低位启动策略（核心选股）
│   ├── screener.py         # 选股主程序
│   └── backtest_report/    # 历史回测报告
├── data_fetch/             # 数据获取与清洗
│   └── mx_data_api.py      # 妙想Skills数据接口封装
├── backtest/               # 回测框架
│   └── engine.py           # 通用回测引擎
└── utils/                  # 工具函数
    └── indicators.py       # 技术指标计算（KDJ/MACD/布林带）
```

## 核心策略

### 1. 低位启动策略

筛选条件：
- 60日价格处于低位区间（20%分位以下）
- 成交量放大 ≥ 1.5倍（近5日均量 vs 60日均量）
- 当日涨幅 1% ~ 7%
- 市值区间 2亿 ~ 200亿
- 排除ST、退市风险股

### 2. DCF内在价值估值

- 三阶段DCF模型（高速增长 → 过渡期 → 永续增长）
- 覆盖行业：半导体、消费电子、医药制造、化工材料
- 已建模个股：兆易创新(603986)、振江股份、深科技等

### 3. 主升浪研判

- 主力资金持续净流入 > 3日
- 均线多头排列（5/10/20/60日）
- MACD金叉 + 量能配合
- 典型案例：奋达科技、露笑科技

## 回测表现

| 策略 | 回测区间 | 年化收益 | 最大回撤 | 夏普比率 |
|------|---------|---------|---------|---------|
| 低位启动 | 2022-2025 | 待更新 | 待更新 | 待更新 |
| 主升浪 | 2023-2025 | 待更新 | 待更新 | 待更新 |

## 技术栈

- **数据源**：东方财富妙想 Skills API
- **语言**：Python 3.9+
- **核心库**：pandas, numpy, matplotlib, mplfinance
- **回测框架**：自建轻量级回测引擎

## 联系方式

- GitHub: [@Xia-LiMing](https://github.com/Xia-LiMing)
- Email: 936543981@qq.com

---

*持续更新中 | Continuously updated*
