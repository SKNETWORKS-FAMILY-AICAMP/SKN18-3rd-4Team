from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from set_model import set_llm_model

def build_context(all_results):
    context_parts = []
    for category, docs in all_results.items():
        context_parts.append(f"### {category}관련 문서 ###")
        for doc, _ in docs:
            context_parts.append(f"- {doc.page_content.strip()}")

    return "\n".join(context_parts)


def chat_llm(context,query):
    prompt_template = f"""
        다음은 유사도 기반으로 검색된 FAQ 내용입니다:

        문서 내용:
            {context}
                
        위 정보를 참고하여 다음 사용자 질문에 답변하세요.
        질문: {query}

    """
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content=(
                "당신은 고객 상담 AI 챗봇입니다. 항상 친절하게 한국어로 답변해주세요."
            )
        ),
        HumanMessagePromptTemplate.from_template(prompt_template),
        ])
    model = set_llm_model()
    chain = chat_prompt | model
    response = chain.invoke({
        "context": context,
        "query":query
    })
    print(response.content)


    