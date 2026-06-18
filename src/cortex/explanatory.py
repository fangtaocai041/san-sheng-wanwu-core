"""
cortex/explanatory — 可解释性: 推理链记录与解释生成

AI 可解释性 (XAI) 要求系统不仅能做出决策, 还能解释:
  1. 做了什么决策
  2. 为什么做这个决策
  3. 证据是什么
  4. 有哪些替代方案被拒绝
  5. 系统的确定性有多高

本模块记录每次决策的完整推理链, 并生成多层解释:
  - L1: 一句话摘要 (什么)
  - L2: 关键原因 (为什么)
  - L3: 完整推理链 (怎么)
  - L4: 反事实分析 (如果不)
  - L5: 概念溯源 (概念的来源与承诺)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid


# ── 推理步骤 ──

@dataclass
class ReasoningStep:
    """推理链中的一个步骤。"""
    step_id: str = ""
    phase: str = ""         # sense | validate | dialectics | emergent | report
    action: str = ""        # 做了什么: search | synthesize | detect | ...
    input_summary: str = ""  # 输入的摘要
    output_summary: str = "" # 输出的摘要
    confidence: float = 0.0  # 本步的可信度 0-1
    duration_ms: float = 0.0
    alternatives: List[str] = field(default_factory=list)  # 被拒绝的替代方案
    evidence: List[str] = field(default_factory=list)       # 支撑证据
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        if not self.step_id:
            self.step_id = uuid.uuid4().hex[:12]


# ── 推理链 ──

@dataclass
class ReasoningTrace:
    """一次查询的完整推理链。"""
    trace_id: str = ""
    query: str = ""
    species: str = ""
    steps: List[ReasoningStep] = field(default_factory=list)
    final_answer: str = ""
    overall_confidence: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        if not self.trace_id:
            self.trace_id = uuid.uuid4().hex

    def add_step(self, step: ReasoningStep):
        """添加推理步骤。"""
        self.steps.append(step)

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def phases_used(self) -> List[str]:
        return list(dict.fromkeys(s.phase for s in self.steps if s.phase))


# ── 解释器 ──

class ExplainabilityEngine:
    """可解释性引擎 — 记录推理链 + 生成多层解释。

    用法:
        engine = ExplainabilityEngine()
        trace = engine.begin(query="鳤", species="Ochetobius elongatus")
        trace.add_step(ReasoningStep(phase="sense", action="search", ...))
        engine.explain(trace, level=1)  # 一句话
        engine.explain(trace, level=3)  # 完整推理链
    """

    def __init__(self):
        self.name = "explainability"
        self._traces: Dict[str, ReasoningTrace] = {}

    def begin(self, query: str, species: str = "") -> ReasoningTrace:
        """开始一个新的推理追踪。"""
        trace = ReasoningTrace(query=query, species=species)
        self._traces[trace.trace_id] = trace
        return trace

    def get_trace(self, trace_id: str) -> Optional[ReasoningTrace]:
        return self._traces.get(trace_id)

    def all_traces(self) -> List[ReasoningTrace]:
        return list(self._traces.values())

    # ── 多层解释生成 ──

    def explain(self, trace: ReasoningTrace, level: int = 2) -> str:
        """生成指定层级的解释。

        Level 1: 一句话摘要
        Level 2: 关键原因 (默认)
        Level 3: 完整推理链
        Level 4: 反事实分析
        Level 5: 概念溯源
        """
        generators = {
            1: self._level1_summary,
            2: self._level2_reasons,
            3: self._level3_chain,
            4: self._level4_counterfactual,
            5: self._level5_provenance,
        }
        gen = generators.get(level, self._level2_reasons)
        return gen(trace)

    def _level1_summary(self, trace: ReasoningTrace) -> str:
        """L1: 一句话摘要 — 什么决策?"""
        total = trace.step_count
        completed = sum(1 for s in trace.steps if not s.error)
        failed = total - completed
        return (
            f"查询「{trace.query}」经过 {total} 步推理 "
            f"({', '.join(trace.phases_used)}), "
            f"{completed} 步成功"
            + (f", {failed} 步失败" if failed else "")
            + f"。综合可信度 {trace.overall_confidence:.0%}。"
        )

    def _level2_reasons(self, trace: ReasoningTrace) -> str:
        """L2: 关键理由 — 为什么?"""
        lines = [f"## 推理解释: {trace.query}", ""]

        # 各阶段的决策理由
        phase_labels = {
            "sense": "感知阶段",
            "kb_lookup": "知识库查询",
            "validate": "可信度验证",
            "dialectics": "辩证综合",
            "emergent": "涌现检测",
            "report": "报告生成",
        }

        for step in trace.steps:
            label = phase_labels.get(step.phase, step.phase)
            icon = "✅" if not step.error else "❌"
            conf = f" (可信度: {step.confidence:.0%})" if step.confidence > 0 else ""
            lines.append(f"### {icon} {label}{conf}")
            lines.append(f"**动作**: {step.action}")
            lines.append(f"**输出**: {step.output_summary[:200]}")
            if step.alternatives:
                lines.append(f"**被拒绝的替代方案**: {'; '.join(step.alternatives[:3])}")
            if step.error:
                lines.append(f"**错误**: {step.error[:100]}")
            lines.append("")

        lines.append(f"**综合可信度**: {trace.overall_confidence:.0%}")
        return "\n".join(lines)

    def _level3_chain(self, trace: ReasoningTrace) -> str:
        """L3: 完整推理链 — 每一步的输入/输出/证据。"""
        lines = [f"## 完整推理链: {trace.query} (trace: {trace.trace_id[:8]})", ""]

        for i, step in enumerate(trace.steps, 1):
            lines.append(f"### Step {i}: {step.phase}/{step.action}")
            lines.append(f"  输入: {step.input_summary[:100]}")
            lines.append(f"  输出: {step.output_summary[:200]}")
            lines.append(f"  可信度: {step.confidence:.0%}")
            lines.append(f"  耗时: {step.duration_ms:.0f}ms")
            if step.evidence:
                for ev in step.evidence[:3]:
                    lines.append(f"  证据: {ev[:150]}")
            if step.alternatives:
                lines.append(f"  替代方案: {'; '.join(step.alternatives[:3])}")
            if step.error:
                lines.append(f"  错误: {step.error}")
            lines.append("")

        return "\n".join(lines)

    def _level4_counterfactual(self, trace: ReasoningTrace) -> str:
        """L4: 反事实分析 — 如果不同选择会怎样?"""
        lines = [f"## 反事实分析: {trace.query}", ""]
        lines.append("反事实分析考察: 如果在关键决策点选择了不同路径会怎样。")
        lines.append("")

        for step in trace.steps:
            if step.alternatives:
                chosen = step.output_summary[:80]
                for alt in step.alternatives[:2]:
                    lines.append(f"- **选择了**: {chosen}")
                    lines.append(f"  **拒绝了**: {alt}")
                    lines.append(f"  **拒绝原因**: {step.evidence[0] if step.evidence else '可信度较低'}")
                    lines.append("")

        if not any(s.alternatives for s in trace.steps):
            lines.append("无替代方案记录 — 此路径是确定性的。")

        return "\n".join(lines)

    def _level5_provenance(self, trace: ReasoningTrace) -> str:
        """L5: 概念溯源 — 用到的概念的来源与承诺。"""
        lines = [f"## 概念溯源: {trace.query}", ""]
        lines.append("本次推理涉及的概念及其本体承诺:")
        lines.append("")

        # 收集涉及的概念
        concepts = set()
        for step in trace.steps:
            if step.phase == "dialectics":
                concepts.add("辩证综合")
                concepts.add("矛盾检测")
            elif step.phase == "validate":
                concepts.add("可信度")
                concepts.add("文献验证")
            elif step.phase == "emergent":
                concepts.add("涌现")
                concepts.add("异常检测")
        concepts.add("物种")
        concepts.add("查询")

        for c in sorted(concepts):
            lines.append(f"- **{c}**")
            if c == "物种":
                lines.append(f"  来源: a_priori (领域先验)")
                lines.append(f"  承诺: 物种是分类学的基本单位，具有可识别的边界")
            elif c == "可信度":
                lines.append(f"  来源: empirical (经验归纳)")
                lines.append(f"  承诺: 多源交叉验证提高认知确定性")
            elif c == "辩证综合":
                lines.append(f"  来源: derived (二阶概念)")
                lines.append(f"  承诺: 矛盾是认知升级的驱动力, 不是错误")
            elif c == "涌现":
                lines.append(f"  来源: empirical (模式发现)")
                lines.append(f"  承诺: ≥3 个独立源指向同一非预期模式 → 涌现信号")
            lines.append("")

        return "\n".join(lines)

    # ── 与 pipeline 集成 ──

    def record_step(self, trace: ReasoningTrace, phase: str, action: str,
                    input_summary: str = "", output_summary: str = "",
                    confidence: float = 0.0, duration_ms: float = 0.0,
                    alternatives: Optional[List[str]] = None,
                    evidence: Optional[List[str]] = None,
                    error: Optional[str] = None) -> ReasoningStep:
        """记录一个推理步骤并添加到追踪。"""
        step = ReasoningStep(
            phase=phase, action=action,
            input_summary=input_summary, output_summary=output_summary,
            confidence=confidence, duration_ms=duration_ms,
            alternatives=alternatives or [],
            evidence=evidence or [],
            error=error,
        )
        trace.add_step(step)
        return step

    def finalize(self, trace: ReasoningTrace, answer: str = "",
                 confidence: float = 0.0):
        """完成推理追踪。"""
        trace.final_answer = answer
        trace.overall_confidence = confidence

    def search(self, query: str, **kwargs) -> dict:
        """兼容 adapter 接口。"""
        traces = self._traces.get(query)
        if traces:
            return {"status": "ok", "explanation": self.explain(traces)}
        return {"status": "ok", "explanation": f"未找到追踪: {query}"}
