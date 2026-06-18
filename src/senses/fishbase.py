"""FishBaseSense — 鱼类性状感受器 (FishBase 形态学数据)"""

from __future__ import annotations
from typing import Any, Dict, List
from .scholar import SenseInput, SenseOutput


class FishBaseSense:
    """鱼类生物学性状感受器。
    
    从 FishBase 感知物种的形态学、生态学参数:
    - 最大体长、体形、截面
    - 营养级、洄游类型
    - IUCN 保护等级
    """

    def __init__(self):
        self.name = "fishbase"

    def sense(self, inp: SenseInput) -> SenseOutput:
        output = SenseOutput(query=inp.query, species=inp.species)
        try:
            traits = self._query_traits(inp)
            output.papers = [traits] if traits else []
            output.total_found = 1 if traits else 0
            output.sources_used = ["fishbase"]
        except Exception as e:
            output.errors.append(str(e))
        return output

    def _query_traits(self, inp: SenseInput) -> dict:
        """查询 FishBase 性状。由爬虫数据 + API 实现。"""
        return {}

    def search(self, query: str, species: str = "", **kwargs) -> dict:
        inp = SenseInput(query=query, species=species or None, **kwargs)
        result = self.sense(inp)
        return {"status": "ok", "traits": result.papers[0] if result.papers else {}}
