import json
d=json.load(open('data/day_care.json',encoding='utf-8'))
F=d['fields']; ix={k:i for i,k in enumerate(F)}; items=d['items']; sido=d['sido']
rs=[r[ix['ratio']] for r in items]
print("min",min(rs),"max",max(rs))
lo=[r for r in items if r[ix['ratio']]==min(rs)][:3]
hi=[r for r in items if r[ix['ratio']]==max(rs)][:3]
for r in lo: print("MIN",sido[r[ix['sidoIx']]],r[ix['sigungu']],r[ix['name']],r[ix['cap']],r[ix['care']],r[ix['ratio']])
for r in hi: print("MAX",sido[r[ix['sidoIx']]],r[ix['sigungu']],r[ix['name']],r[ix['cap']],r[ix['care']],r[ix['ratio']])
# small-scale check
print("care<=2:",sum(1 for r in items if r[ix['care']]<=2))
print("cap<=10:",sum(1 for r in items if r[ix['cap']]<=10))
# top1 per sigungu with care<=2
import collections
g=collections.defaultdict(list)
for r in items: g[(r[ix['sidoIx']],r[ix['sigungu']])].append(r)
cnt=0; ex=[]
for k,v in g.items():
    v.sort(key=lambda r:r[ix['ratio']])
    if v and v[0][ix['care']]<=2:
        cnt+=1
        if len(ex)<8: ex.append((sido[k[0]],k[1],v[0][ix['name']],v[0][ix['cap']],v[0][ix['care']],v[0][ix['ratio']]))
print("시군구 중 1위가 요양보호사<=2명인 곳:",cnt,"/",len(g))
for e in ex: print("   ",e)
