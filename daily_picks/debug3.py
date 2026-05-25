#!/usr/bin/env python3
import requests, json
API_KEY = 'mkt_kZVRqvwI_IBTmK1hRxjQkiljMmLpTJXg1BIkQPlRAmE'
URL = 'https://mkapi2.dfcfs.com/finskillshub/api/claw/query'
headers = {'Content-Type': 'application/json', 'apikey': API_KEY}

for q in ['上证综合指数最新价', '上证指数成交额']:
    r = requests.post(URL, headers=headers, json={'toolQuery': q}, timeout=30).json()
    dtos = r.get('data',{}).get('data',{}).get('searchDataResultDTO',{}).get('dataTableDTOList',[])
    print(f'Query: {q}, DTOs: {len(dtos)}')
    if dtos:
        d = dtos[0]
        nm = d.get("nameMap",{})
        tbl = d.get("table",{})
        for k,v in tbl.items():
            lbl = nm.get(k, k)
            print(f'  {lbl}: {v}')
    print()
