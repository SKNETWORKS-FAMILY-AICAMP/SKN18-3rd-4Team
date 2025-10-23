from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vectordb.set_model import set_score_model
from initial_state import SelfRAGState

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
    
    # 관련성 평가 프롬프트
    relevance_prompt = ChatPromptTemplate.from_messages([
        ("system", 
        """
        당신은 문서가 사용자의 질문에 대한 관련성 정도를 평가하는 전문가입니다.
        
        다음 문서가 사용자의 질문과 얼마나 관련이 있는지를 1~5점으로 평가하세요.
        - 매우 관련있음: 5점
        - 관련있음: 4점  
        - 보통: 3점
        - 약간 관련있음: 2점
        - 관련없음: 1점

        점수만 숫자로 답변하세요 (1-5)."""),
        ("질문: {question}\n\n문서: {document}")
    ])
    
    llm = set_score_model()
    chain = relevance_prompt | llm | StrOutputParser()
    
    
    for doc in retrieved_docs:
        try:
            score_str = chain.invoke({
                "question": state.get("question"),
                "document": doc["content"]
            })
            score = float(score_str.strip())
            
            if score >= 3.0:  # 3점 이상만 관련 문서로 간주
                relevant_docs.append(doc)
                relevance_scores.append(score)
                
        except ValueError:
            print(f"점수 파싱 오류: {score_str}")
            continue
    if not relevant_docs:
        need_retrieval = True
    else:
        need_retrieval= False
    
    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
    
    print(f"{len(relevant_docs)}개의 관련 문서를 선별했습니다. (평균 관련성: {avg_relevance:.2f})")
    
    return {
        **state,
        "need_retrieval":need_retrieval,
        "relevant_docs":relevant_docs,
        "relevance_scores": avg_relevance
    }
    
def should_evaluate_relevance(state: SelfRAGState)-> str:
    """검색 필요성에 따라 다음 단계를 결정하는 조건부 함수"""
    if state["need_retrieval"]:
        return "unsupported_node"
    else:
        return "build_context"