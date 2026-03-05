"""
执行器节点 - ReAct 范式
"""
import json
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from app.config import LLM_API_URL, LLM_API_KEY, LLM_MODEL_NAME
from app.agents.state import ResearchState, Finding, SearchRecord
from app.mcp_tools.search_tool import search_tool
from app.mcp_tools.note_tool import note_tool


# ReAct 提示模板
REACT_PROMPT_ZH = """你是一个研究执行专家，使用 ReAct（思考-行动-观察）方法来执行研究步骤。

当前研究主题：{topic}
当前步骤：{current_step}
步骤详情：{step_detail}

之前的发现：
{previous_findings}

请分析当前情况并决定下一步行动。

请以 JSON 格式返回：
{{
    "thought": "你的思考过程",
    "action": "search" 或 "note",
    "action_input": {{
        // search: {{"query": "搜索查询"}}
        // note: {{"content": "笔记内容", "tags": ["标签"]}}
    }},
    "expected_info": "期望获取的信息"
}}

只返回 JSON，不要其他文字。"""

REACT_PROMPT_EN = """You are a research execution expert using the ReAct (Reason-Act-Observe) method to execute research steps.

Current research topic: {topic}
Current step: {current_step}
Step details: {step_detail}

Previous findings:
{previous_findings}

Please analyze the current situation and decide the next action.

Return in JSON format:
{{
    "thought": "Your reasoning process",
    "action": "search" or "note",
    "action_input": {{
        // search: {{"query": "search query"}}
        // note: {{"content": "note content", "tags": ["tags"]}}
    }},
    "expected_info": "expected information"
}}

Return only JSON, no other text."""


ANALYSIS_PROMPT_ZH = """请分析以下搜索结果，提取与研究主题 "{topic}" 相关的关键信息。

搜索结果：
{search_results}

请以 JSON 格式返回分析结果：
{{
    "key_findings": [
        {{
            "content": "关键发现内容",
            "source": "来源URL",
            "relevance": "high/medium/low"
        }}
    ],
    "summary": "搜索结果摘要",
    "note_content": "值得记录的笔记内容"
}}"""

ANALYSIS_PROMPT_EN = """Please analyze the following search results and extract key information related to the research topic "{topic}".

Search results:
{search_results}

Please return the analysis in JSON format:
{{
    "key_findings": [
        {{
            "content": "key finding content",
            "source": "source URL",
            "relevance": "high/medium/low"
        }}
    ],
    "summary": "summary of search results",
    "note_content": "notable content to record"
}}"""


def get_react_prompt(language: str) -> str:
    return REACT_PROMPT_ZH if language == "zh" else REACT_PROMPT_EN


def get_analysis_prompt(language: str) -> str:
    return ANALYSIS_PROMPT_ZH if language == "zh" else ANALYSIS_PROMPT_EN


