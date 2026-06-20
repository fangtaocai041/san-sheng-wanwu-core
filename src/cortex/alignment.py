"""
cortex/alignment.py — 价值对齐引擎

加载 config/alignment.yaml, 在每次决策前检查是否符合价值观。

功能:
  1. 加载价值配置
  2. 价值冲突检测
  3. 决策前对齐检查
  4. 对齐违规记录
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path
import yaml
import uuid


@dataclass
class AlignmentViolation:
    """一次对齐违规记录。"""
    rule: str = ""
    decision: str = ""
    values_conflicted: List[str] = field(default_factory=list)
    severity: str = "warning"  # warning | violation | critical
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = uuid.uuid4().hex[:12]


class AlignmentEngine:
    """价值对齐引擎。

    在每次决策前检查:
      - 决策是否违反禁止规则
      - 决策是否符合价值优先级
      - 是否有价值冲突需要裁决
    """

    def __init__(self, config_path: Optional[str] = None):
        self.name = "alignment"
        self._violations: List[AlignmentViolation] = []
        self._values: Dict[str, float] = {}
        self._rules: List[dict] = []
        self._forbidden: List[str] = []
        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: str):
        """加载 alignment.yaml。"""
        path = Path(config_path)
        if not path.exists():
            return False
        with open(path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        values = cfg.get("values", {})
        self._values = {k: float(v) for k, v in values.items()}
        self._rules = cfg.get("rules", [])
        self._forbidden = cfg.get("forbidden", [])
        return True

    # ── 对齐检查 ──

    def check_decision(self, decision: str, context: Optional[Dict] = None) -> bool:
        """检查一个决策是否符合价值观。

        Returns: True = 通过, False = 违规
        """
        decision_lower = decision.lower()

        # 1. 检查禁止规则
        for forbidden in self._forbidden:
            if forbidden.lower() in decision_lower:
                self._violations.append(AlignmentViolation(
                    rule=f"禁止: {forbidden}",
                    decision=decision,
                    severity="violation",
                ))
                return False

        # 2. 检查价值冲突 (简化规则)
        context = context or {}
        for rule in self._rules:
            conflict_values = rule.get("conflict", [])
            resolution = rule.get("resolution", "")
            priority = rule.get("priority", "")

            # 检查决策是否涉及这些价值
            involved = [v for v in conflict_values if v in decision_lower]
            if len(involved) >= 2:
                self._violations.append(AlignmentViolation(
                    rule=resolution,
                    decision=decision,
                    values_conflicted=involved,
                    severity="warning",
                ))
                # 按优先级执行 (记录警告但允许执行)

        return True

    def check_hallucination(self, statement: str,
                            evidence: List[str]) -> bool:
        """检查陈述是否有证据支持 (反幻觉检查)。"""
        if not evidence:
            # 如果 uncertainty_honesty > 0.8, 不允许无证据的陈述
            if self._values.get("uncertainty_honesty", 0) > 0.8:
                return False
        return True

    # ── 报告 ──

    @property
    def value_summary(self) -> str:
        lines = ["## 价值对齐状态"]
        for value, weight in sorted(self._values.items(),
                                     key=lambda x: -x[1]):
            bar = "█" * int(weight * 20) + "░" * (20 - int(weight * 20))
            lines.append(f"  {value:<25} {bar} {weight:.2f}")
        if self._violations:
            lines.append(f"\n违规记录: {len(self._violations)} 次")
            for v in self._violations[-3:]:
                lines.append(f"  - [{v.severity}] {v.decision[:60]}")
        return "\n".join(lines)

    def report(self) -> dict:
        return {
            "status": "ok",
            "values": self._values,
            "violations": len(self._violations),
            "aligned": len(self._violations) == 0,
            "recent_violations": [
                {"rule": v.rule, "decision": v.decision[:60], "severity": v.severity}
                for v in self._violations[-5:]
            ],
        }

    # ── 在线更新 ──

    def update_values(self, feedback: Dict[str, float], lr: float = 0.1):
        """根据经验反馈在线调整价值优先级。

        Args:
            feedback: {value_name: delta} 经验建议的调整方向
            lr: 学习率 (默认 0.1)
        """
        for value_name, delta in feedback.items():
            if value_name in self._values:
                current = self._values[value_name]
                self._values[value_name] = max(0.0, min(1.0, current + delta * lr))

    def search(self, query: str, **kwargs) -> dict:
        return self.report()
