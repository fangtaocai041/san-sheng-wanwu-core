"""WebSense — 通用网络感受器 (Tavily/Exa 搜索)"""

from __future__ import annotations
from typing import Any, Dict, List
from .scholar import SenseInput, SenseOutput


class WebSense:
    """通用网络感受器。
    
    覆盖 Scholar 感受器无法触及的区域:
    - 新闻报道、政策文件
    - 机构网站、NGO 报告
    - 非学术性但相关的网络内容
    """

    def __init__(self):
        self.name = "web"

    def sense(self, inp: SenseInput) -> SenseOutput:
        output = SenseOutput(query=inp.query, species=inp.species)
        try:
            items = self._search_web(inp)
            output.papers = items
            output.total_found = len(items)
            output.sources_used = ["tavily"]
        except Exception as e:
            output.errors.append(str(e))
        return output

    def _search_web(self, inp: SenseInput) -> list:
        """通过 Tavily/Exa API 搜索。由 MCP 工具执行。"""
        return []

    def search(self, query: str, species: str = "", **kwargs) -> dict:
        inp = SenseInput(query=query, species=species or None, **kwargs)
        result = self.sense(inp)
        return {"status": "ok", "total": result.total_found}
