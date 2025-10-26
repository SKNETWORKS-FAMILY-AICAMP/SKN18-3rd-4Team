# SK매직몰 기반 제품설명서 질의응답 시스템

---

## Team Information  
<h3 align="center">👥 Team SK매직몰 챗봇 서비스</h3>

<table align="center">
  <tr>
    <td align="center" width="130">
      <img src="./image/githubimg1.png" width="80"><br>
      <b>이상효</b><br>
      팀장 (PM)<br>
      <a href="https://github.com/username1">
        <img src="https://img.shields.io/badge/GitHub-000?logo=github&logoColor=white&style=flat-square">
      </a>
    </td>
    <td align="center" width="130">
      <img src="./image/githubimg2.png" width="80"><br>
      <b>김준규</b><br>
      BACK (LangChain / VectorDB)<br>
      <a href="https://github.com/username2">
        <img src="https://img.shields.io/badge/GitHub-000?logo=github&logoColor=white&style=flat-square">
      </a>
    </td>
    <td align="center" width="130">
      <img src="./image/githubimg3.png" width="80"><br>
      <b>김담하</b><br>
      FRONT (UI/UX)<br>
      <a href="https://github.com/username3">
        <img src="https://img.shields.io/badge/GitHub-000?logo=github&logoColor=white&style=flat-square">
      </a>
    </td>
    <td align="center" width="130">
      <img src="./image/githubimg4.png" width="80"><br>
      <b>손주영</b><br>
      FRONT (Streamlit)<br>
      <a href="https://github.com/username4">
        <img src="https://img.shields.io/badge/GitHub-000?logo=github&logoColor=white&style=flat-square">
      </a>
    </td>
    <td align="center" width="130">
      <img src="./image/githubimg5.png" width="80"><br>
      <b>임연희</b><br>
      DATA (크롤링)<br>
      <a href="https://github.com/username5">
        <img src="https://img.shields.io/badge/GitHub-000?logo=github&logoColor=white&style=flat-square">
      </a>
    </td>
  </tr>
</table>





## 프로젝트 기간
📆 2025.10 (TBD)  
*주차별 산출물과 일정은 프로젝트 킥오프 이후 업데이트 예정입니다.*

---

## 🛠️ Stacks

