"""
NcbiSense — 生命科学文献感受器 (PubMed/PMC)
MCP 注入: search_pubmed (ncbi-mcp)
"""

from __future__ import annotations
from typing import Any, Callable, Optional
from .scholar import SenseInput, SenseOutput
import time


class NcbiSense:
    """NCBI/PubMed 感受器。

    注入 MCP 工具:
      search_pubmed: (query, **kwargs) -> dict
      fetch_pubmed:  (pmid, **kwargs) -> dict
    """

    def __init__(self,
                 search_pubmed: Optional[Callable] = None,
                 fetch_pubmed: Optional[Callable] = None):
        self.name = "ncbi"
        self._search = search_pubmed
        self._fetch = fetch_pubmed

    @property
    def is_wired(self) -> bool:
        return self._search is not None

    def sense(self, inp: SenseInput) -> SenseOutput:
        t0 = time.time()
        output = SenseOutput(query=inp.query, species=inp.species)

        if not self._search:
            output.errors.append("No NCBI MCP injected — stub mode")
            output.duration_ms = (time.time() - t0) * 1000
            return output

        try:
            result = self._search(inp.query, max_results=inp.max_results)
            if isinstance(result, dict):
                papers = result.get("papers", result.get("results", []))
                output.papers = papers
                output.total_found = len(papers)
                output.sources_used = ["pubmed"]
        except Exception as e:
            output.errors.append(str(e))

        output.duration_ms = (time.time() - t0) * 1000
        return output

    def search(self, query: str, species: str = "", **kwargs) -> dict:
        inp = SenseInput(query=query, species=species or None, **kwargs)
        result = self.sense(inp)
        return {"status": "ok", "total": result.total_found}
