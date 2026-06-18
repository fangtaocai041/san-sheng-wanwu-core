"""KnowledgeBase — 物种知识库 (原 fishkb 核心)"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import json
from pathlib import Path


class KnowledgeBase:
    """物种知识库。
    
    存储物种的正名、别名、形态学参数、分布、保护等级等。
    kb_first_lookup = 调查 → 没有调查就没有发言权
    """

    def __init__(self, db_path: Optional[str] = None):
        self.name = "knowledge_base"
        self._species: Dict[str, dict] = {}
        if db_path:
            self.load(db_path)

    def load(self, db_path: str):
        """从 JSON/YAML 文件加载知识库。"""
        path = Path(db_path)
        if path.suffix == ".json":
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self._species = data if isinstance(data, dict) else {}
        # SQLite 支持通过 _load_sqlite 扩展

    def lookup(self, query: str) -> Optional[Dict[str, Any]]:
        """查询物种。支持学名/中文名/别名。"""
        q = query.strip().lower()

        # 精确匹配
        if q in self._species:
            return self._species[q]

        # 中文名/别名匹配
        for key, info in self._species.items():
            names = [key.lower()]
            names.extend(n.lower() for n in info.get("aliases", []))
            names.extend(n.lower() for n in info.get("chinese_names", []))
            if q in names:
                return info

        return None

    def fuzzy_search(self, query: str) -> List[Dict[str, Any]]:
        """模糊搜索 — 返回候选列表。"""
        q = query.lower()
        candidates = []
        for key, info in self._species.items():
            if q in key.lower():
                candidates.append({"species": key, **info})
            else:
                for alias in info.get("aliases", []):
                    if q in alias.lower():
                        candidates.append({"species": key, **info})
                        break
        return candidates[:10]

    def search(self, query: str, species: str = "", **kwargs) -> dict:
        """兼容旧版 adapter 搜索接口。"""
        result = self.lookup(query) or self.lookup(species)
        if result:
            return {"status": "ok", "known_species": True, "data": result}
        candidates = self.fuzzy_search(query)
        return {"status": "ok", "known_species": False, "candidates": candidates}
