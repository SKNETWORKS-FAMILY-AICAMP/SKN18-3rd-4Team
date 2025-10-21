"""
SK매직 FAQ 크롤링 스크립트
- 표 데이터(MD 형식) -> table_markdown 컬럼 마지막에 저장
- 이미지 URL은 '|' 구분자로 images 컬럼에 저장 (단, 표 내부 이미지는 표 마크다운에 삽입)
"""
import csv
import re
import os
import time
import traceback
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def normalize_url(url):
    """상대경로를 절대경로로 변환"""
    if url.startswith('//'):
        return 'https:' + url
    if url.startswith('/'):
        return 'https://service.skmagic.com' + url
    if not url.startswith('http'):
        return 'https://service.skmagic.com/' + url
    return url


def has_border(table):
    """표에 테두리가 있는지 확인"""
    # 테이블 자체에 border 속성이 있는지 확인
    if table.get('border') or 'border' in table.get('style', '').lower():
        return True

    # 셀에 border 스타일이 있는지 확인
    for cell in table.find_all(['td', 'th']):
        style = cell.get('style', '').lower()
        if 'border' in style and 'border:none' not in style and 'border: none' not in style:
            return True
    return False


def table_to_markdown(rows, num):
    """표를 Markdown 형식으로 변환하여 한 줄로 반환"""
    if not rows:
        return ""

    max_cols = max(len(row) for row in rows)
    if max_cols == 0:
        return ""

    # 모든 행의 열 개수를 맞춤
    normalized_rows = [row + [''] * (max_cols - len(row)) for row in rows]

    # Markdown 생성
    md_lines = [f"[표{num}]"]

    # 헤더
    md_lines.append(f"| {' | '.join(normalized_rows[0])} |")
    # 구분선
    md_lines.append(f"| {' | '.join(['---'] * max_cols)} |")
    # 데이터 행
    for row in normalized_rows[1:]:
        md_lines.append(f"| {' | '.join(row)} |")

    return " ".join(md_lines)


def extract_tables(soup):
    """표 데이터를 추출하고 Markdown으로 변환"""
    markdowns = []
    images = []

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
                    cells.append(img_url)
                else:
                    text = re.sub(r'\s+', ' ', td.get_text(separator=' ', strip=True))
                    cells.append(text)

            if cells:
                rows.append(cells)

        if rows:
            md = table_to_markdown(rows, idx)
            if md:
                markdowns.append(md)

    return "\n\n".join(markdowns), images


