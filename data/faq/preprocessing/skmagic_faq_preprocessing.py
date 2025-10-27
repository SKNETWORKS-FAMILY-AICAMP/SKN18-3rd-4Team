import pandas as pd
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CRAWLING_DIR = BASE_DIR.parent / "crawling" / "skmagic_faq_crawling"

# # -------------------------------------------------------------------
# # 헬퍼 함수
# # -------------------------------------------------------------------

def format_images_with_title_and_numbers(images, title):
    """이미지 컬럼의 URL에 번호와 title 주석 추가"""
    if pd.isna(images) or str(images).strip() in ['', '없음']:
        return "없음"

    title_str = str(title).strip() if not pd.isna(title) else ""
    url_list = [url.strip() for url in str(images).split('|') if url.strip()]
    formatted_urls = [f"[{i+1} {title_str}] {url}" for i, url in enumerate(url_list)]
    return ' | '.join(formatted_urls)

def format_tables_with_title_and_numbers(table_markdown, title):
    """table_markdown 컬럼을 번호와 title 주석과 함께 포맷."""
    if pd.isna(table_markdown) or str(table_markdown).strip() == '':
        return ''

    table_str = str(table_markdown).strip()
    title_str = str(title).strip() if not pd.isna(title) else ""

    def replace_table_tag(match):
        table_num = re.search(r'\d+', match.group(0)).group()
        return f"[{table_num} {title_str}]"

    result = re.sub(r'\[표(\d+)\]', replace_table_tag, table_str)
    return result

def clean_table_markdown(table_markdown):
    """표 마크다운 전처리"""
    if pd.isna(table_markdown) or str(table_markdown).strip() == '':
        return table_markdown

    table_text = str(table_markdown).strip()
    table_text = re.sub(r'\n\n+', '', table_text) # 연속된 줄바꿈 정리
    table_text = re.sub(r'[\"\”\‟\〝\〞\",]', '', table_text) # 큰따옴표 및 쉼표 제거
    return table_text

def clean_text(text):
    """텍스트 전처리 파이프라인"""
    if pd.isna(text):
        return text

    text = str(text)
    # 1. 해시태그 제거
    text = re.sub(r'#[가-힣a-zA-Z0-9]+', '', text)

    # 2. 특수기호 제거
    special_chars_pattern = re.compile(r'[☞▶▣•√→※✅⭐]')
    text = special_chars_pattern.sub('', text)

    # 3. 서비스 안내 문구 제거
    service_phrases_pattern = re.compile(
        r'추가 문의가 있으신가요\?.*|'
        r'서비스\s*접수는?\s*\[방문예약\]\s*을?s*이용해\s*주세요\.?|'
        r'확인 후에도 동일 증상[^\n.!?]*[.!?\n]?|'
        r'☞[^\n.!?]*[.!?\n]?|'
        r'확인 후에도 해결되지 않는 증상이라면 전문가의 점검이 필요합니다\.|'
        r'\.입니다\.|'
        r'✅|'
        r'⭐',
        re.DOTALL
    )
    text = service_phrases_pattern.sub('', text)

    # 4. 연속된 마침표 제거 (.. → .)
    text = re.sub(r'\.{2,}', '.', text)

    # 5. 공백 정규화
    text = re.sub(r'\s+', ' ', text).strip()

    # 6. 큰따옴표 및 쉼표 제거
    text = re.sub(r'[\"\”\‟\〝\〞\",]', '', text)

    return text

# -------------------------------------------------------------------
# 메인 전처리 함수
# -------------------------------------------------------------------
def preprocess_data(df):
    """데이터 전처리 수행"""
    print("\n" + "=" * 60)
    print("전처리 시작")
    print("=" * 60)

    # 1. 텍스트 정제
    print("1. 텍스트 정제 중...")
    df['title'] = df['title'].apply(clean_text)
    df['text'] = df['text'].apply(clean_text)
    print("   완료!")

    # 2. 이미지 컬럼에 title과 번호 추가
    if 'images' in df.columns:
        print("2. 이미지 URL에 title과 번호 추가 중...")
        df['images'] = df.apply(lambda row: format_images_with_title_and_numbers(row['images'], row['title']), axis=1)
        image_count = len(df[df['images'].notna() & (df['images'].str.strip() != '') & (df['images'].str.strip() != '없음')])
        print(f"   완료! (이미지가 있는 행: {image_count}개)")

    # 3. 표 데이터에 title과 번호 추가 및 줄바꿈 처리
    if 'table_markdown' in df.columns:
        print("3. 표 데이터에 title과 번호 추가 중...")
        df['table_markdown'] = df.apply(lambda row: format_tables_with_title_and_numbers(row['table_markdown'], row['title']), axis=1)
        df['table_markdown'] = df['table_markdown'].apply(clean_table_markdown)
        table_count = len(df[df['table_markdown'].notna() & (df['table_markdown'].str.strip() != '')])
        print(f"   완료! (표가 있는 행: {table_count}개)")

    # 4. 빈 텍스트 제거
    print("4. 빈 텍스트 제거 중...")
    before_empty_text = len(df)
    df.dropna(subset=['text'], inplace=True)
    df = df[df['text'].str.strip() != '']
    after_empty_text = len(df)
    print(f"   제거된 행: {before_empty_text - after_empty_text}개")

    # 5. 중복 제거
    print("\n5. 중복 제거 중...")
    before_dedup = len(df)
    df.drop_duplicates(inplace=True) # 전체 중복 제거
    # df.drop_duplicates(subset=['text'], inplace=True) # text 기준 중복 제거
    after_dedup = len(df)
    print(f"   총 제거된 중복 행: {before_dedup - after_dedup}개")

    return df

# -------------------------------------------------------------------
# 통계 출력 함수
# -------------------------------------------------------------------
def print_statistics(df, title="통계"):
    """데이터 통계 출력"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(f"총 행 수: {len(df)}")
    print(f"평균 title 길이: {df['title'].str.len().mean():.2f} 자")
    print(f"평균 text 길이: {df['text'].str.len().mean():.2f} 자")

# -------------------------------------------------------------------
# 메인 실행 함수
# -------------------------------------------------------------------
def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("SK매직 FAQ 데이터 전처리 시작")
    print("=" * 60)

    print(f"입력 폴더: {CRAWLING_DIR.resolve()}")
    csv_files = list(CRAWLING_DIR.glob("*.csv"))

    if not csv_files:
        print(f"오류: '{CRAWLING_DIR}' 폴더에서 CSV 파일을 찾을 수 없습니다.")
        return
    
    print("다음 파일들을 병합하여 전처리합니다:")
    df_list = []
    for file in csv_files:
        print(f" - {file.name}")
        df_list.append(pd.read_csv(file, encoding='utf-8-sig'))

    df_original = pd.concat(df_list, ignore_index=True)
    print(f"\n데이터 로드 및 병합 완료: {len(df_original)} 행")

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

    output_file = Path("skmagic_faq_preprocessed.csv")
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
