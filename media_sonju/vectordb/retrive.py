from initial_state import SelfRAGState
from langchain.prompts import PromptTemplate
from vectordb.set_model import set_llm_model

def __get_prompt_for_rewriting_question():
    template = """
    당신은 최고의 질문 재작성자입니다.
    다시 벡터DB에서의 정확한 조회를 위해 사용자의 질문을 한국어로 명확한 표현을 적용하여 하나의 질문으로 재작성해주세요. 
    사용자의 질문을 넣었을 때 나온 문장들에 대한 평가 메세지입니다. 참고해서  다시 사용자의 질문을 재작성해주세요
    
    평가 메세지: {message}

    사용자의 질문: {question}
    """
    return PromptTemplate.from_template(template=template)

def question_retrive(state: SelfRAGState) -> SelfRAGState:
    
    llm = set_llm_model()
    chain = __get_prompt_for_rewriting_question() | llm
    
    result = chain.invoke({
        "question": state["question"],
        "message":state["message"],
    })
    return {
        **state,
        "max_token": True,
        "question": result.content
    }