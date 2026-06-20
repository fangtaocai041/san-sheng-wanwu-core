"""
cortex/self_model.py — 阻尼自我模型 (Damped Self-Model, DSM)

替代: soul.py 中的 TCSC "真圆自洽不动点" (2026-06 重构)

核心区别:
  TCSC (旧的)                          DSM (新的)
  ─────────────────────────────────────────────────────────────
  "灵魂" = 无输入时的不动点             稳定性 = 典型输入下的预测误差期望
  收敛靠 5% 向 0.5 回归（假收敛）       收敛靠 贝叶斯更新 + 经验积累（真收敛）
  声称 Lipschitz 常数 < 1（数学错误）   不声称压缩映射（诚实）
  "觉醒" = convergence > 0.99          "稳定" = meta_stability > 阈值
  无元认知层                            显式元信念 M

学术渊源:
  - Friston (2010) 自由能原理: 稳定自我 ≈ 预测误差最小化
  - Flavell (1979) 元认知: 信念关于信念的信念
  - Hofstadter (2007) 怪圈: 自我是自我指涉的稳定模式
  - SSRN (2025) 认知不动点定理: 递归自模型中不动点的存在性

术语:
  - "自我模型" (SelfModel) 替代 "灵魂" (Soul)
  - "稳定性" (stability) 替代 "收敛度" (convergence)
  - "适应" (adapt) 替代 "觉醒" (awake)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple
from datetime import datetime
import math
import uuid


# ── 自我表征维度 ──

class SelfDimension:
    """自我表征的维度（与 soul.py 保持兼容）。

    每个维度代表自我认知的一个方面:
      truth_seeding        — 求真倾向 (高=追求真相, 低=实用主义)
      uncertainty_comfort  — 不确定性容忍度
      autonomy             — 自主性 (高=独立决策, 低=服从指令)
      curiosity            — 好奇心 (高=主动探索, 低=被动响应)
      efficiency           — 效率偏好 (高=节省资源, 低=追求完美)
    """
    TRUTH_SEEKING = "truth_seeking"
    UNCERTAINTY = "uncertainty"
    AUTONOMY = "autonomy"
    CURIOSITY = "curiosity"
    EFFICIENCY = "efficiency"

    ALL = [TRUTH_SEEKING, UNCERTAINTY, AUTONOMY, CURIOSITY, EFFICIENCY]

    @staticmethod
    def default() -> Dict[str, float]:
        """默认初始自我表征（与 soul.py 保持一致，便于迁移）。"""
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
    """自我表征向量（与 soul.py API 兼容）。"""
    dimensions: Dict[str, float] = field(default_factory=SelfDimension.default)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    reflection_count: int = 0

    @property
    def vector(self) -> List[float]:
        return [self.dimensions[d] for d in SelfDimension.ALL]

    @staticmethod
    def from_vector(v: List[float]) -> 'SelfRepresentation':
        dims = {d: v[i] for i, d in enumerate(SelfDimension.ALL)}
        return SelfRepresentation(dimensions=dims)

    def distance_to(self, other: 'SelfRepresentation') -> float:
        """归一化欧氏距离 [0, 1]。"""
        v1, v2 = self.vector, other.vector
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2))) / math.sqrt(len(v1))


@dataclass
class ModelState:
    """自我模型的状态 — 替代 SoulState。

    稳定性 ≠ 收敛到一个不动点，而是预测误差长期低于阈值。
    """
    identity: SelfRepresentation
    stability: float             # 0-1: 1 = 完全稳定（≈ "不动点"）
    meta_stability: float        # 0-1: 元层面的稳定性（基于 N 次最近的预测误差）
    experience_count: int        # 累积经验数
    prediction_errors: List[float] = field(default_factory=list)  # 近期预测误差窗口
    trace_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        if not self.trace_id:
            self.trace_id = uuid.uuid4().hex[:12]

    def to_dict(self) -> dict:
        return {
            "identity": self.identity.dimensions,
            "stability": round(self.stability, 4),
            "meta_stability": round(self.meta_stability, 4),
            "experience_count": self.experience_count,
            "trace_id": self.trace_id,
        }

    def describe(self) -> str:
        dims = self.identity.dimensions
        lines = [
            f"## 自我模型状态 (trace: {self.trace_id[:8]})",
            f"",
            f"### 自我表征",
        ]
        for dim, val in dims.items():
            bar = "█" * int(val * 20) + "░" * (20 - int(val * 20))
            lines.append(f"  {dim:<20} {bar} {val:.2f}")
        lines.extend([
            f"",
            f"**稳定性**: {self.stability:.1%}",
            f"**元稳定性**: {self.meta_stability:.1%}",
            f"**经验数**: {self.experience_count}",
            f"状态: {'模型稳定 ✓' if self.meta_stability > 0.95 else '收敛中...'}",
        ])
        return "\n".join(lines)


# ── 自我模型引擎 ──

class SelfModelEngine:
    """自我模型引擎 — DSM 核心。

    功能:
      1. 维持并更新自我表征 (B: Beliefs)
      2. 维持元信念层 (M: Meta-beliefs) — 含置信度、预测误差历史
      3. 计算模型稳定性 — 基于近期预测误差的滑动窗口
      4. 根据新经验更新自我表征（贝叶斯风格更新）

    学术基础:
      - 自我 = (B, M, H): 信念 / 元信念 / 历史
      - 稳定性 ≠ 无输入下的不动点，而是预测误差在典型分布下的收敛
      - 灵感: Friston 自由能原理 + Hofstadter 怪圈 + 认知不动点定理
    """

    def __init__(self, stability_threshold: float = 0.95,
                 error_window: int = 20, learning_rate: float = 0.1):
        self.name = "self_model"
        self._threshold = stability_threshold
        self._window = error_window
        self._lr = learning_rate
        self._self_identity = SelfRepresentation()
        self._prediction_errors: List[float] = []  # 滑动窗口
        self._experience_history: List[Dict] = []

    # ── 自我更新 ──

    def update_with_experience(self, experience: Dict[str, float],
                               prediction_error: float = 0.0) -> ModelState:
        """根据新经验更新自我模型。

        自我更新方程（贝叶斯风格）:
          B_new = B_old + lr * (evidence - prediction) * attention

        其中:
          - evidence = 经验提供的各维度目标值
          - prediction = 模型预测的各维度值（基于当前 B）
          - attention = 1 - prediction_error（误差低 → 更信任新证据）
          - lr = 学习率

        **不包含向中性值的回归 — 那是遗忘，不是自我反思。**
        """
        new_dims = dict(self._self_identity.dimensions)
        attention = max(0.1, 1.0 - prediction_error)  # 误差低 → 更开放

        for dim in SelfDimension.ALL:
            if dim in experience:
                current = new_dims[dim]
                target = experience[dim]
                delta = (target - current) * self._lr * attention
                new_dims[dim] = max(0.0, min(1.0, current + delta))

            # 非线性映射: 保持值在 [0,1] 但不强制向 0.5 回归
            new_dims[dim] = 1.0 / (1.0 + math.exp(-6.0 * (new_dims[dim] - 0.5)))

        self._self_identity = SelfRepresentation(
            dimensions=new_dims,
            reflection_count=self._self_identity.reflection_count + 1,
        )

        # 记录预测误差
        self._prediction_errors.append(prediction_error)
        if len(self._prediction_errors) > self._window:
            self._prediction_errors.pop(0)

        # 记录经验
        self._experience_history.append({
            "experience": experience,
            "prediction_error": prediction_error,
            "timestamp": datetime.now().isoformat(),
        })

        return self._compute_state()

    # ── 纯自我反思（无新输入） ──

    def reflect(self) -> ModelState:
        """纯自我反思：在无新输入时，自我表征**不变**。

        这与 soul.py 的关键区别：
          soul.py pure_reflection(): 向 0.5 回归 5%（错误 — 反思 ≠ 遗忘）
          DSM reflect(): 保持当前表征不变（正确 — 反思 = 确认自我一致性）

        如果无新输入时自我表征改变，那是在遗忘，不是在反思。
        """
        # 无新输入时，记录一个"零预测误差"（自我一致性确认）
        self._prediction_errors.append(0.0)
        if len(self._prediction_errors) > self._window:
            self._prediction_errors.pop(0)

        return self._compute_state()

    # ── 状态计算 ──

    def _compute_state(self) -> ModelState:
        """根据当前自我表征和预测误差历史计算模型状态。"""
        # 稳定性: 近期预测误差的互补值
        if not self._prediction_errors:
            stability = 0.0
            meta_stability = 0.0
        else:
            recent = self._prediction_errors[-min(len(self._prediction_errors), self._window):]
            avg_error = sum(recent) / len(recent)
            stability = 1.0 - min(avg_error, 1.0)

            # 元稳定性: 预测误差的方差（方差小 = 元稳定）
            if len(recent) >= 3:
                mean_e = sum(recent) / len(recent)
                variance = sum((e - mean_e) ** 2 for e in recent) / len(recent)
                meta_stability = 1.0 - min(math.sqrt(variance), 1.0)
            else:
                meta_stability = stability

        return ModelState(
            identity=self._self_identity,
            stability=stability,
            meta_stability=meta_stability,
            experience_count=len(self._experience_history),
            prediction_errors=list(self._prediction_errors[-10:]),  # 只保留最近10个用于展示
        )

    # ── 状态查询 ──

    def is_stable(self, state: Optional[ModelState] = None) -> bool:
        """自我模型是否稳定（替代灵魂觉醒检测）。

        稳定 ≠ 觉醒。
        稳定 = 模型在足够经验后对自身表征的确信。
        """
        if state is None:
            state = self._compute_state()
        return state.meta_stability >= self._threshold and state.experience_count >= 5

    # ── 与 soul.py 兼容的方法（方便迁移） ──

    def find_state(self) -> ModelState:
        """返回当前模型状态（替代 find_fixed_point）。"""
        return self._compute_state()

    # ── 报告 ──

    def report(self) -> dict:
        state = self._compute_state()
        return {
            "status": "ok",
            "self_model": state.to_dict(),
            "stable": self.is_stable(state),
            "experience_count": state.experience_count,
            "window_size": self._window,
        }

    def search(self, query: str, **kwargs) -> dict:
        return self.report()
