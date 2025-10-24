from typing import List, Dict, Any, TypedDict, Tuple


class SelfRAGState(TypedDict):
    """Self-RAG 시스템의 상태를 정의하는 클래스"""
    
    # 입력 정보
    question: str  # 사용자 질문
    
    # 검색 관련
    need_quit: bool  # 검색 필요 여부
    domain: str # 고객지원/기술지원 multi agent 분류
    category: List[str]  # 세부 카테고리
    
    # 답변 생성 관련
    retrieval_question:bool  # 재질문 필요 여부 (True: DB에서 관련 문서 없음)
    search_queries: Dict[str, List[Tuple[Any, float]]]  # 벡터DB 검색 결과 (카테고리별 문서 + 유사도 점수)
    retrieved_docs: List[Dict[str, Any]]  # 관련성 평가 후 선별된 문서 (70점 이상, evaluate_relevance에서 설정)
    context: str  # LLM Templete에 들어갈 문장 구성 

    # 평가 관련
    relevance_score: float  # 관련성 점수
    message:str
    max_token: bool  # 토큰 초과 여부

    # 최종 결과
    final_answer: str  # 최종 답변 (출처 포함)

    # 대화 이력 (추가)
    conversation_history: List[Any]  # 이전 대화 메시지 리스트


print("SelfRAGState 클래스 정의 완료!")