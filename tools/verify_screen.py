"""화면 숫자 ↔ 원본 대조 (end-to-end 검증)

배포본 HTML에 실제로 박혀 있는 숫자를 꺼내서,
원본 XLSX로부터 **독립적으로 다시 계산한 값**과 전수 비교한다.
build_data.py 를 재사용하지 않는다 — 같은 코드로 확인하면 자기 자신을 확인하는 꼴이다.

실행: python tools/verify_screen.py build/index.html data/ltc_20260610.xlsx
"""
import sys, json, re, statistics as st
import openpyxl

html_path, xlsx_path = sys.argv[1], sys.argv[2]

# ── 1. 배포본 HTML에서 실제 탑재된 데이터 추출 ────────────────────────────
src = open(html_path, encoding="utf-8").read()
m = re.search(r"const DATA\s*=\s*(\{.*?\});\s*\n", src, re.S)
if not m:
    print("HTML에서 DATA 추출 실패"); sys.exit(1)
DATA = json.loads(m.group(1))
F = {k: i for i, k in enumerate(DATA["fields"])}
items = DATA["items"]
SIDO = DATA["sido"]
meta = DATA["meta"]
print(f"화면 탑재 데이터: {len(items):,}곳 · 시도 {len(SIDO)}개")
print(f"  메타 기준일 {meta['baseDate']} · 갱신 {meta['cycle']} · 데이터 {meta['dataId']}")
print()

# ── 2. 원본 XLSX에서 독립 재계산 (openpyxl 직접 읽기, pandas 미사용) ──────
wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)


def sheet_rows(name):
    ws = wb[name]
    it = ws.iter_rows(values_only=True)
    hdr = [str(c).strip() if c is not None else "" for c in next(it)]
    for r in it:
        yield dict(zip(hdr, r))


gen = {}
for r in sheet_rows("일반현황"):
    code = r.get("장기요양기관코드")
    if code is None or code in gen:
        continue
    full = str(r.get("시도 시군구 법정동명") or "").split()
    gen[code] = {
        "name": str(r.get("장기요양기관이름") or "").strip(),
        "sido": full[0] if len(full) > 0 else "",
        "sgg": full[1] if len(full) > 1 else "",
        "addr": str(r.get("기관별 상세주소") or "").strip(),
        "desig": r.get("지정일자"),
    }

cap = {}
for r in sheet_rows("입소인원"):
    t = str(r.get("기관유형코드") or "")
    if t not in ("B03", "C03"):
        continue
    key = (r.get("장기요양기관코드"), t)
    if key not in cap:
        cap[key] = r.get("정원")

stf = {}
for r in sheet_rows("인력현황"):
    key = (r.get("장기요양기관코드"), str(r.get("기관유형코드") or ""))
    if key not in stf:
        stf[key] = r.get("요양보호사")
wb.close()


def num(v):
    try:
        f = float(v)
        return f if f == f else None
    except (TypeError, ValueError):
        return None


# 원본 기준 계산 — 기관코드별로 ratio 최소값 채택(= build 쪽 중복제거 규칙과 동일 의미)
recomputed = {}
for (code, t), c in cap.items():
    cv, sv = num(c), num(stf.get((code, t)))
    if not cv or not sv or cv <= 0 or sv <= 0:
        continue
    g = gen.get(code)
    if not g or not g["sido"]:
        continue
    ratio = round(cv / sv, 2)
    prev = recomputed.get(code)
    if prev is None or ratio < prev["ratio"]:
        recomputed[code] = {"code": code, "name": g["name"], "sido": g["sido"], "sgg": g["sgg"],
                            "cap": int(cv), "care": int(sv), "ratio": ratio,
                            "desig": g["desig"]}

print(f"원본 독립 재계산: {len(recomputed):,}곳")
print()

# ── 3. 전수 대조 ──────────────────────────────────────────────────────────
by_name = {}
for v in recomputed.values():
    by_name.setdefault((v["name"], v["sido"], v["sgg"]), []).append(v)

mismatch, unmatched = [], []
checked = 0
for it in items:
    k = (it[F["name"]], SIDO[it[F["sidoIx"]]], it[F["sigungu"]])
    cands = by_name.get(k)
    if not cands:
        unmatched.append(k)
        continue
    ok = any(c["cap"] == it[F["cap"]] and c["care"] == it[F["care"]]
             and abs(c["ratio"] - it[F["ratio"]]) < 0.011 for c in cands)
    checked += 1
    if not ok:
        mismatch.append((k, it[F["cap"]], it[F["care"]], it[F["ratio"]],
                         [(c["cap"], c["care"], c["ratio"]) for c in cands]))

