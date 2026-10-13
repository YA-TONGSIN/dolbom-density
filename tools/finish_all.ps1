# 제출본을 끝까지 만드는 단일 명령.
#
#   A. tools\finish_build.ps1  (수집중 확인 -> 데이터·화면 빌드 -> JS 구문 -> 독립 검증 -> 동작검증 -> PDF -> 배포 -> 라이브 확인)
#   B. 빌드 결과에서 "전화번호 있는 곳 N곳(P%)" 을 실측해 문서 7종의 __TELN__ / __TELPCT__ 치환
#   C. 발표슬라이드.html 이 바뀌었으면 발표자료.pdf 재생성
#   D. 발표 분량 재측정 (tools\time_script.py)
#   E. git 커밋·푸시 (apikey 스테이징 시 중단 · data/_probe 제외)
#   F. OneDrive 에 다시 올릴 파일 2개의 경로·크기 출력
#
# 검증이 실패하면 A 단계에서 배포 전에 멈춘다. 여러 번 실행해도 안전하다.
#
# 실행:  powershell -ExecutionPolicy Bypass -File tools\finish_all.ps1

$ErrorActionPreference = "Stop"
$p = "C:\Users\신운종\Desktop\과제_노인돌봄_공공데이터_20261012"
Set-Location $p
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$log  = Join-Path $p "_finish_log.txt"

# 파이썬·콘솔 출력 인코딩을 UTF-8 로 맞춘다 (한글 출력이 로그에서 깨지지 않도록)
$env:PYTHONIOENCODING = "utf-8"
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

function Step($n) { Write-Host ""; Write-Host "=== $n ===" -ForegroundColor Cyan }

# ─────────────────────────────────────────────────────────────────────
Step "A. 빌드 · 검증 · 배포"
# ─────────────────────────────────────────────────────────────────────
& powershell -ExecutionPolicy Bypass -File (Join-Path $p "tools\finish_build.ps1") 2>&1 |
    Tee-Object -FilePath $log
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "### A 단계 실패 (exit $LASTEXITCODE). 배포·치환을 하지 않고 멈춘다." -ForegroundColor Red
    Write-Host "### 전체 출력: $log"
    exit 1
}

# ─────────────────────────────────────────────────────────────────────
Step "B. 실측 수치로 자리표시자 치환"
# ─────────────────────────────────────────────────────────────────────
# 로그 문자열을 파싱하지 않고, 빌드가 만든 day_care.json 에서 직접 센다.
# (build_data.py 의 '전화번호 있는 곳' 과 같은 정의: tel 칸이 빈 문자열이 아닌 기관 수 / 전체)
$raw = python -c "import json;d=json.load(open('data/day_care.json',encoding='utf-8'));i=d['fields'].index('tel');n=sum(1 for r in d['items'] if r[i]);t=len(d['items']);print(n);print(t);print(round(n/t*100,1))"
if ($LASTEXITCODE -ne 0 -or $raw.Count -lt 3) { throw "day_care.json 에서 전화번호 수를 세지 못했다" }

$telN    = [int]$raw[0]
$total   = [int]$raw[1]
$telPct  = $raw[2].Trim()
$telNfmt = "{0:N0}" -f $telN
Write-Host "전화번호 있는 곳 $telNfmt 곳 / 전체 $("{0:N0}" -f $total) 곳  ($telPct%)"

$files = @("PLAN.md", "README.md", "발표슬라이드.html", "발표_대본.md",
           "발표_스크립트.md", "웹서비스_기획서.md", "이것부터 읽기.txt")
$utf8NoBom   = New-Object System.Text.UTF8Encoding($false)
$slideChanged = $false

foreach ($f in $files) {
    $fp = Join-Path $p $f
    if (-not (Test-Path -LiteralPath $fp)) { Write-Host "  (파일 없음) $f" -ForegroundColor Yellow; continue }
    $old = [System.IO.File]::ReadAllText($fp, [System.Text.Encoding]::UTF8)
    $new = $old.Replace('__TELN__', $telNfmt).Replace('__TELPCT__', $telPct)
    if ($new -ne $old) {
        [System.IO.File]::WriteAllText($fp, $new, $utf8NoBom)
        Write-Host "  치환함    $f"
        if ($f -eq "발표슬라이드.html") { $slideChanged = $true }
    } else {
        Write-Host "  변경없음  $f"
    }
}

