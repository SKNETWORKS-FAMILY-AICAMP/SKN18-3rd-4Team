from datetime import datetime
from pathlib import Path
from typing import Optional
import base64
import html
import mimetypes

import streamlit as st
from dotenv import load_dotenv

try:
    from markdown import markdown as md_to_html
except ImportError:  # pragma: no cover
    md_to_html = None

from commons.screen.lang import sendLang
from commons.screen.langsmith_view import fetch_langsmith_runs, format_duration, format_timestamp, summarize_payload
from commons.screen.styles import inject_global_styles

# 페이지 기본 설정
st.set_page_config(
    page_title="Self-RAG 챗봇",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 커스텀 스타일 적용
inject_global_styles()
load_dotenv()

# 세션 스테이트 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "langsmith_selected_run" not in st.session_state:
    st.session_state.langsmith_selected_run = None

BOT_DISPLAY_NAME = "SKmall AI Chatbot"
USER_DISPLAY_NAME = "사용자"
BOT_AVATAR_PATH = str(Path(__file__).parent / "image" / "skmagicaibot.png")
USER_AVATAR = "🧑‍💼"


def _load_avatar_data_uri(path: str) -> Optional[str]:
    file_path = Path(path)
    if not file_path.exists():
        return None
    data = file_path.read_bytes()
    mime, _ = mimetypes.guess_type(str(file_path))
    if not mime:
        mime = "image/png"
    encoded = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


BOT_AVATAR_DATA_URI = _load_avatar_data_uri(BOT_AVATAR_PATH)


try:
    from html import escape as _escape
except ImportError:  # pragma: no cover
    def _escape(val: str) -> str:
        return val


def _simple_markdown_to_html(text: str) -> str:
    """Fallback 마크다운 파서 (이미지/링크/줄바꿈만 지원)."""
    import re

    def replace_image(match: re.Match) -> str:
        alt = _escape(match.group(1))
        src = _escape(match.group(2))
        return f'<img src="{src}" alt="{alt}" />'

    def replace_link(match: re.Match) -> str:
        label = _escape(match.group(1))
        href = _escape(match.group(2))
        return f'<a href="{href}" target="_blank" rel="noopener">{label}</a>'

    html_text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_image, text)
    html_text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, html_text)
    paragraphs = [seg.strip() for seg in html_text.split("\n\n") if seg.strip()]
    if not paragraphs:
        return ""
    return "".join(f"<p>{seg.replace(chr(10), '<br>')}</p>" for seg in paragraphs)


def render_message(container, role: str, content: str, timestamp: str, *, status: bool = False) -> None:
    display_name = BOT_DISPLAY_NAME if role == "assistant" else USER_DISPLAY_NAME
    display_name = _escape(display_name)
    timestamp_html = _escape(timestamp)
    if content is None:
        content = ""
    if md_to_html is not None:
        content_html = md_to_html(content)
    else:
        content_html = _simple_markdown_to_html(content)

    bubble_classes = "chat-row " + role + (" status" if status else "")

    if role == "assistant":
        if BOT_AVATAR_DATA_URI:
            avatar_html = f"<div class='chat-avatar assistant'><img src=\"{BOT_AVATAR_DATA_URI}\" alt='assistant avatar' /></div>"
        else:
            avatar_html = "<div class='chat-avatar assistant'>🤖</div>"
        html_block = f"""
        <div class="{bubble_classes}">
            {avatar_html}
            <div class="chat-bubble">
                <div class="chat-meta">
                    <span class="name">{display_name}</span>
                    <span class="timestamp">{timestamp_html}</span>
                </div>
                <div class="chat-content">{content_html}</div>
            </div>
        </div>
        """
    else:
        avatar_html = f"<div class='chat-avatar user'>{_escape(USER_AVATAR)}</div>"
        html_block = f"""
        <div class="{bubble_classes}">
            <div class="chat-bubble">
                <div class="chat-meta">
                    <span class="name">{display_name}</span>
                    <span class="timestamp">{timestamp_html}</span>
                </div>
                <div class="chat-content">{content_html}</div>
            </div>
            {avatar_html}
        </div>
        """

    container.markdown(html_block, unsafe_allow_html=True)


