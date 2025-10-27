import pandas as pd
from pathlib import Path

# ───────────────────────────────
# 📂 현재 스크립트 기준 경로 설정
# ───────────────────────────────
BASE_DIR = Path(__file__).resolve().parent  # → data/faq/all_data
FAQ_DIR = BASE_DIR.parent                   # → data/faq

# 입력 파일 경로
file_path1 = FAQ_DIR / "preprocessing" / "skmagic_faq_preprocessed.csv"
file_path2 = FAQ_DIR.parent / "pdf" / "data" / "csv" / "all_pdfs.csv"

# 출력 파일 경로
output_path = BASE_DIR / "merged_by_title.csv"

# ───────────────────────────────
# 📄 파일 존재 여부 확인
# ───────────────────────────────
for p in [file_path1, file_path2]:
    if not p.exists():
        print(f"❌ 파일 없음: {p}")
    else:
        print(f"✅ 파일 발견: {p}")

# ───────────────────────────────
# 📊 파일 병합
# ───────────────────────────────
dfs = []
for p in [file_path1, file_path2]:
    if p.exists():
        try:
            dfs.append(pd.read_csv(p, encoding="utf-8-sig"))
        except Exception as e:
            print(f"⚠️ {p.name} 읽기 오류: {e}")

if dfs:
    merged = pd.concat(dfs, ignore_index=True)
    merged.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n✅ 병합 완료 → {output_path}")
else:
    print("\n⚠️ 병합할 데이터가 없습니다.")
