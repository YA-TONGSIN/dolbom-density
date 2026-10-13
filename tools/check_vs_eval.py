"""경쟁 분석 — 공단 평가등급과 '요양보호사 1인당 어르신 수'가 같은 정보인가?
같은 정보라면 이 서비스는 평가등급의 열화판이다. 실제로 확인한다.
※ 평가 데이터는 서비스에 사용하지 않는다. 분석 근거용이다.
"""
import sys, json
import pandas as pd

ev_path, json_path, xlsx_path = sys.argv[1], sys.argv[2], sys.argv[3]

ev = pd.read_csv(ev_path, encoding="cp949")
ev = ev[ev["급여종류"].astype(str).str.contains("주야간", na=False)].copy()
# CSV는 엑셀 텍스트 보호용 작은따옴표 + 하이픈 형식: '1-11560-00018'
# XLSX는 하이픈 없는 11자리 정수: 11156000018
ev["code"] = (ev["장기요양기관기호"].astype(str)
              .str.strip().str.strip("'").str.replace("-", "", regex=False))
ev["평가일자"] = pd.to_datetime(ev["평가일자"].astype(str), errors="coerce")
print(f"평가 데이터(주야간보호) {len(ev):,}건")
print(f"  평가일자 범위 {ev['평가일자'].min():%Y-%m-%d} ~ {ev['평가일자'].max():%Y-%m-%d}")
# 기관별 최신 평가만
ev = ev.sort_values("평가일자").drop_duplicates("code", keep="last")
print(f"  기관 단위 최신 평가 {len(ev):,}곳")
print()

# 서비스 데이터 재구성 (기관코드 포함)
KEY = "장기요양기관코드"
xl = pd.ExcelFile(xlsx_path)
gen = pd.read_excel(xl, "일반현황")
cap = pd.read_excel(xl, "입소인원")
stf = pd.read_excel(xl, "인력현황")
day = cap[cap["기관유형코드"].isin(["B03", "C03"])][[KEY, "기관유형코드", "정원"]]
d = (day.merge(gen[[KEY, "장기요양기관이름"]].drop_duplicates(KEY), on=KEY)
        .merge(stf[[KEY, "기관유형코드", "요양보호사"]].drop_duplicates([KEY, "기관유형코드"]),
               on=[KEY, "기관유형코드"], how="left"))
for c in ["정원", "요양보호사"]:
    d[c] = pd.to_numeric(d[c], errors="coerce")
d = d[(d["정원"] > 0) & (d["요양보호사"] > 0)].copy()
d["ratio"] = d["정원"] / d["요양보호사"]
d = d.sort_values("ratio").drop_duplicates(KEY, keep="first")
d["code"] = d[KEY].astype(str).str.strip()
print(f"서비스 데이터 {len(d):,}곳")

m = d.merge(ev[["code", "평가등급", "평가총점"]], on="code", how="inner")
print(f"매칭 {len(m):,}곳 ({len(m)/len(d)*100:.1f}%)")
print()

print("=" * 66)
print("평가등급별 '요양보호사 1인당 어르신 수'")
print(f"{'등급':>5} {'기관수':>7} {'중앙값':>9} {'평균':>9}")
for g in ["A", "B", "C", "D", "E"]:
    s = m[m["평가등급"] == g]["ratio"]
    if len(s):
        print(f"{g:>5} {len(s):>7,} {s.median():>9.2f} {s.mean():>9.2f}")

print()
print("=" * 66)
score = pd.to_numeric(m["평가총점"], errors="coerce")
valid = m["ratio"].notna() & score.notna()
print(f"평가총점 ↔ 1인당 수치  피어슨 상관계수 = {m.loc[valid,'ratio'].corr(score[valid]):.3f}")
print(f"                      순위상관(랭크 피어슨) = {m.loc[valid,'ratio'].rank().corr(score[valid].rank()):.3f}")

print()
print("=" * 66)
print("A등급 기관 안에서도 1인당 수치가 갈리는가")
a = m[m["평가등급"] == "A"]["ratio"]
if len(a):
    print(f"  A등급 {len(a):,}곳 · 최소 {a.min():.2f} · 25% {a.quantile(.25):.2f} · "
          f"중앙 {a.median():.2f} · 75% {a.quantile(.75):.2f} · 최대 {a.max():.2f}")
e = m[m["평가등급"].isin(["D", "E"])]["ratio"]
if len(e):
    print(f"  D·E등급 {len(e):,}곳 · 중앙 {e.median():.2f}")
print()
good = m[(m["평가등급"] == "A") & (m["ratio"] > m["ratio"].median())]
print(f"  A등급인데 1인당 수치가 전체 중앙값보다 나쁜 기관: {len(good):,}곳 "
      f"(A등급의 {len(good)/max(len(a),1)*100:.1f}%)")
bad = m[(m["평가등급"].isin(["D", "E"])) & (m["ratio"] < m["ratio"].median())]
print(f"  D·E등급인데 1인당 수치가 전체 중앙값보다 좋은 기관: {len(bad):,}곳 "
      f"(D·E등급의 {len(bad)/max(len(e),1)*100:.1f}%)")
