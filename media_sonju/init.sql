-- pgvector 확장 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- 예제 테이블 생성
CREATE TABLE FAQ_VECTORDB (
    id SERIAL PRIMARY KEY,
    content TEXT,                 -- 문서 내용
    embedding VECTOR(1536),       -- 임베딩 크기에 맞춤
    metadata JSONB                -- 메타데이터
);
/*
-- 벡터 인덱스 생성 (성능 향상)
-- ivfflat 인덱스는 대규모 데이터셋에서 빠른 근사 최근접 이웃 검색을 가능하게 합니다.
-- 데이터가 적은 상태에서 ivfflat 인덱스를 생성하면 오히려 성능이 저하될 수 있습니다.
-- 데이터가 충분히 쌓인 후에 아래 명령어로 인덱스를 생성하세요.
-- 예를 들어, 데이터가 10,000개 이상 쌓인 후에 실행하는 것을 권장합니다.
-- 10,000개의 데이터에 대해 nlist를 100으로 설정하는 것이 일반적입니다.
*/
-- CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 1000);
