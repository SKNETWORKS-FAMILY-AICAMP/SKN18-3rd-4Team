from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from .set_model import set_llm_model

def build_context(all_results):
    context_parts = []
    for category, docs in all_results.items():
        context_parts.append(f"### {category}관련 문서 ###")
        for doc, _ in docs:
            context_parts.append(f"- {doc.page_content.strip()}")

    return "\n".join(context_parts)


# def chat_llm(context, query):
#     """
#     기본 챗봇 함수 (메모리 없음)

#     Args:
#         context: FAQ 검색 결과 컨텍스트
#         query: 사용자 질문
#     """
#     prompt_template = f"""
#         다음은 유사도 기반으로 검색된 FAQ 내용입니다:

#         문서 내용:
#             {context}

#         위 정보를 참고하여 다음 사용자 질문에 답변하세요.
#         질문: {query}

#     """
#     chat_prompt = ChatPromptTemplate.from_messages([
#         SystemMessage(
#             content=(
#                 "당신은 고객 상담 AI 챗봇입니다. 항상 친절하게 한국어로 답변해주세요."
#             )
#         ),
#         HumanMessagePromptTemplate.from_template(prompt_template),
#         ])
#     model = set_llm_model()
#     chain = chat_prompt | model
#     response = chain.invoke({
#         "context": context,
#         "query":query
#     })
#     print(response.content)
#     return response.content


# ============================================
# 메모리 기능이 추가된 챗봇 (ConversationSummaryMemory)
# ============================================

def chat_llm_with_memory(context, query, conversation_history, summarize_function):
    """
    메모리 기능이 있는 챗봇 함수

    Args:
        context: FAQ 검색 결과 컨텍스트
        query: 사용자 질문
        conversation_history: 전체 대화 기록 리스트
        summarize_function: 대화 요약 함수

    Returns:
        response_content: AI 답변 내용
        updated_history: 업데이트된 대화 기록
    """
    # 대화 기록이 많으면 요약
    summarized_messages = summarize_function(conversation_history)

    prompt_template = f"""
        다음은 유사도 기반으로 검색된 FAQ 내용입니다:

        문서 내용:
            {context}

        위 정보를 참고하여 다음 사용자 질문에 답변하세요.
        이전 대화 내용도 고려하여 맥락에 맞는 답변을 제공하세요.
        질문: {query}
    """

    # 시스템 메시지 + 요약된 대화 기록
    messages = [
        SystemMessage(
            content=(
                "당신은 SK매직 고객 상담 AI 챗봇입니다. "
                "항상 친절하게 한국어로 답변해주세요. "
                "이전 대화 내용을 참고하여 맥락을 이해하고 답변하세요."
            )
        )
    ]

    # 요약된 대화 기록 추가
    messages.extend(summarized_messages)

    # 현재 질문 추가
    chat_prompt = ChatPromptTemplate.from_messages([
        *messages,
        HumanMessagePromptTemplate.from_template(prompt_template),
    ])

    model = set_llm_model()
    chain = chat_prompt | model
    response = chain.invoke({
        "context": context,
        "query": query
    })

    print(response.content)

    # 대화 기록 업데이트
    updated_history = conversation_history + [
        HumanMessage(content=query),
        AIMessage(content=response.content)
    ]

    return response.content, updated_history


    