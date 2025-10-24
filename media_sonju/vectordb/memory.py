from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from .set_model import set_classify_model  # 요약용 LLM으로 재사용

# ================== ConversationSummaryMemory ===========================
def summarize_old_messages(messages, llm, max_messages=5):
    """
    오래된 메시지들을 AI로 요약하는 함수

    Args:
        messages: 전체 대화 메시지 리스트
        llm: 요약에 사용할 LLM 모델
        max_messages: 최근 메시지 유지 개수

    Returns:
        요약된 메시지 리스트 (요약 시스템 메시지 + 최근 메시지들)
    """
    # 메시지가 적으면 요약 없이 그대로 반환
    if len(messages) <= max_messages:
        return messages

    # 오래된 메시지와 최근 메시지 분리
    old_messages = messages[:-max_messages]
    recent_messages = messages[-max_messages:]

    # 요약용 프롬프트 템플릿
    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 SK매직 고객 상담 대화를 요약하는 전문가입니다.
            다음 대화 내용에서 핵심 정보만 추출해서 3-5문장으로 요약해주세요.
            중요한 정보:
            - 문의한 제품 카테고리 (냉장고, 세탁기 등)
            - 문제 증상이나 질문 내용
            - 제공된 답변의 핵심
            - 사용자가 언급한 구체적인 정보 (에러코드 등)

            불필요한 인사말이나 반복된 내용은 생략하세요."""),
        ("user", "다음 대화를 요약해주세요:\n\n{conversation}")
    ])

    # 오래된 메시지들을 텍스트로 변환
    conversation_text = ""
    for msg in old_messages:
        if hasattr(msg, 'type'):
            if msg.type == "human":
                conversation_text += f"사용자: {msg.content}\n"
            elif msg.type == "ai":
                conversation_text += f"AI: {msg.content}\n"
        else:
            # HumanMessage, AIMessage 등 타입별 처리
            msg_type = type(msg).__name__
            if "Human" in msg_type:
                conversation_text += f"사용자: {msg.content}\n"
            elif "AI" in msg_type:
                conversation_text += f"AI: {msg.content}\n"

    # AI로 요약 생성
    try:
        summary_chain = summary_prompt | llm
        summary_response = summary_chain.invoke({"conversation": conversation_text})
        print("🔍 [DEBUG] Memory 요약 내용:")
        summary_content = summary_response.content
    except Exception as e:
        # 요약 실패 시 폴백: 간단한 텍스트 요약
        print(f"[경고] AI 요약 실패: {e}")
        summary_content = f"이전 대화 요약 ({len(old_messages)}개 메시지):\n{conversation_text[:300]}..."

    # 요약을 시스템 메시지로 생성
    summary_message = SystemMessage(
        content=f"[이전 대화 요약]\n{summary_content}"
    )

    # 요약본 + 최근 메시지 반환
    return [summary_message] + recent_messages


def get_conversation_summary_memory(max_messages=5):
    """
    ConversationSummaryMemory 설정을 반환

    Args:
        max_messages: 요약 없이 유지할 최근 메시지 개수

    Returns:
        summarize_function: 요약 함수
        llm: 요약에 사용할 LLM 모델
    """
    # 요약용 LLM 설정 (gpt-4o-mini 사용)
    llm = set_classify_model()

    # 요약 함수를 클로저로 반환
    def summarize_function(messages):
        return summarize_old_messages(messages, llm, max_messages)

    return summarize_function


# =================공통 유틸리티=====================
def get_memory_config(memory_type="summary"):
    """
    메모리 타입에 따른 설정 반환

    Args:
        memory_type: "summary"

    Returns:
        메모리 설정 객체
    """
    if memory_type == "summary":
        return {
            "type": "ConversationSummaryMemory",
            "summarize_function": get_conversation_summary_memory(),
            "description": "대화 요약 기반 메모리 (최근 5개 메시지 유지, 나머지는 요약)"
        }
    else:
        raise ValueError(f"지원하지 않는 메모리 타입: {memory_type}")