import streamlit as st
import json
import os
from kiwipiepy import Kiwi  # 형태소 분석기

# 페이지 및 파일 경로
st.set_page_config(page_title="경제 용어 AI 주석기", page_icon="💰", layout="wide")
JSON_FILE = "data/economic_terms_ai_summary.json"

# CSS 스타일
def inject_custom_css():
    st.markdown("""
    <style>
        .term-highlight {
            background-color: #fff700;
            color: #333;
            font-weight: bold;
            padding: 0 4px;
            border-radius: 4px;
            cursor: help;
            border-bottom: 2px solid #ffcc00;
            position: relative;
            display: inline-block;
        }
        .term-highlight .tooltip-text {
            visibility: hidden;
            width: 300px;
            background-color: #2c3e50;
            color: #fff;
            text-align: left;
            border-radius: 8px;
            padding: 15px;
            position: absolute;
            z-index: 1000;
            bottom: 130%;
            left: 50%;
            margin-left: -150px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.9rem;
            line-height: 1.5;
            font-weight: normal;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        .term-highlight .tooltip-text::after {
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #2c3e50 transparent transparent transparent;
        }
        .term-highlight:hover .tooltip-text {
            visibility: visible;
            opacity: 1;
        }
        .text-output {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            border: 1px solid #ddd;
            line-height: 2.0;
            font-size: 1.1rem;
        }
    </style>
    """, unsafe_allow_html=True)

# JSON 데이터 로드 및 Kiwi 초기화
@st.cache_resource
def init_kiwi_and_data(filepath):
    if not os.path.exists(filepath):
        return None, None

    with open(filepath, 'r', encoding='utf-8') as f:
        term_dict = json.load(f)

    # Kiwi 초기화
    kiwi = Kiwi()
    
    # 경제 용어들을 고유 명사(NNP)로 사전에 추가
    for term in term_dict.keys():
        # 공백이 포함된 단어(예: '국내 총생산')도 하나의 토큰으로 인식되도록 추가
        kiwi.add_user_word(term, tag='NNP', score=10)

    return term_dict, kiwi

# 토큰화 기반 주석 처리 (핵심 로직)
def annotate_text_with_kiwi(text, term_dict, kiwi):    
    # 형태소 분석 (Tokenization)
    tokens = kiwi.tokenize(text)
    
    result_text = []
    last_end = 0  # 마지막으로 처리한 문자열 인덱스
    match_count = 0
    matched_terms = set()

    for token in tokens:
        # 토큰 사이의 공백이나 특수문자 등을 그대로 보존하기 위해
        # 이전 토큰 끝 ~ 현재 토큰 시작 사이의 텍스트를 먼저 추가
        
        result_text.append(text[last_end:token.start])
        
        token_str = text[token.start:token.start + token.len]
        
        # 토큰이 사전(JSON)에 있는지 확인 (공백 제거 후 비교)
        clean_key = token_str.replace(" ", "")
        
        if clean_key in term_dict:
            summary = term_dict[clean_key]['summary']
            
            tooltip = f"""<span class="term-highlight">{token_str}<span class="tooltip-text"><strong>💡 {clean_key}</strong><br><hr style="margin:5px 0">{summary}</span></span>"""
            result_text.append(tooltip)
            
            match_count += 1
            matched_terms.add(clean_key)
        else:
            result_text.append(token_str)
            
        last_end = token.start + token.len

    result_text.append(text[last_end:])
    
    return "".join(result_text), match_count

# 메인 화면
def main():
    inject_custom_css()
    st.title("경제 용어 AI 주석기")
    st.markdown("경제 관련 용어에 대한 주석을 달아줍니다.")

    term_dict, kiwi = init_kiwi_and_data(JSON_FILE)

    if not term_dict:
        st.error("JSON 데이터 파일이 없습니다.")
        return

    with st.sidebar:
        st.success(f"{len(term_dict)}개 용어 데이터 로딩")

    default_text = """
    최근 미국의 기준금리 인상 가능성이 높아지면서 인플레이션 압력이 거세지고 있습니다. 
    이에 따라 소비자물가지수(CPI)가 예상치를 상회하였으며, 한국은행도 통화정책 방향을 고민하고 있습니다.
    가계부채 문제와 환율 변동성 확대가 주요 리스크 요인으로 지목됩니다.
    """

    user_input = st.text_area("텍스트 입력", value=default_text, height=200)

    if st.button("분석 시작", type="primary"):
        with st.spinner("형태소 분석 및 매칭 중..."):
            final_html, count = annotate_text_with_kiwi(user_input, term_dict, kiwi)
            
            st.subheader(f"결과 ({count}개 발견)")
            st.markdown(f'<div class="text-output">{final_html}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()