def extract_content(html):
    """HTML에서 텍스트와 이미지 추출 (표 제외)"""
    soup = BeautifulSoup(html, 'html.parser')

    # mp4 링크 제거
    for a in soup.find_all('a', href=True):
        if '.mp4' in a['href'].lower():
            a.decompose()

    # 표와 이미지 추출
    table_markdown, table_imgs = extract_tables(soup)

    # 표 외부 텍스트 추출
    soup_copy = BeautifulSoup(html, 'html.parser')
    for t in soup_copy.find_all('table'):
        t.decompose()

    text = soup_copy.get_text(separator=' ', strip=True)
    text = re.sub(r'https?://[^\s]*\.mp4[^\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()

    # 표 외부 이미지 추출
    outside_imgs = []
    for img in soup_copy.find_all('img', src=True):
        src = img['src']
        if not src.lower().endswith('.mp4') and src.strip():
            outside_imgs.append(normalize_url(src))

    all_imgs = outside_imgs + table_imgs

    return text, table_markdown, '|'.join(all_imgs) if all_imgs else "없음"


def crawl_detail(page, faq_id):
    """FAQ 상세 페이지 크롤링"""
    try:
        page.evaluate(f"goFaqDetailFn('{faq_id}')")
        page.wait_for_selector('#faqCnts', state='visible', timeout=10000)
        time.sleep(0.5)

        html = page.inner_html('#faqCnts')
        return extract_content(html)

    except Exception as e:
        print(f"\n!!! 상세 페이지 크롤링 오류: {faq_id}")
        print(f"오류: {e}")
        traceback.print_exc()
        return "", "", "없음"


def crawl_faq(main_cat, cddtlid, use_bracket=False):
    """메인 크롤링 함수"""
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

            # 저장 폴더 생성
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skmagic_faq_table_in_md')
            os.makedirs(output_dir, exist_ok=True)
            print(f"저장 폴더: {output_dir}\n")

            # 서브 카테고리 순회
            for sub_i in range(sub_count):
                menu_name = page.locator(f'#prdSubList dd:nth-child({sub_i + 1}) a').inner_text()
                print(f"{'='*60}\n[{sub_i + 1}/{sub_count}] {menu_name}\n{'='*60}")

                page.click(f'#prdSubList dd:nth-child({sub_i + 1}) a')
                time.sleep(1)

                # 탭 전환
                try:
                    page.wait_for_selector('.tab_link_area.type05 ul li:nth-child(1)', timeout=5000)
                    tab_class = page.locator('.tab_link_area.type05 ul li:nth-child(1)').get_attribute('class')
                    if 'on' not in (tab_class or ''):
                        page.click('.tab_link_area.type05 ul li:nth-child(1)')
                        time.sleep(1)
                except Exception:
                    pass

                # FAQ 목록 확인
                try:
                    page.wait_for_selector('#faqList li[onclick]', state='visible', timeout=10000)
                except:
                    print("FAQ 없음\n")
                    continue

                data = []
                page_num = 1

                # 페이지 순회
                while True:
                    print(f"--- 페이지 {page_num} ---")

                    faq_count = page.locator('#faqList li[onclick]').count()
                    if faq_count == 0:
                        break

                    # FAQ 항목 순회
                    for faq_i in range(faq_count):
                        try:
                            time.sleep(0.3)

                            html = page.inner_html('#faqList')
                            items = BeautifulSoup(html, 'html.parser').find_all('li', onclick=True)

                            if faq_i >= len(items):
                                continue

                            # FAQ ID 추출
                            onclick = items[faq_i].get('onclick', '')
                            match = re.search(r"goFaqDetailFn\('(.+?)'\)", onclick)
                            if not match:
                                continue

                            faq_id = match.group(1)
                            title_elem = items[faq_i].select_one('.contents')
                            title = title_elem.get_text(strip=True) if title_elem else ""

                            # 카테고리 처리
                            bracket_match = re.match(r'\[([^\]]+)\]', title)
                            if use_bracket and bracket_match:
                                category = bracket_match.group(1)
                            else:
                                category = menu_name

                            title = re.sub(r'^\[[^\]]+\]\s*', '', title)

                            print(f"  [{faq_i + 1}/{faq_count}] {title}")

                            # 상세 페이지 크롤링
                            text, table_markdown, images = crawl_detail(page, faq_id)

                            data.append({
                                'sub_category': category,
                                'title': title,
                                'text': text,
                                'table_markdown': table_markdown,
                                'images': images
                            })

                            # 뒤로가기
                            page.go_back()
                            page.wait_for_selector('#faqList li[onclick]', state='visible', timeout=10000)
                            time.sleep(0.5)

                        except Exception as e:
                            print(f"\n!!! FAQ 처리 오류: {e}")
                            traceback.print_exc()
                            try:
                                if 'faqDetail' in page.url or '#' not in page.url:
                                    page.go_back()
                                    page.wait_for_selector('#faqList li[onclick]', state='visible', timeout=10000)
                            except Exception as e2:
                                print(f"복구 실패: {e2}")

                    print(f"페이지 {page_num} 완료")

                    # 다음 페이지 확인
                    try:
                        page.wait_for_selector('#faqPagination', timeout=5000)
                        pg_html = page.inner_html('#faqPagination')
                        pg_soup = BeautifulSoup(pg_html, 'html.parser')

                        next_num = page_num + 1
                        next_li = None

                        for li in pg_soup.find_all('li', onclick=True):
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

                # CSV 저장
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
        print(f"메인 크롤링 오류: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("SK매직 FAQ 크롤링 시작")
    print("=" * 60)

    # try:
    #     crawl_faq("건강가전", "03", True)
    # except Exception as e:
    #     print(f"실행 오류: {e}")
    #     traceback.print_exc()

    # 전체 크롤링
    categories = [
        ("정수기", "01", True),
        ("제빙기", "02", True),
        #("건강가전", "03", True),
        ("주방가전", "04", True),
        ("생활가전", "05", True),
        ("기타가전", "06", True),
        ("구독서비스", "07", False),
    ]
    for cat, id, bracket in categories:
        crawl_faq(cat, id, bracket)
