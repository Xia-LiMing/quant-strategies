#!/usr/bin/env python3
"""生成选股报告所需的完整数据"""
import requests
import json

API_KEY = 'mkt_kZVRqvwI_IBTmK1hRxjQkiljMmLpTJXg1BIkQPlRAmE'
URL = 'https://mkapi2.dfcfs.com/finskillshub/api/claw/query'

def query(q):
    headers = {'Content-Type': 'application/json', 'apikey': API_KEY}
    payload = {'toolQuery': q}
    try:
        resp = requests.post(URL, headers=headers, json=payload, timeout=30)
        return resp.json()
    except Exception as e:
        return {'error': str(e)}

def parse_dto(dto):
    """解析单个dto为字典"""
    table = dto.get('table', {})
    name_map = dto.get('nameMap', {})
    values = {}
    for k, v in table.items():
        if k == 'headName':
            continue
        label = name_map.get(k) or name_map.get(int(k) if str(k).isdigit() else k) or k
        if isinstance(v, list) and v:
            values[str(label)] = str(v[0]) if v[0] is not None else '-'
        else:
            values[str(label)] = str(v) if v is not None else '-'
    return values

def get_dtolist(result):
    try:
        return result['data']['data']['searchDataResultDTO']['dataTableDTOList']
    except:
        return []

# ===== 获取各股资金流向 =====
stocks = [
    ('603466', '风语筑'),
    ('002681', '奋达科技'),
    ('603986', '兆易创新'),
    ('002196', '方正电机'),
    ('603507', '振江股份'),
    ('000021', '深科技'),
    ('002617', '露笑科技'),
]

fund_data = {}
for code, name in stocks:
    print(f"资金流向: {name}...", flush=True)
    r = query(f"{name}今日主力净流入")
    dtos = get_dtolist(r)
    if dtos:
        v = parse_dto(dtos[0])
        net = v.get('(区间)主力净流入资金', '-')
        indays = v.get('(区间)资金净流入天数', '-')
        outdays = v.get('(区间)资金净流出天数', '-')
        fund_data[code] = {'name': name, 'net': net, 'in_days': indays, 'out_days': outdays}
        print(f"  净流入={net}, 流入天={indays}, 流出天={outdays}")
    else:
        fund_data[code] = {'name': name, 'net': '-', 'in_days': '-', 'out_days': '-'}

# ===== 市场宽度数据 =====
print("查询市场宽度...", flush=True)
r2 = query("两市今日上涨家数下跌家数成交额")
dtos2 = get_dtolist(r2)
market_width = {}
if dtos2:
    market_width = parse_dto(dtos2[0])
    print("市场宽度:", json.dumps(market_width, ensure_ascii=False))

# 保存
all_data = {'fund_data': fund_data, 'market_width': market_width}
with open('C:/Users/XR/quant-strategies/daily_picks/all_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
print("完成")
