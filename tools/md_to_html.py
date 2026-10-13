"""Markdown -> 인쇄용 HTML (기획서 PDF 출력 전 단계).

실행:  python tools/md_to_html.py 웹서비스_기획서.md _tmp.html
그다음 Edge --headless 로 --print-to-pdf 하면 된다.
"""
import sys, io
import markdown

src_path = sys.argv[1]
out_path = sys.argv[2]

src = io.open(src_path, encoding="utf-8").read()
body = markdown.markdown(src, extensions=["tables", "fenced_code", "sane_lists"])

CSS = """
@page { size: A4; margin: 16mm 14mm; }
body { font-family: "Malgun Gothic","맑은 고딕",sans-serif; font-size: 10.5pt;
       line-height: 1.6; color: #1b2220; }
h1 { font-size: 19pt; border-bottom: 2px solid #0a6b5c; padding-bottom: 6px; margin-top: 22px; }
h2 { font-size: 14pt; color: #0a6b5c; margin-top: 20px; }
h3 { font-size: 11.5pt; margin-top: 16px; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 9.5pt; }
th, td { border: 1px solid #d8d2c6; padding: 5px 7px; text-align: left; vertical-align: top; }
th { background: #f0eae2; font-weight: 700; }
/* 첫 열은 항목명이라 어색하게 쪼개지지 않도록 폭을 확보한다 */
td:first-child { width: 20%; }
blockquote { border-left: 3px solid #0a6b5c; margin: 10px 0; padding: 4px 14px; background: #f7f4ee; }
code { background: #f0eae2; padding: 1px 4px; border-radius: 3px; font-size: 9.5pt; }
hr { border: 0; border-top: 1px solid #e0dacd; margin: 18px 0; }
tr, blockquote, pre { page-break-inside: avoid; }
h1, h2, h3 { page-break-after: avoid; }
"""

html = (
    '<!DOCTYPE html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
    "<style>" + CSS + "</style>\n</head>\n<body>\n" + body + "\n</body>\n</html>\n"
)

io.open(out_path, "w", encoding="utf-8").write(html)
print("생성 %s  %d chars" % (out_path, len(html)))
