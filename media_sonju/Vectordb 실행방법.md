# VectorDB 실행 방법

## 프로젝트 개요
이 프로젝트는 PostgreSQL + pgvector를 사용하여 FAQ 데이터를 벡터화하고 유사도 검색을 수행하는 시스템입니다.

## 프로젝트 구조
```
media_sonju/
├── vetordb/                    # 벡터DB 관련 모듈
│   ├── connect_db.py          # DB 연결 관리 (싱글톤 패턴)
│   ├── set_embedding.py       # OpenAI 임베딩 모델 설정
│   ├── split_chunk.py         # 문서 청킹 및 Document 생성
│   └── Check_Singleton.py     # 싱글톤 패턴 구현
├── pgvector.py                # PGVector 커스텀 클래스 구현
├── search_query.py            # 검색 쿼리 실행
├── docker-compose.yml         # PostgreSQL + pgvector 컨테이너 설정
├── init.sql                   # DB 초기화 스크립트
└── requirements.txt           # Python 의존성
```

## 사전 준비

### 1. 환경 변수 설정
`.env` 파일을 생성하고 다음 환경 변수를 설정하세요:

```bash
# PostgreSQL 연결 정보
CONNECTION_STRING=""

# OpenAI API 키
OPENAI_API_KEY=""
```

### 2. Python 의존성 설치
```bash
pip install -r requirements.txt
```

## 실행 방법

### 1. Docker 컨테이너 시작
```bash
# PostgreSQL + pgvector 컨테이너 실행
docker-compose up -d
```

### 2. 벡터DB 구축 및 데이터 추가
```bash
# pgvector.py 실행하여 벡터DB 구축 및 데이터 추가
python pgvector.py
```

이 스크립트는 다음 작업을 수행합니다:
- PostgreSQL 데이터베이스에서 `skmagic_faq` 테이블의 데이터를 읽어옴
- FAQ 데이터를 Document 객체로 변환
- 텍스트를 청킹(chunk_size=100, chhunk_overlap=20)
- OpenAI 임베딩 모델(text-embedding-3-small)로 벡터화
- `FAQ_VECTORDB` 테이블에 벡터 데이터 저장

### 3. 검색 쿼리 실행
```bash
# search_query.py 실행하여 유사도 검색 수행
python search_query.py
```

검색 결과는 다음과 같이 출력됩니다:
- 유사도 점수 (0~1, 높을수록 유사)
- FAQ ID, 테이블명, 카테고리
- 검색된 문서 내용

## 주요 기능

### 1. 벡터DB 클래스 (CustomPGVector)
- `add_texts()`: 텍스트와 임베딩을 벡터DB에 추가
- `similarity_search()`: 유사도 기반 검색 (필터 지원)
- `similarity_search_with_score()`: 유사도 점수와 함께 검색 결과 반환

### 2. 데이터베이스 연결 관리
- 싱글톤 패턴으로 연결 풀 관리
- 최대 5개의 동시 연결 지원
- 자동 연결 해제 및 재사용

### 3. 문서 처리
- FAQ 데이터를 "Question: {title} Answer: {text}" 형태로 변환
- RecursiveCharacterTextSplitter로 텍스트 청킹
- 메타데이터 포함 (테이블명, ID, 카테고리)

## 데이터베이스 스키마

### FAQ_VECTORDB 테이블
```sql
CREATE TABLE FAQ_VECTORDB (
    id SERIAL PRIMARY KEY,
    content TEXT,                 -- 문서 내용
    embedding VECTOR(1536),       -- OpenAI 임베딩 (1536차원) <- embedding 차원에 맞게 고쳐야함
    metadata JSONB                -- 메타데이터 (ID, 테이블명, 카테고리)
);
```

## 문제 해결

### 1. Docker 컨테이너 연결 실패
- Docker가 실행 중인지 확인

### 2. OpenAI API 오류
- API 키가 올바른지 확인
- 네트워크 연결 상태 확인

### 3. 데이터베이스 연결 오류
- 환경 변수 설정 확인
- PostgreSQL 서비스 상태 확인
- 연결 문자열 형식 확인

## 사용 예시

### 검색 쿼리 수정
`search_query.py`에서 검색할 질문을 변경할 수 있습니다:

```python
query = "공기청정기가 잘 작동하다가 동작을 안해요"  # 이 부분을 원하는 질문으로 변경
```

### 검색 결과 개수 조정
검색 결과 개수를 조정하려면 `k` 값을 변경하세요:

```python
results = vectorstore.similarity_search_with_score(query, k=5)  # 상위 5개 결과
```

### 데이터 영속화
- PostgreSQL 데이터는 `./database` 디렉토리에 저장됩니다
- 컨테이너를 삭제해도 데이터는 유지됩니다

## 주의사항
- OpenAI API 사용량에 따른 비용이 발생할 수 있습니다
- 벡터 임베딩은 시간이 오래 걸릴 수 있습니다
- 대용량 데이터 처리 시 메모리 사용량을 모니터링하세요
