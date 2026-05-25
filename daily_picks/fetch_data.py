#!/usr/bin/env python3
"""获取选股报告所需数据"""
import requests
import json
import sys

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

def extract_value(result, idx=0):
    """从API响应中提取第一个数值"""
    try:
        data = result.get('data', {})
        inner = data.get('data', {})
        search = inner.get('searchDataResultDTO', {})
        dto_list = search.get('dataTableDTOList', [])
        if not dto_list:
            return None, None
        dto = dto_list[idx] if idx < len(dto_list) else dto_list[0]
        table = dto.get('table', {})
        name_map = dto.get('nameMap', {})
        head_name = table.get('headName', [])
        # 获取所有指标
        result_dict = {}
        for k, v in table.items():
            if k == 'headName':
                continue
            label = name_map.get(k) or name_map.get(int(k) if str(k).isdigit() else k) or k
            if isinstance(v, list) and v:
                result_dict[str(label)] = str(v[0]) if v[0] is not None else '-'
            else:
                result_dict[str(label)] = str(v) if v is not None else '-'
        return result_dict, head_name
    except Exception as e:
        return None, str(e)

def main():
    results = {}

    # 1. 上证指数
    print("查询上证指数...", flush=True)
    r = query("上证指数最新价涨跌幅涨跌")
    data, head = extract_value(r)
    results['sh_index'] = data
    print("上证指数结果:", json.dumps(data, ensure_ascii=False) if data else "无数据")

    # 2. 个股行情
    stocks = [
        ('603466', '风语筑'),
        ('002681', '奋达科技'),
        ('603986', '兆易创新'),
        ('002196', '方正电机'),
        ('603507', '振江股份'),
        ('000021', '深科技'),
        ('002617', '露笑科技'),
    ]
    results['stocks'] = {}
    for code, name in stocks:
        print(f"查询 {name}({code})...", flush=True)
        r = query(f"{name}最新价涨跌幅量比市值")
        data, head = extract_value(r)
        results['stocks'][code] = {'name': name, 'data': data}
        print(f"  {name}: {json.dumps(data, ensure_ascii=False) if data else '无数据'}")

    # 3. 主力资金流向
    print("查询主力资金流向...", flush=True)
    codes_str = "风语筑 奋达科技 兆易创新 方正电机 振江股份 深科技 露笑科技"
    r = query(f"{codes_str}今日主力净流入")
    data, head = extract_value(r)
    results['fund_flow'] = data
    print("资金流向:", json.dumps(data, ensure_ascii=False) if data else "无数据")

    # 输出完整结果
    with open('C:/Users/XR/quant-strategies/daily_picks/fetch_result.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n数据已保存到 fetch_result.json")

if __name__ == '__main__':
    main()
