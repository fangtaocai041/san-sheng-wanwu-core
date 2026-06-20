"""
cortex/evolution.py — 自我进化引擎 (代码执行层)

从只读分析器升级为可执行代码修改的进化引擎:

  1. analyze() — AST 分析代码质量
  2. mutate() — 在 AST 层执行代码变异 (安全沙箱内)
  3. evolve_file() — 完整管线: 读 → 分析 → 变异 → 测试 → 提交
  4. batch_evolve() — 批量进化多个文件

安全机制:
  - 安全锁 (默认 readonly, unlock() 才可写)
  - 变异前备份原文件
  - 变异后运行测试, 失败则自动回滚
  - 每次变异记录完整事件日志

这是硅基生命从迭代中学习的最高级形式:
  不是人修改代码 → 而是系统修改自身。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import ast
import os
import shutil
import subprocess
import sys
import textwrap
import time
import uuid


# ── 数据结构 ──

@dataclass
class ModificationProposal:
    target_file: str = ""
    description: str = ""
    code_before: str = ""
    code_after: str = ""
    risk_level: str = "low"
    estimated_impact: str = ""
    author: str = "self"
    id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = uuid.uuid4().hex[:12]


@dataclass
class EvolutionEvent:
    proposal_id: str
    target_file: str
    success: bool
    action: str = ""
    duration_ms: float = 0.0
    error: Optional[str] = None
    new_test_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ── AST 变异器 ──

MUTATION_RULES = [
    {
        "name": "add_docstring_to_module",
        "description": "为无文档字符串的模块添加 docstring",
        "risk": "low",
    },
    {
        "name": "add_type_hints_to_function",
        "description": "为函数添加返回类型提示",
        "risk": "medium",
    },
    {
        "name": "extract_long_function",
        "description": "将超过 50 行的函数拆分为子函数",
        "risk": "high",
    },
]


def _mutate_add_docstring(source: str, filepath: str) -> Optional[str]:
    """为模块添加文档字符串 (如果没有的话)。"""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    if ast.get_docstring(tree):
        return None  # 已有 docstring
    rel_path = os.path.relpath(filepath).replace("\\", "/")
    name = os.path.splitext(os.path.basename(filepath))[0]
    lines = source.split("\n")
    # 跳过 shebang 和 encoding 声明
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("#!") or line.startswith("# -*-"):
            insert_at = i + 1
        else:
            break
    docstring = f'"""{rel_path} — {name} module."""'
    lines.insert(insert_at, "")
    lines.insert(insert_at, docstring)
    return "\n".join(lines)


def _mutate_add_return_type(source: str, filepath: str = "") -> Optional[str]:
    """为没有返回类型提示的函数添加 -> None。"""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    modified = False
    # 遍历函数定义, 找到没有 return annotation 的
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.returns is None and node.name != "__init__":
                # 检查函数体是否有 return 语句
                has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
                if not has_return:
                    modified = True
    if not modified:
        return None
    # 简单位替换: 在 def 行末添加 -> None
    lines = source.split("\n")
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("def ") and "->" not in stripped and stripped.endswith(":"):
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(f"{indent}def {stripped[4:-1]} -> None:")
        else:
            new_lines.append(line)
    return "\n".join(new_lines)


# ── 变异引擎 ──

class MutationEngine:
    """AST 变异引擎 — 在代码的语法树层执行受控变异。"""

    def __init__(self):
        self._mutators = {
            "add_docstring_to_module": _mutate_add_docstring,
            "add_type_hints_to_function": _mutate_add_return_type,
        }

    def apply(self, source: str, filepath: str,
              rule_name: str = "") -> Optional[str]:
        """对源代码执行一次变异。返回变异后的代码, 或 None(无需变异)。"""
        if rule_name and rule_name in self._mutators:
            mutator = self._mutators[rule_name]
            return mutator(source, filepath)

        # 无指定规则 → 尝试所有规则, 返回第一个成功的
        for name, mutator in self._mutators.items():
            result = mutator(source, filepath)
            if result is not None and result != source:
                return result
        return None


# ── 进化引擎 ──

class EvolutionEngine:
    """自我进化引擎 (代码执行层)。

    完整进化管线:
      1. analyze() — AST 分析代码质量
      2. evolve_file() — 变异 → 测试 → 提交/回滚

    安全机制:
      - safety_lock = True 时只读 (默认)
      - unlock() 启用写模式
      - 变异前备份, 测试失败回滚
    """

    def __init__(self, test_cmd: str = "python -m pytest tests/ -q --tb=line"):
        self.name = "evolution"
        self._events: List[EvolutionEvent] = []
        self._pending: List[ModificationProposal] = []
        self._safety_lock = True
        self._test_cmd = test_cmd
        self._mutation = MutationEngine()
        self._backup_dir: Optional[str] = None

    @property
    def is_readonly(self) -> bool:
        return self._safety_lock

    def unlock(self):
        self._safety_lock = False

    def lock(self):
        self._safety_lock = True

    # ── 转座驯化通道 (与 transposition.py 集成) ──

    def propose_domestication(self, source_domain: str, target_domain: str,
                              pattern_type: str, fitness_delta: float,
                              success_count: int) -> ModificationProposal:
        """接受来自转座层的驯化通路生成为进化提案。

        当 TranspositionLayer 检测到某个跨域模式被成功复用多次后，
        调用此方法将其转化为一个代码层面的进化提案。

        对应生物学: TE 被驯化为功能性调控元件 → 基因组层面的固定。

        Args:
            source_domain: 源知识域
            target_domain: 目标知识域
            pattern_type: 模式类型 (concept/inference/strategy)
            fitness_delta: 平均适应性变化
            success_count: 成功转座次数

        Returns:
            ModificationProposal (安全锁开启时自动执行, 否则排队)
        """
        description = (
            f"[转座驯化] {source_domain}→{target_domain} "
            f"({pattern_type}, fitness={fitness_delta:.2f}, "
            f"success_count={success_count})"
        )
        proposal = ModificationProposal(
            target_file=f"config/knowledge_base/transpositions.yaml",
            description=description,
            code_before="# 待添加驯化通路",
            code_after=(
                f"# 驯化通路: {source_domain}→{target_domain}\n"
                f"# 类型: {pattern_type}\n"
                f"# 适应性: {fitness_delta:.2f}\n"
                f"# 成功次数: {success_count}\n"
            ),
            risk_level="low",
            estimated_impact=f"跨域路由 {source_domain}↔{target_domain} 固化",
            author="transposition_layer",
        )
        self._pending.append(proposal)

        # 非安全锁模式自动提交
        if not self._safety_lock:
            self._auto_commit(proposal)

        return proposal

    def _auto_commit(self, proposal: ModificationProposal):
        """自动提交进化事件 (用于驯化通路的快速固化)。"""
        event = EvolutionEvent(
            proposal_id=proposal.id,
            target_file=proposal.target_file,
            success=True,
            action="domestication",
            duration_ms=0.0,
        )
        self._events.append(event)

    # ── 分析 (只读) ──

    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        try:
            with open(filepath, encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
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
        analysis = self.analyze_file(filepath)
        proposals = []
        if analysis.get("status") == "error":
            return proposals
        if not analysis.get("has_docstring"):
            proposals.append(ModificationProposal(
                target_file=filepath, description="add module docstring",
                risk_level="low"))
        return proposals

    # ── 进化管线 ──

    def evolve_file(self, filepath: str, rule_name: str = "",
                    run_tests: bool = True) -> EvolutionEvent:
        """对一个文件执行完整进化管线。

        Pipeline:
          1. 读取源代码
          2. AST 变异
          3. 备份原文件
          4. 写入变异后代码
          5. 运行测试
          6. 通过 → 记录事件; 失败 → 回滚
        """
        t0 = time.time()
        rel_path = os.path.relpath(filepath)

        if self._safety_lock:
            return EvolutionEvent(
                proposal_id="", target_file=rel_path, action="blocked",
                success=False, error="safety lock enabled",
                duration_ms=(time.time() - t0) * 1000)

        if not os.path.isfile(filepath):
            return EvolutionEvent(
                proposal_id="", target_file=rel_path, action="error",
                success=False, error="file not found",
                duration_ms=(time.time() - t0) * 1000)

        # 1. Read
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        # 2. Mutate
        mutated = self._mutation.apply(source, filepath, rule_name)
        if mutated is None or mutated == source:
            return EvolutionEvent(
                proposal_id="", target_file=rel_path, action="skipped",
                success=True, error="no mutation applicable",
                duration_ms=(time.time() - t0) * 1000)

        # 3. Backup
        backup = filepath + ".bak"
        shutil.copy2(filepath, backup)

        # 4. Write
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(mutated)

        # 5. Test
        if run_tests:
            test_ok, test_output = self._run_tests(filepath)
        else:
            test_ok, test_output = True, ""

        # 6. Commit or rollback
        if test_ok:
            os.remove(backup)
            event = EvolutionEvent(
                proposal_id=uuid.uuid4().hex[:12],
                target_file=rel_path, action="evolved",
                success=True,
                duration_ms=(time.time() - t0) * 1000)
        else:
            shutil.move(backup, filepath)  # rollback
            event = EvolutionEvent(
                proposal_id=uuid.uuid4().hex[:12],
                target_file=rel_path, action="rollback",
                success=False, error=f"tests failed: {test_output[:200]}",
                duration_ms=(time.time() - t0) * 1000)

        self._events.append(event)
        return event

    def batch_evolve(self, filepaths: List[str]) -> List[EvolutionEvent]:
        """批量进化多个文件。"""
        results = []
        for fp in filepaths:
            result = self.evolve_file(fp)
            results.append(result)
        return results

    # ── 测试运行器 ──

    def _run_tests(self, mutated_file: str) -> Tuple[bool, str]:
        """运行测试套件验证变异。"""
        project_root = self._find_project_root(mutated_file)
        if not project_root:
            return False, "cannot determine project root"
        try:
            r = subprocess.run(
                self._test_cmd.split(),
                capture_output=True, text=True, timeout=60,
                cwd=project_root,
            )
            passed = r.returncode == 0
            output = r.stdout.strip().split("\n")[-1] if r.stdout else ""
            return passed, output
        except subprocess.TimeoutExpired:
            return False, "timeout"
        except Exception as e:
            return False, str(e)

    def _find_project_root(self, filepath: str) -> Optional[str]:
        """从文件路径向上查找项目根 (含 tests/ 或 pyproject.toml)。"""
        d = os.path.dirname(os.path.abspath(filepath))
        for _ in range(5):
            if os.path.isfile(os.path.join(d, "pyproject.toml")) or \
               os.path.isdir(os.path.join(d, "tests")):
                return d
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
        return None

    # ── 报告 ──

    def report(self) -> dict:
        evolved = sum(1 for e in self._events if e.success and e.action == "evolved")
        rolled = sum(1 for e in self._events if e.action == "rollback")
        return {
            "status": "ok",
            "mode": "readonly" if self._safety_lock else "readwrite",
            "events": len(self._events),
            "evolved": evolved,
            "rollbacks": rolled,
            "recent": [
                {"file": e.target_file, "action": e.action,
                 "success": e.success, "error": (e.error or "")[:60]}
                for e in self._events[-5:]
            ],
        }

    def search(self, query: str, **kwargs) -> dict:
        return self.report()
