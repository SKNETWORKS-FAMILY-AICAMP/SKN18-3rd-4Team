from typing import List, Dict, Any, TypedDict, Tuple


class SelfRAGState(TypedDict):
    """Self-RAG 시스템의 상태를 정의하는 클래스"""
    
    # 입력 정보
    question: str  # 사용자 질문
    
    # 검색 관련
    need_quit: bool  # 검색 필요 여부
    domain: str # 고객지원/기술지원 multi agent 분류
    category: List[str]  # 세부 카테고리
    max_token:bool
    
    # 답변 생성 관련
    retrieval_question:bool
    search_queries: Dict[str, List[Tuple[Any, float]]] # RAG 결과
    retrieved_docs: List[Dict[str, Any]] # 검증이후 query
    context: str # LLM Templete에 들어갈 문장 구성
    #chunk_metadata: Dict[str,List[Dict[str]]]

    # 평가 관련
    relevance_score: float  # 관련성 점수
    message:str
    
    # 최종 결과
    
    final_answer: str  # 최종 답변 (출처 포함)


print("SelfRAGState 클래스 정의 완료!")