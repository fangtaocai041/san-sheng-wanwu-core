"""
motor/tdd_engine.py — TDD 测试驱动开发引擎 (内化自 Matt Pocock tdd)

红-绿-重构循环:
  RED:   先写失败测试
  GREEN: 最小代码让测试通过
  REFACTOR: 优化代码结构，测试继续通过

与 RCCA 集成:
  - 配合 godel_agent.py: SELF_IMPROVE 时用 TDD 验证修改
  - 配合 healing.py: 诊断后自动生成回归测试
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import subprocess
import sys
import time
import uuid


@dataclass
class TddCycle:
    """一次 TDD 循环的记录。"""
    cycle_id: str = ""
    phase: str = ""      # red | green | refactor
    test_passed: bool = False
    test_output: str = ""
    duration_ms: float = 0.0


@dataclass
class TddResult:
    """完整 TDD 流程结果。"""
    cycles: List[TddCycle] = field(default_factory=list)
    total_cycles: int = 0
    final_green: bool = False
    total_duration_ms: float = 0.0


class TddEngine:
    """TDD 引擎 — 红-绿-重构循环自动化。

    用法:
        engine = TddEngine()
        result = engine.run(test_code="def test_add(): assert 1+1==2",
                            impl_code="def add(a,b): return a+b")
    """

    MAX_CYCLES = 10

    def __init__(self, test_dir: str = "tests/tdd_scratch"):
        self.name = "tdd_engine"
        self._test_dir = test_dir
        self._history: List[TddResult] = []

    def run(self, test_code: str = "", impl_code: str = "",
            target_file: str = "tdd_target.py") -> TddResult:
        """执行完整 TDD 循环。

        Args:
            test_code: 测试代码
            impl_code: 实现代码
            target_file: 实现文件名

        Returns:
            TddResult
        """
        t0 = time.time()
        result = TddResult()
        cycle_count = 0

        # RED phase: write test, expect failure
        red = self._phase_red(test_code, target_file)
        result.cycles.append(red)
        cycle_count += 1

        if not red.test_passed:
            # Expected: test should fail in red phase
            # GREEN phase: minimal implementation
            green = self._phase_green(test_code, impl_code, target_file)
            result.cycles.append(green)
            cycle_count += 1

            if green.test_passed:
                # REFACTOR phase: clean up
                refactor = self._phase_refactor(target_file)
                result.cycles.append(refactor)
                result.final_green = refactor.test_passed
            else:
                result.final_green = False
        else:
            result.final_green = red.test_passed

        result.total_cycles = len(result.cycles)
        result.total_duration_ms = round((time.time() - t0) * 1000, 1)
        self._history.append(result)
        return result

    def _phase_red(self, test_code: str, target_file: str) -> TddCycle:
        """RED: 写测试, 期望失败 (实现不存在)。"""
        t0 = time.time()
        # 创建测试文件
        import os
        test_path = os.path.join(self._test_dir, f"test_{target_file[:-3]}.py")
        os.makedirs(self._test_dir, exist_ok=True)

        full_test = f"""
def test_tdd():
{chr(10).join('    '+l for l in test_code.split(chr(10)))}
"""
        with open(test_path, "w") as f:
            f.write(full_test)

        # 运行测试 (期望失败)
        try:
            r = subprocess.run(
                [sys.executable, "-m", "pytest", test_path, "-q", "--tb=line"],
                capture_output=True, text=True, timeout=30
            )
            return TddCycle(
                cycle_id=uuid.uuid4().hex[:8], phase="red",
                test_passed=(r.returncode == 0),
                test_output=r.stdout.strip()[-100:] if r.stdout else "",
                duration_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return TddCycle(
                cycle_id=uuid.uuid4().hex[:8], phase="red",
                test_passed=False, test_output=str(e)[:100],
                duration_ms=(time.time() - t0) * 1000,
            )

    def _phase_green(self, test_code: str, impl_code: str,
                     target_file: str) -> TddCycle:
        """GREEN: 最小实现, 期望通过。"""
        t0 = time.time()
        import os
        test_path = os.path.join(self._test_dir, f"test_{target_file[:-3]}.py")
        impl_path = os.path.join(self._test_dir, target_file)

        # 写入实现
        with open(impl_path, "w") as f:
            f.write(impl_code)

        # 更新测试文件添加 import
        full_test = f"""from {target_file[:-3]} import *\n
def test_tdd():
{chr(10).join('    '+l for l in test_code.split(chr(10)))}
"""
        with open(test_path, "w") as f:
            f.write(full_test)

        try:
            r = subprocess.run(
                [sys.executable, "-m", "pytest", test_path, "-q", "--tb=line"],
                capture_output=True, text=True, timeout=30
            )
            return TddCycle(
                cycle_id=uuid.uuid4().hex[:8], phase="green",
                test_passed=(r.returncode == 0),
                test_output=r.stdout.strip()[-100:] if r.stdout else "",
                duration_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return TddCycle(
                cycle_id=uuid.uuid4().hex[:8], phase="green",
                test_passed=False, test_output=str(e)[:100],
                duration_ms=(time.time() - t0) * 1000,
            )

    def _phase_refactor(self, target_file: str) -> TddCycle:
        """REFACTOR: 重塑代码结构, 测试继续通过。"""
        t0 = time.time()
        import os
        test_path = os.path.join(self._test_dir, f"test_{target_file[:-3]}.py")

        try:
            r = subprocess.run(
                [sys.executable, "-m", "pytest", test_path, "-q", "--tb=line"],
                capture_output=True, text=True, timeout=30
            )
            return TddCycle(
                cycle_id=uuid.uuid4().hex[:8], phase="refactor",
                test_passed=(r.returncode == 0),
                test_output=r.stdout.strip()[-100:] if r.stdout else "",
                duration_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return TddCycle(
                cycle_id=uuid.uuid4().hex[:8], phase="refactor",
                test_passed=False, test_output=str(e)[:100],
                duration_ms=(time.time() - t0) * 1000,
            )

    def search(self, query: str, **kwargs) -> dict:
        return self.report()

    def report(self) -> dict:
        return {
            "status": "ok",
            "total_runs": len(self._history),
            "last_green": self._history[-1].final_green if self._history else None,
        }
