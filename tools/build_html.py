"""data/day_care.json -> 자체완결 HTML 1개.

실행:  python tools/build_html.py data/day_care.json dist/돌봄밀도.html
서버·네트워크 없이 더블클릭으로 열린다.
"""
import sys, json, os

src = sys.argv[1] if len(sys.argv) > 1 else "data/day_care.json"
out = sys.argv[2] if len(sys.argv) > 2 else "dist/돌봄밀도.html"

# ── 법정 수가 (주야간보호 급여비용) ─────────────────────────────────────────
# 주야간보호 비용은 기관마다 다르지 않고 공단이 고시하는 전국 공통 수가다.
# 따라서 원본 데이터(15124763)에 금액 칸이 없어도 등급·이용시간만 고르면 계산된다.
#
# ※ 표가 비어 있으면 화면에 비용 UI가 아예 나오지 않는다(틀린 금액을 보여주지 않기 위해).
#    공단 > 제도안내 > 급여비용 의 "주야간보호" 1일당 금액을 그대로 옮겨 적을 것.
# 쓰는 값: 등급별 "재가급여 이용 월 한도액". 주야간보호 1일당 수가표가 아니라
# 한 달에 쓸 수 있는 급여 총액의 상한이다. 기관마다 다르지 않고 등급으로만 정해진다.
#
# 검산(표 내부 정합성): 2026÷2025 = 8.95 / 11.89 / 2.86 / 2.85 / 2.71 / 2.88% — 표에 적힌 인상률과 일치.
# 교차검증: 2025년 1등급 2,306,400원이 별도 출처(infopolicy.co.kr)와 일치.
YEAR = "2026"   # "2025" 로 바꾸면 그 해 한도액으로 계산된다
FEE = {
    "source": "보건복지부·국민건강보험공단 — 등급별 재가급여 이용 월 한도액",
    "asOf": YEAR + "년 기준",
    "copayRate": 0.15,   # 일반 대상 본인부담률 15% (감경 대상은 다름 → 화면에 명시)
    "limits": {
        "2026": {"1등급": 2512900, "2등급": 2331200, "3등급": 1528200,
                 "4등급": 1409700, "5등급": 1208900, "인지지원등급": 676320},
        "2025": {"1등급": 2306400, "2등급": 2083400, "3등급": 1485700,
                 "4등급": 1370600, "5등급": 1177000, "인지지원등급": 657400},
    }[YEAR],
}

with open(src, encoding="utf-8") as f:
    data = json.load(f)

