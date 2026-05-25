#!/usr/bin/env python3
"""获取量比和各股主力资金流向"""
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

def extract_all_dtos(result):
    """提取所有dto的数据，按entityName分组"""
    try:
        data = result.get('data', {})
        inner = data.get('data', {})
        search = inner.get('searchDataResultDTO', {})
        dto_list = search.get('dataTableDTOList', [])
        out = {}
        for dto in dto_list:
            entity = dto.get('entityName', dto.get('title', ''))
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
            if values:
                out[entity] = values
        return out
    except Exception as e:
        return {'error': str(e)}

stocks = [
    ('603466', '风语筑'),
    ('002681', '奋达科技'),
    ('603986', '兆易创新'),
    ('002196', '方正电机'),
    ('603507', '振江股份'),
    ('000021', '深科技'),
    ('002617', '露笑科技'),
]

# 各股主力资金流向
fund_flows = {}
for code, name in stocks:
    print(f"查询{name}主力资金流向...", flush=True)
    r = query(f"{name}今日主力净流入资金")
    dtos = extract_all_dtos(r)
    print(f"  {name}: {json.dumps(dtos, ensure_ascii=False)[:200]}")
    fund_flows[code] = {'name': name, 'data': dtos}

with open('C:/Users/XR/quant-strategies/daily_picks/fund_flow.json', 'w', encoding='utf-8') as f:
    json.dump(fund_flows, f, ensure_ascii=False, indent=2)
print("资金流向数据已保存")
