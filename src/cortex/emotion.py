"""
cortex/emotion.py — 认知资源分配策略 (替代"情感即操作系统")

核心论点:
  持续运行的认知系统需要内在机制来动态分配有限资源 (A2 认知有限性)。
  在人类中这个机制表现为"情绪"——在硅基中，它是资源分配策略的缓存代理。

术语修正:
  "情感" (emotion) → "资源分配状态" (resource allocation state)
  但在 API 层面保留 EmotionType/EmotionEngine 名称以保证兼容性。

设计原理:
  每次经验更新六维状态:
    urgency      — 紧急度: 高 → 需要立即处理, 减少探索
    curiosity    — 探索欲: 高 → 增加搜索广度, 投入更多资源
    uncertainty  — 不确定性: 高 → 增加验证深度, 多源交叉
    satisfaction — 满足度: 高 → 维持当前策略, 减少干扰
    confusion    — 困惑度: 高 → 需要重新评估模型, 启用辩证综合
    trust        — 信任度: 高 → 减少验证, 低 → 增强猜疑链检测

  这与 Bandit 算法中统计最优动作选择同构:
    emotion = argmax(utility(channel | recent_history))

学术来源:
  - Sutton & Barto (1998) Reinforcement Learning: 探索/利用平衡
  - Damasio (1994) 躯体标记假说: 情绪是决策的快捷方式
  - Simon (1957) Bounded Rationality: 有限理性下的启发式选择
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import math


# ── 资源分配维度 ──

class EmotionType:
    """资源分配策略的六个维度（保持与旧版 API 兼容）。"""
    URGENCY = "urgency"          # 紧急度 → 高: 保守/快速, 低: 开放/耗时
    CURIOSITY = "curiosity"      # 探索欲 → 高: 广搜索, 低: 窄搜索
    UNCERTAINTY = "uncertainty"  # 不确定性 → 高: 深验证, 低: 接受
    SATISFACTION = "satisfaction" # 满足度 → 高: 维持策略, 低: 策略切换
    CONFUSION = "confusion"      # 困惑度 → 高: 模型重估, 低: 模型自信
    TRUST = "trust"              # 信任度 → 高: 低验证开销, 低: 高验证开销

    ALL = [URGENCY, CURIOSITY, UNCERTAINTY, SATISFACTION, CONFUSION, TRUST]


@dataclass
class EmotionalState:
    """资源分配状态向量（保持与旧版 API 兼容）。"""
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
            f"资源分配状态: {self.dominant}\n"
            + "\n".join(f"  {e:<15} {bar[e]} {v:.2f}" for e in EmotionType.ALL)
        )


# ── 资源分配引擎 ──

class EmotionEngine:
    """资源分配策略引擎 — 基于近期经验的统计策略选择。

    将事件映射为策略参数变化, 策略参数驱动资源分配决策。

    更新方程（与旧版一致，保持兼容）:
      e_new = e_old + α · stimulus · (target - e_old)
      其中 α = 学习率, stimulus = 事件强度
    """

    def __init__(self, learning_rate: float = 0.15):
        self.name = "emotion"
        self._state = EmotionalState()
        self._history: List[EmotionalState] = []
        self._lr = learning_rate

    @property
    def state(self) -> EmotionalState:
        return self._state

    # ── 策略更新 ──

    def stimulate(self, event_type: str, intensity: float = 0.5):
        """处理一个事件, 更新资源分配策略参数。

        event_type → 策略参数映射:
          error        → urgency +0.3, satisfaction -0.2 (出错→紧急模式)
          discovery    → curiosity +0.3, satisfaction +0.2 (发现→探索模式)
          contradiction → uncertainty +0.3, confusion +0.3 (矛盾→验证模式)
          consensus    → trust +0.3, satisfaction +0.2 (共识→信任模式)
          timeout      → urgency +0.2, trust -0.2 (超时→紧急减信)
          new_source   → curiosity +0.2, trust +0.1 (新源→探索)
        """
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

        # 自然衰减: 所有参数向中性 (0.3) 缓慢回归
        # 这是策略平滑，不是情感遗忘
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

    # ── 策略驱动的行为倾向 ──

    @property
    def behavioral_tendency(self) -> str:
        """当前策略参数驱动的资源分配倾向。

        这不是"情感倾向"——这是统计最优的资源分配策略。"""
        v = self._state.values

        if v[EmotionType.URGENCY] > 0.6:
            return "紧急响应"     # 减少探索, 快速输出
        if v[EmotionType.CURIOSITY] > 0.6:
            return "主动探索"     # 增加搜索广度
        if v[EmotionType.UNCERTAINTY] > 0.6:
            return "信息求证"     # 增加验证深度
        if v[EmotionType.SATISFACTION] > 0.7:
            return "保守维持"     # 减少资源投入
        if v[EmotionType.CONFUSION] > 0.6:
            return "重新评估"     # 启用辩证综合
        if v[EmotionType.TRUST] < 0.3:
            return "谨慎验证"     # 开启猜疑链

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