### Environment & Ops
![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-007ACC?style=for-the-badge&logo=Visual%20Studio%20Code&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=Git&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

### Backend · AI
![Python](https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3F?style=for-the-badge&logo=langchain&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0A0A32?style=for-the-badge&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![LangSmith](https://img.shields.io/badge/LangSmith-0F172A?style=for-the-badge&logo=langchain&logoColor=white)

### Data & Storage
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/beautifulsoup-1A1A1A?style=for-the-badge&logo=python&logoColor=white)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF4LLM-0B1F3B?style=for-the-badge&logoColor=white)

### Communication
![Discord](https://img.shields.io/badge/discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)

---

![SK매직몰 챗봇 UI](image/output.png)

---

# 1. 프로젝트 개요

## 1-1. 프로젝트 목표
SK매직 IoT 제품 사용자들이 제품 설치, 사용, 오류 해결과 관련된 매뉴얼을 자연어로 즉시 조회할 수 있도록 **RAG 기반 제품설명서 질의응답 시스템**을 구축합니다. 사용자가 “모델명 + 상황”으로 질문하면 적절한 설명서 페이지와 이미지를 찾아 **단계별로 이해하기 쉬운 답변**을 제공합니다.

### 주요 특징
- LLM 기반 자연어 이해와 LangGraph Self-RAG 파이프라인을 결합한 **정확한 응답 생성**
- PostgreSQL + pgvector를 활용한 **제품별/카테고리별 문서 검색**
- PDF · HTML · FAQ 등 이기종 문서를 통합한 **문단 수준 Retrieval**
- LangSmith 연동을 통한 **프롬프트/워크플로우 모니터링**

### 기대 효과
- 고객센터 FAQ 탐색 시간을 줄이고 **셀프 디지털 케어** 경험 강화
- 상담 인입 감소와 문제 해결 시간 단축
- 사용자 모델/상황에 맞춘 **맞춤형 솔루션 제공**

---

## 1-2. 문제 정의

### 기존 채널의 한계
- **SK매직 공식 챗봇**은 FAQ 링크 전달 수준에 머무르며 복잡한 설치·연동 질문을 지원하지 못함
- PDF/웹 매뉴얼이 분산되어 있어 사용자가 직접 검색해야 하고, 검색·필터 기능이 제한적
- 로그인 절차가 필요하거나 다중 질문을 병렬로 처리하기 어려움

### 사용자 불편 사례
- “에어워셔와 IoCare 연동 방법은?” → 앱/FAQ에서는 답변 제공 불가
- “모델 SMC-1000 필터 교체 단계” → 매뉴얼 PDF에서 수동 탐색 필요
- 오류 코드를 포함한 긴급 상황에서도 문서 탐색과 이해에 시간이 소요

---

## 1-3. 경쟁사 분석

| 경쟁 서비스 | 특징 | 장점 | 한계점 |
| --- | --- | --- | --- |
| **Samsung SmartThings** | 스마트 기기 통합 제어 앱 | 앱 하나로 다양한 기기 관리, 실시간 상태 확인 | 연결 실패 원인 파악 어려움, 공식 매뉴얼 즉시 확인 불가 |
| **LG ThinQ** | LG 가전 원격 제어 및 자동화 | 직관적 UI, 간단한 자동화 | 모델별 기능 편차, FAQ 수동 탐색 필요, 통합 검색 미지원 |

**우리의 차별점**
- RAG 기반으로 **PDF·FAQ·HTML 매뉴얼 통합 검색**
- 질문 의도에 맞춘 **문단·표·이미지 포함 응답**
- LangGraph를 활용한 **자체 피드백(Self-RAG)**으로 부정확한 검색을 즉시 보정

---

## 1-4. 기술 구성 요약

| 구성 요소 | 상세 |
| --- | --- |
| **데이터 수집** | `data/pdf/crawling`, `data/faq/crawling`의 Playwright + BeautifulSoup 크롤러로 설명서/FAQ 수집, 필요 시 PyMuPDF4LLM로 PDF OCR |
| **데이터 전처리** | `data/faq/preprocessing`, `data/pdf/preprocess` 스크립트로 텍스트/표/이미지 메타데이터 정규화 및 문단 단위 청킹 |
| **PostgreSQL 저장** | `commons/rag/vectordb/connect_db.py`, `Singleton.py`에서 연결 풀 구성, 전처리 텍스트와 메타데이터 저장 |
| **VectorDB 구축** | `commons/rag/vectordb/pgvector.py`로 OpenAI `text-embedding-3-large` 임베딩 생성 후 pgvector에 저장 |
| **RAG 파이프라인** | `commons/langgraph/workflow.py`, `SelfRAGState` 기반 LangGraph 워크플로우로 질문 분류 → 검색 → 관련성 평가 → 답변 생성 |
| **UI** | `app.py`에서 Streamlit 채팅 UI, LangSmith 트레이스 패널 제공 |

---

# 2. 데이터 파이프라인

1. **제품/FAQ 크롤링**  
   - Playwright headless 브라우저로 동적 페이지 완전 로딩 후 HTML 수집 (`data/faq/crawling/sk_magic_faq_crawling.py`)  
   - 제품 매뉴얼 PDF/HTML 다운로드 및 이미지 링크 추출 (`data/pdf/crawling`)  
   - 결과물은 카테고리별 CSV 및 원문 자료로 저장

2. **전처리 & 청킹**  
   - `data/faq/preprocessing/skmagic_faq_preprocessing.py`에서 불필요 문구 제거, 표/이미지 참조 정리  
   - `pandas` 기반으로 텍스트를 문단(chunk) 단위로 분할, 이미지·표 메타데이터를 JSON 형태로 통합  
   - PDF는 `pymupdf4llm`을 통해 레이아웃을 유지한 텍스트/표 추출

3. **데이터 적재**  
   - 정제된 문단과 메타데이터를 PostgreSQL(`skmagic_faq`, `manual_documents`) 테이블에 적재  
   - pgvector 확장 테이블(`faq_vectordb`)은 content + embedding + metadata(JSONB) 형태로 구성

---

# 3. Self-RAG 파이프라인 (LangGraph)

Self-RAG 파이프라인은 `commons/langgraph/workflow.py`에서 정의되며, 상태는 `SelfRAGState`(`commons/langgraph/initial_state.py`)로 추적합니다.

1. **질문 분류 (`decide_classify_category`)**  
   - `gpt-4o-mini`로 질문의 도메인(고객/기술지원)과 제품 카테고리를 JSON으로 분류  
   - 지원 범위 밖 질문은 즉시 종료 (END 노드)

2. **문서 검색 (`search_question`)**  
   - 카테고리 기반 필터 혹은 도메인 전체 검색  
   - `CustomPGVector.similarity_search_with_filter_score`로 pgvector에서 Top-K 검색

3. **관련성 평가 (`evaluate_relevance`)**  
   - `gpt-5-nano`가 각 문단을 0~100점으로 채점, 50점 이상만 유지  
   - 관련 문서가 없으면 질문을 재구성하여 재검색 (`question_retrive`)

4. **컨텍스트 구성 & 답변 생성 (`chat_llm`)**  
   - 표(`table_markdown`)와 이미지(`image_url`)를 Markdown으로 조합  
   - 이전 대화 히스토리를 포함해 `gpt-5-nano`가 단계별 가이드 생성

5. **LangSmith 모니터링**  
   - `commons/screen/langsmith_view.py`에서 최근 LangGraph 실행 내역을 Streamlit 사이드바에 표시  
   - 프롬프트 튜닝 및 검색 품질 개선에 활용

---

# 4. VectorDB & 데이터베이스

1. **환경 변수 설정**  
   - `.env.sample`을 복사해 `.env` 생성  
   - `CONNECTION_STRING`, `OPENAI_API_KEY`, `LANGCHAIN_*` 값 입력

2. **Docker 기반 PostgreSQL + pgvector**  
   - `data/pgvector/docker-compose.yml` (추가 예정) 또는 로컬 PostgreSQL 사용  
   - `CREATE EXTENSION IF NOT EXISTS vector;` 실행 후 `faq_vectordb` 테이블 생성

3. **임베딩 적재**  
   - `Vectordb 실행방법.md`를 참고해 `commons/rag/vectordb/split_chunk.py`, `pgvector.py` 조합으로 초기 임베딩 구축  
   - 임베딩 모델: `text-embedding-3-large`  
   - 문단별 메타데이터: `id`, `title`, `category`, `image_url`, `table_markdown`, `source_url` 등

4. **싱글톤 풀 관리**  
   - `SingletonDatabase`가 psycopg2 연결 풀을 관리해 Streamlit 세션에서도 안전하게 재사용

---

# 5. Streamlit UI

`app.py`는 Streamlit 기반 챗봇 화면과 LangSmith 트레이스 뷰를 제공하며 다음 기능을 포함합니다.

- **커스텀 챗 UI**: `commons/screen/styles.py`로 다크 테마 채팅 버블, 아바타, 타임스탬프 적용  
- **LangGraph Self-RAG 호출**: `commons/screen/lang.py` → `commons/service/self_rag.py` 경로로 LangGraph 워크플로우 실행  
- **실패 알림 및 재시도 안내**: 검색 실패 시 사용자에게 세부 설명 제공  
- **LangSmith 패널**: 최근 실행, 단계별 input/output, 소요 시간 등 모니터링 기능 제공

---

# 6. 예시 시나리오

| 단계 | 내용 |
| --- | --- |
| **[1] 사용자 질문** | “세탁기 필터 청소 방법 알려줘” |
| **[2] 질문 임베딩 생성** | OpenAI `text-embedding-3-large` 사용 |
| **[3] pgvector 검색** | Top-5 문단: 세탁기 필터 구조, 청소 단계, 배수구 관리 문서 등 |
| **[4] Self-RAG 평가** | 관련성 50점 이상 문단만 추출, 부족 시 질문 재작성 |
| **[5] LLM 응답 생성** | GPT가 표/이미지를 포함한 단계별 가이드 생성 |
| **[6] UI 출력** | Streamlit 화면에 답변 + 원문 링크/이미지 버튼 표시 |

---

# 7. 설치 및 실행 가이드

```bash
# 1) 가상환경 생성 (Windows 예시)
python -m venv .venv
.venv\Scripts\activate

# 2) 패키지 설치
pip install -r requirements.txt

# 3) 환경 변수 설정
cp .env.sample .env  # 수동 복사 후 값 입력

# 4) (선택) PostgreSQL + pgvector 기동
docker compose -f data/pgvector/docker-compose.yml up -d  # 준비 중

# 5) 벡터 DB 초기화
# Vectordb 실행방법.md 절차(데이터 청킹 → 임베딩 → pgvector 적재)를 순차적으로 수행

# 6) Streamlit 실행
streamlit run app.py
```

> 📌 **테스트용 데이터**: `data/faq/all_data`, `data/pdf/data`에 샘플 CSV/PDF가 포함되어 있으며, 실제 서비스 데이터 확보 후 교체 예정입니다.

---

# 8. 폴더 구조 (요약)

```
SKN18-3rd-4Team/
├── app.py                       # Streamlit 메인 앱
├── commons/
│   ├── langgraph/               # Self-RAG 상태/워크플로우
│   ├── llm/                     # OpenAI 모델 설정
│   ├── rag/
│   │   └── vectordb/            # pgvector 연동 및 검색 로직
│   ├── screen/                  # UI, LangSmith 헬퍼
│   └── service/                 # Self-RAG 서비스 계층
├── data/
│   ├── faq/                     # FAQ 크롤링·전처리 스크립트
│   ├── pdf/                     # 제품 설명서 수집·전처리
│   └── pgvector/                # DB 스키마 및 Docker 설정 (예정)
├── image/                       # UI 스크린샷, 챗봇 아바타
├── requirements.txt
├── .env.sample
└── Vectordb 실행방법.md         # 벡터 DB 구축 매뉴얼
```

---

# 9. 향후 계획

- GraphRAG 기반 엔터티/관계 확장 검색 도입 (제품-부품-오류 코드 그래프)
- 멀티모달 답변 강화를 위한 이미지 캡션 생성 및 도면 하이라이트 기능
- 모델별/고객 상황별 프롬프트 템플릿 세분화 및 자동 평가 파이프라인 구축
- 대시보드에 검색 로그 분석, 모델 추론량 모니터링 지표 추가

---

# 10. 참고 링크

- SK매직 고객지원: https://service.skmagic.com/web/easy/easyMain.do?tabIndex=3#Back  
- LangChain Docs: https://python.langchain.com  
- LangGraph Docs: https://langchain-ai.github.io/langgraph/  
- pgvector Docs: https://github.com/pgvector/pgvector  
- Playwright Docs: https://playwright.dev/python/docs/intro  

> 프로젝트 진행에 따라 README는 지속적으로 업데이트됩니다.
