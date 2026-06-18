"""FishBaseSense — 鱼类性状感受器 (FishBase 数据)"""
from __future__ import annotations
from typing import Any, Callable, Optional
from .scholar import SenseInput, SenseOutput
import time


class FishBaseSense:
    """鱼类生物学性状感受器。

    从本地 species.db (FTS5) + FishBase API 感知物种形态学参数。
    注入 MCP 工具:
      search_fishbase: (species, **kwargs) -> dict
    """

    def __init__(self, search_fishbase: Optional[Callable] = None):
        self.name = "fishbase"
        self._search = search_fishbase

    @property
    def is_wired(self) -> bool:
        return self._search is not None

    def sense(self, inp: SenseInput) -> SenseOutput:
        t0 = time.time()
        output = SenseOutput(query=inp.query, species=inp.species)

        if not self._search:
            output.errors.append("No FishBase MCP injected — stub mode")
            output.duration_ms = (time.time() - t0) * 1000
            return output

        try:
            species_name = inp.species or inp.query
            result = self._search(species_name)
            if isinstance(result, dict):
                output.papers = [result]
                output.total_found = 1
                output.sources_used = ["fishbase"]
        except Exception as e:
            output.errors.append(str(e))

        output.duration_ms = (time.time() - t0) * 1000
        return output

    def search(self, query: str, species: str = "", **kwargs) -> dict:
        inp = SenseInput(query=query, species=species or None, **kwargs)
        result = self.sense(inp)
        return {"status": "ok", "traits": result.papers[0] if result.papers else {}}
