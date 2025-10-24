from vectordb.set_model import set_score_model
from initial_state import SelfRAGState
import json 
from langchain.prompts import PromptTemplate

def evaluate_relevance(state: SelfRAGState)-> SelfRAGState:
    """검색된 문서의 관련성을 평가하는 함수"""
    search_queries = state.get("search_queries")
    retrieved_docs = [{
        "search_category": category,
        "content": doc.page_content,
        "metadata": doc.metadata
        } 
        for category, docs in search_queries.items()
        for (doc, _) in docs
    ] 


    relevant_docs = []
    relevance_scores = []
    avg_relevance = 0.0
    message = ""
    
    # 관련성 평가 프롬프트
    relevance_prompt = PromptTemplate.from_template(
        """
        당신은 최고의 평가자입니다.
        사용자의 질문에 대한 답변이 벡터DB의 데이터와 얼마나 일치하는지 평가해주세요.
        평가 기준:
        - 100점: 질문과 문서의 주제/키워드가 정확히 일치
        - 80~90점: 매우 관련성 높음, 직접적인 답변 가능
        - 60~70점: 어느 정도 관련 있지만 불완전
        - 50점 이하: 관련성 낮음, 다른 주제
        {{
        "evaluation_score": 0~100 사이의 숫자,
        "evaluation_detail": "답변이 벡터DB의 데이터와 얼마나 일치하는지 설명"
        }}

        사용자의 질문: {question}
        벡터DB의 데이터: {document}
        """
    )
    
    llm = set_score_model()
    chain = relevance_prompt | llm
    
    
    for doc in retrieved_docs:
        try:
            result = chain.invoke({
                "question": state.get("question"),
                "document": doc["content"]
            })
            json_result = json.loads(result.content)

            if json_result["evaluation_score"] >= 70:  # 70점 이상만 관련 문서로 간주
                relevant_docs.append(doc)
                relevance_scores.append(json_result["evaluation_score"])
                
            elif json_result["evaluation_score"] < 70:
                message += json_result["evaluation_detail"] + "\n"
                continue
                
        except ValueError:
            print(f"점수 파싱 오류: {json_result["evaluation_score"]}")
            continue
    if not relevant_docs:
        retrieval_question = True
        max_token = state.get("max_token", False)  # 증가하지 않고 현재 상태 유지

    else:
        retrieval_question= False
        max_token = state.get("max_token", False)  # 현재 상태 유지

    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
    
    print(f"{len(relevant_docs)}개의 관련 문서를 선별했습니다. (평균 관련성: {avg_relevance:.2f})")
    
    return {
        **state,
        "max_token": max_token,
        "retrieval_question":retrieval_question,
        "retrieved_docs":relevant_docs,  # 수정: relevant_docs → retrieved_docs (chat_llm과 키 일치)
        "relevance_scores": avg_relevance,
        "message":message
    }
    
def classify_retrieval(state: SelfRAGState)-> str:
    """검색 필요성에 따라 다음 단계를 결정하는 조건부 함수"""
    if state["retrieval_question"]:
        return "question_retrive"
    else:
        return "chat_llm"