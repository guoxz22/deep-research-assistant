"""
笔记持久化工具 - MCP 标准实现
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from app.config import NOTES_DIR


@dataclass
class Note:
    """笔记数据结构"""
    id: str
    content: str
    tags: List[str]
    created_at: str
    source: Optional[str] = None
    metadata: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at,
            "source": self.source,
            "metadata": self.metadata
        }


class NoteTool:
    """
    笔记持久化工具 - MCP 标准

    用于保存和管理研究笔记
    """

    name = "note"
    description = "保存研究笔记到本地文件，支持标签分类和元数据"
    parameters = {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "笔记内容"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "标签列表"
            },
            "source": {
                "type": "string",
                "description": "笔记来源（如搜索结果URL）"
            },
            "metadata": {
                "type": "object",
                "description": "额外元数据"
            }
        },
        "required": ["content"]
    }

    def __init__(self, notes_dir: Optional[Path] = None):
        self.notes_dir = notes_dir or NOTES_DIR
        self._ensure_notes_dir()

    def _ensure_notes_dir(self):
        """确保笔记目录存在"""
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    def _generate_note_id(self) -> str:
        """生成唯一笔记ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"note_{timestamp}"

    def _get_note_filepath(self, note_id: str) -> Path:
        """获取笔记文件路径"""
        return self.notes_dir / f"{note_id}.json"

    async def execute(
        self,
        content: str,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Note:
        """
        保存笔记

        Args:
            content: 笔记内容
            tags: 标签列表
            source: 来源信息
            metadata: 额外元数据

        Returns:
            保存的笔记对象
        """
        note_id = self._generate_note_id()
        created_at = datetime.now().isoformat()

        note = Note(
            id=note_id,
            content=content,
            tags=tags or [],
            created_at=created_at,
            source=source,
            metadata=metadata
        )

        # 保存到文件
        filepath = self._get_note_filepath(note_id)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(note.to_dict(), f, ensure_ascii=False, indent=2)

        return note

    async def get_note(self, note_id: str) -> Optional[Note]:
        """
        获取笔记

        Args:
            note_id: 笔记ID

        Returns:
            笔记对象或None
        """
        filepath = self._get_note_filepath(note_id)
        if not filepath.exists():
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        return Note(**data)

    async def list_notes(
        self,
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Note]:
        """
        列出笔记

        Args:
            tags: 过滤标签
            limit: 最大返回数量

        Returns:
            笔记列表
        """
        notes = []

        for filepath in sorted(
            self.notes_dir.glob("note_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            note = Note(**data)

            # 标签过滤
            if tags and not any(tag in note.tags for tag in tags):
                continue

            notes.append(note)

        return notes

    async def delete_note(self, note_id: str) -> bool:
        """
        删除笔记

        Args:
            note_id: 笔记ID

        Returns:
            是否删除成功
        """
        filepath = self._get_note_filepath(note_id)
        if filepath.exists():
            filepath.unlink()
            return True
        return False

    async def append_to_note(
        self,
        note_id: str,
        additional_content: str
    ) -> Optional[Note]:
        """
        追加内容到现有笔记

        Args:
            note_id: 笔记ID
            additional_content: 追加内容

        Returns:
            更新后的笔记
        """
        note = await self.get_note(note_id)
        if not note:
            return None

        note.content += f"\n\n{additional_content}"

        filepath = self._get_note_filepath(note_id)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(note.to_dict(), f, ensure_ascii=False, indent=2)

        return note

    def to_mcp_tool(self) -> dict:
        """转换为 MCP 工具格式"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.parameters
        }


# 创建默认实例
note_tool = NoteTool()
