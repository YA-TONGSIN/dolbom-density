import json,collections
d=json.load(open('data/day_care.json',encoding='utf-8'))
F=d['fields']; ix={k:i for i,k in enumerate(F)}; items=d['items']; sido=d['sido']
bad=collections.Counter()
for r in items:
    sg=r[ix['sigungu']]
    if sg and not (sg.endswith('시') or sg.endswith('군') or sg.endswith('구')):
        bad[(sido[r[ix['sidoIx']]],sg)]+=1
print("시/군/구로 끝나지 않는 시군구 값:",sum(bad.values()))
for k,v in bad.most_common(30): print("  ",k,v)
