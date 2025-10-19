from langchain_openai import OpenAIEmbeddings
import os
# from dotenv import load_dotenv

def set_openapi():
    #load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    return api_key
    
    
# embedding 모델 설정
def set_embedding_model():
    embedding_model = OpenAIEmbeddings(
        model = "text-embedding-3-small",    # OpenAI 제공하는 모델명 
        openai_api_key = set_openapi()
    )
    return embedding_model
