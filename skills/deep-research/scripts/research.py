#!/usr/bin/env python3
"""
深度研究技能脚本

可以从命令行直接调用的研究脚本
"""
import asyncio
import argparse
import json
import sys
from pathlib import Path

# 添加后端路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from app.agents.graph import run_research


async def main():
    parser = argparse.ArgumentParser(description="深度研究助手")
    parser.add_argument("topic", help="研究主题")
    parser.add_argument("--max-steps", type=int, default=5, help="最大研究步骤数")
    parser.add_argument("--language", choices=["zh", "en"], default="zh", help="输出语言")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")

    args = parser.parse_args()

    print(f"🔍 开始研究: {args.topic}")
    print(f"📋 最大步骤: {args.max_steps}")
    print(f"🌐 输出语言: {args.language}")
    print("-" * 50)

    report_content = None

    async for event in run_research(
        topic=args.topic,
        max_steps=args.max_steps,
        language=args.language
    ):
        event_type = event.get("type")
        data = event.get("data", {})

        if args.verbose:
            print(f"[{event_type}] {json.dumps(data, ensure_ascii=False)[:100]}")

        if event_type == "plan":
            print(f"\n📋 研究计划 ({data['total_steps']} 步):")
            for step in data["steps"]:
                print(f"   {step['step']}. {step['action']}")

        elif event_type == "progress":
            if data.get("message"):
                print(f"⏳ {data['message']}")

        elif event_type == "search_result":
            print(f"🔍 搜索完成: 找到 {data['count']} 个结果")

        elif event_type == "note":
            print(f"📝 笔记已保存: {data['id']}")

        elif event_type == "report":
            print("\n" + "=" * 50)
            print("📄 研究报告已生成!")
            print("=" * 50)
            report_content = data["report"]

            if args.output:
                output_path = Path(args.output)
                output_path.write_text(report_content, encoding="utf-8")
                print(f"💾 报告已保存到: {output_path}")
            else:
                print("\n" + report_content)

        elif event_type == "error":
            print(f"❌ 错误: {data.get('message', '未知错误')}")

        elif event_type == "done":
            print("\n✅ 研究完成!")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
