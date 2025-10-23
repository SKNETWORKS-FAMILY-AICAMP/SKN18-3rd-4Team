"""
run_pdf_pipeline.py
--------------------
1️⃣ 중복 PDF 제거
2️⃣ PDF → Markdown → CSV (sub_category 포함)
"""

import os
import re
import csv
import pathlib
import pymupdf
import pymupdf4llm
import multiprocessing
from typing import Iterable


# =========================================================
# ① 중복 PDF 제거
# =========================================================
def remove_duplicate_pdfs(base_dir: str):
    dup_pattern = re.compile(r"^(?P<name>.+?)\s*\(\d+\)\.pdf$", re.IGNORECASE)
    removed_count = 0

    for root, _, files in os.walk(base_dir):
        for filename in files:
            if not filename.lower().endswith(".pdf"):
                continue

            match = dup_pattern.match(filename)
            if not match:
                continue

            base_name = match.group("name").strip() + ".pdf"
            base_path = os.path.join(root, base_name)
            dup_path = os.path.join(root, filename)

            if os.path.exists(base_path):
                os.remove(dup_path)
                removed_count += 1
                print(f"🗑️ 중복 삭제: {dup_path}")
            else:
                print(f"⚠️ 원본 없음, 보존: {dup_path}")

    print(f"\n✅ 총 {removed_count}개의 중복 PDF 삭제 완료.\n")


# =========================================================
# ② PDF → CSV 변환 (sub_category 포함)
# =========================================================
def clean_markdown(md_text: str) -> str:
    md_text = re.sub(r"!\[.*?\]\(.*?\)", "", md_text)
    md_text = re.sub(r"^\|.*?\|$", "", md_text, flags=re.MULTILINE)
    md_text = re.sub(r"[#*_>`~]+", " ", md_text)
    md_text = re.sub(r"={2,}|-{2,}|_{2,}", " ", md_text)
    md_text = re.sub(r"(?i)^ *목차.*$", "", md_text, flags=re.MULTILINE)
    md_text = re.sub(r"(?i)(page\s*\d+|\d+\s*페이지)", " ", md_text)
    md_text = re.sub(r"[-–—•·∙∙·•]+", " ", md_text)
    md_text = re.sub(r"\b\d{1,3}\b", " ", md_text)
    md_text = re.sub(r"[简體繁體日汉英中一-龥ぁ-ゔァ-ヴー々〆〤]+", " ", md_text)
    md_text = re.sub(r"\([^)]*(특정|모델|그림|참조|이미지|페이지)[^)]*\)", "", md_text)
    md_text = re.sub(r"https?://\S+|www\.\S+", "", md_text)
    md_text = re.sub(r"[^\w가-힣\s,.!?]", " ", md_text)
    md_text = re.sub(r"\s+", " ", md_text).strip()
    return md_text


def _convert_pdf_to_md(path_str: str):
    return pymupdf4llm.to_markdown(path_str)


def safe_to_markdown(pdf_path: str, timeout: int = 300) -> str | None:
    ctx = multiprocessing.get_context("spawn")  # Windows 호환
    with ctx.Pool(processes=1) as pool:
        result = pool.apply_async(_convert_pdf_to_md, (pdf_path,))
        try:
            return result.get(timeout=timeout)
        except multiprocessing.TimeoutError:
            pool.terminate()
            pool.join()
            print(f"⏰ [타임아웃 - 변환 강제 중단] {pdf_path}")
            return None


def iter_pdf_files(root: pathlib.Path) -> Iterable[pathlib.Path]:
    return root.rglob("*.pdf")


