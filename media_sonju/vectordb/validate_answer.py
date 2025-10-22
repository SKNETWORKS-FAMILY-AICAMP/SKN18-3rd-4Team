from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .set_model import set_validate_model

def validate_answer(query, answer):
    """
    LLM 답변이 사용자 질문과 관련있는지 검증
    
    Args:
        query: 사용자 질문
        answer: LLM이 생성한 답변
        
    Returns:
        dict: {
            "is_valid": bool,
            "score": float,        # 1-5점
            "reason": str (optional)
        }
    """
    validation_prompt = ChatPromptTemplate.from_messages([
        ("system", 
            """
            당신은 AI 답변의 품질을 평가하는 전문가입니다.
            
            다음 답변이 사용자의 질문에 대해 얼마나 적합한지를 1~5점으로 평가하세요.
            
            [AI의 답변 평가 지침]
            평가 기준:
            - 매우 적합함 (질문에 완벽히 부합, 구체적이고 유용한 정보 제공): 5점
            - 적합함 (질문에 잘 부합, 충분한 정보 제공): 4점  
            - 보통 (질문과 관련있으나 일부 부족한 정보): 3점
            - 부적합함 (질문과 약간 관련있으나 핵심을 벗어남): 2점
            - 매우 부적합함 (질문과 무관하거나 무응답): 1점
            
            다음 경우는 반드시 낮은 점수를 부여하세요:
            - "정보를 찾지 못했습니다" 같은 무응답: 1점
            - 질문과 주제가 다른 내용: 1-2점
            
            점수만 숫자로 답변하세요 (1-5).
            질문이 답변에 충분히 반영되지 않았다면 낮은 점수를 주세요.

            [사용자의 질문 지침]
            질문이 올바르게 답변되었는지 엄격하게 평가하세요.   
            질문이 목적에 부합하는지 신중히 판단하세요.
            질문이 목적에 부합하지 않으면 다시 사용자의 질문을 받으세요.


            """),
        ("human", "사용자 질문: {question}\n\nAI 답변: {answer}")
    ])
    
    llm = set_validate_model()
    chain = validation_prompt | llm | StrOutputParser()
    
    score_str = chain.invoke({
            "question": query,
            "answer": answer
        })
    score = float(score_str.strip())
        
        # 점수가 1-5 범위를 벗어나면 기본값 설정
    if score < 1 or score > 5:
            print(f"[경고] 비정상적인 점수: {score}, 기본값 3.0 사용")
            score = 3.0
        
        # 3점 이상이면 적합한 답변으로 판단
    is_valid = score >= 3.0
        
    print(f"[답변 검증 결과] 점수: {score:.1f}/5.0 - {'✓ 통과' if is_valid else '✗ 실패'}")
        
    return {
            "is_valid": is_valid,
            "score": score,
            "threshold": 3.0
        }