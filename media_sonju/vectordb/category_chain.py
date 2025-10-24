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
    CUSTOMER_SUPPORT  = ["계약관련", "관리서비스", "구독/멤버십제도", "요금납부","제휴카드"]
    TECH_SUPPORT = ["공기청정기", "비데", "안마의자", "히터", "믹서기", "냉장고", "커피머신", "전기온수기", 
                    "세탁기", "상업용 스팀오븐레인지","상업용 튀김기", "선풍기", "이동식에어컨", "써큘레이터", 
                    "청소기", "매트리스", "의류건조기","전동식 빨래건조대", "제습기", "정수기", "제빙기",
                    "슈퍼아이스", "가스오븐", "레인지후드", "식기세척기", "음식물처리기", "전자레인지", "전기오븐"]

    template = """
        # **카테고리 분류 지시사항**

        아래 고객 질문에 대해 다음 단계를 순서대로 판단하세요.

        ## 1. **지원 서비스 여부 판단**
        - 우리의 서비스는 아래 두 가지 도메인만 지원합니다.
            - 고객지원: 계약/요금/카드/회원/구독/구매/관리 서비스 등
            - 기술지원: 제품 고장/설치/사용법/점검/수리 등
        - 이 외의 서비스라면 `"need_quit": true` 로 설정합니다.

        ## 2. **도메인 분류**
        - 고객지원 또는 기술지원 중 하나를 정확히 선택합니다.

        ## 3. **세부 카테고리 분류**
        - 도메인별 후보 리스트를 참고하여 category를 작성합니다.
        - 여러 개에 속하면 배열로 여러 항목을 포함시킵니다.
        - 분류할 수 없다면 `"category": null` 로 답변합니다.

        ### 고객지원 세부 후보
        {customer_support}

        ### 기술지원 세부 후보
        {tech_support}

        ## 4. **출력 형식 (JSON ONLY)**
        반드시 아래 형식으로만 출력하세요:
        {{
            "need_quit": false,
            "domain": "고객지원",
            "category": ["구독/멤버십제도"]
        }}

        ---
        # **질문**
        {question}
    """
    parser = JsonOutputParser(pydantic_object=CategoryResponse)
    prompt = PromptTemplate.from_template(template)
    chain = prompt | set_classify_model() | parser
    res = chain.invoke({"question": state["question"],
                        "customer_support": ", ".join(CUSTOMER_SUPPORT),
                        "tech_support": ", ".join(TECH_SUPPORT)})

    return res
    
def classify_quit(state: SelfRAGState) -> str:    
    if state.get("need_quit"):
        print("죄송합니다. 지원하지 않는 질문입니다. 다시 입력해주세요")
        return END
    else:
        return "search"