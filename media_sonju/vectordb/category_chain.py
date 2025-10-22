from vectordb.set_model import set_classify_model
from langchain.schema import HumanMessage


def classify_category(question: str) -> dict:
    CUSTOMER_SUPPORT  = ["계약관련", "관리서비스", "구독/멤버십제도", "요금납부","제휴카드"]
    TECH_SUPPORT = ["공기청정기", "비데", "안마의자", "히터", "믹서기", "냉장고", "커피머신", "전기온수기", 
                    "세탁기", "상업용 스팀오븐레인지","상업용 튀김기", "선풍기", "이동식에어컨", "써큘레이터", 
                    "청소기", "매트리스", "의류건조기","전동식 빨래건조대", "제습기", "정수기", "제빙기",
                    "슈퍼아이스", "가스오븐", "레인지후드", "식기세척기", "음식물처리기", "전자레인지", "전기오븐"]
    prompt = f"""
                다음 고객 질문에 대해 분석해주세요.
                1. 도메인을 분류하세요: '고객지원' 또는 '기술지원' 단, CUSTOMER_SUPPORT, TECH_SUPPORT에서 상관이 없다고 판단되면 없음이라고 출력력
                2. 도메인이 '고객지원'인 경우, 세부 카테고리(CUSTOMER_SUPPORT) 중 해당되는 것이 있으면 출력, 없으면 '없음'이라고 출력
                3. 도메인이 '기술지원'인 경우, 세부 카테고리(TECH_SUPPORT) 중 해당되는 것이 있으면 출력, 없으면 '없음'이라고 출력
            

                고객지원 카테고리 후보: {', '.join(CUSTOMER_SUPPORT)}
                기술지원 카테고리 후보: {', '.join(TECH_SUPPORT)}

                질문: "{question}"
                
                출력 형식:
                    도메인: <고객지원/기술지원>
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
    if domain not in ["고객지원", "기술지원"]:
        return {
            "status": "NOT_SUPPORTED",
            "message": "죄송합니다. 현재 제공되는 고객지원/기술지원 범위 외의 질문입니다. 다른 질문을 해주세요."
        }
    return {
        "status": "SUPPORTED",
        "도메인": domain, 
        "세부카테고리": categories if categories else None}

'''
if __name__ == "__main__":
    question = input("궁금한점 입력: ")
    print(classify_category(question))
'''