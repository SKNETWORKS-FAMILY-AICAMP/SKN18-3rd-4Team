import streamlit as st
from lang import sendLang  # front/lang.py에서 정의한 함수

# 페이지 기본 설정
st.set_page_config(page_title="Self-RAG 챗봇", page_icon="💬")

# 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Self-RAG 챗봇")

# 기존 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("말씀해주세요."):
    # 사용자 메시지를 먼저 UI와 세션 상태에 반영
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 지금까지 대화 이력을 복사해 전달 (필요하면 최근 n개만 취해서 넘겨도 됨)
    history = st.session_state.messages.copy()

    # RAG 파이프라인 호출
    answer = sendLang(prompt, history=history)

    # 모델 응답 표시 및 저장
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
