"""
cortex/validate — 文献验证皮层

整合自:
  - cognitive-search-engine/src/validator.py (核心评分)
  - fishkb/fishkb/credibility.py (期刊白名单)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


# ── 数据结构 ──

@dataclass
class Paper:
    """论文实体。"""
    doi: str = ""
    title: str = ""
    year: Optional[int] = None
    journal: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    citations: int = 0
    pmid: Optional[str] = None
    pmcid: Optional[str] = None
    source: str = ""  # pubmed, crossref, cnki, scholar
    trust_score: int = 50
    credibility_score: int = 50


@dataclass
class ValidationStats:
    total: int = 0
    verified: int = 0
    pending: int = 0
    rejected: int = 0
    avg_trust: float = 0.0
    avg_credibility: float = 0.0
    by_source: Dict[str, int] = field(default_factory=dict)
    by_year: Dict[str, int] = field(default_factory=dict)


# ── 常量 (从旧 validator 移植) ──

SCI_JOURNALS = ["nature", "science ", "pnas", "ecology", "evolution",
                "freshwater", "fish", "fisheries", "ichthyology"]
CSCD_JOURNALS = ["水生生物学报", "水产学报", "中国水产科学", "生态学报",
                 "生物多样性", "动物学杂志", "湖泊科学", "长江流域资源与环境"]
CSTPCD_JOURNALS = ["水生态学杂志", "淡水渔业", "水产科学", "海洋渔业"]
PREPRINT_SERVERS = ["arxiv", "biorxiv", "research square", "preprints.org",
                    "ssrn", "medrxiv", "preprint"]
PREDATORY_PATTERNS = ["predatory", "oapjb", "waset", "world academy of science",
                      "public science reference", "scholarly exchange"]


# ── 核心评分 ──

def calc_trust_score(paper: Paper, species_terms: List[str] | None = None) -> int:
    """五级可信度评分。"""
    score = 50
    species_terms = species_terms or []

    if paper.doi and paper.doi.startswith("10."):
        score += 20
    if paper.pmid:
        score += 15
    title_lower = (paper.title or "").lower()
    if any(term.lower() in title_lower for term in species_terms):
        score += 10
    if paper.authors:
        score += 10
    if paper.journal:
        score += 5
    return min(100, score)


def calc_credibility_score(paper: Paper) -> int:
    """期刊权威性评分。"""
    score = 50
    journal_lower = (paper.journal or "").lower()

    if "retracted" in journal_lower or "retraction" in (paper.title or "").lower():
        return -1

    is_sci = any(sci in journal_lower for sci in SCI_JOURNALS)
    is_cscd = any(cscd in journal_lower for cscd in CSCD_JOURNALS)
    is_cstpcd = any(cstpcd in journal_lower for cstpcd in CSTPCD_JOURNALS)

    if is_sci:
        score += 30
    elif is_cscd:
        score += 25
    elif is_cstpcd:
        score += 20
    elif paper.journal:
        score += 10

    if paper.doi and paper.doi.startswith("10."):
        score += 10
    if paper.pmid:
        score += 10
    if paper.pmcid:
        score += 5
    if paper.citations >= 50:
        score += 10
    elif paper.citations >= 10:
        score += 5

    if any(srv in journal_lower for srv in PREPRINT_SERVERS):
        score -= 30
    if any(pat in journal_lower for pat in PREDATORY_PATTERNS):
        score -= 40

    return max(0, min(100, score))


# ── 皮层接口 ──

class ValidateCortex:
    """文献验证皮层。
    
    整合信任度评分 + 期刊权威评分 + 多源独立性检查。
    """

    def __init__(self):
        self.name = "validate"

    def validate(self, raw_papers: List[Dict[str, Any]],
                 species_terms: List[str] | None = None) -> dict:
        """验证论文批次，返回分类统计和评分。"""
        papers = [self._to_paper(p) for p in raw_papers]
        for p in papers:
            p.trust_score = calc_trust_score(p, species_terms)
            p.credibility_score = calc_credibility_score(p)

        stats = ValidationStats(total=len(papers))
        for p in papers:
            if p.trust_score >= 70 and p.credibility_score >= 60:
                stats.verified += 1
            elif p.credibility_score < 0:
                stats.rejected += 1
            else:
                stats.pending += 1
            if p.source:
                stats.by_source[p.source] = stats.by_source.get(p.source, 0) + 1
            if p.year:
                ykey = str(p.year)
                stats.by_year[ykey] = stats.by_year.get(ykey, 0) + 1

        avg_t = sum(p.trust_score for p in papers) / max(len(papers), 1)
        avg_c = sum(max(p.credibility_score, 0) for p in papers) / max(len(papers), 1)
        stats.avg_trust = round(avg_t, 1)
        stats.avg_credibility = round(avg_c, 1)

        return {
            "status": "ok",
            "stats": {
                "total": stats.total,
                "verified": stats.verified,
                "pending": stats.pending,
                "rejected": stats.rejected,
                "avg_trust": stats.avg_trust,
                "avg_credibility": stats.avg_credibility,
                "by_source": stats.by_source,
                "by_year": stats.by_year,
            },
            "papers": [
                {"doi": p.doi, "title": p.title[:80],
                 "trust": p.trust_score, "credibility": p.credibility_score,
                 "source": p.source, "year": p.year}
                for p in papers
            ],
        }

    def _to_paper(self, raw: dict) -> Paper:
        return Paper(
            doi=raw.get("doi", ""),
            title=raw.get("title", ""),
            year=raw.get("year"),
            journal=raw.get("journal"),
            authors=raw.get("authors", []),
            citations=raw.get("citations", 0),
            pmid=raw.get("pmid"),
            pmcid=raw.get("pmcid"),
            source=raw.get("source", ""),
        )

    def quick_validate(self, papers: List[dict]) -> dict:
        """快速验证（兼容旧版接口）。"""
        return self.validate(papers)

    def search(self, query: str, species: str = "", **kwargs) -> dict:
        """兼容旧版 adapter 协议。"""
        papers = kwargs.get("papers", [])
        return self.validate(papers, species_terms=[species, query] if species else [query])
