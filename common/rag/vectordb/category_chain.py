from langgraph.graph import END
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel

from ...llm.models import set_classify_model
from ...langgraph.initial_state import SelfRAGState

class CategoryResponse(BaseModel):
    need_quit: bool
    domain: str | None = None
    category: list[str] | None = None

def decide_classify_category(state: SelfRAGState) -> SelfRAGState:
    message = state.get("final_answer")
    
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
    - 서로 다른 도메인의 이슈가 동시에 포함된 경우 반드시 `"domain": null` 로 설정합니다.

    ## 세부 카테고리(category)
    - 도메인별 후보 리스트 중 하나 이상을 선택합니다. (복수 선택 가능)
    - 질문에 여러 주제가 등장하면 모든 관련 카테고리를 배열에 담습니다.
      예) 정수기 문제 + 구독 해지 → ["정수기", "구독/멤버십제도"]
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

    raw_categories = res.get("category") or []
    if isinstance(raw_categories, str):
        raw_categories = [raw_categories]

    category_order = []
    seen = set()
    for cat in raw_categories:
        normalized = cat.strip()
        if not normalized:
            continue
        if normalized not in CUSTOMER_SUPPORT and normalized not in TECH_SUPPORT:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        category_order.append(normalized)

    has_customer = any(cat in CUSTOMER_SUPPORT for cat in category_order)
    has_tech = any(cat in TECH_SUPPORT for cat in category_order)

    if has_customer and has_tech:
        domain = None
    elif domain is None:
        if has_customer and not has_tech:
            domain = "고객지원"
        elif has_tech and not has_customer:
            domain = "기술지원"

    if res["need_quit"]:
        message = "지원하지 않는 질문입니다. 다시 질문해주세요."

    return {
        **state,
        "need_quit": res.get("need_quit", False),
        "domain": domain,
        "category": category_order,
        "final_answer": message,
    }

def classify_quit(state: SelfRAGState) -> str:
    if state.get("need_quit", False):
        return END
    return "evaluate_relevance"
