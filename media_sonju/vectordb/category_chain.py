from vectordb.set_model import set_classify_model
from langchain.prompts import PromptTemplate
from initial_state import SelfRAGState
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
#from set_model import set_classify_model
class CategoryResponse(BaseModel):
    need_retrieval: bool
    domain: str | None = None
    category: list[str] | None = None


def decide_classify_category(state: SelfRAGState) -> SelfRAGState:
    CUSTOMER_SUPPORT  = ["계약관련", "관리서비스", "구독/멤버십제도", "요금납부","제휴카드"]
    TECH_SUPPORT = ["공기청정기", "비데", "안마의자", "히터", "믹서기", "냉장고", "커피머신", "전기온수기", 
                    "세탁기", "상업용 스팀오븐레인지","상업용 튀김기", "선풍기", "이동식에어컨", "써큘레이터", 
                    "청소기", "매트리스", "의류건조기","전동식 빨래건조대", "제습기", "정수기", "제빙기",
                    "슈퍼아이스", "가스오븐", "레인지후드", "식기세척기", "음식물처리기", "전자레인지", "전기오븐"]
    template = """
                다음 고객 질문에 대해 분석해주세요.
                1. 제일 먼저!!!!!! 우리의 서비스는 아래와 같은 서비스만 지원합니다. 지원하는 서비스가 아니라면 need_retrieval 가 True로 답해주세요!!
                    - 고객지원: 계약/요금/카드/회원/구독/구매/관리 서비스 등 일반 고객 문의
                    - 기술지원: 제품 고장/설치/사용법/점검/수리 등 기기 관련
                2. 그 다음 고객 질문에 대해 고객지원인지, 기술질문인지 분류해주세요
                3. 도메인 분류 후!!!!!, 아래 써져있는 도메인에 따른 세부 카레고리 후보에 따라 category를 작성해주세요. 
                    여러개에 속하면 category에 여러개를 작성해주세요. 단, 분류할 수 없으면 None으로 대답해주세요!!

                    - 고객지원 세부 카테고리 후보: {customer_support}
                    - 기술지원 세부 카테고리 후보: {tech_support}

                질문: {question}
                
                출력 형식은 반드시 JSON으로만 출력해주세요.
                예시)
                {{
                    "need_retrieval" : false,
                    "domain" : "고객지원",
                    "category" : ["구독/멤버십제도"]
                }}
            """
    parser = JsonOutputParser(pydantic_object=CategoryResponse)
    prompt = PromptTemplate.from_template(template)
    chain = prompt | set_classify_model() | parser
    res = chain.invoke({"question": state["question"],
                        "customer_support": ", ".join(CUSTOMER_SUPPORT),
                        "tech_support": ", ".join(TECH_SUPPORT)})
    need_retrieval = res["need_retrieval"]
    # 파싱

    if need_retrieval:
        return {
            "need_retrieval": True,
            "message": "죄송합니다. 지원하지 않는 질문입니다. 다시 입력해주세요"
        }
    else:
        #print(res)
        return res

def should_question(state: SelfRAGState) -> str:
    """검색 필요성에 따라 다음 단계를 결정하는 조건부 함수"""
    if state["need_retrieval"]:
        return "unsupported_node"
    else:
        return "search"
    
def unsupported_node(state: SelfRAGState) -> SelfRAGState:
    print(state.get("message"))
    # 새 질문을 받도록 로직 설계 (예: 사용자 입력 대기 or 다음 단계로 리턴)
    new_question = input("질문을 입력해주세요: ")  # 또는 UI단에서 입력 받음
    state["question"] = new_question
    return state
