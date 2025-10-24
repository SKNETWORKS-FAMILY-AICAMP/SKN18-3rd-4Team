"""
Memory 기능 테스트를 위한 연속 대화 RAG 시스템

이 파일은 대화 이력을 누적하고 Memory 요약 기능을 테스트하기 위해 작성되었습니다.
- 연속 대화 루프로 여러 질문 처리
- 대화 이력 누적 및 전달
- 메시지 개수 추적 (5개 초과 시 요약 작동)
"""

from dotenv import load_dotenv
from vectordb.connect_db import connect_DB
from vectordb.pgvector import create_pgvector_store
from vectordb.set_model import set_embedding_model
from rag_workflow import create_self_rag_workflow
from run_rag import run_self_rag


def print_header():
    """테스트 헤더 출력"""
    print("\n" + "="*60)
    print("🧪 Memory 기능 테스트 - 연속 대화 RAG 시스템")
    print("="*60)
    print("💡 5개 이상의 메시지가 누적되면 자동으로 요약됩니다.")
    print("💡 종료하려면 'quit', 'exit', '종료' 중 하나를 입력하세요.")
    print("="*60 + "\n")


def print_message_count(conversation_history):
    """현재 메시지 개수 및 요약 상태 출력"""
    msg_count = len(conversation_history)
    print(f"\n📊 [현재 대화 이력: {msg_count}개 메시지]", end="")

    if msg_count > 5:
        print(f" → 🔄 요약 모드 작동 중 (최근 5개 유지, 나머지 요약됨)")
    elif msg_count >= 3:
        print(f" → ⚠️  요약 임박 ({5 - msg_count}개 더 누적 시 요약)")
    else:
        print(f" → ✅ 요약 미작동 ({5 - msg_count}개 더 필요)")
    print()


def main():
    """Memory 기능 테스트 메인 함수"""

    # 초기화
    load_dotenv()
    db = connect_DB()
    embeddings = set_embedding_model()
    vectorstore = create_pgvector_store(db, embeddings)
    self_rag_app = create_self_rag_workflow(vectorstore)

    # 대화 이력 초기화
    conversation_history = []

    print_header()

    # 연속 대화 루프
    question_number = 1
    while True:
        # 메시지 카운트 표시
        print_message_count(conversation_history)

        # 사용자 질문 입력
        question = input(f"[질문 #{question_number}] 궁금한 점을 질문하세요: ").strip()

        # 종료 명령어 체크
        if question.lower() in ["quit", "exit", "종료", "q"]:
            print("\n👋 대화를 종료합니다. 감사합니다!")
            break

        # 빈 질문 건너뛰기
        if not question:
            print("⚠️  질문을 입력해주세요.\n")
            continue

        print("\n" + "-"*60)

        # Self-RAG 실행 (대화 이력 전달)
        try:
            result = run_self_rag(
                self_rag_app,
                question,
                conversation_history=conversation_history,
                verbose=True
            )

            # 대화 이력 업데이트 (result에서 반환된 이력 사용)
            conversation_history = result.get("conversation_history", conversation_history)

            question_number += 1

        except KeyboardInterrupt:
            print("\n\n⚠️  중단되었습니다.")
            break
        except Exception as e:
            print(f"\n❌ 오류 발생: {str(e)}")
            print("계속 진행합니다...\n")

        print("-"*60 + "\n")

    # 최종 통계 출력
    print("\n" + "="*60)
    print(f"📈 최종 통계")
    print("="*60)
    print(f"총 질문 개수: {question_number - 1}개")
    print(f"최종 대화 이력: {len(conversation_history)}개 메시지")
    if len(conversation_history) > 10:
        print(f"요약 작동 횟수: {(len(conversation_history) - 10) // 2 + 1}회 예상")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
