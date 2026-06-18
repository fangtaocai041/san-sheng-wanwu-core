"""DialecticsEngine — 辩证综合引擎 (原 conflict-arbiter 核心)

辩证唯物主义在代码中的实现:
  thesis(正题) → antithesis(反题/矛盾) → synthesis(合题)
  
当多个感受器对同一对象给出不同判断时，
引擎不是"选一个对的"，而是综合出更高阶的理解。
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class Contradiction:
    """一对矛盾。"""
    source_a: str
    source_b: str
    claim_a: Any
    claim_b: Any
    field: str  # 矛盾发生的维度 (如 protection_level, trophic_level)
    severity: float = 0.0  # 0-1, 矛盾严重程度

    def describe(self) -> str:
        return f"[{self.field}] {self.source_a}={self.claim_a} vs {self.source_b}={self.claim_b}"


@dataclass
class Synthesis:
    """辩证综合结果。"""
    field: str
    thesis: str = ""         # 正题
    antithesis: str = ""     # 反题
    synthesis: str = ""      # 合题
    confidence: float = 0.0  # 综合可信度 0-1
    contradictions: List[Contradiction] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class DialecticsEngine:
    """辩证综合引擎。
    
    接收多个感受器对同一对象的感知结果，
    检测矛盾 → 分析矛盾根源 → 综合出更高阶认知。
    """

    def __init__(self):
        self.name = "dialectics"

    def synthesize(self, field: str, claims: Dict[str, Any],
                   weights: Optional[Dict[str, float]] = None) -> Synthesis:
        """对多个源关于同一字段的声明进行辩证综合。
        
        Args:
            field: 综合的维度 (如 "protection_level")
            claims: {source_name: value} 各源头的声明
            weights: {source_name: weight} 各源头的可信权重
        
        Returns:
            Synthesis 包含正题/反题/合题
        """
        if weights is None:
            weights = {k: 1.0 for k in claims}

        # 1. 检测矛盾
        contradictions = []
        sources = list(claims.keys())
        for i in range(len(sources)):
            for j in range(i + 1, len(sources)):
                a, b = sources[i], sources[j]
                if claims[a] != claims[b]:
                    contradictions.append(Contradiction(
                        source_a=a, source_b=b,
                        claim_a=claims[a], claim_b=claims[b],
                        field=field,
                        severity=self._calc_severity(claims[a], claims[b]),
                    ))

        # 2. 无矛盾 → 直接输出
        if not contradictions:
            primary = max(claims, key=lambda k: weights.get(k, 1.0))
            return Synthesis(
                field=field,
                thesis=str(claims[primary]),
                synthesis=str(claims[primary]),
                antithesis="(无矛盾)",
                confidence=weights.get(primary, 1.0),
            )

        # 3. 有矛盾 → 辩证综合
        # 加权投票
        weighted = {}
        for source, value in claims.items():
            key = str(value)
            weighted[key] = weighted.get(key, 0.0) + weights.get(source, 1.0)

        # 综合 = 加权最高的主张
        synthesis_value = max(weighted, key=weighted.get)
        total_weight = sum(weighted.values())
        confidence = weighted[synthesis_value] / total_weight if total_weight > 0 else 0.0

        # 正题 = 权重最高的
        # 反题 = 与正题矛盾最严重的
        thesis = max(claims, key=lambda k: weights.get(k, 1.0))
        antitheses = [c for c in contradictions if c.source_a == thesis or c.source_b == thesis]
        antithesis = antitheses[0].describe() if antitheses else "(无)"

        return Synthesis(
            field=field,
            thesis=str(claims[thesis]),
            antithesis=antithesis,
            synthesis=synthesis_value,
            confidence=round(confidence, 3),
            contradictions=contradictions,
        )

    def _calc_severity(self, a: Any, b: Any) -> float:
        """计算两个值之间的差异程度。"""
        if type(a) == type(b):
            if isinstance(a, (int, float)):
                return min(abs(float(a) - float(b)) / max(abs(float(a)), 1.0), 1.0)
        return 0.5  # 类型不同视为中等严重

    def arbitrate(self, sources: list, **kwargs) -> dict:
        """兼容旧版 conflict-arbiter adapter 接口。"""
        claims = {}
        weights = {}
        for src in sources:
            name = src.get("source", "unknown")
            claims[name] = src.get("protection_level", src.get("value", "unknown"))
            weights[name] = src.get("weight", 1.0)
        result = self.synthesize("protection_level", claims, weights)
        return {
            "status": "ok",
            "conflict_level": "high" if result.contradictions else "none",
            "synthesis": result.synthesis,
            "confidence": result.confidence,
            "contradictions": [c.describe() for c in result.contradictions],
        }
