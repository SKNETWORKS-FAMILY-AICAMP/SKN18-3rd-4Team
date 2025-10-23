"""
SK매직 FAQ 크롤링 스크립트
"""
import csv
import re
import os
import time
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
    """표에 테두리가 있는지 확인 (데이터 표인지 판별)"""
    if table.get('border') or 'border' in table.get('style', '').lower():
        return True
    for cell in table.find_all(['td', 'th']):
        style = cell.get('style', '').lower()
        if 'border' in style and 'border:none' not in style and 'border: none' not in style:
            return True
    return False


def table_to_markdown(rows, num):
    """텍스트 데이터(rows)를 Markdown 형식으로 변환하여 한 줄로 반환"""
    if not rows:
        return ""
    max_cols = max(len(row) for row in rows)
    if max_cols == 0:
        return ""

    normalized_rows = [row + [''] * (max_cols - len(row)) for row in rows]
    md_lines = [
        f"[표{num}]",
        f"| {' | '.join(normalized_rows[0])} |",
        f"| {' | '.join(['---'] * max_cols)} |"
    ]
    for row in normalized_rows[1:]:
        md_lines.append(f"| {' | '.join(row)} |")
    return " ".join(md_lines)


def extract_content(html):
    """HTML에서 텍스트, 표(Markdown), 이미지 URL을 분리하여 추출"""
    soup = BeautifulSoup(html, 'html.parser')
    # mp4 링크 제거
    for a in soup.find_all('a', href=True):
        if '.mp4' in a['href'].lower():
            a.decompose()

    table_markdowns = []
    all_images = []
    table_num = 1

    for table in soup.find_all('table'):
        if not has_border(table):
            continue
        # 표 마크다운 생성
        rows = []
        for tr in table.find_all('tr'):
            cells = [re.sub(r'\s+', ' ', td.get_text(separator=' ', strip=True)) 
                     for td in tr.find_all(['td', 'th'])]
            if cells:
                rows.append(cells)
        
        if rows:
            md = table_to_markdown(rows, table_num)
            if md:
                table_markdowns.append(md)
                table_num += 1
        # 표 내 이미지 추출 -> all_images에 추가
        for img in table.find_all('img', src=True):
            all_images.append(normalize_url(img['src']))
        
        table.decompose()
    # 표 밖의 이미지 추출 -> all_images에 추가
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src and not src.lower().endswith('.mp4') and src.strip():
            all_images.append(normalize_url(img['src']))
        img.decompose()
    # 순수 텍스트 추출
    text = re.sub(r'\s+', ' ', soup.get_text(separator=' ', strip=True)).strip()
    
    images_str = '|'.join(all_images) if all_images else "없음"
    table_md_str = '\n\n'.join(table_markdowns)

    return text, table_md_str, images_str


def crawl_detail(page, faq_id):
    """FAQ 상세 페이지 크롤링 -> 특정 faq_id에 대해 텍스트, 표(Markdown), 이미지 URL 추출"""
    try:
        page.evaluate(f"goFaqDetailFn('{faq_id}')")
        page.wait_for_selector('#faqCnts', state='visible', timeout=10000)
        time.sleep(0.5) 
        html = page.inner_html('#faqCnts')
        return extract_content(html)
    except Exception as e:
        print(f"\n!!! 상세 페이지 크롤링 오류: {faq_id}, {e}")
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
                print("서브 카테고리가 없어 종료합니다.")
                browser.close()
                return

            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skmagic_faq_crawling')
            os.makedirs(output_dir, exist_ok=True)
            print(f"저장 폴더: {output_dir}\n")

            for sub_i in range(sub_count):
                menu_name = page.locator(f'#prdSubList dd:nth-child({sub_i + 1}) a').inner_text()
                print(f"{'='*60}\n[{sub_i + 1}/{sub_count}] {menu_name}\n{'='*60}")

                page.click(f'#prdSubList dd:nth-child({sub_i + 1}) a')
                time.sleep(1)

                try:
                    page.wait_for_selector('.tab_link_area.type05 ul li:nth-child(1)', timeout=5000)
                    tab_class = page.locator('.tab_link_area.type05 ul li:nth-child(1)').get_attribute('class')
                    if 'on' not in (tab_class or ''):
                        page.click('.tab_link_area.type05 ul li:nth-child(1)')
                        time.sleep(1)
                except Exception:
                    pass 

                try:
                    page.wait_for_selector('#faqList li[onclick]', state='visible', timeout=10000)
                except:
                    print("FAQ 없음\n")
                    continue

                data = []
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
                            category = bracket_match.group(1) if use_bracket and bracket_match else menu_name
                            title = re.sub(r'^\[[^\]]+\]\s*', '', title)

                            print(f"  [{faq_i + 1}/{faq_count}] {title}")
                            text, table_markdown, images = crawl_detail(page, faq_id)

                            data.append({
                                'sub_category': category, 'title': title, 'text': text,
                                'table_markdown': table_markdown, 'images': images
                            })

                            page.go_back()
                            page.wait_for_selector('#faqList li[onclick]', state='visible', timeout=10000)
                            time.sleep(0.5)

                        except Exception as e:
                            print(f"\n!!! FAQ 항목 처리 오류: {e}")
                            try:
                                if 'faqDetail' in page.url or '#' not in page.url:
                                    print("페이지 복구: 뒤로가기 수행")
                                    page.go_back()
                                    page.wait_for_selector('#faqList li[onclick]', state='visible', timeout=10000)
                            except Exception as e2:
                                print(f"복구 실패: {e2}. 현재 서브 카테고리를 중단합니다.")
                                break 

                    print(f"페이지 {page_num} 완료")

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

                if data:
                    safe_name = re.sub(r'[\\/:*?"<>|]', '_', menu_name)
                    filename = os.path.join(output_dir, f"{main_cat}_{safe_name}.csv")
                    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                        writer = csv.DictWriter(f, fieldnames=['sub_category', 'title', 'text', 'table_markdown', 'images'])
                        writer.writeheader()
                        writer.writerows(data)
                    print(f"\n저장: {filename} ({len(data)}개)\n")

            browser.close()
            print(f"\n{'='*60}\n크롤링 완료: {main_cat}\n{'='*60}")

    except Exception as e:
        print(f"메인 크롤링 오류: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("SK매직 FAQ 크롤링 시작")
    print("=" * 60)

  # # 전체 크롤링
    categories = [
        ("정수기", "01", True),
        #("제빙기", "02", True),
        #("건강가전", "03", True),
        ("주방가전", "04", True),
        ("생활가전", "05", True),
        ("기타가전", "06", True),
        ("구독서비스", "07", False),
    ]
    
    for cat, id, bracket in categories:
        try:
            crawl_faq(cat, id, bracket)
        except Exception as e:
            print(f"!!! {cat} 카테고리 처리 중 심각한 오류 발생 !!!")
            print(f"오류: {e}")
            traceback.print_exc()


    print("=" * 60)
    print("모든 작업 완료.")
    print("=" * 60)