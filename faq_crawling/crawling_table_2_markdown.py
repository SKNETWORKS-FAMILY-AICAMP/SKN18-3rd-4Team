"""
SK매직 FAQ 크롤링 스크립트 - Markdown 표 변환 버전 (동기 버전)
- Playwright를 사용한 동기 웹 크롤링
- 표 데이터를 Markdown 형식으로 변환
- 이미지 URL 수집 및 저장
"""
import csv
import re
import os
import time
import traceback
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# URL 정규화 함수 (상대경로 -> 절대경로)
def normalize_url(url):
    if url.startswith('//'):
        return 'https:' + url
    if url.startswith('/'):
        return 'https://service.skmagic.com' + url
    if not url.startswith('http'):
        return 'https://service.skmagic.com/' + url
    return url

# 표(Table) 인식 함수
def has_border(table):
    for cell in table.find_all(['td', 'th']):
        style = cell.get('style', '').lower()
        if 'border' in style and 'border:none' not in style and 'border: none' not in style:
            return True
    return bool(table.get('border')) or 'border' in table.get('style', '').lower()

# 표 → Markdown 변환 함수
def table_to_markdown(rows, num):
    if not rows:
        return ""

    # 최대 열 개수 찾기
    max_cols = max(len(row) for row in rows) if rows else 0
    if max_cols == 0:
        return ""

    # 모든 행의 열 개수를 max_cols에 맞춤
    normalized_rows = []
    for row in rows:
        normalized_row = row + [''] * (max_cols - len(row))
        normalized_rows.append(normalized_row)

    # Markdown 표 생성
    md_lines = []
    md_lines.append(f"[표{num}]")

    # 헤더 행 (첫 번째 행)
    if normalized_rows:
        header = " | ".join(normalized_rows[0])
        md_lines.append(f"| {header} |")

        # 구분선
        separator = " | ".join(["---"] * max_cols)
        md_lines.append(f"| {separator} |")

        # 데이터 행 (나머지 행들)
        for row in normalized_rows[1:]:
            data_row = " | ".join(row)
            md_lines.append(f"| {data_row} |")

    return "\n".join(md_lines)

# 표 → 문장 변환 함수 (기존 유지)
def table_to_sentence(rows, num):
    if not rows:
        return ""

    get_text = lambda cells: [c.strip() for c in cells if c.strip() and c.strip() != "[이미지]"]
    # 케이스 1: 첫 행이 모두 이미지인 경우
    if not get_text(rows[0]):
        sentences = [f"[표{num}]"]
        for row in rows[1:]:
            texts = get_text(row)
            if texts:
                sentences.append(". ".join(texts) + ".")
        return " ".join(sentences) if len(sentences) > 1 else ""
    # 케이스 2: 첫 행을 열 헤더(column header)로 사용하는 일반적인 경우
    col_headers = [c.strip() if c.strip() != "[이미지]" else None for c in rows[0]]
    sentences = [f"[표{num}]"]

    for row in rows[1:]:
        row_header = row[0].strip() if row and row[0].strip() != "[이미지]" else None

        for i in range(1, len(row)):
            if row[i].strip() and row[i].strip() != "[이미지]":
                val = row[i].strip()
                col_h = col_headers[i] if i < len(col_headers) else None

                if row_header and col_h:
                    sentences.append(f"{row_header}의 {col_h}은 {val}입니다.")
                elif row_header:
                    sentences.append(f"{row_header}: {val}.")
                elif col_h:
                    sentences.append(f"{col_h}: {val}.")
                else:
                    sentences.append(f"{val}.")

    return " ".join(sentences) if len(sentences) > 1 else ""

# 표 추출 및 변환 함수 (Markdown 버전 추가)
def extract_tables(soup):
    sentences, markdowns, images = [], [], []

    for idx, table in enumerate(soup.find_all('table'), 1):
        if not has_border(table):
            continue

        rows = []

        for tr in table.find_all('tr'):
            cells = []

            for td in tr.find_all(['td', 'th']):
                img = td.find('img', src=True)
                if img:
                    img_url = normalize_url(img['src'])
                    images.append(img_url)
                    cells.append("[이미지]")
                else:
                    text = re.sub(r'\s+', ' ', td.get_text(separator=' ', strip=True))
                    cells.append(text)

            if cells:
                rows.append(cells)

        if rows:
            # 문장 형식 변환
            sent = table_to_sentence(rows, idx)
            if sent:
                sentences.append(sent)

            # Markdown 형식 변환 ([이미지]로 표시)
            md = table_to_markdown(rows, idx)
            if md:
                markdowns.append(md)

    return " ".join(sentences), "\n\n".join(markdowns), images