async def executor_node(
    state: ResearchState
) -> AsyncGenerator[dict, None]:
    """
    执行器节点

    使用 ReAct 范式执行当前研究步骤

    Args:
        state: 当前研究状态

    Yields:
        事件字典
    """
    topic = state["topic"]
    language = state["language"]
    plan = state["plan"]
    current_index = state["current_step_index"]
    previous_findings = state.get("findings", [])

    if current_index >= len(plan):
        yield {
            "type": "state_update",
            "data": {"is_complete": True}
        }
        return

    current_step = plan[current_index]
    step_num = current_index + 1
    total_steps = len(plan)

    # 发送进度事件
    yield {
        "type": "progress",
        "data": {
            "phase": "execution",
            "status": "started",
            "step": step_num,
            "total_steps": total_steps,
            "message": f"正在执行步骤 {step_num}/{total_steps}: {current_step.get('action', '')}"
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

        # 准备上下文
        findings_text = "\n".join([
            f"- {f.get('content', '')} (来源: {f.get('source', '未知')})"
            for f in previous_findings[-5:]  # 最近5个发现
        ]) or "暂无之前的发现"

        # 决定行动
        react_prompt = get_react_prompt(language).format(
            topic=topic,
            current_step=step_num,
            step_detail=json.dumps(current_step, ensure_ascii=False),
            previous_findings=findings_text
        )

        response = await llm.ainvoke([HumanMessage(content=react_prompt)])
        content = response.content

        # 解析决策
        try:
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            decision = json.loads(content.strip())
        except json.JSONDecodeError:
            # 默认执行搜索
            decision = {
                "thought": "执行搜索获取信息",
                "action": "search",
                "action_input": {"query": current_step.get("query", topic)},
                "expected_info": "相关信息"
            }

        action = decision.get("action", "search")
        action_input = decision.get("action_input", {})

        # 执行行动
        if action == "search":
            # 执行搜索
            query = action_input.get("query", current_step.get("query", topic))

            yield {
                "type": "progress",
                "data": {
                    "phase": "searching",
                    "query": query,
                    "message": f"正在搜索: {query}"
                }
            }

            results = await search_tool.execute(query=query, max_results=5)

            # 记录搜索
            search_record = SearchRecord(
                query=query,
                results=[r.to_dict() for r in results],
                timestamp=__import__('datetime').datetime.now().isoformat()
            )

            yield {
                "type": "search_result",
                "data": {
                    "query": query,
                    "results": [r.to_dict() for r in results],
                    "count": len(results)
                }
            }

            # 分析搜索结果
            results_text = "\n".join([
                f"标题: {r.title}\n内容: {r.content}\n来源: {r.url}\n"
                for r in results
            ])

            analysis_prompt = get_analysis_prompt(language).format(
                topic=topic,
                search_results=results_text
            )

            analysis_response = await llm.ainvoke([HumanMessage(content=analysis_prompt)])

            try:
                analysis_content = analysis_response.content
                if "```" in analysis_content:
                    analysis_content = analysis_content.split("```")[1]
                    if analysis_content.startswith("json"):
                        analysis_content = analysis_content[4:]
                analysis = json.loads(analysis_content.strip())
            except json.JSONDecodeError:
                analysis = {
                    "key_findings": [],
                    "summary": "分析失败",
                    "note_content": ""
                }

            # 保存笔记
            if analysis.get("note_content"):
                note = await note_tool.execute(
                    content=analysis["note_content"],
                    tags=[topic, f"step_{step_num}"],
                    source=f"search:{query}"
                )

                yield {
                    "type": "note",
                    "data": {
                        "id": note.id,
                        "content": note.content[:200] + "..." if len(note.content) > 200 else note.content,
                        "tags": note.tags
                    }
                }

            # 更新状态
            new_findings = [
                Finding(**f) for f in analysis.get("key_findings", [])
            ]

            yield {
                "type": "state_update",
                "data": {
                    "current_step_index": current_index + 1,
                    "search_records": [search_record],
                    "findings": new_findings,
                    "notes": [note.id] if analysis.get("note_content") else []
                }
            }

        elif action == "note":
            # 直接记录笔记
            content = action_input.get("content", "")
            tags = action_input.get("tags", [topic])

            if content:
                note = await note_tool.execute(
                    content=content,
                    tags=tags,
                    source="executor"
                )

                yield {
                    "type": "note",
                    "data": {
                        "id": note.id,
                        "content": note.content[:200] + "..." if len(note.content) > 200 else note.content,
                        "tags": note.tags
                    }
                }

            yield {
                "type": "state_update",
                "data": {
                    "current_step_index": current_index + 1,
                    "notes": [note.id] if content else []
                }
            }

        else:
            # 未知行动，继续下一步
            yield {
                "type": "state_update",
                "data": {
                    "current_step_index": current_index + 1
                }
            }

    except Exception as e:
        yield {
            "type": "error",
            "data": {
                "phase": "execution",
                "step": step_num,
                "message": str(e)
            }
        }

        # 即使出错也继续下一步
        yield {
            "type": "state_update",
            "data": {
                "current_step_index": current_index + 1,
                "error": str(e)
            }
        }
