"""
cortex/domain_modeler.py — 领域建模引擎 (内化自 Matt Pocock domain-modeling)

核心功能:
  1. 从领域知识中提炼和挑战术语
  2. 自动生成/更新 CONTEXT.md 词汇表
  3. 应力测试领域概念的边界条件
  4. 在合适时机提议 ADR (架构决策记录)

与 MAGMA 集成:
  领域术语 → MAGMA SignNode
  ADR → 长期记忆冷层

内化原因 (RCCA/Gödel Agent):
  领域建模应该是自我模型的一部分——能被反思、转座、进化。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime
import os
import re
import time
import uuid


@dataclass
class DomainTerm:
    """一个领域术语条目。"""
    term: str = ""                # 规范术语
    definition: str = ""          # 精确定义
    aliases: List[str] = field(default_factory=list)  # 别名
    category: str = ""            # 分类
    conflicts_with: List[str] = field(default_factory=list)  # 冲突术语
    last_updated: str = ""


@dataclass
class AdrRecord:
    """一条架构决策记录。"""
    id: int = 0
    title: str = ""
    context: str = ""
    decision: str = ""
    consequences: str = ""
    status: str = "accepted"
    date: str = ""


class DomainModeler:
    """领域建模引擎 — 提炼、挑战、维护领域语言。

    三种操作:
      1. challenge(term, usage) — 挑战术语与代码的一致性
      2. define(term, definition) — 定义或更新规范术语
      3. stress_test(concept) — 边界条件下的概念测试
    """

    def __init__(self, context_path: str = "CONTEXT.md"):
        self.name = "domain_modeler"
        self._context_path = context_path
        self._terms: Dict[str, DomainTerm] = {}
        self._adrs: List[AdrRecord] = []
        self._load_context()

    def _load_context(self):
        """从 CONTEXT.md 加载已有术语。"""
        if os.path.isfile(self._context_path):
            with open(self._context_path, "r", encoding="utf-8") as f:
                content = f.read()
            # 简单解析: 寻找 `- **术语**: 定义` 模式
            for match in re.finditer(r"\*\*([^*]+)\*\*:\s*(.+)", content):
                term = match.group(1).strip()
                definition = match.group(2).strip()
                self._terms[term.lower()] = DomainTerm(
                    term=term, definition=definition,
                )

    # ── 挑战术语 ──

    def challenge(self, term: str, usage: str) -> Dict[str, Any]:
        """检查术语使用是否与词汇表定义一致。

        Returns:
            {status, message, suggestion}
        """
        key = term.lower()
        existing = self._terms.get(key)

        if not existing:
            return {
                "status": "undefined",
                "message": f"术语 '{term}' 不在词汇表中",
                "suggestion": f"建议定义: {term} = {usage[:80]}",
            }

        # 简单一致性检查
        definition_words = set(existing.definition.lower().split())
        usage_words = set(usage.lower().split())
        overlap = len(definition_words & usage_words) / max(len(definition_words), 1)

        if overlap < 0.3:
            return {
                "status": "conflict",
                "message": f"'{term}' 的使用似乎与定义不一致",
                "suggestion": f"定义: {existing.definition}. 当前使用: {usage[:80]}",
            }

        return {
            "status": "consistent",
            "message": f"'{term}' 使用与定义一致",
            "definition": existing.definition,
        }

    # ── 定义术语 ──

    def define(self, term: str, definition: str,
               category: str = "", aliases: Optional[List[str]] = None) -> DomainTerm:
        """定义或更新一个规范术语，写入 CONTEXT.md。

        Args:
            term: 规范术语名
            definition: 精确定义
            category: 分类标签
            aliases: 别名词汇
        """
        dt = DomainTerm(
            term=term, definition=definition,
            category=category, aliases=aliases or [],
            last_updated=datetime.now().isoformat(),
        )
        self._terms[term.lower()] = dt
        self._write_context()
        return dt

    # ── 边界测试 ──

    def stress_test(self, concept: str) -> List[str]:
        """对领域概念进行边界条件应力测试。

        Returns:
            发现的潜在问题列表
        """
        issues = []

        key = concept.lower()
        term = self._terms.get(key)
        if not term:
            issues.append(f"未定义的术语: '{concept}'")
            return issues

        # 检查模糊词
        fuzzy_words = ["一般", "通常", "可能", "某种", "相关", "等等"]
        for fw in fuzzy_words:
            if fw in term.definition:
                issues.append(f"定义模糊: 含 '{fw}' — 建议精确化")

        # 检查是否有冲突术语
        if term.conflicts_with:
            issues.append(f"已知冲突: {', '.join(term.conflicts_with)}")

        # 检查定义长度
        if len(term.definition) < 20:
            issues.append(f"定义过短 ({len(term.definition)} 字符)")

        return issues

    # ── ADR ──

    def propose_adr(self, title: str, context: str,
                    decision: str, consequences: str) -> Optional[AdrRecord]:
        """在满足三条件时提议 ADR:
          1. 难以逆转
          2. 无上下文时令人疑惑
          3. 是真正 trade-off 的结果
        """
        adr = AdrRecord(
            id=len(self._adrs) + 1,
            title=title, context=context,
            decision=decision, consequences=consequences,
            date=datetime.now().isoformat(),
        )
        self._adrs.append(adr)
        self._write_adr(adr)
        return adr

    def _write_context(self):
        """写回 CONTEXT.md。"""
        lines = ["# Context — Domain Language", ""]
        by_category: Dict[str, List[DomainTerm]] = {}
        for dt in self._terms.values():
            cat = dt.category or "General"
            by_category.setdefault(cat, []).append(dt)

        for cat, terms in by_category.items():
            lines.append(f"## {cat}")
            lines.append("")
            for dt in terms:
                aliases_str = f" (aka {', '.join(dt.aliases)})" if dt.aliases else ""
                lines.append(f"- **{dt.term}**{aliases_str}: {dt.definition}")
            lines.append("")

        try:
            os.makedirs(os.path.dirname(self._context_path) or ".", exist_ok=True)
            with open(self._context_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except Exception:
            pass

    def _write_adr(self, adr: AdrRecord):
        """写入 ADR。"""
        adr_dir = os.path.join(os.path.dirname(self._context_path) or "docs", "adr")
        os.makedirs(adr_dir, exist_ok=True)

        filename = f"{adr.id:04d}-{adr.title.lower().replace(' ', '-')[:50]}.md"
        path = os.path.join(adr_dir, filename)
        content = f"""# {adr.id:04d}: {adr.title}

**Status**: {adr.status}
**Date**: {adr.date}

## Context
{adr.context}

## Decision
{adr.decision}

## Consequences
{adr.consequences}
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def search(self, query: str, **kwargs) -> dict:
        return self.report()

    def report(self) -> dict:
        return {
            "status": "ok",
            "terms": len(self._terms),
            "adrs": len(self._adrs),
        }
