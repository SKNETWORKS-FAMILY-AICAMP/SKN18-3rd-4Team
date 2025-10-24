from initial_state import SelfRAGState
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from .set_model import set_llm_model
from initial_state import SelfRAGState


def chat_llm(state: SelfRAGState) -> SelfRAGState:
    print(f"{state.get("domain")} AI 챗봇 실행")
    question = state.get("question")
    context_parts = []
    for doc in state.get("retrieved_docs"):
        context_parts.append(f"### {doc['search_category']}관련 문서 ###")
        metadata = doc.get("metadata", {})
        context_parts.append(f"- {doc['content'].strip()} (출처: {metadata.get("title")})")
    
    context =  "\n".join(context_parts)
    
    
    prompt_template = f"""
        다음은 질문에 대해 관련된 정보입니다 :

        문서 내용:
            {context}
                
        위 정보를 종합적으로 참고하여 다음 사용자 질문에 답변하세요 마지막에 참고한 문서에 대한 출처들에 대해 작성해주세요.
        질문: {question}

    """
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content=(
                "당신은 기술지원 상담 AI 챗봇입니다. 고객의 불편사항 및 오류 사항에 대해 항상 논리적이고, 정확하게 한국어로 해결하는 방안을 답변해주세요."
            )
        ),
        HumanMessagePromptTemplate.from_template(prompt_template),
        ])
    model = set_llm_model()
    chain = chat_prompt | model
    response = chain.invoke({
        "context": context,
        "question":question
    })
    
    return {
        **state,
        "final_answer" : response.content
    }