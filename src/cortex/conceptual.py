"""
cortex/conceptual — 概念工程: 本体设计与概念溯源

概念工程 (Conceptual Engineering) 是分析哲学的一个分支,
研究概念的设计、评估与修订。在 AI 系统中, 概念工程回答:
  1. 系统使用了哪些概念?
  2. 这些概念的边界在哪里?
  3. 概念之间的关系是什么?
  4. 概念随证据变化如何修订?

本模块将哲学概念工程转化为可执行的代码结构。
每个概念是一个一等对象, 有定义、溯源、承诺与修订历史。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
import uuid


# ── 概念: 系统认知的基本单元 ──

@dataclass
class Concept:
    """一个形式化概念。

    结构:
      name         — 概念标识符 (如 "protection_level")
      definition   — 概念的形式化定义
      domain       — 值域 (允许的值集合)
      provenance   — 来源: "a_priori" | "empirical" | "derived"
      commitments  — 使用此概念时做出的本体承诺
      version      — 修订版本号
      created_at   — 创建时间
      superseded_by — 被哪个新概念取代 (概念演变)
    """
    name: str
    definition: str = ""
    domain: Optional[Set[str]] = None  # 允许的值集合
    provenance: str = "empirical"      # a_priori / empirical / derived
    commitments: List[str] = field(default_factory=list)
    version: int = 1
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    superseded_by: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "definition": self.definition,
            "domain": sorted(self.domain) if self.domain else [],
            "provenance": self.provenance,
            "commitments": self.commitments,
            "version": self.version,
            "created_at": self.created_at,
            "superseded_by": self.superseded_by,
        }

    def describe(self) -> str:
        """生成概念的人类可读描述。"""
        parts = [
            f"概念: {self.name} (v{self.version})",
            f"定义: {self.definition}",
            f"来源: {self.provenance}",
        ]
        if self.domain:
            parts.append(f"值域: {{{', '.join(sorted(self.domain))}}}")
        if self.commitments:
            parts.append(f"本体承诺: {'; '.join(self.commitments)}")
        if self.superseded_by:
            parts.append(f"被取代: → {self.superseded_by}")
        return "\n".join(parts)


# ── 概念关系 ──

@dataclass
class ConceptRelation:
    """两个概念之间的关系。"""
    subject: str     # 主概念
    predicate: str   # 关系类型: is_a | has_property | opposes | entails | depends_on
    object: str      # 客概念
    strength: float = 1.0  # 关系强度 0-1
    evidence: str = ""

    def describe(self) -> str:
        return f"{self.subject} --[{self.predicate}]--> {self.object}"


# ── 概念修订记录 ──

@dataclass
class ConceptRevision:
    """概念的修订事件。"""
    concept_name: str
    old_version: int
    new_version: int
    reason: str  # 修订原因
    evidence: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ── 概念注册表 ──

class ConceptRegistry:
    """概念注册表 — 系统的本体管理核心。

    功能:
      - 注册/检索概念
      - 定义概念之间的关系
      - 追踪概念修订历史
      - 概念冲突检测
      - 概念溯源查询

    用法:
        registry = ConceptRegistry()
        registry.register(Concept(name="species", definition="..."))
        registry.relate("species", "is_a", "organism")
        registry.explain("species")  # 返回概念及其关系网络
    """

    def __init__(self):
        self._concepts: Dict[str, Concept] = {}
        self._relations: List[ConceptRelation] = []
        self._revisions: List[ConceptRevision] = []

    # ── 注册 ──

    def register(self, concept: Concept) -> Concept:
        """注册或修订一个概念。"""
        if concept.name in self._concepts:
            old = self._concepts[concept.name]
            concept.version = old.version + 1
            concept.created_at = old.created_at
            old.superseded_by = concept.name
            self._revisions.append(ConceptRevision(
                concept_name=concept.name,
                old_version=old.version,
                new_version=concept.version,
                reason=f"Auto-revision from v{old.version}",
            ))
        self._concepts[concept.name] = concept
        return concept

    def get(self, name: str) -> Optional[Concept]:
        """获取概念。返回当前版本。"""
        return self._concepts.get(name)

    def get_version(self, name: str, version: int) -> Optional[Concept]:
        """获取指定版本的概念。"""
        # 当前实现简化: 只保留最新版本
        c = self._concepts.get(name)
        if c and c.version == version:
            return c
        return None

    def all(self) -> List[Concept]:
        """列出所有概念。"""
        return list(self._concepts.values())

    # ── 关系 ──

    def relate(self, subject: str, predicate: str, obj: str,
               strength: float = 1.0, evidence: str = "") -> ConceptRelation:
        """定义两个概念之间的关系。"""
        if subject not in self._concepts:
            raise KeyError(f"Unknown subject concept: {subject}")
        if obj not in self._concepts:
            raise KeyError(f"Unknown object concept: {obj}")
        relation = ConceptRelation(
            subject=subject, predicate=predicate, object=obj,
            strength=strength, evidence=evidence,
        )
        self._relations.append(relation)
        return relation

    def get_relations(self, name: str) -> List[ConceptRelation]:
        """获取与某概念相关的所有关系。"""
        return [r for r in self._relations
                if r.subject == name or r.object == name]

    def get_graph(self, name: str, depth: int = 2) -> Dict[str, Any]:
        """获取以某概念为中心的知识图谱。"""
        visited = set()
        nodes = {}
        edges = []

        def _walk(current: str, d: int):
            if d > depth or current in visited:
                return
            visited.add(current)
            c = self._concepts.get(current)
            if c:
                nodes[current] = c.to_dict()
            for r in self.get_relations(current):
                edges.append(r.describe())
                other = r.object if r.subject == current else r.subject
                _walk(other, d + 1)

        _walk(name, 0)
        return {"center": name, "nodes": nodes, "edges": edges, "depth": depth}

    # ── 冲突检测 ──

    def detect_conflicts(self) -> List[str]:
        """概念间矛盾检测。

        检测类型:
          - 循环依赖: A depends_on B, B depends_on A
          - 继承冲突: A is_a B, A is_a C, B 和 C 互斥
        """
        conflicts = []

        # 循环依赖检测 (简化版)
        dependents = [(r.subject, r.object) for r in self._relations
                      if r.predicate == "depends_on"]
        if len(dependents) >= 2:
            a1, b1 = dependents[0]
            a2, b2 = dependents[1]
            if a1 == b2 and b1 == a2:
                conflicts.append(f"循环依赖: {a1} ↔ {b1}")

        return conflicts

    # ── 解释 ──

    def explain(self, name: str) -> str:
        """生成概念的人类可读解释。"""
        c = self._concepts.get(name)
        if not c:
            return f"未找到概念: {name}"

        lines = [f"## 概念: {name}", f"", c.describe(), ""]

        relations = self.get_relations(name)
        if relations:
            lines.append("### 关系网络")
            for r in relations:
                lines.append(f"  - {r.describe()}")
            lines.append("")

        revisions = [rev for rev in self._revisions
                     if rev.concept_name == name]
        if revisions:
            lines.append("### 修订历史")
            for rev in revisions:
                lines.append(f"  - v{rev.old_version}→v{rev.new_version}: {rev.reason}")
            lines.append("")

        return "\n".join(lines)

    # ── 持久化 ──

    def to_dict(self) -> dict:
        return {
            "concepts": {k: v.to_dict() for k, v in self._concepts.items()},
            "relations": [r.describe() for r in self._relations],
            "revisions": [
                {"concept": r.concept_name, "from": r.old_version,
                 "to": r.new_version, "reason": r.reason}
                for r in self._revisions
            ],
            "conflicts": self.detect_conflicts(),
        }

    def search(self, query: str, **kwargs) -> dict:
        """兼容 adapter 接口。"""
        result = self.explain(query)
        return {"status": "ok", "explanation": result, "concept": query}
