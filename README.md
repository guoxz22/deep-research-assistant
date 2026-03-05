# 🔍 深度研究助手

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.4+-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)](https://fastapi.tiangolo.com/)

基于 LangChain/LangGraph 的学术文献深度研究智能体应用。输入研究主题，AI 将自动规划研究步骤、搜索学术文献、记录关键发现，并生成结构化双语研究报告。

## ✨ 特性

- 🤖 **ReAct + Plan-and-Solve 混合范式** - 智能规划与执行
- 🔍 **Tavily 搜索集成** - 高质量学术文献搜索
- 📝 **自动笔记记录** - 持久化研究笔记
- 📊 **结构化报告** - 完整研究报告 + 要点清单 + 对比表格
- 🌐 **双语支持** - 中文/英文报告输出
- ⚡ **SSE 流式输出** - 实时研究进度展示

## 🖼️ 截图

> 研究界面展示（可添加实际截图）

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- LLM API 密钥（支持 OpenAI 兼容接口）
- Tavily API 密钥

### 1. 克隆项目

```bash
git clone https://github.com/your-username/deep-research-assistant.git
cd deep-research-assistant
```

### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install
```

### 4. 启动服务

**终端 1 - 启动后端：**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**终端 2 - 启动前端：**
```bash
cd frontend
npm run dev
```

### 5. 访问应用

打开浏览器访问 http://localhost:5173

## ⚙️ 配置说明

编辑 `backend/.env` 文件：

```env
# LLM 配置（支持 OpenAI 兼容接口）
LLM_API_URL=https://api.openai.com/v1
LLM_API_KEY=your_api_key
LLM_MODEL_NAME=gpt-4

# Tavily 搜索配置
TAVILY_API_KEY=your_tavily_api_key

# 服务器配置（可选）
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

| 环境变量 | 说明 | 必填 |
|----------|------|------|
| LLM_API_URL | LLM API 地址 | 是 |
| LLM_API_KEY | LLM API 密钥 | 是 |
| LLM_MODEL_NAME | 模型名称 | 是 |
| TAVILY_API_KEY | Tavily API 密钥 | 是 |

> 💡 获取 Tavily API 密钥：https://tavily.com

## 📁 项目结构

```
deep-research-assistant/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # API 入口
│   │   ├── config.py       # 配置管理
│   │   ├── routers/        # API 路由
│   │   ├── agents/         # LangGraph 智能体
│   │   │   ├── planner.py  # 规划器
│   │   │   ├── executor.py # 执行器
│   │   │   └── synthesizer.py # 综合器
│   │   └── mcp_tools/      # MCP 工具
│   ├── requirements.txt
│   └── .env.example
├── frontend/               # Vue3 前端
│   ├── src/
│   │   ├── components/    # Vue 组件
│   │   ├── services/      # API 服务
│   │   └── App.vue
│   └── package.json
├── skills/                 # Anthropic Skills
└── notes/                  # 研究笔记存储
```

## 🔌 API 文档

### POST /research/stream

启动研究流程，返回 SSE 流式响应。

**请求体：**
```json
{
  "topic": "大语言模型在医疗诊断中的应用",
  "max_steps": 5,
  "language": "zh"
}
```

**SSE 事件类型：**

| 事件 | 说明 |
|------|------|
| `plan` | 研究计划生成 |
| `progress` | 执行进度更新 |
| `search_result` | 搜索结果 |
| `note` | 笔记记录 |
| `report` | 最终报告 |
| `done` | 完成信号 |
| `error` | 错误信息 |

### POST /research/sync

同步研究接口，返回完整结果。

## 🏗️ 架构设计

### ReAct + Plan-and-Solve 混合范式

```
┌─────────────────────────────────────┐
│         用户输入研究主题              │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│   Planner (Plan-and-Solve)          │
│   分解研究问题为具体步骤              │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│   Executor (ReAct Loop)             │
│   思考 → 行动 → 观察 循环执行         │
│   • Search Tool (Tavily)            │
│   • Note Tool (本地持久化)           │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│   Synthesizer                       │
│   生成结构化研究报告                  │
└─────────────────────────────────────┘
```

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| AI 框架 | LangChain, LangGraph |
| 搜索服务 | Tavily API |
| 前端框架 | Vue 3 + TypeScript |
| 构建工具 | Vite |
| Markdown | Marked + Highlight.js |

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证。

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Tavily](https://tavily.com)
- [Vue.js](https://vuejs.org)
- [FastAPI](https://fastapi.tiangolo.com)
