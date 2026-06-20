"""
motor/world_model.py — D₃ 世界模型 (World Model)

从 cognitive-search-engine 的 SearchPrediction 升级为完整的世界模型。
在发出感知控制前先在内部模拟中进行仿真推演。

核心原理 (Yann LeCun / AMI Labs 2026):
  LLM 预测下一个 token → 符号空间
  世界模型预测下一个状态 → 物理/知识空间

架构:
  - StatePredictor: 当前状态 → 预测下一状态
  - ActionSimulator: 给定行动 → 模拟结果
  - CounterfactualEngine: "如果不同选择会怎样"

学术渊源:
  - LeCun AMI Labs (2025-2026): JEPA 世界模型
  - DeepMind Genie 3 (2025): 实时交互世界模型
  - World Labs Marble (2025): 3D 世界模型
  - Tiny Recursive Model (2025): 递归深度替代参数规模
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import math
import time
import uuid


@dataclass
class WorldState:
    """世界状态快照。"""
    state_id: str = ""
    known_papers: int = 0         # 已知论文数
    contradiction_level: float = 0.0  # 矛盾水平 0-1
    confidence: float = 0.5       # 整体置信度
    active_channels: int = 0      # 活跃感知通道数
    token_budget: float = 1.0     # 剩余 token 预算 0-1
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.state_id:
            self.state_id = uuid.uuid4().hex[:8]
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class StatePrediction:
    """状态预测结果。"""
    next_state: WorldState
    confidence: float       # 预测置信度 0-1
    alternatives: List[WorldState] = field(default_factory=list)


class WorldModel:
    """D₃ 世界模型 — 在发出行动前模拟后果。

    用法:
        wm = WorldModel()
        current = WorldState(known_papers=5, contradiction_level=0.3)
        pred = wm.predict_next(current, action="deep_search")
        wm.update(pred, actual_next)
    """

    def __init__(self, learning_rate: float = 0.1):
        self.name = "world_model"
        self._lr = learning_rate
        self._prediction_errors: List[float] = []
        self._states: List[WorldState] = []

    def predict_next(self, current: WorldState,
                     action: str = "search") -> StatePrediction:
        """基于当前状态和行动预测下一状态。

        Args:
            current: 当前世界状态
            action: 要模拟的行动 (search/deep_search/verify/explore)

        Returns:
            包含预测状态和替代方案的 StatePrediction
        """
        # 行动 → 变换参数
        action_params = {
            "search":      {"papers_delta": 3, "conf_delta": 0.05, "token_cost": 0.1},
            "deep_search": {"papers_delta": 8, "conf_delta": 0.15, "token_cost": 0.3},
            "verify":      {"papers_delta": 1, "conf_delta": 0.10, "token_cost": 0.15},
            "explore":     {"papers_delta": 5, "conf_delta": -0.05, "token_cost": 0.2},
        }
        params = action_params.get(action, action_params["search"])

        # 预测下一状态
        next_state = WorldState(
            known_papers=current.known_papers + params["papers_delta"],
            contradiction_level=max(0, min(1, current.contradiction_level
                                          + (0.1 if action == "verify" else 0.05))),
            confidence=max(0, min(1, current.confidence + params["conf_delta"])),
            active_channels=current.active_channels,
            token_budget=max(0, current.token_budget - params["token_cost"]),
        )

        # 预测置信度 (基于历史准确率)
        if self._prediction_errors:
            avg_error = sum(self._prediction_errors[-10:]) / len(self._prediction_errors[-10:])
            confidence = 1.0 - min(avg_error, 1.0)
        else:
            confidence = 0.7  # 初始默认

        # 替代方案: 不同行动的模拟结果
        alternatives = []
        for alt_action, alt_params in action_params.items():
            if alt_action != action:
                alt = WorldState(
                    known_papers=current.known_papers + alt_params["papers_delta"],
                    confidence=max(0, min(1, current.confidence + alt_params["conf_delta"])),
                    token_budget=max(0, current.token_budget - alt_params["token_cost"]),
                )
                alternatives.append(alt)

        return StatePrediction(
            next_state=next_state,
            confidence=round(confidence, 3),
            alternatives=alternatives,
        )

    def update(self, prediction: StatePrediction,
               actual: WorldState):
        """根据实际结果更新世界模型参数。"""
        # 计算预测误差: 归一化欧氏距离
        pred = prediction.next_state
        error = (
            abs(pred.known_papers - actual.known_papers) / max(pred.known_papers, 1)
            + abs(pred.confidence - actual.confidence)
        ) / 2
        self._prediction_errors.append(min(error, 1.0))

    @property
    def prediction_accuracy(self) -> float:
        if not self._prediction_errors:
            return 0.0
        return 1.0 - sum(self._prediction_errors[-10:]) / len(self._prediction_errors[-10:])

    def search(self, query: str, **kwargs) -> dict:
        return {
            "status": "ok",
            "accuracy": self.prediction_accuracy,
            "states": len(self._states),
        }

    def report(self) -> dict:
        return {
            "status": "ok",
            "name": self.name,
            "prediction_accuracy": round(self.prediction_accuracy, 3),
            "prediction_count": len(self._prediction_errors),
        }
