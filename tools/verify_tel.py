"""화면에 박힌 전화번호 ↔ 수집 원본(tel.json) 전수 대조.

①② 는 verify_screen.py 가 원본에서 독립 재계산해 대조한다.
③(전화번호)에는 그런 절이 없었다 — 5,270건이 한 번도 대조된 적 없이 제출본에 실려 있었다.
이 스크립트가 그 구멍을 메운다.

빌더(build_data.py)를 재사용하지 않는다. 배포본 HTML에서 DATA 를 꺼내고,
tel.json 을 따로 읽어 비교한다.

실행: python tools/verify_tel.py build/index.html data/tel.json
"""
import sys, json, re, io
from collections import Counter

html_path = sys.argv[1] if len(sys.argv) > 1 else "build/index.html"
tel_path = sys.argv[2] if len(sys.argv) > 2 else "data/tel.json"

src = io.open(html_path, encoding="utf-8").read()
DATA = json.loads(re.search(r"const DATA\s*=\s*(\{.*?\});\s*\n", src, re.S).group(1))
F = {k: i for i, k in enumerate(DATA["fields"])}
items = DATA["items"]
SIDO = DATA["sido"]
raw = json.load(io.open(tel_path, encoding="utf-8"))

print("화면 %d곳 · 수집 원본 %d건" % (len(items), len(raw)))
print()

# ── 1. 화면 번호가 전부 원본에서 온 것인가 (지어낸 번호가 없는가) ──────────
# 화면에는 기관코드가 실리지 않으므로 '번호 집합'으로 대조한다.
pool = set(raw.values())
shown = [r[F["tel"]] for r in items if r[F["tel"]]]
ghost = [t for t in shown if t not in pool]
blank = sum(1 for r in items if not r[F["tel"]])

print("=" * 66)
print("【전수 대조】 화면 전화번호 vs 수집 원본")
print("  화면에 번호가 있는 곳   %5d (%.1f%%)" % (len(shown), len(shown) / len(items) * 100))
print("  화면이 비어 있는 곳     %5d" % blank)
print("  ★ 원본에 없는 번호      %5d   (지어낸 번호가 있으면 0이 아니다)" % len(ghost))
for g in ghost[:5]:
    print("      ", g)

# ── 2. 형식 ───────────────────────────────────────────────────────────────
BAD = [t for t in shown if not re.fullmatch(r"\d{2,4}-\d{3,4}-\d{4}", t)]
print("  ★ 형식 위반             %5d" % len(BAD))
for b in BAD[:5]:
    print("      ", b)

# ── 3. 지역번호와 시·도가 맞는가 ──────────────────────────────────────────
# 틀렸다고 바로 오류는 아니다(대표번호 1588·070·010, 생활권이 다른 접경지).
# 숫자를 내놓고 사유가 설명되는지만 본다.
AREA = {"02": "서울특별시", "031": "경기도", "032": "인천광역시", "033": "강원특별자치도",
        "041": "충청남도", "042": "대전광역시", "043": "충청북도", "044": "세종특별자치시",
        "051": "부산광역시", "052": "울산광역시", "053": "대구광역시", "054": "경상북도",
        "055": "경상남도", "061": "전라남도", "062": "광주광역시", "063": "전북특별자치도",
        "064": "제주특별자치도"}
mismatch, nongeo = [], Counter()
for r in items:
    t = r[F["tel"]]
    if not t:
        continue
    head = t.split("-")[0]
    if head not in AREA:
        nongeo[head] += 1          # 070·010·1588 등 지역번호가 아닌 것
        continue
    sido = SIDO[r[F["sidoIx"]]]
    if AREA[head] != sido:
        mismatch.append((r[F["name"]], sido, r[F["sigungu"]], t))

print()
print("=" * 66)
print("【지역번호 ↔ 시·도】")
print("  불일치 %d건 · 지역번호가 아닌 번호 %d건 %s"
      % (len(mismatch), sum(nongeo.values()), dict(nongeo.most_common(5))))
print("  (불일치는 오류가 아니라 생활권·대표번호 사유가 대부분이다. 예시:)")
for m in mismatch[:6]:
    print("      %s · %s %s · %s" % m)

# ── 4. 판정 ───────────────────────────────────────────────────────────────
ok = (len(ghost) == 0 and len(BAD) == 0)
print()
print("=" * 66)
print("판정: 원본에 없는 번호 %d건 · 형식 위반 %d건 · 빈칸 %d곳 → %s"
      % (len(ghost), len(BAD), blank, "통과" if ok else "### 실패"))
sys.exit(0 if ok else 1)
