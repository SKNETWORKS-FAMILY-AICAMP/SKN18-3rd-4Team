# SK매직 FAQ 크롤링 프로젝트

## 프로젝트 개요

SK매직 고객지원 페이지의 FAQ 데이터를 자동으로 수집하는 웹 크롤링 스크립트

표(Table) 데이터를 Markdown 형식으로 변환하고, 이미지 URL을 함께 수집하여 CSV 파일로 저장

### 주요 기능

- **동적 웹 페이지 크롤링**: Playwright를 사용한 브라우저 자동화
- **표 데이터 변환**: HTML 표를 Markdown 형식으로 자동 변환
- **이미지 URL 수집**: FAQ 내 모든 이미지 URL 추출 및 저장
- **카테고리별 분류**: 제품군별/서브카테고리별 데이터 정리
- **자동 페이지 네비게이션**: 페이지네이션 자동 처리

---

## 설치 방법

### 1. 필수 라이브러리 설치

```bash
pip install playwright beautifulsoup4
```

### 2. Playwright 브라우저 설치

```bash
playwright install chromium
```

---

## 파일 구조

```
faq_crawling/
├── faq_crawling_table_2_md.py  # 메인 크롤링 스크립트
└── skmagic_faq_data/                      # 크롤링 결과 저장 폴더 (자동 생성)
    ├── 정수기_서브카테고리1.csv
    ├── 정수기_서브카테고리2.csv
    └── ...
```

---

## 사용 방법

### 기본 실행 (단일 카테고리)

```python
python faq_crawling_table_2_md.py
```

### 전체 카테고리 크롤링

코드 하단의 주석을 해제하여 실행:

```python
categories = [
    ("정수기", "01", True),
    ("제빙기", "02", True),
    ("건강가전", "03", True),
    ("주방가전", "04", True),
    ("생활가전", "05", True),
    ("기타가전", "06", True),
    ("구독서비스", "07", False),
]
for cat, id, bracket in categories:
    crawl_faq(cat, id, bracket)
```

### 매개변수 설명

- `main_cat`: 메인 카테고리 이름 (예: "정수기", "제빙기")
- `cddtlid`: 카테고리 ID (01~07)
- `use_bracket`: 제목 내 대괄호 카테고리 사용 여부
  - `True`: 제목의 `[카테고리명]`을 sub_category로 사용
  - `False`: 메뉴명을 sub_category로 사용

---

## 출력 데이터 형식

### CSV 파일 구조

각 CSV 파일은 다음 5개의 컬럼으로 구성됩니다:

| 컬럼명 | 설명 | 예시 |
| --- | --- | --- |
| `sub_category` | 서브 카테고리 | 렌탈/멤버십 |
| `title` | FAQ 제목 | 렌탈 신청은 어떻게 하나요? |
| `text` | 본문 텍스트 (표 제외) | 홈페이지 또는 고객센터를 통해... |
| `table_markdown` | 표 데이터 (Markdown 형식) | [표1]<br>\| 항목 \| 내용 \|... |
| `images` | 이미지 URL 목록 (파이프 구분) | https://...jpg\|https://...png |

표 내 이미지가 있는 경우 `[이미지]`로 표시.

---

## 크롤링 프로세스

```
1. 브라우저 실행 (Chromium)
   ↓
2. SK매직 고객지원 페이지 접속
   ↓
3. 메인 카테고리 선택 (예: 정수기)
   ↓
4. 서브 카테고리 순회
   ↓
5. 각 서브 카테고리 내 FAQ 목록 조회
   ↓
6. 페이지네이션 처리 (다음 페이지 자동 이동)
   ↓
7. 각 FAQ 항목 클릭 및 상세 내용 수집
   - 제목 추출
   - 본문 텍스트 추출
   - 표 → Markdown 변환
   - 이미지 URL 수집
   ↓
8. CSV 파일로 저장
   (파일명: {메인카테고리}_{서브카테고리}.csv)
```

---

## 에러 처리

### 자동 복구 기능

- FAQ 처리 중 오류 발생 시 자동으로 뒤로가기
- 페이지 로딩 실패 시 다음 항목으로 스킵
- 모든 에러는 콘솔에 상세 출력 (traceback 포함)

### 대기 시간 (sleep)

- 페이지 로딩 안정성을 위한 적절한 대기 시간 설정
- 네트워크 부하 방지

---

## 개발 환경

- **Python**: 3.8 이상
- **Playwright**: 1.40.0 이상
- **BeautifulSoup4**: 4.12.0 이상