"""
Tavily 搜索工具 - MCP 标准实现
"""
from typing import List, Optional
from dataclasses import dataclass
from tavily import TavilyClient
import httpx

from app.config import TAVILY_API_KEY


@dataclass
class SearchResult:
    """搜索结果数据结构"""
    title: str
    url: str
    content: str
    score: float
    raw_content: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "content": self.content,
            "score": self.score,
            "raw_content": self.raw_content
        }


class SearchTool:
    """
    Tavily 搜索工具 - MCP 标准

    用于搜索学术文献和相关资料
    """

    name = "search"
    description = "搜索学术文献和相关资料，返回结构化搜索结果"
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索查询语句"
            },
            "max_results": {
                "type": "integer",
                "description": "最大返回结果数",
                "default": 5
            },
            "search_depth": {
                "type": "string",
                "enum": ["basic", "advanced"],
                "description": "搜索深度",
                "default": "basic"
            },
            "include_domains": {
                "type": "array",
                "items": {"type": "string"},
                "description": "限定搜索域名列表"
            }
        },
        "required": ["query"]
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or TAVILY_API_KEY
        self._client = None

    @property
    def client(self) -> TavilyClient:
        """懒加载 Tavily 客户端"""
        if self._client is None:
            if not self.api_key:
                raise ValueError("TAVILY_API_KEY 未配置")
            self._client = TavilyClient(api_key=self.api_key)
        return self._client

    async def execute(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """
        执行搜索

        Args:
            query: 搜索查询
            max_results: 最大结果数
            search_depth: 搜索深度 (basic/advanced)
            include_domains: 限定域名列表

        Returns:
            搜索结果列表
        """
        try:
            # 构建搜索参数
            search_params = {
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
            }

            if include_domains:
                search_params["include_domains"] = include_domains

            # 执行搜索
            response = self.client.search(**search_params)

            # 解析结果
            results = []
            for item in response.get("results", []):
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    score=item.get("score", 0.0),
                    raw_content=item.get("raw_content")
                )
                results.append(result)

            return results

        except Exception as e:
            raise RuntimeError(f"搜索失败: {str(e)}")

    async def search_academic(
        self,
        query: str,
        max_results: int = 5
    ) -> List[SearchResult]:
        """
        学术搜索 - 限定学术域名

        Args:
            query: 搜索查询
            max_results: 最大结果数

        Returns:
            搜索结果列表
        """
        academic_domains = [
            "scholar.google.com",
            "arxiv.org",
            "pubmed.ncbi.nlm.nih.gov",
            "dl.acm.org",
            "ieeexplore.ieee.org",
            "springer.com",
            "nature.com",
            "science.org",
            "researchgate.net",
            "semanticscholar.org"
        ]

        return await self.execute(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            include_domains=academic_domains
        )

    def to_mcp_tool(self) -> dict:
        """转换为 MCP 工具格式"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.parameters
        }


# 创建默认实例
search_tool = SearchTool()
