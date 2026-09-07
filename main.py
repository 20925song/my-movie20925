어제의 박스오피스를 보여 주는 스트림릿 앱 하나(main.py)를 만들어 줘. 스트림릿 클라우드에 올릴 거야.
아래에 공식 API 문서에서 복사한 내용을 붙였어.

- 인증키는 비밀 금고(secrets)의 KOBIS_KEY에서 불러와. 코드에는 절대 쓰지 마.
- 조회 날짜는 고정하지 말고 '어제'를 자동으로 계산해서 써. 오늘 건 아직 집계 전이거든.
  '어제'는 한국 시간 기준이야. 배포 서버 시계는 한국 시간이 아니야.
- 순위·영화명·개봉일·관객수·누적관객·스크린수를 표로 보여 줘.
- 1위 영화는 지표 카드 세 장으로 크게, 관객수 상위 5편은 막대그래프로.
- 숫자가 글자로 오니 숫자로 바꿔서 정렬과 그래프에 써 줘.
- 같은 날짜를 다시 물으면 API를 또 부르지 말고, 불러온 결과를 한 시간쯤 기억해 줘.
- 요청이 실패하거나, 오류 상자(faultInfo)가 오거나, 영화 목록이 비어서 올 때는
  빈 화면 대신 무엇을 확인해야 하는지 한국어로 안내해 줘.
- 필요한 라이브러리 목록(requirements.txt)도 같이 줘. 버전 숫자 없이 이름만.
- 초보자용 한국어 주석을 달고 main.py 전체 코드를 한 번에 줘.

──── 아래는 KOBIS 공식 문서에서 복사한 부분 ────
요청 주소: https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json
요청변수: key(발급받은 인증키) · targetDt(조회 날짜, yyyymmdd 여덟 자리)
응답 구조: boxOfficeResult 안의 dailyBoxOfficeList 목록에 영화별로
  rank(순위) · rankInten(전날 대비 순위 증감) · movieNm(영화명) · openDt(개봉일) ·
  audiCnt(그날 관객수) · audiAcc(누적 관객수) · scrnCnt(스크린수) · showCnt(상영횟수)
  ※ 숫자 값이 전부 문자열로 온다.
  ※ 인증키가 틀려도 상태코드는 200이고, 대신 faultInfo 상자가 온다.
