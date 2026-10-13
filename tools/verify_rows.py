"""이상치 기관의 원본 행 전체를 꺼내 본다.
가설: 주야간보호(B03/C03) 행의 요양보호사가 1명인 것은, 그 기관의 인력이
      같은 기관코드의 다른 유형 행(방문요양 등)에 기록돼 있기 때문일 수 있다.
"""
import sys
import pandas as pd

path = sys.argv[1]
names = sys.argv[2:]

KEY = "장기요양기관코드"
xl = pd.ExcelFile(path)
gen = pd.read_excel(xl, "일반현황")
cap = pd.read_excel(xl, "입소인원")
stf = pd.read_excel(xl, "인력현황")

for nm in names:
    hit = gen[gen["장기요양기관이름"].astype(str).str.strip() == nm]
    if hit.empty:
        print(f"[{nm}] 일반현황에서 못 찾음")
        continue
    for _, g in hit.iterrows():
        code = g[KEY]
        print("=" * 76)
        print(f"[{nm}]  기관코드 {code}")
        print(f"  주소     {g['시도 시군구 법정동명']} / {g['기관별 상세주소']}")
        print(f"  지정일자 {g['지정일자']}  설치신고 {g['설치신고일자']}")

        c = cap[cap[KEY] == code]
        print(f"  -- 입소인원 {len(c)}행")
        for _, r in c.iterrows():
            print(f"       {r['기관유형코드']:5} {str(r['기관유형명'])[:22]:24} 정원 {r['정원']}")

        s = stf[stf[KEY] == code]
        print(f"  -- 인력현황 {len(s)}행")
        for _, r in s.iterrows():
            tot = sum(pd.to_numeric(r[c2], errors="coerce") or 0 for c2 in
                      ["시설장", "사무국장", "사회복지사", "의사_전임", "의사_촉탁", "간호사",
                       "간호조무사", "치위생사", "물리치료사", "작업치료사", "요양보호사",
                       "영양사", "기타"])
            print(f"       {r['기관유형코드']:5} 요양보호사 {r['요양보호사']:>4}  간호 {r['간호사']:>3}/{r['간호조무사']:>3}  "
                  f"사복 {r['사회복지사']:>3}  총인원 {int(tot):>4}")
        print()
