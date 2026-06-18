"""ScholarSense — 学术文献感受器 (Scholar/CrossRef/OpenAlex)"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime
import json


@dataclass
class SenseInput:
    """统一的感受器输入格式。"""
    query: str
    species: Optional[str] = None
    max_results: int = 10
    sources: List[str] = field(default_factory=lambda: ["crossref", "openalex", "google_scholar"])
    time_range: Optional[tuple] = None  # (start_year, end_year)


@dataclass
class SenseOutput:
    """统一的感受器输出格式。
    
    所有感受器返回此格式，皮层模块不必关心底层协议差异。
    """
    query: str
    species: Optional[str] = None
    total_found: int = 0
    papers: List[Dict[str, Any]] = field(default_factory=list)
    sources_used: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class ScholarSense:
    """学术文献感受器。
    
    包装 scholar-mcp、article-mcp 等外部 MCP 服务，
    将原始响应规范化为 SenseOutput。
    """

    def __init__(self):
        self.name = "scholar"
        self.sources = ["crossref", "openalex", "pubmed", "google_scholar"]

    def sense(self, inp: SenseInput) -> SenseOutput:
        """执行学术文献感知。

        注意: 实际运行时通过 MCP 协议查找外部服务。
        此方法返回规范化的 SenseOutput。
        """
        from time import time
        t0 = time()

        output = SenseOutput(
            query=inp.query,
            species=inp.species,
            sources_used=[],
        )

        for source_name in inp.sources:
            if source_name not in self.sources:
                continue
            try:
                papers = self._query_source(source_name, inp)
                output.papers.extend(papers)
                output.sources_used.append(source_name)
            except Exception as e:
                output.errors.append(f"{source_name}: {e}")

        # 去重 (按 DOI)
        seen_dois = set()
        unique = []
        for p in output.papers:
            doi = p.get("doi", "")
            if doi and doi in seen_dois:
                continue
            if doi:
                seen_dois.add(doi)
            unique.append(p)
        output.papers = unique
        output.total_found = len(output.papers)
        output.duration_ms = (time() - t0) * 1000

        return output

    def _query_source(self, source: str, inp: SenseInput) -> list:
        """查询单个数据源。由 MCP 工具实现。"""
        # 在实际运行时，此方法通过 MCP 协议调用外部搜索服务。
        # 返回论文字典列表。
        return []

    def search(self, query: str, species: str = "", **kwargs) -> dict:
        """简化的直接搜索接口，兼容旧版 adapter 协议。"""
        inp = SenseInput(query=query, species=species or None, **kwargs)
        result = self.sense(inp)
        return {
            "status": "ok",
            "total": result.total_found,
            "papers": result.papers,
            "sources": result.sources_used,
            "errors": result.errors[:3],
            "duration_ms": result.duration_ms,
        }
