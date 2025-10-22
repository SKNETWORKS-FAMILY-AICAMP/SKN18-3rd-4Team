from vectordb.memory import get_conversation_summary_memory
from vectordb.connect_db import connect_DB
from vectordb.split_chunk import make_chunk
from vectordb.set_model import set_embedding_model
from vectordb.pgvector import create_pgvector_store, add_documents_to_pgvector
from dotenv import load_dotenv
from vectordb.search_query import search_question
from vectordb.chat import build_context, chat_llm_with_memory

def create_faq_vectordb(db, vectorstore):
    chunks = make_chunk(db)
    add_documents_to_pgvector(vectorstore, chunks)
    
def search(vectorstore):
    # 대화 히스토리 초기화
    conversation_history = []
    summarize_function = get_conversation_summary_memory(max_messages=10)
    
    # 반복 대화 루프
    while True:
        query = input(f"\n궁금한 점을 입력하세요 (종료: 'quit'): ")
        if query.lower() == 'quit':
            break
            
        all_results = search_question(vectorstore, query)
        context = build_context(all_results)
        
        # 메모리 기능 사용 + 업데이트된 히스토리 저장
        conversation_history = chat_llm_with_memory(
            context, 
            query, 
            conversation_history,  # 이전 대화 전달
            summarize_function     # 요약 함수 전달
        )

if __name__ == "__main__":
    load_dotenv()
    db = connect_DB()
    embeddings = set_embedding_model()
    vectorstore = create_pgvector_store(db, embeddings)
    #create_faq_vectordb(db,vectorstore) #<- 처음 한번 실행
    search(vectorstore)


