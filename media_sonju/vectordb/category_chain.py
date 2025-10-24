from vectordb.set_model import set_classify_model
from langchain.prompts import PromptTemplate
from initial_state import SelfRAGState
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
from langgraph.graph import END
#from set_model import set_classify_model
class CategoryResponse(BaseModel):
    need_quit: bool
    domain: str | None = None
    category: list[str] | None = None


def decide_classify_category(state: SelfRAGState) -> SelfRAGState:
    # question_retrive에서 need_quit이 True로 설정된 경우 그대로 유지
    if state.get("need_quit", False):
        return {**state}

    CUSTOMER_SUPPORT  = ["계약관련", "관리서비스", "구독/멤버십제도", "요금납부","제휴카드"]
    TECH_SUPPORT = ["공기청정기", "비데", "안마의자", "히터", "믹서기", "냉장고", "커피머신", "전기온수기",
                    "세탁기", "상업용 스팀오븐레인지","상업용 튀김기", "선풍기", "이동식에어컨", "써큘레이터",
                    "청소기", "매트리스", "의류건조기","전동식 빨래건조대", "제습기", "정수기", "제빙기",
                    "슈퍼아이스", "가스오븐", "레인지후드", "식기세척기", "음식물처리기", "전자레인지", "전기오븐"]

    # === 대화 이력 처리 (Memory 맥락 활용) ===
    conversation_history = state.get("conversation_history", [])
    context_summary = ""

    if conversation_history:
        # 최근 4개 메시지 (2개 질문+답변) 추출
        recent_messages = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history

        context_parts = []
        for msg in recent_messages:
            msg_type = type(msg).__name__
            # HumanMessage 또는 type이 "human"인 경우
            if "Human" in msg_type or (hasattr(msg, 'type') and msg.type == "human"):
                content_preview = msg.content[:80] + ("..." if len(msg.content) > 80 else "")
                context_parts.append(f"이전 질문: {content_preview}")
            # AIMessage 또는 type이 "ai"인 경우
            elif "AI" in msg_type or (hasattr(msg, 'type') and msg.type == "ai"):
                # AI 답변은 너무 길 수 있으므로 첫 80자만
                content_preview = msg.content[:80] + ("..." if len(msg.content) > 80 else "")
                context_parts.append(f"이전 답변: {content_preview}")

        if context_parts:
            context_summary = "\n".join(context_parts)

    # === 프롬프트 템플릿 (대화 맥락 포함) ===
    template = """
                {context}

                다음 고객 질문에 대해 분석해주세요.

                1. 제일 먼저!!!!!! 우리의 서비스는 아래와 같은 서비스만 지원합니다. 지원하는 서비스가 아니라면 need_quit 가 True로 답해주세요!!
                    - 고객지원: 계약/요금/카드/회원/구독/구매/관리 서비스 등 일반 고객 문의
                    - 기술지원: 제품 고장/설치/사용법/점검/수리 등 기기 관련

                    💡 중요: "처음에", "그", "그거", "아까", "이전에" 같은 대명사가 있고 위에 이전 대화 맥락이 있다면,
                    이전 대화를 참고하여 분류하세요! 이전 대화에서 언급된 제품 카테고리를 우선 고려하세요.

                2. 그 다음 고객 질문에 대해 고객지원인지, 기술질문인지 분류해주세요

                3. 도메인 분류 후!!!!!, 아래 써져있는 도메인에 따른 세부 카레고리 후보에 따라 category를 작성해주세요.
                    여러개에 속하면 category에 여러개를 작성해주세요. 단, 분류할 수 없으면 None으로 대답해주세요!!

                    - 고객지원 세부 카테고리 후보: {customer_support}
                    - 기술지원 세부 카테고리 후보: {tech_support}

                현재 질문: {question}

                출력 형식은 반드시 JSON으로만 출력해주세요.
                예시)
                {{
                    "need_quit" : false,
                    "domain" : "고객지원",
                    "category" : ["구독/멤버십제도"]
                }}
            """
    parser = JsonOutputParser(pydantic_object=CategoryResponse)
    prompt = PromptTemplate.from_template(template)
    chain = prompt | set_classify_model() | parser

    # context_summary를 프롬프트에 전달
    context_text = f"[이전 대화 맥락]\n{context_summary}\n" if context_summary else "[이전 대화 없음]\n"

    res = chain.invoke({
        "context": context_text,
        "question": state["question"],
        "customer_support": ", ".join(CUSTOMER_SUPPORT),
        "tech_support": ", ".join(TECH_SUPPORT)
    })

    # state의 다른 필드들을 유지하면서 res의 내용을 업데이트
    return {**state, **res}
    
def classify_quit(state: SelfRAGState) -> str:    
    if state.get("need_quit"):
        if state.get("max_token") == False:
            print("\n[안내] DB에서 적절한 답변을 찾지 못했습니다. 다시 시도해주세요.")
        else:
            print("지원하지 않는 질문입니다.")
        return END
    else:
        return "search"