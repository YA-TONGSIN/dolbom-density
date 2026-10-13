import sys, pandas as pd

path = sys.argv[1]
sido = sys.argv[2] if len(sys.argv) > 2 else "서울특별시"

xl = pd.ExcelFile(path)
gen = pd.read_excel(xl, "일반현황")
cap = pd.read_excel(xl, "입소인원")
stf = pd.read_excel(xl, "인력현황")

KEY = "장기요양기관코드"
gen["시도"] = gen["시도 시군구 법정동명"].astype(str).str.split().str[0]
gen["시군구"] = gen["시도 시군구 법정동명"].astype(str).str.split().str[1]

# 주야간보호만 (B03 재가노인복지시설, C03 재가장기요양기관)
day = cap[cap["기관유형코드"].isin(["B03", "C03"])][[KEY, "기관유형명", "정원"]]

# 인력현황도 (기관코드, 기관유형코드) 단위다. 기관코드만으로 조인하면
# 같은 기관의 방문요양 인력이 주야간보호에 붙어버린다.
day = cap[cap["기관유형코드"].isin(["B03", "C03"])][[KEY, "기관유형코드", "기관유형명", "정원"]]
stf_cols = [KEY, "기관유형코드", "요양보호사", "간호사", "간호조무사", "사회복지사", "물리치료사", "작업치료사"]

df = (day.merge(gen[[KEY, "장기요양기관이름", "시도", "시군구", "기관별 상세주소", "지정일자"]].drop_duplicates(KEY), on=KEY)
         .merge(stf[stf_cols].drop_duplicates([KEY, "기관유형코드"]),
                on=[KEY, "기관유형코드"], how="left"))

df = df[df["시도"] == sido].copy()
print(f"[{sido}] 주야간보호 기관 {len(df):,}곳")

for c in ["요양보호사", "간호사", "간호조무사", "사회복지사", "물리치료사", "작업치료사"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

print(f"  정원 결측        {df['정원'].isna().sum():,}")
print(f"  요양보호사 결측   {df['요양보호사'].isna().sum():,}")
print(f"  요양보호사 0명    {(df['요양보호사'] == 0).sum():,}")

d = df[(df["정원"].fillna(0) > 0) & (df["요양보호사"].fillna(0) > 0)].copy()
d["어르신당_요양보호사"] = (d["정원"] / d["요양보호사"]).round(2)
d["간호인력"] = (d["간호사"].fillna(0) + d["간호조무사"].fillna(0)).astype(int)
print(f"  → 순위 산출 가능   {len(d):,}곳  (정원·요양보호사 모두 있는 기관)")

print()
print(f"=== {sido} · 요양보호사 1인당 어르신 수가 적은 순 Top 10 ===")
top = d.sort_values(["어르신당_요양보호사", "정원"], ascending=[True, False]).head(10)
for i, (_, r) in enumerate(top.iterrows(), 1):
    nurse = f"간호인력 {r['간호인력']}명" if r["간호인력"] > 0 else "간호인력 없음"
    print(f"{i:2}. {r['장기요양기관이름'][:22]:24} 1인당 {r['어르신당_요양보호사']:5.2f}명 "
          f"(정원 {int(r['정원']):3} / 요양보호사 {int(r['요양보호사']):3})  {nurse}  {r['시군구']}")

print()
print("=== 분포 (전체 기관 기준) ===")
print(d["어르신당_요양보호사"].describe().round(2).to_string())
print()
print(f"간호인력 1명 이상 기관: {(d['간호인력'] > 0).sum():,} / {len(d):,} "
      f"({(d['간호인력'] > 0).mean() * 100:.1f}%)")
