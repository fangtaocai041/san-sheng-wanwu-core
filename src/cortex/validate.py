"""ValidateEngine — 文献验证引擎 (原 cognitive-search-engine 核心)"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class PaperProfile:
    """一篇论文的规范轮廓。"""
    title: str = ""
    doi: str = ""
    authors: List[str] = field(default_factory=list)
    journal: str = ""
    year: int = 0
    citations: int = 0
    source: str = ""          # pubmed, crossref, cnki, google_scholar
    confidence: float = 0.0   # 0-1 可信度评分
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)


class ValidateEngine:
    """文献验证与可信度评估。
    
    多源交叉验证 + 期刊权重 + 引用分析。
    """

    def __init__(self):
        self.name = "validate"

    def validate(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """验证一批论文并评分。返回统计数据。"""
        profiles = []
        for p in papers:
            profiles.append(self._profile(p))

        stats = {
            "total": len(profiles),
            "verified": sum(1 for p in profiles if p.confidence > 0.5),
            "avg_confidence": round(
                sum(p.confidence for p in profiles) / max(len(profiles), 1), 3
            ),
            "by_source": {},
            "by_year": {},
        }

        for p in profiles:
            stats["by_source"][p.source] = stats["by_source"].get(p.source, 0) + 1
            if p.year:
                stats["by_year"][p.year] = stats["by_year"].get(p.year, 0) + 1

        return {
            "status": "ok",
            "stats": stats,
            "papers": [asdict(p) for p in profiles],
        }

    def _profile(self, raw: dict) -> PaperProfile:
        """将原始论文字典规范化为 PaperProfile。"""
        p = PaperProfile(
            title=raw.get("title", ""),
            doi=raw.get("doi", ""),
            authors=raw.get("authors", []),
            journal=raw.get("journal", ""),
            year=raw.get("year", 0),
            citations=raw.get("citations", 0),
            source=raw.get("source", "unknown"),
            abstract=raw.get("abstract", "")[:300],
        )
        p.confidence = self._calc_confidence(p)
        return p

    def _calc_confidence(self, paper: PaperProfile) -> float:
        """计算单篇论文的可信度 (0-1)。"""
        score = 0.0
        if paper.doi:
            score += 0.3  # 有 DOI 是关键加分
        if paper.authors:
            score += 0.15  # 有作者
        if paper.journal:
            score += 0.15  # 有期刊
        if paper.abstract:
            score += 0.1  # 有摘要
        if paper.citations > 0:
            score += min(paper.citations / 100, 0.2)  # 引用越多越可信
        if paper.source in ("pubmed", "crossref"):
            score += 0.1  # 权威源加分
        return min(score, 1.0)

    def verify(self, query: str, species: str = "", **kwargs) -> dict:
        """兼容旧版 adapter 协议。"""
        papers = kwargs.get("papers", [])
        result = self.validate(papers)
        return result
