# VectorDB 실행 방법

## 프로젝트 개요
이 프로젝트는 PostgreSQL + pgvector를 사용하여 FAQ 데이터를 벡터화하고 Self-RAG 시스템을 통해 지능적인 질문 답변을 수행하는 시스템입니다.

## 프로젝트 구조
```
media_sonju/
├── vectordb/                    # 벡터DB 관련 모듈
│   ├── connect_db.py           # DB 연결 관리
│   ├── set_model.py            # OpenAI 모델 설정
│   ├── split_chunk.py          # 문서 청킹 및 Document 생성
│   ├── pgvector.py             # PGVector 커스텀 클래스
│   ├── Singleton.py            # 싱글톤 패턴 구현
│   ├── category_chain.py        # 질문 카테고리 분류
│   ├── search_query.py         # 검색 쿼리 처리
│   ├── evaluate_chunks.py      # 문서 관련성 평가
│   ├── chat_templete.py        # 컨텍스트 빌드 및 에이전트 분류
│   ├── multi_agent.py          # 고객지원/기술지원 멀티 에이전트
│   └── utils.py                # 유틸리티 함수
├── pgvector/                   # PostgreSQL + pgvector 설정
│   ├── docker-compose.yml      # Docker 컨테이너 설정
│   ├── init.sql               # 데이터베이스 초기화 스크립트
│   └── skmagic.sql            # FAQ 테이블 스키마
├── creat_vectordb.py          # 벡터DB 생성 스크립트
├── rag_workflow.py            # Self-RAG 워크플로우 정의
├── initial_state.py           # SelfRAG 상태 정의
├── main_rag.py               # RAG 시스템 메인 실행 파일
├── run_rag.py                # RAG 실행 스크립트
├── test.ipynb                # Jupyter 노트북 테스트
└── requirements.txt           # Python 의존성
```

## 사전 준비
### 1. 가상환경 설정
```bash
# 가상환경 생성
uv venv .venv --python 3.13

# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source .venv/bin/activate
```

### 2. 환경 변수 설정
프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```bash
# PostgreSQL 연결 정보
CONNECTION_STRING=postgresql://<userid>:<passwords>@localhost:5432/<database>

# OpenAI API 키
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Python 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. Docker 설치 및 실행
```bash
# pgvector 디렉토리로 이동
cd pgvector

# PostgreSQL + pgvector 컨테이너 실행
docker-compose up -d

# 컨테이너 상태 확인
docker-compose ps
```

## 실행 방법

### 1단계: 데이터베이스 테이블 생성
**DBeaver에서 `skmagic_faq` 테이블 생성하기**
- 데이터 가져오기를 통해 CSV 파일 업로드
- `skmagic.sql` 스크립트 실행 (ID 컬럼 생성)

```sql
-- skmagic.sql 내용
ALTER TABLE skmagic_faq ADD COLUMN id SERIAL PRIMARY KEY;
```

### 2단계: 벡터DB 구축 (최초 1회만 실행)
```bash
python creat_vectordb.py
```

**작업 내용:**
- PostgreSQL의 `skmagic_faq` 테이블에서 데이터 읽기
- 텍스트 청킹 (chunk_size=200, chunk_overlap=50)
- OpenAI 임베딩 모델(`text-embedding-3-large`)로 벡터화
- `faq_vectordb` 테이블에 저장

### 3단계: Self-RAG 시스템 실행

#### 방법 1: Python 스크립트 실행
```bash
python run_rag.py
```

#### 방법 2: Jupyter 노트북 실행
```python
# test.ipynb에서 실행
from rag_workflow import create_self_rag_workflow
from vectordb.connect_db import connect_DB
from vectordb.set_model import set_embedding_model
from vectordb.pgvector import create_pgvector_store

# 데이터베이스 및 벡터스토어 초기화
db = connect_DB()
embeddings = set_embedding_model()
vectorstore = create_pgvector_store(db, embeddings)

# Self-RAG 워크플로우 생성
self_rag_app = create_self_rag_workflow(vectorstore)

# 질문 실행
result = self_rag_app.invoke({"question": "사용자 질문"})
print(result["final_answer"])
```

#### 방법 3: 워크플로우 시각화
```python
from IPython.display import Image, display

