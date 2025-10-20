from vetordb.connect_db import connect_DB
from vetordb.split_chunk import make_chunk
from vetordb.set_model import set_embedding_model
from vetordb.pgvector import create_pgvector_store, add_documents_to_pgvector
from dotenv import load_dotenv
from vetordb.search_query import search_question

       
def create_faq_vectordb(db, vectorstore):
    chunks = make_chunk(db)
    add_documents_to_pgvector(vectorstore, chunks)
    
    
    
def search(vectorstore):
    query = input(f"궁금한 점을 입력하세요: ")# 질문 검색
    search_question(vectorstore, query)
    
    
if __name__ == "__main__":
    load_dotenv()
    db =connect_DB()
    embeddings = set_embedding_model()
    vectorstore = create_pgvector_store(db, embeddings)
    #create_faq_vectordb(db,vectorstore) #<- 처음 한번 실행
    search(vectorstore)

