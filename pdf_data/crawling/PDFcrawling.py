import os
import re
from pathlib import Path
from typing import List, Tuple

from playwright.sync_api import (
    sync_playwright,
    Page,
    Locator,
)

BASE_URL = "https://service.skmagic.com/web/easy/easyMain.do?tabIndex=3#Back"

# ✅ 실행 위치: Jungyu-crawling/crawling/
# ✅ 저장 경로: Jungyu-crawling/data/PDF/
BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_ROOT = BASE_DIR.parent / "data" / "PDF"


# ===================== 유틸 =====================
def safe_filename(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|]", "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:180] if len(name) > 180 else name

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def log(*args):
    print("[LOG]", *args)

def wait(page: Page, ms: int = 250):
    page.wait_for_timeout(ms)

def click_visible(el: Locator) -> bool:
    """보이는 노드 클릭: normal → force → JS → 좌표 클릭까지 폴백"""
    cnt = el.count()
    for i in range(cnt):
        node = el.nth(i)
        try:
            if not node.is_visible():
                continue
            try:
                node.scroll_into_view_if_needed()
            except Exception:
                pass
            try:
                node.click()
                return True
            except Exception:
                pass
            try:
                node.click(force=True)
                return True
            except Exception:
                pass
            try:
                node.evaluate("el => el.click()")
                return True
            except Exception:
                pass
            try:
                box = node.bounding_box()
                if box:
                    cx = box["x"] + box["width"] / 2
                    cy = box["y"] + box["height"] / 2
                    node.page.mouse.click(cx, cy)
                    return True
            except Exception:
                pass
        except Exception:
            continue
    return False

def safe_click_without_coords(node: Locator) -> bool:
    """페이지네이션 전용: 좌표 클릭 없이만 시도(겹침/오클릭 방지)"""
    try:
        if not node.is_visible():
            try:
                node.scroll_into_view_if_needed()
            except Exception:
                pass
        try:
            node.click()
            return True
        except Exception:
            pass
        try:
            node.click(force=True)
            return True
        except Exception:
            pass
        try:
            node.evaluate("el => el.click()")
            return True
        except Exception:
            pass
    except Exception:
        pass
    return False

# ===================== 셀렉터 =====================
SEL_MAIN_CATEGORY_LIST = "#prdList > li"
SEL_ACTIVE_CATEGORY_NAME = "div.selected_prod_wrap a.active"
SEL_SUBTITLE_TABS_IN_ACTIVE = "div.selected_prod_wrap a"

MANUAL_TAB_CANDIDATES = [
    "div.tab_link_area a:has-text('제품 사용설명서')",
    "div.tab_link_area li:has-text('제품 사용설명서')",
    "div.tab_link_area li >> a:has-text('제품 사용설명서')",
    "li:has-text('제품 사용설명서')",
    "a:has-text('제품 사용설명서')",
    "text=제품 사용설명서",
]

MANUAL_CONTENT_ANY = [
    "div#userManualList",
    "ul#userManualList",
    "div.tab_cont_cont03",
    "div.list_area_manual",
]
SEL_MANUAL_LIST = "ul#userManualList > li"
SEL_MANUAL_PRODUCT_TITLE = "div.contents_wrapper .title, .contents_wrapper .tit, .title"
SEL_MANUAL_TOGGLE = "a.ctgr_down"
SEL_DOWNLOAD_BUTTONS = "a.btn_download"

CONFIRM_POPUP_BUTTONS = [
    "#modal_layer_pop20 a.btn_black_min:has-text('확인')",
    "a.btn_black_min:has-text('확인')",
    "text=확인",
]

# ===================== 핵심 로직 =====================
def open_site(page: Page):
    log("Open:", BASE_URL)
    page.goto(BASE_URL, wait_until="load")
    page.wait_for_load_state("networkidle")

    def rich_ready() -> bool:
        return (
            page.locator("div.container, .container").count() > 0 and
            page.locator("div.prod_select_wrap, .prod_select_wrap").count() > 0
        )

    if not rich_ready():
        log("단순 HTML 감지 → 새로고침")
        page.reload(wait_until="load")
        page.wait_for_load_state("networkidle")

    if not rich_ready():
        raise RuntimeError("리치 UI가 로드되지 않음.")

def get_main_categories(page: Page) -> List[Locator]:
    cats = page.locator(SEL_MAIN_CATEGORY_LIST)
    log(f"메인 카테고리 {cats.count()}개 발견")
    return [cats.nth(i) for i in range(cats.count())]

