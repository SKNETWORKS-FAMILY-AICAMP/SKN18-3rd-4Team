from initial_state import SelfRAGState
from langchain.prompts import PromptTemplate
from vectordb.set_model import set_llm_model

def __get_prompt_for_rewriting_question():
    template = """
    당신은 최고의 질문 재작성자입니다.
    다시 벡터DB에서의 정확한 조회를 위해 사용자의 질문을 한국어로 명확한 표현을 적용하여 하나의 질문으로 재작성해주세요. 
    사용자의 질문을 넣었을 때 나온 문장들에 대한 평가 메세지입니다. 참고해서 다시 사용자의 질문을 재작성해주세요
    
    평가 메세지: {message}

    사용자의 질문: {question}
    """

    return PromptTemplate.from_template(template=template)

def question_retrive(state: SelfRAGState) -> SelfRAGState:
    # retry_count = state.get("retry_count", 0)
    # 1회 초과시 종료 신호
    if max_token == True:
        print("\n[안내] 적절한 답변을 찾을 수 없습니다.")
        return {
            **state,
            "max_token": max_token,
            "need_quit": True
        }

    max_token += 1
    # 사용자에게 다시 질문 받기
    #-> final message로 변경
    print(f"\n[평가 메시지] 'DB에서 관련 정보를 찾지 못했습니다.'")
    print("="*50)
    new_question = input("질문을 다시 입력해주세요: ")
    return {
        **state,
        "question": new_question,  # 사용자가 입력한 새 질문
        "max_token": max_token
    }