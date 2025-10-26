from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .utils import set_openapi


def set_embedding_model() -> OpenAIEmbeddings:
    """Instantiate the embedding model used for vector operations."""
    return OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=set_openapi(),
    )


def set_classify_model() -> ChatOpenAI:
    """Return the classifier model for routing questions."""
    return ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=set_openapi(),
        temperature=0,
    )


def set_llm_model() -> ChatOpenAI:
    """Return the main chat model for answer generation."""
    return ChatOpenAI(
        model="gpt-5-nano",
        openai_api_key=set_openapi(),
        reasoning_effort="high",
    )


def set_score_model() -> ChatOpenAI:
    """Return the model used to score document relevance."""
    return ChatOpenAI(
        model="gpt-5-nano",
        openai_api_key=set_openapi(),
        frequency_penalty=0,
    )
