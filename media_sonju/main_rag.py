from dotenv import load_dotenv
from vectordb.connect_db import connect_DB
from vectordb.pgvector import create_pgvector_store
from vectordb.set_model import set_embedding_model
from rag_workflow import create_self_rag_workflow
from run_rag import run_self_rag


if __name__ == "__main__":
    load_dotenv()
    db =connect_DB()
    embeddings = set_embedding_model()
    vectorstore = create_pgvector_store(db, embeddings)
    self_rag_app = create_self_rag_workflow(vectorstore)
    question = input("궁금한 점을 질문하세요: ")
    result = run_self_rag(self_rag_app,question)
    
    

