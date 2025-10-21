"""
SK매직 FAQ 데이터 전처리 스크립트
- CSV 파일 통합 (현재 main에서는 미사용)
- 텍스트 정제 (특수문자, 해시태그, 서비스 문구 등 제거)
- [수정] table_markdown에서 이미지 URL을 추출하여 images 컬럼으로 이동
- 중복 제거
- 큰 따옴표 및 쉼표 제거
- images 컬럼: 이미지 URL에 번호 추가 ([1] title url1 | [2] title url2)
- table_markdown 컬럼: 표에 번호 확인 ([1], [2] 형식)
- 결과 저장
"""
import pandas as pd
import re
from pathlib import Path


# -------------------------------------------------------------------
# 신규 추가된 함수
# -------------------------------------------------------------------
def extract_and_remove_images_from_table(table_markdown):
    """
    table_markdown에서 마크다운 이미지 URL( ![]() )과 일반 이미지 URL을 추출하고,
    테이블 텍스트에서는 해당 마크다운 태그를 제거합니다.

    반환: (제거된 텍스트, 추출된 URL 리스트)
    """
    if pd.isna(table_markdown) or str(table_markdown).strip() == '':
        return table_markdown, []

    table_text = str(table_markdown)
    extracted_urls = []

    # 1. 마크다운 형식의 이미지 태그 ![]() 처리
    # 모든 이미지 확장자 지원 (png, jpg, jpeg, gif, bmp, svg, webp 등)
    markdown_image_pattern = re.compile(
        r'!\[.*?\]\((https?://[^\s)]+\.(?:png|jpg|jpeg|gif|bmp|svg|webp|ico))\)',
        re.IGNORECASE
    )

    # URL 추출
    extracted_urls.extend(markdown_image_pattern.findall(table_text))

    # 마크다운 이미지 태그 제거
    table_text = markdown_image_pattern.sub('', table_text)

    # 2. 마크다운 형식이 아닌 일반 이미지 URL도 처리 (확장자가 없는 경우 포함)
    # 예: https://static.service.skmagic.com/editor/faq/ckimg/cc3a512e82ef4afb8062847fe1b0af42.png
    plain_url_pattern = re.compile(
        r'(https?://[^\s|]+\.(?:png|jpg|jpeg|gif|bmp|svg|webp|ico))',
        re.IGNORECASE
    )

    # 일반 URL 추출 (이미 추출된 URL 제외)
    plain_urls = plain_url_pattern.findall(table_text)
    for url in plain_urls:
        if url not in extracted_urls:
            extracted_urls.append(url)

    # 일반 이미지 URL 제거
    table_text = plain_url_pattern.sub('', table_text)

    # 3. 공백 정리
    table_text = re.sub(r'\s+', ' ', table_text).strip()

    return table_text, extracted_urls
# -------------------------------------------------------------------

def format_images_with_title_and_numbers(images, title):
    """이미지 컬럼의 URL에 번호와 title 주석 추가
    예: url1 | url2 → [1 title] url1 | [2 title] url2
    """
    if pd.isna(images) or str(images).strip() in ['', '없음']:
        return "없음"

    title_str = str(title).strip() if not pd.isna(title) else ""
    # '|'로 구분된 URL 분리
    url_list = [url.strip() for url in str(images).split('|') if url.strip()]

    # 각 URL마다 번호와 title 붙이기
    formatted_urls = [f"[{i+1} {title_str}] {url}" for i, url in enumerate(url_list)]

    # ' | '로 연결
    return ' | '.join(formatted_urls)



def format_tables_with_title_and_numbers(table_markdown, title):
    """table_markdown 컬럼을 번호와 title 주석과 함께 포맷.

    예: [표1] 내용 [표2] 내용 → [1 title] 내용 [2 title] 내용
    """
    if pd.isna(table_markdown) or str(table_markdown).strip() == '':
        return ''

    table_str = str(table_markdown).strip()
    title_str = str(title).strip() if not pd.isna(title) else ""

    # [표1], [표2] 등을 찾아서 [1 title], [2 title]로 변경
    def replace_table_tag(match):
        table_num = re.search(r'\d+', match.group(0)).group()
        return f"[{table_num} {title_str}]"

    # 테이블 태그([표1], [표2], ...)를 title 주석과 함께 변경
    result = re.sub(r'\[표(\d+)\]', replace_table_tag, table_str)

    return result


