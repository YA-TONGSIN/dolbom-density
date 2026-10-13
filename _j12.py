import json,collections
d=json.load(open('data/day_care.json',encoding='utf-8'))
F=d['fields']; ix={k:i for i,k in enumerate(F)}; items=d['items']; sido=d['sido']
by=collections.defaultdict(set)
for r in items: by[sido[r[ix['sidoIx']]]].add(r[ix['sigungu']])
for s in ['제주특별자치도','세종특별자치시','서울특별시']:
    print(s, "시군구수=",len(by[s]), sorted(by[s])[:8])
# counts for sido with only one sigungu
one=[s for s,v in by.items() if len(v)<=1]
print("시군구가 1개뿐인 시도:",one)
for s in one:
    n=sum(1 for r in items if sido[r[ix['sidoIx']]]==s)
    dn=sum(1 for r in items if sido[r[ix['sidoIx']]]==s and r[ix['dong']])
    print("  ",s,"기관",n,"동값보유",dn)
