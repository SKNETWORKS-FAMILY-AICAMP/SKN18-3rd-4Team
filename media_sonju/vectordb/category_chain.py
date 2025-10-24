from media_sonju.vectordb.set_model import set_classify_model
from langchain.prompts import PromptTemplate
from media_sonju.initial_state import SelfRAGState
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
from langgraph.graph import END

class CategoryResponse(BaseModel):
    need_quit: bool
    domain: str | None = None
    category: list[str] | None = None

def decide_classify_category(state: SelfRAGState) -> SelfRAGState:
    message = state.get("final_answer")

    conversation_history = state.get("conversation_history", [])
    history_text = ""
    if conversation_history:
        # 최근 3개만 사용 (토큰 절약)
        for msg in conversation_history[-3:]:
            history_text += f"{msg}\n"
    
    CUSTOMER_SUPPORT  = ["계약관련", "관리서비스", "구독/멤버십제도", "요금납부","제휴카드"]
    TECH_SUPPORT = ["공기청정기", "비데", "안마의자", "히터", "믹서기", "냉장고", "커피머신", "전기온수기", 
                    "세탁기", "상업용 스팀오븐레인지","상업용 튀김기", "선풍기", "이동식에어컨", "써큘레이터", 
                    "청소기", "매트리스", "의류건조기","전동식 빨래건조대", "제습기", "정수기", "제빙기",
                    "슈퍼아이스", "가스오븐", "레인지후드", "식기세척기", "음식물처리기", "전자레인지", "전기오븐"]

    template = """
    # **카테고리 분류 지시사항**

    아래 고객 질문에 대해 **정확한 JSON 형식**으로만 출력하세요.
    모든 필드는 반드시 포함되어야 하며 생략하지 마세요.

    ---
    ## 도메인(domain)
    - 반드시 "고객지원" 또는 "기술지원" 중 하나로 지정합니다.
    - 둘 다 해당되지 않으면 `"domain": null` 로 작성합니다.
    - 절대로 빈 문자열("")이나 생략은 허용되지 않습니다.

    ## 세부 카테고리(category)
    - 도메인별 후보 리스트 중 하나 이상을 선택합니다.
    - 없으면 null로 작성합니다.

    ### 고객지원 후보
    {customer_support}

    ### 기술지원 후보
    {tech_support}

    ---
    ## 출력 예시
    {{
        "need_quit": false,
        "domain": "기술지원",
        "category": ["공기청정기"]
    }}

    ---
    # 질문:
    {question}
    """

    parser = JsonOutputParser(pydantic_object=CategoryResponse)
    prompt = PromptTemplate.from_template(template)
    chain = prompt | set_classify_model() | parser
    res = chain.invoke({
        "question": state.get("question"),
        "customer_support": ", ".join(CUSTOMER_SUPPORT),
        "tech_support": ", ".join(TECH_SUPPORT)
    })

    # ✅ 안전 보정
    domain = res.get("domain")
    if not domain or str(domain).strip().lower() in ["", "none", "null"]:
        domain = None

    if res["need_quit"]:
        message = "지원하지 않는 질문입니다. 다시 질문해주세요."

    return {
        **state,
        "need_quit": res.get("need_quit", False),
        "domain": domain,
        "category": res.get("category", []),
        "final_answer": message,
    }

def classify_quit(state: SelfRAGState) -> str:
    if state.get("need_quit", False):
        return END
    return "evaluate_relevance"
