# 전화번호 수집이 끝난 뒤 제출본을 끝까지 만드는 파이프라인.
#
# 한 번에 다 한다: 데이터 빌드 -> 화면 빌드 -> JS 구문 -> 독립 검증 -> 배포 -> 발표자료 PDF
# 중간에 실패하면 그 자리에서 멈춘다(배포 전에 검증이 먼저다).
# 여러 번 실행해도 안전하다.
#
# 실행: powershell -ExecutionPolicy Bypass -File tools\finish_build.ps1

$ErrorActionPreference = "Stop"
$p = "C:\Users\신운종\Desktop\과제_노인돌봄_공공데이터_20261012"
Set-Location $p
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

function Step($n) { Write-Host ""; Write-Host "=== $n ===" }

# 0. 수집이 아직 돌고 있으면 중단 — 반쪽 데이터로 빌드하지 않는다
$running = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
             Where-Object { $_.CommandLine -like "*fetch_tel*" }).Count
if ($running -gt 0) { Write-Host "### 수집이 아직 진행 중이다 ($running개). 끝난 뒤 다시 실행하라."; exit 1 }

$tel = (Get-Content "data\tel.json" -Raw -Encoding UTF8 | ConvertFrom-Json)
$telN = ($tel.PSObject.Properties | Measure-Object).Count
Write-Host "전화번호 $telN 건으로 빌드한다"

Step "1. 데이터 빌드 (3종 결합)"
python tools\build_data.py "data\ltc_20260610.xlsx" "data\day_care.json" "data\eval_20260625.csv"
if ($LASTEXITCODE -ne 0) { throw "build_data 실패" }

Step "2. 화면 빌드"
python tools\build_html.py "data\day_care.json" "돌봄밀도.html"
if ($LASTEXITCODE -ne 0) { throw "build_html 실패" }
Copy-Item "돌봄밀도.html" "build\index.html" -Force
Copy-Item "data\day_care.json" "build\data.json" -Force

Step "3. JS 구문 검사"
python -c @"
import re,io
h=io.open('build/index.html',encoding='utf-8').read()
io.open('build/_c.js','w',encoding='utf-8').write(re.search(r'<script>(.*?)</script>',h,re.S).group(1))
"@
node --check "build\_c.js"
if ($LASTEXITCODE -ne 0) { throw "JS 구문 오류" }
Remove-Item "build\_c.js" -Force

Step "4. 독립 검증 (빌더 코드 미재사용)"
$v = python tools\verify_screen.py "build\index.html" "data\ltc_20260610.xlsx" "data\eval_20260625.csv"
$verdict = $v | Select-Object -Last 1
Write-Host $verdict
if ($verdict -notmatch "값 불일치 0건" -or $verdict -notmatch "등급 불일치 0건") {
  throw "검증 실패 — 배포하지 않는다: $verdict"
}

Step "5. 동작 검증 (19건)"
Start-Process -FilePath $edge -ArgumentList '--headless=new','--disable-gpu','--hide-scrollbars',
  '--allow-file-access-from-files','--virtual-time-budget=14000','--window-size=1000,1400',
  "--screenshot=$p\_ux_check.png","file:///$p/tools/check_ux.html" -Wait

Step "6. 발표자료 PDF 재생성"
Remove-Item "발표자료.pdf" -Force -ErrorAction SilentlyContinue
Start-Process -FilePath $edge -ArgumentList '--headless=new','--disable-gpu','--no-pdf-header-footer',
  '--virtual-time-budget=12000',"--print-to-pdf=$p\발표자료.pdf","file:///$p/발표슬라이드.html" -Wait
python -c "import pymupdf; d=pymupdf.open('발표자료.pdf'); print('발표자료.pdf', d.page_count, '쪽')"

Step "7. 배포"
npx wrangler pages deploy build --project-name dolbomok --branch main --commit-dirty=true

Step "8. 라이브 확인"
Start-Sleep -Seconds 12
$u = "https://dolbomok.pages.dev/?cb=" + (Get-Random)
$r = Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 60 -Headers @{"Cache-Control"="no-cache"}
$localLen = (Get-Item "build\index.html").Length
Write-Host ("live $($r.StatusCode) · $($r.RawContentLength) bytes / 로컬 $localLen bytes")
if ($r.RawContentLength -ne $localLen) { Write-Host "### 라이브와 로컬 크기가 다르다 — 엣지 캐시일 수 있으니 재확인 필요" }
if ($r.Content -match 'telSlot') { Write-Host "전화 기능 반영 확인" }

Write-Host ""
Write-Host "=== 완료 ==="
Write-Host "전화번호 $telN 건 · $verdict"
