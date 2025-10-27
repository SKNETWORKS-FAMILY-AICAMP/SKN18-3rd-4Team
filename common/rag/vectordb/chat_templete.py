import re

from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate

from ...langgraph.initial_state import SelfRAGState
from ...llm.models import set_llm_model

def find_image_for_title(image_field: str, title: str) -> list[str]:
    """
    image_url 필드에서 title 관련 이미지 URL 추출
    - | 또는 줄바꿈(\n)으로 구분된 여러 이미지 대응
    - title 일부만 포함돼도 매칭
    - 공백/대소문자 차이 무시
    """
    if not image_field or str(image_field).lower() in ["없음", "none", "null"]:
        return []

    urls = []
    norm_title = re.sub(r"\s+", "", title.lower())
    parts = re.split(r"[|\n]", str(image_field))
    for part in parts:
        norm_part = re.sub(r"\s+", "", part.lower())
        if norm_title and norm_title in norm_part:
            found = re.findall(r"https?://[^\s)]+", part)
            urls.extend(found)
    return urls

def chat_llm(state: SelfRAGState) -> SelfRAGState:
    """검색된 문서 기반으로 기술/고객지원 답변 생성"""
    print(f'{state.get("domain")} AI 챗봇 실행')
    question = state.get("question")

    context_parts = []
    for doc in state.get("retrieved_docs", []):
        metadata = doc.get("metadata", {})
        title = metadata.get("title", "제목 없음").strip()
        image_field = metadata.get("image_url", "")
        table_field = metadata.get("table_markdown", "")  
        content = doc.get("content", "").strip()
        category = doc.get("search_category", "일반")

        # ✅ 이미지 처리
        image_list = find_image_for_title(image_field, title)

        # ✅ 기본 본문 구성
        content_with_extras = content

        # ✅ 표(table_markdown) 처리
        if table_field and str(table_field).lower() not in ["없음", "none", "null"]:
            # 테이블 안에 제목 부분([1 제목]) 등 제거하고 깔끔히 정리
            cleaned_table = re.sub(r"\[\d+\s.*?\]", "", table_field).strip()
            content_with_extras += f"\n\n📊 **관련 표:**\n{cleaned_table}"

        # ✅ 이미지 처리 (본문 밑에 추가)
        if image_list:
            img_section = "\n".join(
                [f"[{i+1} {title}]({url})" for i, url in enumerate(image_list)]
            )
            content_with_extras += f"\n\n🖼 **관련 이미지:**\n{img_section}"

        context_parts.append(f"### 📘 {category} 관련 문서: {title}\n{content_with_extras}")

    context = "\n\n---\n\n".join(context_parts)
    history = state.get("conversation_history") or []
    history_lines = [
        f"{msg.get('role', 'user')}: {msg.get('content', '').strip()}"
        for msg in history
    ]
    history_text = "\n".join(history_lines) if history_lines else "이전 대화 없음"
    
    # ✅ 프롬프트 정의
    prompt_template = f"""
    # **AI 기술지원, 고객지원 답변 생성 요청**

    당신은 **기술지원, 고객지원 상담 AI**입니다.
    아래 문서들을 참고하여 사용자의 질문에 대한 **정확하고 구체적인 답변**을 작성하세요.

    ## 이전 대화 맥락
    - {history_text}

    ## 지시사항
    - 문서 내용을 바탕으로 논리적이고 구체적으로 설명합니다.
    - 사용자의 질문에 직접적인 답변을 제공합니다.
    - 문서의 출처(title)를 괄호 안에 명시합니다.
    - 표가 제공된 경우, 마크다운 형식을 그대로 유지하세요.
    - 이미지가 제공된 경우, `![제목](URL)` 형태로 작성해 바로 표시되도록 합니다.

    ---
    # **참고 문서들**
    {context}

    ---
    # **사용자 질문**
    {question}
    """

    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content=(
                "당신은 기술지원, 고객지원 상담 AI 챗봇입니다. "
                "고객의 불편사항 및 오류 사항에 대해 항상 논리적이고 정확하게 해결 방안을 제시합니다."
            )
        ),
        HumanMessagePromptTemplate.from_template(prompt_template),
    ])

    model = set_llm_model()
    chain = chat_prompt | model
    response = chain.invoke({"context": context, "question": question, "history_text": history_text})

    return {**state, "final_answer": response.content}
