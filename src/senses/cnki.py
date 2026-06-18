"""CnkiSense — 中文知网感受器 (补充英文中心的感知盲区)"""

from __future__ import annotations
from typing import Any, Dict, List
from .scholar import SenseInput, SenseOutput


class CnkiSense:
    """CNKI 中文文献感受器。
    
    英文数据库对中文文献覆盖不足 (系统性盲区)。
    此感受器专门覆盖中国学术话语空间。
    """

    def __init__(self):
        self.name = "cnki"

    def sense(self, inp: SenseInput) -> SenseOutput:
        """感知中文文献。"""
        output = SenseOutput(query=inp.query, species=inp.species)
        try:
            papers = self._query_cnki(inp)
            output.papers = papers
            output.total_found = len(papers)
            output.sources_used = ["cnki"]
        except Exception as e:
            output.errors.append(str(e))
        return output

    def _query_cnki(self, inp: SenseInput) -> list:
        """查询知网。实际通过 CNKI MCP 服务器执行。"""
        return []

    def search(self, query: str, species: str = "", **kwargs) -> dict:
        inp = SenseInput(query=query, species=species or None, **kwargs)
        result = self.sense(inp)
        return {"status": "ok", "total": result.total_found}