# 표 외부 텍스트 추출 함수
def extract_text(soup):
    for t in soup.find_all('table'):
        t.decompose()
    return re.sub(r'\s+', ' ', soup.get_text(separator=' ', strip=True)).strip()

def extract_images(soup):
    for t in soup.find_all('table'):
        t.decompose()
    imgs = []
    for img in soup.find_all('img', src=True):
        src = img['src']
        if not src.lower().endswith('.mp4') and src.strip():
            imgs.append(normalize_url(src))
    return imgs

# FAQ 상세 페이지 크롤링 함수 (동기 버전)
def crawl_detail(page, faq_id):
    try:
        page.evaluate(f"goFaqDetailFn('{faq_id}')")
        page.wait_for_selector('#faqCnts', state='visible', timeout=10000)
        time.sleep(0.5)

        html = page.inner_html('#faqCnts')
        soup = BeautifulSoup(html, 'html.parser')

        for a in soup.find_all('a', href=True):
            if '.mp4' in a['href'].lower():
                a.decompose()

        _, table_markdown, table_imgs = extract_tables(soup)

        text = extract_text(BeautifulSoup(html, 'html.parser'))
        text = re.sub(r'https?://[^\s]*\.mp4[^\s]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text).strip()

        outside_imgs = extract_images(BeautifulSoup(html, 'html.parser'))

        all_imgs = outside_imgs + table_imgs

        return text, table_markdown, '|'.join(all_imgs) if all_imgs else "없음"
    except Exception as e:
        print(f"\n!!! crawl_detail 오류 발생 !!!")
        print(f"FAQ ID: {faq_id}")
        print(f"오류: {e}")
        traceback.print_exc()
        return "", "", "없음"

# 메인 크롤링 함수 (동기 버전)
def crawl_faq(main_cat, cddtlid, use_bracket=False):
    try:
        with sync_playwright() as p:
            print(f"\n브라우저 실행 중...")
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            print(f"페이지 로딩: {main_cat}")
            page.goto('https://service.skmagic.com/web/easy/easyMain.do?tabIndex=3')
            page.wait_for_load_state('networkidle')

            page.click(f'li[data-cddtlid="{cddtlid}"]')
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            page.wait_for_selector('#prdSubList dd', timeout=10000)
            sub_count = page.locator('#prdSubList dd').count()
            print(f"서브 카테고리: {sub_count}개\n")

            if sub_count == 0:
                browser.close()
                return

            # 현재 스크립트 파일의 디렉토리 경로
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, 'skmagic_faq_table_md')
            os.makedirs(output_dir, exist_ok=True)
            print(f"저장 폴더: {output_dir}\n")

            for sub_i in range(sub_count):
                menu_name = page.locator(f'#prdSubList dd:nth-child({sub_i + 1}) a').inner_text()
                print(f"{'='*60}\n[{sub_i + 1}/{sub_count}] {menu_name}\n{'='*60}")

                data = []

                page.click(f'#prdSubList dd:nth-child({sub_i + 1}) a')
                time.sleep(1)

                try:
                    page.wait_for_selector('.tab_link_area.type05 ul li:nth-child(1)', timeout=5000)
                    tab_class = page.locator('.tab_link_area.type05 ul li:nth-child(1)').get_attribute('class')
                    if 'on' not in (tab_class or ''):
                        page.click('.tab_link_area.type05 ul li:nth-child(1)')
                        time.sleep(1)
                except Exception as e:
                    print(f"탭 전환 오류 (무시): {e}")

                try:
                    page.wait_for_selector('#faqList li[onclick]', state='visible', timeout=10000)
                except:
                    print("FAQ 없음\n")
                    continue

                page_num = 1
                while True:
                    print(f"--- 페이지 {page_num} ---")

                    faq_count = page.locator('#faqList li[onclick]').count()
                    if faq_count == 0:
                        break

                    for faq_i in range(faq_count):
                        try:
                            time.sleep(0.3)

                            html = page.inner_html('#faqList')
                            items = BeautifulSoup(html, 'html.parser').find_all('li', onclick=True)

                            if faq_i >= len(items):
                                continue

                            onclick = items[faq_i].get('onclick', '')
                            match = re.search(r"goFaqDetailFn\('(.+?)'\)", onclick)
                            if not match:
                                continue

                            faq_id = match.group(1)
                            title_elem = items[faq_i].select_one('.contents')
                            title = title_elem.get_text(strip=True) if title_elem else ""

                            bracket_match = re.match(r'\[([^\]]+)\]', title)
                            if use_bracket and bracket_match:
                                category = bracket_match.group(1)
                                title = re.sub(r'^\[[^\]]+\]\s*', '', title)
                            else:
                                category = menu_name
                                title = re.sub(r'^\[[^\]]+\]\s*', '', title)

                            print(f"  [{faq_i + 1}/{faq_count}] {title}")

                            text, table_markdown, images = crawl_detail(page, faq_id)

                            data.append({
                                'sub_category': category,
                                'title': title,
                                'text': text,
                                'table_markdown': table_markdown,
                                'images': images
                            })

                            page.go_back()
                            page.wait_for_selector('#faqList li[onclick]', state='visible', timeout=10000)
                            time.sleep(0.5)

                        except Exception as e:
                            print(f"\n!!! FAQ 아이템 처리 오류 !!!")
                            print(f"오류: {e}")
                            traceback.print_exc()
                            print("=" * 60 + "\n")
                            try:
                                if 'faqDetail' in page.url or '#' not in page.url:
                                    page.go_back()
                                    page.wait_for_selector('#faqList li[onclick]', state='visible', timeout=10000)
                            except Exception as e2:
                                print(f"복구 시도 실패: {e2}")

                    print(f"페이지 {page_num} 완료")
                    try:
                        page.wait_for_selector('#faqPagination', timeout=5000)
                        pg_html = page.inner_html('#faqPagination')
                        pg_soup = BeautifulSoup(pg_html, 'html.parser')

                        next_num = page_num + 1
                        all_lis = pg_soup.find_all('li', onclick=True)
                        next_li = None

                        for li in all_lis:
                            if li.get_text(strip=True).isdigit() and int(li.get_text(strip=True)) == next_num:
                                next_li = li
                                break

                        if next_li:
                            page.click(f'#faqPagination li:has-text("{next_num}")')
                            page.wait_for_selector('#faqList li[onclick]', state='visible', timeout=10000)
                            time.sleep(0.8)
                            page_num = next_num
                        else:
                            next_btn = pg_soup.find('a', class_='btn_list_next')
                            if next_btn and 'unclick' not in next_btn.get('class', []):
                                page.click('#faqPagination .btn_list_next')
                                page.wait_for_selector('#faqList li[onclick]', state='visible', timeout=10000)
                                time.sleep(0.8)
                                page_num = next_num
                            else:
                                print(f">>> 마지막 페이지 ({page_num})")
                                break
                    except:
                        break

                if data:
                    safe_name = re.sub(r'[\\/:*?"<>|]', '_', menu_name)
                    filename = os.path.join(output_dir, f"{main_cat}_{safe_name}.csv")

                    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                        writer = csv.DictWriter(f, fieldnames=['sub_category', 'title', 'text', 'table_markdown', 'images'])
                        writer.writeheader()
                        writer.writerows(data)

                    print(f"\n저장: {filename} ({len(data)}개)\n")

            browser.close()
            print(f"\n{'='*60}\n크롤링 완료!\n{'='*60}")

    except Exception as e:
        print(f"\n!!! 메인 크롤링 오류 발생 !!!")
        print(f"오류: {e}")
        traceback.print_exc()

# === 실행 ===
if __name__ == "__main__":
    print("=" * 60)
    print("SK매직 FAQ 크롤링 시작")
    print("=" * 60)

    try:
        crawl_faq("구독서비스", "07", True)
    except Exception as e:
        print(f"\n!!! 실행 오류 !!!")
        print(f"오류: {e}")
        traceback.print_exc()

    # # 전체 크롤링
    # categories = [
    #     ("정수기", "01", True),
    #     ("제빙기", "02", True),
    #     ("건강가전", "03", True),
    #     ("주방가전", "04", True),
    #     ("생활가전", "05", True),
    #     ("기타가전", "06", True),
    #     ("구독서비스", "07", False),
    # ]
    # for cat, id, bracket in categories:
    #     crawl_faq(cat, id, bracket)
