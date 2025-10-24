from initial_state import SelfRAGState
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from .set_model import set_llm_model
from .memory import get_conversation_summary_memory  # 추가


def chat_llm(state: SelfRAGState) -> SelfRAGState:
    print(f"{state.get('domain')} AI 챗봇 실행")
    question = state.get("question")

    context_parts = []
    for doc in state.get("retrieved_docs"):
        context_parts.append(f"### {doc['search_category']}관련 문서 ###")
        metadata = doc.get("metadata", {})
        context_parts.append(f"- {doc['content'].strip()} (출처: {metadata.get('title')})")

    context = "\n".join(context_parts)
    
    # === Memory 기능 추가 ===
    # 1. 이전 대화 이력 가져오기
    conversation_history = state.get("conversation_history", [])
    
    # 2. Memory 요약 함수 설정 (최근 5개 메시지 유지)
    summarize_function = get_conversation_summary_memory(max_messages=5)
    
    # 3. 대화 이력이 많으면 요약
    if len(conversation_history) > 5:
        conversation_history = summarize_function(conversation_history)
    
    # === 프롬프트 구성 ===
    # 시스템 메시지
    system_message = SystemMessage(
        content=(
            "당신은 기술지원 상담 AI 챗봇입니다. "
            "고객의 불편사항 및 오류 사항에 대해 항상 논리적이고, 정확하게 한국어로 해결하는 방안을 답변해주세요.\n"
            "이전 대화 내용을 참고하여 맥락에 맞는 답변을 제공하세요."
        )
    )
    
    # 현재 질문 메시지
    current_question_template = f"""
        다음은 질문에 대해 관련된 정보입니다:

        문서 내용:
        {context}
            
        위 정보를 종합적으로 참고하여 다음 사용자 질문에 답변하세요.
        마지막에 참고한 문서에 대한 출처들에 대해 작성해주세요.

        질문: {question}
"""
    
    # === 메시지 리스트 구성 ===
    # [시스템 메시지] + [이전 대화 이력] + [현재 질문]
    messages = [system_message]
    messages.extend(conversation_history)  # 이전 대화 추가
    messages.append(HumanMessage(content=current_question_template))  # 현재 질문
    
    # === LLM 호출 ===
    model = set_llm_model()
    response = model.invoke(messages)
    
    # === 대화 이력 업데이트 ===
    # 현재 질문과 답변을 이력에 추가
    updated_history = conversation_history + [
        HumanMessage(content=question),  # 사용자 질문
        AIMessage(content=response.content)  # AI 답변
    ]
    
    return {
        **state,
        "final_answer": response.content,
        "conversation_history": updated_history  # 업데이트된 이력 반환
    }