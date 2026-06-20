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


# ═══════════════════════════════════════════════════════════
# 音律学: 输出节奏控制 (RhythmicOutput)
# 参考: Shannon 信息论 + 音乐节奏理论
# ═══════════════════════════════════════════════════════════

class RhythmicOutput:
    """受音律学启发的输出节奏控制。

    知识传递和音乐有共同结构: 节奏、韵律、重复、变奏。
    最优的信息节奏不是恒定的，而是与接收者的状态相关的。

    速度模式:
      - allegro (快板): 高置信度 → 直接输出结论
      - andante (行板): 正常节奏
      - adagio  (慢板): 低不确定性 → 放慢、多确认
      - rest    (休止): 矛盾 → 先内部解决再输出
    """

    TEMPO_ALLEGRO = "allegro"
    TEMPO_ANDANTE = "andante"
    TEMPO_ADAGIO = "adagio"
    TEMPO_REST = "rest"

    @staticmethod
    def select_tempo(uncertainty: float = 0.5,
                     confusion: float = 0.3,
                     confidence: float = 0.5) -> str:
        """根据认知状态选择输出速度。"""
        if confusion > 0.7:
            return RhythmicOutput.TEMPO_REST
        if uncertainty > 0.7:
            return RhythmicOutput.TEMPO_ADAGIO
        if confidence > 0.8:
            return RhythmicOutput.TEMPO_ALLEGRO
        return RhythmicOutput.TEMPO_ANDANTE

    @staticmethod
    def describe_tempo(tempo: str) -> str:
        descriptions = {
            RhythmicOutput.TEMPO_ALLEGRO: "快板 — 直接输出结论",
            RhythmicOutput.TEMPO_ANDANTE: "行板 — 正常节奏输出",
            RhythmicOutput.TEMPO_ADAGIO: "慢板 — 放慢输出、多确认",
            RhythmicOutput.TEMPO_REST: "休止 — 先解决内部矛盾",
        }
        return descriptions.get(tempo, "未知节奏")

    @staticmethod
    def should_output(tempo: str) -> bool:
        """根据节奏决定是否输出。"""
        return tempo != RhythmicOutput.TEMPO_REST
