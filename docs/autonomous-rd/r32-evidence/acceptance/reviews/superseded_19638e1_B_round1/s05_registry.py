# -*- coding: utf-8 -*-
"""只读: 注册表结构与计划指标条目。用法: python3 -I s05_registry.py <registry_path>"""
import json, sys
p = sys.argv[1]
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
print("TYPE", type(d).__name__)
if isinstance(d, dict):
    for k, v in d.items():
        if isinstance(v, list):
            print("KEY", k, "list len", len(v))
        elif isinstance(v, dict):
            print("KEY", k, "dict len", len(v), "subkeys", list(v.keys())[:12])
        else:
            print("KEY", k, "=", repr(v)[:300])
# find metrics container
cont = None
if isinstance(d, dict):
    for k in ('metrics', 'series', 'registry', 'items'):
        if k in d and isinstance(d[k], (list, dict)):
            cont = d[k]; print("CONTAINER", k, type(cont).__name__); break
if cont is None and isinstance(d, list):
    cont = d
plan = ['US_REAL_GDP','UNEMPLOYMENT','INDPRO','CPI','CORE_CPI','CORE_PCE','EA_REAL_GDP_YOY','EA_HICP_YOY','JP_POLICY_RATE','JP_POLICY_TARGET',
        'UST_10Y','TIPS_10Y','BEI_10Y','SPX','NIKKEI225','VIX','DXY','GOLD_F','USDJPY']
items = []
if isinstance(cont, dict):
    items = [dict(v, _id=k) if isinstance(v, dict) else {'_id': k, 'v': v} for k, v in cont.items()]
elif isinstance(cont, list):
    items = cont
print("N items", len(items))
def mid(it):
    return it.get('id') or it.get('metric_id') or it.get('_id') or it.get('series_id') or it.get('name')
ids = [mid(it) for it in items]
print("JP-economy ids:", [i for i, it in zip(ids, items) if isinstance(it, dict) and (it.get('economy') == 'JP')])
print("any id containing POLICY:", [i for i in ids if i and 'POLICY' in str(i).upper()])
print("any id containing TARGET:", [i for i in ids if i and 'TARGET' in str(i).upper()])
for it in items:
    if mid(it) in plan:
        print("----", json.dumps(it, ensure_ascii=False))
