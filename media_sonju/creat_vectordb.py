from media_sonju.vectordb.connect_db import connect_DB
from media_sonju.vectordb.split_chunk import make_chunk
from media_sonju.vectordb.set_model import set_embedding_model
from media_sonju.vectordb.pgvector import (
    create_pgvector_store,
    add_documents_to_pgvector,
)
from dotenv import load_dotenv

def create_faq_vectordb(db, vectorstore):
    chunks = make_chunk(db)
    add_documents_to_pgvector(vectorstore, chunks)
    
    
if __name__ == "__main__":
    load_dotenv()
    db =connect_DB()
    embeddings = set_embedding_model()
    vectorstore = create_pgvector_store(db, embeddings)
    create_faq_vectordb(db,vectorstore) #<- 처음 한번 실행
    #search(vectorstore)


