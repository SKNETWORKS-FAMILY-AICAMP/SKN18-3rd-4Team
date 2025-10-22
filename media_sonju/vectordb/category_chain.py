from vectordb.set_model import set_classify_model
from langchain.schema import HumanMessage
from initial_state import SelfRAGState

def decide_classify_category(state: SelfRAGState) -> SelfRAGState:
    CUSTOMER_SUPPORT  = ["계약관련", "관리서비스", "구독/멤버십제도", "요금납부","제휴카드"]
    TECH_SUPPORT = ["공기청정기", "비데", "안마의자", "히터", "믹서기", "냉장고", "커피머신", "전기온수기", 
                    "세탁기", "상업용 스팀오븐레인지","상업용 튀김기", "선풍기", "이동식에어컨", "써큘레이터", 
                    "청소기", "매트리스", "의류건조기","전동식 빨래건조대", "제습기", "정수기", "제빙기",
                    "슈퍼아이스", "가스오븐", "레인지후드", "식기세척기", "음식물처리기", "전자레인지", "전기오븐"]
    prompt = f"""
                다음 고객 질문에 대해 분석해주세요.
                1. 도메인을 분류하세요: '고객지원' 또는 '기술지원', '없음'이라고 출력
                    - 고객지원: 계약/요금/카드/회원/구독/구매/관리 서비스 등 일반 고객 문의
                    - 기술지원: 제품 고장/설치/사용법/점검/수리 등 기기 관련
                2. 먼저!!!! 도메인 먼저!!!!! 도메인 분류 후에, 고객지원은 CUSTOMER_SUPPORT에서, 기술지원은 TECH_SUPPORT에서 세부 카테고리를 분류하세요.!!

                    - 고객지원 세부 카테고리 후보: {', '.join(CUSTOMER_SUPPORT)}
                    - 기술지원 세부 카테고리 후보: {', '.join(TECH_SUPPORT)}

                [예시]
                - 질문: 의류건조기 구매 어떻게 해? -> 도메인: 고객지원, 세부카테고리: 구독/멤버십제도
                
                - 질문: 의류건조기에서 물방울이 맺혀 -> 도메인: 기술지원, 세부카테고리: 의류건조기
                
                - 질문: 전원이 안켜져 -> 도메인: 기술지원, 세부카테고리: 없음
                
                - 질문: 해약은 어떻게 하는거야 -> 도메인: 고객지원, 세부카테고리: 계약관련
                
                - 질문: 의류건조기와 히터에서 큰 소리가 나 -> 도메인: 기술지원, 세부 카테고리: 의류건조기, 히터


                질문: "{state["question"]}"
                
                출력 형식:
                    도메인: <고객지원/기술지원/없음>
                    세부 카테고리: <카테고리 이름(여러 개일 수 있음, 쉼표로 구분) 또는 없음>
            """
    chat_model = set_classify_model() 
    res = chat_model.invoke([HumanMessage(content=prompt)])
    output = res.content.strip()
    # 파싱
    domain, categories  = None, []
    for line in output.splitlines():
        if line.startswith("도메인:"):
            domain = line.replace("도메인:", "").strip()
        if line.startswith("세부 카테고리:"):
            cat_str = line.replace("세부 카테고리:", "").strip()
            if cat_str != "없음":
                categories = [c.strip() for c in cat_str.split(",")]
    if domain in ["고객지원", "기술지원"]:
        return {
            **state,
            "need_retrieval": False,
            "domain": domain, 
            "category": categories if categories else None}
    else:
        return {
            **state,
            "need_retrieval": True,
            "message": "죄송합니다. 지원하지 않는 질문입니다. 다시 입력해주세요"
        }

def should_question(state: SelfRAGState) -> str:
    """검색 필요성에 따라 다음 단계를 결정하는 조건부 함수"""
    if state["need_retrieval"]:
        return "retrieve"
    else:
        return "generate"
    
def unsupported_node(state: SelfRAGState) -> SelfRAGState:
    print(state.get("message"))
    # 새 질문을 받도록 로직 설계 (예: 사용자 입력 대기 or 다음 단계로 리턴)
    new_question = input("질문을 입력해주세요: ")  # 또는 UI단에서 입력 받음
    state["question"] = new_question
    return state