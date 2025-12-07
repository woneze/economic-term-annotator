# logic.py
import json
import os
import streamlit as st
from kiwipiepy import Kiwi

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