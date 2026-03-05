"""
研究状态定义
"""
from typing import List, Optional, TypedDict, Annotated
from operator import add

from langchain_core.messages import BaseMessage


class SearchRecord(TypedDict):
    """搜索记录"""
    query: str
    results: List[dict]
    timestamp: str


class Finding(TypedDict):
    """关键发现"""
    content: str
    source: str
    relevance: str  # high, medium, low


class ResearchState(TypedDict):
    """
    研究状态

    跟踪整个研究流程的状态
    """
    # 输入
    topic: str                       # 研究主题
    language: str                    # 输出语言 (zh/en)
    max_steps: int                   # 最大研究步骤数

    # 规划
    plan: List[str]                  # 研究计划步骤列表
    current_step_index: int          # 当前执行步骤索引

    # 执行
    search_records: Annotated[List[SearchRecord], add]  # 搜索记录（累积）
    notes: Annotated[List[str], add]                    # 笔记ID列表（累积）
    findings: Annotated[List[Finding], add]             # 关键发现（累积）

    # 输出
    final_report: Optional[str]      # 最终报告（Markdown格式）
    bullet_points: Optional[str]     # 要点清单
    comparison_table: Optional[str]  # 对比表格

    # 对话历史
    messages: Annotated[List[BaseMessage], add]  # 消息历史（累积）

    # 控制流
    is_complete: bool                # 是否完成
    error: Optional[str]             # 错误信息


def create_initial_state(
    topic: str,
    language: str = "zh",
    max_steps: int = 5
) -> ResearchState:
    """
    创建初始研究状态

    Args:
        topic: 研究主题
        language: 输出语言
        max_steps: 最大步骤数

    Returns:
        初始化的研究状态
    """
    return ResearchState(
        topic=topic,
        language=language,
        max_steps=max_steps,
        plan=[],
        current_step_index=0,
        search_records=[],
        notes=[],
        findings=[],
        final_report=None,
        bullet_points=None,
        comparison_table=None,
        messages=[],
        is_complete=False,
        error=None
    )
