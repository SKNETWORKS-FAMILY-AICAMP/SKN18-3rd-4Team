import json
from typing import Any

from langchain.prompts import PromptTemplate
from langgraph.graph import END

from common.llm.models import set_score_model
from common.langgraph.initial_state import SelfRAGState

from .search_query import search_question


def evaluate_relevance(state: SelfRAGState, vectorstore: Any) -> SelfRAGState:
    """Evaluate retrieved documents and update the Self-RAG state."""

    search_state = {
        "question": state.get("question"),
        "domain": state.get("domain"),
        "category": state.get("category"),
    }
    search_queries = search_question(search_state, vectorstore)

    retrieved_docs = [
        {
            "search_category": category,
            "content": doc.page_content,
            "metadata": doc.metadata,
        }
        for category, docs in search_queries.items()
        for (doc, _) in docs
    ]

    final_message = state.get("final_answer")
    relevant_docs: list[dict] = []
    relevance_scores: list[float] = []
    feedback_messages: list[str] = []

    relevance_prompt = PromptTemplate.from_template(
        """
        #  **검색 문서 관련성 평가**

        당신은 **벡터DB 기반 검색 결과 평가 전문가**입니다.
        사용자의 질문과 문서 내용이 얼마나 관련이 높은지 **0~100점**으로 평가하세요.

        ## 평가 기준
        - **100점:** 질문의 핵심 답변을 직접 포함
        - **70~99점:** 매우 유사하거나 직접적인 관련
        - **50~69점:** 부분적으로 관련 있음
        - **0~49점:** 관련성 낮음 (무시)

        ## 출력 형식 (JSON)
        {{
            "evaluation_score": (0~100),
            "evaluation_detail": "간단한 이유 설명"
        }}

        ---
        # 질문:
        {question}

        # 문서 내용:
        {document}
        """
    )

    chain = relevance_prompt | set_score_model()

    for doc in retrieved_docs:
        try:
            result = chain.invoke(
                {"question": state.get("question"), "document": doc["content"]}
            )
            payload = json.loads(result.content)
        except (ValueError, json.JSONDecodeError):
            print("점수 파싱 오류")
            continue

        score = payload.get("evaluation_score", 0)
        if score >= 50:
            relevant_docs.append(doc)
            relevance_scores.append(float(score))
        else:
            detail = payload.get("evaluation_detail")
            if detail:
                feedback_messages.append(detail)

    retrieval_question = not bool(relevant_docs)

    if retrieval_question and state.get("max_token"):
        final_message = "죄송합니다. 조금 더 상세히 설명해주시면 도와드리도록 하겠습니다."

    avg_relevance = (
        sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
    )

    print(
        f"{len(relevant_docs)}개의 관련 문서를 선별했습니다. "
        f"(평균 관련성: {avg_relevance:.2f})"
    )

    return {
        **state,
        "retrieval_question": retrieval_question,
        "retrieved_docs": relevant_docs,
        "relevance_scores": avg_relevance,
        "message": "\n".join(feedback_messages),
        "final_answer": final_message,
    }


def classify_retrieval(state: SelfRAGState) -> str:
    if state["retrieval_question"]:
        return END if state.get("max_token") else "question_retrive"
    return "chat_llm"
