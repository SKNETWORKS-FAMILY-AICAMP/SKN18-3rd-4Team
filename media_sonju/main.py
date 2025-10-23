from vectordb.connect_db import connect_DB
from vectordb.split_chunk import make_chunk
from vectordb.set_model import set_embedding_model
from vectordb.pgvector import create_pgvector_store, add_documents_to_pgvector
from dotenv import load_dotenv
from vectordb.search_query import search_question
from vectordb.chat import build_context,chat_llm
from vectordb.evaluate_chunks import evaluate_relevance

def create_faq_vectordb(db, vectorstore):
    chunks = make_chunk(db)
    add_documents_to_pgvector(vectorstore, chunks)
    
    
def search(vectorstore):
    while True:
        query = input(f"궁금한 점을 입력하세요: ") # 질문 검색
        all_results = search_question(vectorstore, query)
        if not all_results:
            continue
        contexts = evaluate_relevance(all_results, query)
        chat_llm(build_context(contexts), query)
        break
    
    
if __name__ == "__main__":
    load_dotenv()
    db = connect_DB()
    embeddings = set_embedding_model()
    vectorstore = create_pgvector_store(db, embeddings)
    #create_faq_vectordb(db,vectorstore) #<- 처음 한번 실행
    search(vectorstore)

