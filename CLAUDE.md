# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Deep Research Assistant is an academic literature research agent built on LangChain/LangGraph. It uses a hybrid ReAct + Plan-and-Solve paradigm to automatically plan research steps, search academic literature via Tavily, record key findings, and generate structured bilingual research reports.

## Development Commands

### Backend (FastAPI)

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with LLM_API_KEY and TAVILY_API_KEY

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Vue 3 + TypeScript + Vite)

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Architecture

### Backend Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI entry point, CORS config
│   ├── config.py        # Environment variables (LLM_API_URL, LLM_API_KEY, TAVILY_API_KEY)
│   ├── routers/
│   │   └── research.py  # API endpoints: POST /research/stream, POST /research/sync
│   ├── agents/
│   │   ├── state.py     # ResearchState TypedDict - tracks entire research flow
│   │   ├── graph.py     # LangGraph orchestration, run_research() async generator
│   │   ├── planner.py   # Plan-and-Solve: decomposes topic into research steps
│   │   ├── executor.py  # ReAct: thinks, acts (search/note), observes per step
│   │   └── synthesizer.py # Generates final report, bullet points, comparison table
│   └── mcp_tools/
│       ├── search_tool.py  # Tavily search wrapper, MCP-compatible
│       └── note_tool.py    # Note persistence to notes/ directory, MCP-compatible
```

### Frontend Structure

```
frontend/
├── src/
│   ├── App.vue               # Main app layout
│   ├── main.ts               # Vue app entry
│   ├── components/
│   │   ├── ResearchModal.vue   # Research input form
│   │   ├── ResearchProgress.vue # Real-time progress display
│   │   └── MarkdownViewer.vue  # Markdown report rendering
│   └── services/
│       └── researchApi.ts    # SSE client for /research/stream
├── vite.config.ts            # Proxy /research to localhost:8000
└── package.json
```

### Agent Flow

1. **Planner** (Plan-and-Solve): Decomposes research topic into JSON plan with steps containing `action`, `query`, `purpose`
2. **Executor** (ReAct loop): For each step, decides action via LLM (search or note), executes via MCP tools, analyzes results
3. **Synthesizer**: Generates structured report (executive summary, findings, comparison table, bullet points)

### SSE Event Types

The `/research/stream` endpoint emits these event types:
- `plan` - Research plan with steps
- `progress` - Phase/status updates (planning, execution, synthesis)
- `search_result` - Tavily search results
- `note` - Saved note metadata
- `report` - Final structured report
- `done` - Completion signal
- `error` - Error information

## Key Configuration

Environment variables (in `backend/.env`):
- `LLM_API_URL` - LLM API endpoint (default: https://llmapi.paratera.com/v1)
- `LLM_API_KEY` - Required for LLM calls
- `LLM_MODEL_NAME` - Model name (default: kimi-k2)
- `TAVILY_API_KEY` - Required for search functionality

## MCP Tools

Both tools implement `to_mcp_tool()` for MCP compatibility:

- **search_tool**: Wraps Tavily API, supports `search_academic()` with predefined academic domains
- **note_tool**: Persists notes as JSON files in `notes/` directory with tags and metadata

## API Endpoints

- `POST /research/stream` - SSE streaming research (preferred for real-time UI)
- `POST /research/sync` - Synchronous research, returns complete results
- `GET /` - Health check
- `GET /health` - Health check

## Skills

The `skills/deep-research/` directory contains Anthropic skill definitions:
- `SKILL.md` - Skill configuration and documentation
- `resources/templates/report_template.md` - Report structure template

## Notes

- The frontend runs on port 5173, backend on port 8000
- Vite proxy forwards `/research/*` requests to backend
- Notes are stored as JSON files in `backend/notes/` (created automatically)
- Research reports include Chinese and English bilingual support
