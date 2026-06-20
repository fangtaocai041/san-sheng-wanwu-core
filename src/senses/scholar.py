"""
ScholarSense — 学术文献感受器 (Scholar/CrossRef/OpenAlex)

依赖注入模式:
  sense = ScholarSense(
      search_literature=mcp_scholar_search,  # 在 Reasonix 中注入
      fetch_details=mcp_fetch_article,       # MCP 工具函数
  )
  result = sense.sense(SenseInput(query="鳤", species="Ochetobius elongatus"))

测试时:
  sense = ScholarSense()  # 无注入 = stub 模式
  result = sense.sense(SenseInput(query="test"))
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
import time


# ── 统一输入/输出协议 ──

@dataclass
class SenseInput:
    """统一的感受器输入格式。"""
    query: str
    species: Optional[str] = None
    speech_act: str = "assertion"  # assertion|question|directive|commissive|expressive
    max_results: int = 10
    sources: List[str] = field(default_factory=lambda: ["crossref", "openalex", "google_scholar"])
    time_range: Optional[tuple] = None  # (start_year, end_year)


@dataclass
class SenseOutput:
    """统一的感受器输出格式 — 所有感受器返回此协议。"""
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


# ── MCP 工具函数类型 ──

# 搜索文献: (query, **kwargs) -> dict
SearchFn = Callable[..., dict]

# 获取全文: (identifier, **kwargs) -> dict
FetchFn = Callable[..., dict]

# 获取引用关系: (identifier, **kwargs) -> dict
RelationFn = Callable[..., dict]


class ScholarSense:
    """学术文献感受器。

    注入的 MCP 工具:
      search_literature — 多源文献搜索 (article-mcp / scholarly-mcp)
      fetch_details    — 文献全文获取 (article-mcp)
      get_relations    — 引用关系分析 (article-mcp)

    无注入时运行在 stub 模式 (返回空结果，不崩溃)。
    """

    def __init__(self,
                 search_literature: Optional[SearchFn] = None,
                 fetch_details: Optional[FetchFn] = None,
                 get_relations: Optional[RelationFn] = None):
        self.name = "scholar"
        self.sources = ["crossref", "openalex", "pubmed", "google_scholar"]
        self._search = search_literature
        self._fetch = fetch_details
        self._relations = get_relations

    @property
    def is_wired(self) -> bool:
        """是否已注入真实 MCP 工具。"""
        return self._search is not None

    def sense(self, inp: SenseInput) -> SenseOutput:
        """执行学术文献感知。"""
        t0 = time.time()
        output = SenseOutput(query=inp.query, species=inp.species)

        if not self._search:
            output.errors.append("No MCP search tool injected — stub mode")
            output.duration_ms = (time.time() - t0) * 1000
            return output

        try:
            # 调用 MCP 搜索工具
            result = self._search(
                inp.query,
                max_results=inp.max_results,
            )
            if isinstance(result, dict):
                papers = result.get("papers", result.get("results", []))
                output.papers = self._normalize(papers, "crossref")
                output.sources_used = ["scholar"]
        except Exception as e:
            output.errors.append(f"search_literature: {e}")

        # 去重
        output.papers = self._dedup(output.papers)
        output.total_found = len(output.papers)
        output.duration_ms = (time.time() - t0) * 1000
        return output

    def _normalize(self, raw_papers: list, source: str) -> list:
        """将 MCP 返回的原始数据规范化为统一格式。"""
        normalized = []
        for p in raw_papers:
            if isinstance(p, dict):
                normalized.append({
                    "doi": p.get("doi", ""),
                    "title": p.get("title", ""),
                    "authors": p.get("authors", p.get("author", [])),
                    "journal": p.get("journal", p.get("container_title", "")),
                    "year": p.get("year", p.get("publication_date", "")[:4] if p.get("publication_date") else 0),
                    "citations": p.get("citations", p.get("cited_by_count", 0)),
                    "source": source,
                    "abstract": p.get("abstract", "")[:300],
                    "url": p.get("url", ""),
                })
        return normalized

    def _dedup(self, papers: list) -> list:
        seen = set()
        unique = []
        for p in papers:
            key = p.get("doi", "") or p.get("title", "")
            if key and key in seen:
                continue
            if key:
                seen.add(key)
            unique.append(p)
        return unique

    def search(self, query: str, species: str = "", **kwargs) -> dict:
        """兼容旧版 adapter 协议。"""
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
