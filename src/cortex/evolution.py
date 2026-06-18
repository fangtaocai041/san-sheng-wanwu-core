"""
cortex/evolution.py — 自我进化引擎 (Phase 3 骨架)

安全自修改能力:
  1. 分析当前代码状态 (测试是否通过)
  2. 识别可优化的模块 (性能最差/测试最脆弱的)
  3. 生成修改提案 (带风险评估)
  4. 执行修改 (在沙箱中)
  5. 验证修改 (运行测试)
  6. 回滚如果失败

这是硅基生命从迭代中学习的最高级形式:
  不是人修改代码 → 而是系统修改自身。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime
import ast
import textwrap
import uuid


# ── 修改提案 ──

@dataclass
class ModificationProposal:
    """一个代码修改提案。"""
    target_file: str           # 目标文件路径
    description: str           # 修改描述
    code_before: str = ""      # 修改前的代码片段
    code_after: str = ""       # 修改后的代码片段
    risk_level: str = "low"    # low | medium | high
    estimated_impact: str = "" # 预期影响
    author: str = "self"       # self | human
    id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = uuid.uuid4().hex[:12]


@dataclass
class EvolutionEvent:
    """一次进化事件。"""
    proposal_id: str
    target_file: str
    success: bool
    duration_ms: float = 0.0
    error: Optional[str] = None
    new_test_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ── 进化引擎 ──

class EvolutionEngine:
    """自我进化引擎 (Phase 3 骨架)。

    当前状态: 只读分析器 — 可识别优化机会但不可自动修改。
    未来: 可安全修改自身代码 (需沙箱 + 测试验证)。
    """

    def __init__(self):
        self.name = "evolution"
        self._events: List[EvolutionEvent] = []
        self._pending_proposals: List[ModificationProposal] = []
        self._safety_lock = True  # 安全锁: True = 只读模式

    @property
    def is_readonly(self) -> bool:
        return self._safety_lock

    def unlock(self):
        """解锁写模式 (高风险! 仅在受控环境使用)。"""
        self._safety_lock = False

    def lock(self):
        self._safety_lock = True

    # ── 代码分析 (只读) ──

    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """分析一个 Python 文件的代码质量。"""
        try:
            with open(filepath, encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)

            # 统计
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]

            return {
                "file": filepath,
                "lines": len(source.splitlines()),
                "classes": len(classes),
                "functions": len(functions),
                "imports": len(imports),
                "has_docstring": ast.get_docstring(tree) is not None,
                "status": "ok",
            }
        except Exception as e:
            return {"file": filepath, "status": "error", "error": str(e)}

    def suggest_improvements(self, filepath: str) -> List[ModificationProposal]:
        """建议代码改进 (纯分析, 不修改)。"""
        analysis = self.analyze_file(filepath)
        proposals = []

        if analysis.get("status") == "error":
            return proposals

        if not analysis.get("has_docstring"):
            proposals.append(ModificationProposal(
                target_file=filepath,
                description="添加模块文档字符串",
                risk_level="low",
                estimated_impact="提高代码可读性",
            ))

        if analysis.get("classes", 0) > 3 and analysis.get("functions", 0) > 10:
            proposals.append(ModificationProposal(
                target_file=filepath,
                description="考虑拆分大模块为子包",
                risk_level="medium",
                estimated_impact="改善模块化",
            ))

        return proposals

    # ── 模拟修改 (未来: 实际执行) ──

    def apply_proposal(self, proposal: ModificationProposal) -> EvolutionEvent:
        """应用修改提案 (当前: 仅记录, 不执行)。"""
        event = EvolutionEvent(
            proposal_id=proposal.id,
            target_file=proposal.target_file,
            success=False if self._safety_lock else True,
            error="安全锁启用: 只读模式" if self._safety_lock else None,
        )
        self._events.append(event)
        return event

    # ── 报告 ──

    def report(self) -> dict:
        return {
            "status": "ok",
            "mode": "readonly" if self._safety_lock else "readwrite",
            "events_count": len(self._events),
            "pending_proposals": len(self._pending_proposals),
            "suggestions": [
                {"file": p.target_file, "desc": p.description, "risk": p.risk_level}
                for p in self._pending_proposals[:5]
            ],
        }

    def search(self, query: str, **kwargs) -> dict:
        return self.report()
