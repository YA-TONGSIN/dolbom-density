# 주야간보호센터 돌봄 밀도 비교

## 프로젝트 소개
- 보호자가 부모님 동네 주야간보호센터를 "요양보호사 1인당 어르신 수"로 비교하는 한 장짜리 웹페이지
- 공공데이터 1종(국민건강보험공단_장기요양기관 시설별 현황, ID 15124763)만 사용
- 서버 없이 build 폴더의 파일만으로 동작하며, 공개 주소는 https://dolbomok.pages.dev

## 규칙
- 모든 구현은 PLAN.md를 근거로 한다
- PLAN.md에 없는 기능은 만들지 않는다
- 기획이 바뀌면 PLAN.md를 먼저 고치고, 그다음 코드를 고친다
- 인증키는 build 폴더 안 어디에도 넣지 않는다

## 데이터
- 데이터는 build/data.json
- 원본은 data/ltc_20260610.xlsx 이고, tools/build_data.py 로 build/data.json 을 만든다
- 화면(build/index.html)은 같은 데이터를 파일 안에 내장해 읽는다 (tools/build_html.py)

## 배포
- 배포는 build 폴더만
