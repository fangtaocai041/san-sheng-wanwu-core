"""
cortex/transposition.py — 概念转座层 (Conceptual Transposition Layer)

受生物学跳跃基因 (Transposable Elements) 启发，将 TE 的核心逻辑原则
映射为认知架构中的信息流动机制。

生物学原理 → 架构映射:
  转座 (Transposition)         概念/推理模式在知识域之间复制移动
  驯化 (Exaptation)            跨域复用成功 → 固化为新路由专家
  压力激活 (Stress Activation) 不确定性/矛盾升高 → 转座速率上调
  Arc 病毒样包装              高置信推理链 → Agent 间知识胶囊
  顺式调控重写                新概念插入 → 局部图谱重连

学术来源:
  - Arc 基因: Current Opinion in Neurobiology (2025) — 驯化的逆转录转座子
  - TE 与记忆: Mustafin (2025) Russian J. Genetics — 17 种 TE 衍生 miRNA
  - 压力诱导 TE: Aging/neurodegeneration 研究 (2025-2026)
  - 驯化调控: Chuong et al. (2017) Nat. Rev. Genet. — TE → 调控元件

用法:
    tl = TranspositionLayer()
    tl.set_stress_level(uncertainty=0.7, confusion=0.6)
    event = tl.transpose(
        source_domain="biology",
        target_domain="economics",
        pattern={"concept": "种群承载力", "inference": "logistic_growth"}
    )
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
import time
import uuid


# ── 数据结构 ──

@dataclass
class TranspositionEvent:
    """一次概念转座事件的记录。"""
    event_id: str = ""
    source_domain: str = ""
    target_domain: str = ""
    pattern_type: str = ""      # concept | inference | strategy
    pattern_summary: str = ""
    success: bool = False
    fitness_delta: float = 0.0  # 转座后性能变化 (-1 ~ 1)
    domesticated: bool = False  # 是否被驯化
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.event_id:
            self.event_id = uuid.uuid4().hex[:12]
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class DomesticatedPattern:
    """被驯化的跨域模式 — 已固化为稳定路由路径。"""
    pattern_id: str = ""
    source_domain: str = ""
    target_domain: str = ""
    pattern_type: str = ""
    success_count: int = 0
    avg_fitness_delta: float = 0.0
    first_domesticated: float = 0.0
    last_used: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ── 拓扑连接矩阵 (与 domains.py 互操作) ──

# 默认 12 学科间转座倾向性 [0, 1]
# 值越高表示两个域之间越容易发生转座
DEFAULT_TRANSPOSITION_BIAS: Dict[str, Dict[str, float]] = {
    "biology":           {"ecology": 0.9, "conservation": 0.8, "chemistry": 0.5,
                          "psychology": 0.4, "economics": 0.3, "cs": 0.2},
    "ecology":           {"biology": 0.9, "conservation": 0.8, "geography": 0.7,
                          "economics": 0.4, "cs": 0.2},
    "conservation":      {"biology": 0.8, "ecology": 0.8, "economics": 0.6,
                          "geography": 0.5},
    "economics":         {"conservation": 0.6, "ecology": 0.4, "cs": 0.4,
                          "biology": 0.3, "psychology": 0.3},
    "cs":                {"math": 0.8, "physics": 0.5, "biology": 0.2,
                          "psychology": 0.4, "economics": 0.4},
    "physics":           {"math": 0.8, "cs": 0.5, "chemistry": 0.6,
                          "scifi": 0.3},
    "chemistry":         {"physics": 0.6, "biology": 0.5, "cs": 0.2},
    "psychology":        {"biology": 0.4, "cs": 0.4, "philosophy": 0.5,
                          "economics": 0.3, "literature": 0.3},
    "philosophy":        {"psychology": 0.5, "cs": 0.3, "physics": 0.4,
                          "literature": 0.4, "chinese_philosophy": 0.7},
    "chinese_philosophy":{"philosophy": 0.7, "literature": 0.5, "biology": 0.2},
    "literature":        {"philosophy": 0.4, "scifi": 0.5, "psychology": 0.3,
                          "chinese_philosophy": 0.5},
    "scifi":             {"literature": 0.5, "cs": 0.4, "physics": 0.3,
                          "biology": 0.3},
}


# ── 转座层引擎 ──

class TranspositionLayer:
    """概念转座层 — 跳跃基因逻辑的认知架构实现。

    核心功能:
      1. 跨域转座: 将推理模式/概念从一个知识域复制到另一个
      2. 压力调控: 不确定性/困惑度升高 → 转座活性上调
      3. 驯化追踪: 成功复用的跨域模式 → 固化为稳定路由
      4. 适应性评估: 每次转座后评估适应性变化

    使用方式:
        tl = TranspositionLayer()
        tl.set_stress_level(uncertainty=0.7, confusion=0.5)

        # 单次转座 — 将一个域的搜索策略复制到相关域
        event = tl.transpose("biology", "conservation",
                            {"concept": "种群瓶颈效应", "confidence": 0.85})

        # 获取当前活性 (用于情感系统回调)
        activity = tl.current_activity

        # 查询已验证的跨域通路
        pathways = tl.get_domesticated_pathways()
    """

    def __init__(self, base_activity: float = 0.3,
                 domestication_threshold: int = 3):
        self.name = "transposition"
        self._base_activity = base_activity       # 基础转座活性
        self._stress_boost: float = 0.0           # 压力提升的活性
        self._domestication_threshold = domestication_threshold  # 驯化所需成功次数

        # 事件记录
        self._events: List[TranspositionEvent] = []
        self._domesticated: Dict[str, DomesticatedPattern] = {}

        # 近期表现追踪 (用于适应性评估)
        self._recent_fitness: List[float] = []

    # ── 压力调控 (与 emotion.py 集成) ──

    def set_stress_level(self, uncertainty: float = 0.0,
                         confusion: float = 0.0) -> float:
        """根据认知压力水平调节转座活性。

        对应生物学: 应激状态下 TEs 的抑制被放松,
        允许更多重组以寻找适应性解决方案。

        Args:
            uncertainty: emotion["uncertainty"] 0-1
            confusion: emotion["confusion"] 0-1

        Returns:
            当前转座活性 (0-1)
        """
        self._stress_boost = (uncertainty * 0.5 + confusion * 0.5) * 0.5
        return self.current_activity

    @property
    def current_activity(self) -> float:
        """当前转座活性 = 基础活性 + 压力提升 (上限 0.95)。"""
        return min(0.95, self._base_activity + self._stress_boost)

    @property
    def is_hyperactive(self) -> bool:
        """是否处于高活性状态 (>0.8)。"""
        return self.current_activity > 0.8

    # ── 跨域转座 ──

    def transpose(self, source_domain: str, target_domain: str,
                  pattern: Dict[str, Any]) -> TranspositionEvent:
        """将推理模式/概念从一个域转座到另一个域。

        对应生物学: 逆转录转座子的 copy-and-paste 机制。
        原模式保留 (copy), 新副本插入目标域 (paste)。

        Args:
            source_domain: 源知识域
            target_domain: 目标知识域
            pattern: 要转座的模式 {concept, inference, confidence, ...}

        Returns:
            TranspositionEvent 记录
        """
        # 1. 检查转座倾向性
        bias = self._get_transposition_bias(source_domain, target_domain)
        if bias <= 0:
            return TranspositionEvent(
                source_domain=source_domain, target_domain=target_domain,
                pattern_type=pattern.get("type", "concept"),
                pattern_summary=str(pattern.get("concept", ""))[:80],
                success=False, fitness_delta=-0.5,
            )

        # 2. 活性概率: 转座是否实际发生
        activity = self.current_activity
        if activity < 0.1:
            # 活性太低, 跳过转座
            return TranspositionEvent(
                source_domain=source_domain, target_domain=target_domain,
                pattern_type=pattern.get("type", "concept"),
                pattern_summary=str(pattern.get("concept", ""))[:80],
                success=False, fitness_delta=0.0,
            )

        # 3. 成功概率 = 偏置 × 活性 × 模式置信度
        pattern_confidence = pattern.get("confidence", 0.5)
        success_prob = bias * activity * pattern_confidence

        # 模拟转座结果
        import random
        success = random.random() < success_prob

        # 适应性变化: 成功时正向, 失败时负向但小
        fitness_delta = (random.random() * 0.3 + 0.1
                        if success
                        else -(random.random() * 0.2))

        event = TranspositionEvent(
            source_domain=source_domain,
            target_domain=target_domain,
            pattern_type=pattern.get("type", "concept"),
            pattern_summary=str(pattern.get("concept", ""))[:80],
            success=success,
            fitness_delta=round(fitness_delta, 4),
        )

        self._events.append(event)
        self._recent_fitness.append(fitness_delta)

        # 4. 驯化检测: 如果同一模式多次成功转座
        if success:
            self._check_domestication(event)

        return event

    def _get_transposition_bias(self, source: str, target: str) -> float:
        """获取域间转座倾向性。"""
        row = DEFAULT_TRANSPOSITION_BIAS.get(source, {})
        bias = row.get(target, 0.0)
        if bias == 0.0:
            # 尝试反向
            row = DEFAULT_TRANSPOSITION_BIAS.get(target, {})
            bias = row.get(source, 0.0)
        return bias

    # ── 驯化追踪 ──

    def _check_domestication(self, event: TranspositionEvent):
        """检查是否需要驯化 —— 同一模式成功转座达到阈值后固化为稳定路由。

        对应生物学: TE 序列被宿主"驯化"为功能性调控元件的过程。
        """
        key = f"{event.source_domain}→{event.target_domain}:{event.pattern_type}"

        if key in self._domesticated:
            dp = self._domesticated[key]
            dp.success_count += 1
            dp.last_used = time.time()
            dp.avg_fitness_delta = (
                (dp.avg_fitness_delta * (dp.success_count - 1) + event.fitness_delta)
                / dp.success_count
            )
            if dp.success_count >= self._domestication_threshold:
                event.domesticated = True
        else:
            self._domesticated[key] = DomesticatedPattern(
                pattern_id=key,
                source_domain=event.source_domain,
                target_domain=event.target_domain,
                pattern_type=event.pattern_type,
                success_count=1,
                avg_fitness_delta=event.fitness_delta,
                first_domesticated=time.time(),
                last_used=time.time(),
            )

    def get_domesticated_pathways(self) -> List[DomesticatedPattern]:
        """获取所有已驯化的跨域通路。"""
        return list(self._domesticated.values())

    def is_domesticated(self, source: str, target: str,
                        pattern_type: str = "concept") -> bool:
        """检查指定跨域通路是否已被驯化。"""
        key = f"{source}→{target}:{pattern_type}"
        dp = self._domesticated.get(key)
        return dp is not None and dp.success_count >= self._domestication_threshold

    # ── Arc 样知识封装 (与 swarm.py 集成) ──

    def package_knowledge(self, reasoning_chain: List[Dict[str, Any]],
                          confidence: float = 0.8) -> Dict[str, Any]:
        """将高置信推理链封装为可移植的知识胶囊。

        对应生物学: Arc 基因形成病毒样外壳包裹 mRNA 在神经元间运输。

        Args:
            reasoning_chain: 推理链步骤列表
            confidence: 整体置信度

        Returns:
            封装后的知识胶囊
        """
        return {
            "capsule_id": uuid.uuid4().hex[:12],
            "type": "reasoning_capsule",
            "content": reasoning_chain,
            "confidence": confidence,
            "timestamp": time.time(),
            "origin": self.name,
        }

    def unpack_knowledge(self, capsule: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解包知识胶囊。"""
        if capsule.get("type") != "reasoning_capsule":
            return []
        return capsule.get("content", [])

    # ── 报告与统计 ──

    @property
    def total_transpositions(self) -> int:
        return len(self._events)

    @property
    def success_rate(self) -> float:
        if not self._events:
            return 0.0
        return sum(1 for e in self._events if e.success) / len(self._events)

    @property
    def domestication_rate(self) -> float:
        """驯化率 = 已驯化模式 / 总尝试的唯一模式数。"""
        if not self._domesticated:
            return 0.0
        domesticated_count = sum(
            1 for dp in self._domesticated.values()
            if dp.success_count >= self._domestication_threshold
        )
        return domesticated_count / max(len(self._domesticated), 1)

    def report(self) -> dict:
        return {
            "status": "ok",
            "activity": round(self.current_activity, 3),
            "stress_boost": round(self._stress_boost, 3),
            "hyperactive": self.is_hyperactive,
            "total_transpositions": self.total_transpositions,
            "success_rate": round(self.success_rate, 3),
            "domesticated_pathways": len(self._domesticated),
            "domestication_rate": round(self.domestication_rate, 3),
            "recent_events": [
                {"source": e.source_domain, "target": e.target_domain,
                 "success": e.success, "fitness": e.fitness_delta,
                 "domesticated": e.domesticated}
                for e in self._events[-5:]
            ],
        }

    def search(self, query: str, **kwargs) -> dict:
        return self.report()
