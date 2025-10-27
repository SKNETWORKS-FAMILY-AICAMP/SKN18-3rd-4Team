import streamlit as st
from ..service.self_rag import init_self_rag, ask_self_rag


@st.cache_resource
def get_self_rag_app():
    return init_self_rag()


def sendLang(message: str, history=None) -> str:
    get_self_rag_app()  # 캐시 초기화 보장
    return ask_self_rag(message, history=history, verbose=False)
