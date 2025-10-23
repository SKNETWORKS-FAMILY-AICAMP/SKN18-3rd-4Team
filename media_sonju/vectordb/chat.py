from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from .set_model import set_llm_model
from .validate_answer import validate_answer
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

    # 답변 검증
    validation_result = validate_answer(query, response.content)

    # 검증 결과 출력 추가
    print("\n" + "="*60)
    print("답변 검증 결과")
    print("="*60)
    print(f"✓ 질문 유효성: {'통과' if validation_result['is_question_valid'] else '실패'}")
    print(f"  └─ 피드백: {validation_result['question_feedback']}")
    print(f"\n✓ 답변 점수: {validation_result['score']}/5.0 (기준: {validation_result['threshold']}점 이상)")
    print(f"  └─ 피드백: {validation_result['answer_feedback']}")
    print(f"\n✓ 최종 판정: {'✅ 통과' if validation_result['is_valid'] else '❌ 실패 (재검색 필요)'}")
    print("="*60 + "\n")

    if validation_result["is_valid"]:
        return response.content
    else:
        fallback_message = (
            "재검색 중입니다. 잠시만 기다려 주세요."
        )
        return fallback_message

