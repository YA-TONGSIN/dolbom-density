import json,collections
d=json.load(open('data/day_care.json',encoding='utf-8'))
sido=d['sido']; items=d['items']; F=d['fields']; ix={k:i for i,k in enumerate(F)}
# duplicates by (sido,sigungu,name,addr)
c=collections.Counter()
for r in items:
    c[(r[ix['sidoIx']],r[ix['sigungu']],r[ix['name']],r[ix['addr']])]+=1
dups=[k for k,v in c.items() if v>1]
print("exact name+addr dup groups:",len(dups),"rows:",sum(c[k] for k in dups))
# name-only dup within same sigungu (addr differs) -> notice would NOT fire
c2=collections.Counter()
for r in items: c2[(r[ix['sidoIx']],r[ix['sigungu']],r[ix['name']])]+=1
nd=[k for k,v in c2.items() if v>1]
print("name dup groups (same sigungu):",len(nd),"rows:",sum(c2[k] for k in nd))
missed=[k for k in nd if (k[0],k[1],k[2]) not in [(x[0],x[1],x[2]) for x in dups]]
print("name-dup but addr differs (notice NOT shown):",len(missed))
for k in missed[:10]:
    print("  ",sido[k[0]],k[1],k[2])
    for r in items:
        if (r[ix['sidoIx']],r[ix['sigungu']],r[ix['name']])==k:
            print("      addr=",repr(r[ix['addr']]),"cap",r[ix['cap']],"care",r[ix['care']],"ratio",r[ix['ratio']],"grade",repr(r[ix['grade']]),"tel",r[ix['tel']])
print()
# 행복나눔
for r in items:
    if '행복나눔요양기관' in r[ix['name']]:
        print("HN:",sido[r[ix['sidoIx']]],r[ix['sigungu']],r[ix['name']],"|addr",repr(r[ix['addr']]),"cap",r[ix['cap']],"care",r[ix['care']],"ratio",r[ix['ratio']],"grade",repr(r[ix['grade']]),"tel",r[ix['tel']])
