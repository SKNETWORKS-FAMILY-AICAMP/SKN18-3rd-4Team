from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vectordb.set_model import set_score_model

def evaluate_relevance(all_results:dict,query:str):
    """검색된 문서의 관련성을 평가하는 함수"""
    domain = all_results.get("도메인")
    results = all_results.get("results")
    retrieved_docs = [{
        "category": category,
        "content": doc.page_content,
        "metadata": doc.metadata
        } 
        for category, docs in results.items()
        for (doc, _) in docs
    ] 


    relevant_docs = []
    relevance_scores = []
    
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
                "question": query,
                "document": doc["content"]
            })
            score = float(score_str.strip())
            
            if score >= 3.0:  # 3점 이상만 관련 문서로 간주
                relevant_docs.append(doc)
                relevance_scores.append(score)
                
        except ValueError:
            print(f"점수 파싱 오류: {score_str}")
            continue
    
    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
    
    print(f"{len(relevant_docs)}개의 관련 문서를 선별했습니다. (평균 관련성: {avg_relevance:.2f})")
    
    return {"domain": domain ,"content":relevant_docs}