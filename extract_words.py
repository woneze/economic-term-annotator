import fitz  # PyMuPDF
import pandas as pd

def extract_terms_right_to_left(pdf_path, output_csv):
    doc = fitz.open(pdf_path)
    extracted_terms = []
    
    # 중점 및 점선으로 간주할 문자들 정의
    separators = ['.', '·', '・', '…']

    for page in doc:
        text = page.get_text("text")
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 헤더/메타데이터 등 명백한 노이즈 제외
            if not line or any(x in line for x in ["찾아보기", "경제금융용어", "source:"]):
                continue

            # 오른쪽 끝에서부터 한 글자씩 읽기
            found_separator = False
            cut_index = -1
            
            for i in range(len(line) - 1, -1, -1):
                char = line[i]
                
                # 점선/중점 구역을 만났는지 체크
                if char in separators:
                    found_separator = True
                
                # 점선을 이미 만난 상태에서('found_separator=True'),
                # 점선도 아니고 공백도 아닌 '실제 글자'가 나오면 그곳이 단어의 끝(End)임
                if found_separator and char not in separators and char != ' ':
                    cut_index = i
                    break
            
            # 유효한 단어를 찾았으면 리스트에 추가
            if cut_index != -1:
                term = line[:cut_index + 1].strip()
                
                # 너무 짧거나(인덱스 문자) 숫자만 남은 경우 제외
                if len(term) > 1 and not term.isdigit():
                    extracted_terms.append(term)

    # 중복 제거 및 가나다순 정렬
    final_terms = sorted(list(set(extracted_terms)))
    
    # CSV 저장
    df = pd.DataFrame(final_terms, columns=['Term'])
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    
    print(f"Extraction Complete. Saved to '{output_csv}'")
    print(f"Total Terms: {len(final_terms)}")
    
    return final_terms

if __name__ == "__main__":
    pdf_path = "data/index_only.pdf"
    csv_path = "data/economic_terms_final.csv"
    
    terms = extract_terms_right_to_left(pdf_path, csv_path)
    
    # 상위 20개 결과 미리보기
    print("\n[Preview]")
    for t in terms[:20]:
        print(t)