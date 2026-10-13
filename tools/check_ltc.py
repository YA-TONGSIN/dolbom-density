import sys, pandas as pd

path = sys.argv[1]
xl = pd.ExcelFile(path)

gen = pd.read_excel(xl, "일반현황")
cap = pd.read_excel(xl, "입소인원")
stf = pd.read_excel(xl, "인력현황")
cod = pd.read_excel(xl, "기관유형코드 정의")

print("=" * 78)
print("[입소인원] 컬럼별 결측 점검")
for c in cap.columns:
    nn = cap[c].notna().sum()
    print(f"  {str(c)!r:28} 비어있지 않은 값 {nn:,} / {len(cap):,}")

print()
print("=" * 78)
print("[기관유형코드 정의] 전체")
for _, r in cod.iterrows():
    print(f"  {r.iloc[0]}  {r.iloc[1]}")

print()
print("=" * 78)
print("[입소인원] 기관유형별 건수 / 정원 결측")
g = cap.groupby(["기관유형코드", "기관유형명"]).agg(
    기관수=("장기요양기관코드", "count"),
    정원있음=("정원", lambda s: s.notna().sum()),
    정원평균=("정원", "mean"),
).reset_index().sort_values("기관수", ascending=False)
print(g.head(20).to_string(index=False))

print()
print("=" * 78)
print("[인력현황] 요양보호사 결측 / 분포")
print(f"  행수 {len(stf):,}")
print(f"  요양보호사 비결측 {stf['요양보호사'].notna().sum():,}")
print(f"  요양보호사 0명 {(stf['요양보호사'] == 0).sum():,}")
print(f"  간호사 1명 이상 {(stf['간호사'].fillna(0) > 0).sum():,}")
print(f"  간호조무사 1명 이상 {(stf['간호조무사'].fillna(0) > 0).sum():,}")

print()
print("=" * 78)
print("[조인 가능성] 장기요양기관코드 기준")
sg, sc, ss = set(gen["장기요양기관코드"]), set(cap["장기요양기관코드"]), set(stf["장기요양기관코드"])
print(f"  일반현황 {len(sg):,} / 입소인원 {len(sc):,} / 인력현황 {len(ss):,}")
print(f"  일반∩입소        {len(sg & sc):,}")
print(f"  일반∩입소∩인력   {len(sg & sc & ss):,}")

print()
print("=" * 78)
print("[일반현황] 시도 분포 상위")
print(gen["시도 시군구 법정동명"].astype(str).str.split().str[0].value_counts().head(20).to_string())