data["fee"] = FEE if (FEE["asOf"] and FEE["limits"]) else None
payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>주야간보호센터 돌봄 밀도 비교 — 요양보호사 1인당 어르신 수로 전국 비교</title>
<meta name="description" content="부모님 동네 주야간보호센터를 요양보호사 1인당 어르신 수로 비교합니다. 공공데이터 2종(국민건강보험공단 장기요양기관 시설별 현황 + 평가 결과), 전국 __COUNT__곳, 공단 평가등급과 나란히 표시.">
<meta property="og:title" content="주야간보호센터 돌봄 밀도 비교">
<meta property="og:description" content="공단 평가등급은 알려주지 않는 숫자 — 요양보호사 한 명이 어르신 몇 분을 돌보는지로 전국 주야간보호센터를 비교합니다.">
<meta property="og:type" content="website">
<meta name="theme-color" content="#0a6b5c">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230a6b5c'/%3E%3Ctext x='32' y='45' font-size='34' font-family='Malgun Gothic,sans-serif' font-weight='700' fill='%23fff' text-anchor='middle'%3E%EB%8F%8C%3C/text%3E%3C/svg%3E">
<style>
  /* ===== 디자인 토큰 =============================================
     색   : 흰 배경 · 짙은 남색 글자 · 틸 강조 1색 (3색 원칙 유지).
            나머지는 새 색이 아니라 같은 계열의 농도 단계다.
     크기 : 황금비 1.618. 본문 17 → 27 → 44, 아래로 17÷1.618 ≈ 11.
     여백 : 피보나치 5·8·13·21·34·55 (황금비의 정수 근사).
     ============================================================== */
  /* 토스·당근 계열 소비자 앱 문법: 연회색 바탕 위 흰 카드, 테두리 대신 여백과 그림자로 구분 */
  :root{
    /* Claude Design 1차 시안(10-13) 팔레트 — 따뜻한 크림 중립색. 색상은 여전히 흰/검정/틸 셋 */
    --ink:#1b2220;         /* 글자 — 거의 검정(녹색기) */
    --mute:#5e5850;        /* 보조 글자 — 따뜻한 회갈색, 크림 바탕 대비 6.5:1 */
    --accent:#0a6b5c;      /* 강조 1색 — 틸 (브랜드색 하나) */
    --accent-deep:#07564a; /* 강조색 짙은 단계 (호버) */
    --accent-wash:#e3f0ea; /* 강조색 가장 옅은 단계 (배지) */
    --on-accent:#ffffff;   /* 강조색 위에 올리는 글자 */
    --bg:#fbf7f0;          /* 페이지 바탕 — 크림 */
    --card:#ffffff;        /* 카드 */
    --field:#ffffff;       /* 입력창 — 흰 바탕에 따뜻한 테두리 */
    --soft:#f0eae2;        /* 면 (안내 상자·중립 배지) */
    --line:#e6ddcf;        /* 구분선·입력 테두리 — 크림보다 한 단계 짙게 */
    --hair:rgba(27,34,32,.06);  /* 카드 테두리 */
    --track:#c9d0cd;            /* 토글 꺼짐·막대 트랙 */
    --ph:#9a938a;               /* 입력 안내문 */
    /* 층위 있는 그림자 — 따뜻한 그림자색 */
    --shadow:0 1px 2px rgba(60,48,30,.05), 0 2px 10px rgba(60,48,30,.06);
    --shadow-lift:0 2px 4px rgba(60,48,30,.05), 0 10px 28px rgba(60,48,30,.10);
    --t-fast:.15s cubic-bezier(.2,.8,.2,1);   /* 상태 전환 (장식 아님) */

    /* 가독성 바닥: 화면에 보이는 UI 글자는 15px 아래로 내려가지 않는다 (사용자 50대). 13은 푸터용 */
    --t-xs:13px; --t-sm:15px; --t-base:17px; --t-md:21px; --t-lg:27px; --t-xl:44px;
    --s1:5px; --s2:8px; --s3:13px; --s4:21px; --s5:34px; --s6:55px;
    --r:20px; --r-sm:14px;  /* 둥근 모서리 — 카드 20, 입력·버튼 14 */
  }

  /* 다크 모드 — 기기 설정을 따른다. 순검정이 아니라 남색기 도는 짙은 회색.
     color-scheme 을 선언해야 브라우저가 자체 자동 반전을 멈추고 셀렉트·스크롤바도 함께 어두워진다 */
  :root{color-scheme:light dark}
  @media (prefers-color-scheme:dark){
    :root{
      --ink:#f3efe8; --mute:#b6aea3;
      /* 밝은 틸 위에는 흰 글자 대비가 모자라 어두운 글자를 쓴다 */
      --accent:#5cc4b0; --accent-deep:#4fb39f; --accent-wash:#15241f; --on-accent:#0f1a17;
      --bg:#171513; --card:#221f1b; --field:#2a2622; --soft:#2a2622;
      --line:#3b3530; --hair:rgba(255,255,255,.05);
      --track:#3b3530; --ph:#7d766c;
      --shadow:0 1px 2px rgba(0,0,0,.3), 0 2px 10px rgba(0,0,0,.25);
      --shadow-lift:0 2px 4px rgba(0,0,0,.3), 0 10px 28px rgba(0,0,0,.35);
    }
  }

  /* 움직임에 민감한 사람에게는 전환 제거 */
  @media (prefers-reduced-motion:reduce){ *{transition:none !important} }
  *{box-sizing:border-box}
  html,body{margin:0;padding:0}
  /* 세로 리듬은 그리드 gap 하나로만 만든다 — 요소 기본 마진은 전부 제거 */
  p,h1,h2,h3,ol,ul,figure,blockquote{margin:0}
  body{
    background:var(--bg); color:var(--ink);
    font-family:"Pretendard Variable",Pretendard,-apple-system,"Apple SD Gothic Neo",
                "Malgun Gothic","맑은 고딕",system-ui,sans-serif;
    font-size:var(--t-base); line-height:1.55;
    -webkit-text-size-adjust:100%;
  }

  /* 전체 세로 리듬을 그리드 gap 하나로 통제한다 (요소별 margin 사용 안 함) */
  /* 폭 1180 — 데스크톱에서 카드를 3열로 놓기 위해 (시안 1c) */
  .wrap{
    max-width:1180px;margin:0 auto;padding:var(--s4) var(--s3) var(--s6);
    display:grid;grid-template-columns:minmax(0,1fr);row-gap:var(--s4);
    overflow-wrap:anywhere;
  }
  .wrap>*{margin:0}

  .head{display:grid;row-gap:var(--s2);padding:var(--s2) var(--s1) 0}
  /* 섹션 라벨 — 점 하나로 시작하는 현대적 메타 표기 */
  .eyebrow{font-size:var(--t-xs);color:var(--mute);font-weight:700;letter-spacing:.01em;
           display:flex;align-items:center;gap:7px}
  .eyebrow::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--accent);flex:0 0 auto}
  h1{font-size:30px;letter-spacing:-0.035em;line-height:1.22;font-weight:800}
  .lede{font-size:var(--t-base);color:var(--mute);line-height:1.5}

  /* 입력 영역 — 카드. 그림자 + 머리카락 테두리로 가장자리를 또렷하게 */
  .panel{
    background:var(--card);border-radius:var(--r);box-shadow:var(--shadow);border:1px solid var(--hair);
    padding:var(--s4);display:grid;row-gap:var(--s3);
  }
  /* 시·도 / 시·군·구 / 기관명 — 넓으면 한 줄 3칸, 좁으면 세로 (시안 1c) */
  .pick{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:var(--s3)}
  .pick label,.find label{display:grid;row-gap:var(--s1);min-width:0}
  .pick span,.find span{font-size:var(--t-sm);color:var(--ink);font-weight:700}
  /* 입력창 — 회색 채움, 테두리 없음 (토스 문법) */
  select,.find input{
    width:100%;padding:15px 16px;font-size:var(--t-base);font-family:inherit;font-weight:600;
    color:var(--ink);background:var(--field);border:1.5px solid var(--line);border-radius:var(--r-sm);
    transition:background var(--t-fast),border-color var(--t-fast);
  }
  .find input::placeholder{color:var(--ph);font-weight:400}
  select:focus,.find input:focus{outline:none;background:var(--card);border-color:var(--accent)}
  .find{display:grid}

  .opts{display:grid;grid-template-columns:1fr auto;gap:var(--s2) var(--s3);align-items:center;font-size:var(--t-base)}
  /* 토글은 한 덩어리 — 공유 버튼과 섞이지 않게 */
  .toggles{display:grid;row-gap:var(--s2);min-width:0}
  .opts label{display:flex;align-items:center;gap:11px;cursor:pointer;font-weight:600}
  /* 토글 스위치 — 체크박스를 그대로 쓰되 모양만 바꾼다 (접근성·키보드 유지) */
  .opts input[type=checkbox]{
    appearance:none;-webkit-appearance:none;margin:0;flex:0 0 auto;
    width:46px;height:28px;border-radius:999px;background:var(--track);
    position:relative;cursor:pointer;transition:background var(--t-fast);
  }
  .opts input[type=checkbox]::after{
    content:"";position:absolute;top:3px;left:3px;width:22px;height:22px;border-radius:50%;
    background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.22);transition:transform var(--t-fast);
  }
  .opts input[type=checkbox]:checked{background:var(--accent)}
  .opts input[type=checkbox]:checked::after{transform:translateX(18px)}
  .opts input[type=checkbox]:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
  button.share{
    padding:11px 16px;font-size:var(--t-sm);font-family:inherit;font-weight:700;
    color:var(--ink);background:var(--soft);border:1px solid var(--line);
    border-radius:999px;cursor:pointer;white-space:nowrap;transition:background var(--t-fast);
  }
  button.share:hover{background:var(--line)}
  button.share:active{transform:scale(.97)}

  /* 지역 기준선 — 떠 있는 흰 카드, 스크롤해도 남는다. 중간값 수치는 화면에서 여기 한 곳에만 */
  .bar{
    position:sticky;top:var(--s2);z-index:5;
    padding:var(--s3) var(--s4);border-radius:var(--r-sm);
    background:var(--card);box-shadow:var(--shadow-lift);border:1px solid var(--hair);
    font-size:var(--t-base);line-height:1.5;backdrop-filter:saturate(1.2);
  }
  .bar b{font-size:19px;font-weight:800}
  .bar small.hint{display:block;margin-top:4px;font-size:var(--t-xs);color:var(--mute);font-weight:400;line-height:1.45}
  .bar small.fee{display:block;margin-top:10px;padding-top:10px;border-top:1px solid var(--line);
                 font-size:var(--t-sm);color:var(--mute);font-weight:400;line-height:1.5}
  .bar small.fee b{color:var(--ink);font-weight:700}
  /* 설명은 접어 둔다 — sticky 바가 커지면 스크롤 내내 목록을 가린다 */
  .bar details.feenote{margin-top:6px}
  .bar details.feenote summary{cursor:pointer;font-weight:700;color:var(--accent-deep);
                               list-style:none;display:inline-flex;gap:5px;align-items:center}
  .bar details.feenote summary::-webkit-details-marker{display:none}
  .bar details.feenote summary::before{content:"ⓘ"}
  .bar details.feenote[open]{padding-top:6px}

  /* 결과 — 카드 하나가 기관 하나. 넓으면 3열, 중간 2열, 휴대폰 1열 (시안 1c) */
  ol{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:var(--s3)}
  li{
    background:var(--card);border-radius:var(--r);box-shadow:var(--shadow);border:1px solid var(--hair);
    padding:var(--s4);transition:box-shadow var(--t-fast),transform var(--t-fast);
  }
  li:hover{box-shadow:var(--shadow-lift);transform:translateY(-1px)}

  /* 카드 안 구성(시안): N위 + 기관명 → 주소 → "요양보호사 1명이 돌보는 어르신" → 큰 숫자 → 근거 → 막대 → 배지 → 인력 → 행동 */
  /* 카드 안은 평평한 10행 그리드. 서브그리드를 쓰면 같은 줄 카드끼리
     이름·주소·숫자·막대 행 높이가 전부 맞아 떨어진다 (주소가 두 줄인 카드가 섞여도) */
  li{display:grid;grid-template-rows:repeat(10,auto);row-gap:8px}
  li>.act{margin-top:auto}
  @supports (grid-template-rows:subgrid){
    ol{grid-auto-rows:auto}
    li{grid-row:span 10;grid-template-rows:subgrid}
    li>.act{margin-top:0}
  }
  .rank{font-size:var(--t-sm);font-weight:800;color:var(--mute);font-variant-numeric:tabular-nums;
        white-space:nowrap;margin-right:7px}
  /* 상위 3곳만 순위를 틸 알약으로. 왕관·금은동 대신 이 방법을 쓰는 이유:
     ① 새 색이 늘지 않는다(기존 --accent) ② 아이콘이 늘지 않는다
     ③ 1인당 숫자가 여전히 가장 커서 "강조는 하나" 규칙이 안 깨진다
     ④ 왕관은 "여기가 최고"로 읽혀 하단의 "품질을 보증하지 않는다" 고지와 부딪친다.
        실제로 관악구 1위는 공단 평가 C등급이다. 상위 3곳이라는 '사실'만 말한다. */
  .rank.top{
    display:inline-block;padding:3px 10px;border-radius:999px;margin-right:9px;
    background:var(--accent);color:var(--on-accent);font-weight:800;
  }
  .name{font-size:var(--t-md);font-weight:700;word-break:keep-all;line-height:1.3;align-self:start}
  /* 빈 슬롯도 숨기지 않는다 — 숨기면 그 카드만 행이 하나 줄어 버튼이 다시 어긋난다 */
  .where{font-size:var(--t-sm);color:var(--mute);word-break:keep-all;line-height:1.5}
  /* 주소 줄 끝에 전화번호. 새 행을 만들지 않는다 — 카드가 서브그리드 10행으로 묶여 있어
     행을 늘리면 3열에서 카드끼리 높이가 어긋난다. */
  .where .telno{color:var(--ink);font-weight:700;white-space:nowrap}
  .cap{font-size:var(--t-sm);color:var(--mute);margin-top:4px}

  .big{display:flex;align-items:baseline;gap:6px}
  .num{font-size:44px;font-weight:800;line-height:1;font-variant-numeric:tabular-nums;letter-spacing:-0.045em}
  .num.good{color:var(--accent)}
  .unit{font-size:var(--t-base);color:var(--ink);font-weight:700}
  .calc{font-size:var(--t-sm);color:var(--mute)}

  /* 판정 배지 — 채움형 알약. 중간값 수치는 위 기준선에 있으므로 여기선 방향만 */
  /* 판정 배지. 바탕을 --field(흰색)로 두면 카드와 같은 색이라
     "중간값보다 많습니다"만 알약이 안 보이고 맨 글자로 읽힌다.
     유리한 판정만 알약이고 불리한 판정은 아닌 건 공정하지 않다 → --soft 로 채운다. */
  .chip{
    display:inline-block;padding:7px 14px;border-radius:999px;
    font-size:var(--t-sm);font-weight:700;line-height:1.3;
    background:var(--soft);color:var(--ink);
  }
  .chip.good{background:var(--accent-wash);color:var(--accent-deep)}
  .chip.near{background:var(--ink);color:var(--card);margin-left:6px}   /* 내 동네 표식 — 검정 알약 */
  /* 공단 평가등급 — 2종째 데이터. 우리 숫자(틸)와 섞이지 않게 테두리형 중립 배지로 둔다.
     등급은 공단이 매긴 값이고 우리 지표가 아니다. 색으로 서열을 매기지 않는다. */
  .chip.gr{background:transparent;border:1.5px solid var(--line);color:var(--mute);font-weight:700}
  .chip.gr b{color:var(--ink);font-weight:800}
  .chip.gr.none{border-style:dashed}
  .verdict{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
  @media (prefers-color-scheme:dark){ .chip.good{color:#5fd3b8} }  /* 어두운 바탕에서 배지 글자 대비 확보 */

  /* 두 데이터를 겹쳐야만 나오는 한 문장 — 이 서비스가 존재하는 이유 */
  .insight{
    padding:var(--s3) 15px;border-radius:var(--r-sm);
    background:var(--accent-wash);color:var(--ink);
    font-size:var(--t-sm);line-height:1.6;border:1px solid var(--hair);
  }
  .insight b{font-weight:800;color:var(--accent-deep)}
  @media (prefers-color-scheme:dark){ .insight b{color:#7fd9c6} }

  /* 넓은 화면 — 카드가 3열로 서므로 카드 안은 세로 쌓기 유지. 숫자만 조금 더 크게 */
  @media (min-width:900px){
    .num{font-size:48px}
  }

  /* 중간값 대비 막대 — 가운데 눈금이 해당 시·도 중간값. 수치는 안 적고 "중간값" 한 단어만 */
  .meter{max-width:420px;display:grid;row-gap:4px}
  .meter .track{position:relative;height:10px;background:var(--field);border-radius:999px}
  .meter .fill{height:100%;border-radius:999px;background:var(--mute)}
  .meter .fill.good{background:var(--accent)}
  .meter .tick{position:absolute;left:50%;top:-6px;bottom:-6px;width:2px;background:var(--ink);border-radius:1px}
  .meter .lab{display:grid;grid-template-columns:1fr auto 1fr;font-size:var(--t-xs);color:var(--mute)}
  .meter .lab span:nth-child(2){justify-self:center;font-weight:700;color:var(--mute)}
  .meter .lab span:last-child{justify-self:end}

  .tags{font-size:var(--t-sm);color:var(--mute);line-height:1.5}
  .tags i{font-style:normal;color:var(--ink)}
  .tags b{font-weight:700;color:var(--mute);margin-right:6px}

  /* 개원 1년 미만 안내 — 접힌 한 줄(summary), 누르면 전문 */
  .new{font-size:var(--t-sm);border-radius:var(--r-sm);background:var(--soft);color:var(--ink);line-height:1.55}
  .new summary{padding:10px 13px;cursor:pointer;font-weight:700;list-style:none;display:flex;gap:8px;align-items:flex-start}
  .new summary::-webkit-details-marker{display:none}
  .new summary::before{content:"ⓘ";flex:0 0 auto;color:var(--mute)}
  .new[open] summary::before{content:"ⓘ"}
  .new p{padding:0 13px 12px 36px;color:var(--mute);line-height:1.65}
  .new b{font-weight:700;color:var(--ink)}

  /* 행동 — 전화 안내 아이콘 · 검색하기 · 주소 복사 한 줄, 그 아래 공단 링크 */
  .act{display:grid;row-gap:var(--s2);justify-items:stretch;padding-top:var(--s1)}
  .btns{display:grid;grid-template-columns:auto 1fr auto;gap:var(--s2);align-items:stretch}
  .act a.go{text-align:center}

  /* 전화 아이콘 — 번호를 띄우는 게 아니라 "왜 번호가 없는지"를 알려준다 */
  .tel{position:relative;display:grid;place-items:center;width:52px;border-radius:var(--r-sm);
       background:var(--soft);color:var(--mute);cursor:help;transition:background var(--t-fast),color var(--t-fast)}
  .tel:hover,.tel:focus-visible{background:var(--accent-wash);color:var(--accent-deep);outline:none}
  /* 번호를 받은 기관은 아이콘이 실제 통화 링크가 된다(휴대폰에서 탭하면 바로 발신).
     틸을 쓰는 건 '좋음'이 아니라 '행동'이라는 뜻 — 검색하기 버튼과 같은 규칙이다. */
  a.tel{text-decoration:none;cursor:pointer;background:var(--accent-wash);color:var(--accent-deep)}
  a.tel:hover,a.tel:focus-visible{background:var(--accent);color:var(--on-accent)}
  /* 말풍선은 아이콘 왼쪽 끝에 맞춰 오른쪽으로 편다.
     가운데 정렬하면 첫 열 카드에서 화면 밖으로 잘린다. */
  .tel .tip{
    position:absolute;bottom:calc(100% + 9px);left:0;transform:translateY(4px);
    width:max-content;max-width:230px;padding:10px 13px;border-radius:var(--r-sm);
    background:var(--ink);color:var(--card);font-size:var(--t-xs);font-weight:500;line-height:1.5;
    text-align:left;opacity:0;visibility:hidden;pointer-events:none;z-index:20;
    transition:opacity var(--t-fast),transform var(--t-fast),visibility var(--t-fast);
  }
  .tel .tip::after{content:"";position:absolute;top:100%;left:20px;
                   border:6px solid transparent;border-top-color:var(--ink)}
  .tel .tip b{color:var(--card)}
  .tel:hover .tip,.tel:focus-visible .tip{opacity:1;visibility:visible;transform:translateY(0)}

  button.copy{
    padding:0 var(--s4);font-size:var(--t-sm);font-family:inherit;font-weight:700;white-space:nowrap;
    color:var(--ink);background:var(--soft);border:1px solid var(--line);border-radius:var(--r-sm);
    cursor:pointer;transition:background var(--t-fast),color var(--t-fast);
  }
  button.copy:hover{background:var(--line)}
  button.copy.done{background:var(--accent-wash);color:var(--accent-deep);border-color:#cfe3dd}

  a.go{
    display:inline-block;padding:15px 24px;font-size:var(--t-base);font-weight:700;
    color:var(--on-accent);background:var(--accent);border-radius:var(--r-sm);text-decoration:none;
    transition:background var(--t-fast),transform var(--t-fast);
  }
  a.go:hover{background:var(--accent-deep)}
  a.go:active{transform:scale(.98)}
  a.portal{font-size:var(--t-sm);color:var(--mute);font-weight:600;text-decoration:none;word-break:keep-all}
  a.portal::after{content:" ›";font-weight:800}
  a.portal:hover{color:var(--accent-deep)}

  .more{
    width:100%;padding:16px;font-size:var(--t-base);font-family:inherit;font-weight:700;
    color:var(--ink);background:var(--card);border:1px solid var(--hair);box-shadow:var(--shadow);
    border-radius:var(--r-sm);cursor:pointer;transition:box-shadow var(--t-fast),transform var(--t-fast);
  }
  .more:hover{box-shadow:var(--shadow-lift)}
  .more:active{transform:scale(.99)}
  [hidden]{display:none !important}
  .empty{padding:var(--s5) 0;color:var(--mute);text-align:center;box-shadow:none;background:transparent}

  footer{padding:var(--s3) var(--s1) 0;font-size:14px;color:var(--mute);line-height:1.7;display:grid;row-gap:2px}
  footer b{color:var(--ink)}
  .warn{margin-top:var(--s2);padding:var(--s3) 15px;background:var(--card);border:1px solid var(--hair);border-radius:var(--r-sm);line-height:1.7;font-size:var(--t-sm);box-shadow:var(--shadow)}

  @media (max-width:480px){
    .wrap{padding:var(--s3) var(--s3) var(--s5);row-gap:var(--s3)}
    .pick{grid-template-columns:1fr;gap:var(--s2)}
    h1{font-size:23px}
    .num{font-size:34px}
    /* width/height는 순위가 '원'이던 시절의 잔재다. 지금은 "N위" 글자라
       고정 크기를 주면 inline-block인 .rank.top에서 글자가 잘린다. 내용 크기를 따른다. */
    .rank{font-size:13px}
    .rank.top{padding:2px 9px}
    li{padding:var(--s3) 15px}
    .panel{padding:var(--s3) 15px}
    .opts{grid-template-columns:1fr}
    a.go,button.share{width:100%;text-align:center}
    .act{justify-items:stretch}
    a.portal{text-align:center}
    .tel{width:48px}
    button.copy{padding:0 var(--s3)}
  }
</style>
</head>
<body>
<div class="wrap">

  <header class="head">
    <p class="eyebrow">공공데이터 2종 · 전국 __COUNT__곳</p>
    <h1>주야간보호센터 돌봄 밀도 비교</h1>
    <p class="lede">요양보호사 한 명이 어르신 몇 분을 돌보는지로 비교합니다. 숫자가 적을수록 한 분께 더 많은 손길이 갑니다.</p>
    <p class="insight">공단 평가 <b>A등급</b>을 받은 __GAPBASE__곳 가운데 <b>__GAPCOUNT__곳(__GAPPCT__%)</b>은
      요양보호사 1인당 어르신 수가 전국 중간값보다 많습니다. 등급과 이 숫자는 거의 따로 움직입니다
      (평가총점과의 상관계수 __CORR__). <b>등급만 보고 고르면 놓치는 숫자</b>라서, 두 가지를 나란히 놓았습니다.</p>
  </header>

  <div class="panel">
  <div class="pick">
    <label><span>시 · 도</span>
      <select id="sido"><option value="">선택하세요</option></select>
    </label>
    <label><span>시 · 군 · 구</span>
      <select id="sgg"><option value="">전체</option></select>
    </label>
    <label id="dongwrap" hidden><span>읍면동 — 내 동네 먼저 (선택)</span>
      <select id="dong"><option value="">선택 안 함</option></select>
    </label>
    <label class="find"><span>기관명으로 찾기 (선택)</span>
      <input id="q" type="search" placeholder="예: 효사랑 · 비워두면 전체" autocomplete="off">
    </label>
  </div>

  <!-- 걸러보기 토글은 한 묶음으로 둔다. 공유 버튼이 토글 사이에 끼면
       "고르는 것"과 "내보내는 것"이 섞여 읽힌다 (좁은 화면에서 특히). -->
  <div class="opts">
    <div class="toggles">
      <label><input id="only" type="checkbox"> 중간값보다 적은 곳만</label>
      <label><input id="onlyab" type="checkbox"> 공단 평가 A·B등급만</label>
      <label id="feeopts" hidden><input id="feeon" type="checkbox"> 비용 함께 보기</label>
    </div>
    <button id="share" class="share" type="button" hidden>이 결과 링크 복사</button>
  </div>
  <div class="pick" id="feepick" hidden>
    <label><span>부모님 장기요양 등급</span><select id="grade"></select></label>
  </div>
  </div>

  <div id="bar" class="bar">부모님이 계신 지역을 선택하세요.</div>

  <ol id="list"></ol>
  <button id="more" class="more" hidden>나머지 전부 보기</button>

  <footer>
    <div><b>출처 ①</b> 공공데이터포털 · 국민건강보험공단_장기요양기관 시설별 현황 (데이터 __DATAID__)</div>
    <div><b>자료 기준일</b> __BASEDATE__ · <b>갱신 주기</b> __CYCLE__</div>
    <div><b>출처 ②</b> 공공데이터포털 · __SOURCE2__ (데이터 __DATAID2__) · 평가일자 __EVALRANGE__</div>
    <div><b>두 자료 연결</b> __JOINKEY__ · 등급이 붙은 곳 <b>__EVALMATCHED__곳(__EVALRATE__%)</b>, 나머지는 「평가 이력 없음」</div>
    <div><b>대상</b> __TYPES__ · 전국 <b>__COUNT__곳</b></div>
    <div><b>계산식</b> 요양보호사 1인당 어르신 수 = 정원 &divide; 요양보호사 수 (적을수록 앞)</div>
    <div><b>중간값 기준</b> __MEDIANNOTE__ (개원 __NEWCOUNT__곳 제외)</div>
    <div class="warn">
      이 숫자는 <b>돌봄 품질을 보증하지 않습니다.</b> 정원은 실제 이용 인원이 아니라 등록 가능한 최대 인원이고,
      요양보호사 수는 기관이 신고한 값입니다. <b>비교의 출발점</b>으로만 사용하시고,
      실제 선택 전에는 기관에 직접 확인하시기 바랍니다.
      <br><br>
      <b>개원 1년 미만 기관은 따로 표시했습니다.</b> 전국 자료로 확인해 보면 개원 2개월 미만 기관의
      1인당 어르신 수 중간값은 11.0명, 10년 이상 된 기관은 6.2명입니다.
      갓 문을 연 곳이 불리하게 보이는 것은 운영이 자리 잡는 중이기 때문이지 돌봄이 나쁘다는 뜻이 아닙니다.
      <br><br>
      <b>공단 평가등급은 __EVALRANGE__에 이뤄진 평가입니다.</b> 그 뒤에 바뀐 사정은 반영되어 있지 않고,
      아직 평가를 받지 않은 기관도 많아 __COUNT__곳 중 __EVALMATCHED__곳에만 등급이 있습니다.
      등급이 없는 것은 <b>나쁘다는 뜻이 아니라 자료가 없다는 뜻</b>입니다.
      두 자료는 기관코드로만 연결했고, 이름이나 주소가 비슷하다는 이유로 붙이지 않았습니다.
    </div>
  </footer>

</div>

<script>
const DATA = __PAYLOAD__;
const F = {}; DATA.fields.forEach((k,i)=>F[k]=i);
const ITEMS = DATA.items;
const MED = DATA.meta.sidoMedian;

const $sido = document.getElementById('sido');
const $sgg  = document.getElementById('sgg');
const $bar  = document.getElementById('bar');
const $list = document.getElementById('list');
const $more = document.getElementById('more');
const $q    = document.getElementById('q');
const $dong = document.getElementById('dong');
const $dongwrap = document.getElementById('dongwrap');
const FEE = DATA.fee || null;
const $feeopts=document.getElementById('feeopts'), $feeon=document.getElementById('feeon');
const $feepick=document.getElementById('feepick'), $grade=document.getElementById('grade');
const $only = document.getElementById('only');
const $onlyab = document.getElementById('onlyab');
const $share= document.getElementById('share');
const SAVE  = 'dolbom.pick';   // 마지막 선택 지역 (브라우저에만 저장)

DATA.sido.forEach((s,i)=>{
  const o=document.createElement('option'); o.value=String(i); o.textContent=s; $sido.appendChild(o);
});

let expanded=false, current=[];
const PAGE=10;

function fillSgg(){
  const v=$sido.value;
  $sgg.innerHTML='<option value="">전체</option>';
  if(v==='') return;
  (DATA.sigungu[DATA.sido[+v]]||[]).forEach(g=>{
    const o=document.createElement('option'); o.value=g; o.textContent=g; $sgg.appendChild(o);
  });
}

function fmt(n){ return Number(n).toFixed(1); }

/* ── 비용 ───────────────────────────────────────────────────────────────
   주야간보호 급여비용은 기관이 아니라 등급·이용시간으로 정해지는 전국 공통 수가라,
   기관마다 다르지 않다. 그래서 카드가 아니라 기준선 바 아래에 한 줄로 둔다.
   수가표가 없으면(빌드 설정이 비어 있으면) 이 기능 자체가 화면에 안 나온다. */
function initFee(){
  if(!FEE) return;
  Object.keys(FEE.limits).forEach(g=>{
    const o=document.createElement('option'); o.value=g; o.textContent=g; $grade.appendChild(o);
  });
  $grade.value='4등급';            // 주야간보호 이용이 가장 많은 등급
  $feeopts.hidden=false;
}
function feeLine(){
  if(!FEE || !$feeon.checked) return '';
  const limit=FEE.limits[$grade.value];
  if(!limit) return '';
  const copay=Math.round(limit*FEE.copayRate);
  // "약 211천원"은 회계 표기다. 50대 보호자가 쓰는 말은 "약 21만 원".
  const man = Math.round(copay/10000).toLocaleString();
  // 설명은 접어 둔다 — 이 블록은 sticky 바 안이라 펼쳐 두면 스크롤 내내 목록을 가린다.
  return '<small class="fee"><b>'+esc($grade.value)+'</b> 재가급여 월 한도 <b>'+limit.toLocaleString()+'원</b>'
    + ' · 한도를 다 쓰면 본인부담 <b>약 '+man+'만 원</b>'
    + '<details class="feenote"><summary>이 금액이 무엇인지</summary>'
    + '한 달에 쓸 수 있는 <b>상한</b>이고, 주야간보호·방문요양 등을 <b>합쳐서</b> 쓰는 금액입니다. '
    + '등급으로 정해지므로 <b>기관마다 같습니다</b>. 일반 대상 본인부담 '+(FEE.copayRate*100)+'% 기준이며, '
    + '감경 대상은 비율이 다르고 식재료비·간식비 등 비급여는 빠져 있습니다.<br>'
    + '이 금액은 <b>위 공공데이터 2종에 들어 있지 않습니다.</b> '
    + esc(FEE.source)+'('+esc(FEE.asOf)+')를 상수로 넣은 것이며, <b>순위·정렬에는 쓰지 않습니다.</b>'
    + '</details></small>';
}

/* 읍면동 목록 — 시·군·구를 고른 뒤에만 보인다. 좌표가 없어 거리는 못 재지만
   같은 동 기관을 먼저 보여주는 "내 동네 먼저"는 주소 칸만으로 가능하다 */
function fillDong(){
  const si=$sido.value, gg=$sgg.value;
  $dong.innerHTML='<option value="">선택 안 함</option>';
  if(si===''||gg===''){ $dongwrap.hidden=true; return; }
  const set=new Set();
  ITEMS.forEach(r=>{ if(r[F.sidoIx]===+si && r[F.sigungu]===gg && r[F.dong]) set.add(r[F.dong]); });
  [...set].sort((a,b)=>a.localeCompare(b,'ko')).forEach(d=>{
    const o=document.createElement('option'); o.value=d; o.textContent=d; $dong.appendChild(o);
  });
  $dongwrap.hidden = set.size===0;
}

function render(){
  $list.innerHTML=''; $more.hidden=true;
  const si=$sido.value;
  if(si===''){ $bar.textContent='부모님이 계신 지역을 선택하세요.'; $share.hidden=true; return; }

  const sidoName=DATA.sido[+si];
  const gg=$sgg.value;
  const med=MED[sidoName];

  const region=ITEMS.filter(r=> r[F.sidoIx]===+si && (gg===''||r[F.sigungu]===gg))
               .sort((a,b)=> a[F.ratio]-b[F.ratio] || b[F.cap]-a[F.cap]);
  // 지역 내 순위는 검색과 무관하게 유지한다
  region.forEach((r,i)=> r.rank=i+1);

  const where = gg===''? sidoName : sidoName+' '+gg;
  if(region.length===0){
    $bar.textContent = where+'에 해당하는 주야간보호센터 자료가 없습니다.';
    $list.innerHTML='<li class="empty">다른 지역을 선택해 보세요.</li>';
    return;
  }

  $share.hidden=false;
  const q=$q.value.trim().toLowerCase();
  current = q? region.filter(r=> r[F.name].toLowerCase().includes(q)) : region;
  if($only.checked) current = current.filter(r=> r[F.ratio] < med);
  // 공단 평가등급 필터. 평가 이력이 없는 기관은 여기서 전부 빠지므로 아래에서 몇 곳이 빠졌는지 밝힌다
  const noEval = region.filter(r=> !r[F.grade]).length;
  if($onlyab.checked) current = current.filter(r=> r[F.grade]==='A' || r[F.grade]==='B');

  // "내 동네 먼저" — 같은 읍면동을 위로, 그 안에서는 1인당 적은 순. 순위 번호(r.rank)는 지역 순위 그대로
  const dg=$dong.value;
  if(dg) current = current.slice().sort((a,b)=>
      ((a[F.dong]===dg)?0:1)-((b[F.dong]===dg)?0:1) || a[F.ratio]-b[F.ratio] || b[F.cap]-a[F.cap]);

  const cond=[];
  if(q) cond.push('\''+esc($q.value.trim())+'\'');
  if($only.checked) cond.push('중간값보다 적은 곳');
  if($onlyab.checked) cond.push('평가 A·B등급');

  if(current.length===0){
    $bar.innerHTML = where+' 주야간보호센터 '+region.length+'곳 중 <b>'+cond.join(' · ')+'</b>에 해당하는 곳이 없습니다.'
      + ($onlyab.checked && noEval? '<small class="hint">이 지역 '+noEval+'곳은 공단 평가 이력이 없어 등급 조건에서 빠집니다.</small>' : '');
    $list.innerHTML='<li class="empty">'+(($only.checked||$onlyab.checked)? '체크를 풀거나 ' : '')+(q? '검색어를 지우거나 ' : '')+'다른 지역을 골라 보세요.</li>';
    return;
  }
  $bar.innerHTML = where+' 주야간보호센터 <b>'+region.length+'곳</b>'
    + (cond.length? ' 중 <b>'+cond.join(' · ')+' '+current.length+'곳</b>' : '')
    + ' · '+sidoName+' 중간값 <b>'+fmt(med)+'명</b>'
    + (dg? ' · <b>'+esc(dg)+'</b> '+current.filter(r=>r[F.dong]===dg).length+'곳 먼저' : '')
    + '<small class="hint">중간값 = 이 지역 기관을 줄 세웠을 때 한가운데 값 (개원 1년 미만 제외)'
    + ($onlyab.checked && noEval? '<br>이 지역 '+noEval+'곳은 공단 평가 이력이 없어 이 조건에서 빠져 있습니다.' : '')
    + '</small>'
    + feeLine();

  expanded=false;
  draw();
}

/* 공단 평가등급 배지 — 2종째 데이터에서 온 값.
   우리가 매긴 등급이 아니라는 걸 분명히 하려고 "공단 평가"를 앞에 적고,
   평가 연도까지 붙인다 (2023~2024년 평가라 최근 변화는 반영되지 않는다).
   이력이 없으면 숨기지 않고 "평가 이력 없음"으로 적는다 — 빈칸은 오해를 만든다. */
function gradeChip(r){
  const g=r[F.grade];
  if(!g) return '<span class="chip gr none" title="공단 평가를 아직 받지 않았거나 공개 자료에 없습니다">공단 평가 이력 없음</span>';
  const y=r[F.gyear];
  return '<span class="chip gr">공단 평가 <b>'+esc(g)+'등급</b>'+(y? ' <span>('+esc(y)+')</span>' : '')+'</span>';
}

/* 전화 슬롯. 번호를 받은 기관은 실제 통화 링크, 못 받은 기관은 종전처럼 안내 말풍선.
   번호가 없는 이유가 바뀌었다 — 예전엔 "데이터에 칸이 없음"이었지만 지금은
   "이 기관만 공개돼 있지 않음"이다. 문구도 사실에 맞게 바꾼다. */
const PHONE_SVG = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">'
  + '<path fill="currentColor" d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.2.4 2.4.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.4 0 .8-.2 1l-2.3 2.2z"/></svg>';

function telSlot(r){
  const t = r[F.tel];
  if(t){
    return '<a class="tel" href="tel:'+esc(t.replace(/-/g,''))+'" '
      + 'aria-label="'+esc(r[F.name])+' 전화 걸기 '+esc(t)+'" title="'+esc(t)+'">'
      + PHONE_SVG + '</a>';
  }
  return '<span class="tel" tabindex="0" role="note" aria-label="전화번호 안내">'
    + PHONE_SVG
    + '<span class="tip">이 기관은 <b>전화번호가 공개되어 있지 않습니다.</b><br>「검색하기」로 확인하세요.</span>'
    + '</span>';
}

function meter(ratio, med, good){
  // 가운데(50%)가 중간값. 중간값의 2배를 끝으로 잡아 채움 길이를 정한다.
  // 수치 라벨은 달지 않는다 — 값은 큰 숫자에, 중간값은 상단 기준선에 이미 있다.
  const pct = Math.max(4, Math.min(100, ratio/(med*2)*100));
  return '<div class="meter" title="가운데 눈금이 '+fmt(med)+'명(중간값)"><div class="track">'
    + '<div class="fill'+(good?' good':'')+'" style="width:'+pct.toFixed(1)+'%"></div>'
    + '<div class="tick"></div></div>'
    + '<div class="lab"><span></span><span>중간값</span><span></span></div>'
    + '</div>';
}

// 주소에 지역을 붙인다 (#서울특별시/관악구) → 링크를 보내면 같은 목록이 바로 열린다
function setHash(){
  const s=DATA.sido[+$sido.value];
  const h = s? '#'+encodeURIComponent(s)+'/'+encodeURIComponent($sgg.value)
              + ($dong.value? '/'+encodeURIComponent($dong.value) : '') : '';
  history.replaceState(null,'',location.pathname+location.search+h);
}
function fromHash(){
  try{
    const h=decodeURIComponent(location.hash.slice(1)); if(!h) return false;
    const [s,g,d]=h.split('/'); const ix=DATA.sido.indexOf(s); if(ix<0) return false;
    $sido.value=String(ix); fillSgg();
    if(g && [...$sgg.options].some(o=>o.value===g)) $sgg.value=g;
    fillDong();
    if(d && [...$dong.options].some(o=>o.value===d)) $dong.value=d;
    render(); return true;
  }catch(e){ return false; }
}
function share(){
  const url=location.href, done=()=>{ $share.textContent='복사됐습니다 · 가족에게 보내세요'; setTimeout(()=>$share.textContent='이 결과 링크 복사',2500); };
  if(navigator.clipboard && navigator.clipboard.writeText){ navigator.clipboard.writeText(url).then(done).catch(()=>prompt('주소를 복사하세요', url)); }
  else prompt('주소를 복사하세요', url);
}

function savePick(){
  try{ localStorage.setItem(SAVE, JSON.stringify({s: DATA.sido[+$sido.value]||'', g: $sgg.value, d: $dong.value})); }catch(e){}
}
function restorePick(){
  try{
    const p=JSON.parse(localStorage.getItem(SAVE)||'null'); if(!p||!p.s) return;
    const ix=DATA.sido.indexOf(p.s); if(ix<0) return;
    $sido.value=String(ix); fillSgg();
    if(p.g && [...$sgg.options].some(o=>o.value===p.g)) $sgg.value=p.g;
    fillDong();
    if(p.d && [...$dong.options].some(o=>o.value===p.d)) $dong.value=p.d;
    render();
  }catch(e){}
}

function draw(){
  const show = expanded? current : current.slice(0,PAGE);
  const sidoName = DATA.sido[+$sido.value];
  const med = MED[sidoName];

  // 같은 이름+주소가 이 지역에 두 번 이상 나오는지 미리 센다 (중복 등록 안내용)
  const seen = new Map(), dupKeys = new Set();
  current.forEach(r=>{
    const k = r[F.name]+'|'+r[F.addr];
    if(seen.has(k)) dupKeys.add(k); else seen.set(k, 1);
  });

  $list.innerHTML = show.map((r,i)=>{
    const ratio=r[F.ratio], good = ratio < med;
    const tags=[];
    // 시안의 "인력" 행 — 0명도 숨기지 않고 적는다 (없다는 정보도 정보)
    tags.push('간호인력 '+r[F.nurse]+'명');
    if(r[F.rehab]>0) tags.push('물리·작업치료사 '+r[F.rehab]+'명');
    tags.push('사회복지사 '+r[F.social]+'명');

    // 중간값 수치는 상단 기준선에 한 번만. 카드에서는 방향만 말한다 (중복 제거)
    const cmp = good ? '중간값보다 적습니다' : '중간값보다 많습니다';

    // 개원 1년 미만 안내 — 카드 맨 아래, 한 줄로 접어 두고 누르면 전문. 버튼 높이를 흔들지 않기 위해
    let note = r[F.isNew]
      ? '<details class="new"><summary>'+esc(r[F.since])+' 지정 · 개원 1년 미만 — 숫자가 실제보다 나쁘게 나올 수 있어요</summary>'
        + '<p>문 연 지 얼마 안 된 곳은 정원은 인가받은 최대치인데 인력은 채워지는 중이라 '
        + '이 숫자가 <b>실제보다 나쁘게</b> 나옵니다. 숫자만으로 판단하지 마세요.</p></details>'
      : '';
    // 같은 이름·같은 주소가 두 번 나오는 경우가 있다. 원본에 기관코드가 둘로 등록된 것이라
    // 어느 쪽이 실제인지 우리가 판단할 수 없어 합치지 않았다. 대신 화면에서 설명한다.
    // 설명 없이 두면 보호자가 한 센터를 서로 다른 숫자로 두 번 보게 된다.
    if(dupKeys.has(r[F.name]+'|'+r[F.addr])){
      note += '<details class="new"><summary>같은 주소에 기관코드가 2개 등록돼 있어요 — 아래에 한 번 더 나옵니다</summary>'
        + '<p>원본 자료에 이 시설이 <b>기관코드 2개로 등록</b>되어 있어 정원·인력 신고값이 서로 다릅니다. '
        + '어느 쪽이 현재 상태인지는 자료만으로 알 수 없어 <b>합치지 않고 그대로 보여드립니다.</b> '
        + '기관에 직접 확인하세요.</p></details>';
    }

    const q=encodeURIComponent(r[F.name]+' '+r[F.sigungu]);
    // 지도 앱에 그대로 붙여넣도록 시·도까지 붙인 전체 주소.
    // 원본 주소에 공백이 겹친 행이 있어 한 칸으로 줄인다 — 화면은 HTML이 알아서 접지만
    // 클립보드로는 그대로 나간다.
    const fullAddr = (DATA.sido[r[F.sidoIx]]+' '+r[F.sigungu]+' '+r[F.addr]).replace(/\s+/g,' ').trim();
    // 카드 안을 평평한 10행으로 둔다 — 서브그리드로 같은 줄 카드의 행 높이를 맞추기 위해
    return '<li>'
      + '<p class="name"><span class="rank'+(r.rank<=3?' top':'')+'">'+r.rank+'위</span>'+esc(r[F.name])+'</p>'
      +   '<p class="where">'+esc(r[F.sigungu]+' '+r[F.addr])
      +     (r[F.tel]? ' · <span class="telno">'+esc(r[F.tel])+'</span>' : '')+'</p>'
      +   '<p class="cap">요양보호사 1명이 돌보는 어르신</p>'
      +   '<div class="big"><span class="num'+(good?' good':'')+'">'+fmt(ratio)+'</span>'
      +     '<span class="unit">명</span></div>'
      +   '<p class="calc">정원 '+r[F.cap]+'명 &divide; 요양보호사 '+r[F.care]+'명</p>'
      +   meter(ratio, med, good)
      +   '<p class="verdict"><span class="chip'+(good?' good':'')+'">'+cmp+'</span>'
      +     gradeChip(r)
      +     (($dong.value && r[F.dong]===$dong.value)? '<span class="chip near">내 동네</span>' : '')+'</p>'
      +   '<p class="tags"><b>인력</b> <i>'+tags.join(' · ')+'</i></p>'
      +   '<div class="noteslot">'+note+'</div>'
      +   '<div class="act">'
      +   '<div class="btns">'
      +     telSlot(r)
      +     '<a class="go" target="_blank" rel="noopener noreferrer" '
      +       'href="https://search.naver.com/search.naver?query='+q+'">검색하기</a>'
      +     '<button class="copy" type="button" data-addr="'+esc(fullAddr)+'">주소 복사</button>'
      +   '</div>'
      +   '<a class="portal" target="_blank" rel="noopener noreferrer" '
      +     'href="https://www.longtermcare.or.kr/npbs/r/a/201/selectLtcoSrch.web">공단 포털에서 직접 찾기 (이용가능 여부)</a>'
      +   '</div>'
      + '</li>';
  }).join('');

  if(!expanded && current.length>PAGE){
    $more.hidden=false;
    $more.textContent='나머지 '+(current.length-PAGE)+'곳 전부 보기';
  } else { $more.hidden=true; }
}

function esc(s){ return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

/* 주소 복사 — 카드가 매번 다시 그려지므로 목록에 위임해서 한 번만 연결한다 */
$list.addEventListener('click', e=>{
  const btn = e.target.closest('button.copy'); if(!btn) return;
  const addr = btn.getAttribute('data-addr') || '';
  const done = ()=>{
    const old = btn.textContent;
    btn.textContent='복사됨'; btn.classList.add('done');
    setTimeout(()=>{ btn.textContent=old; btn.classList.remove('done'); }, 1800);
  };
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(addr).then(done).catch(()=>prompt('주소를 복사하세요', addr));
  } else {
    prompt('주소를 복사하세요', addr);
  }
});

$sido.addEventListener('change',()=>{ fillSgg(); fillDong(); render(); savePick(); setHash(); });
$sgg .addEventListener('change', ()=>{ fillDong(); render(); savePick(); setHash(); });
$dong.addEventListener('change', ()=>{ render(); savePick(); setHash(); });
$q   .addEventListener('input', render);
$only.addEventListener('change', render);
$onlyab.addEventListener('change', render);
if(FEE){
  $feeon.addEventListener('change', ()=>{ $feepick.hidden=!$feeon.checked; render(); });
  $grade.addEventListener('change', render);
}
$share.addEventListener('click', share);
$more.addEventListener('click',()=>{ expanded=true; draw(); window.scrollBy(0,80); });
initFee();
if(!fromHash()) restorePick();   // 링크에 지역이 있으면 그게 우선, 없으면 마지막 선택
</script>
</body>
</html>
"""

m = data["meta"]
html = (TEMPLATE
        .replace("__PAYLOAD__", payload)
        .replace("__DATAID__", m["dataId"])
        .replace("__BASEDATE__", m["baseDate"])
        .replace("__CYCLE__", m["cycle"])
        .replace("__TYPES__", m["types"])
        .replace("__COUNT__", f"{m['count']:,}")
        .replace("__MEDIANNOTE__", m["medianNote"].replace("중앙값", "중간값"))   # 화면 용어는 "중간값"
        .replace("__NEWCOUNT__", f"{m['newCount']:,}")
        # ── 2종째(평가 결과) 관련 ───────────────────────────────────────
        .replace("__SOURCE2__", m["source2"].replace("공공데이터포털 ", ""))
        .replace("__DATAID2__", m["dataId2"])
        .replace("__JOINKEY__", m["joinKey"])
        .replace("__EVALRANGE__", m["evalRange"])
        .replace("__EVALMATCHED__", f"{m['evalMatched']:,}")
        .replace("__EVALRATE__", f"{m['evalRate']}")
        .replace("__GAPCOUNT__", f"{m['gapCount']:,}")
        .replace("__GAPBASE__", f"{m['gapBase']:,}")
        .replace("__GAPPCT__", f"{m['gapPct']}")
        .replace("__CORR__", f"{m['corr']}"))

outdir = os.path.dirname(out)
if outdir:                      # 현재 폴더에 바로 쓰는 경우 dirname이 빈 문자열이다
    os.makedirs(outdir, exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    f.write(html)

print(f"생성 {out}  {os.path.getsize(out):,} bytes ({os.path.getsize(out)/1024:.0f} KB)")
print(f"  기관 {m['count']:,}곳 · 시도 {len(data['sido'])}개 · 시군구 {sum(len(v) for v in data['sigungu'].values())}개")
