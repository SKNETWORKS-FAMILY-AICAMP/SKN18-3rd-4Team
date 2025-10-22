from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from .set_model import set_llm_model
# import json

def build_context(relevant_docs):
    context_parts = []
    domain = relevant_docs.get("domain")
    context_parts.append(f"도메인: {domain}\n")
    results = relevant_docs.get("content")
    for doc in results:
        context_parts.append(f"### {doc['category']}관련 문서 ###")
        metadata = doc.get("metadata", {})
        context_parts.append(f"- {doc['content'].strip()} (출처: {metadata.get("title")})")
    
    context =  "\n".join(context_parts)
    return context

def chat_llm(context,query):
    prompt_template = f"""
        다음은 유사도 기반으로 검색된 FAQ 내용입니다 :

        문서 내용:
            {context}
                
        위 정보를 종합적으로 참고하여 다음 사용자 질문에 답변하세요 마지막에 참고한 문서에 대한 출처들에 대해 작성해주세요.
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


    