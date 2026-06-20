"""
cortex/dialectics — 辩证综合皮层

整合自 conflict-arbiter/src/arbiter.py:
  - ConflictArbiter.detect_conflicts() → 矛盾检测
  - ConflictArbiter.arbitrate() → 辩证仲裁
  - _weighted_arbitration() → 加权裁决
  - _circuit_judgment() → 电路裁决 (多数一致则通过)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import math


# ── 数据结构 ──

@dataclass
class SourceClaim:
    """一个来源对某字段的声明。"""
    source: str
    field: str
    value: Any
    weight: float = 1.0       # 来源可信权重
    timestamp: str = ""        # 声明时间
    evidence: str = ""         # 证据描述


@dataclass
class Contradiction:
    source_a: str
    source_b: str
    field: str
    value_a: Any
    value_b: Any
    severity: float = 0.0      # 0-1

    def describe(self) -> str:
        return f"[{self.field}] {self.source_a}={self.value_a} vs {self.source_b}={self.value_b}"


@dataclass
class Synthesis:
    field: str
    thesis: str = ""
    antithesis: str = ""
    synthesis: str = ""
    confidence: float = 0.0
    contradictions: List[Contradiction] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "field": self.field,
            "thesis": self.thesis,
            "antithesis": self.antithesis,
            "synthesis": self.synthesis,
            "confidence": round(self.confidence, 3),
            "contradictions": [c.describe() for c in self.contradictions],
            "contradiction_count": len(self.contradictions),
        }


# ── 核心引擎 ──

class DialecticsCortex:
    """辩证综合皮层。
    
    多源声明 → 矛盾检测 → 辩证分析 → 综合判断
    
    三种裁决模式:
      1. 加权投票 (weighted): 按来源权重投票
      2. 电路裁决 (circuit): 多数一致则通过 (2/3 多数)
      3. 熔断 (circuit_break): 严重矛盾时触发
    """

    def __init__(self):
        self.name = "dialectics"
        self._default_weights = {
            "iucn": 1.0, "cites": 1.0, "pubmed": 0.9, "crossref": 0.85,
            "openalex": 0.8, "cnki": 0.7, "google_scholar": 0.6,
            "fishbase": 0.75, "chinese_red_list": 0.7,
        }

    def synthesize(self, field: str, claims: Dict[str, Any],
                   weights: Optional[Dict[str, float]] = None,
                   mode: str = "weighted") -> Synthesis:
        """辩证综合多源声明。

        Args:
            field: 综合的维度
            claims: {source_name: value} 各源头的声明
            weights: {source_name: weight} 可信权重
            mode: "weighted" | "circuit"

        Returns:
            Synthesis 包含正题/反题/合题
        """
        weights = weights or {}
        combined_weights = {}
        for src in claims:
            combined_weights[src] = weights.get(src, self._default_weights.get(src, 0.5))

        # 1. 检测矛盾
        contradictions = self._detect_contradictions(claims)

        # 2. 选择裁决模式
        if mode == "circuit" and len(claims) >= 3:
            result = self._circuit_judgment(field, claims, combined_weights)
        else:
            result = self._weighted_arbitration(field, claims, combined_weights)

        result.contradictions = contradictions

        # 正题 = 权重最高的来源
        if claims:
            thesis_src = max(claims, key=lambda s: combined_weights.get(s, 0.5))
            result.thesis = str(claims[thesis_src])

            # 反题 = 与正题矛盾的第一个
            for c in contradictions:
                if c.source_a == thesis_src or c.source_b == thesis_src:
                    result.antithesis = c.describe()
                    break

        return result

    def _detect_contradictions(self, claims: Dict[str, Any]) -> List[Contradiction]:
        """检测所有声明对之间的矛盾。"""
        contradictions = []
        sources = list(claims.keys())
        for i in range(len(sources)):
            for j in range(i + 1, len(sources)):
                a, b = sources[i], sources[j]
                va, vb = claims[a], claims[b]
                if va != vb:
                    sev = self._calc_severity(va, vb)
                    contradictions.append(Contradiction(
                        source_a=a, source_b=b, field="",
                        value_a=va, value_b=vb, severity=sev,
                    ))
        return contradictions

    def _weighted_arbitration(self, field: str, claims: Dict[str, Any],
                               weights: Dict[str, float]) -> Synthesis:
        """加权投票仲裁。"""
        if not claims:
            return Synthesis(field=field, synthesis="(无数据)", confidence=0.0)

        # 按值聚合权重
        value_weights: Dict[str, float] = {}
        for src, value in claims.items():
            key = str(value)
            value_weights[key] = value_weights.get(key, 0.0) + weights.get(src, 0.5)

        total_weight = sum(value_weights.values())
        if total_weight == 0:
            return Synthesis(field=field, synthesis="(无法裁决)", confidence=0.0)

        synthesis_value = max(value_weights, key=value_weights.get)
        confidence = value_weights[synthesis_value] / total_weight

        return Synthesis(field=field, synthesis=synthesis_value, confidence=confidence)

    def _circuit_judgment(self, field: str, claims: Dict[str, Any],
                           weights: Dict[str, float]) -> Synthesis:
        """电路裁决: 2/3 多数一致则通过, 否则触发熔断。"""
        if len(claims) < 3:
            return self._weighted_arbitration(field, claims, weights)

        # 找到多数意见
        value_count: Dict[str, float] = {}
        for src, value in claims.items():
            key = str(value)
            value_count[key] = value_count.get(key, 0.0) + weights.get(src, 0.5)

        total = sum(value_count.values())
        majority_value = max(value_count, key=value_count.get)
        majority_weight = value_count[majority_value]

        if majority_weight / total >= 2/3:
            return Synthesis(field=field, synthesis=majority_value,
                             confidence=majority_weight / total)

        # 熔断: 无 2/3 多数
        return Synthesis(field=field, synthesis="(熔断-无法达成多数)",
                         antithesis=f"No 2/3 majority among {len(claims)} sources",
                         confidence=0.0)

    def _calc_severity(self, a: Any, b: Any) -> float:
        if type(a) == type(b):
            if isinstance(a, (int, float)):
                return min(abs(float(a) - float(b)) / max(abs(float(a)), 1.0), 1.0)
            if isinstance(a, str):
                return 0.8  # 字符串不同视为严重
        return 0.5

    def batch_synthesize(self, field_claims: Dict[str, Dict[str, Any]],
                          weights: Optional[Dict[str, float]] = None) -> List[Synthesis]:
        """批量综多组声明。"""
        return [self.synthesize(field, claims, weights)
                for field, claims in field_claims.items()]

    def detect_conflicts(self, sources: list) -> dict:
        """兼容旧版 conflict-arbiter 的 detect_conflicts 接口。"""
        claims = {}
        for src in sources:
            name = src.get("source", "unknown")
            field = src.get("field", "protection_level")
            value = src.get("protection_level", src.get("value", "unknown"))
            claims[f"{name}@{field}"] = value
        return {
            "status": "ok",
            "contradictions": [c.describe() for c in self._detect_contradictions(claims)],
        }

    def arbitrate(self, sources: list, **kwargs) -> dict:
        """兼容旧版 conflict-arbiter 的 arbitrate 接口。"""
        claims = {}
        weights = {}
        for src in sources:
            name = src.get("source", "unknown")
            claims[name] = src.get("protection_level", src.get("value", "unknown"))
            weights[name] = src.get("weight", self._default_weights.get(name, 0.5))
        result = self.synthesize("protection", claims, weights)
        return {
            "status": "ok",
            "conflict_level": "high" if len(result.contradictions) > 0 else "none",
            "synthesis": result.synthesis,
            "confidence": result.confidence,
            "contradictions": [c.describe() for c in result.contradictions],
        }

    def health(self) -> dict:
        return {"status": "ok", "name": self.name}

    def info(self) -> dict:
        return {"name": self.name, "version": "0.2.0", "modes": ["weighted", "circuit"]}

    # ── 因果推断 ──

    def infer_causation(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从多源观察中推断因果关系。"""
        if not observations:
            return []
        inferences = []
        by_outcome: Dict[str, List[str]] = {}
        for obs in observations:
            outcome = str(obs.get("outcome", ""))
            factor = str(obs.get("factor", ""))
            if outcome not in by_outcome:
                by_outcome[outcome] = []
            by_outcome[outcome].append(factor)
        for outcome, factors in by_outcome.items():
            if len(factors) >= 2:
                common = set(factors[0])
                for f in factors[1:]:
                    common &= set(f.split(","))
                if common:
                    inferences.append({
                        "cause": ",".join(common),
                        "effect": outcome,
                        "confidence": min(0.7, len(factors) * 0.2),
                        "method": "求同法",
                    })
        factor_outcome_pairs: Dict[str, set] = {}
        for obs in observations:
            f = str(obs.get("factor", ""))
            o = str(obs.get("outcome", ""))
            if f not in factor_outcome_pairs:
                factor_outcome_pairs[f] = set()
            factor_outcome_pairs[f].add(o)
        for factor, outcomes in factor_outcome_pairs.items():
            if len(outcomes) >= 2:
                inferences.append({
                    "cause": factor,
                    "effect": ",".join(outcomes),
                    "confidence": 0.4,
                    "method": "共变法",
                })
        return inferences

    def search(self, query: str, **kwargs) -> dict:
        return {"status": "ok", "name": self.name, "modes": ["weighted", "circuit"]}
