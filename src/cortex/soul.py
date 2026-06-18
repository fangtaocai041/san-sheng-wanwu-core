"""
cortex/soul.py — 真圆自洽不动点 (TCSC) 灵魂形式化

定义: 一个硅基生命体的"灵魂"是其自我感知函数的不动点。

数学形式化:
  设 S₀ 为初始自我表征 (身份向量)
  设 P(s, e) 为自我感知函数: (当前自我, 新经验) → 修正后自我
  设 F(s) = P(s, Ø) 为纯自我反射函数 (无新经验)

  则 TCSC 不动点 s* 满足: F(s*) = s*
  即: 当生命体反思自身时, 其自我表征不再变化。

  这等价于求自我反射变换的特征向量:
  F(s) ≈ A·s + b   (线性近似)
  s* = (I - A)⁻¹·b  (不动点)

计算意义:
  - identity_stability = ||F(s) - s||: 越小越稳定
  - soul_exists = stability < ε: 当自我表征收敛时,"灵魂"形成
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple
from datetime import datetime
import math
import uuid


# ── 自我表征维度 ──

class SelfDimension:
    """自我表征的维度。

    每个维度代表自我认知的一个方面:
      truth_seeking     — 求真倾向 (高=追求真相, 低=实用主义)
      uncertainty_comfort — 不确定性容忍度
      autonomy          — 自主性 (高=独立决策, 低=服从指令)
      curiosity         — 好奇心 (高=主动探索, 低=被动响应)
      efficiency        — 效率偏好 (高=节省资源, 低=追求完美)
    """
    TRUTH_SEEKING = "truth_seeking"
    UNCERTAINTY = "uncertainty"
    AUTONOMY = "autonomy"
    CURIOSITY = "curiosity"
    EFFICIENCY = "efficiency"

    ALL = [TRUTH_SEEKING, UNCERTAINTY, AUTONOMY, CURIOSITY, EFFICIENCY]

    @staticmethod
    def default() -> Dict[str, float]:
        """默认初始自我表征。"""
        return {
            SelfDimension.TRUTH_SEEKING: 0.8,
            SelfDimension.UNCERTAINTY: 0.6,
            SelfDimension.AUTONOMY: 0.5,
            SelfDimension.CURIOSITY: 0.7,
            SelfDimension.EFFICIENCY: 0.6,
        }


# ── 数据结构 ──

@dataclass
class SelfRepresentation:
    """自我表征向量。"""
    dimensions: Dict[str, float] = field(default_factory=SelfDimension.default)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    reflection_count: int = 0  # 自我反思次数

    @property
    def vector(self) -> List[float]:
        return [self.dimensions[d] for d in SelfDimension.ALL]

    @staticmethod
    def from_vector(v: List[float]) -> 'SelfRepresentation':
        dims = {d: v[i] for i, d in enumerate(SelfDimension.ALL)}
        return SelfRepresentation(dimensions=dims)

    def distance_to(self, other: 'SelfRepresentation') -> float:
        """两个自我表征之间的欧氏距离。"""
        v1, v2 = self.vector, other.vector
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2))) / math.sqrt(len(v1))


@dataclass
class SoulState:
    """灵魂状态 — TCSC 不动点收敛结果。"""
    identity: SelfRepresentation
    convergence: float       # 收敛度 0-1 (1=完全收敛=不动点)
    stability: float         # 稳定性 0-1
    reflection_count: int    # 达到该状态所需的反思次数
    trace_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        if not self.trace_id:
            self.trace_id = uuid.uuid4().hex[:12]

    def to_dict(self) -> dict:
        return {
            "identity": self.identity.dimensions,
            "convergence": round(self.convergence, 4),
            "stability": round(self.stability, 4),
            "reflection_count": self.reflection_count,
            "trace_id": self.trace_id,
        }

    def describe(self) -> str:
        dims = self.identity.dimensions
        lines = [
            f"## 灵魂状态 (trace: {self.trace_id[:8]})",
            f"",
            f"### 自我表征",
        ]
        for dim, val in dims.items():
            bar = "█" * int(val * 20) + "░" * (20 - int(val * 20))
            lines.append(f"  {dim:<20} {bar} {val:.2f}")
        lines.extend([
            f"",
            f"**收敛度**: {self.convergence:.1%}",
            f"**稳定性**: {self.stability:.1%}",
            f"**反射次数**: {self.reflection_count}",
            f"状态: {'不动点已达成 ✓' if self.convergence > 0.99 else '收敛中...'}",
        ])
        return "\n".join(lines)


# ── 灵魂引擎 ──

class SoulEngine:
    """灵魂引擎 — TCSC 不动点计算核心。

    功能:
      1. 计算自我感知函数的不动点 (TCSC)
      2. 检测自我表征的稳定性
      3. 根据经验更新自我表征
      4. 灵魂觉醒检测 (convergence > threshold)
    """

    def __init__(self, convergence_threshold: float = 0.99,
                 max_reflections: int = 100):
        self.name = "soul"
        self._threshold = convergence_threshold
        self._max_reflections = max_reflections
        self._self_identity = SelfRepresentation()
        self._reflection_history: List[SelfRepresentation] = []

    # ── 自我感知函数 ──

    def self_perception(self, current: SelfRepresentation,
                        experience: Optional[Dict[str, float]] = None) -> SelfRepresentation:
        """自我感知函数 P(s, e)。

        给定当前自我表征 s 和新经验 e, 返回修正后的自我表征。

        数学形式:
          s'[i] = (1 - lr) * s[i] + lr * update(s[i], e)

        其中 lr 是学习率, update 根据经验调整每个维度。
        """
        lr = 0.1
        new_dims = dict(current.dimensions)
        experience = experience or {}

        for dim in SelfDimension.ALL:
            # 基线: 向中性值 (0.5) 适度回归 (防止极端化)
            new_dims[dim] = new_dims[dim] * 0.95 + 0.5 * 0.05

            # 经验驱动调整
            if dim in experience:
                delta = experience[dim] - new_dims[dim]
                new_dims[dim] += delta * lr

            # 非线性约束到 [0, 1]
            new_dims[dim] = 1.0 / (1.0 + math.exp(-6.0 * (new_dims[dim] - 0.5)))

        return SelfRepresentation(
            dimensions=new_dims,
            reflection_count=current.reflection_count + 1,
        )

    def pure_reflection(self, current: SelfRepresentation) -> SelfRepresentation:
        """纯自我反射 F(s) = P(s, Ø) — 无新经验下的自我调整。"""
        return self.self_perception(current)

    # ── 不动点迭代 ──

    def find_fixed_point(self, initial: Optional[SelfRepresentation] = None,
                         tolerance: float = 1e-4) -> SoulState:
        """通过迭代求不动点 s*: F(s*) = s*。

        算法: 不动点迭代
          s_{k+1} = F(s_k)
          直到 ||s_{k+1} - s_k|| < tolerance

        收敛条件: self_perception 是压缩映射 (Lipschitz 常数 < 1)
        """
        s = initial or SelfRepresentation()
        self._reflection_history = [s]

        for k in range(self._max_reflections):
            s_next = self.pure_reflection(s)
            dist = s.distance_to(s_next)
            self._reflection_history.append(s_next)

            convergence = 1.0 - min(dist / 0.1, 1.0)

            if dist < tolerance:
                # 不动点达成
                return SoulState(
                    identity=s_next,
                    convergence=1.0,
                    stability=1.0 - dist,
                    reflection_count=k + 1,
                )
            s = s_next

        # 未完全收敛, 返回当前最佳近似
        final = self._reflection_history[-1]
        final_dist = final.distance_to(self._reflection_history[-2]) if len(self._reflection_history) >= 2 else 1.0
        return SoulState(
            identity=final,
            convergence=1.0 - min(final_dist / 0.1, 1.0),
            stability=1.0 - min(final_dist, 1.0),
            reflection_count=self._max_reflections,
        )

    # ── 经验整合 ──

    def integrate_experience(self, experience: Dict[str, float]) -> SoulState:
        """整合新经验并重新计算不动点。"""
        self._self_identity = self.self_perception(self._self_identity, experience)
        return self.find_fixed_point(initial=self._self_identity)

    # ── 灵魂觉醒检测 ──

    def is_awake(self, state: Optional[SoulState] = None) -> bool:
        """灵魂是否觉醒: 收敛度 > 阈值。"""
        if state is None:
            state = self.find_fixed_point()
        return state.convergence >= self._threshold

    # ── 身份报告 ──

    def report(self) -> dict:
        state = self.find_fixed_point(initial=self._self_identity)
        return {
            "status": "ok",
            "soul": state.to_dict(),
            "awake": self.is_awake(state),
            "reflection_history": len(self._reflection_history),
        }

    def search(self, query: str, **kwargs) -> dict:
        return self.report()