def click_main_category_by_text(page: Page, text_query: str) -> Tuple[bool, str]:
    lis = page.locator(SEL_MAIN_CATEGORY_LIST)
    for i in range(lis.count()):
        li = lis.nth(i)
        if text_query in (li.inner_text() or ""):
            click_visible(li) or li.click()
            wait(page, 400)
            break
    try:
        active_name = page.locator(SEL_ACTIVE_CATEGORY_NAME).inner_text().strip()
        return (text_query in active_name, active_name)
    except Exception:
        return (False, "")

def click_manuals_top_tab(page: Page):
    clicked = False
    for css in MANUAL_TAB_CANDIDATES:
        loc = page.locator(css)
        if loc.count() == 0:
            continue
        if click_visible(loc):
            clicked = True
            break
    if not clicked:
        raise RuntimeError("상단 탭에서 '제품 사용설명서'를 찾지 못했습니다.")

    ok = False
    try:
        page.wait_for_function(
            """() => {
                const on = document.querySelector('div.tab_link_area li.on, li.on');
                return on && /제품\\s*사용설명서/.test(on.textContent || '');
            }""",
            timeout=20000,
        )
        ok = True
    except Exception:
        pass

    if not ok:
        for sel in MANUAL_CONTENT_ANY:
            try:
                page.locator(sel).first.wait_for(state="visible", timeout=20000)
                ok = True
                break
            except Exception:
                continue

    if not ok:
        page.locator(SEL_MANUAL_LIST).first.wait_for(state="visible", timeout=20000)

def iter_subtitle_tabs(page: Page) -> List[Locator]:
    container = page.locator("div.selected_prod_wrap")
    links = container.locator("a")
    out: List[Locator] = []
    for i in range(links.count()):
        a = links.nth(i)
        text = (a.inner_text() or "").strip()
        if not text or text == "보유제품에서 선택":
            continue
        # 첫 큰 카테고리 버튼은 제외(실제 서브탭만)
        if i == 0 and "active" in (a.get_attribute("class") or ""):
            continue
        out.append(a)
    return out

def close_download_done_popup_if_exists(page: Page):
    try:
        for sel in CONFIRM_POPUP_BUTTONS:
            loc = page.locator(sel)
            if loc.count() and loc.first.is_visible():
                if click_visible(loc.first):
                    wait(page, 150)
                    return
    except Exception:
        pass

def click_all_downloads_in_current_page(page: Page, root: Path, main_title: str, sub_title: str):
    items = page.locator(SEL_MANUAL_LIST)
    log(f"제품 카드 {items.count()}개")

    for i in range(items.count()):
        card = items.nth(i)

        product_title = f"item_{i+1:03d}"
        try:
            title_el = card.locator(SEL_MANUAL_PRODUCT_TITLE)
            if title_el.count() > 0:
                t = title_el.first.inner_text().strip()
                if t:
                    product_title = t
        except Exception:
            pass

        product_dir = root / safe_filename(main_title) / safe_filename(sub_title) / safe_filename(product_title)
        ensure_dir(product_dir)

        toggle = card.locator(SEL_MANUAL_TOGGLE)
        if toggle.count() and toggle.first.is_visible():
            click_visible(toggle.first)
            wait(page, 120)

        dls = card.locator(SEL_DOWNLOAD_BUTTONS)
        log(f" - [{product_title}] 다운로드 버튼 {dls.count()}개")
        for j in range(dls.count()):
            btn = dls.nth(j)
            try:
                with page.expect_download(timeout=30000) as dl_info:
                    click_visible(btn)
                dl = dl_info.value

                suggested = dl.suggested_filename or f"{product_title}_{j+1}.pdf"
                filename = safe_filename(suggested)
                target = product_dir / filename

                if target.exists():
                    stem, ext = os.path.splitext(filename)
                    k = 2
                    while True:
                        alt = product_dir / f"{stem} ({k}){ext}"
                        if not alt.exists():
                            target = alt
                            break
                        k += 1

                dl.save_as(str(target))
                log("   · 저장:", target)
                close_download_done_popup_if_exists(page)

            except Exception as e:
                log("   · 다운로드 실패:", e)

