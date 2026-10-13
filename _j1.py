import json,re,collections
d=json.load(open('data/day_care.json',encoding='utf-8'))
print("top keys:",list(d.keys())[:20])
meta=d.get('meta',{})
print("meta keys:",list(meta.keys()))
rows=d.get('rows') or d.get('items') or d.get('data')
print("rowcount",len(rows))
print("sample row:",json.dumps(rows[0],ensure_ascii=False))
