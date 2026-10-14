"""문제의 크기를 데이터로 잰다 — "이 불편이 실재하는가"에 숫자로 답하기 위해.

주장이 아니라 수치로 묻는다:
  ① 보호자 한 명이 실제로 마주하는 후보가 몇 곳인가  (고르기 어려운가)
  ② 어디를 고르냐에 따라 실제로 차이가 나는가        (고를 가치가 있는가)

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
# 개원 1년 미만 기관은 중간값 계산에서 뺐으므로 여기서도 뺀 값을 본문 수치로 쓴다.
# (넣으면 정원 91명·요양보호사 1명 같은 신규 기관 때문에 격차가 부풀려진다)
def spread(rows_by_sgg, label):
    gaps, best, worst = [], [], []
    for k, v in rows_by_sgg.items():
        rs = sorted(x[F["ratio"]] for x in v)
        if len(rs) < 5:
            continue
        gaps.append(rs[-1] - rs[0]); best.append(rs[0]); worst.append(rs[-1])
    fold = st.median(worst) / max(st.median(best), 0.01)
    print(f"  [{label}] 기관 5곳 이상 시·군·구 {len(gaps)}개 · 격차 중앙값 {st.median(gaps):.1f}명 · "
          f"가장 적은 곳 {st.median(best):.1f}명 ↔ 많은 곳 {st.median(worst):.1f}명 = {fold:.1f}배")
    return st.median(gaps), fold

print()
print("=" * 70)
print("② 같은 시·군·구 안에서, 어디를 고르냐에 따라 생기는 차이")
spread(by_sgg, "전체 (참고)")
mature_by = defaultdict(list)
for k, v in by_sgg.items():
    mature_by[k] = [x for x in v if not x[F["isNew"]]]
gap_m, fold_m = spread(mature_by, "운영 1년 이상 — 본문 수치")
print(f"  → 같은 동네 안에서도 {fold_m:.1f}배 차이. 멀리 갈 것도 없이 '옆 센터'가 다르다")

# ── ③ 기존 수단 ──────────────────────────────────────────────────────────
# 데이터 1종 규칙이라 평가등급과의 비교는 하지 않는다(10-14 개정).
# 지도앱·공단 포털이 지역 안 비교를 제공하지 않는다는 것은 직접 확인한 사실로 PLAN 1번에 적는다.

print()
print("=" * 70)
print("한 문장으로")
print(f"  후보는 한 동네에 중앙값 {st.median(counts):.0f}곳이고, 그 안에서 1인당이 "
      f"{fold_m:.1f}배({gap_m:.1f}명)까지 갈리는데, 그 차이를 한눈에 보여주는 수단이 없다.")