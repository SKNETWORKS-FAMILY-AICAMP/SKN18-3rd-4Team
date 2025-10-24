from rag_workflow import create_self_rag_workflow
from vectordb.set_model import set_embedding_model
from dotenv import load_dotenv

# 편리한 실행 함수
def run_self_rag(self_rag_app, question: str, conversation_history=None, verbose: bool = True):
    """Self-RAG 시스템을 실행하는 메인 함수"""
    
    print(f"질문: {question}")
    print("=" * 50)

    # 대화 이력이 없으면 빈 리스트
    if conversation_history is None:
        conversation_history = []
    
    # 초기 상태 설정
    initial_state = {
        "question": question,
        "need_quit": False,
        "retrieval_question":False,
        "domain": "",
        "category":[],
        "message":"",
        "search_queries": {},
        "retrieved_docs":[],
        "relevance_scores":0.0,
        "context":"",
        "final_answer":"",
        "chunk_metadata": {},
        "max_token":False,
        "end_error_message":""
    }
    
    # Self-RAG 워크플로우 실행
    try:
        result = self_rag_app.invoke(initial_state)
        
        if verbose:
            print("\n=== Self-RAG 실행 결과 ===")
        
        print(result["final_answer"])
        
        return result
        
    except Exception as e:
        error_message = f"Self-RAG 실행 중 오류가 발생했습니다: {str(e)}"
        print(error_message)
        return {"final_answer": "죄송하지만 시스템 오류로 인해 답변을 제공할 수 없습니다."}





