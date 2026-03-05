"""
配置管理模块
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# LLM 配置
LLM_API_URL = os.getenv("LLM_API_URL", "https://llmapi.paratera.com/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "kimi-k2")

# Tavily 搜索配置
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# 笔记存储路径
NOTES_DIR = BASE_DIR / "notes"
NOTES_DIR.mkdir(exist_ok=True)

# 服务器配置
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

# CORS 配置
CORS_ORIGINS = [
    "http://localhost:5173",  # Vite 开发服务器
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