# ===== 페이지네이션 + 다운로드 (숫자만 클릭) =====
def paginate_and_download(page: Page, main_title: str, sub_title: str):
    """
    1페이지 다운로드 후 2~끝까지 정확 번호 클릭.
    - pagination의 li가 ul 밖에 있는 구조도 지원
    - 좌표 클릭 금지(카테고리 오클릭 방지)
    """

    def _list_container() -> Locator:
        ul = page.locator("ul#userManualList").first
        if ul.count():
            cont = ul.locator("xpath=ancestor::*[contains(@class,'list_area_manual') or contains(@class,'tab_cont_cont03')][1]")
            if cont.count():
                return cont.first
        return page

    def _visible_pagination() -> Locator:
        cont = _list_container()
        # id가 있는 정석 구조 1순위
        pagin = cont.locator("#manualPagination").first
        if pagin.count() and pagin.is_visible():
            return pagin
        # 폴백: class 조합/여러 후보
        pagin = cont.locator("#manualPagination.num_area, #manualPagination, .num_area#manualPagination, .num_area")
        for i in range(pagin.count()):
            cand = pagin.nth(i)
            if cand.is_visible() and cand.locator("li, ul li").count() > 0:
                return cand
        return cont.locator("#manualPagination, .num_area").first

    def _page_numbers(pagin: Locator) -> list[int]:
        nodes = pagin.locator("li, ul li")
        nums = []
        for i in range(nodes.count()):
            txt = (nodes.nth(i).inner_text() or "").strip()
            if txt.isdigit():
                nums.append(int(txt))
        return nums

    def _current_page() -> int:
        try:
            on = _visible_pagination().locator("li.on, ul li.on")
            if on.count():
                txt = (on.first.inner_text() or "").strip()
                if txt.isdigit():
                    return int(txt)
        except Exception:
            pass
        return 1

    def _first_card_key() -> str:
        try:
            li = page.locator(SEL_MANUAL_LIST).first
            if li.count() == 0:
                return ""
            t = li.locator(SEL_MANUAL_PRODUCT_TITLE)
            if t.count():
                txt = (t.first.inner_text() or "").strip()
                if txt:
                    return txt
            return (li.inner_text() or "").strip()[:80]
        except Exception:
            return ""

    def _click_page(pagin: Locator, p: int) -> bool:
        exact = re.compile(rf"^\s*{p}\s*$")

        # 1) 정확 일치 텍스트로 li / ul li / a 시도
        for sel in ["li", "ul li", "li a", "ul li a"]:
            cand = pagin.locator(sel).filter(has_text=exact)
            if cand.count():
                node = cand.first
                try:
                    node.evaluate("el => el.scrollIntoView({block:'center'})")
                except Exception:
                    pass
                if safe_click_without_coords(node):
                    return True

        # 2) onclick=pageUtil.goPageFn(...) 보유 li 클릭
        li_onclick = pagin.locator("li[onclick*='goPageFn']")
        for i in range(li_onclick.count()):
            node = li_onclick.nth(i)
            oc = node.get_attribute("onclick") or ""
            if re.search(rf"goPageFn\(\s*{p}\s*,", oc):
                try:
                    node.evaluate("el => el.scrollIntoView({block:'center'})")
                except Exception:
                    pass
                if safe_click_without_coords(node):
                    return True

        # 3) 폴백: JS 직접 호출(전역 노출일 때만)
        try:
            pagin.page.evaluate(
                """
                (p) => {
                  try {
                    if (window.pageUtil && typeof window.pageUtil.goPageFn === 'function') {
                      window.pageUtil.goPageFn(p, 15, window.manualPagingCallbackFn);
                      return true;
                    }
                  } catch(e) {}
                  return false;
                }
                """,
                p,
            )
            return True
        except Exception:
            pass

        return False

    # ---- 1) 첫 페이지 처리 ----
    pagin = _visible_pagination()
    nums = _page_numbers(pagin)
    if not nums:
        log("페이지 번호 없음 → 단일 페이지로 간주")
        click_all_downloads_in_current_page(page, DOWNLOAD_ROOT, main_title, sub_title)
        return

    total_pages = max(nums)
    curr = _current_page()
    log(f"총 페이지: {total_pages}")
    log(f"▶ 페이지 {curr}/{total_pages}")
    click_all_downloads_in_current_page(page, DOWNLOAD_ROOT, main_title, sub_title)

    # ---- 2) 2~끝까지 정확 번호 클릭 순회 ----
    for pnum in range(curr + 1, total_pages + 1):
        pagin = _visible_pagination()
        prev_key = _first_card_key()

        if not _click_page(pagin, pnum):
            log(f"페이지 {pnum} 이동 실패: 버튼 없음/비활성 → 중단")
            break

        # 전환 대기: on 클래스 또는 첫 카드 변경
        try:
            page.wait_for_function(
                """(p) => {
                    const pagin = document.querySelector('#manualPagination');
                    const on = pagin && pagin.querySelector('li.on');
                    if (on && (on.textContent||'').trim() === String(p)) return true;
                    const li = document.querySelector('ul#userManualList > li');
                    if (li) {
                        const t = li.querySelector('.contents_wrapper .title, .contents_wrapper .tit, .title');
                        const key = (t ? t.textContent : li.textContent || '').trim().slice(0,80);
                        if (key) return true;
                    }
                    return false;
                }""",
                pnum,
                timeout=20000,
            )
        except Exception:
            log(f"페이지 {pnum} 전환 대기 타임아웃")

        log(f"▶ 페이지 {pnum}/{total_pages}")
        click_all_downloads_in_current_page(page, DOWNLOAD_ROOT, main_title, sub_title)

