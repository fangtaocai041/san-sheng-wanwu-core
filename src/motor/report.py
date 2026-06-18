"""ReportGenerator — 报告生成器"""

from __future__ import annotations
from typing import Any, Dict, List
from datetime import datetime


class ReportGenerator:
    """生成结构化的分析报告。"""

    def __init__(self):
        self.name = "report"

    def generate(self, pipeline_result: dict, format: str = "markdown") -> str:
        """根据管道执行结果生成报告。"""
        if format == "markdown":
            return self._markdown(pipeline_result)
        elif format == "json":
            import json
            return json.dumps(pipeline_result, ensure_ascii=False, indent=2)
        return str(pipeline_result)

    def _markdown(self, data: dict) -> str:
        trace = data.get("trace_id", "unknown")[:8]
        query = data.get("query", "")
        species = data.get("species", "")
        stages = data.get("stages", {})

        lines = [
            f"# 物种分析报告: {query}",
            f"",
            f"- **Trace**: {trace}",
            f"- **查询**: {query}",
            f"- **物种**: {species}",
            f"- **时间**: {data.get('timestamp', '')}",
            f"- **耗时**: {data.get('total_duration_ms', 0):.0f}ms",
            f"",
            f"## 执行阶段",
            f"",
        ]
        for name, stage in stages.items():
            icon = {"completed": "✅", "failed": "❌", "sensing": "🔄", "processing": "🔄", "pending": "⏳"}
            status_icon = icon.get(stage.get("status", ""), "❓")
            summary = stage.get("summary", "")
            duration = stage.get("duration_ms", 0)
            lines.append(f"### {status_icon} {name} ({duration:.0f}ms)")
            lines.append(f"")
            lines.append(f"{summary}")
            if stage.get("error"):
                lines.append(f"")
                lines.append(f"> ⚠️ {stage['error']}")
            lines.append(f"")

        passed = sum(1 for s in stages.values() if s.get("status") == "completed")
        total = len(stages)
        lines.append(f"---")
        lines.append(f"**{passed}/{total} 阶段完成**")

        return "\n".join(lines)
