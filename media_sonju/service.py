from functools import lru_cache
from dotenv import load_dotenv

from media_sonju.vectordb.connect_db import connect_DB
from media_sonju.vectordb.pgvector import create_pgvector_store
from media_sonju.vectordb.set_model import set_embedding_model
from media_sonju.rag_workflow import create_self_rag_workflow
from media_sonju.run_rag import run_self_rag


@lru_cache(maxsize=1)
def init_self_rag():
    load_dotenv()
    db = connect_DB()
    embeddings = set_embedding_model()
    vectorstore = create_pgvector_store(db, embeddings)
    return create_self_rag_workflow(vectorstore)


def ask_self_rag(question: str, history=None, verbose: bool = False) -> str:
    app = init_self_rag()
    result = run_self_rag(
        app,
        question,
        conversation_history=history,
        verbose=verbose,
    )
    return result.get("final_answer", "")
