from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .set_model import set_validate_model
import json

def validate_answer(query, answer):
    """
    하나의 통합 검증 에이전트:
    1단계: 질문의 합리성 검증
    2단계: (질문이 VALID할 경우) 답변의 적합성 평가
    """

    llm = set_validate_model()

    # ------------------------------
    # ✅ 통합 검증 프롬프트
    # ------------------------------
    validation_prompt = ChatPromptTemplate.from_messages([
        ("system", 
        """
        당신은 '검증 에이전트(Validation Agent)'입니다.
        사용자 질문과 LLM의 답변을 동시에 평가합니다.

        [작업 단계]
        1. 질문의 합리성 평가
           - 구체적이고 의미가 명확하며, 실제로 답변 가능한 질문이면 'VALID'
           - 모호하거나 비논리적이거나 의미가 통하지 않으면 'INVALID'

	    예시)
        - "매트리스에 물이 나와요" → INVALID
        - "매트리스에서 물이 새는 이유는 무엇인가요?" → INVALID
        - "냉장고가 작동하지 않아요" → VALID
        - "냉장고에 기분이 나빠요" → INVALID

        2. (질문이 VALID한 경우) 답변 적합성 평가
           - 질문에 대한 답변의 관련성과 품질을 1~5점으로 평가하세요.

        [답변 점수 기준]
        - 5점: 매우 적합 (질문과 완벽히 부합, 구체적이고 유용함)
        - 4점: 적합 (충분히 부합, 유용함)
        - 3점: 보통 (관련은 있으나 일부 부족)
        - 2점: 부적합 (부분적으로 관련 있으나 핵심 벗어남)
        - 1점: 매우 부적합 (무관하거나 틀린 답변)

        [출력 형식(JSON)]
        다음 JSON 형식으로만 출력하세요. 추가 문장은 절대 포함하지 마세요.
        {{
            "is_question_valid": true or false,
            "question_feedback": "질문에 대한 평가 설명",
            "answer_score": 1~5 or null,
            "answer_feedback": "답변에 대한 품질 설명 또는 null"
        }}
        """),

        ("human",
        """
        사용자 질문: {question}

        LLM 답변: {answer}
        """)
    ])

    chain = validation_prompt | llm | StrOutputParser()
    response = chain.invoke({
        "question": query,
        "answer": answer
    }).strip()

    # ------------------------------
    # 결과 파싱
    # ------------------------------
    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        result = {
            "is_question_valid": False,
            "question_feedback": "출력 형식 오류",
            "answer_score": None,
            "answer_feedback": None
        }

    # ------------------------------
    # 점수 보정 및 통과 여부 판단
    # ------------------------------
    score = result.get("answer_score")
    if score is None:
        score = 0.0

    try:
        score = float(score)
    except:
        score = 0.0

    # 질문이 유효하고, 답변 점수가 3 이상일 때 “통과”
    is_valid = result.get("is_question_valid", False) and (score >= 3.0)
    return {
        "is_valid": is_valid,
        "is_question_valid": result.get("is_question_valid"),
        "question_feedback": result.get("question_feedback"),
        "score": score,
        "answer_feedback": result.get("answer_feedback"),
        "threshold": 3.0
    }
