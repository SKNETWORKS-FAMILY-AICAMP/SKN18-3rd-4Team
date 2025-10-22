from vectordb.category_chain import classify_category

def search_question(vectorstore, query):
    classified = classify_category(query)  # LLM 기반 세부 카테고리
    
    # 범위 외 질문 처리
    if classified.get("status") == "NOT_SUPPORTED":
        print(classified["message"])
        return ""
    elif classified.get("status") == "SUPPORTED":
        domain = classified.get("도메인")
        categories = classified.get("세부카테고리")
        all_results = {}
        all_results = {"도메인": domain, "results": {}}
        if categories:
            for cat in categories:
                search_categories = [cat, "공통"]
                print(f"{cat} 유사도 검색 시작")
                results = vectorstore.similarity_search_with_filter_score(query=query, 
                                        k=5, categories=search_categories) # Cosine 유사도 기반으로 계산-> 높을 수록 좋음
                all_results["results"][cat] = results
                print_from(results)
        else:
            print("전체에서 유사도 검색 시작")
            results = vectorstore.similarity_search_with_score(query, 5) # Cosine 유사도 기반으로 계산-> 높을 수록 좋음
            all_results["results"]["전체"] = results
            print_from(results)
        
    return all_results
    

def print_from(results):
    # mean_score = sum(score for (_, score) in results) / 3
    for i, (doc, score) in enumerate(results, start=1):
        print(f"Rank {i}")
        print(f"Similarity: {score:.3f}")  # 소수점 3자리로 
        print(f"ID: {doc.metadata.get('id')}, Table: {doc.metadata.get('DB_table')}, Category: {doc.metadata.get('category')}")
        print(f"Content: {doc.page_content}") 
