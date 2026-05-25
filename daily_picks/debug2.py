#!/usr/bin/env python3
import requests, json
API_KEY = 'mkt_kZVRqvwI_IBTmK1hRxjQkiljMmLpTJXg1BIkQPlRAmE'
URL = 'https://mkapi2.dfcfs.com/finskillshub/api/claw/query'
headers = {'Content-Type': 'application/json', 'apikey': API_KEY}

for q in ['沪深两市今日上涨家数下跌家数成交额', '上证指数今日成交量成交额']:
    r = requests.post(URL, headers=headers, json={'toolQuery': q}, timeout=30).json()
    dtos = r.get('data',{}).get('data',{}).get('searchDataResultDTO',{}).get('dataTableDTOList',[])
    print(f'Query: {q}')
    print(f'DTOs count: {len(dtos)}')
    if dtos:
        for d in dtos[:3]:
            print(f'  title={d.get("title")}, entity={d.get("entityName")}')
            nm = d.get("nameMap",{})
            print(f'  nameMap={json.dumps(nm, ensure_ascii=False)[:300]}')
            tbl = d.get("table",{})
            for k,v in tbl.items():
                if k != 'headName':
                    lbl = nm.get(k, k)
                    print(f'    {lbl}: {v}')
    print()
