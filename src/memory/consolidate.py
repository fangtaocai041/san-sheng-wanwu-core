"""
memory/consolidate.py — 记忆巩固系统 (MAGMA 增强版)

整合 MAGMA 四维正交图谱记忆:
  - 写入时自动建立四维关系 (语义/时序/因果/实体)
  - 检索 = 策略引导图遍历 (非纯关键词匹配)
  - 保留原有的 Ebbinghaus 遗忘曲线和三层架构

三层记忆架构:
  工作记忆 (WM)  — Dict 上下文
  短期记忆 (STM) — 图谱节点, Ebbinghaus 衰减
  长期记忆 (LTM) — 图谱节点, 巩固后不遗忘

MAGMA 升级:
  consolidate.py 的 recall() 使用 MagmaMemory.search() 进行图遍历检索,
  而非简单的关键词匹配。大幅提升多跳推理和长上下文检索能力。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import math
import time
import uuid

from .magma import MagmaMemory, MemoryNode, RelationType


# ── 遗忘曲线 (保留) ──

def ebbinghaus_forgetting(hours_elapsed: float, strength: float = 1.0) -> float:
    """Ebbinghaus 遗忘曲线。
    R(t) = e^(-t / S), S = 记忆强度"""
    return math.exp(-hours_elapsed / max(strength, 0.01))


def reinforcement_boost(repetitions: int) -> float:
    """重复强化提升强度。"""
    return 1.0 + math.log1p(repetitions)


# ── 记忆系统 (MAGMA 增强) ──

@dataclass
class MemoryItem:
    """一条记忆 (兼容旧接口)。"""
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
        return ebbinghaus_forgetting(self.age_hours, self.strength)

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
            "age_hours": round(self.age_hours, 1),
            "forgotten": self.is_forgotten,
        }


class MemorySystem:
    """三层记忆系统 (MAGMA 增强版)。

    用法:
        mem = MemorySystem()
        mem.store("鳤是长江珍稀鱼类", entities=["鳤", "Ochetobius elongatus"])
        results = mem.recall("长江鱼类的保护")  # 使用四维图遍历
    """

    def __init__(self, consolidation_threshold: int = 3,
                 stm_capacity: int = 100, wm_capacity: int = 10):
        # MAGMA 四维图谱记忆 (核心)
        self._magma = MagmaMemory()

        # 工作记忆
        self.working: Dict[str, Any] = {}
        self._wm_capacity = wm_capacity

        # 短期/长期记忆 (保留以兼容旧接口)
        self._stm: List[MemoryItem] = []
        self._ltm: List[MemoryItem] = []
        self._stm_capacity = stm_capacity
        self._consolidation_threshold = consolidation_threshold

    # ── 存储 (MAGMA 增强) ──

    def store(self, content: str, entities: Optional[List[str]] = None,
              metadata: Optional[Dict] = None,
              memory_type: str = "stm") -> MemoryItem:
        """存储一条新记忆。同时写入 MAGMA 图谱和 STM 列表。"""
        # 写入 MAGMA 四维图谱
        node = self._magma.add(content, entities=entities, metadata=metadata)

        # 写入 STM 列表 (兼容旧接口)
        item = MemoryItem(
            id=node.node_id, content=content, memory_type=memory_type,
            metadata={**(metadata or {}), "magma_node_id": node.node_id},
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

    # ── 检索 (MAGMA 图遍历替代关键词匹配) ──

    def recall(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        """从所有层检索记忆。

        使用 MAGMA 四维图遍历 (非旧版关键词匹配)。
        同时检索图谱节点和 STM/LTM 列表,
        用 RRF 融合排序。
        """
        # 1. MAGMA 图遍历检索
        magma_nodes = self._magma.search(query, top_k=top_k)

        # 2. 将图谱节点映射回 MemoryItem
        magma_results = []
        for node in magma_nodes:
            item = self._find_item(node.node_id)
            if item and item.is_forgotten:
                continue
            if item:
                item.access()
                magma_results.append(item)

        # 3. 旧版关键词匹配 (作为补充)
        q = query.lower()
        keyword_results = []
        for item in self._stm + self._ltm:
            if item.is_forgotten:
                continue
            if q in item.content.lower():
                item.access()
                keyword_results.append(item)

        # 4. 融合: 图遍历优先, 关键词补充
        seen = set()
        fused = []
        for item in magma_results + keyword_results:
            if item.id not in seen:
                fused.append(item)
                seen.add(item.id)

        return fused[:top_k]

    def _find_item(self, node_id: str) -> Optional[MemoryItem]:
        """按 node_id 查找 MemoryItem。"""
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

    def consolidate(self) -> Dict[str, int]:
        """记忆巩固: STM → LTM。"""
        promoted = 0
        remaining_stm = []
        for item in self._stm:
            if item.is_forgotten:
                continue
            if item.access_count >= self._consolidation_threshold:
                item.memory_type = "ltm"
                self._ltm.append(item)
                promoted += 1
            else:
                remaining_stm.append(item)
        self._stm = remaining_stm

        return {
            "stm_to_ltm": promoted,
            "stm_count": len(self._stm),
            "ltm_count": len(self._ltm),
            "magma_nodes": self._magma.node_count,
            "magma_edges": self._magma.edge_count,
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
            "method": "magma_4d_graph_traversal",
        }
