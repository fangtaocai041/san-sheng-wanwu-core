"""NcbiSense — 生命科学文献感受器 (PubMed/PMC)"""

from __future__ import annotations
from typing import Any, Dict, List
from .scholar import SenseInput, SenseOutput


class NcbiSense:
    """NCBI/PubMed 感受器。
    
    生命科学与医学领域的权威文献源。
    覆盖比 ScholarSense 更专深的生物医学领域。
    """

    def __init__(self):
        self.name = "ncbi"

    def sense(self, inp: SenseInput) -> SenseOutput:
        output = SenseOutput(query=inp.query, species=inp.species)
        try:
            papers = self._query_pubmed(inp)
            output.papers = papers
            output.total_found = len(papers)
            output.sources_used = ["pubmed"]
        except Exception as e:
            output.errors.append(str(e))
        return output

    def _query_pubmed(self, inp: SenseInput) -> list:
        """通过 NCBI E-utilities 查询。实际由 ncbi-mcp 执行。"""
        return []

    def search(self, query: str, species: str = "", **kwargs) -> dict:
        inp = SenseInput(query=query, species=species or None, **kwargs)
        result = self.sense(inp)
        return {"status": "ok", "total": result.total_found}
