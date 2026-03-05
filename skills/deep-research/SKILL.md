---
name: deep-research
version: 1.0.0
description: 学术文献深度研究助手
author: Research Team
triggers:
  - "/research"
  - "研究"
tools:
  - search
  - note-taking
output_format:
  - structured_report
  - bullet_points
  - comparison_table
  - bilingual
---

# 深度研究技能

## 功能描述

自动执行学术文献研究全流程，基于 ReAct + Plan-and-Solve 混合范式。

## 使用方式

### 触发命令
- `/research <主题>`
- 直接输入包含"研究"关键词的问题

### 参数配置
| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| max_steps | int | 5 | 最大研究步骤数 |
| language | str | zh | 输出语言 (zh/en) |
| search_depth | str | advanced | 搜索深度 |

## 工作流程

```
┌─────────────┐
│   输入主题   │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  规划阶段    │────▶│ Plan-and-Solve│
│  Planner    │     │ 分解研究步骤  │
└──────┬──────┘     └──────────────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  执行阶段    │────▶│    ReAct     │
│  Executor   │     │ 思考-行动-观察│
└──────┬──────┘     └──────────────┘
       │                   │
       │    ┌──────────────┘
       │    │
       ▼    ▼
┌─────────────┐     ┌──────────────┐
│  搜索工具    │     │   笔记工具    │
│ Tavily API  │     │  本地持久化   │
└─────────────┘     └──────────────┘
       │
       ▼
┌─────────────┐
│  综合阶段    │
│ Synthesizer │
│ 生成报告    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   输出报告   │
│ • 结构化报告 │
│ • 要点清单   │
│ • 对比表格   │
│ • 双语输出   │
└─────────────┘
```

## 输出格式

### 1. 结构化研究报告
- 摘要（Executive Summary）
- 研究背景
- 主要发现（分类整理）
- 对比分析
- 结论与建议
- 参考来源

### 2. 要点清单
- 5-10个核心要点
- 按重要性排序
- 简洁明了（1-2句话）

### 3. 对比表格
- 识别对比维度
- Markdown表格格式
- 至少3个对比维度

### 4. 双语支持
- 中文报告（language=zh）
- 英文报告（language=en）

## 示例用法

```bash
# 中文研究
/research 大语言模型在医疗诊断中的应用

# 英文研究
/research Applications of Large Language Models in Medical Diagnosis

# 指定深度
/research --max_steps=8 量子计算的最新进展
```

## 技术实现

### 后端
- **框架**: FastAPI
- **智能体**: LangGraph
- **LLM**: Kimi-K2
- **搜索**: Tavily API

### 前端
- **框架**: Vue 3 + TypeScript
- **构建**: Vite
- **样式**: Scoped CSS

### 部署
- 前后端分离
- SSE 流式通信
- 支持 CORS

## 注意事项

1. **API 配置**: 需要配置 LLM_API_KEY 和 TAVILY_API_KEY
2. **网络要求**: 需要稳定的网络连接访问 Tavily API
3. **执行时间**: 完整研究流程可能需要 1-3 分钟
4. **笔记存储**: 笔记保存在本地 notes/ 目录

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 网络超时 | 自动重试3次 |
| API限制 | 等待后重试 |
| 解析失败 | 使用默认计划 |
| 搜索无结果 | 调整查询继续 |

## 更新日志

### v1.0.0 (2024-01)
- 初始版本
- 实现 ReAct + Plan-and-Solve 混合范式
- 支持 SSE 流式输出
- 双语报告生成
