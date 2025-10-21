"""
SK매직 FAQ 데이터 전처리 스크립트
- CSV 파일 통합
- 텍스트 정제 (특수문자, 해시태그, 서비스 문구 등 제거)
- 중복 제거
- 큰 따옴표 및 쉼표 제거
- 결과 저장
"""
import pandas as pd
import re
from pathlib import Path


def clean_table_markdown(table_markdown):
    """표 마크다운 전처리"""
    if pd.isna(table_markdown) or str(table_markdown).strip() == '':
        return table_markdown

    table_text = str(table_markdown).strip()

    # 연속된 줄바꿈 정리 (\n\n → \n)
    table_text = re.sub(r'\n\n+', '', table_text)

    # 큰따옴표 및 쉼표 제거
    table_text = re.sub(r'[\"“”‟〝〞＂,]', '', table_text)

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

    # # 3. 고객상담센터 및 연락처 정보 제거
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
    """CSV 파일 읽기 및 통합"""
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

    # 2. 표 데이터 줄바꿈 처리
    if 'table_markdown' in df.columns:
        print("2. 표 데이터 줄바꿈 처리 중...")
        df['table_markdown'] = df['table_markdown'].apply(clean_table_markdown)
        table_count = len(df[df['table_markdown'].notna() & (df['table_markdown'].str.strip() != '')])
        print(f"   완료! (표가 있는 행: {table_count}개)")

    # 3. 빈 텍스트 제거
    print("3. 빈 텍스트 제거 중...")
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

    # 4. 중복 제거
    print("\n4. 중복 제거 중...")
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

    script_dir = Path(__file__).parent
    #skmagic_faq_table_in_text , skmagic_faq_split_cols, skmagic_faq_with_tags
    input_folder = script_dir.parent / "yh_faq_crawling" / "skmagic_faq_table_in_text" 
    df_original = load_csv_files(input_folder)

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

    output_file = script_dir / "skmagic_faq_preprocessed_table_in_text.csv"
    df_processed.to_csv(output_file, index=False, encoding='utf-8-sig')

    print("\n전처리 완료!")
    print(f"저장된 파일: {output_file}")
    print(f"최종 데이터: {len(df_processed)} 행 x {len(df_processed.columns)} 컬럼")

    if 'table_markdown' in df_processed.columns:
        table_count = len(df_processed[df_processed['table_markdown'].notna() & (df_processed['table_markdown'].str.strip() != '')])
        print(f"표 데이터가 있는 행: {table_count}개 ({table_count/len(df_processed)*100:.1f}%)")


if __name__ == "__main__":
    main()
