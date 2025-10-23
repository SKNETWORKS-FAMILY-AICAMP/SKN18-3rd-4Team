import os
from dotenv import load_dotenv

def set_openapi():
#    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    return api_key

