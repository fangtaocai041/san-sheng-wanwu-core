"""EmergentDetector — 涌现信号检测器 (原 infrastructure/unified_emergence)

三阶处理:
  D₁ 异常: 单个指标偏离基线
  D₂ 突变: 多个相关指标同时偏移
  D₃ 涌现: 形成可解释的新模式
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import math


@dataclass
class EmergentSignal:
    """涌现信号。"""
    level: int          # 1, 2, 3
    description: str
    indicators: List[str] = field(default_factory=list)
    confidence: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "level": f"D{self.level}",
            "description": self.description,
            "indicators": self.indicators,
            "confidence": round(self.confidence, 3),
            "timestamp": self.timestamp,
        }


class EmergentDetector:
    """涌现信号检测器。

    检测来自多个感受器的数据之间的非预期模式。
    当 ≥3 个独立源指向同一个非预期模式时 → D₃ 涌现信号。
    """

    def __init__(self):
        self.name = "emergent"
        self._history: List[dict] = []
        self._z_scores: Dict[str, float] = {}

    def feed(self, data: Dict[str, Any]) -> Optional[EmergentSignal]:
        """输入新数据点，检测涌现信号。返回检测到的信号或 None。"""
        self._history.append(data)
        signal = self._detect(data)
        if signal:
            self._z_scores.clear()
        return signal

    def _detect(self, data: dict) -> Optional[EmergentSignal]:
        """三阶检测：异常 → 突变 → 涌现。"""
        # D₁: 检测异常值
        anomalies = self._find_anomalies(data)
        if not anomalies:
            return None

        # D₂: 检查多个异常是否同时出现
        if len(anomalies) >= 2:
            # D₃: 检查是否形成可解释模式
            pattern = self._find_pattern(anomalies, data)
            if pattern:
                return EmergentSignal(
                    level=3,
                    description=pattern,
                    indicators=anomalies,
                    confidence=min(len(anomalies) * 0.25, 0.95),
                )
            return EmergentSignal(
                level=2,
                description=f"多指标同时偏移: {', '.join(anomalies)}",
                indicators=anomalies,
                confidence=min(len(anomalies) * 0.2, 0.8),
            )

        return EmergentSignal(
            level=1,
            description=f"异常: {anomalies[0]}",
            indicators=anomalies,
            confidence=0.4,
        )

    def _find_anomalies(self, data: dict) -> list:
        """找出数据中的异常指标。"""
        anomalies = []
        for key, value in data.items():
            if isinstance(value, (int, float)):
                z = self._z_score(key, value)
                if abs(z) > 2.0:  # |z| > 2 视为异常
                    anomalies.append(key)
        return anomalies

    def _z_score(self, key: str, value: float) -> float:
        """计算某个指标的 Z 分数。"""
        if key not in self._z_scores:
            self._z_scores[key] = value
            return 0.0
        prev = self._z_scores[key]
        if prev == 0:
            return 0.0
        return (value - prev) / max(abs(prev), 0.001)

    def _find_pattern(self, anomalies: list, data: dict) -> Optional[str]:
        """检查异常是否形成可解释的模式。"""
        pattern_pairs = {
            ("papers_found", "avg_confidence"): "文献数量和质量的同步变化",
            ("temperature", "salinity"): "水环境参数变化",
            ("population", "habitat_loss"): "种群与栖息地的关联变化",
        }
        for (k1, k2), desc in pattern_pairs.items():
            if k1 in anomalies and k2 in data:
                return desc
        return None

    def detect(self, metrics: dict) -> dict:
        """兼容旧版接口。"""
        signal = self.feed(metrics)
        return {
            "status": "ok",
            "signal": signal.to_dict() if signal else None,
            "history_length": len(self._history),
        }
