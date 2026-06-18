"""
CnkiSense — 中文知网感受器

覆盖英文数据库的系统性盲区。
MCP 注入: search_literature (cnki-mcp)
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional
from .scholar import SenseInput, SenseOutput
import time


class CnkiSense:
    """CNKI 中文文献感受器。

    注入 MCP 工具:
      search_cnki: (query, **kwargs) -> dict

    无注入时返回 stub 结果。
    """

    def __init__(self, search_cnki: Optional[Callable] = None):
        self.name = "cnki"
        self._search = search_cnki

    @property
    def is_wired(self) -> bool:
        return self._search is not None

    def sense(self, inp: SenseInput) -> SenseOutput:
        t0 = time.time()
        output = SenseOutput(query=inp.query, species=inp.species)

        if not self._search:
            output.errors.append("No CNKI MCP injected — stub mode")
            output.duration_ms = (time.time() - t0) * 1000
            return output

        try:
            result = self._search(inp.query, max_results=inp.max_results)
            if isinstance(result, dict):
                papers = result.get("papers", result.get("results", []))
                output.papers = papers
                output.total_found = len(papers)
                output.sources_used = ["cnki"]
        except Exception as e:
            output.errors.append(str(e))

        output.duration_ms = (time.time() - t0) * 1000
        return output

    def search(self, query: str, species: str = "", **kwargs) -> dict:
        inp = SenseInput(query=query, species=species or None, **kwargs)
        result = self.sense(inp)
        return {"status": "ok", "total": result.total_found, "errors": result.errors}
