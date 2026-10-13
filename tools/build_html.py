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
<meta name="description" content="부모님 동네 주야간보호센터를 요양보호사 1인당 어르신 수로 비교합니다. 공공데이터 1종(국민건강보험공단 장기요양기관 시설별 현황), 전국 5,346곳, 시·도 중앙값과 나란히 표시.">
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
  :root{
    --ink:#16243f;         /* 글자 — 짙은 남색 */
    --mute:#697585;        /* 보조 글자 */
    --accent:#0a6b5c;      /* 강조 1색 — 틸 */
    --accent-deep:#07564a; /* 강조색 짙은 단계 (호버·테두리) */
    --accent-wash:#e8f1ee; /* 강조색 가장 옅은 단계 (배지 바탕) */
    --soft:#f4f7f7;        /* 면 */
    --line:#dfe6e7;        /* 구분선 */

    --t-xs:11px; --t-sm:13px; --t-base:17px; --t-md:21px; --t-lg:27px; --t-xl:44px;
    --s1:5px; --s2:8px; --s3:13px; --s4:21px; --s5:34px; --s6:55px;
    --r:12px; --r-sm:9px;
  }
  *{box-sizing:border-box}
  html,body{margin:0;padding:0}
  /* 세로 리듬은 그리드 gap 하나로만 만든다 — 요소 기본 마진은 전부 제거 */
  p,h1,h2,h3,ol,ul,figure,blockquote{margin:0}
  body{
    background:#fff; color:var(--ink);
    font-family:"Malgun Gothic","맑은 고딕",system-ui,-apple-system,sans-serif;
    font-size:var(--t-base); line-height:1.55;
    -webkit-text-size-adjust:100%;
  }
  body::before{content:"";display:block;height:4px;background:var(--accent)}

  /* 전체 세로 리듬을 그리드 gap 하나로 통제한다 (요소별 margin 사용 안 함) */
  .wrap{
    max-width:720px;margin:0 auto;padding:var(--s4) var(--s3) var(--s6);
    display:grid;grid-template-columns:minmax(0,1fr);row-gap:var(--s4);
    overflow-wrap:anywhere;
  }
  .wrap>*{margin:0}

  .head{display:grid;row-gap:var(--s1)}
  .eyebrow{font-size:var(--t-sm);color:var(--accent);font-weight:700;letter-spacing:.02em}
  h1{font-size:var(--t-lg);letter-spacing:-0.025em;line-height:1.22;font-weight:700}
  .lede{font-size:15px;color:var(--mute)}

  /* 입력 영역 — 고르는 곳과 결과의 경계 */
  .panel{
    background:var(--soft);border:1px solid var(--line);border-radius:var(--r);
    padding:var(--s3);display:grid;row-gap:var(--s3);
  }
  .pick{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:var(--s3)}
  .pick label,.find label{display:grid;row-gap:var(--s1);min-width:0}
  .pick span,.find span{font-size:var(--t-sm);color:var(--mute)}
  select,.find input{
    width:100%;padding:var(--s3) 12px;font-size:var(--t-base);font-family:inherit;
    color:var(--ink);background:#fff;border:1.5px solid var(--line);border-radius:var(--r-sm);
  }
  select:focus,.find input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-wash)}
  .find{display:grid}

  .opts{display:grid;grid-template-columns:1fr auto;gap:var(--s2) var(--s3);align-items:center;font-size:15px}
  .opts label{display:flex;align-items:center;gap:var(--s2);cursor:pointer}
  .opts input{width:18px;height:18px;margin:0;accent-color:var(--accent)}
  button.share{
    padding:var(--s2) var(--s3);font-size:var(--t-sm);font-family:inherit;font-weight:700;
    color:var(--accent-deep);background:#fff;border:1.5px solid var(--line);
    border-radius:var(--r-sm);cursor:pointer;white-space:nowrap;
  }
  button.share:hover{border-color:var(--accent)}

  /* 지역 기준선 — 스크롤해도 남도록 고정. 중앙값 수치는 화면에서 여기 한 곳에만 둔다 */
  .bar{
    position:sticky;top:0;z-index:5;
    padding:var(--s3);border:1px solid var(--line);border-left:4px solid var(--accent);
    border-radius:var(--r-sm);background:#fbfdfd;font-size:15px;
  }
  .bar b{font-size:var(--t-base)}

  ol{list-style:none;padding:0;display:grid;row-gap:0}
  li{border-bottom:1px solid var(--line);padding:var(--s4) 0}
  li:first-child{border-top:1px solid var(--line)}

  .row{display:grid;grid-template-columns:auto minmax(0,1fr);column-gap:var(--s3);align-items:start}
  .rank{
    width:30px;height:30px;border-radius:50%;background:#fff;border:1.5px solid var(--line);
    display:grid;place-items:center;margin-top:2px;
    font-size:var(--t-sm);font-weight:700;color:var(--mute);font-variant-numeric:tabular-nums;
  }
  .body{display:grid;row-gap:var(--s2);min-width:0}
  .name{font-size:19px;font-weight:700;word-break:keep-all;line-height:1.3}
  .where{font-size:var(--t-sm);color:var(--mute);word-break:keep-all}

  .big{display:flex;align-items:baseline;gap:7px}
  .num{font-size:34px;font-weight:700;line-height:1;font-variant-numeric:tabular-nums;letter-spacing:-0.02em}
  .num.good{color:var(--accent)}
  .unit{font-size:var(--t-sm);color:var(--mute)}
  .calc{font-size:var(--t-sm);color:var(--mute)}

  /* 판정 배지 — 중앙값 수치는 위 기준선에 있으므로 여기선 방향만 말한다 */
  .chip{
    display:inline-block;padding:4px var(--s3);border-radius:999px;
    font-size:var(--t-sm);font-weight:700;
    background:var(--soft);color:var(--mute);border:1px solid var(--line);
  }
  .chip.good{background:var(--accent-wash);color:var(--accent-deep);border-color:#cfe3dd}

  /* 넓은 화면 — 좌:우 = 1.618 : 1 (황금분할) */
  @media (min-width:600px){
    .body{
      grid-template-columns:1.618fr 1fr;column-gap:var(--s4);
      grid-template-areas:"name big" "where big" "calc big" "meter big" "verdict big" "note note" "tags tags" "act act";
    }
    .name{grid-area:name}.where{grid-area:where}.calc{grid-area:calc}.meter{grid-area:meter}
    .verdict{grid-area:verdict}.new{grid-area:note}.tags{grid-area:tags}.act{grid-area:act}
    .big{grid-area:big;flex-direction:column;align-items:flex-end;gap:0;text-align:right}
    .num{font-size:var(--t-xl)}
    .unit{font-size:var(--t-xs)}
  }

  /* 중앙값 대비 막대 — 가운데 눈금이 해당 시·도 중앙값 */
  .meter{max-width:420px}
  .meter .track{position:relative;height:var(--s2);background:var(--soft);border:1px solid var(--line);border-radius:999px}
  .meter .fill{height:100%;border-radius:999px;background:var(--mute)}
  .meter .fill.good{background:var(--accent)}
  .meter .tick{position:absolute;left:50%;top:-5px;bottom:-5px;width:2px;background:var(--ink);border-radius:1px}

  .tags{font-size:var(--t-sm);color:var(--mute)}
  .tags i{font-style:normal}

  .new{
    font-size:var(--t-sm);padding:var(--s3);border-radius:var(--r-sm);
    background:var(--soft);border:1px solid var(--line);color:var(--ink);line-height:1.6;
  }
  .new b{font-weight:700}

  .act{display:grid;row-gap:var(--s2);justify-items:start}
  a.go{
    display:inline-block;padding:var(--s3) var(--s4);font-size:16px;font-weight:700;
    color:#fff;background:var(--accent);border-radius:var(--r-sm);text-decoration:none;
  }
  a.go:hover{background:var(--accent-deep)}
  a.portal{font-size:var(--t-sm);color:var(--mute);text-decoration:underline;word-break:keep-all}
  a.portal:hover{color:var(--accent-deep)}

  .more{
    width:100%;padding:var(--s3);font-size:16px;font-family:inherit;font-weight:700;
    color:var(--accent-deep);background:#fff;border:1.5px solid var(--line);
    border-radius:var(--r-sm);cursor:pointer;
  }
  .more:hover{border-color:var(--accent)}
  [hidden]{display:none !important}
  .empty{padding:var(--s5) 0;color:var(--mute);border:0}

  footer{padding-top:var(--s4);border-top:1px solid var(--line);
         font-size:var(--t-sm);color:var(--mute);line-height:1.7;display:grid;row-gap:2px}
  footer b{color:var(--ink)}
  .warn{margin-top:var(--s2);padding:var(--s3);background:var(--soft);border-radius:var(--r-sm);line-height:1.65}

  @media (max-width:480px){
    .wrap{padding:var(--s3) var(--s3) var(--s5);row-gap:var(--s3)}
    .pick{grid-template-columns:1fr;gap:var(--s2)}
    h1{font-size:var(--t-md)}
    .num{font-size:30px}
    .rank{width:26px;height:26px;font-size:12px}
    .row{column-gap:var(--s2)}
    li{padding:var(--s3) 0}
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
    <p class="lede">요양보호사 한 명이 어르신 몇 분을 돌보는지로 비교합니다.</p>
  </header>

  <div class="panel">
  <div class="pick">
    <label><span>시 · 도</span>
      <select id="sido"><option value="">선택하세요</option></select>
    </label>
    <label><span>시 · 군 · 구</span>
      <select id="sgg"><option value="">전체</option></select>
    </label>
  </div>

  <div class="find">
    <label><span>기관명으로 찾기 (선택)</span>
      <input id="q" type="search" placeholder="예: 효사랑 · 비워두면 전체" autocomplete="off">
    </label>
  </div>

  <div class="opts">
    <label><input id="only" type="checkbox"> 중앙값보다 적은 곳만</label>
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
    <div><b>중앙값 기준</b> __MEDIANNOTE__ (개원 __NEWCOUNT__곳 제외)</div>
    <div class="warn">
      이 숫자는 <b>돌봄 품질을 보증하지 않습니다.</b> 정원은 실제 이용 인원이 아니라 등록 가능한 최대 인원이고,
      요양보호사 수는 기관이 신고한 값입니다. <b>비교의 출발점</b>으로만 사용하시고,
      실제 선택 전에는 기관에 직접 확인하시기 바랍니다.
      <br><br>
      <b>개원 1년 미만 기관은 따로 표시했습니다.</b> 전국 자료로 확인해 보면 개원 2개월 미만 기관의
      1인당 어르신 수 중앙값은 11.0명, 10년 이상 된 기관은 6.2명입니다.
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

  if(current.length===0){
    $bar.innerHTML = where+' 주야간보호센터 '+region.length+'곳 중 '
      + (q? '<b>\''+esc($q.value.trim())+'\'</b>이 들어간 이름' : '')
      + (q&&$only.checked? '이면서 ' : '')
      + ($only.checked? '중앙값보다 적은 곳' : '')
      + '이 없습니다.';
    $list.innerHTML='<li class="empty">'+($only.checked? '체크를 풀거나 ' : '')+(q? '검색어를 지우거나 ' : '')+'다른 지역을 골라 보세요.</li>';
    return;
  }
  const cond=[]; if(q) cond.push('\''+esc($q.value.trim())+'\''); if($only.checked) cond.push('중앙값보다 적은 곳');
  $bar.innerHTML = where+' 주야간보호센터 <b>'+region.length+'곳</b>'
    + (cond.length? ' 중 <b>'+cond.join(' · ')+' '+current.length+'곳</b>' : '')
    + ' · '+sidoName+' 중앙값 <b>'+fmt(med)+'명</b>';

  expanded=false;
  draw();
}

function meter(ratio, med, good){
  // 가운데(50%)가 중앙값. 중앙값의 2배를 끝으로 잡아 채움 길이를 정한다.
  // 수치 라벨은 달지 않는다 — 값은 큰 숫자에, 중앙값은 상단 기준선에 이미 있다.
  const pct = Math.max(4, Math.min(100, ratio/(med*2)*100));
  return '<div class="meter" title="가운데 눈금이 '+fmt(med)+'명(중앙값)"><div class="track">'
    + '<div class="fill'+(good?' good':'')+'" style="width:'+pct.toFixed(1)+'%"></div>'
    + '<div class="tick"></div></div>'
    + '</div>';
}

// 주소에 지역을 붙인다 (#서울특별시/관악구) → 링크를 보내면 같은 목록이 바로 열린다
function setHash(){
  const s=DATA.sido[+$sido.value];
  const h = s? '#'+encodeURIComponent(s)+'/'+encodeURIComponent($sgg.value) : '';
  history.replaceState(null,'',location.pathname+location.search+h);
}
function fromHash(){
  try{
    const h=decodeURIComponent(location.hash.slice(1)); if(!h) return false;
    const [s,g]=h.split('/'); const ix=DATA.sido.indexOf(s); if(ix<0) return false;
    $sido.value=String(ix); fillSgg();
    if(g && [...$sgg.options].some(o=>o.value===g)) $sgg.value=g;
    render(); return true;
  }catch(e){ return false; }
}
function share(){
  const url=location.href, done=()=>{ $share.textContent='복사됐습니다 · 가족에게 보내세요'; setTimeout(()=>$share.textContent='이 결과 링크 복사',2500); };
  if(navigator.clipboard && navigator.clipboard.writeText){ navigator.clipboard.writeText(url).then(done).catch(()=>prompt('주소를 복사하세요', url)); }
  else prompt('주소를 복사하세요', url);
}

function savePick(){
  try{ localStorage.setItem(SAVE, JSON.stringify({s: DATA.sido[+$sido.value]||'', g: $sgg.value})); }catch(e){}
}
function restorePick(){
  try{
    const p=JSON.parse(localStorage.getItem(SAVE)||'null'); if(!p||!p.s) return;
    const ix=DATA.sido.indexOf(p.s); if(ix<0) return;
    $sido.value=String(ix); fillSgg();
    if(p.g && [...$sgg.options].some(o=>o.value===p.g)) $sgg.value=p.g;
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
    if(r[F.nurse]>0) tags.push('간호인력 '+r[F.nurse]+'명');
    if(r[F.rehab]>0) tags.push('물리·작업치료사 '+r[F.rehab]+'명');
    if(r[F.social]>0) tags.push('사회복지사 '+r[F.social]+'명');

    // 중앙값 수치는 상단 기준선에 한 번만. 카드에서는 방향만 말한다 (중복 제거)
    const cmp = good ? '중앙값보다 적습니다' : '중앙값보다 많습니다';

    const note = r[F.isNew]
      ? '<p class="new"><b>'+esc(r[F.since])+' 지정 · 개원 1년 미만</b>입니다. '
        + '문 연 지 얼마 안 된 곳은 정원은 인가받은 최대치인데 인력은 채워지는 중이라 '
        + '이 숫자가 <b>실제보다 나쁘게</b> 나옵니다. 숫자만으로 판단하지 마세요.</p>'
      : '';

    const q=encodeURIComponent(r[F.name]+' '+r[F.sigungu]);
    return '<li><div class="row">'
      + '<div class="rank">'+r.rank+'</div>'
      + '<div class="body">'
      +   '<p class="name">'+esc(r[F.name])+'</p>'
      +   '<p class="where">'+esc(r[F.sigungu]+' '+r[F.addr])+'</p>'
      +   '<div class="big"><span class="num'+(good?' good':'')+'">'+fmt(ratio)+'</span>'
      +     '<span class="unit">명 / 요양보호사 1명</span></div>'
      +   '<p class="calc">정원 '+r[F.cap]+'명 &divide; 요양보호사 '+r[F.care]+'명</p>'
      +   meter(ratio, med, good)
      +   '<p class="verdict"><span class="chip'+(good?' good':'')+'">'+cmp+'</span></p>'
      +   note
      +   (tags.length? '<p class="tags"><i>'+tags.join(' · ')+'</i></p>' : '')
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

$sido.addEventListener('change',()=>{ fillSgg(); render(); savePick(); setHash(); });
$sgg .addEventListener('change', ()=>{ render(); savePick(); setHash(); });
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
        .replace("__MEDIANNOTE__", m["medianNote"])
        .replace("__NEWCOUNT__", f"{m['newCount']:,}"))

os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    f.write(html)

print(f"생성 {out}  {os.path.getsize(out):,} bytes ({os.path.getsize(out)/1024:.0f} KB)")
print(f"  기관 {m['count']:,}곳 · 시도 {len(data['sido'])}개 · 시군구 {sum(len(v) for v in data['sigungu'].values())}개")
