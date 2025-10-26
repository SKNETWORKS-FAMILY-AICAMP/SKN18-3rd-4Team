from __future__ import annotations

import html
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

try:
    from langsmith import Client
except ImportError:  # pragma: no cover
    Client = None  # type: ignore

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None  # type: ignore


LOCAL_TZ = ZoneInfo("Asia/Seoul") if ZoneInfo else None


@dataclass
class LangSmithStep:
    name: str
    run_type: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    inputs: Any
    outputs: Any


@dataclass
class LangSmithRun:
    id: str
    name: str
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    tags: List[str]
    run_type: str
    steps: List[LangSmithStep]


def get_langsmith_client() -> Tuple[Optional[Any], Optional[str], Optional[str]]:
    if Client is None:
        return None, None, "langsmith 패키지가 설치되어 있지 않습니다. `pip install langsmith`로 추가해 주세요."

    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        return None, None, "LANGCHAIN_API_KEY 환경 변수가 설정되어 있지 않습니다."

    project = os.getenv("LANGCHAIN_PROJECT")
    if not project:
        return None, None, "LANGCHAIN_PROJECT 환경 변수가 설정되어 있지 않습니다."

    endpoint = os.getenv("LANGCHAIN_ENDPOINT")
    client_kwargs: Dict[str, Any] = {"api_key": api_key}
    if endpoint:
        client_kwargs["api_url"] = endpoint

    try:
        return Client(**client_kwargs), project, None
    except Exception as exc:  # pragma: no cover
        return None, None, str(exc)


def ensure_datetime_awareness(ts: datetime) -> datetime:
    if getattr(ts, "tzinfo", None) is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts


def format_timestamp(ts: Optional[datetime]) -> str:
    if not ts:
        return "-"
    aware_ts = ensure_datetime_awareness(ts)
    if LOCAL_TZ:
        aware_ts = aware_ts.astimezone(LOCAL_TZ)
    return aware_ts.strftime("%m월 %d일 %H:%M:%S")


def format_duration(start: Optional[datetime], end: Optional[datetime]) -> str:
    if not start or not end:
        return "-"
    start_aware = ensure_datetime_awareness(start)
    end_aware = ensure_datetime_awareness(end)
    delta = end_aware - start_aware
    total = delta.total_seconds()
    if total < 1:
        return f"{total * 1000:.0f}ms"
    return f"{total:.1f}s"


def summarize_payload(payload: Any, max_chars: int = 600) -> str:
    if payload is None:
        return "-"
    if isinstance(payload, (str, int, float, bool)):
        text = str(payload)
    else:
        try:
            text = json.dumps(payload, ensure_ascii=False, indent=2)
        except TypeError:
            text = str(payload)
    if len(text) > max_chars:
        text = text[: max_chars - 3] + "..."
    return html.escape(text).replace("\n", "<br>")


def fetch_langsmith_runs(limit: int = 3, step_limit: int = 10) -> Tuple[List[LangSmithRun], Optional[str]]:
    client, project, error = get_langsmith_client()
    if error:
        return [], error
    assert client is not None and project is not None

    try:
        runs_iter = client.list_runs(
            project_name=project,
            limit=limit,
            order="desc",
        )
        runs: List[LangSmithRun] = []
        for raw_run in runs_iter:
            run_id = str(getattr(raw_run, "id", ""))
            steps_iter = client.list_runs(
                project_name=project,
                parent_run_id=run_id,
                limit=step_limit,
                order="asc",
            )
            steps: List[LangSmithStep] = []
            for step in steps_iter:
                steps.append(
                    LangSmithStep(
                        name=getattr(step, "name", getattr(step, "run_type", "Step")),
                        run_type=getattr(step, "run_type", ""),
                        start_time=getattr(step, "start_time", None),
                        end_time=getattr(step, "end_time", None),
                        inputs=getattr(step, "inputs", None),
                        outputs=getattr(step, "outputs", None),
                    )
                )
            runs.append(
                LangSmithRun(
                    id=run_id,
                    name=getattr(raw_run, "name", None) or getattr(raw_run, "run_type", "Run"),
                    status=getattr(raw_run, "state", None) or getattr(raw_run, "status", "unknown"),
                    start_time=getattr(raw_run, "start_time", None),
                    end_time=getattr(raw_run, "end_time", None),
                    tags=list(getattr(raw_run, "tags", []) or []),
                    run_type=getattr(raw_run, "run_type", ""),
                    steps=steps,
                )
            )
        return runs, None
    except Exception as exc:  # pragma: no cover
        return [], str(exc)
