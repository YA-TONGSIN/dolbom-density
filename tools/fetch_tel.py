"""장기요양기관 전화번호 수집 — 데이터 ③ 상세조회 API (15058856).

왜 API인가: 전화번호는 ①시설별 현황(4개 시트)에도 ②평가 결과(20개 컬럼)에도 없다.
            직접 확인했고, PLAN 4번에 "없음"으로 적어 둔 그 칸이다.

호출: getGeneralSttusDetailInfoItem02
      필수 파라미터 longTermAdminSym(기관기호) + adminPttnCd(기관유형코드)
      둘 다 ①에서 이미 갖고 있으므로 기관 목록을 따로 받을 필요가 없다.

실제 응답에서 확인한 것 (문서와 달랐던 부분):
  - 전화번호 필드는 **locTelNo_1 / locTelNo_2 / locTelNo_3** — 밑줄이 들어간다.
    가이드 표에는 locTelNo1 로 적혀 있어 처음에 0건이 나왔다.
  - 가이드의 "30 TPS"는 운영계정 기준으로 보인다. 개발계정은 훨씬 빡빡하고,
    한 번 429에 걸리면 한동안 계속 429가 난다(패널티 창). 그래서 **순차 + 적응형 간격**으로 간다.

중단해도 안전하다: 진행분을 주기적으로 저장하고, 다시 실행하면 이어서 받는다.

인증키: apikey.txt (또는 data/apikey.txt, _apikey.txt). .gitignore 가 *apikey*.txt 로 막는다.

실행:
  python tools/fetch_tel.py data/ltc_20260610.xlsx data/tel.json
  python tools/fetch_tel.py data/ltc_20260610.xlsx data/tel.json --limit 30
"""
import sys, os, json, time, io, re
import urllib.parse, urllib.request, urllib.error
import xml.etree.ElementTree as ET
import pandas as pd

xlsx = sys.argv[1] if len(sys.argv) > 1 else "data/ltc_20260610.xlsx"
out = sys.argv[2] if len(sys.argv) > 2 else "data/tel.json"
limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None

BASE = ("http://apis.data.go.kr/B550928/getLtcInsttDetailInfoService02"
        "/getGeneralSttusDetailInfoItem02")
TYPES = ["B03", "C03"]

DELAY0, DELAY_MIN, DELAY_MAX = 0.45, 0.30, 4.0   # 적응형 간격(초)
PENALTY = 20.0        # 429를 만나면 이만큼 쉰다 (패널티 창을 빠져나오기 위해)
SAVE_EVERY = 100


def load_key():
    k = os.environ.get("LTC_API_KEY", "").strip()
    if k:
        return k
    for p in ("apikey.txt", "data/apikey.txt", "data/_apikey.txt", "_apikey.txt"):
        if os.path.exists(p):
            k = io.open(p, encoding="utf-8").read().strip()
            if k:
                return k
    sys.exit("인증키가 없다. apikey.txt 에 넣어라.")


KEY = load_key()
# data.go.kr은 Encoding 키(%2B 포함)와 Decoding 키(원문)를 둘 다 준다. 어느 쪽이든 받는다.
KEY_PARAM = KEY if "%" in KEY else urllib.parse.quote(KEY, safe="")

TEL_RE = re.compile(r"\d{2,4}-\d{3,4}-\d{4}")


def parse_tel(body):
    root = ET.fromstring(body)
    if (root.findtext(".//resultCode") or "00") not in ("00", "0"):
        return None
    parts = [(root.findtext(".//locTelNo_%d" % i) or "").strip() for i in (1, 2, 3)]
    if not all(parts):
        return None
    tel = "-".join(parts)
    return tel if TEL_RE.fullmatch(tel) else None


# ── 대상 기관 (①에서 그대로) ──────────────────────────────────────────────
xl = pd.ExcelFile(xlsx)
cap = pd.read_excel(xl, "입소인원")
day = cap[cap["기관유형코드"].isin(TYPES)][["장기요양기관코드", "기관유형코드"]].drop_duplicates()
targets = [(str(r["장기요양기관코드"]).strip(), str(r["기관유형코드"]).strip())
           for _, r in day.iterrows()]
if limit:
    targets = targets[:limit]

# 이어받기: 이미 받아 둔 건 건너뛴다
result = {}
if os.path.exists(out):
    try:
        result = json.load(io.open(out, encoding="utf-8"))
        print("기존 %s 에서 %d곳 이어받기" % (out, len(result)))
    except Exception:
        result = {}
todo = [t for t in targets if t[0] not in result]
print("대상 %d곳 · 남은 %d곳" % (len(targets), len(todo)))


def save():
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    tmp = out + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, out)


delay = DELAY0
hit429 = miss = 0
t0 = time.time()

for n, (code, pttn) in enumerate(todo, 1):
    url = "%s?serviceKey=%s&longTermAdminSym=%s&adminPttnCd=%s" % (BASE, KEY_PARAM, code, pttn)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                body = r.read()
            tel = parse_tel(body)
            if tel:
                result[code] = tel
            else:
                miss += 1
            delay = max(DELAY_MIN, delay * 0.97)      # 잘 되면 조금씩 빠르게
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                hit429 += 1
                delay = min(DELAY_MAX, delay * 1.6)   # 걸리면 느리게
                time.sleep(PENALTY)
                continue
            miss += 1
            break
        except Exception:
            if attempt == 4:
                miss += 1
                break
            time.sleep(1.5 * (attempt + 1))
    else:
        miss += 1

    if n % SAVE_EVERY == 0:
        save()
        el = time.time() - t0
        rate = n / max(el, 1)
        eta = (len(todo) - n) / max(rate, 0.01) / 60
        print("  %d/%d · 수집 %d · 429 %d · %.1f건/초 · 남은 %.0f분 (간격 %.2fs)"
              % (n, len(todo), len(result), hit429, rate, eta, delay))
    time.sleep(delay)

save()
el = time.time() - t0
print()
print("저장 %s · %d곳 (%.1f%%) · %.0f분" %
      (out, len(result), len(result) / max(len(targets), 1) * 100, el / 60))
print("못 받은 곳 %d — 빈칸으로 두고 화면에서는 「검색하기」로 보낸다 (429 %d회)"
      % (len(targets) - len(result), hit429))