# 사이드바 네비게이션
with st.sidebar:
    st.markdown("### 메뉴")
    nav_choice = st.radio(
        "화면 선택",
        options=["💬 Chat", "📊 LangGraph 트레이스"],
        index=0,
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption(
        "LangGraph 트레이스에서는 LangSmith에 기록된 실행 내역과 단계별 Input/Output을 확인할 수 있습니다."
    )

if nav_choice == "💬 Chat":
    st.markdown(
        "<style>div[data-testid='stChatInput']{display:flex !important;}</style>",
        unsafe_allow_html=True,
    )
    chat_shell = st.container()
    with chat_shell:
        st.markdown(
            """
            <div class="chat-frame">
                <div class="chat-header">
                    <div class="chat-title">어떤 도움이 필요하신가요?</div>
                    <p class="chat-subtitle">
                        SKmall 고객지원 문서를 LangGraph Self-RAG 파이프라인으로 분석해 가장 알맞은 해결책을 제안해 드립니다.
                    </p>
                </div>
            """,
            unsafe_allow_html=True,
        )

        chat_history_container = st.container()
        for message in st.session_state.messages:
            role = message.get("role", "assistant")
            timestamp = message.get("timestamp") or datetime.now().strftime("%H:%M")
            render_message(
                chat_history_container,
                role,
                message.get("content", ""),
                timestamp,
            )

        chat_shell.markdown("</div>", unsafe_allow_html=True)

    if prompt := st.chat_input("무엇을 도와드릴까요?"):
        timestamp = datetime.now().strftime("%H:%M")
        render_message(
            chat_history_container,
            "user",
            prompt,
            timestamp,
        )

        st.session_state.messages.append(
            {"role": "user", "content": prompt, "timestamp": timestamp}
        )

        history_copy = st.session_state.messages.copy()

        status_timestamp = datetime.now().strftime("%H:%M")
        status_placeholder = chat_history_container.empty()
        render_message(
            status_placeholder,
            "assistant",
            "🔍 LangGraph 워크플로우가 문서를 검색하고 답변을 준비하고 있습니다...",
            status_timestamp,
            status=True,
        )

        error_response: Optional[str] = None
        try:
            answer = sendLang(prompt, history=history_copy)
        except Exception as exc:  # pragma: no cover
            error_response = (
                "시스템 오류로 인해 답변을 생성하지 못했습니다. 잠시 후 다시 시도해 주세요."
            )
            answer = ""
            print(f"Self-RAG 실행 중 오류: {exc}")
        finally:
            status_placeholder.empty()

        answer_timestamp = datetime.now().strftime("%H:%M")
        render_message(
            chat_history_container,
            "assistant",
            error_response or answer,
            answer_timestamp,
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_response or answer,
                "timestamp": answer_timestamp,
            }
        )
else:
    st.markdown(
        "<style>div[data-testid='stChatInput']{display:none !important;}</style>",
        unsafe_allow_html=True,
    )
    st.title("LangGraph 트레이스")
    langsmith_runs, langsmith_error = fetch_langsmith_runs(limit=6, step_limit=20)

    if langsmith_error:
        st.warning(f"LangSmith 데이터를 불러오지 못했습니다: {langsmith_error}")
    elif not langsmith_runs:
        st.info("최근 실행된 LangGraph 트레이스가 없습니다. 채팅에서 질문을 해보세요.")
    else:
        st.markdown("#### 최근 실행 워크플로우")
        for run in langsmith_runs:
            tags = ", ".join(run.tags)
            st.markdown(
                f"""
                <div class="sidebar-run-card">
                    <h4>{run.name}</h4>
                    <div class="sidebar-run-meta">
                        <div>상태 · {run.status}</div>
                        <div>시작 · {format_timestamp(run.start_time)}</div>
                        <div>소요 · {format_duration(run.start_time, run.end_time)}</div>
                        {"<div>태그 · " + tags + "</div>" if tags else ""}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if run.steps:
                st.markdown("##### 실행 단계")
                for step in run.steps:
                    st.markdown(
                        f"""
                        <div class="sidebar-step">
                            <strong>{step.name}</strong>
                            <span class="step-duration">
                                타입 · {step.run_type} · 소요 {format_duration(step.start_time, step.end_time)}
                            </span>
                            <div class="io-label">Input</div>
                            <div class="io-box">{summarize_payload(step.inputs, max_chars=600)}</div>
                            <div class="io-label">Output</div>
                            <div class="io-box">{summarize_payload(step.outputs, max_chars=600)}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
