"""WebSense — 通用网络感受器 (Tavily/Exa 网络搜索)"""
from __future__ import annotations
from typing import Any, Callable, Optional
from .scholar import SenseInput, SenseOutput
import time


class WebSense:
    """通用网络感受器 — 覆盖学术搜索无法触及的区域。

    注入 MCP 工具:
      search_web: (query, **kwargs) -> dict  (tavily-mcp / exa-mcp)
    """

    def __init__(self, search_web: Optional[Callable] = None):
        self.name = "web"
        self._search = search_web

    @property
    def is_wired(self) -> bool:
        return self._search is not None

    def sense(self, inp: SenseInput) -> SenseOutput:
        t0 = time.time()
        output = SenseOutput(query=inp.query, species=inp.species)

        if not self._search:
            output.errors.append("No Web MCP injected — stub mode")
            output.duration_ms = (time.time() - t0) * 1000
            return output

        try:
            result = self._search(inp.query, max_results=inp.max_results)
            if isinstance(result, dict):
                items = result.get("results", result.get("items", []))
                output.papers = items
                output.total_found = len(items)
                output.sources_used = ["web"]
        except Exception as e:
            output.errors.append(str(e))

        output.duration_ms = (time.time() - t0) * 1000
        return output

    def search(self, query: str, species: str = "", **kwargs) -> dict:
        inp = SenseInput(query=query, species=species or None, **kwargs)
        result = self.sense(inp)
        return {"status": "ok", "total": result.total_found}
