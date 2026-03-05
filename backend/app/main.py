"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.routers import research

# 创建 FastAPI 应用
app = FastAPI(
    title="深度研究助手 API",
    description="基于 LangChain/LangGraph 的学术文献深度研究智能体",
    version="1.0.0",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(research.router, prefix="/research", tags=["research"])


@app.get("/")
async def root():
    """健康检查端点"""
    return {"status": "ok", "message": "深度研究助手服务运行中"}


@app.get("/health")
async def health():
    """健康检查端点"""
    return {"status": "healthy"}
