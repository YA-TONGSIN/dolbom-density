import json,re,collections
d=json.load(open('data/day_care.json',encoding='utf-8'))
print("fields:",d['fields'])
print("meta:",json.dumps(d['meta'],ensure_ascii=False)[:2000])
