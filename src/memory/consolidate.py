"""
memory/consolidate.py — 记忆巩固系统

三层记忆架构:
  工作记忆 (WM)  — 当前上下文, 活跃推理状态, 易失
  短期记忆 (STM) — 近期查询与结果, 衰减曲线
  长期记忆 (LTM) — 巩固后的知识, 半永久存储

巩固过程:
  1. 工作记忆中的模式被重复激活 → 进入短期记忆
  2. 短期记忆中的模式被强化 ≥ consolidation_threshold 次 → 进入长期记忆
  3. 未被强化的短期记忆按 Ebbinghaus 遗忘曲线衰减

遗忘曲线: R(t) = e^(-t/S) 其中 S = 记忆强度
  R = 1.0 时完全记住, R → 0 时完全遗忘
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math
import time
import uuid


# ── 遗忘曲线 ──

def ebbinghaus_forgetting(hours_elapsed: float, strength: float = 1.0) -> float:
    """Ebbinghaus 遗忘曲线。

    R(t) = e^(-t / S)
      R = 回忆率 (0-1)
      t = 经过时间 (小时)
      S = 记忆强度 (小时)
    
    强度越大, 遗忘越慢。
    """
    return math.exp(-hours_elapsed / max(strength, 0.01))


def reinforcement_boost(repetitions: int) -> float:
    """重复强化对记忆强度的提升。

    每次重复增加 S, 但收益递减:
    S = base * (1 + log(1 + repetitions))
    """
    return 1.0 + math.log1p(repetitions)


# ── 记忆条 ──

@dataclass
class MemoryItem:
    """一条记忆。"""
    id: str = ""
    content: str = ""           # 记忆内容
    memory_type: str = "stm"    # wm | stm | ltm
    strength: float = 1.0        # 记忆强度 (小时)
    access_count: int = 0        # 访问次数
    last_access: float = 0.0     # 最后访问时间戳
    created_at: float = 0.0      # 创建时间戳
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
        """基于遗忘曲线的回忆概率。"""
        return ebbinghaus_forgetting(self.age_hours, self.strength)

    @property
    def is_forgotten(self) -> bool:
        """是否已遗忘 (recall < 0.1)。"""
        return self.recall_probability < 0.1

    def access(self):
        """访问记忆, 强化强度。"""
        self.access_count += 1
        self.last_access = time.time()
        self.strength = reinforcement_boost(self.access_count)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content[:100],
            "type": self.memory_type,
            "strength": round(self.strength, 2),
            "access_count": self.access_count,
            "recall": round(self.recall_probability, 3),
            "age_hours": round(self.age_hours, 1),
            "forgotten": self.is_forgotten,
        }


# ── 记忆系统 ──

class MemorySystem:
    """三层记忆系统。

    用法:
        mem = MemorySystem()
        mem.working.set("current_query", "鳤")          # 工作记忆
        mem.store("查询结果: 鳤是长江珍稀鱼类")             # → STM
        mem.consolidate()                                # 巩固: STM→LTM
        results = mem.recall("鳤")                       # 搜索所有层
    """

    def __init__(self, consolidation_threshold: int = 3,
                 stm_capacity: int = 100,
                 wm_capacity: int = 10):
        # 工作记忆: 当前上下文 (Dict)
        self.working: Dict[str, Any] = {}

        # 短期记忆: 列表 + 容量限制
        self._stm: List[MemoryItem] = []
        self._stm_capacity = stm_capacity

        # 长期记忆: 列表 (理论上可持久化到 DB)
        self._ltm: List[MemoryItem] = []

        self._consolidation_threshold = consolidation_threshold
        self._wm_capacity = wm_capacity

    # ── 存储 ──

    def store(self, content: str, metadata: Optional[Dict] = None,
              memory_type: str = "stm") -> MemoryItem:
        """存储一条新记忆。"""
        item = MemoryItem(
            content=content,
            memory_type=memory_type,
            metadata=metadata or {},
        )
        if memory_type == "ltm":
            self._ltm.append(item)
        else:
            self._stm.append(item)
            # 超出容量 → 淘汰回忆概率最低的
            if len(self._stm) > self._stm_capacity:
                self._stm.sort(key=lambda x: x.recall_probability)
                self._stm.pop(0)
        return item

    def set_working(self, key: str, value: Any):
        """设置工作记忆。"""
        self.working[key] = value
        # 工作记忆容量限制
        if len(self.working) > self._wm_capacity:
            # 移除最早添加的 key
            oldest = next(iter(self.working))
            del self.working[oldest]

    def get_working(self, key: str, default=None) -> Any:
        return self.working.get(key, default)

    # ── 检索 ──

    def recall(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        """从所有层检索记忆 (简单关键词匹配)。"""
        q = query.lower()
        results = []

        for item in self._stm + self._ltm:
            if item.is_forgotten:
                continue
            if q in item.content.lower():
                item.access()
                results.append(item)

        # 按回忆概率排序
        results.sort(key=lambda x: x.recall_probability, reverse=True)
        return results[:top_k]

    def recall_by_type(self, memory_type: str, top_k: int = 10) -> List[MemoryItem]:
        """按类型检索。"""
        pool = self._stm if memory_type == "stm" else self._ltm
        items = [m for m in pool if not m.is_forgotten]
        items.sort(key=lambda x: x.recall_probability, reverse=True)
        return items[:top_k]

    # ── 巩固 ──

    def consolidate(self) -> Dict[str, int]:
        """记忆巩固: STM → LTM 转移。

        访问次数 ≥ consolidation_threshold 的 STM 提升为 LTM。
        返回 {stm_to_ltm, stm_forgotten, ltm_count}。
        """
        promoted = 0
        now = time.time()

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
            "forgotten_stm": sum(1 for m in self._stm if m.is_forgotten),
        }

    # ── 统计 ──

    def stats(self) -> dict:
        return {
            "working_count": len(self.working),
            "stm_count": len(self._stm),
            "ltm_count": len(self._ltm),
            "consolidation_threshold": self._consolidation_threshold,
            "stm_capacity": self._stm_capacity,
        }

    def forget(self, item_id: str) -> bool:
        """主动遗忘一条记忆。"""
        for pool in [self._stm, self._ltm]:
            for i, item in enumerate(pool):
                if item.id == item_id:
                    pool.pop(i)
                    return True
        return False

    def clear_working(self):
        """清空工作记忆。"""
        self.working.clear()

    def search(self, query: str, **kwargs) -> dict:
        """兼容 adapter 接口。"""
        results = self.recall(query)
        return {
            "status": "ok",
            "results": [r.to_dict() for r in results],
            "total": len(results),
        }
