from vectordb.set_model import set_score_model
from initial_state import SelfRAGState
import json 
from langchain.prompts import PromptTemplate
from vectordb.search_query import search_question
from langgraph.graph import END

def evaluate_relevance(state: SelfRAGState,vectorstore)-> SelfRAGState:
    
    search_state ={"question":state.get("question"),
                    "domain":state.get("domain"),
                    "category":state.get("category")}
    search_queries = search_question(search_state, vectorstore)
    """검색된 문서의 관련성을 평가하는 함수"""
    retrieved_docs = [{
        "search_category": category,
        "content": doc.page_content,
        "metadata": doc.metadata
        } 
        for category, docs in search_queries.items()
        for (doc, _) in docs
    ] 

    final_message = state.get("final_anwser")
    relevant_docs = []
    relevance_scores = []
    avg_relevance = 0.0
    message = ""
    
    # 관련성 평가 프롬프트
    relevance_prompt = PromptTemplate.from_template(
        """
        #  **검색 문서 관련성 평가**

        당신은 **벡터DB 기반 검색 결과 평가 전문가**입니다.
        사용자의 질문과 문서 내용이 얼마나 관련이 높은지 **0~100점**으로 평가하세요.

        ## 평가 기준
        - **100점:** 질문의 핵심 답변을 직접 포함
        - **70~99점:** 매우 유사하거나 직접적인 관련
        - **50~69점:** 부분적으로 관련 있음
        - **0~49점:** 관련성 낮음 (무시)

        ## 출력 형식 (JSON)
        {{
            "evaluation_score": (0~100),
            "evaluation_detail": "간단한 이유 설명"
        }}

        ---
        # 질문:
        {question}

        # 문서 내용:
        {document}
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
            
            if json_result["evaluation_score"] >=50:  # 3점 이상만 관련 문서로 간주
                relevant_docs.append(doc)
                relevance_scores.append(json_result["evaluation_score"])
                
            elif json_result["evaluation_score"] < 50:
                message += json_result["evaluation_detail"] + "\n"
                continue
                
        except ValueError:
            print("점수 파싱 오류")
            continue

    if not relevant_docs:
        retrieval_question = True
        if state.get("max_token"):
            final_message ="죄송합니다. 조금 더 상세히 설명해주시면 도와드리도록 하겠습니다." 

    else:
        retrieval_question = False

    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
    
    print(f"{len(relevant_docs)}개의 관련 문서를 선별했습니다. (평균 관련성: {avg_relevance:.2f})")
    
    return {
        **state,
        "retrieval_question": retrieval_question,
        "retrieved_docs": relevant_docs,   # ✅ 여기 변경
        "relevance_scores": avg_relevance,
        "message":message,
        "final_answer": final_message
    }

    
def classify_retrieval(state: SelfRAGState)-> str:
    if state["retrieval_question"]:
        if state.get("max_token"):
            return END
        else:
            return "question_retrive"
    else:
        return "chat_llm"