"""경쟁 분석용 — 공단 평가등급의 변별력을 실제로 확인한다.
※ 이 데이터는 서비스에 사용하지 않는다. 기획서의 '기존 대안' 분석 근거일 뿐이다.
"""
import sys
import pandas as pd

path = sys.argv[1]
df = None
for enc in ("cp949", "utf-8-sig", "utf-8"):
    try:
        df = pd.read_csv(path, encoding=enc)
        print(f"인코딩 {enc} · {len(df):,}행 · {len(df.columns)}열")
        break
    except Exception as e:
        print(f"  {enc} 실패: {str(e)[:60]}")
if df is None:
    sys.exit(1)

print("컬럼:", list(df.columns))
print()

# 등급 컬럼 찾기
gcol = next((c for c in df.columns if "등급" in str(c)), None)
ycol = next((c for c in df.columns if "연도" in str(c) or "년도" in str(c)), None)
kcol = next((c for c in df.columns if "급여" in str(c) and "종류" in str(c)), None)
print(f"등급 컬럼={gcol}  연도={ycol}  급여종류={kcol}")
print()

if gcol:
    print("=" * 60)
    print("전체 등급 분포")
    vc = df[gcol].value_counts(dropna=False)
    tot = len(df)
    for k, v in vc.items():
        print(f"  {str(k):>8}  {v:>7,}  ({v/tot*100:>5.1f}%)")

    if ycol:
        print()
        print("=" * 60)
        print("최근 연도 분포")
        last = df[ycol].max()
        sub = df[df[ycol] == last]
        print(f"  연도 {last} · {len(sub):,}건")
        for k, v in sub[gcol].value_counts().items():
            print(f"    {str(k):>8}  {v:>7,}  ({v/len(sub)*100:>5.1f}%)")

    if kcol:
        print()
        print("=" * 60)
        print("주야간보호만")
        day = df[df[kcol].astype(str).str.contains("주야간", na=False)]
        print(f"  {len(day):,}건")
        if len(day):
            if ycol:
                last = day[ycol].max()
                day = day[day[ycol] == last]
                print(f"  최근 평가연도 {last} · {len(day):,}건")
            for k, v in day[gcol].value_counts().items():
                print(f"    {str(k):>8}  {v:>7,}  ({v/len(day)*100:>5.1f}%)")
