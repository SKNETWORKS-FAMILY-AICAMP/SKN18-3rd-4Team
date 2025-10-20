from vetordb.category_chain import classify_category


def search_question(vectorstore, query):
    response_category = classify_category(query)
    filters = {"category": response_category}
    
    print(f"이 질문은 {response_category}에 관한 질문입니다.")
    
    if response_category != "기타":
        print("유사도 검색 시작")
        results = vectorstore.similarity_search_with_filter_score(query, 3,filters) # Cosine 유사도 기반으로 계산-> 높을 수록 좋음
    else:
        print("유사도 전체 검색 시작")
        results = vectorstore.similarity_search_with_score(query, 3) # Cosine 유사도 기반으로 계산-> 높을 수록 좋음
        
    
    for i, (doc, score) in enumerate(results, start=1):
        print(f"Rank {i}")
        print(f"Similarity: {score:.3f}")  # 소수점 3자리로 
        print(f"ID: {doc.metadata.get('id')}, Table: {doc.metadata.get('table')}, Category: {doc.metadata.get('category')}")
        print(f"Content: {doc.page_content}") 
        print("="*80)