"""
cortex/veracity.py — 真实性约束引擎

编译进框架底层的三条铁律：
  1. 没有执行证据的话不允许输出结论
  2. "确定"之前必须重新验证
  3. 不知道就输出None，不允许编造

这些不是行为准则——是执行约束。每个输出在返回前经过veracity gate检查。
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
import traceback


class VeracityError(Exception):
    """真实性约束违反。输出被拦截。"""


@dataclass
class Verdict:
    """一条输出声明的验证结果。"""
    statement: str = ""
    evidence: Optional[str] = None
    passed: bool = False
    rejected_reason: str = ""


class VeracityGate:
    """真实性门控。

    使用方式:
        gate = VeracityGate()
        gate.assert_evidence("测试通过", "153 passed in 1.00s")
        # → 通过

        gate.assert_evidence("已推送", None)
        # → VeracityError: "已推送" 无执行证据
    """

    def __init__(self):
        self._log: list[Verdict] = []

    def assert_evidence(self, statement: str, evidence: Any) -> str:
        """规则1: 没有执行证据，不允许输出结论。

        Args:
            statement: 要输出的声明 (如"测试通过")
            evidence: 执行结果 (如 "153 passed")。None = 未执行

        Returns:
            证据字符串 (可原文输出)

        Raises:
            VeracityError: evidence 为 None 或空
        """
        if evidence is None:
            v = Verdict(statement=statement, passed=False,
                       rejected_reason="无执行证据")
            self._log.append(v)
            raise VeracityError(
                f"[VERACITY] 规则1违反: \"{statement}\" 无执行证据。"
                f"运行命令重新验证。"
            )
        evidence_str = str(evidence).strip()
        if not evidence_str:
            v = Verdict(statement=statement, passed=False,
                       rejected_reason="证据为空字符串")
            self._log.append(v)
            raise VeracityError(
                f"[VERACITY] 规则1违反: \"{statement}\" 证据为空。"
            )
        v = Verdict(statement=statement, evidence=evidence_str, passed=True)
        self._log.append(v)
        return evidence_str

    def require_reverify(self, statement: str,
                         current_evidence: Any,
                         verify_fn=None) -> str:
        """规则2: "确定"之前重新验证。

        如果 current_evidence 是旧的或 None，调用 verify_fn 重跑。
        """
        if current_evidence is None and verify_fn is not None:
            current_evidence = verify_fn()
        return self.assert_evidence(statement, current_evidence)

    def reject_unknown(self, query: str) -> None:
        """规则3: 不知道就拒绝，不允许编造。"""
        v = Verdict(statement=query, passed=False,
                   rejected_reason="模型不知道答案")
        self._log.append(v)
        raise VeracityError(
            f"[VERACITY] 规则3违反: 拒绝编造 \"{query}\" 的答案。"
        )

    @property
    def violations(self) -> list[Verdict]:
        return [v for v in self._log if not v.passed]

    @property
    def is_clean(self) -> bool:
        return len(self.violations) == 0

    def report(self) -> dict:
        return {
            "status": "ok" if self.is_clean else "violations",
            "total_checks": len(self._log),
            "violations": [
                {"statement": v.statement, "reason": v.rejected_reason}
                for v in self.violations
            ],
        }
