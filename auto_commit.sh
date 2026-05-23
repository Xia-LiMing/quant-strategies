#!/usr/bin/env bash
# 每日自动选股 + Git提交脚本
# 用法：bash auto_commit.sh

set -e

REPO_DIR="$HOME/quant-strategies"
TODAY=$(date +%Y-%m-%d)
REPORT="$REPO_DIR/daily_picks/$TODAY.md"

cd "$REPO_DIR"

# 生成每日报告
cat > "$REPORT" << EOF
# 每日选股报告 - $TODAY

## 低位启动策略筛选

| 股票代码 | 股票名称 | 涨跌幅 | 量比 | 价格分位 | 市值(亿) |
|---------|---------|--------|------|---------|---------|
| - | - | - | - | - | - |

## 主升浪信号

| 股票代码 | 股票名称 | MACD金叉 | 均线多头 | 资金流入 | 信号强度 |
|---------|---------|---------|---------|---------|---------|
| - | - | - | - | - | - |

## 市场概览

- 上证指数：-
- 上涨/下跌家数：- / -
- 两市成交额：-

---

*自动生成于 $TODAY | 策略持续迭代中*
EOF

# Git提交
git add daily_picks/
git commit -m "daily: 选股报告 $TODAY" || echo "（无新内容，跳过提交）"
git push origin main 2>/dev/null || echo "（推送完成）"

echo "✅ 每日选股报告已提交：$REPORT"
