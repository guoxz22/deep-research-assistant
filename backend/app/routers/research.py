"""
研究 API 路由 - SSE 流式响应
"""
import json
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agents.graph import run_research

router = APIRouter()


class ResearchRequest(BaseModel):
    """研究请求模型"""
    topic: str
    max_steps: int = 5
    language: str = "zh"  # zh 或 en


def format_sse_event(event_type: str, data: dict) -> str:
    """格式化 SSE 事件"""
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def research_stream_generator(
    topic: str,
    max_steps: int,
    language: str
) -> AsyncGenerator[str, None]:
    """
    生成研究流程的 SSE 流

    事件类型:
    - plan: 研究计划生成
    - progress: 执行进度更新
    - search_result: 搜索结果
    - note: 笔记记录
    - report: 最终报告
    - done: 完成信号
    - error: 错误信息
    """
    try:
        async for event in run_research(topic, max_steps, language):
            event_type = event.get("type", "progress")
            data = event.get("data", {})
            yield format_sse_event(event_type, data)

        # 发送完成信号
        yield format_sse_event("done", {"message": "研究完成"})

    except Exception as e:
        yield format_sse_event("error", {"message": str(e)})


@router.post("/stream")
async def stream_research(request: ResearchRequest):
    """
    启动研究流程并返回 SSE 流

    返回 SSE 事件流，包含研究全过程的实时更新
    """
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="研究主题不能为空")

    return StreamingResponse(
        research_stream_generator(
            topic=request.topic,
            max_steps=request.max_steps,
            language=request.language
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/sync")
async def sync_research(request: ResearchRequest):
    """
    同步研究接口 - 返回完整结果

    适用于不需要实时更新的场景
    """
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="研究主题不能为空")

    results = []
    async for event in run_research(request.topic, request.max_steps, request.language):
        results.append(event)

    # 提取最终报告
    final_report = None
    for event in reversed(results):
        if event.get("type") == "report":
            final_report = event.get("data")
            break

    return {
        "topic": request.topic,
        "events": results,
        "final_report": final_report
    }
