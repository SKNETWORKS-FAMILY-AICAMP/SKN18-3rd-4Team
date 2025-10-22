# Media Sonju - Vector DB FAQ Search System

## Overview
PostgreSQL + pgvector 기반 FAQ 검색 및 답변 생성 시스템

## Key Features
- **Semantic Search**: OpenAI embeddings로 의미 기반 FAQ 검색
- **Smart Categorization**: 질문을 제품 카테고리로 자동 분류 (37개 가전 카테고리)
- **AI Answer Generation**: LLM 기반 자연어 답변 생성
- **Metadata Filtering**: 카테고리별 필터링으로 검색 정확도 향상

## Tech Stack
- **Database**: PostgreSQL 16 + pgvector extension
- **Framework**: LangChain
- **Models**:
  - `text-embedding-3-large` (3072-dim) - 문서 임베딩
  - `gpt-4o-mini` - 질문 분류
  - `gpt-5-nano` - 답변 생성
- **Language**: Python 3.x

## Architecture
```
User Question
  ↓
Category Classification (gpt-4o-mini)
  ↓
Vector Similarity Search (pgvector + OpenAI embeddings)
  ↓
Context Building (top-k FAQs)
  ↓
Answer Generation (gpt-5-nano)
  ↓
Natural Language Answer
```

## Core Components
| Component | Purpose |
|-----------|---------|
| `pgvector.py` | 코사인 유사도 기반 커스텀 벡터 저장소 |
| `category_chain.py` | 	37개 가전 카테고리로 질문 분류 |
| `search_query.py` | S카테고리 필터링을 활용한 검색 오케스트레이션 |
| `chat.py` | 	LLM 기반 답변 생성 |
| `split_chunk.py` | 	FAQ 문서 청킹 (크기=150, 오버랩=50) |
| `connect_db.py` | 	PostgreSQL 연결 관리 |
| `Check_Singleton.py` | DB 커넥션 풀링을 위한 싱글톤 패턴 |

## Quick Start

### 1. Environment Setup
```bash
cp .env.sample .env
# Edit .env with your credentials:
# CONNECTION_STRING=postgresql://user:password@host:5432/dbname
# OPENAI_API_KEY=sk-xxxx
```

### 2. Start Database
```bash
docker-compose up -d
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
python main.py
```

## Database Schema
```sql
CREATE TABLE FAQ_VECTORDB (
    id SERIAL PRIMARY KEY,
    document TEXT,
    embedding VECTOR(3072),
    metadata JSONB  -- {id, category, image_url}
);
```

## Data Source
- FAQ 데이터: `skmagic_faq_preprocessed_final` 테이블
- 필수 컬럼: `id`, `title`, `text`, `sub_category`, `images`

## Workflow
1. **Vectorization**: FAQ 문서를 3072차원 벡터로 변환하여 DB 저장
2. **Classification**: 사용자 질문을 제품 카테고리로 분류
3. **Search**: 카테고리 내에서 코사인 유사도 기반 검색
4. **Fallback**: 카테고리 매칭 실패 시 전체 DB 검색
5. **Generation**: 검색된 FAQ 컨텍스트로 자연어 답변 생성

## Performance Optimization
- Connection pooling (1-5 connections)
- Singleton pattern for DB instance
- Metadata-based filtering for targeted search
- Future: IVFFlat index for large-scale vector search

## Requirements
- Python 3.x
- PostgreSQL 16+
- OpenAI API key
- 2GB+ RAM for vector operations

## Documentation
상세 실행 방법: `Vectordb 실행방법.md` 참조
