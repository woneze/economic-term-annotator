import streamlit as st
from styles import CSS_STYLE  # 스타일 가져오기
from logic import init_kiwi_and_data, annotate_text_with_kiwi # 로직 가져오기

# 설정
st.set_page_config(page_title="경제 용어 AI 주석기", page_icon="💰", layout="wide")
JSON_FILE = "data/economic_terms_ai_summary.json"

def main():
    # 스타일 적용
    st.markdown(CSS_STYLE, unsafe_allow_html=True)
    
    # UI 구성
    st.title("경제 용어 AI 주석기")
    st.markdown("경제 관련 용어에 대한 주석을 달아줍니다.")

    # 로직 호출
    term_dict, kiwi = init_kiwi_and_data(JSON_FILE)

    if not term_dict:
        st.error(f"데이터 파일({JSON_FILE})을 찾을 수 없습니다.")
        return

    with st.sidebar:
        st.success(f"{len(term_dict)}개 용어 데이터 로드 완료")

    # 사용자 입력 및 처리
    default_text = """
    최근 미국의 기준금리 인상 가능성이 높아지면서 인플레이션 압력이 거세지고 있습니다. 
    이에 따라 소비자물가지수(CPI)가 예상치를 상회하였으며...
    """
    user_input = st.text_area("텍스트 입력", value=default_text, height=200)

    if st.button("분석 시작", type="primary"):
        with st.spinner("분석 중..."):
            # 로직 호출
            final_html, count = annotate_text_with_kiwi(user_input, term_dict, kiwi)
            
            st.subheader(f"결과 ({count}개 발견)")
            st.markdown(f'<div class="text-output">{final_html}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()