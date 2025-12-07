# logic.py
import json
import os
import streamlit as st
from kiwipiepy import Kiwi
from openai import OpenAI
from dotenv import load_dotenv

@st.cache_resource
def init_kiwi_and_data(filepath):
    """데이터 로드 및 Kiwi 초기화"""
    if not os.path.exists(filepath):
        return None, None

    with open(filepath, 'r', encoding='utf-8') as f:
        term_dict = json.load(f)

    kiwi = Kiwi()
    # 경제 용어 사전 등록
    for term in term_dict.keys():
        kiwi.add_user_word(term, tag='NNP', score=10)

    return term_dict, kiwi

def annotate_text_with_kiwi(text, term_dict, kiwi):    
    """토큰화 및 HTML 태그 생성"""
    tokens = kiwi.tokenize(text)
    
    result_text = []
    last_end = 0
    match_count = 0

    for token in tokens:
        # 공백 및 비토큰 문자 보존
        result_text.append(text[last_end:token.start])
        token_str = text[token.start:token.start + token.len]
        
        # 키 매칭 (공백 제거)
        clean_key = token_str.replace(" ", "")
        
        if clean_key in term_dict:
            summary = term_dict[clean_key]['summary']
            tooltip = f"""<span class="term-highlight">{token_str}<span class="tooltip-text"><strong>💡 {clean_key}</strong><br><hr style="margin:5px 0">{summary}</span></span>"""
            result_text.append(tooltip)
            match_count += 1
        else:
            result_text.append(token_str)
            
        last_end = token.start + token.len

    result_text.append(text[last_end:])
    
    return "".join(result_text), match_count

# OpenAI 요약 기능
def summarize_text_with_ai(text):
    api_key = load_dotenv("OPENAI_API_KEY")
    if not api_key:
        return ".env 파일에 OPENAI_API_KEY가 설정되지 않았습니다."

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 경제 뉴스나 리포트를 읽고 핵심 내용을 3줄 요약해주는 AI 비서야. 독자가 이해하기 쉽게 명확하고 간결한 한국어로 요약해줘."},
                {"role": "user", "content": f"다음 텍스트를 핵심 위주로 3줄 요약해줘:\n\n{text}"}
            ],
            temperature=0.3,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"요약 중 오류가 발생했습니다: {str(e)}"