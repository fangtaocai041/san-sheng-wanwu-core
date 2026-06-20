"""
memory/consolidate.py — 记忆巩固系统 (嵌套记忆增强版 v2.0)

整合 MAGMA v2.0 嵌套记忆层级:
  - Hot (工作记忆): 当前 session, 半衰期 3 分钟
  - Warm (短期记忆): 跨 session, 半衰期 4 小时
  - Cold (长期记忆): 巩固后不遗忘, 半衰期 1 年

记忆巩固流程:
  Hot → Age-out (超时) → Warm → 巩固 (高频访问) → Cold

遗忘曲线 (每层配置不同半衰期):
  Hot:  R(t) = e^(-t * ln(2) / 0.05h)  — 快速衰减
  Warm: R(t) = e^(-t * ln(2) / 4h)     — 中等衰减
  Cold: R(t) = e^(-t * ln(2) / 8760h)  — 几乎不衰减

学术渊源:
  - Ebbinghaus 遗忘曲线 (1885): R(t) = e^(-t/S)
  - Google Nested Learning (NeurIPS 2025): 多速度更新
  - 突触可塑性 (Pitt 2025 Science Advances): 自发/诱发信号双通道
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import math
import time
import uuid

from .magma import MagmaMemory, MemoryNode, RelationType, MemoryTier, forgetting_curve


# ── 遗忘曲线 (v1 兼容) ──

def ebbinghaus_forgetting(hours_elapsed: float, strength: float = 1.0) -> float:
    """Ebbinghaus 遗忘曲线 (保留兼容).
    R(t) = e^(-t / S), S = 记忆强度"""
    return math.exp(-hours_elapsed / max(strength, 0.01))


def reinforcement_boost(repetitions: int) -> float:
    """重复强化提升强度。"""
    return 1.0 + math.log1p(repetitions)


# ── 按层遗忘曲线 ──

def tier_recall_probability(hours_elapsed: float, tier: str) -> float:
    """按记忆层级计算回忆概率。"""
    return forgetting_curve(hours_elapsed, MemoryTier.HALF_LIFE_HOURS[tier])


# ── 记忆系统 (MAGMA v2.0 增强) ──

@dataclass
class MemoryItem:
    """一条记忆 (API 与 v1 兼容)。"""
    id: str = ""
    content: str = ""
    memory_type: str = "stm"
    strength: float = 1.0
    access_count: int = 0
    last_access: float = 0.0
    created_at: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        now = time.time()
        if not self.id:
            self.id = uuid.uuid4().hex[:12]
        if not self.created_at:
            self.created_at = now
        if not self.last_access:
            self.last_access = now

    @property
    def age_hours(self) -> float:
        return (time.time() - self.created_at) / 3600

    @property
    def recall_probability(self) -> float:
        """回忆概率 (使用 Ebbinghaus, 兼容旧式)。"""
        return ebbinghaus_forgetting(self.age_hours, self.strength)

    @property
    def tier(self) -> str:
        """从 metadata 获取当前层级。"""
        return self.metadata.get("tier", MemoryTier.HOT)

    @property
    def tier_recall(self) -> float:
        """按层级遗忘曲线计算的回忆概率。"""
        return tier_recall_probability(self.age_hours, self.tier)

    @property
    def is_forgotten(self) -> bool:
        return self.recall_probability < 0.1

    def access(self):
        self.access_count += 1
        self.last_access = time.time()
        self.strength = reinforcement_boost(self.access_count)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "content": self.content[:100],
            "type": self.memory_type, "strength": round(self.strength, 2),
            "access_count": self.access_count,
            "recall": round(self.recall_probability, 3),
            "tier": self.tier,
            "age_hours": round(self.age_hours, 1),
            "forgotten": self.is_forgotten,
        }


class MemorySystem:
    """三层嵌套记忆系统 (MAGMA v2.0 增强版)。

    用法 (API 与 v1 兼容):
        mem = MemorySystem()
        mem.store("鳤是长江珍稀鱼类", entities=["鳤", "Ochetobius elongatus"])
        results = mem.recall("长江鱼类的保护")
    """

    def __init__(self, consolidation_threshold: int = 3,
                 stm_capacity: int = 100, wm_capacity: int = 10):
        # MAGMA v2.0 嵌套层级记忆 (核心)
        self._magma = MagmaMemory()

        # 工作记忆 (旧接口兼容)
        self.working: Dict[str, Any] = {}
        self._wm_capacity = wm_capacity

        # 短期/长期记忆 (旧接口兼容)
        self._stm: List[MemoryItem] = []
        self._ltm: List[MemoryItem] = []
        self._stm_capacity = stm_capacity
        self._consolidation_threshold = consolidation_threshold

    # ── 存储 (MAGMA v2.0 增强) ──

    def store(self, content: str, entities: Optional[List[str]] = None,
              metadata: Optional[Dict] = None,
              memory_type: str = "stm") -> MemoryItem:
        """存储一条新记忆。默认写入 Hot 层。"""
        # 确定写入层级
        tier = MemoryTier.HOT if memory_type == "stm" else MemoryTier.COLD

        # 写入 MAGMA v2.0 嵌套层级
        node = self._magma.add(content, entities=entities,
                              metadata={**(metadata or {}), "tier": tier},
                              tier=tier)

        # 写入 STM/LTM 列表 (旧接口兼容)
        item = MemoryItem(
            id=node.node_id, content=content, memory_type=memory_type,
            metadata={**(metadata or {}), "tier": tier, "magma_node_id": node.node_id},
        )
        if memory_type == "ltm":
            self._ltm.append(item)
        else:
            self._stm.append(item)
            if len(self._stm) > self._stm_capacity:
                self._stm.sort(key=lambda x: x.recall_probability)
                self._stm.pop(0)

        return item

    def set_working(self, key: str, value: Any):
        self.working[key] = value
        if len(self.working) > self._wm_capacity:
            oldest = next(iter(self.working))
            del self.working[oldest]

    def get_working(self, key: str, default=None) -> Any:
        return self.working.get(key, default)

    # ── 检索 (MAGMA v2.0 多层级) ──

    def recall(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        """从所有层级检索记忆。

        使用 MAGMA v2.0 多层级选择性图遍历。
        """
        # 1. MAGMA 多层级检索
        magma_nodes = self._magma.search(query, top_k=top_k)

        # 2. 映射回 MemoryItem + 旧版关键词补充
        seen = set()
        fused = []

        for node in magma_nodes:
            item = self._find_item(node.node_id)
            if item:
                if not item.is_forgotten:
                    item.access()
                    fused.append(item)
                    seen.add(item.id)

        # 3. 旧版关键词补充
        q = query.lower()
        for item in self._stm + self._ltm:
            if item.id not in seen and not item.is_forgotten:
                if q in item.content.lower():
                    item.access()
                    fused.append(item)
                    seen.add(item.id)

        return fused[:top_k]

    def _find_item(self, node_id: str) -> Optional[MemoryItem]:
        for item in self._stm + self._ltm:
            if item.id == node_id:
                return item
        return None

    def recall_by_type(self, memory_type: str, top_k: int = 10) -> List[MemoryItem]:
        pool = self._stm if memory_type == "stm" else self._ltm
        items = [m for m in pool if not m.is_forgotten]
        items.sort(key=lambda x: x.recall_probability, reverse=True)
        return items[:top_k]

    # ── 巩固 ──

    def age_out(self) -> Dict[str, int]:
        """将超时的 Hot 记忆降级到 Warm (MAGMA v2.0 自动管理)。"""
        promoted = self._magma.age_out_hot()

        # 同步 STM 列表中的层级标记
        updated = 0
        for item in self._stm:
            if item.tier == MemoryTier.HOT:
                item.metadata["tier"] = MemoryTier.WARM
                updated += 1

        return {"hot_to_warm": promoted, "stm_tier_updated": updated}

    def consolidate(self) -> Dict[str, int]:
        """记忆巩固: Hot → Warm → Cold 升级。

        巩固条件:
          - Hot 层超时 → 自动降级为 Warm (通过 age_out)
          - Warm 层访问频次 ≥ threshold → 提升为 Cold
        """
        # 1. Hot → Warm 超时降级
        age_out_result = self.age_out()

        # 2. Warm → Cold 高频巩固
        promoted = 0
        remaining_stm = []
        for item in self._stm:
            if item.is_forgotten:
                continue
            if item.access_count >= self._consolidation_threshold:
                item.memory_type = "ltm"
                item.metadata["tier"] = MemoryTier.COLD
                self._ltm.append(item)
                # 同时在 MAGMA 中提升
                self._magma.promote(item.id, MemoryTier.WARM, MemoryTier.COLD)
                promoted += 1
            else:
                remaining_stm.append(item)
        self._stm = remaining_stm

        return {
            "hot_to_warm": age_out_result["hot_to_warm"],
            "warm_to_cold": promoted,
            "stm_count": len(self._stm),
            "ltm_count": len(self._ltm),
            "magma": self._magma.stats(),
        }

    # ── 统计 ──

    def stats(self) -> dict:
        return {
            "working_count": len(self.working),
            "stm_count": len(self._stm),
            "ltm_count": len(self._ltm),
            "magma": self._magma.stats(),
        }

    def forget(self, item_id: str) -> bool:
        for pool in [self._stm, self._ltm]:
            for i, item in enumerate(pool):
                if item.id == item_id:
                    pool.pop(i)
                    return True
        return False

    def clear_working(self):
        self.working.clear()

    def search(self, query: str, **kwargs) -> dict:
        results = self.recall(query)
        return {
            "status": "ok",
            "results": [r.to_dict() for r in results],
            "total": len(results),
            "method": "magma_v2_nested_tiers",
        }
