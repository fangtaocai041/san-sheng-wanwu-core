"""
cortex/reviewer.py — 同行评审模拟引擎

对应 Codex 科研工作流: nature-reviewer / nature-polishing

功能:
  1. 评审论文: 检测逻辑漏洞、方法缺陷、证据不足
  2. 润色建议: 改进写作清晰度
  3. 审稿意见生成

学术来源:
  - 同行评审的五大标准: 原创性/方法/证据/逻辑/表述
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import time
import uuid


@dataclass
class ReviewComment:
    """一条审稿意见。"""
    category: str = ""       # 原创性 | 方法 | 证据 | 逻辑 | 表述
    severity: str = "minor"  # critical | major | minor
    content: str = ""
    line_ref: str = ""


@dataclass
class ReviewReport:
    """完整审稿报告。"""
    overall_score: float = 0.5       # 0-1
    recommendation: str = ""         # accept | minor_revision | major_revision | reject
    comments: List[ReviewComment] = field(default_factory=list)
    summary: str = ""
    duration_ms: float = 0.0


class ReviewerEngine:
    """同行评审模拟引擎 — 模拟审稿人评审论文。"""

    CATEGORIES = ["原创性", "方法学", "证据充分性", "逻辑一致性", "表述清晰度"]

    def __init__(self):
        self.name = "reviewer"
        self._reviews: List[ReviewReport] = []

    def review(self, title: str = "", abstract: str = "",
               methods: str = "", results: str = "") -> ReviewReport:
        """模拟评审一篇论文。"""
        t0 = time.time()
        comments = []

        # 自动检测各维度的问题
        # 方法检查
        if len(methods) < 50:
            comments.append(ReviewComment(
                category="方法学", severity="major",
                content="方法描述过于简略，缺少关键细节"
            ))

        # 结果检查
        if len(results) < 50:
            comments.append(ReviewComment(
                category="证据充分性", severity="major",
                content="结果部分数据不足，需补充更多分析"
            ))

        if "p < 0.05" not in results and "significant" not in results.lower():
            comments.append(ReviewComment(
                category="证据充分性", severity="minor",
                content="未报告统计显著性指标"
            ))

        # 逻辑检查
        if not title or not abstract:
            comments.append(ReviewComment(
                category="逻辑一致性", severity="critical",
                content="缺少标题或摘要"
            ))

        # 计算综合评分
        n_critical = sum(1 for c in comments if c.severity == "critical")
        n_major = sum(1 for c in comments if c.severity == "major")
        n_minor = sum(1 for c in comments if c.severity == "minor")

        score = max(0, 1.0 - n_critical * 0.4 - n_major * 0.2 - n_minor * 0.05)

        if n_critical > 0:
            recommendation = "reject"
        elif n_major > 2:
            recommendation = "major_revision"
        elif n_major > 0:
            recommendation = "minor_revision"
        else:
            recommendation = "accept"

        report = ReviewReport(
            overall_score=round(score, 2),
            recommendation=recommendation,
            comments=comments,
            summary=f"共{len(comments)}条意见 ({n_critical} critical, {n_major} major, {n_minor} minor)",
            duration_ms=round((time.time() - t0) * 1000, 1),
        )
        self._reviews.append(report)
        return report

    def search(self, query: str, **kwargs) -> dict:
        report = self.review(title=query)
        return {
            "status": "ok",
            "report": {
                "score": report.overall_score,
                "recommendation": report.recommendation,
                "comments": [c.__dict__ for c in report.comments],
            }
        }

    def report(self) -> dict:
        return {
            "status": "ok",
            "total_reviews": len(self._reviews),
        }
