"""발표 대본의 실제 '말하는 분량'을 재서 3분 안에 들어가는지 확인한다.

내용을 고치면 시간이 늘어난다. "175초"는 한 번 재놓고 끝낼 숫자가 아니라
대본을 고칠 때마다 다시 재야 하는 숫자다.

말하지 않는 것은 빼고 센다:
  - `( ... )` 로 시작하는 지문 줄 (→ 슬라이드 넘기기, 화면 조작 등)
  - 표 행(`|`), 머리말(`#`), 수평선(`---`), 체크리스트(`- [ ]`)
  - "시간이 밀릴 때 자르는 순서" 이후, "예상 질문" 이후 전부

환산 기준: 한국어 발표 속도 5.3음절/초 (≈318음절/분).
  뉴스 낭독 ≈5.0 · 평상 대화 6.5~7.0 · 심사 발표는 그 사이.
  여유를 보기 위해 느린 쪽(4.8)도 함께 출력한다.

실행: python tools/time_script.py 발표_대본.md
"""
import sys, re, io

path = sys.argv[1] if len(sys.argv) > 1 else "발표_대본.md"
RATE, RATE_SLOW = 5.3, 4.8
LIMIT = 180

text = io.open(path, encoding="utf-8").read()

# 발표 본문만 남긴다 — 뒤쪽 부록(자르는 순서·예상 질문·체크리스트)은 말하는 분량이 아니다
for marker in ("# 예상 질문", "## 시간이 밀릴 때", "# 시간이 부족하면", "## 발표 직전 체크"):
    i = text.find(marker)
    if i > 0:
        text = text[:i]

# `## 머리말` 단위로 쪼갠다 (대본은 `## [슬라이드 N …] — 30초`, 스크립트는 `## ① … — 30초`)
parts = re.split(r"^##\s+(.+?)\s*$", text, flags=re.M)

SKIP = re.compile(r"^\s*(\(|\||---|===|- \[|>?\s*\*\*참고|\d+\.\s)")

def spoken(body):
    out = []
    for line in body.split("\n"):
        s = line.strip()
        if not s or SKIP.match(s):
            continue
        s = re.sub(r"^>\s*", "", s)                 # 인용 기호는 낭독문 표기라 벗겨서 센다
        s = re.sub(r"\([^)]*\)", " ", s)            # 줄 안의 괄호 지문
        s = re.sub(r"[*_`#\[\]]", " ", s)           # 마크다운 기호
        out.append(s)
    return " ".join(out)

def syllables(s):
    ko = len(re.findall(r"[가-힣]", s))
    digits = len(re.findall(r"\d", s))
    latin = len(re.findall(r"[A-Za-z]", s))
    return ko + digits + latin // 2

total = 0.0
rows = []
for i in range(1, len(parts), 2):
    title = parts[i].strip()
    syl = syllables(spoken(parts[i + 1]))
    if syl == 0:
        continue
    sec = syl / RATE
    m = re.search(r"—\s*(\d+)\s*초", title)
    budget = int(m.group(1)) if m else None
    total += sec
    rows.append((re.sub(r"\s*—.*$", "", title), syl, sec, syl / RATE_SLOW, budget))

print("=" * 76)
print(f"{'구간':<32}{'음절':>6}{'예상(5.3)':>11}{'느리게(4.8)':>12}{'배정':>7}{'판정':>7}")
print("-" * 76)
over = []
for title, syl, sec, slow, budget in rows:
    if budget:
        flag = "OK" if sec <= budget else f"+{sec - budget:.0f}s"
        if sec > budget:
            over.append((title, sec - budget))
    else:
        flag = "-"
    b = f"{budget}s" if budget else "-"
    print(f"{title[:30]:<32}{syl:>6}{sec:>10.0f}s{slow:>11.0f}s{b:>7}{flag:>7}")

slow_total = total * RATE / RATE_SLOW
print("-" * 76)
print(f"{'합계':<32}{'':>6}{total:>10.0f}s{slow_total:>11.0f}s")
print()
print(f"3분(180초) 기준 — 보통 {total:.0f}초 · 느리게 {slow_total:.0f}초")
if slow_total <= LIMIT:
    print(f"  느리게 말해도 {LIMIT - slow_total:.0f}초 여유. 들어간다")
elif total <= LIMIT:
    print(f"  보통 속도면 {LIMIT - total:.0f}초 여유. 다만 느려지면 {slow_total - LIMIT:.0f}초 초과 — 줄이는 게 안전")
else:
    print(f"  ### 보통 속도로도 {total - LIMIT:.0f}초 초과 — 반드시 줄일 것")
for t, d in sorted(over, key=lambda x: -x[1])[:4]:
    print(f"    배정 초과: {t} +{d:.0f}초")
