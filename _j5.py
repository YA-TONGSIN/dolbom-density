import json,re,collections
d=json.load(open('data/day_care.json',encoding='utf-8'))
sido=d['sido']; items=d['items']; F=d['fields']; ix={k:i for i,k in enumerate(F)}
# dong suffix check
SUF=('동','읍','면','가','리')
bad=collections.Counter(); ex=collections.defaultdict(list)
empty=0
for r in items:
    dg=r[ix['dong']]
    if not dg: empty+=1; continue
    if not dg.endswith(SUF):
        bad[dg]+=1
        if len(ex[dg])<2: ex[dg].append((sido[r[ix['sidoIx']]],r[ix['sigungu']],r[ix['name']]))
print("dong empty:",empty, "fill%",round((len(items)-empty)/len(items)*100,2))
print("non-suffix dong values:",sum(bad.values()))
for k,v in bad.most_common(20): print("  ",k,v,ex[k])
# 구 ending check
gu=[r for r in items if r[ix['dong']] and r[ix['dong']].endswith('구')]
print("dong ending with 구:",len(gu))
# cheongju dong list
cj=sorted(set(r[ix['dong']] for r in items if r[ix['sigungu']]=='청주시'))
print("청주시 dong values:",cj)
print("청주시 count:",sum(1 for r in items if r[ix['sigungu']]=='청주시'))