def clean_table_markdown(table_markdown):
    """표 마크다운 전처리"""
    if pd.isna(table_markdown) or str(table_markdown).strip() == '':
        return table_markdown

    table_text = str(table_markdown).strip()

    # 연속된 줄바꿈 정리 (\n\n → \n)
    table_text = re.sub(r'\n\n+', '', table_text)

    # 큰따옴표 및 쉼표 제거
    table_text = re.sub(r'[\"""‟〝〞＂,]', '', table_text)

    return table_text


def clean_text(text):
    """텍스트 전처리 파이프라인"""
    if pd.isna(text):
        return text

    # 1. 해시태그 제거 (#한글, #영문, #숫자)
    text = re.sub(r'#[가-힣a-zA-Z0-9]+', '', text)

    # 2. 특수기호 제거
    special_chars = ['☞', '▶', '▣', '•', '√', '→', '※', '✅', '⭐']
    for char in special_chars:
        text = text.replace(char, '')

    # # 3. 고객상담센터 및 연락처 정보 제거 (주석 처리됨)
    # text = re.sub(r'[^\n.!?]*\[고객상담센터[^\]]*\][^\n.!?]*[.!?\n]?', '', text)
    # text = re.sub(r'[^\n.!?]*1600\-1661[^\n.!?]*[.!?\n]?', '', text)

    # 4. 서비스 안내 문구 제거
    service_phrases = [
        r'추가 문의가 있으신가요\?.*',
        r'서비스\s*접수는?\s*\[방문예약\]\s*을?\s*이용해\s*주세요\.?',
        r'확인 후에도 동일 증상[^\n.!?]*[.!?\n]?',
        r'☞[^\n.!?]*[.!?\n]?',
        r'확인 후에도 해결되지 않는 증상이라면 전문가의 점검이 필요합니다.',
        r'\.입니다\.',
        r'✅',
        r'⭐',
    ]

    for pattern in service_phrases:
        text = re.sub(pattern, '', text, flags=re.DOTALL)

    # 5. 연속된 마침표 제거 (.. → .)
    text = re.sub(r'\.{2,}', '.', text)

    # 6. 공백 정규화
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    # 7. 큰따옴표 및 쉼표 제거
    text = re.sub(r'[\"“”‟〝〞＂,]', '', text)

    return text


def load_csv_files(input_folder):
    """CSV 파일 읽기 및 통합 (현재 main 함수에서 사용되지 않음)"""
    input_path = Path(input_folder)
    print(f"검색 경로: {input_path.resolve()}")

    csv_files = list(input_path.glob("*.csv"))
    print(f"발견된 CSV 파일 수: {len(csv_files)}")

    dfs = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        print(f"  {csv_file.name}: {len(df)} 행")
        dfs.append(df)

    df_combined = pd.concat(dfs, ignore_index=True)
    print(f"\n통합 완료: 총 {len(df_combined)} 행")
    return df_combined


