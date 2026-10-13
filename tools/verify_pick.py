import json, sys
import statistics as st

p = sys.argv[1] if len(sys.argv) > 1 else "data/day_care.json"
d = json.load(open(p, encoding="utf-8"))
F = {k: i for i, k in enumerate(d["fields"])}
items = d["items"]
SD = d["sido"]


def show(title, rows):
    print("=" * 76)
    print(title)
    for r in rows:
        print(f"  {r[F['ratio']]:6.2f}명  정원 {r[F['cap']]:4} / 요양보호사 {r[F['care']]:4}  "
              f"간호 {r[F['nurse']]:2} 재활 {r[F['rehab']]:2} 사복 {r[F['social']]:2}  "
              f"| {r[F['name']]}  ({SD[r[F['sidoIx']]]} {r[F['sigungu']]})")
    print()


# 1) 데모 지역 (서울 관악구) 상위 3
seoul = SD.index("서울특별시")
gwanak = [r for r in items if r[F["sidoIx"]] == seoul and r[F["sigungu"]] == "관악구"]
gwanak.sort(key=lambda r: (r[F["ratio"]], -r[F["cap"]]))
show("① 데모 지역 — 서울 관악구 상위 3곳", gwanak[:3])

# 2) 전국 최저 (가장 의심스러운 쪽)
allr = sorted(items, key=lambda r: r[F["ratio"]])
show("② 전국 최저 5곳 — 값이 너무 좋아서 의심되는 구간", allr[:5])

# 3) 전국 최고 (반대쪽 이상치)
show("③ 전국 최고 5곳 — 값이 너무 나빠서 의심되는 구간", allr[-5:])

# 4) 분포 점검
ratios = [r[F["ratio"]] for r in items]
caps = [r[F["cap"]] for r in items]
cares = [r[F["care"]] for r in items]
print("=" * 76)
print("④ 분포")
print(f"  기관수 {len(items):,}")
print(f"  1인당  중앙값 {st.median(ratios):.2f} / 평균 {st.mean(ratios):.2f} / "
      f"최소 {min(ratios):.2f} / 최대 {max(ratios):.2f}")
print(f"  정원   중앙값 {st.median(caps):.0f} / 최소 {min(caps)} / 최대 {max(caps)}")
print(f"  요양보호사 중앙값 {st.median(cares):.0f} / 최소 {min(cares)} / 최대 {max(cares)}")
print()

# 5) 상식 밖 후보 카운트
print("=" * 76)
print("⑤ 이상 의심 건수")
print(f"  요양보호사 1명뿐           {sum(1 for r in items if r[F['care']] == 1):,}")
print(f"  정원 10명 미만             {sum(1 for r in items if r[F['cap']] < 10):,}")
print(f"  1인당 2명 미만 (과하게 좋음) {sum(1 for r in items if r[F['ratio']] < 2):,}")
print(f"  1인당 20명 초과 (과하게 나쁨){sum(1 for r in items if r[F['ratio']] > 20):,}")
print(f"  간호인력 0명               {sum(1 for r in items if r[F['nurse']] == 0):,}")
