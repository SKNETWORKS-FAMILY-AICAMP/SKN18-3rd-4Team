from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

from ..rag.vectordb.connect_db import connect_DB
from ..rag.vectordb.pgvector import create_pgvector_store
from ..llm.models import set_embedding_model
from ..langgraph.workflow import create_self_rag_workflow
from .run_rag import run_self_rag


def _ensure_env_loaded() -> None:
    """프로젝트 전역 .env 또는 media_sonju/.env를 순차적으로 로드."""
    if load_dotenv():
        return

    project_root = Path(__file__).resolve().parents[2]
    fallback_paths = [
        project_root / ".env",
        project_root / "media_sonju" / ".env",
        project_root / "config" / ".env",
    ]

    for env_path in fallback_paths:
        if env_path.exists():
            load_dotenv(env_path)
            return


@lru_cache(maxsize=1)
def init_self_rag():
    _ensure_env_loaded()
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
