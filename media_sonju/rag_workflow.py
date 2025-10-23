from langgraph.graph import StateGraph, END
from vectordb.category_chain import decide_classify_category,classify_quit
from vectordb.search_query import search_question
from vectordb.evaluate_chunks import evaluate_relevance,classify_retrieval
from vectordb.chat_templete import chat_llm
from vectordb.retrive import question_retrive
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
    workflow.add_node("search", search_node)
    workflow.add_node("evaluate_relevance", evaluate_relevance)
    workflow.add_node("question_retrive",question_retrive)
    workflow.add_node("chat_llm",chat_llm)

    # 엣지 추가
    workflow.set_entry_point("classify") # 실행이 시작되는 노드 
    # 검색/분류 경로
    workflow.add_conditional_edges(
        "classify",
        classify_quit,
        {
            END: END,
            "search": "search"})
    
    # 조건부엣지
    workflow.add_conditional_edges(
        "evaluate_relevance",
        classify_retrieval,
        {
            "question_retrive":"question_retrive",
            "chat_llm":"chat_llm"
                
        }
    )
    
    
    # 공통 경로
    workflow.add_edge("question_retrive","classify")
    workflow.add_edge("search", "evaluate_relevance")
    workflow.add_edge("chat_llm",  END)

    
    # 워크플로우 컴파일
    app = workflow.compile()
    
    return app