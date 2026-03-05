"""
报告综合器节点
"""
import json
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from app.config import LLM_API_URL, LLM_API_KEY, LLM_MODEL_NAME
from app.agents.state import ResearchState


# 报告生成提示
REPORT_PROMPT_ZH = """你是一个学术研究报告撰写专家。请根据以下研究结果撰写一份结构化的研究报告。

研究主题：{topic}

研究过程：
{research_process}

关键发现：
{findings}

笔记记录：
{notes}

请生成一份完整的研究报告，包含以下部分：

1. 摘要（Executive Summary）
2. 研究背景
3. 主要发现（分类整理）
4. 对比分析（如有多个相关研究/方法）
5. 结论与建议
6. 参考来源

请使用 Markdown 格式输出。"""

REPORT_PROMPT_EN = """You are an academic research report writing expert. Please write a structured research report based on the following research results.

Research Topic: {topic}

Research Process:
{research_process}

Key Findings:
{findings}

Notes:
{notes}

Please generate a comprehensive research report with the following sections:

1. Executive Summary
2. Background
3. Key Findings (organized by category)
4. Comparative Analysis (if multiple related studies/methods)
5. Conclusions and Recommendations
6. References

Please output in Markdown format."""


BULLET_POINTS_PROMPT_ZH = """请根据以下研究发现，生成要点清单：

{findings}

要求：
- 每个要点简洁明了（1-2句话）
- 按重要性排序
- 生成5-10个要点
- 使用 Markdown 列表格式"""

BULLET_POINTS_PROMPT_EN = """Please generate a bullet point list based on the following research findings:

{findings}

Requirements:
- Each point should be concise (1-2 sentences)
- Sort by importance
- Generate 5-10 points
- Use Markdown list format"""


COMPARISON_TABLE_PROMPT_ZH = """请根据以下研究发现，生成对比表格：

{findings}

要求：
- 识别可以对比的维度（如方法、性能、优缺点等）
- 使用 Markdown 表格格式
- 至少包含3个对比维度
- 如果数据不适合表格，说明原因"""

COMPARISON_TABLE_PROMPT_EN = """Please generate a comparison table based on the following research findings:

{findings}

Requirements:
- Identify comparable dimensions (e.g., methods, performance, pros/cons)
- Use Markdown table format
- Include at least 3 comparison dimensions
- If the data is not suitable for a table, explain why"""


def get_report_prompt(language: str) -> str:
    return REPORT_PROMPT_ZH if language == "zh" else REPORT_PROMPT_EN


def get_bullet_points_prompt(language: str) -> str:
    return BULLET_POINTS_PROMPT_ZH if language == "zh" else BULLET_POINTS_PROMPT_EN


def get_comparison_table_prompt(language: str) -> str:
    return COMPARISON_TABLE_PROMPT_ZH if language == "zh" else COMPARISON_TABLE_PROMPT_EN


async def synthesizer_node(
    state: ResearchState
) -> AsyncGenerator[dict, None]:
    """
    综合器节点

    将所有研究结果综合成结构化报告

    Args:
        state: 当前研究状态

    Yields:
        事件字典
    """
    topic = state["topic"]
    language = state["language"]
    plan = state["plan"]
    search_records = state.get("search_records", [])
    findings = state.get("findings", [])
    notes = state.get("notes", [])

    # 发送进度事件
    yield {
        "type": "progress",
        "data": {
            "phase": "synthesis",
            "status": "started",
            "message": "正在生成研究报告..." if language == "zh" else "Generating research report..."
        }
    }

    try:
        # 初始化 LLM
        llm = ChatOpenAI(
            model=LLM_MODEL_NAME,
            api_key=LLM_API_KEY,
            base_url=LLM_API_URL,
            temperature=0.5  # 稍高的温度以获得更自然的报告
        )

        # 准备上下文
        research_process = "\n".join([
            f"- 步骤{i+1}: {step.get('action', '')} - {step.get('purpose', '')}"
            for i, step in enumerate(plan)
        ])

        findings_text = "\n".join([
            f"- [{f.get('relevance', 'medium')}] {f.get('content', '')} (来源: {f.get('source', '未知')})"
            for f in findings
        ]) or "暂无关键发现"

        notes_text = "\n".join(notes) if notes else "暂无笔记"

        # 生成主报告
        report_prompt = get_report_prompt(language).format(
            topic=topic,
            research_process=research_process,
            findings=findings_text,
            notes=notes_text
        )

        report_response = await llm.ainvoke([HumanMessage(content=report_prompt)])
        final_report = report_response.content

        yield {
            "type": "progress",
            "data": {
                "phase": "synthesis",
                "status": "report_generated",
                "message": "主报告已生成，正在生成要点清单..."
            }
        }

        # 生成要点清单
        bullet_prompt = get_bullet_points_prompt(language).format(findings=findings_text)
        bullet_response = await llm.ainvoke([HumanMessage(content=bullet_prompt)])
        bullet_points = bullet_response.content

        yield {
            "type": "progress",
            "data": {
                "phase": "synthesis",
                "status": "bullets_generated",
                "message": "要点清单已生成，正在生成对比表格..."
            }
        }

        # 生成对比表格
        comparison_prompt = get_comparison_table_prompt(language).format(findings=findings_text)
        comparison_response = await llm.ainvoke([HumanMessage(content=comparison_prompt)])
        comparison_table = comparison_response.content

        # 组合完整报告
        full_report = f"""# {topic}

## 研究报告

{final_report}

---

## 要点清单

{bullet_points}

---

## 对比分析

{comparison_table}

---

## 研究元数据

- 研究步骤数: {len(plan)}
- 搜索次数: {len(search_records)}
- 关键发现数: {len(findings)}
"""

        # 发送最终报告
        yield {
            "type": "report",
            "data": {
                "topic": topic,
                "report": full_report,
                "bullet_points": bullet_points,
                "comparison_table": comparison_table,
                "metadata": {
                    "total_steps": len(plan),
                    "search_count": len(search_records),
                    "findings_count": len(findings)
                }
            }
        }

        # 更新状态
        yield {
            "type": "state_update",
            "data": {
                "final_report": full_report,
                "bullet_points": bullet_points,
                "comparison_table": comparison_table,
                "is_complete": True
            }
        }

    except Exception as e:
        yield {
            "type": "error",
            "data": {
                "phase": "synthesis",
                "message": str(e)
            }
        }

        yield {
            "type": "state_update",
            "data": {
                "error": str(e),
                "is_complete": True
            }
        }
