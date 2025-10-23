from initial_state import SelfRAGState

def build_context(state: SelfRAGState) -> SelfRAGState:
    context_parts = []
    for doc in state.get("retrieved_docs"):
        context_parts.append(f"### {doc['search_category']}관련 문서 ###")
        metadata = doc.get("metadata", {})
        context_parts.append(f"- {doc['content'].strip()} (출처: {metadata.get("title")})")
    
    context =  "\n".join(context_parts)
    return {
        **state,
        "context":context
    
    }


def classify_agent(state: SelfRAGState) -> str:
    domain = state.get("domain")
    
    if domain == "기술지원":
        agent = "Tech" 
    elif domain == "고객지원":
        agent = "Customer"
    
    return agent
    