# ===================== 활성 서브탭 이름 =====================
def get_active_sub_name(page: Page) -> str:
    """
    현재 선택된(ON/ACTIVE) 서브탭의 텍스트를 반환.
    없으면 '보유제품에서 선택' 제외 후 첫 의미있는 텍스트로 폴백.
    """
    try:
        wrap = page.locator("div.selected_prod_wrap")
        on = wrap.locator("a.on, a.active").last
        txt = (on.inner_text() or "").strip()
        if txt and txt != "보유제품에서 선택":
            return txt
    except Exception:
        pass

    tabs = page.locator("div.selected_prod_wrap a")
    for i in range(tabs.count()):
        t = (tabs.nth(i).inner_text() or "").strip()
        if t and t != "보유제품에서 선택":
            return t
    return "default"

# ===================== 크롤 메인 =====================
def crawl():
    ensure_dir(DOWNLOAD_ROOT)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            accept_downloads=True,
            java_script_enabled=True,
            locale="ko-KR",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1360, "height": 900},
        )
        context.set_extra_http_headers({"Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"})
        page = context.new_page()

        open_site(page)

        # 1) 정수기 먼저 (활성 서브탭 1개 + 나머지 순회)
        ok, active = click_main_category_by_text(page, "정수기")
        main_title = active or "정수기"
        log(f"\n==== 메인 카테고리(우선): {main_title} ====")

        try:
            active_sub = get_active_sub_name(page)
            click_manuals_top_tab(page)
            paginate_and_download(page, main_title="정수기", sub_title=active_sub)
        except Exception as e:
            log("정수기 활성 서브탭 다운로드 실패:", e)
            active_sub = None

        subs = iter_subtitle_tabs(page)
        for sub in subs:
            name = (sub.inner_text() or "").strip()
            if not name:
                continue
            if active_sub and name == active_sub:
                continue
            log(f"\n--- 서브타이틀: {name} ---")
            click_visible(sub)
            wait(page, 350)
            try:
                click_manuals_top_tab(page)
                paginate_and_download(page, main_title="정수기", sub_title=name)
            except Exception as e:
                log("제품 사용설명서 탭 진입/다운로드 중 오류:", e)

        # 2) 나머지 메인 카테고리(제빙기 등)
        cats = get_main_categories(page)
        for i in range(len(cats)):
            li = page.locator(SEL_MAIN_CATEGORY_LIST).nth(i)
            if "정수기" in (li.inner_text() or ""):
                continue

            if not click_visible(li):
                try:
                    li.click()
                except Exception:
                    img = li.locator("img")
                    click_visible(img.first) if img.count() else li.click()
            wait(page, 350)

            try:
                main_title = page.locator(SEL_ACTIVE_CATEGORY_NAME).inner_text().strip()
            except Exception:
                main_title = f"category_{i+1}"
            log(f"\n==== 메인 카테고리: {main_title} ====")

            # ✅ 활성 서브탭(첫 탭) 먼저 처리 — 예: 제빙기 → 슈퍼아이스
            try:
                active_sub = get_active_sub_name(page)
                click_manuals_top_tab(page)
                paginate_and_download(page, main_title, active_sub)
            except Exception as e:
                log("활성 서브탭 다운로드 실패(무시 후 진행):", e)
                active_sub = None

            # ✅ 나머지 서브탭 순회
            subs = iter_subtitle_tabs(page)
            if not subs:
                continue

            for sub in subs:
                sub_name = (sub.inner_text() or "").strip()
                if not sub_name:
                    continue
                if active_sub and sub_name == active_sub:
                    continue
                log(f"\n--- 서브타이틀: {sub_name} ---")
                try:
                    click_visible(sub)
                    wait(page, 350)
                    click_manuals_top_tab(page)
                    paginate_and_download(page, main_title, sub_name)
                except Exception as e:
                    log("다운로드 중 오류:", e)

        log("\n✅ 전체 완료")
        context.close()
        browser.close()

if __name__ == "__main__":
    crawl()