def get_sub_category(pdf_path: pathlib.Path, pdf_root: pathlib.Path) -> str:
    """
    PDF 폴더 기준 2단계 하위 폴더명을 sub_category로 반환.
    예:
      data/PDF/식기세척기/가스오븐레인지/매뉴얼.pdf → 가스오븐레인지
      data/PDF/식기세척기/매뉴얼.pdf → 식기세척기
    """
    try:
        rel = pdf_path.relative_to(pdf_root)
        parts = rel.parts

        # 0: 최상위 PDF
        # 1: 1차 카테고리 (식기세척기)
        # 2: 2차 카테고리 (가스오븐레인지)
        # 3: 그 이후는 무시 (날짜, 버전 등)
        if len(parts) >= 3:
            sub = parts[1]  # 1차
            candidate = parts[2]  # 2차
            # “제품사용설명서”, “Ver”, “2020” 등은 제외
            if re.search(r"(제품|사용설명서|Ver|버전|20\d{2}|\d{4}\.\d{2}\.\d{2})", candidate, re.I):
                return sub
            return candidate
        elif len(parts) >= 2:
            return parts[1]
    except Exception:
        pass
    return "기타"



def convert_all_pdfs_to_single_csv(pdf_root: pathlib.Path, output_csv_path: pathlib.Path):
    if not pdf_root.exists():
        raise FileNotFoundError(f"PDF 폴더를 찾을 수 없습니다: {pdf_root}")

    output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    seen_titles = set()
    total, success, skipped = 0, 0, 0

    with open(output_csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        # ✅ sub_category 컬럼 추가
        writer.writerow(["sub_category", "title", "text"])

        for pdf_file in iter_pdf_files(pdf_root):
            total += 1
            title = pdf_file.stem
            sub_category = get_sub_category(pdf_file, pdf_root)

            if title in seen_titles:
                skipped += 1
                print(f"⏩ [중복 건너뜀] {title}")
                continue

            try:
                doc = pymupdf.open(str(pdf_file))
                page_count = len(doc)
                print(f"[📄 {pdf_file.name}] ({sub_category}) 총 {page_count}페이지 처리 중...")

                # ---- 텍스트 밀도 체크 ----
                sample_text = ""
                for i in range(min(3, page_count)):
                    sample_text += doc.load_page(i).get_text("text")

                text_len = len(sample_text.strip())
                avg_text_per_page = text_len / max(1, min(3, page_count))

                if text_len < 400 or avg_text_per_page < 150:
                    print(f"⚠️ [이미지 위주 PDF로 판단, 건너뜀] {pdf_file.name} "
                          f"(샘플텍스트 {text_len}자, 평균 {avg_text_per_page:.1f}/페이지)")
                    continue

                print(f"   → 텍스트 충분함 ({text_len}자), 변환 시작 (최대 300초 제한)")
                md_text = safe_to_markdown(str(pdf_file), timeout=300)
                if not md_text:
                    continue

                cleaned = clean_markdown(md_text)
                if not cleaned.strip():
                    print(f"⚠️ [빈 텍스트 건너뜀] {pdf_file.name}")
                    continue

                writer.writerow([sub_category, title, cleaned])
                seen_titles.add(title)
                success += 1
                print(f"✅ [{title}] ({sub_category}) 변환 완료")

            except Exception as e:
                print(f"⚠️ [오류 건너뜀] {pdf_file.name} ({e})")

    print(f"\n🎯 총 {total}개 중 {success}개 저장, {skipped}개 중복 건너뜀")
    print(f"📄 결과 파일: {output_csv_path}")


# =========================================================
# ③ 전체 실행
# =========================================================
if __name__ == "__main__":
    base_dir = pathlib.Path(__file__).resolve().parent
    pdf_root_dir = base_dir.parent / "data" / "PDF"
    results_root_dir = base_dir.parent / "data" / "csv"
    results_root_dir.mkdir(parents=True, exist_ok=True)
    all_csv_path = results_root_dir / "all_pdfs.csv"

    print("🚀 [1단계] 중복 PDF 제거 시작...")
    remove_duplicate_pdfs(str(pdf_root_dir))

    print("\n🚀 [2단계] PDF → CSV 변환 시작...")
    convert_all_pdfs_to_single_csv(pdf_root_dir, all_csv_path)

    print("\n✅ 전체 파이프라인 완료!")
