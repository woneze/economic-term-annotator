import pdfplumber
import pandas as pd
import json
import re
import os
import time
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

# ==========================================
# [설정]
# ==========================================
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"

client = OpenAI(api_key=API_KEY)

def clean_text(text):
    """PDF 텍스트 전처리: 불필요한 공백과 줄바꿈을 정리"""
    if not text:
        return ""
   
    # 연속된 공백 및 줄바꿈을 단일 공백으로 변경
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_pdf_text(pdf_path):
    """PDF 전체 텍스트 추출"""
    full_text = ""
    print(f"PDF 로딩 중: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        for page in tqdm(pdf.pages, desc="PDF 페이지 추출"):
            text = page.extract_text()
            if text:
                full_text += clean_text(text) + " "
    return full_text

def summarize_with_gpt(term, raw_text):
    """OpenAI API 요약"""
    if not raw_text or len(raw_text) < 10:
        return None

    prompt = f"""
    아래 텍스트는 경제 용어 '{term}'에 대한 설명입니다.
    이 설명을 컴퓨터공학 전공 대학생이 이해하기 쉽도록 2~3문장으로 명확하게 요약해주세요.
    
    [제약사항]
    1. '연관검색어'나 페이지 번호 같은 불필요한 정보는 무시하세요.
    2. 정의가 불분명하면 '정의를 찾을 수 없음'이라고 답변하세요.

    [원문]:
    {raw_text[:2000]}  # 토큰 절약을 위해 길이 제한
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "핵심만 요약하는 AI 조교입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"\n[API ERROR] {term}: {e}")
        time.sleep(2)
        return None
    
def load_existing_data(filepath):
    """기존 JSON 파일이 있으면 로드"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(filepath, data):
    """데이터를 JSON 파일로 저장"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def find_definition_range(full_text, current_term, next_term):
    """
    단어 검색 로직 강화:
    단어 사이에 공백이나 줄바꿈이 섞여 있어도 찾을 수 있도록 정규식 변환
    예: "가계수지" -> "가\s*계\s*수\s*지"
    """
    # 단어의 각 글자 사이에 유연한 공백 허용 패턴 생성
    flexible_term = r"\s*".join([re.escape(char) for char in current_term])
    
    match = re.search(flexible_term, full_text)
    if not match:
        return None, None
    
    start_idx = match.end()
    
    # 다음 단어까지의 범위 설정 (다음 단어가 없으면 임의로 1500자)
    end_idx = start_idx + 1500
    if next_term:
        flexible_next = r"\s*".join([re.escape(char) for char in next_term])
        # 현재 위치 이후에서 다음 단어 검색
        next_match = re.search(flexible_next, full_text[start_idx:])
        if next_match:
            end_idx = start_idx + next_match.start()
            
    return start_idx, end_idx

def main():
    pdf_file = "data/main_text_only.pdf"
    csv_file = "data/economic_terms_final.csv"
    output_file = "data/economic_terms_ai_summary.json"
    failed_file = "data/failed_terms.csv" # 실패한 단어 저장용

    # 1. 용어 로드
    df = pd.read_csv(csv_file)
    terms = df.iloc[:, 0].dropna().astype(str).tolist()
    print(f"CSV 로드 완료: {len(terms)}개 단어")


    # 2. PDF 로드
    full_pdf_text = get_pdf_text(pdf_file)
    if not full_pdf_text:
        return

    # 3. 기존 진행상황 로드 (이어하기)
    final_data = load_existing_data(output_file)
    print(f"기존 데이터 로드: {len(final_data)}개")

    failed_terms = []

    print("\nAI 요약 및 데이터 생성 시작")
    
    for i, term in enumerate(tqdm(terms)):
        current_term = term.strip()
        if current_term in final_data:
            continue

        next_term = terms[i+1].strip() if i + 1 < len(terms) else None
        
        try:
            start_idx, end_idx = find_definition_range(full_pdf_text, current_term, next_term)
            
            if start_idx:
                raw_definition = full_pdf_text[start_idx:end_idx]
                
                # API 호출
                summary = summarize_with_gpt(current_term, raw_definition)
                
                if summary:
                    final_data[current_term] = {
                        "summary": summary
                    }
                    save_data(output_file, final_data)
                else:
                    failed_terms.append(current_term) # API 실패
                
                # Rate Limit 방지
                time.sleep(0.5) 
            else:
                # PDF에서 단어를 못 찾음
                failed_terms.append(current_term)

        except Exception as e:
            print(f"{current_term}: {e}")
            failed_terms.append(current_term)
            continue

    # 4. 결과 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    
    # 실패한 목록 저장 (추후 따로 처리 위함)
    if failed_terms:
        pd.DataFrame(failed_terms, columns=['Term']).to_csv(failed_file, index=False)
        print(f"\n{len(failed_terms)}개 단어 처리 실패.")

    print(f"\n{len(final_data)}개 단어 저장 완료: {output_file}")

if __name__ == "__main__":
    main()