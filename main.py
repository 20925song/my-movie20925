import datetime
import requests
import pandas as pd
import pytz
import streamlit as st

# 1. 페이지 기본 설정 (타이틀 및 레이아웃)
st.set_page_config(page_title="어제 박스오피스", layout="wide")


# 2. 한국 시간 기준 '어제' 날짜 계산 함수
def get_yesterday_kst():
    # 한국 표준시(KST) 타임존 설정 (배포 서버 시계가 달라도 정확히 계산)
    kst = pytz.timezone("Asia/Seoul")
    now_kst = datetime.datetime.now(kst)
    yesterday = now_kst - datetime.timedelta(days=1)
    return yesterday.strftime("%Y%m%d")


# 3. KOBIS API 데이터 호출 함수 (Streamlit 캐시 활용)
# ttl=3600: 동일한 요청에 대해 1시간(3600초) 동안 결과를 기억하여 재요청을 방지합니다.
@st.cache_data(ttl=3600)
def fetch_box_office_data(api_key, target_date):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_date}

    try:
        response = requests.get(url, params=params, timeout=10)
        # HTTP 응답 상태 코드가 200이 아니면 예외 발생
        response.raise_for_status()
        data = response.json()
        return data, None
    except Exception as e:
        # 네트워크 오류 등 예외 발생 시 처리
        return None, f"API 요청 중 네트워크 오류가 발생했습니다: {e}"


# --- 메인 UI 시작 ---
st.title("🎬 어제자 일별 박스오피스")

# Secrets에서 KOBIS_KEY 인증키 불러오기
if "KOBIS_KEY" not in st.secrets:
    st.error(
        "Secrets에 'KOBIS_KEY'가 설정되어 있지 않습니다. Streamlit Cloud 설정에서 인증키를 등록해 주세요."
    )
    st.stop()

api_key = st.secrets["KOBIS_KEY"]
target_date = get_yesterday_kst()

# 날짜 표시 (YYYY-MM-DD 형식)
formatted_date = (
    f"{target_date[:4]}년 {target_date[4:6]}월 {target_date[6:]}일"
)
st.caption(f"기준일자: {formatted_date} (한국 시간 기준 어제)")

# 데이터 불러오기
data, error_msg = fetch_box_office_data(api_key, target_date)

# 4. 예외 및 오류 처리
if error_msg:
    st.error(error_msg)
    st.info(
        "💡 **확인해 보세요:** 인터넷 연결 상태를 확인하시거나 잠시 후 다시 시도해 주세요."
    )
    st.stop()

# API 응답 내 faultInfo(키 오류 등) 검증
if "faultInfo" in data:
    fault_message = data["faultInfo"].get("message", "알 수 없는 오류")
    st.error(f"API 오류가 발생했습니다: {fault_message}")
    st.info(
        "💡 **확인해 보세요:** secrets.toml 또는 Streamlit Cloud Secrets에 입력한 `KOBIS_KEY`가 올바른지 확인해 주세요."
    )
    st.stop()

# 영화 데이터 목록 추출 및 빈 데이터 검증
boxoffice_result = data.get("boxOfficeResult", {})
daily_list = boxoffice_result.get("dailyBoxOfficeList", [])

if not daily_list:
    st.warning("박스오피스 데이터가 비어 있습니다.")
    st.info(
        "💡 **확인해 보세요:** 아직 해당 날짜의 집계가 완료되지 않았거나 KOBIS 서비스 점검 중일 수 있습니다."
    )
    st.stop()


# 5. 데이터 가공 (문자열 -> 숫자 변환)
df = pd.DataFrame(daily_list)

# 필요한 컬럼 숫자로 형변환
numeric_columns = [
    "rank",
    "rankInten",
    "audiCnt",
    "audiAcc",
    "scrnCnt",
    "showCnt",
]
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# 순위 기준으로 정렬
df = df.sort_values(by="rank")


# 6. 1위 영화 지표 카드 (Metrics)
top_movie = df.iloc[0]

st.subheader(f"🥇 1위: {top_movie['movieNm']}")

col1, col2, col3 = st.columns(3)

# 당일 관객수 및 전일 대비 순위 변환
rank_inten = int(top_movie["rankInten"])
if rank_inten > 0:
    delta_str = f"▲ {rank_inten}"
elif rank_inten < 0:
    delta_str = f"▼ {abs(rank_inten)}"
else:
    delta_str = "변동 없음"

col1.metric(
    label="어제 관객수",
    value=f"{int(top_movie['audiCnt']):,} 명",
    delta=delta_str,
)
col2.metric(label="누적 관객수", value=f"{int(top_movie['audiAcc']):,} 명")
col3.metric(label="스크린 수", value=f"{int(top_movie['scrnCnt']):,} 개")

st.divider()


# 7. 관객수 상위 5편 막대그래프
st.subheader("📊 관객수 상위 5개 영화")

top5_df = df.head(5).copy()
# 시각화를 위해 관객수 내림차순 정렬
top5_df = top5_df.sort_values(by="audiCnt", ascending=True)

# Streamlit 기본 차트 사용 (x: 영화명, y: 어제 관객수)
st.bar_chart(
    data=top5_df,
    x="movieNm",
    y="audiCnt",
    color="#FF4B4B",
    use_container_width=True,
)

st.divider()


# 8. 전체 박스오피스 순위 표
st.subheader("📋 전체 순위 목록")

# 표에 보여 줄 컬럼 선택 및 이름 변경
display_df = df[
    ["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]
].copy()
display_df.columns = [
    "순위",
    "영화명",
    "개봉일",
    "관객수(명)",
    "누적관객(명)",
    "스크린수",
]

# 데이터프레임 출력 (숫자 세 자리마다 콤마 포맷 적용)
st.dataframe(
    display_df.style.format(
        {"관객수(명)": "{:,.0f}", "누적관객(명)": "{:,.0f}", "스크린수": "{:,.0f}"}
    ),
    hide_index=True,
    use_container_width=True,
)
