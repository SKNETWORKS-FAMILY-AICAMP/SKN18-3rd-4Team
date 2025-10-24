from langgraph.graph import StateGraph, END
from media_sonju.vectordb.category_chain import (
    decide_classify_category,
    classify_quit,
)
from media_sonju.vectordb.evaluate_chunks import (
    evaluate_relevance,
    classify_retrieval,
)
from media_sonju.vectordb.chat_templete import chat_llm
from media_sonju.vectordb.retrive import question_retrive
from media_sonju.initial_state import SelfRAGState

def create_self_rag_workflow(vectorstore):
    """Self-RAG 워크플로우를 생성하는 함수"""
    
    # StateGraph 생성
    workflow = StateGraph(SelfRAGState)

    # search 노드: 래퍼 함수 사용 (partial 대신 안전)
    def evaluate_relevance_node(state: SelfRAGState):
        return evaluate_relevance(state, vectorstore=vectorstore)
    
    # 노드 추가
    workflow.add_node("classify", decide_classify_category)
    workflow.add_node("evaluate_relevance", evaluate_relevance_node)
    workflow.add_node("question_retrive",question_retrive)
    workflow.add_node("chat_llm",chat_llm)

    # 엣지 시작
    workflow.set_entry_point("classify") # 실행이 시작되는 노드 
    
    # 검색/분류 경로
    workflow.add_conditional_edges(
        "classify",
        classify_quit,
        {
            END : END,
            "evaluate_relevance":"evaluate_relevance"
                
        }
    )
    
    workflow.add_conditional_edges(
        "evaluate_relevance",
        classify_retrieval,
        {
            END : END,
            "question_retrive":"question_retrive",
            "chat_llm":"chat_llm"
                
        }
    )
    workflow.add_conditional_edges(
        "chat_llm",
        classify_retrieval,
        {
            END : END,
            "chat_llm":"classify"
        }
    )
    
    # 공통 경로
    workflow.add_edge("question_retrive","classify")

    # 워크플로우 컴파일
    app = workflow.compile()
    
    return app
