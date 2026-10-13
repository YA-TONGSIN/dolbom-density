"""가설 검정: 1인당 어르신 수가 비정상적으로 높은 기관은 '최근 지정된 신규 기관'인가?
자료 기준일 2026-06-10 기준으로 지정일자와 1인당 수치의 관계를 본다.
"""
import sys
import pandas as pd

path = sys.argv[1]
KEY = "장기요양기관코드"
xl = pd.ExcelFile(path)
gen = pd.read_excel(xl, "일반현황")
cap = pd.read_excel(xl, "입소인원")
stf = pd.read_excel(xl, "인력현황")

gen["시도"] = gen["시도 시군구 법정동명"].astype(str).str.split().str[0]
day = cap[cap["기관유형코드"].isin(["B03", "C03"])][[KEY, "기관유형코드", "정원"]]

df = (day.merge(gen[[KEY, "장기요양기관이름", "시도", "지정일자"]].drop_duplicates(KEY), on=KEY)
         .merge(stf[[KEY, "기관유형코드", "요양보호사"]].drop_duplicates([KEY, "기관유형코드"]),
                on=[KEY, "기관유형코드"], how="left"))

for c in ["정원", "요양보호사"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df["지정일"] = pd.to_datetime(df["지정일자"].astype("Int64").astype(str),
                            format="%Y%m%d", errors="coerce")

d = df[(df["정원"] > 0) & (df["요양보호사"] > 0)].copy()
d["ratio"] = d["정원"] / d["요양보호사"]
d = d.sort_values("ratio").drop_duplicates(subset=[KEY], keep="first")

BASE = pd.Timestamp("2026-06-10")
d["지정후_개월"] = ((BASE - d["지정일"]).dt.days / 30.44).round(1)

print(f"대상 {len(d):,}곳 · 지정일 결측 {d['지정일'].isna().sum():,}")
print()

bins = [(0, 2, "0~2개월"), (2, 6, "2~6개월"), (6, 12, "6~12개월"),
        (12, 36, "1~3년"), (36, 120, "3~10년"), (120, 10000, "10년 이상")]
print("=" * 72)
print("지정 후 경과기간별 1인당 어르신 수")
print(f"{'구간':>10} {'기관수':>7} {'중앙값':>8} {'평균':>8} {'20명초과':>9}")
for lo, hi, label in bins:
    g = d[(d["지정후_개월"] >= lo) & (d["지정후_개월"] < hi)]
    if len(g) == 0:
        continue
    over = (g["ratio"] > 20).sum()
    print(f"{label:>10} {len(g):>7,} {g['ratio'].median():>8.2f} {g['ratio'].mean():>8.2f} "
          f"{over:>5,} ({over/len(g)*100:>4.1f}%)")

print()
print("=" * 72)
print("1인당 20명 초과 기관(134곳)의 지정 시점")
bad = d[d["ratio"] > 20]
print(f"  총 {len(bad):,}곳")
print(f"  지정 후 2개월 미만  {(bad['지정후_개월'] < 2).sum():,}곳")
print(f"  지정 후 6개월 미만  {(bad['지정후_개월'] < 6).sum():,}곳")
print(f"  요양보호사 1명      {(bad['요양보호사'] == 1).sum():,}곳")
print()
print("  지정일 상위 분포:")
print(bad["지정일"].dt.to_period("M").value_counts().head(6).to_string())

print()
print("=" * 72)
print("참고 — 전체에서 지정 후 2개월 미만 기관")
new = d[d["지정후_개월"] < 2]
print(f"  {len(new):,}곳 · 중앙값 {new['ratio'].median():.2f} · 20명 초과 {(new['ratio'] > 20).sum():,}곳")
old = d[d["지정후_개월"] >= 2]
print(f"  나머지 {len(old):,}곳 · 중앙값 {old['ratio'].median():.2f} · 20명 초과 {(old['ratio'] > 20).sum():,}곳")
