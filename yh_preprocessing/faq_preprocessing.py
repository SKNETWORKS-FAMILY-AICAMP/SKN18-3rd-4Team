"""
SK매직 FAQ 데이터 전처리 스크립트
- CSV 파일 통합
- 텍스트 정제 (특수문자, 해시태그, 서비스 문구 등 제거)
- 중복 제거
- 결과 저장
"""
import pandas as pd
import re
from pathlib import Path


def clean_table_markdown(table_markdown):
    """[표N] 앞의 빈 줄만 제거 (표 내용의 줄바꿈은 유지)"""
    if pd.isna(table_markdown) or str(table_markdown).strip() == '':
        return table_markdown

    table_text = str(table_markdown)

    # [표N] 앞의 연속된 줄바꿈(\n\n, \n\n\n 등)을 하나의 줄바꿈(\n)으로 변경
    # 예: "\n\n[표2]" → "\n[표2]"
    table_text = re.sub(r'\n\n+(\[표\d+\])', r'\n\1', table_text)

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

    # 3. 고객상담센터 및 연락처 정보 제거
    text = re.sub(r'[^\n.!?]*\[고객상담센터[^\]]*\][^\n.!?]*[.!?\n]?', '', text)
    text = re.sub(r'[^\n.!?]*1600\-1661[^\n.!?]*[.!?\n]?', '', text)

    # 4. 서비스 안내 문구 + 이모티콘 제거
    service_phrases = [
        r'추가 문의가 있으신가요\?.*',
        r'서비스\s*접수는?\s*\[방문예약\]\s*을?\s*이용해\s*주세요\.?',
        r'확인 후에도 동일 증상[^\n.!?]*[.!?\n]?',
        r'☞[^\n.!?]*[.!?\n]?',
        r'확인 후에도 해결되지 않는 증상이라면 전문가의 점검이 필요합니다.',
        r'\.입니다\.',
        r'✅',
        r'⭐',
        # r'서비스 접수는 [대성하이원 ☎031-358-7034]을 이용해 주세요',
        # r'서비스 접수는 [POK ☎1661-0083]을 이용해 주세요.'
    ]
    for pattern in service_phrases:
        text = re.sub(pattern, '', text, flags=re.DOTALL)

    # # 5. 표 참조 제거 ([표1], [표2] 등)
    # text = re.sub(r'\[표\d+\]', '', text)

    # 6. 연속된 마침표 제거 (.. → .)
    text = re.sub(r'\.{2,}', '.', text)

    # 7. 공백 정규화 (연속된 공백 → 하나, 앞뒤 공백 제거)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text


def load_csv_files(input_folder):
    """CSV 파일 읽기 및 통합"""
    input_path = Path(input_folder)

    # 디버깅: 실제 경로 출력
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

    # 2. 표 데이터 줄바꿈 제거
    if 'table_markdown' in df.columns:
        print("2. 표 데이터 줄바꿈 제거 중...")
        df['table_markdown'] = df['table_markdown'].apply(clean_table_markdown)
        table_count = len(df[df['table_markdown'].notna() & (df['table_markdown'].str.strip() != '')])
        print(f"   완료! (표가 있는 행: {table_count}개)")

    # 3. 빈 텍스트 제거
    print("3. 빈 텍스트 제거 중...")
    before = len(df)
    df = df[df['text'].notna() & (df['text'].str.strip() != '')]
    after = len(df)
    print(f"   제거된 행: {before - after}개")

    # 4. 중복 제거
    print("4. 중복 제거 중...")
    before = len(df)

    # 전체 행 중복 제거
    df = df.drop_duplicates()
    after_full = len(df)
    print(f"   전체 행 중복: {before - after_full}개 제거")

    # text 기준 중복 제거
    df = df.drop_duplicates(subset=['text'])
    after_text = len(df)
    print(f"   text 중복: {after_full - after_text}개 제거")
    print(f"   총 중복 제거: {before - after_text}개")

    return df


def print_statistics(df, title="통계"):
    """데이터 통계 출력"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(f"총 행 수: {len(df)}")
    print(f"평균 title 길이: {df['title'].str.len().mean():.2f} 자")
    print(f"평균 text 길이: {df['text'].str.len().mean():.2f} 자")
    print(f"\n상위 10개 카테고리:")
    print(df['sub_category'].value_counts().head(10))


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("SK매직 FAQ 데이터 전처리 시작")
    print("=" * 60)

    # 1. CSV 파일 로드
    # 스크립트 파일 기준 상대 경로 사용
    script_dir = Path(__file__).parent
    input_folder = script_dir.parent / "yh_faq_crawling" / "skmagic_faq_data"
    df_original = load_csv_files(input_folder)

    # 2. 전처리 전 통계
    print_statistics(df_original, "전처리 전 통계")

    # 3. 전처리 수행
    df_processed = preprocess_data(df_original.copy())

    # 4. 전처리 후 통계
    print_statistics(df_processed, "전처리 후 통계")

    # 5. 전후 비교
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

    # 6. 결과 저장
    output_file = script_dir / "skmagic_faq_preprocessed.csv"
    df_processed.to_csv(output_file, index=False, encoding='utf-8-sig')

    print("\n" + "=" * 60)
    print("전처리 완료!")
    print("=" * 60)
    print(f"저장된 파일: {output_file}")
    print(f"최종 데이터: {len(df_processed)} 행 x {len(df_processed.columns)} 컬럼")

    # 표 데이터 통계
    if 'table_markdown' in df_processed.columns:
        table_count = len(df_processed[df_processed['table_markdown'].notna() & (df_processed['table_markdown'].str.strip() != '')])
        print(f"표 데이터가 있는 행: {table_count}개 ({table_count/len(df_processed)*100:.1f}%)")

    # 7. 샘플 데이터 출력
    print("\n샘플 데이터 (처음 5개):")
    print(df_processed.head())


if __name__ == "__main__":
    main()