# -------------------------------------------------------------------
# 수정된 preprocess_data 함수
# -------------------------------------------------------------------
def preprocess_data(df):
    """전처리 수행"""
    print("\n" + "=" * 60)
    print("전처리 시작")
    print("=" * 60)

    # 1. 텍스트 정제
    print("1. 텍스트 정제 중...")
    df['title'] = df['title'].apply(clean_text)
    df['text'] = df['text'].apply(clean_text)
    print("   완료!")

    # ---------------------------------------------------------------
    # 1.5. [신규] 테이블 마크다운에서 이미지 URL 추출 및 'images' 컬럼으로 이동
    if 'table_markdown' in df.columns and 'images' in df.columns:
        print("1.5. 테이블 마크다운에서 이미지 URL 추출 및 'images' 컬럼으로 이동 중...")
        
        # (cleaned_text, extracted_urls_list) 튜플을 반환하는 함수 적용
        extracted_data = df['table_markdown'].apply(extract_and_remove_images_from_table)
        
        # 1. table_markdown 컬럼 업데이트 (이미지 태그가 제거된 텍스트)
        df['table_markdown'] = extracted_data.apply(lambda x: x[0])
        
        # 2. 추출된 URL 리스트 (Series)
        extracted_urls_lists = extracted_data.apply(lambda x: x[1])
        
        # 3. 기존 'images' 컬럼과 병합하는 함수
        def merge_images(existing_images, extracted_urls):
            if not extracted_urls:  # 추출된 URL이 없으면 기존 값 반환
                return existing_images
            
            # 추출된 URL들을 '|'로 연결
            extracted_str = ' | '.join(extracted_urls)
            
            # 기존 'images'가 비어있거나 '없음'인 경우
            if pd.isna(existing_images) or str(existing_images).strip() in ['', '없음']:
                return extracted_str
            # 기존 'images'가 있는 경우, 뒤에 추가
            else:
                return str(existing_images).strip() + ' | ' + extracted_str
        
        # apply를 사용하여 'images' 컬럼 업데이트
        df['images'] = df.apply(
            lambda row: merge_images(row['images'], extracted_urls_lists.loc[row.name]), 
            axis=1
        )
        print("    완료!")
    # ---------------------------------------------------------------

    # 2. 이미지 컬럼에 title과 번호 추가 (기존 2번 -> 1.5번 이후 실행)
    if 'images' in df.columns:
        print("2. 이미지 URL에 title과 번호 추가 중...")
        df['images'] = df.apply(lambda row: format_images_with_title_and_numbers(row['images'], row['title']), axis=1)
        image_count = len(df[df['images'].notna() & (df['images'].str.strip() != '') & (df['images'].str.strip() != '없음')])
        print(f"   완료! (이미지가 있는 행: {image_count}개)")

    # 3. 표 데이터에 title과 번호 추가 및 줄바꿈 처리 (기존 3번 -> 1.5번 이후 실행)
    if 'table_markdown' in df.columns:
        print("3. 표 데이터에 title과 번호 추가 중...")
        # 1.5에서 이미지가 제거된 table_markdown에 포맷팅 적용
        df['table_markdown'] = df.apply(lambda row: format_tables_with_title_and_numbers(row['table_markdown'], row['title']), axis=1)
        print("   표 데이터 줄바꿈 처리 중...")
        df['table_markdown'] = df['table_markdown'].apply(clean_table_markdown)
        table_count = len(df[df['table_markdown'].notna() & (df['table_markdown'].str.strip() != '')])
        print(f"   완료! (표가 있는 행: {table_count}개)")

    # 4. 빈 텍스트 제거
    print("4. 빈 텍스트 제거 중...")
    before = len(df)
    empty_text_mask = df['text'].isna() | (df['text'].str.strip() == '')
    empty_rows = df[empty_text_mask]
    df = df[~empty_text_mask]
    after = len(df)
    print(f"   제거된 행: {before - after}개")

    if len(empty_rows) > 0:
        print("\n   [제거된 빈 텍스트 데이터]")
        for idx, row in empty_rows.iterrows():
            print(f"   - 인덱스 {idx}: 제목='{row['title']}'")

    # 5. 중복 제거
    print("\n5. 중복 제거 중...")
    before = len(df)

    # 전체 중복 찾기
    duplicated_full_mask = df.duplicated(keep='first')
    duplicated_full = df[duplicated_full_mask]

    # text 기준 중복 찾기 (전체 중복 제거 후)
    df = df.drop_duplicates()
    duplicated_text_mask = df.duplicated(subset=['text'], keep='first')
    duplicated_text = df[duplicated_text_mask]

    df = df.drop_duplicates(subset=['text'])
    after = len(df)
    print(f"   전체 중복 제거: {len(duplicated_full)}개")
    print(f"   text 중복 제거: {len(duplicated_text)}개")
    print(f"   총 제거된 행: {before - after}개")

    if len(duplicated_full) > 0:
        print("\n   [제거된 전체 중복 데이터 (최대 50개)]")
        for idx, row in duplicated_full.head(50).iterrows():
            print(f"   - 인덱스 {idx}: 제목='{row['title'][:50]}...'")

    if len(duplicated_text) > 0:
        print("\n   [제거된 text 중복 데이터 (최대 50개)]")
        for idx, row in duplicated_text.head(50).iterrows():
            print(f"   - 인덱스 {idx}: 제목='{row['title'][:50]}...'")
            print(f"     내용='{row['text'][:80]}...'")

    return df