# 워크플로우 그래프 표시
display(Image(self_rag_app.get_graph().draw_mermaid_png()))
```

## Self-RAG 워크플로우

### 1. 질문 분류 (`category_chain.py`)
- **고객지원**: 계약관련, 관리서비스, 구독/멤버십제도, 요금납부, 제휴카드
- **기술지원**: 공기청정기, 비데, 안마의자, 히터, 믹서기 등 제품별 분류
- **지원하지 않는 질문**: 범위 밖 질문 필터링

### 2. 벡터 검색 (`search_query.py`)
- 카테고리별 필터링 검색
- 코사인 유사도 기반 문서 검색
- 상위 5개 문서 반환

### 3. 관련성 평가 (`evaluate_chunks.py`)
- 검색된 문서의 질문 관련성 평가 (1-5점)
- 3점 이상 문서만 선별
- 관련 문서가 없으면 재질문 요청

### 4. 컨텍스트 빌드 (`chat_templete.py`)
- 관련 문서들을 컨텍스트로 구성
- 출처 정보 포함

### 5. 멀티 에이전트 답변 생성 (`multi_agent.py`)
- **기술지원 에이전트**: 제품 고장/설치/사용법 등 기술적 문제 해결
- **고객지원 에이전트**: 계약/요금/구독 등 고객 서비스 안내

## 주요 컴포넌트

### 벡터 검색 (`pgvector.py`)
```python
# 기본 검색
results = vectorstore.similarity_search(query, k=5)

# 점수와 함께 검색
results = vectorstore.similarity_search_with_score(query, k=5)

# 카테고리별 필터링 검색
results = vectorstore.similarity_search_with_filter_score(
    query, k=5, categories=["계약관련", "요금납부"]
)
```

### 모델 설정 (`set_model.py`)
- **임베딩 모델**: `text-embedding-3-large` (3072차원)
- **분류 모델**: `gpt-4o-mini` (카테고리 분류)
- **답변 모델**: `gpt-5-nano` (고객지원/기술지원 답변)
- **평가 모델**: `gpt-5-nano` (벡터DB 검색 결과 정확도 평가)

### 데이터베이스 스키마
```sql
-- pgvector 확장 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- 벡터 테이블 생성
CREATE TABLE faq_vectordb (
    id SERIAL PRIMARY KEY,
    content TEXT,                 -- 문서 내용
    embedding VECTOR(3072),       -- 임베딩 벡터 (text-embedding-3-large)
    metadata JSONB                -- 메타데이터 (id, title, category 등)
);
```

## 문제 해결

### Docker 관련
```bash
# 컨테이너 상태 확인
cd pgvector
docker-compose ps

# 로그 확인
docker-compose logs postgres

# 컨테이너 재시작
docker-compose restart
```

### 데이터베이스 연결 오류
- `CONNECTION_STRING` 형식 확인
- Docker 컨테이너 실행 상태 확인
- 포트 5432 충돌 여부 확인

### OpenAI API 오류
- `OPENAI_API_KEY` 유효성 확인
- API 사용량 및 제한 확인
- 네트워크 연결 상태 확인

### 벡터DB 관련 오류
- `faq_vectordb` 테이블 존재 여부 확인
- 임베딩 차원 일치 확인 (`VECTOR(3072)`)
- pgvector 확장 설치 확인

### Self-RAG 워크플로우 오류
- 상태 필드 누락 확인 (`relevant_docs`, `relevance_scores` 등)
- 모델 응답 파싱 오류 확인
- 환경 변수 설정 확인


### 청킹 설정 조정
`split_chunk.py`에서 청킹 설정을 조정할 수 있습니다:

```python
recursive_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,      # 청크 크기
    chunk_overlap=50,    # 오버랩 크기
    separators=["\n\n", "\n", ".", " ", ""] # split 단위
)
```

## 참고사항

- 임베딩 모델 변경 시 테이블의 `VECTOR(N)` 차원도 반드시 일치시켜야 합니다
- 벡터DB 구축은 최초 한 번만 실행하면 됩니다
- Self-RAG 시스템은 질문을 자동으로 분류하여 적절한 에이전트가 답변을 생성합니다
- Jupyter 노트북을 사용하면 워크플로우를 시각적으로 확인할 수 있습니다