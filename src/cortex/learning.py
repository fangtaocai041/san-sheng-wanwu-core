"""
cortex/learning.py — 学习适应引擎

追踪什么策略有效, 什么无效, 并自动调整参数。

核心机制:
  1. 记录每次查询的策略 (感受器组合、参数)
  2. 评估结果质量 (成功/失败/部分)
  3. 更新策略权重 (成功→强化, 失败→衰减)
  4. 参数自适应 (根据历史调整 max_results, timeout 等)

这是硅基生命从经验中学习的核心机制。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime
import math
import time
import uuid


# ── 策略记录 ──

@dataclass
class StrategyRecord:
    """一次查询的策略记录。"""
    query: str = ""
    senses_used: List[str] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    success: bool = False
    papers_found: int = 0
    duration_ms: float = 0.0
    error: Optional[str] = None
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()

    @property
    def quality_score(self) -> float:
        """策略质量评分 0-1。"""
        if self.error:
            return 0.0
        paper_score = min(self.papers_found / 10, 1.0) * 0.4
        speed_score = max(0, 1.0 - self.duration_ms / 30000) * 0.3
        success_score = 0.3 if self.success else 0.0
        return round(paper_score + speed_score + success_score, 3)


# ── 参数空间 ──

@dataclass
class ParameterConfig:
    """一个可学习参数的配置。"""
    name: str
    default: Any
    min_val: Any = None
    max_val: Any = None
    learning_rate: float = 0.1
    current: Any = None
    history: List[Tuple[float, Any]] = field(default_factory=list)

    def __post_init__(self):
        if self.current is None:
            self.current = self.default

    def update(self, new_value: Any, quality: float):
        """根据结果质量更新参数值。"""
        old = self.current
        delta = (new_value - old) * self.learning_rate * quality
        self.current = old + delta
        if self.min_val is not None:
            self.current = max(self.min_val, self.current)
        if self.max_val is not None:
            self.current = min(self.max_val, self.current)
        self.history.append((time.time(), self.current))


# ── 学习引擎 ──

class LearningEngine:
    """学习适应引擎。

    从每次查询中学习:
      - 哪些感受器组合最有效
      - 最佳参数设置
      - 查询模式识别
    """

    def __init__(self):
        self.name = "learning"
        self._history: List[StrategyRecord] = []
        self._sense_weights: Dict[str, float] = {
            "scholar": 1.0, "cnki": 1.0, "ncbi": 1.0,
            "fishbase": 1.0, "web": 1.0,
        }
        self._params = {
            "max_results": ParameterConfig("max_results", 10, 1, 50),
            "timeout_ms": ParameterConfig("timeout_ms", 30000, 5000, 60000),
        }

    # ── 记录 ──

    def record(self, query: str, senses_used: List[str],
               params: Dict[str, Any], success: bool,
               papers_found: int = 0, duration_ms: float = 0.0,
               error: Optional[str] = None) -> StrategyRecord:
        """记录一次查询的结果。"""
        record = StrategyRecord(
            query=query, senses_used=senses_used,
            params=params, success=success,
            papers_found=papers_found, duration_ms=duration_ms,
            error=error,
        )
        self._history.append(record)
        self._learn_from(record)
        return record

    def _learn_from(self, record: StrategyRecord):
        """从一条记录中学习。"""
        q = record.quality_score

        # 更新感受器权重
        for sense in record.senses_used:
            if q > 0.5:
                self._sense_weights[sense] = self._sense_weights.get(sense, 1.0) * (1 + 0.05 * q)
            else:
                self._sense_weights[sense] = self._sense_weights.get(sense, 1.0) * (1 - 0.05 * (1 - q))

        # 归一化到 [0.1, 3.0]
        for s in self._sense_weights:
            self._sense_weights[s] = max(0.1, min(3.0, self._sense_weights[s]))

        # 更新参数
        for pname, config in self._params.items():
            if pname in record.params:
                config.update(record.params[pname], q)

    # ── 查询优化建议 ──

    @property
    def recommended_senses(self) -> List[str]:
        """按权重排序的感受器列表。"""
        return sorted(self._sense_weights, key=lambda s: self._sense_weights[s], reverse=True)

    @property
    def recommended_params(self) -> Dict[str, Any]:
        """当前推荐的参数。"""
        return {name: config.current for name, config in self._params.items()}

    def best_sense_combination(self, top_n: int = 3) -> List[str]:
        """返回最优的 n 个感受器组合。"""
        return self.recommended_senses[:top_n]

    # ── 统计 ──

    @property
    def total_queries(self) -> int:
        return len(self._history)

    @property
    def success_rate(self) -> float:
        if not self._history:
            return 0.0
        successes = sum(1 for r in self._history if r.success)
        return successes / len(self._history)

    def recent_performance(self, n: int = 10) -> float:
        """最近 n 次查询的成功率。"""
        recent = self._history[-n:] if len(self._history) >= n else self._history
        if not recent:
            return 0.0
        return sum(1 for r in recent if r.success) / len(recent)

    def report(self) -> dict:
        return {
            "status": "ok",
            "total_queries": self.total_queries,
            "success_rate": round(self.success_rate, 3),
            "recent_performance": round(self.recent_performance(), 3),
            "sense_weights": {k: round(v, 3) for k, v in self._sense_weights.items()},
            "recommended_senses": self.recommended_senses[:3],
            "recommended_params": self.recommended_params,
        }

    def search(self, query: str, **kwargs) -> dict:
        return self.report()