print("=" * 72)
print("【전수 대조】 화면 숫자 vs 원본 재계산")
print(f"  화면 레코드        {len(items):,}")
print(f"  원본에서 매칭됨     {checked:,}")
print(f"  매칭 실패          {len(unmatched):,}")
print(f"  ★ 값 불일치        {len(mismatch):,}")
if mismatch[:5]:
    for x in mismatch[:5]:
        print(f"      {x[0]}  화면({x[1]}/{x[2]}/{x[3]})  원본{x[4]}")
if unmatched[:3]:
    print("  매칭 실패 예시:", unmatched[:3])
print()

# ── 4. 화면에 뜨는 중앙값 대조 ────────────────────────────────────────────
print("=" * 72)
print("【중앙값 대조】 화면 표시값 vs 원본 재계산 (개원 12개월 미만 제외 규칙 적용)")
from datetime import date

BASE = date(2026, 6, 10)


def months_since(d):
    """일 단위로 정확히 계산한다.
    월 단위 근사(연*12+월)를 쓰면 경계(정확히 12개월 부근) 기관의 포함 여부가
    달라져 중앙값이 미세하게 어긋난다. 실제로 울산·충북에서 그 차이가 났다."""
    if d is None:
        return None
    s = str(int(d))
    if len(s) != 8:
        return None
    try:
        dt = date(int(s[:4]), int(s[4:6]), int(s[6:8]))
    except ValueError:
        return None
    return (BASE - dt).days / 30.44


mature = {}
for v in recomputed.values():
    ms = months_since(v["desig"])
    if ms is not None and ms >= 12:
        mature.setdefault(v["sido"], []).append(v["ratio"])

bad = 0
for sd in SIDO:
    shown = meta["sidoMedian"].get(sd)
    calc = round(st.median(mature[sd]), 2) if mature.get(sd) else None
    flag = "OK" if (calc is not None and abs(shown - calc) < 0.051) else "### 불일치"
    if flag != "OK":
        bad += 1
    print(f"  {sd:<10} 화면 {shown:>5}   원본재계산 {str(calc):>5}   {flag}")
print(f"\n  중앙값 불일치 {bad}건")
print()

# ── 5. 데모 상위 3곳 원본 대조 ────────────────────────────────────────────
print("=" * 72)
print("【데모 Top 3】 서울 관악구 — 화면값과 원본 행 직접 비교")
gw = sorted([x for x in items
             if SIDO[x[F["sidoIx"]]] == "서울특별시" and x[F["sigungu"]] == "관악구"],
            key=lambda r: (r[F["ratio"]], -r[F["cap"]]))[:3]
for i, x in enumerate(gw, 1):
    src_rows = by_name.get((x[F["name"]], "서울특별시", "관악구"), [])
    s = src_rows[0] if src_rows else None
    print(f"  {i}. {x[F['name']]}")
    print(f"       화면: 정원 {x[F['cap']]} / 요양보호사 {x[F['care']]} / {x[F['ratio']]}명")
    if s:
        same = (s['cap'] == x[F['cap']] and s['care'] == x[F['care']])
        print(f"       원본: 정원 {s['cap']} / 요양보호사 {s['care']} / {s['ratio']}명   "
              f"{'일치 ✔' if same else '### 불일치'}")
    else:
        print("       원본: 매칭 실패")

# ── 6. 데이터 1종 확인 ────────────────────────────────────────────────────
# 규칙: 원본 공공데이터셋 1개. 화면에 다른 데이터에서 온 칸·메타가 남아 있으면 실패로 본다.
print("=" * 72)
print("【데이터 종수】 화면 탑재 데이터에 15124763 외의 칸이 남아 있는가")
EXTRA_FIELDS = {"grade", "gyear", "tel"}
EXTRA_META = {"source2", "dataId2", "joinKey", "evalRange", "evalMatched", "evalRate",
              "corr", "gradeMedian", "gradeCount", "gapCount", "gapPct", "gapBase"}
left_f = sorted(EXTRA_FIELDS & set(DATA["fields"]))
left_m = sorted(EXTRA_META & set(meta))
meta_ok = not left_f and not left_m and meta["dataId"] == "15124763"
print(f"  남은 칸 {left_f or '없음'} · 남은 메타 {left_m or '없음'} · 출처 {meta['dataId']}")
print(f"  {'1종 ✔' if meta_ok else '### 다른 데이터가 남아 있음'}")
print()

print("=" * 72)
print(f"판정: 값 불일치 {len(mismatch)}건 · 중앙값 불일치 {bad}건 · 매칭실패 {len(unmatched)}건 · "
      f"데이터 {'1종 OK' if meta_ok else '1종 아님'}")