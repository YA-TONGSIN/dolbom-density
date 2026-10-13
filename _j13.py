import json,collections
d=json.load(open('data/day_care.json',encoding='utf-8'))
F=d['fields']; ix={k:i for i,k in enumerate(F)}; items=d['items']; sido=d['sido']
for r in items:
    if sido[r[ix['sidoIx']]]=='세종특별자치시':
        print(repr(r[ix['sigungu']]), '| dong=',repr(r[ix['dong']]),'|',r[ix['name']][:24],'| addr=',repr(r[ix['addr']])[:50])
