"""장기요양기관 전화번호 수집 — 데이터 ③ 상세조회 API (15058856).

왜 API인가: 전화번호는 ①시설별 현황(4개 시트)에도 ②평가 결과(20개 컬럼)에도 없다.
            직접 확인했고, PLAN 4번에 "없음"으로 적어 둔 그 칸이다.

호출: getGeneralSttusDetailInfoItem02
      필수 파라미터 longTermAdminSym(기관기호) + adminPttnCd(기관유형코드)
      둘 다 ①에서 이미 갖고 있으므로 기관 목록을 따로 받을 필요가 없다.
      응답의 locTelNo1/2/3 = 지역·국번·번호.

제약: 30 TPS. 기본 동시 10으로 돌린다(여유). 실패는 재시도하고, 끝까지 실패하면 빈칸으로 둔다.
      **빈칸을 지어내지 않는다.** 못 받은 기관은 화면에서 종전처럼 「검색하기」로 보낸다.

인증키: 환경변수 LTC_API_KEY, 또는 data/_apikey.txt 첫 줄.
        둘 다 .gitignore에 있고 build/ 에는 절대 들어가지 않는다.

실행: python tools/fetch_tel.py data/ltc_20260610.xlsx data/tel.json
      python tools/fetch_tel.py data/ltc_20260610.xlsx data/tel.json --limit 20   (시험용)
"""
import sys, os, json, time, io, re
import urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET
import pandas as pd

xlsx = sys.argv[1] if len(sys.argv) > 1 else "data/ltc_20260610.xlsx"
out = sys.argv[2] if len(sys.argv) > 2 else "data/tel.json"
limit = None
if "--limit" in sys.argv:
    limit = int(sys.argv[sys.argv.index("--limit") + 1])

BASE = ("http://apis.data.go.kr/B550928/getLtcInsttDetailInfoService02"
        "/getGeneralSttusDetailInfoItem02")
WORKERS = 10          # 30 TPS 상한 대비 여유
RETRY = 3
TYPES = ["B03", "C03"]


def load_key():
    k = os.environ.get("LTC_API_KEY", "").strip()
    if k:
        return k
    for p in ("data/_apikey.txt", "_apikey.txt"):
        if os.path.exists(p):
            k = io.open(p, encoding="utf-8").read().strip()
            if k:
                return k
    sys.exit("인증키가 없다. 환경변수 LTC_API_KEY 또는 data/_apikey.txt 에 넣어라.")


KEY = load_key()


# data.go.kr은 Encoding 키와 Decoding 키를 둘 다 준다. 섞어 쓰면 전량 인증 실패다.
#   Encoding 키: 이미 URL 인코딩됨(%2B, %3D 포함) → 그대로 붙여야 한다
#   Decoding 키: 원문(+, /, = 포함)           → 반드시 인코딩해야 한다 (+가 공백으로 해석됨)
# 어느 쪽을 넣든 돌아가게 '%' 포함 여부로 판별한다.
KEY_IS_ENCODED = "%" in KEY
KEY_PARAM = KEY if KEY_IS_ENCODED else urllib.parse.quote(KEY, safe="")
print("인증키 형식: %s" % ("Encoding(그대로 사용)" if KEY_IS_ENCODED else "Decoding(인코딩해서 사용)"))


def fetch(code, pttn):
    """기관 하나의 전화번호. 못 받으면 None (빈칸으로 둔다)."""
    qs = "serviceKey=%s&longTermAdminSym=%s&adminPttnCd=%s" % (
        KEY_PARAM,
        urllib.parse.quote(str(code), safe=""),
        urllib.parse.quote(str(pttn), safe=""),
    )
    url = BASE + "?" + qs
    for attempt in range(RETRY):
        try:
            with urllib.request.urlopen(url, timeout=12) as r:
                body = r.read()
            root = ET.fromstring(body)
            rc = root.findtext(".//resultCode")
            if rc not in (None, "00", "0"):
                msg = (root.findtext(".//resultMsg") or "")[:60]
                # 키 문제는 재시도해도 소용없다 — 바로 멈춘다
                if "SERVICE" in msg.upper() or "KEY" in msg.upper():
                    return ("FATAL", msg)
                return None
            parts = [root.findtext(".//locTelNo%d" % i) for i in (1, 2, 3)]
            parts = [(p or "").strip() for p in parts]
            if not all(parts):
                return None
            tel = "-".join(parts)
            # 숫자-숫자-숫자 형태만 받는다
            return tel if re.fullmatch(r"\d{2,4}-\d{3,4}-\d{4}", tel) else None
        except Exception:
            if attempt == RETRY - 1:
                return None
            time.sleep(0.4 * (attempt + 1))
    return None


# ── 대상 기관 목록 (①에서 그대로) ─────────────────────────────────────────
xl = pd.ExcelFile(xlsx)
cap = pd.read_excel(xl, "입소인원")
day = cap[cap["기관유형코드"].isin(TYPES)][["장기요양기관코드", "기관유형코드"]].drop_duplicates()
targets = [(str(r["장기요양기관코드"]).strip(), str(r["기관유형코드"]).strip())
           for _, r in day.iterrows()]
if limit:
    targets = targets[:limit]
print("대상 %d곳 · 동시 %d" % (len(targets), WORKERS))

result, fatal = {}, []
done = [0]
t0 = time.time()


def work(t):
    code, pttn = t
    v = fetch(code, pttn)
    done[0] += 1
    if done[0] % 250 == 0:
        el = time.time() - t0
        print("  %d/%d  %.0f초  수집 %d" % (done[0], len(targets), el, len(result)))
    if isinstance(v, tuple):
        fatal.append(v[1])
        return
    if v:
        result[code] = v


with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    list(ex.map(work, targets))

if fatal:
    sys.exit("### 인증키 오류로 중단: " + fatal[0])

os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
with io.open(out, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, separators=(",", ":"))

el = time.time() - t0
print()
print("저장 %s · %d곳 (%.1f%%) · %.0f초" %
      (out, len(result), len(result) / max(len(targets), 1) * 100, el))
print("못 받은 곳 %d — 빈칸으로 두고 화면에서는 「검색하기」로 보낸다" %
      (len(targets) - len(result)))
