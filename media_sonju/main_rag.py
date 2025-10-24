from media_sonju.service import init_self_rag, ask_self_rag


def main():
    init_self_rag()
    question = input("궁금한 점을 질문하세요: ")
    answer = ask_self_rag(question, verbose=True)
    print(answer)


if __name__ == "__main__":
    main()
