from vectordb.set_model import set_classify_model
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
                다음 고객 질문이 어떤 가전제품에 해당하는지 판단하세요.
                - 질문이 여러 카테고리에 해당하면 모두 선택하세요.
                - 관련 없는 질문은 '기타'라고 답하세요.
                - 카테고리 이름만 쉼표로 구분해서 출력하세요.
                
                예시:
                    - "공기청정기 필터를 교체하려면?" → 공기청정기
                    - "요금 납부 방법이 궁금해요" → 요금납부
                    - "필터 청소 방법 알려줘" → 기타
                    - "식기세척기와 공기청정기가 전원이 안켜져요" → 식기세척기, 공기청정기

                
                카테고리 후보: {', '.join(CATEGORIES)}

                질문: "{question}"
            """
    chat_model = set_classify_model() 
    res = chat_model.invoke([HumanMessage(content=prompt)])
    # 쉼표로 분리, 공백 제거, 기타 제거
    categories = [c.strip() for c in res.content.split(",") if c.strip() != "기타"]

    return categories