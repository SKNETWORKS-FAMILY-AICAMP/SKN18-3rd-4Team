from vectordb.category_chain import classify_category


def search_question(vectorstore, query):
    response_categories = classify_category(query)
    all_results = {}
    
    if response_categories:
        print(f"{response_categories} 유사도 검색 시작")
        for cat in response_categories:
            search_categories = [cat, "공통"]
            print(f"{cat} 유사도 검색 시작")
            results = vectorstore.similarity_search_with_filter_score(query=query, 
                                    k=3, categories=search_categories) # Cosine 유사도 기반으로 계산-> 높을 수록 좋음
            all_results[cat] = results
            #print_from(all_results)
    else:
        print("전체에서 유사도 검색 시작")
        results = vectorstore.similarity_search_with_score(query, 3) # Cosine 유사도 기반으로 계산-> 높을 수록 좋음
        all_results["전체"] = results
        #print_from(results)
    return all_results
    

def print_from(results):
    # mean_score = sum(score for (_, score) in results) / 3
    for i, (doc, score) in enumerate(results, start=1):
        print(f"Rank {i}")
        print(f"Similarity: {score:.3f}")  # 소수점 3자리로 
        print(f"ID: {doc.metadata.get('id')}, Table: {doc.metadata.get('table')}, Category: {doc.metadata.get('category')}")
        print(f"Content: {doc.page_content}") 
