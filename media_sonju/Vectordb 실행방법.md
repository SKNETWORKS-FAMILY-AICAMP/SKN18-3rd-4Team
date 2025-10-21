# VectorDB 실행 방법

## 프로젝트 개요
이 프로젝트는 PostgreSQL + pgvector를 사용하여 FAQ 데이터를 벡터화하고 유사도 검색을 수행하는 시스템입니다.

## 프로젝트 구조 (업데이트)
```
media_sonju/
├── vetordb/
│   ├── connect_db.py          # DB 연결 관리 (싱글톤 패턴)
│   ├── set_model.py           # OpenAI 임베딩/분류 모델 설정
│   ├── split_chunk.py         # 문서 청킹 및 Document 생성
│   ├── category_chain.py      # 질문 카테고리 분류 체인
│   ├── pgvector.py            # PGVector 커스텀 클래스 구현 (벡터 연산/검색)
│   └── Check_Singleton.py     # 싱글톤 패턴 구현
├── main.py                    # 실행 엔트리포인트(검색/DB구축 실행)
├── docker-compose.yml         # PostgreSQL + pgvector 컨테이너 설정
├── init.sql                   # pgvector 확장/테이블 초기화 스크립트
├── skmagic.sql                # skmagic_faq 테이블 보정 (id 추가)
└── requirements.txt           # Python 의존성
```

## 사전 준비

### 1. 환경 변수 설정
- 가상환경 설정 
```bash
uv venv .venv --python 3.13
```
- `.env` 파일을 생성하고 다음 환경 변수를 설정하세요:
```bash
# PostgreSQL 연결 정보 (예시)
CONNECTION_STRING=""
# OpenAI API 키
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Python 의존성 설치
```bash
pip install -r requirements.txt
```

## 데이터베이스 준비

### 1) Docker로 PostgreSQL + pgvector 실행
```bash
docker-compose up -d
```

### 2) 초기 스키마 구성
- 컨테이너 시작 시 `init.sql`이 실행되어 벡터 테이블이 생성됩니다.
- 데이터 가져오기를 통해 `skmagic_faq` 테이블을 생성하고, 기본키가 없다면 `skmagic.sql`로 보정하세요.

```sql
-- skmagic.sql
ALTER TABLE skmagic_faq ADD COLUMN id SERIAL PRIMARY KEY;
```

## 실행 방법

### 1) 처음 한 번: 벡터DB 구축 (최초 적재 시)
`main.py`의 주석을 해제하여 실행하면 DB에서 FAQ를 불러 벡터DB에 적재합니다.

```python
# main.py
# create_faq_vectordb(db, vectorstore)  # <- 처음 한번 실행
```

```bash
python main.py
```

작업 내용:
- PostgreSQL의 `skmagic_faq`에서 데이터를 읽어 `Document`로 변환
- 텍스트를 청킹(chunk_size=100, chunk_overlap=20)
- OpenAI 임베딩 모델(`text-embedding-3-large`)로 벡터화
- 테이블 `faq_vectordb`에 저장 (기본 테이블명)

임베딩 차원 주의: `text-embedding-3-large`는 3072차원입니다. 테이블의 `init.sql`에서  `VECTOR(3072)`여야 합니다.

### 2) 검색 실행
`main.py`를 실행하면 콘솔 입력으로 질의를 받아 검색합니다.

```bash
python main.py
```

출력:
- 유사도 점수(코사인 유사도) 높은 순 정렬
- 문서 메타데이터(`id`, 카테고리 등)와 내용

## 주요 컴포넌트

### 1. 벡터 검색 (`vetordb/pgvector.py`)
- `similarity_search()` : 코사인 유사도 기반 검색, 메타데이터 필터 지원
- `similarity_search_with_score()` : 유사도 점수 함께 반환 (코사인 거리 `<=>` → `1 - 거리`)
- 기본 테이블명: `faq_vectordb`

### 2. 모델 설정 (`vetordb/set_model.py`)
- 임베딩: `text-embedding-3-large` (3072차원)
- 분류: `gpt-5-nano` (옵션, 카테고리 분류용)

### 3. 문서 처리 (`vetordb/split_chunk.py`)
- FAQ를 "Question: {title}  Answer: {text}"로 합성해 `Document` 생성
- `RecursiveCharacterTextSplitter`로 청킹

## 데이터베이스 스키마 예시

`init.sql`의 기본 예시는 아래와 유사합니다. 임베딩 모델 차원에 맞춰 수정하세요.

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS faq_vectordb (
  id SERIAL PRIMARY KEY,
  content TEXT,
  embedding VECTOR(3072),  -- text-embedding-3-large 기준
  metadata JSONB
);
```

## 문제 해결

### 1) Docker 컨테이너 연결 실패
- Docker 데몬 실행 여부 확인
- 포트 `5432` 충돌 여부 확인
- 로그 확인: `docker-compose logs postgres`

### 2) OpenAI API 오류
- `OPENAI_API_KEY` 확인
- 네트워크 및 API 제한 확인

### 3) 데이터베이스 연결 오류
- `CONNECTION_STRING` 형식 및 값 확인
- DB 서버 상태/방화벽 확인

## 참고/팁
- 임베딩 모델 변경 시 테이블의 `VECTOR(N)` 차원도 반드시 일치시켜야 합니다.