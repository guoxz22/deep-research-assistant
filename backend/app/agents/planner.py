"""
规划器节点 - Plan-and-Solve 范式
"""
import json
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from app.config import LLM_API_URL, LLM_API_KEY, LLM_MODEL_NAME
from app.agents.state import ResearchState


# 规划提示模板
PLANNER_PROMPT_ZH = """你是一个学术研究规划专家。用户想要深入研究以下主题：

主题：{topic}

请制定一个系统的研究计划，包含 {max_steps} 个具体步骤。每个步骤应该：
1. 明确要搜索的内容
2. 说明该步骤的目的
3. 指出预期的信息类型

请以 JSON 数组格式返回计划，每个元素包含：
- step: 步骤编号
- action: 行动描述
- query: 建议的搜索查询
- purpose: 该步骤的目的

只返回 JSON 数组，不要包含其他文字。"""

PLANNER_PROMPT_EN = """You are an academic research planning expert. The user wants to conduct in-depth research on the following topic:

Topic: {topic}

Please create a systematic research plan with {max_steps} specific steps. Each step should:
1. Clearly define what to search for
2. Explain the purpose of the step
3. Indicate the expected type of information

Please return the plan as a JSON array, where each element contains:
- step: step number
- action: action description
- query: suggested search query
- purpose: purpose of this step

Return only the JSON array, no other text."""


def get_planner_prompt(language: str) -> str:
    """获取对应语言的规划提示"""
    return PLANNER_PROMPT_ZH if language == "zh" else PLANNER_PROMPT_EN


async def planner_node(
    state: ResearchState
) -> AsyncGenerator[dict, None]:
    """
    规划器节点

    将研究主题分解为具体步骤

    Args:
        state: 当前研究状态

    Yields:
        事件字典，包含类型和数据
    """
    topic = state["topic"]
    language = state["language"]
    max_steps = state["max_steps"]

    # 发送开始事件
    yield {
        "type": "progress",
        "data": {
            "phase": "planning",
            "status": "started",
            "message": "正在制定研究计划..." if language == "zh" else "Creating research plan..."
        }
    }

    try:
        # 初始化 LLM
        llm = ChatOpenAI(
            model=LLM_MODEL_NAME,
            api_key=LLM_API_KEY,
            base_url=LLM_API_URL,
            temperature=0.3
        )

        # 生成计划
        prompt = get_planner_prompt(language).format(
            topic=topic,
            max_steps=max_steps
        )

        response = await llm.ainvoke([HumanMessage(content=prompt)])
        content = response.content

        # 解析计划
        # 尝试提取 JSON
        try:
            # 清理可能的 markdown 代码块
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            plan_steps = json.loads(content.strip())
        except json.JSONDecodeError:
            # 如果解析失败，创建默认计划
            plan_steps = [
                {
                    "step": 1,
                    "action": f"搜索 {topic} 的基础信息",
                    "query": topic,
                    "purpose": "获取主题概述"
                },
                {
                    "step": 2,
                    "action": f"搜索 {topic} 的最新研究进展",
                    "query": f"{topic} 最新研究",
                    "purpose": "了解前沿动态"
                },
                {
                    "step": 3,
                    "action": f"搜索 {topic} 的应用案例",
                    "query": f"{topic} 应用案例",
                    "purpose": "收集实际应用"
                }
            ]

        # 发送计划事件
        yield {
            "type": "plan",
            "data": {
                "steps": plan_steps,
                "total_steps": len(plan_steps)
            }
        }

        # 更新状态（不发送messages到前端，避免序列化问题）
        new_messages = state.get("messages", []) + [
            HumanMessage(content=prompt),
            AIMessage(content=str(plan_steps))
        ]
        state["messages"] = new_messages

        yield {
            "type": "state_update",
            "data": {
                "plan": plan_steps,
                "current_step_index": 0
            }
        }

    except Exception as e:
        yield {
            "type": "error",
            "data": {
                "phase": "planning",
                "message": str(e)
            }
        }
