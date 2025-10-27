# SK Magic FAQ 데이터 수집 및 전처리

## 프로세스 개요

1.  **크롤링**: `crawling/sk_magic_faq_crawling.py` 
2.  **전처리**: `preprocessing/skmagic_faq_preprocessing.py`

## 파일 설명

### 1. `crawling/sk_magic_faq_crawling.py`

SK Magic 서비스 센터의 FAQ 페이지에서 데이터를 크롤링하는 스크립트입니다.

-   **주요 기능**:
    -   `Playwright`와 `BeautifulSoup` 라이브러리를 사용하여 동적 웹 페이지의 콘텐츠를 수집합니다.
    -   정수기, 주방가전, 생활가전 등 주요 제품 카테고리별로 모든 FAQ를 순회합니다.
    -   각 FAQ 페이지에서 제목, 본문 텍스트, 표, 이미지를 분리하여 추출합니다.
        -   **텍스트**: 순수 텍스트만 추출합니다.
        -   **표**: Markdown 형식으로 변환하여 저장합니다.
        -   **이미지**: 이미지 URL을 추출하여 `|` 문자로 구분된 문자열로 저장합니다.

-   **실행 방법**:
    ```bash
    python crawling/sk_magic_faq_crawling.py
    ```
    
-   **결과**:
    -   `crawling/skmagic_faq_crawling/` 폴더 내에 각 서브 카테고리별로 `[메인카테고리]_[서브카테고리].csv` 형식의 파일이 생성
 
### 2. `preprocessing/skmagic_faq_preprocessing.py`

크롤링을 통해 생성된 여러 개의 CSV 파일을 하나로 병합하고, 데이터를 정제하는 스크립트입니다.

-   **주요 기능**:
    -   `pandas`를 사용하여 CSV 파일들을 하나로 통합합니다.
    -   텍스트 데이터에서 불필요한 특수기호, 해시태그, 반복적인 안내 문구 등을 제거합니다.
    -   이미지 URL과 표(Markdown) 데이터에 해당 FAQ의 제목과 번호를 추가하여 명확성을 높입니다.
    -   내용이 비어있거나 중복되는 데이터를 제거하여 최종 데이터셋을 생성합니다.

-   **실행 방법**:
    ```bash
    python preprocessing/skmagic_faq_preprocessing.py
    ```
-   **결과**:
    -   `skmagic_faq_preprocessed.csv` 파일 생성

## 요구사항

```bash
pip install -r requirements.txt
```
