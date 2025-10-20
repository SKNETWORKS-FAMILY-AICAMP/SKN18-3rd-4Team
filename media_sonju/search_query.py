from vetordb.connect_db import connect_DB
from vetordb.set_embedding import set_embedding_model
from dotenv import load_dotenv
from pgvector import create_pgvector_store

def search_question(vectorstore, query):
    results = vectorstore.similarity_search_with_score(query, 3) # Cosine 유사도 기반으로 계산-> 높을 수록 좋음
    for i, (doc, score) in enumerate(results, start=1):
        print(f"Rank {i}")
        print(f"Similarity: {score:.3f}")  # 소수점 3자리로 
        print(f"ID: {doc.metadata.get('id')}, Table: {doc.metadata.get('table')}, Category: {doc.metadata.get('category')}")
        print(f"Content: {doc.page_content}") 
        print("="*80)

if __name__ == "__main__":
    load_dotenv()
    db =connect_DB()
    embeddings = set_embedding_model()
    vectorstore = create_pgvector_store(db, embeddings)
    query = "공기청정기가 잘 작동하다가 동작을 안해요" # 질문 검색
    search_question(vectorstore, query)