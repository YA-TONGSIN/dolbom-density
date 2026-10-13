"""data/day_care.json -> 자체완결 HTML 1개.

실행:  python tools/build_html.py data/day_care.json dist/돌봄밀도.html
서버·네트워크 없이 더블클릭으로 열린다.
"""
import sys, json, os

src = sys.argv[1] if len(sys.argv) > 1 else "data/day_care.json"
out = sys.argv[2] if len(sys.argv) > 2 else "dist/돌봄밀도.html"

with open(src, encoding="utf-8") as f:
    data = json.load(f)

payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>주야간보호센터 돌봄 밀도 비교 — 요양보호사 1인당 어르신 수로 전국 비교</title>
<meta name="description" content="부모님 동네 주야간보호센터를 요양보호사 1인당 어르신 수로 비교합니다. 공공데이터 1종(국민건강보험공단 장기요양기관 시설별 현황), 전국 5,346곳, 시·도 중간값과 나란히 표시.">
<meta property="og:title" content="주야간보호센터 돌봄 밀도 비교">
<meta property="og:description" content="요양보호사 한 명이 어르신 몇 분을 돌보는지로 전국 주야간보호센터를 비교합니다.">
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

  /* 결과 — 카드 하나가 기관 하나. 넓으면 3열, 중간 2열, 휴대폰 1열 (시안 1c) */
  ol{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:var(--s3)}
  li{
    background:var(--card);border-radius:var(--r);box-shadow:var(--shadow);border:1px solid var(--hair);
    padding:var(--s4);transition:box-shadow var(--t-fast),transform var(--t-fast);
  }
  li:hover{box-shadow:var(--shadow-lift);transform:translateY(-1px)}

  /* 카드 안 구성(시안): N위 + 기관명 → 주소 → "요양보호사 1명이 돌보는 어르신" → 큰 숫자 → 근거 → 막대 → 배지 → 인력 → 행동 */
  /* 카드 높이는 같은 줄에서 맞춰지고(그리드 stretch), 버튼은 아래로 밀어 줄마다 같은 높이에 선다 */
  li{display:grid}
  .row{display:grid;grid-template-columns:auto minmax(0,1fr);grid-template-rows:auto minmax(0,1fr);
       column-gap:10px;align-items:baseline;height:100%}
  .rank{font-size:var(--t-sm);font-weight:800;color:var(--mute);font-variant-numeric:tabular-nums;white-space:nowrap}
  .body{display:flex;flex-direction:column;gap:8px;min-width:0;grid-column:1 / -1;height:100%}
  .body>.act{margin-top:auto}
  .name{font-size:var(--t-md);font-weight:700;word-break:keep-all;line-height:1.3}
  .where{font-size:var(--t-sm);color:var(--mute);word-break:keep-all;line-height:1.5}
  .cap{font-size:var(--t-sm);color:var(--mute);margin-top:4px}

  .big{display:flex;align-items:baseline;gap:6px}
  .num{font-size:44px;font-weight:800;line-height:1;font-variant-numeric:tabular-nums;letter-spacing:-0.045em}
  .num.good{color:var(--accent)}
  .unit{font-size:var(--t-base);color:var(--ink);font-weight:700}
  .calc{font-size:var(--t-sm);color:var(--mute)}

  /* 판정 배지 — 채움형 알약. 중간값 수치는 위 기준선에 있으므로 여기선 방향만 */
  .chip{
    display:inline-block;padding:7px 14px;border-radius:999px;
    font-size:var(--t-sm);font-weight:700;line-height:1.3;
    background:var(--field);color:var(--ink);
  }
  .chip.good{background:var(--accent-wash);color:var(--accent-deep)}
  .chip.near{background:var(--ink);color:var(--card);margin-left:6px}   /* 내 동네 표식 — 검정 알약 */
  .verdict{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
  @media (prefers-color-scheme:dark){ .chip.good{color:#5fd3b8} }  /* 어두운 바탕에서 배지 글자 대비 확보 */

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

  /* 행동 — 주 버튼은 크고 둥글게 (높이 52), 보조는 글자 링크 */
  .act{display:grid;row-gap:var(--s2);justify-items:stretch;padding-top:var(--s1)}
  .act a.go{text-align:center}
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
    .rank{width:26px;height:26px;font-size:12px}
    .row{column-gap:var(--s2)}
    li{padding:var(--s3) 15px}
    .panel{padding:var(--s3) 15px}
    .opts{grid-template-columns:1fr}
    a.go,button.share{width:100%;text-align:center}
    .act{justify-items:stretch}
    a.portal{text-align:center}
  }
</style>
</head>
<body>
<div class="wrap">

  <header class="head">
    <p class="eyebrow">공공데이터 1종 · 전국 __COUNT__곳</p>
    <h1>주야간보호센터 돌봄 밀도 비교</h1>
    <p class="lede">요양보호사 한 명이 어르신 몇 분을 돌보는지로 비교합니다. 숫자가 적을수록 한 분께 더 많은 손길이 갑니다.</p>
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

  <div class="opts">
    <label><input id="only" type="checkbox"> 중간값보다 적은 곳만</label>
    <button id="share" class="share" type="button" hidden>이 결과 링크 복사</button>
  </div>
  </div>

  <div id="bar" class="bar">부모님이 계신 지역을 선택하세요.</div>

  <ol id="list"></ol>
  <button id="more" class="more" hidden>나머지 전부 보기</button>

  <footer>
    <div><b>출처</b> 공공데이터포털 · 국민건강보험공단_장기요양기관 시설별 현황 (데이터 __DATAID__)</div>
    <div><b>자료 기준일</b> __BASEDATE__ · <b>갱신 주기</b> __CYCLE__</div>
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
const $only = document.getElementById('only');
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

/* 읍면동 목록 — 시·군·구를 고른 뒤에만 보인다. 좌표가 없어 거리는 못 재지만
   같은 동 기관을 먼저 보여주는 "내 동네 먼저"는 데이터 1종 안에서 가능하다 */
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

  // "내 동네 먼저" — 같은 읍면동을 위로, 그 안에서는 1인당 적은 순. 순위 번호(r.rank)는 지역 순위 그대로
  const dg=$dong.value;
  if(dg) current = current.slice().sort((a,b)=>
      ((a[F.dong]===dg)?0:1)-((b[F.dong]===dg)?0:1) || a[F.ratio]-b[F.ratio] || b[F.cap]-a[F.cap]);

  if(current.length===0){
    $bar.innerHTML = where+' 주야간보호센터 '+region.length+'곳 중 '
      + (q? '<b>\''+esc($q.value.trim())+'\'</b>이 들어간 이름' : '')
      + (q&&$only.checked? '이면서 ' : '')
      + ($only.checked? '중간값보다 적은 곳' : '')
      + '이 없습니다.';
    $list.innerHTML='<li class="empty">'+($only.checked? '체크를 풀거나 ' : '')+(q? '검색어를 지우거나 ' : '')+'다른 지역을 골라 보세요.</li>';
    return;
  }
  const cond=[]; if(q) cond.push('\''+esc($q.value.trim())+'\''); if($only.checked) cond.push('중간값보다 적은 곳');
  $bar.innerHTML = where+' 주야간보호센터 <b>'+region.length+'곳</b>'
    + (cond.length? ' 중 <b>'+cond.join(' · ')+' '+current.length+'곳</b>' : '')
    + ' · '+sidoName+' 중간값 <b>'+fmt(med)+'명</b>'
    + (dg? ' · <b>'+esc(dg)+'</b> '+current.filter(r=>r[F.dong]===dg).length+'곳 먼저' : '')
    + '<small class="hint">중간값 = 이 지역 기관을 줄 세웠을 때 한가운데 값 (개원 1년 미만 제외)</small>';

  expanded=false;
  draw();
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
    const note = r[F.isNew]
      ? '<details class="new"><summary>'+esc(r[F.since])+' 지정 · 개원 1년 미만 — 숫자가 실제보다 나쁘게 나올 수 있어요</summary>'
        + '<p>문 연 지 얼마 안 된 곳은 정원은 인가받은 최대치인데 인력은 채워지는 중이라 '
        + '이 숫자가 <b>실제보다 나쁘게</b> 나옵니다. 숫자만으로 판단하지 마세요.</p></details>'
      : '';

    const q=encodeURIComponent(r[F.name]+' '+r[F.sigungu]);
    return '<li><div class="row">'
      + '<div class="rank">'+r.rank+'위</div>'
      + '<p class="name">'+esc(r[F.name])+'</p>'
      + '<div class="body">'
      +   '<p class="where">'+esc(r[F.sigungu]+' '+r[F.addr])+'</p>'
      +   '<p class="cap">요양보호사 1명이 돌보는 어르신</p>'
      +   '<div class="big"><span class="num'+(good?' good':'')+'">'+fmt(ratio)+'</span>'
      +     '<span class="unit">명</span></div>'
      +   '<p class="calc">정원 '+r[F.cap]+'명 &divide; 요양보호사 '+r[F.care]+'명</p>'
      +   meter(ratio, med, good)
      +   '<p class="verdict"><span class="chip'+(good?' good':'')+'">'+cmp+'</span>'
      +     (($dong.value && r[F.dong]===$dong.value)? '<span class="chip near">내 동네</span>' : '')+'</p>'
      +   '<p class="tags"><b>인력</b> <i>'+tags.join(' · ')+'</i></p>'
      +   note
      +   '<div class="act">'
      +   '<a class="go" target="_blank" rel="noopener noreferrer" '
      +     'href="https://search.naver.com/search.naver?query='+q+'">전화번호 찾아보기</a>'
      +   '<a class="portal" target="_blank" rel="noopener noreferrer" '
      +     'href="https://www.longtermcare.or.kr/npbs/r/a/201/selectLtcoSrch.web">공단 포털에서 이용가능·평가등급 확인</a>'
      +   '</div>'
      + '</div></div></li>';
  }).join('');

  if(!expanded && current.length>PAGE){
    $more.hidden=false;
    $more.textContent='나머지 '+(current.length-PAGE)+'곳 전부 보기';
  } else { $more.hidden=true; }
}

function esc(s){ return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

$sido.addEventListener('change',()=>{ fillSgg(); fillDong(); render(); savePick(); setHash(); });
$sgg .addEventListener('change', ()=>{ fillDong(); render(); savePick(); setHash(); });
$dong.addEventListener('change', ()=>{ render(); savePick(); setHash(); });
$q   .addEventListener('input', render);
$only.addEventListener('change', render);
$share.addEventListener('click', share);
$more.addEventListener('click',()=>{ expanded=true; draw(); window.scrollBy(0,80); });
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
        .replace("__NEWCOUNT__", f"{m['newCount']:,}"))

os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    f.write(html)

print(f"생성 {out}  {os.path.getsize(out):,} bytes ({os.path.getsize(out)/1024:.0f} KB)")
print(f"  기관 {m['count']:,}곳 · 시도 {len(data['sido'])}개 · 시군구 {sum(len(v) for v in data['sigungu'].values())}개")
