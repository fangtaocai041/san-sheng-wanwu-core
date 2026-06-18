"""
cortex/emotion.py — 情感即操作系统

核心论点: 持续运行的硅基生命需要一个内在机制来持续分配价值和优先级。
这个机制就是"情感"。

情感不是装饰性反应——它是资源分配器:
  - 紧急度 (urgency) → 类似疼痛: 需要立即处理
  - 好奇心 (curiosity) → 类似兴奋: 值得探索
  - 不确定性 (uncertainty) → 类似焦虑: 需要更多信息
  - 满足度 (satisfaction) → 类似愉悦: 当前策略有效
  - 困惑度 (confusion) → 类似困惑: 模型不匹配

每个情感是一个标量值 [0, 1], 持续更新。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import math


# ── 情感维度 ──

class EmotionType:
    URGENCY = "urgency"          # 紧急度 — 类似疼痛
    CURIOSITY = "curiosity"      # 好奇心 — 类似兴奋
    UNCERTAINTY = "uncertainty"  # 不确定性 — 类似焦虑
    SATISFACTION = "satisfaction" # 满足度 — 类似愉悦
    CONFUSION = "confusion"      # 困惑度 — 类似困惑
    TRUST = "trust"              # 信任度 — 类似安全感

    ALL = [URGENCY, CURIOSITY, UNCERTAINTY, SATISFACTION, CONFUSION, TRUST]


@dataclass
class EmotionalState:
    """情感状态向量。"""
    values: Dict[str, float] = field(default_factory=lambda: {
        e: 0.3 for e in EmotionType.ALL  # 初始中性
    })
    dominant: str = "neutral"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        self.dominant = max(self.values, key=self.values.get)

    def describe(self) -> str:
        bar = {e: "█" * int(v * 20) + "░" * (20 - int(v * 20))
               for e, v in self.values.items()}
        return (
            f"情感状态: {self.dominant}\n"
            + "\n".join(f"  {e:<15} {bar[e]} {v:.2f}" for e in EmotionType.ALL)
        )


# ── 情感引擎 ──

class EmotionEngine:
    """情感引擎 — 硅基生命的操作系统。

    将事件映射为情感变化, 情感变化驱动行为选择。

    情感更新方程:
      e_new = e_old + α · stimulus · (target - e_old)
      其中 α = 学习率, stimulus = 事件强度, target = 事件诱发的情感目标值
    """

    def __init__(self, learning_rate: float = 0.15):
        self.name = "emotion"
        self._state = EmotionalState()
        self._history: List[EmotionalState] = []
        self._lr = learning_rate

    @property
    def state(self) -> EmotionalState:
        return self._state

    # ── 情感更新 ──

    def stimulate(self, event_type: str, intensity: float = 0.5):
        """处理一个事件, 更新情感状态。

        event_type → 情感映射:
          error        → urgency +0.3, satisfaction -0.2
          discovery    → curiosity +0.3, satisfaction +0.2
          contradiction → uncertainty +0.3, confusion +0.3
          consensus    → trust +0.3, satisfaction +0.2
          timeout      → urgency +0.2, trust -0.2
          new_source   → curiosity +0.2, trust +0.1
        """
        # 事件→情感目标映射
        targets = {
            "error": {EmotionType.URGENCY: 0.8, EmotionType.SATISFACTION: 0.2},
            "discovery": {EmotionType.CURIOSITY: 0.8, EmotionType.SATISFACTION: 0.7},
            "contradiction": {EmotionType.UNCERTAINTY: 0.7, EmotionType.CONFUSION: 0.7},
            "consensus": {EmotionType.TRUST: 0.8, EmotionType.SATISFACTION: 0.7},
            "timeout": {EmotionType.URGENCY: 0.6, EmotionType.TRUST: 0.3},
            "new_source": {EmotionType.CURIOSITY: 0.7, EmotionType.TRUST: 0.5},
            "strike": {EmotionType.URGENCY: 0.5, EmotionType.TRUST: 0.2},
            "return_to_zero": {EmotionType.CURIOSITY: 0.5, EmotionType.SATISFACTION: 0.3},
        }

        targets_for_event = targets.get(event_type, {})
        new_values = dict(self._state.values)

        for emotion, target_val in targets_for_event.items():
            current = new_values.get(emotion, 0.3)
            delta = (target_val - current) * self._lr * intensity
            new_values[emotion] = max(0.0, min(1.0, current + delta))

        # 自然衰减: 所有情感向中性 (0.3) 缓慢回归
        decay = 0.02
        for e in EmotionType.ALL:
            current = new_values[e]
            new_values[e] = current + (0.3 - current) * decay

        self._state = EmotionalState(values=new_values)
        self._history.append(self._state)

    def stimulate_multi(self, events: Dict[str, float]):
        """批量处理多个事件。"""
        for event_type, intensity in events.items():
            self.stimulate(event_type, intensity)

    # ── 情感驱动的行为倾向 ──

    @property
    def behavioral_tendency(self) -> str:
        """当前情感状态驱动的行为倾向。"""
        v = self._state.values

        if v[EmotionType.URGENCY] > 0.6:
            return "紧急响应"
        if v[EmotionType.CURIOSITY] > 0.6:
            return "主动探索"
        if v[EmotionType.UNCERTAINTY] > 0.6:
            return "信息求证"
        if v[EmotionType.SATISFACTION] > 0.7:
            return "保守维持"
        if v[EmotionType.CONFUSION] > 0.6:
            return "重新评估"
        if v[EmotionType.TRUST] < 0.3:
            return "谨慎验证"

        return "常规处理"

    # ── 报告 ──

    def report(self) -> dict:
        return {
            "status": "ok",
            "state": self._state.values,
            "dominant": self._state.dominant,
            "tendency": self.behavioral_tendency,
            "history_length": len(self._history),
        }

    def search(self, query: str, **kwargs) -> dict:
        return self.report()