# 남은 자리표시자가 하나도 없어야 한다
$existing = $files | ForEach-Object { Join-Path $p $_ } | Where-Object { Test-Path -LiteralPath $_ }
$left = Select-String -LiteralPath $existing -Pattern '__TELN__|__TELPCT__'
if ($left) {
    Write-Host "### 자리표시자가 남아 있다 — 커밋하지 않는다:" -ForegroundColor Red
    $left | ForEach-Object { Write-Host "    $($_.Path) : $($_.LineNumber)" }
    exit 1
}
Write-Host "남은 __TELN__ / __TELPCT__ : 0건"

# ─────────────────────────────────────────────────────────────────────
Step "C. 발표자료 PDF"
# ─────────────────────────────────────────────────────────────────────
if ($slideChanged) {
    Remove-Item "발표자료.pdf" -Force -ErrorAction SilentlyContinue
    Start-Process -FilePath $edge -ArgumentList '--headless=new','--disable-gpu','--no-pdf-header-footer',
        '--virtual-time-budget=12000',"--print-to-pdf=$p\발표자료.pdf","file:///$p/발표슬라이드.html" -Wait
    python -c "import pymupdf; d=pymupdf.open('발표자료.pdf'); print('발표자료.pdf', d.page_count, '쪽')"
} else {
    Write-Host "발표슬라이드.html 이 바뀌지 않았다 — A 단계에서 만든 PDF 를 그대로 쓴다"
}

# ─────────────────────────────────────────────────────────────────────
Step "D. 발표 분량 재측정 (느리게 말해도 180초 안이어야 한다)"
# ─────────────────────────────────────────────────────────────────────
python tools\time_script.py 발표_스크립트.md

# ─────────────────────────────────────────────────────────────────────
Step "E. 커밋 · 푸시"
# ─────────────────────────────────────────────────────────────────────
$ErrorActionPreference = "Continue"   # git 은 진행상황을 stderr 로 쓴다
git add -A
git reset HEAD data/_probe 2>&1 | Out-Null
$staged = @(git diff --cached --name-only)
$bad = $staged | Where-Object { $_ -match 'apikey' -or $_ -match '\.key$' }
if ($bad) {
    Write-Host "### 인증키 파일이 스테이지에 올라와 있다 — 커밋을 중단한다:" -ForegroundColor Red
    $bad | ForEach-Object { Write-Host "    $_" }
    exit 1
}
Write-Host "스테이지된 파일 $($staged.Count)개 (apikey 없음 확인)"
if ($staged.Count -eq 0) {
    Write-Host "커밋할 변경이 없다"
} else {
    git commit -m "전화번호(데이터 3종) 반영 · 문서 수치를 실측값으로 치환"
    git push
    if ($LASTEXITCODE -ne 0) { Write-Host "### git push 실패 — 로컬 커밋은 남아 있다" -ForegroundColor Red }
}
$ErrorActionPreference = "Stop"

# ─────────────────────────────────────────────────────────────────────
Step "F. OneDrive 에 다시 올릴 파일 (기존 것에 덮어쓰기)"
# ─────────────────────────────────────────────────────────────────────
Get-Item -LiteralPath (Join-Path $p "PLAN.md"), (Join-Path $p "발표자료.pdf") |
    Format-Table @{n='파일';e={$_.Name}},
                 @{n='크기';e={ if ($_.Length -ge 1MB) { "{0:N2} MB" -f ($_.Length/1MB) } else { "{0:N1} KB" -f ($_.Length/1KB) } }},
                 @{n='수정시각';e={$_.LastWriteTime.ToString('MM-dd HH:mm')}},
                 @{n='경로';e={$_.FullName}} -AutoSize

Write-Host ""
Write-Host "=== 전부 완료 ===" -ForegroundColor Green
Write-Host "전화번호 있는 곳 $telNfmt 곳 / $("{0:N0}" -f $total) 곳 ($telPct%)"
Write-Host "휴대폰에서 https://dolbomok.pages.dev 를 새로고침하고 관악구 · 청주시에서 전화 버튼을 눌러 볼 것"
Write-Host "전체 출력 로그: $log"
