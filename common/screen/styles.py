from __future__ import annotations

import streamlit as st


def inject_global_styles() -> None:
    custom_css = """
    <style>
    :root {
        --bg-gradient: linear-gradient(135deg, #101924 0%, #0b121d 45%, #05080f 100%);
        --chat-surface: rgba(16, 23, 34, 0.92);
        --sidebar-surface: rgba(10, 14, 20, 0.9);
        --border-soft: rgba(148, 163, 184, 0.18);
        --brand-accent: #4f8bff;
        --bubble-assistant: rgba(28, 36, 50, 0.88);
        --bubble-user: linear-gradient(135deg, #4f8bff, #7a5dff);
        --bubble-user-shadow: 0 18px 46px rgba(79, 139, 255, 0.32);
        --bubble-assistant-shadow: 0 20px 48px rgba(5, 9, 17, 0.35);
        --input-bg: rgba(12, 18, 27, 0.95);
        --text-primary: #f6f8fc;
        --text-secondary: rgba(214, 222, 235, 0.72);
    }
    html, body, .stApp {
        background: var(--bg-gradient);
        color: var(--text-primary);
    }
    .main .block-container {
        max-width: 960px;
        padding: 3rem 0 4rem;
    }
    .chat-frame {
        width: min(820px, 100%);
        margin: 0 auto;
        background: var(--chat-surface);
        border-radius: 26px;
        padding: 2.6rem 2.4rem 2rem;
        border: 1px solid rgba(80, 99, 128, 0.18);
        box-shadow: 0 32px 90px rgba(4, 7, 15, 0.55);
    }
    .chat-header {
        text-align: left;
        margin-bottom: 1.8rem;
    }
    .chat-title {
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.15;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    .chat-subtitle {
        font-size: 0.95rem;
        color: var(--text-secondary);
        margin: 0;
    }
    .chat-row {
        display: flex;
        align-items: flex-end;
        gap: 0.75rem;
        width: 100%;
    }
    .chat-row.assistant {
        justify-content: flex-start;
    }
    .chat-row.user {
        justify-content: flex-end;
    }
    .chat-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(79, 139, 255, 0.12);
        border: 1px solid rgba(79, 139, 255, 0.18);
        font-size: 1.7rem;
    }
    .chat-avatar.assistant {
        background: rgba(80, 99, 128, 0.25);
        border: 1px solid rgba(80, 99, 128, 0.3);
    }
    .chat-avatar.assistant img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 50%;
    }
    .chat-bubble {
        background: var(--bubble-assistant);
        border-radius: 20px;
        border: 1px solid rgba(80, 99, 128, 0.2);
        padding: 1rem 1.35rem;
        width: clamp(320px, 60vw, 640px);
        max-width: 100%;
        color: var(--text-primary);
        box-shadow: var(--bubble-assistant-shadow);
    }
    .chat-row.user .chat-bubble {
        background: var(--bubble-user);
        border: none;
        box-shadow: var(--bubble-user-shadow);
        color: #f8faff;
    }
    .chat-meta {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.78rem;
        opacity: 0.75;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
    }
    .chat-meta .timestamp {
        font-size: 0.72rem;
        opacity: 0.6;
    }
    .chat-row.user .chat-meta {
        justify-content: flex-end;
        text-align: right;
    }
    .chat-content {
        font-size: 0.99rem;
        line-height: 1.62;
        white-space: pre-wrap;
    }
    .chat-row.user .chat-content {
        text-align: right;
    }
    .chat-content p {
        margin: 0 0 0.4rem;
    }
    .chat-content ul,
    .chat-content ol {
        margin: 0 0 0.4rem 1.1rem;
    }
    .chat-content li {
        margin-bottom: 0.25rem;
    }
    .chat-content code {
        background: rgba(14, 21, 30, 0.6);
        border: 1px solid rgba(80, 99, 128, 0.3);
        padding: 0.2rem 0.4rem;
        border-radius: 6px;
    }
    .chat-content img {
        max-width: 100%;
        border-radius: 12px;
        border: 1px solid rgba(80, 99, 128, 0.25);
        margin-top: 0.5rem;
        box-shadow: 0 14px 30px rgba(8, 12, 20, 0.45);
    }
    .chat-row.status .chat-bubble {
        border-style: dashed;
        border-color: rgba(80, 99, 128, 0.4);
        background: rgba(28, 36, 50, 0.6);
        box-shadow: none;
        color: var(--text-secondary);
    }
    div[data-testid="stChatInput"] {
        background: var(--input-bg);
        border-radius: 14px;
        border: 1px solid rgba(80, 99, 128, 0.24);
        padding: 0.55rem 0.7rem;
        margin-top: 1.8rem;
        box-shadow: 0 26px 52px rgba(4, 7, 15, 0.5);
    }
    div[data-testid="stChatInput"] textarea {
        background: transparent;
        color: var(--text-primary);
        font-size: 0.98rem;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: rgba(214, 222, 235, 0.45);
    }
    div[data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #4f8bff, #7a5dff);
        border: none;
        color: #f9fbff;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.4rem 1.3rem;
        box-shadow: 0 16px 32px rgba(79, 139, 255, 0.35);
    }
    div[data-testid="stChatInput"] button:hover {
        box-shadow: 0 18px 38px rgba(79, 139, 255, 0.45);
    }
    [data-testid="stSidebar"] {
        background: var(--sidebar-surface);
        border-right: 1px solid rgba(80, 99, 128, 0.18);
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 1.9rem 1.6rem 2.2rem;
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        gap: 0;
    }
    [data-testid="stSidebar"] * {
        color: var(--text-secondary);
    }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: var(--text-primary);
    }
    .sidebar-brand {
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
        padding-bottom: 1.2rem;
        border-bottom: 1px solid rgba(80, 99, 128, 0.25);
    }
    .sidebar-brand-main {
        font-size: 1.65rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: 0.03em;
    }
    .sidebar-brand-sub {
        font-size: 1.12rem;
        color: rgba(214, 222, 235, 0.75);
        letter-spacing: 0.012em;
        line-height: 1.4;
    }
    .sidebar-section {
        margin-top: 1.45rem;
    }
    .sidebar-section .stRadio {
        margin-top: 0.75rem;
    }
    .sidebar-footer {
        margin-top: auto;
        padding-top: 1.6rem;
        border-top: 1px solid rgba(80, 99, 128, 0.25);
        font-size: 0.82rem;
        line-height: 1.6;
        color: rgba(214, 222, 235, 0.7);
    }
    .sidebar-run-card {
        background: rgba(16, 23, 32, 0.92);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        border: 1px solid rgba(80, 99, 128, 0.22);
        box-shadow: 0 24px 60px rgba(4, 7, 15, 0.45);
        margin-bottom: 1.1rem;
    }
    .sidebar-run-meta {
        font-size: 0.82rem;
        line-height: 1.55;
        color: rgba(214, 222, 235, 0.75);
    }
    .sidebar-step {
        margin-bottom: 0.8rem;
        border-radius: 14px;
        border: 1px solid rgba(80, 99, 128, 0.25);
        background: rgba(12, 17, 26, 0.92);
        padding: 0.75rem 0.85rem;
        box-shadow: 0 20px 45px rgba(4, 7, 15, 0.38);
    }
    .sidebar-step strong {
        color: var(--text-primary);
        display: block;
        margin-bottom: 0.35rem;
        font-size: 0.95rem;
    }
    .sidebar-step .step-duration {
        display: block;
        font-size: 0.78rem;
        color: rgba(214, 222, 235, 0.6);
        margin-bottom: 0.45rem;
    }
    .sidebar-step .io-label {
        font-size: 0.74rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: rgba(214, 222, 235, 0.5);
        margin-bottom: 0.25rem;
    }
    .sidebar-step .io-box {
        font-size: 0.84rem;
        line-height: 1.45;
        color: rgba(214, 222, 235, 0.75);
        background: rgba(18, 26, 38, 0.9);
        border-radius: 10px;
        border: 1px solid rgba(80, 99, 128, 0.26);
        padding: 0.55rem 0.65rem;
        margin-bottom: 0.35rem;
    }
    .sidebar-divider {
        height: 1px;
        width: 100%;
        background: rgba(80, 99, 128, 0.25);
        margin: 1.4rem 0;
    }
    .empty-hint {
        text-align: center;
        font-size: 0.9rem;
        color: rgba(214, 222, 235, 0.6);
        margin-top: 2.2rem;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
