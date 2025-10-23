from initial_state import SelfRAGState

def search_question(state:SelfRAGState,vectorstore) -> SelfRAGState:
    
    domain = state.get("domain")
    categories = state.get("category")
    query = state.get("question")  
    all_results = {}  
    if categories:
        for cat in categories:
                print(f"{cat} 유사도 검색 시작")
                results = vectorstore.similarity_search_with_filter_score(query=query, 
                                        k=5, categories=cat) # Cosine 유사도 기반으로 계산-> 높을 수록 좋음
                #print(results)
                all_results[cat] = results
                print_from(results)
    else:
        if domain == "고객지원":
            results = vectorstore.similarity_search_with_filter_score(query=query, 
                                        k=5, categories=["계약관련", "관리서비스", "구독/멤버십제도", "요금납부","제휴카드"]) # Cosine 유사도 기반으로 계산-> 높을 수록 좋음
            all_results["공통"] = results
            print_from(results)
        elif domain=="기술지원":
            print("전체에서 유사도 검색 시작")
            results = vectorstore.similarity_search_with_score(query, 5) # Cosine 유사도 기반으로 계산-> 높을 수록 좋음
            all_results["공통"] = results
            print_from(results)
                
        
    return {
        **state,
        "search_queries" : all_results
    }
    

def print_from(results):
    # mean_score = sum(score for (_, score) in results) / 3
    for i, (doc, score) in enumerate(results, start=1):
        #print(f"Rank {i}")
        print(f"Similarity: {score:.3f}")  # 소수점 3자리로 
        print(f"ID: {doc.metadata.get('id')}, Category: {doc.metadata.get('category')}, Title: {doc.metadata.get('title')}")
        #print(f"Content: {doc.page_content}") 
