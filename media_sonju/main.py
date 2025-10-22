from vectordb.connect_db import connect_DB
from vectordb.split_chunk import make_chunk
from vectordb.set_model import set_embedding_model
from vectordb.pgvector import create_pgvector_store, add_documents_to_pgvector
from dotenv import load_dotenv
from vectordb.search_query import search_question
from vectordb.chat import build_context, chat_llm
from vectordb.evaluate_chunks import evaluate_relevance
from langchain_core.messages import HumanMessage, AIMessage

def create_faq_vectordb(db, vectorstore):
    chunks = make_chunk(db)
    add_documents_to_pgvector(vectorstore, chunks)


def search(vectorstore):
    """
    메모리 기능이 추가된 대화형 검색 함수
    여러 번의 질문-답변을 이어서 할 수 있습니다.
    """
    # 대화 이력 초기화
    chat_history = []

    print("SK매직 고객 상담 챗봇입니다. 질문을 입력하세요. (종료는 'quit' 입력)")
    print("-" * 60)

    while True:
        query = input(f"\n질문을 입력해주세요.: ")

        # 종료 명령어 확인
        if query.lower() == 'quit':
            print("상담을 종료합니다. 감사합니다!")
            break
        
        # 질문 검색
        all_results = search_question(vectorstore, query)
        if not all_results:
            print("관련된 FAQ를 찾을 수 없습니다. 다른 질문을 시도해보세요.")
            continue

        # 관련성 평가 및 컨텍스트 구성
        contexts = evaluate_relevance(all_results, query)
        context = build_context(contexts)

        # AI 응답 생성 (대화 이력 포함)
        print("\nAI: ", end="")
        response_content = chat_llm(context, query, chat_history)

        # 대화 이력에 추가
        chat_history.append(HumanMessage(content=query))
        chat_history.append(AIMessage(content=response_content))

        print("\n" + "-" * 60)


if __name__ == "__main__":
    load_dotenv()
    db = connect_DB()
    embeddings = set_embedding_model()
    vectorstore = create_pgvector_store(db, embeddings)
    #create_faq_vectordb(db, vectorstore) #<- 처음 한번 실행
    search(vectorstore)


