"""
memory/magma.py — 四维正交图谱记忆 (MAGMA 架构移植)

核心: 将每个记忆项在四个正交关系图上表示:
  语义图 (Semantic)   — 内容相似性
  时序图 (Temporal)   — 时间关联
  因果图 (Causal)     — 因果关系链
  实体图 (Entity)     — 实体间关系

检索 = 策略引导的图遍历, 而非纯语义相似度。

移植自: MAGMA (Multi-Graph based Agentic Memory Architecture)
论文: arXiv 2601.03236 | GitHub: FredJiang0324/MAGMA

本实现是轻量版: 无 networkx/sentence-transformers 依赖,
保留核心四维正交图结构和策略引导遍历算法。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from datetime import datetime
import math
import time
import uuid


# ═══════════════════════════════════════════════════════════════
# 图数据结构
# ═══════════════════════════════════════════════════════════════

class RelationType:
    """四维正交关系类型。"""
    TEMPORAL = "temporal"   # 时间先后/同时
    SEMANTIC = "semantic"   # 内容相似/相关
    CAUSAL = "causal"       # 因果/使能/阻止
    ENTITY = "entity"       # 实体指代


@dataclass
class MemoryNode:
    """记忆图谱中的一个节点。"""
    node_id: str = ""
    content: str = ""          # 记忆内容
    summary: str = ""          # 摘要 (用于快速匹配)
    entities: List[str] = field(default_factory=list)   # 涉及的实体
    timestamp: float = 0.0     # 创建时间
    importance: float = 0.5    # 重要性 0-1
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.node_id:
            self.node_id = uuid.uuid4().hex[:12]
        if not self.timestamp:
            self.timestamp = time.time()
        if not self.summary:
            self.summary = self.content[:80]

    @property
    def age_hours(self) -> float:
        return (time.time() - self.timestamp) / 3600


@dataclass
class Relation:
    """两个节点之间的关系。"""
    source_id: str
    target_id: str
    rel_type: str        # temporal | semantic | causal | entity
    weight: float = 1.0  # 关系强度 0-1
    label: str = ""      # 关系标签 (如 "precedes", "leads_to", "refers_to")


# ═══════════════════════════════════════════════════════════════
# 四维图谱记忆
# ═══════════════════════════════════════════════════════════════

class MagmaMemory:
    """四维正交图谱记忆。

    四张正交关系图:
      G_temporal: 时间先后/同时/包含
      G_semantic:  内容相似/相关/部分
      G_causal:    导致/因为/使能/阻止
      G_entity:    提及/指代

    检索策略:
      - 意图感知路由器: 分析查询 → 选择主导维度
      - 自适应遍历: 沿选定维度跳跃, 融合多图结果
      - 结构化上下文构建: 将遍历结果线性化

    用法:
        mem = MagmaMemory()
        node = mem.add("用户说鳤是珍稀鱼类")
        results = mem.search("鳤的保护现状")
    """

    def __init__(self):
        self.name = "magma"
        self._nodes: Dict[str, MemoryNode] = {}
        self._graphs: Dict[str, Dict[str, List[Relation]]] = {
            RelationType.TEMPORAL: {},
            RelationType.SEMANTIC: {},
            RelationType.CAUSAL: {},
            RelationType.ENTITY: {},
        }

    # ── 写入 ──

    def add(self, content: str, entities: Optional[List[str]] = None,
            importance: float = 0.5, metadata: Optional[Dict] = None) -> MemoryNode:
        """添加一条记忆并自动建立四维关系。"""
        node = MemoryNode(
            content=content,
            entities=entities or self._extract_entities(content),
            importance=importance,
            metadata=metadata or {},
        )
        self._nodes[node.node_id] = node

        # 与现有节点自动建立关系
        for existing in self._nodes.values():
            if existing.node_id == node.node_id:
                continue

            # 语义关系: 关键词重叠
            semantic_score = self._calc_semantic(node, existing)
            if semantic_score > 0.3:
                self._relate(node.node_id, existing.node_id,
                            RelationType.SEMANTIC, semantic_score)

            # 实体关系: 共享实体
            entity_overlap = set(node.entities) & set(existing.entities)
            if entity_overlap:
                union_size = len(set(node.entities) | set(existing.entities))
                self._relate(node.node_id, existing.node_id,
                            RelationType.ENTITY,
                            len(entity_overlap) / max(union_size, 1))

            # 时序关系: 时间接近
            time_diff = abs(node.timestamp - existing.timestamp)
            if time_diff < 3600:  # 1 小时内
                temporal_weight = 1.0 - (time_diff / 3600)
                self._relate(node.node_id, existing.node_id,
                            RelationType.TEMPORAL, temporal_weight,
                            "concurrent" if time_diff < 300 else "precedes")

        return node

    def relate(self, source_id: str, target_id: str,
               rel_type: str = RelationType.CAUSAL,
               weight: float = 1.0, label: str = ""):
        """手动建立两个节点之间的关系。"""
        self._relate(source_id, target_id, rel_type, weight, label)

    def _relate(self, source_id: str, target_id: str,
                rel_type: str, weight: float, label: str = ""):
        """在指定关系图上添加边。"""
        if source_id not in self._nodes or target_id not in self._nodes:
            return
        rel = Relation(source_id, target_id, rel_type, weight, label)
        self._graphs[rel_type].setdefault(source_id, []).append(rel)

    # ── 检索 (策略引导图遍历) ──

    def search(self, query: str, top_k: int = 10) -> List[MemoryNode]:
        """四维图遍历检索。

        步骤:
          1. 意图分析: 检测查询的语义/实体/因果需求
          2. 锚点选择: 找到查询相关的起始节点
          3. 策略遍历: 沿选定维度跳跃
          4. 多图融合: RRF 融合各图结果
          5. 提取聚合: 线性化为上下文
        """
        if not self._nodes:
            return []

        # 1. 意图分析 + 2. 锚点选择
        query_entities = self._extract_entities(query)
        query_terms = set(query.lower().split())

        # 找到锚点节点 (与查询语义/实体相关的节点)
        scored: Dict[str, float] = {}
        for nid, node in self._nodes.items():
            score = 0.0
            # 实体匹配
            if query_entities and node.entities:
                qe_set = set(query_entities)
                ne_set = set(node.entities)
                overlap = len(qe_set & ne_set)
                score += overlap * 0.4
            # 关键词匹配
            node_terms = set(node.content.lower().split())
            term_overlap = len(query_terms & node_terms)
            score += term_overlap * 0.1
            # 内容包含匹配 (对中文友好)
            q_lower = query.lower()
            if q_lower in node.content.lower():
                score += 0.2
            # 重要性加权
            score *= node.importance
            if score > 0:
                scored[nid] = score

        if not scored:
            return []

        # 3. 策略遍历: 从高分锚点出发沿图跳跃
        top_anchors = sorted(scored, key=scored.get, reverse=True)[:3]
        visited: Set[str] = set()
        results: Dict[str, float] = {}

        for anchor_id in top_anchors:
            self._traverse(anchor_id, visited, results, depth=0, max_depth=2)

        # 4. 多图融合: 合并各维度结果并重新排序
        sorted_ids = sorted(results, key=results.get, reverse=True)[:top_k]
        return [self._nodes[nid] for nid in sorted_ids if nid in self._nodes]

    def _traverse(self, node_id: str, visited: Set[str],
                  results: Dict[str, float], depth: int, max_depth: int):
        """从指定节点出发, 沿所有四维图遍历。"""
        if depth > max_depth or node_id in visited:
            return
        visited.add(node_id)

        # 衰减权重
        decay = 0.7 ** depth
        results[node_id] = results.get(node_id, 0) + decay

        # 探索所有四维图的邻接节点
        for rel_type in RelationType.TEMPORAL, RelationType.SEMANTIC, RelationType.CAUSAL, RelationType.ENTITY:
            relations = self._graphs[rel_type].get(node_id, [])
            for rel in relations:
                next_id = rel.target_id
                if next_id not in visited:
                    decayed = decay * rel.weight
                    results[next_id] = results.get(next_id, 0) + decayed
                    self._traverse(next_id, visited, results, depth + 1, max_depth)

    # ── 辅助 ──

    def _extract_entities(self, text: str) -> List[str]:
        """从文本中提取实体。"""
        words = text.split()
        entities = []
        for w in words:
            clean = w.strip("，。！？、""''（）()《》【】[]·,").strip()
            if len(clean) >= 2:
                # 英文学名或大写缩写
                if clean[0].isupper() or any(c.isalpha() for c in clean):
                    entities.append(clean)
        return entities

    def _calc_semantic(self, a: MemoryNode, b: MemoryNode) -> float:
        """计算两个节点之间的语义相似度 (基于关键词重叠)。"""
        terms_a = set(a.content.lower().split())
        terms_b = set(b.content.lower().split())
        if not terms_a or not terms_b:
            return 0.0
        overlap = len(terms_a & terms_b)
        return overlap / max(len(terms_a | terms_b), 1)

    # ── 统计 ──

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return sum(len(edges) for g in self._graphs.values() for edges in g.values())

    def stats(self) -> dict:
        return {
            "nodes": self.node_count,
            "edges": self.edge_count,
            "graphs": {rt: sum(len(es) for es in g.values())
                      for rt, g in self._graphs.items()},
        }

    def report(self) -> dict:
        return {"status": "ok", "stats": self.stats()}
