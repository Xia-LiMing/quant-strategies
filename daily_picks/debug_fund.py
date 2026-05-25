#!/usr/bin/env python3
"""获取资金流向 - 调试版本"""
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

r = query("风语筑今日主力净流入")
print(json.dumps(r, ensure_ascii=False, indent=2)[:3000])
