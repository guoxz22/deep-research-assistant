"""
LangGraph 状态图 - 研究流程编排
"""
from typing import AsyncGenerator

from langgraph.graph import StateGraph, END

from app.agents.state import ResearchState, create_initial_state
from app.agents.planner import planner_node
from app.agents.executor import executor_node
from app.agents.synthesizer import synthesizer_node


def should_continue(state: ResearchState) -> str:
    """
    条件边：判断是否继续执行

    Args:
        state: 当前状态

    Returns:
        下一个节点名称
    """
    if state.get("is_complete", False):
        return "synthesizer"

    if state.get("error") and "planning" in str(state.get("error", "")).lower():
        return END

    current_index = state.get("current_step_index", 0)
    plan = state.get("plan", [])

    if current_index >= len(plan):
        return "synthesizer"

    return "executor"


async def run_research(
    topic: str,
    max_steps: int = 5,
    language: str = "zh"
) -> AsyncGenerator[dict, None]:
    """
    运行完整研究流程

    Args:
        topic: 研究主题
        max_steps: 最大步骤数
        language: 输出语言

    Yields:
        事件字典
    """
    # 初始化状态
    state = create_initial_state(
        topic=topic,
        language=language,
        max_steps=max_steps
    )

    # 构建状态图
    # 注意：由于 LangGraph 的异步特性，我们手动编排流程
    # 而不是使用 StateGraph.compile()

    # Phase 1: 规划
    async for event in planner_node(state):
        yield event

        # 更新状态
        if event.get("type") == "state_update":
            for key, value in event["data"].items():
                if key == "messages":
                    state["messages"] = state.get("messages", []) + value
                elif key == "plan":
                    state["plan"] = value
                elif key == "current_step_index":
                    state["current_step_index"] = value

    # 检查规划是否成功
    if not state.get("plan"):
        yield {
            "type": "error",
            "data": {
                "phase": "planning",
                "message": "规划失败，无法生成研究计划"
            }
        }
        return

    # Phase 2: 执行
    while not state.get("is_complete", False):
        current_index = state.get("current_step_index", 0)
        plan = state.get("plan", [])

        if current_index >= len(plan):
            break

        async for event in executor_node(state):
            yield event

            # 更新状态
            if event.get("type") == "state_update":
                for key, value in event["data"].items():
                    if key == "current_step_index":
                        state["current_step_index"] = value
                    elif key == "search_records":
                        state["search_records"] = state.get("search_records", []) + value
                    elif key == "findings":
                        state["findings"] = state.get("findings", []) + value
                    elif key == "notes":
                        state["notes"] = state.get("notes", []) + value
                    elif key == "error":
                        state["error"] = value

    # Phase 3: 综合
    async for event in synthesizer_node(state):
        yield event


def build_research_graph() -> StateGraph:
    """
    构建 LangGraph 状态图

    Returns:
        编译后的状态图
    """
    # 创建状态图
    graph = StateGraph(ResearchState)

    # 添加节点
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("synthesizer", synthesizer_node)

    # 设置入口点
    graph.set_entry_point("planner")

    # 添加边
    graph.add_edge("planner", "executor")
    graph.add_conditional_edges(
        "executor",
        should_continue,
        {
            "executor": "executor",
            "synthesizer": "synthesizer"
        }
    )
    graph.add_edge("synthesizer", END)

    return graph


# 预编译的图（用于可视化）
research_graph = build_research_graph()
