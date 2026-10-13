"""문제의 크기를 데이터로 잰다 — "이 불편이 실재하는가"에 숫자로 답하기 위해.

주장이 아니라 수치로 묻는다:
  ① 보호자 한 명이 실제로 마주하는 후보가 몇 곳인가  (고르기 어려운가)
  ② 어디를 고르냐에 따라 실제로 차이가 나는가        (고를 가치가 있는가)
  ③ 그 차이를 기존 수단(공단 평가등급)으로 알 수 있는가 (새 도구가 필요한가)

실행: python tools/size_problem.py build/index.html
"""
import sys, json, re, statistics as st
from collections import defaultdict

html_path = sys.argv[1] if len(sys.argv) > 1 else "build/index.html"

src = open(html_path, encoding="utf-8").read()
DATA = json.loads(re.search(r"const DATA\s*=\s*(\{.*?\});\s*\n", src, re.S).group(1))
F = {k: i for i, k in enumerate(DATA["fields"])}
items = DATA["items"]
SIDO = DATA["sido"]
nat = DATA["meta"]["nationalMedian"]

# ── ① 보호자가 마주하는 후보 수 ───────────────────────────────────────────
by_sgg = defaultdict(list)
for r in items:
    by_sgg[(SIDO[r[F["sidoIx"]]], r[F["sigungu"]])].append(r)

counts = sorted(len(v) for v in by_sgg.values())
print("=" * 70)
print("① 보호자 한 명이 마주하는 후보 — 시·군·구 단위")
print(f"  시·군·구 {len(counts)}개 · 기관 {len(items):,}곳")
print(f"  한 시·군·구당 기관 수   중앙값 {st.median(counts):.0f}곳 · 평균 {st.mean(counts):.1f}곳 · 최대 {max(counts)}곳")
for th in (10, 20, 30):
    n = sum(1 for c in counts if c >= th)
    pop = sum(c for c in counts if c >= th)
    print(f"    {th}곳 이상인 시·군·구 {n:>3}개 ({n/len(counts)*100:.0f}%) — 그 안에 기관 {pop:,}곳 "
          f"({pop/len(items)*100:.0f}%의 기관이 '후보 {th}곳 이상'인 동네에 있다)")

# ── ② 같은 동네 안에서 선택이 만드는 차이 ─────────────────────────────────
print()
print("=" * 70)
print("② 같은 시·군·구 안에서, 어디를 고르냐에 따라 생기는 차이")
gaps, ratios_best, ratios_worst = [], [], []
for k, v in by_sgg.items():
    if len(v) < 5:
        continue
    rs = sorted(x[F["ratio"]] for x in v)
    gaps.append(rs[-1] - rs[0])
    ratios_best.append(rs[0])
    ratios_worst.append(rs[-1])
print(f"  대상: 기관 5곳 이상인 시·군·구 {len(gaps)}개")
print(f"  최저 ~ 최고 1인당 격차   중앙값 {st.median(gaps):.1f}명 · 평균 {st.mean(gaps):.1f}명")
print(f"  그 동네 가장 좋은 곳     중앙값 {st.median(ratios_best):.1f}명")
print(f"  그 동네 가장 나쁜 곳     중앙값 {st.median(ratios_worst):.1f}명")
fold = st.median(ratios_worst) / max(st.median(ratios_best), 0.01)
print(f"  → 같은 동네 안에서도 {fold:.1f}배 차이. 멀리 갈 것도 없이 '옆 센터'가 다르다")

# ── ③ 기존 수단으로 그 차이를 알 수 있는가 ────────────────────────────────
print()
print("=" * 70)
print("③ 공단 평가등급만으로 그 차이를 알 수 있는가")
graded = [r for r in items if r[F["grade"]]]
ungraded = [r for r in items if not r[F["grade"]]]
print(f"  평가등급이 있는 기관 {len(graded):,}곳 / 없는 기관 {len(ungraded):,}곳 "
      f"({len(ungraded)/len(items)*100:.0f}%는 등급으로 비교 자체가 불가)")

# 같은 시군구·같은 등급인데 1인당이 갈리는 쌍이 얼마나 되나
same_grade_spread = []
for k, v in by_sgg.items():
    byg = defaultdict(list)
    for x in v:
        if x[F["grade"]]:
            byg[x[F["grade"]]].append(x[F["ratio"]])
    for g, rs in byg.items():
        if len(rs) >= 3:
            same_grade_spread.append(max(rs) - min(rs))
if same_grade_spread:
    print(f"  같은 시·군·구 + 같은 등급 묶음 {len(same_grade_spread)}개 (3곳 이상)")
    print(f"    그 안에서의 1인당 격차  중앙값 {st.median(same_grade_spread):.1f}명 · 최대 {max(same_grade_spread):.1f}명")
    print(f"    → 등급이 같아도 인력은 갈린다. 등급은 이 질문에 답하지 않는다")

# 보호자가 '등급 A'만 믿고 고를 때 실제로 밟는 지뢰
a_rows = [r for r in graded if r[F["grade"]] == "A"]
trap = [r for r in a_rows if r[F["ratio"]] > nat]
print(f"  A등급 {len(a_rows):,}곳 중 전국 중간값({nat}) 초과 {len(trap):,}곳 ({len(trap)/len(a_rows)*100:.1f}%)")

print()
print("=" * 70)
print("한 문장으로")
print(f"  후보는 한 동네에 중앙값 {st.median(counts):.0f}곳이고, 그 안에서 1인당이 "
      f"{st.median(gaps):.1f}명까지 갈리는데,")
print(f"  그 차이를 알려주는 수단이 없다 — {len(ungraded)/len(items)*100:.0f}%는 등급조차 없고, "
      f"등급이 있어도 A등급의 {len(trap)/len(a_rows)*100:.0f}%가 중간값 아래다.")