def print_statistics(df, title="통계"):
    """데이터 통계 출력"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(f"총 행 수: {len(df)}")
    print(f"평균 title 길이: {df['title'].str.len().mean():.2f} 자")
    print(f"평균 text 길이: {df['text'].str.len().mean():.2f} 자")
    if 'sub_category' in df.columns:
        print(f"\n상위 10개 카테고리:")
        print(df['sub_category'].value_counts().head(10))


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("SK매직 FAQ 데이터 전처리 시작")
    print("=" * 60)

    # __file__은 스크립트가 실행될 때 정의됩니다. 
    # (예: .py 파일로 저장 후 실행)
    # 인터랙티브 환경(노트북 등)에서는 Path.cwd() 등을 사용해야 할 수 있습니다.
    try:
        script_dir = Path(__file__).parent
    except NameError:
        print("경고: __file__을 찾을 수 없습니다. 현재 작업 디렉토리를 사용합니다.")
        script_dir = Path.cwd()


    # 기존 CSV 파일 직접 읽기
    input_file = script_dir / "skmagic_faq_preprocessed_split_cols.csv"

    if not input_file.exists():
        print(f"오류: 파일을 찾을 수 없습니다: {input_file.resolve()}")
        return

    print(f"입력 파일: {input_file.resolve()}")
    df_original = pd.read_csv(input_file, encoding='utf-8-sig')
    print(f"데이터 로드 완료: {len(df_original)} 행")

    print_statistics(df_original, "전처리 전 통계")

    df_processed = preprocess_data(df_original.copy())
    print_statistics(df_processed, "전처리 후 통계")

    print("\n" + "=" * 60)
    print("전처리 전후 비교")
    print("=" * 60)
    print(f"전처리 전: {len(df_original)} 행")
    print(f"전처리 후: {len(df_processed)} 행")
    print(f"제거된 행: {len(df_original) - len(df_processed)} 행 "
          f"({(len(df_original) - len(df_processed)) / len(df_original) * 100:.2f}%)")
    print(f"\n평균 text 길이: {df_original['text'].str.len().mean():.2f} → "
          f"{df_processed['text'].str.len().mean():.2f} "
          f"({df_processed['text'].str.len().mean() - df_original['text'].str.len().mean():.2f})")

    # 동일한 파일 이름으로 덮어쓰기
    output_file = script_dir / "skmagic_faq_preprocessed_split_cols_1.csv"
    df_processed.to_csv(output_file, index=False, encoding='utf-8-sig')

    print("\n전처리 완료!")
    print(f"저장된 파일: {output_file.resolve()}")
    print(f"최종 데이터: {len(df_processed)} 행 x {len(df_processed.columns)} 컬럼")

    if 'table_markdown' in df_processed.columns:
        table_count = len(df_processed[df_processed['table_markdown'].notna() & (df_processed['table_markdown'].str.strip() != '')])
        print(f"표 데이터가 있는 행: {table_count}개 ({table_count/len(df_processed)*100:.1f}%)")

    if 'images' in df_processed.columns:
        image_count = len(df_processed[df_processed['images'].notna() & (df_processed['images'].str.strip() != '') & (df_processed['images'].str.strip() != '없음')])
        print(f"이미지가 있는 행: {image_count}개 ({image_count/len(df_processed)*100:.1f}%)")


if __name__ == "__main__":
    main()