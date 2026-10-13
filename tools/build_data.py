import sys, json, os
import pandas as pd

path = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else "data/day_care.json"

KEY = "장기요양기관코드"
TYPES = ["B03", "C03"]  # 재가노인복지시설 / 재가장기요양기관 주야간보호

xl = pd.ExcelFile(path)
gen = pd.read_excel(xl, "일반현황")
cap = pd.read_excel(xl, "입소인원")
stf = pd.read_excel(xl, "인력현황")

gen["시도"] = gen["시도 시군구 법정동명"].astype(str).str.split().str[0]
gen["시군구"] = gen["시도 시군구 법정동명"].astype(str).str.split().str[1]

day = cap[cap["기관유형코드"].isin(TYPES)][[KEY, "기관유형코드", "정원"]]
stf_cols = [KEY, "기관유형코드", "요양보호사", "간호사", "간호조무사",
            "사회복지사", "물리치료사", "작업치료사"]

df = (day.merge(gen[[KEY, "장기요양기관이름", "시도", "시군구", "기관별 상세주소", "지정일자"]].drop_duplicates(KEY), on=KEY)
         .merge(stf[stf_cols].drop_duplicates([KEY, "기관유형코드"]), on=[KEY, "기관유형코드"], how="left"))

print(f"주야간보호 전국 원시 {len(df):,}곳")

for c in ["정원", "요양보호사", "간호사", "간호조무사", "사회복지사", "물리치료사", "작업치료사"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df = df[df["시도"].notna() & (df["시도"] != "nan")]
bad_cap = (df["정원"].fillna(0) <= 0).sum()
bad_stf = (df["요양보호사"].fillna(0) <= 0).sum()

d = df[(df["정원"] > 0) & (df["요양보호사"] > 0)].copy()
d["ratio"] = (d["정원"] / d["요양보호사"]).round(2)

print(f"  정원 0/결측    제외 {bad_cap:,}")
print(f"  요양보호사 0/결측 제외 {bad_stf:,}")
print(f"  → 순위 산출 가능 {len(d):,}곳")

# 같은 기관이 B03/C03 중복 등록된 경우 1인당 수치가 유리한 쪽만 남김
d = d.sort_values("ratio").drop_duplicates(subset=[KEY], keep="first")
print(f"  → 기관코드 중복 제거 후 {len(d):,}곳")

# 개원 경과개월. 신규 지정 기관은 정원(인가치)은 큰데 인력이 아직 미충원이라
# 1인당 수치가 구조적으로 나쁘게 나온다. 숨기지 않고 '개원 초기'로 표시한다.
BASE = pd.Timestamp("2026-06-10")
desig = pd.to_datetime(d["지정일자"].astype("Int64").astype(str), format="%Y%m%d", errors="coerce")
d["months"] = ((BASE - desig).dt.days / 30.44)
d["ym"] = desig.dt.strftime("%Y-%m").fillna("")
NEW_MONTHS = 12
d["is_new"] = (d["months"] < NEW_MONTHS).fillna(False)
print(f"  → 개원 {NEW_MONTHS}개월 미만 {int(d['is_new'].sum()):,}곳 (표시 대상)")

# 중앙값은 개원 초기 기관을 빼고 계산한다 — 비교 기준이 왜곡되지 않도록
mature = d[~d["is_new"]]
nat_med = float(mature["ratio"].median())
sido_med = mature.groupby("시도")["ratio"].median().round(2).to_dict()
for s in d["시도"].unique():            # 성숙 기관이 없는 시도 대비
    sido_med.setdefault(s, round(float(d[d["시도"] == s]["ratio"].median()), 2))

# 용량 절감 ①: 시도 문자열을 인덱스로
sido_list = sorted(d["시도"].unique())
sido_ix = {s: i for i, s in enumerate(sido_list)}

# 용량 절감 ②: 상세주소 앞의 시도·시군구 중복 제거
# 세종처럼 시군구 자리에 동/면이 오는 경우 "시도 시군구" 순서가 아닐 수 있어
# 어느 쪽이든 앞에 붙어 있으면 반복해서 떼어낸다.
def trim_addr(addr, sd, sg):
    a = str(addr).strip()
    changed = True
    while changed:
        changed = False
        for pre in (sd, sg):
            if pre and a.startswith(pre):
                a = a[len(pre):].lstrip()
                changed = True
    return a

# 용량 절감 ③: 객체 → 배열 (키 이름 반복 제거)
FIELDS = ["name", "sidoIx", "sigungu", "addr", "cap", "care", "ratio",
          "nurse", "rehab", "social", "since", "isNew"]
records = []
for _, r in d.iterrows():
    records.append([
        str(r["장기요양기관이름"]),
        sido_ix[r["시도"]],
        str(r["시군구"]),
        trim_addr(r["기관별 상세주소"], r["시도"], r["시군구"]),
        int(r["정원"]),
        int(r["요양보호사"]),
        float(r["ratio"]),
        int((r["간호사"] or 0) + (r["간호조무사"] or 0)),
        int((r["물리치료사"] or 0) + (r["작업치료사"] or 0)),
        int(r["사회복지사"] or 0),
        str(r["ym"]),
        1 if r["is_new"] else 0,
    ])

sigungu_by_sido = {s: sorted(d[d["시도"] == s]["시군구"].unique()) for s in sido_list}

payload = {
    "meta": {
        "source": "공공데이터포털 국민건강보험공단_장기요양기관 시설별 현황",
        "dataId": "15124763",
        "baseDate": "2026-06-10",
        "cycle": "반기",
        "types": "재가노인복지시설/재가장기요양기관 주야간보호 (B03·C03)",
        "count": len(records),
        "newCount": int(d["is_new"].sum()),
        "newMonths": NEW_MONTHS,
        "nationalMedian": round(nat_med, 2),
        "sidoMedian": sido_med,
        "medianNote": f"중앙값은 개원 {NEW_MONTHS}개월 미만 기관을 제외하고 계산",
    },
    "fields": FIELDS,
    "sido": sido_list,
    "sigungu": sigungu_by_sido,
    "items": records,
}

os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

size = os.path.getsize(out)
print()
print(f"저장 {out}  {size:,} bytes  ({size/1024:.0f} KB)")
print(f"전국 중앙값 {nat_med:.2f}명")
print()
print("=== 시도별 기관수 / 중앙값 ===")
g = d.groupby("시도").agg(기관수=("ratio", "size"), 중앙값=("ratio", "median")).round(2)
print(g.sort_values("기관수", ascending=False).to_string())
print()
print("=== 시군구 수 ===")
print(f"  {d.groupby(['시도','시군구']).ngroups}개 시군구")
