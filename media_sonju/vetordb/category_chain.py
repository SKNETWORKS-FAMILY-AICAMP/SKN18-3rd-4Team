from vetordb.set_model import set_classify_model
from langchain.schema import HumanMessage


def classify_category(question: str) -> str:
    CATEGORIES = [
        "공기청정기", "비데", "안마의자", "계약관련", "관리서비스", "구독/멤버십제도", "요금납부",
        "제휴카드", "히터", "믹서기", "냉장고", "커피머신", "전기온수기", "세탁기", "상업용 스팀오븐레인지",
        "상업용 튀김기", "선풍기", "이동식에어컨", "써큘레이터", "청소기", "매트리스", "의류건조기",
        "전동식 빨래건조대", "제습기", "정수기", "제빙기", "슈퍼아이스", 
        "가스오븐", "레인지후드", "식기세척기", "음식물처리기", "전자레인지", "전기오븐"
        ]
    prompt = f"""
                다음 고객 질문이 어떤 가전제품에 대한 것인지 가장 적절한 카테고리를 선택해줘.
                만약 특정 카테고리에 속하지 않으면 '기타'라고 대답해줘.
                카테고리 후보: {', '.join(CATEGORIES)}

                질문: "{question}"

                출력 형식: 카테고리 이름만 출력
            """
    chat_model = set_classify_model() 
    res = chat_model.invoke([HumanMessage(content=prompt)])
    return res.content.strip()