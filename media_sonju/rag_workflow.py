from langgraph.graph import StateGraph, END
from vectordb.category_chain import decide_classify_category, should_question,unsupported_node
from vectordb.search_query import search_question
from vectordb.evaluate_chunks import evaluate_relevance,should_evaluate_relevance
from vectordb.chat_templete import build_context,classify_agent
from vectordb.multi_agent import customer_chat_llm,tech_chat_llm
from initial_state import SelfRAGState

def create_self_rag_workflow(vectorstore):
    """Self-RAG 워크플로우를 생성하는 함수"""
    
    # StateGraph 생성
    workflow = StateGraph(SelfRAGState)
   
    # search 노드: 래퍼 함수 사용 (partial 대신 안전)
    def search_node(state: SelfRAGState):
        return search_question(state, vectorstore=vectorstore)
    
    # 노드 추가
    workflow.add_node("classify", decide_classify_category)
    workflow.add_node("unsupported_node", unsupported_node)
    workflow.add_node("search", search_node)
    workflow.add_node("evaluate_relevance", evaluate_relevance)
    workflow.add_node("build_context",build_context)
    workflow.add_node("Tech",tech_chat_llm)
    workflow.add_node("Customer",customer_chat_llm)

    
    # 엣지 추가
    workflow.set_entry_point("classify") # 실행이 시작되는 노드 
    
    # 조건부 엣지1: 검색 필요성에 따라 분기
    workflow.add_conditional_edges(
        "classify",
        should_question,
        {
            "unsupported_node": "unsupported_node",
            "search": "search"
        }
    )
    # 조건부 엣지2: 검색 필요성에 따라 분기
    workflow.add_conditional_edges(
        "evaluate_relevance",
        should_evaluate_relevance,
        {
            "unsupported_node": "unsupported_node",
            "build_context": "build_context"
        }
    )
    # 조건부 엣지2: multi_agent에 따른 분기
    workflow.add_conditional_edges(
        "build_context",
        classify_agent,
        {
            "Tech": "Tech",
            "Customer": "Customer"
        }
    )
    
    # 검색/분류 경로
    workflow.add_edge("unsupported_node", "classify")
    
    
    # 공통 경로
    workflow.add_edge("search", "evaluate_relevance")
    workflow.add_edge("Tech", END)
    workflow.add_edge("Customer", END)

    
    # 워크플로우 컴파일
    app = workflow.compile()
    
    return app