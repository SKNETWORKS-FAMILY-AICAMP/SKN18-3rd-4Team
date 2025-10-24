from initial_state import SelfRAGState
from langchain.prompts import PromptTemplate
from vectordb.set_model import set_llm_model

def __get_prompt_for_rewriting_question():
    template = """
    # **질문 재작성 작업**

    당신은 **RAG 검색 품질 개선 전문가**입니다.
    사용자의 질문을 벡터DB 검색에 최적화된 문장으로 **한국어로 재작성**하세요.

    ## 참고 자료
    아래는 이전 단계에서 평가된 메시지입니다.
    이를 참고하여 더 명확하고 구체적인 질문으로 바꿔주세요.

    ---
    # 평가 메세지:
    {message}

    # 원본 질문:
    {question}

    ---
    # 출력 형식
    - 오직 하나의 재작성된 문장만 출력합니다.
    - 설명이나 추가 문구 없이 질문만 작성합니다.
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
        "question": result.content,
        "max_token":True
    }