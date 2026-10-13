import json,re,collections
d=json.load(open('data/day_care.json',encoding='utf-8'))
sido=d['sido']; items=d['items']
F=d['fields']; ix={k:i for i,k in enumerate(F)}
N=len(items)
tel=[r[ix['tel']] for r in items]
has=[t for t in tel if t]
print("total",N,"with tel",len(has),"pct",round(len(has)/N*100,2))
# format check
pat=re.compile(r'^0\d{1,2}-\d{3,4}-\d{4}$')
bad=[r for r in items if r[ix['tel']] and not pat.match(r[ix['tel']])]
print("non-matching format:",len(bad))
for r in bad[:25]: print("  BADFMT",r[ix['name']],"|",r[ix['sigungu']],"|",repr(r[ix['tel']]))
# area code vs sido
AC={'서울특별시':'02','부산광역시':'051','대구광역시':'053','인천광역시':'032','광주광역시':'062','대전광역시':'042','울산광역시':'052','세종특별자치시':'044','경기도':'031','강원특별자치도':'033','충청북도':'043','충청남도':'041','전북특별자치도':'063','전라남도':'061','경상북도':'054','경상남도':'055','제주특별자치도':'064'}
mis=collections.Counter(); misex=collections.defaultdict(list)
for r in items:
    t=r[ix['tel']]
    if not t: continue
    s=sido[r[ix['sidoIx']]]
    ac=t.split('-')[0]
    exp=AC.get(s)
    if exp and ac!=exp:
        mis[(s,ac)]+=1
        if len(misex[(s,ac)])<3: misex[(s,ac)].append((r[ix['name']],r[ix['sigungu']],t))
print("\n== area code mismatch by (sido, actual AC) ==")
tot=0
for k,v in mis.most_common(40):
    tot+=v
    print(" ",k,v,misex[k])
print("total mismatched area codes:",tot)
