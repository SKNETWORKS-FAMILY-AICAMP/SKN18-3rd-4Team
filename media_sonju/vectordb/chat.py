from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import HumanMessagePromptTemplate, MessagesPlaceholder
from .set_model import set_llm_model
from .memory import get_conversation_summary_memory

def build_context(relevant_docs):
    context_parts = []
    domain = relevant_docs.get("domain")
    context_parts.append(f"도메인: {domain}\n")
    results = relevant_docs.get("content")
    for doc in results:
        context_parts.append(f"### {doc['category']}관련 문서 ###")
        metadata = doc.get("metadata", {})
        context_parts.append(f"- {doc['content'].strip()} (출처: {metadata.get("title")})")

    context =  "\n".join(context_parts)
    return context

def chat_llm(context, query, chat_history=None):
    """
    메모리 기능이 추가된 챗봇 응답 함수

    Args:
        context: 검색된 FAQ 문서 내용
        query: 사용자 질문
        chat_history: 대화 이력 리스트

    Returns:
        response_content: AI 응답 내용
    """
    # 대화 이력이 없으면 빈 리스트로 초기화
    if chat_history is None:
        chat_history = []

    # 메모리 요약 함수 가져오기
    summarize_function = get_conversation_summary_memory(max_messages=10)

    # 대화 이력이 있으면 요약 적용
    processed_history = summarize_function(chat_history) if chat_history else []

    prompt_template = f"""
        다음은 유사도 기반으로 검색된 FAQ 내용입니다 :

        문서 내용:
            {context}

        위 정보를 종합적으로 참고하여 다음 사용자 질문에 답변하세요 마지막에 참고한 문서에 대한 출처들에 대해 작성해주세요.
        질문: {query}

    """

    # 프롬프트 템플릿에 메시지 플레이스홀더 추가
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content=(
                "당신은 고객 상담 AI 챗봇입니다. 항상 친절하게 한국어로 답변해주세요."
            )
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(prompt_template),
    ])

    model = set_llm_model()
    chain = chat_prompt | model

    response = chain.invoke({
        "context": context,
        "query": query,
        "chat_history": processed_history
    })

    print(response.content)

    # 응답 내용 반환
    return response.content


    