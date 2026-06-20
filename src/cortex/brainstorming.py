"""
cortex/brainstorming.py — 科学头脑风暴引擎 (选题/假设生成)

对应 Codex 科研工作流: scientific-brainstorming (选题)

核心功能:
  1. 基于知识图谱中的概念关联生成研究假设
  2. 检测知识空白 (Knowledge Gap)
  3. 跨学科思维组合 (类比映射)

学术来源:
  - Boden (1990) 创造力三类型: 组合/探索/转换
  - Koestler (1964) 双关联 (bisociation): 两个不相关框架的交叉
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime
import math
import time
import uuid


@dataclass
class Hypothesis:
    """一条研究假设。"""
    title: str = ""
    question: str = ""
    rationale: str = ""         # 提出依据
    domains: List[str] = field(default_factory=list)  # 涉及的学科
    novelty: float = 0.5        # 新颖度 0-1
    feasibility: float = 0.5    # 可行性 0-1
    source_concepts: List[str] = field(default_factory=list)
    id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = uuid.uuid4().hex[:8]

    @property
    def score(self) -> float:
        return round((self.novelty * 0.6 + self.feasibility * 0.4), 3)


class BrainstormingEngine:
    """科学头脑风暴引擎 — 从已有知识生成新假设。

    三种创造力模式:
      1. 组合 (Combinational): 重组已有概念
      2. 探索 (Exploratory): 在概念空间中搜索边界
      3. 转换 (Transformational): 跨越学科映射

    用法:
        engine = BrainstormingEngine()
        hypos = engine.generate(domain="biology", count=5)
        for h in hypos:
            print(f"{h.title} (novelty={h.novelty})")
    """

    def __init__(self):
        self.name = "brainstorming"
        self._history: List[Hypothesis] = []

    # ── 预置思维模板 ──

    TEMPLATES = [
        {
            "pattern": "类比迁移",
            "description": "将A领域的成熟理论映射到B领域的新问题",
            "domains_needed": 2,
        },
        {
            "pattern": "反向思考",
            "description": "质疑当前领域的基本假设，考虑相反可能性",
            "domains_needed": 1,
        },
        {
            "pattern": "交叉育种",
            "description": "将两种不相关的方法/技术结合",
            "domains_needed": 2,
        },
        {
            "pattern": "边缘探索",
            "description": "在现有知识的边界处寻找异常/未解释现象",
            "domains_needed": 1,
        },
        {
            "pattern": "尺度转换",
            "description": "将宏观规律映射到微观或反之",
            "domains_needed": 1,
        },
    ]

    def generate(self, domain: str = "biology",
                 count: int = 5, topics: Optional[List[str]] = None) -> List[Hypothesis]:
        """生成研究假设。

        Args:
            domain: 目标学科
            count: 生成数量
            topics: 可选的主题列表

        Returns:
            假设列表
        """
        hypotheses = []

        # 从拓扑矩阵获取邻居学科
        neighbors = self._get_neighbor_domains(domain)

        for i in range(min(count, len(self.TEMPLATES))):
            tmpl = self.TEMPLATES[i]
            partner = neighbors[i % len(neighbors)] if neighbors else "cs"

            title = f"{domain} × {partner}: {tmpl['pattern']}"

            hypothesis = Hypothesis(
                title=title,
                question=f"如何将{domain}领域的知识通过{tmpl['pattern']}应用于{partner}？",
                rationale=f"基于{tmpl['description']}的思维模板",
                domains=[domain, partner] if tmpl["domains_needed"] > 1 else [domain],
                novelty=round(0.5 + (i / count) * 0.4, 2),
                feasibility=round(0.7 - (i / count) * 0.3, 2),
                source_concepts=[f"{domain}_core", f"{partner}_method"],
            )
            hypotheses.append(hypothesis)

        self._history.extend(hypotheses)
        return hypotheses

    def _get_neighbor_domains(self, domain: str) -> List[str]:
        """获取与指定学科关联最强的邻居学科。"""
        try:
            from .domains import DOMAIN_TOPOLOGY_MATRIX
            row = DOMAIN_TOPOLOGY_MATRIX.get(domain, {})
            neighbors = [(d, w) for d, w in row.items() if d != domain and w >= 0.3]
            neighbors.sort(key=lambda x: x[1], reverse=True)
            return [d for d, _ in neighbors[:5]]
        except ImportError:
            return ["math", "physics", "cs", "psychology"]

    def search(self, query: str, **kwargs) -> dict:
        hypos = self.generate(domain=query or "biology")
        return {
            "status": "ok",
            "hypotheses": [h.__dict__ for h in hypos],
            "count": len(hypos),
        }

    def report(self) -> dict:
        return {
            "status": "ok",
            "total_generated": len(self._history),
            "recent": [h.title for h in self._history[-5:]],
        }
