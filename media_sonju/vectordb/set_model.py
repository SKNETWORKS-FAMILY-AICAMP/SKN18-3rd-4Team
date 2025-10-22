from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from .utils import set_openapi
# from dotenv import load_dotenv

def set_embedding_model():
    embedding_model = OpenAIEmbeddings(
        model = "text-embedding-3-large",    # OpenAI 제공하는 모델명 
        openai_api_key = set_openapi()                                                        
    )
    return embedding_model
# 분류 모델
def set_classify_model():
    classify_model = ChatOpenAI(
        model = "gpt-4o-mini",    # OpenAI 제공하는 모델명 
        openai_api_key = set_openapi(),
        temperature=0
    )
    return classify_model

# 답변 모델
def set_llm_model():
    chat_model = ChatOpenAI(
        model = "gpt-5-nano",    # OpenAI 제공하는 모델명 
        openai_api_key = set_openapi(),
        reasoning_effort="high"
    )
    return chat_model

# 평가 모델
def set_score_model():
    chat_model = ChatOpenAI(
        model = "gpt-5-nano",    # OpenAI 제공하는 모델명 
        openai_api_key = set_openapi(),
        frequency_penalty=0
        
    )
    return chat_model