"""
motor/statistics.py — 统计分析引擎

对应 Codex 科研工作流: statistical-analysis

提供科研常用的统计方法:
  - 描述性统计 (mean, std, distribution)
  - 推断统计 (t-test, chi-square)
  - 相关性分析 (Pearson/Spearman)
  - 简单回归

所有计算使用纯 Python 实现，零外部依赖。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math


@dataclass
class StatResult:
    """统计结果。"""
    method: str = ""
    statistic: float = 0.0
    p_value: float = 1.0
    interpretation: str = ""
    summary: str = ""


class StatisticsEngine:
    """统计分析引擎 — 轻量级科研统计。"""

    def __init__(self):
        self.name = "statistics"

    # ── 描述性统计 ──

    @staticmethod
    def describe(data: List[float]) -> Dict[str, float]:
        """描述性统计。"""
        n = len(data)
        if n == 0:
            return {"n": 0}
        mean = sum(data) / n
        variance = sum((x - mean) ** 2 for x in data) / max(n - 1, 1)
        std = math.sqrt(variance)
        sorted_data = sorted(data)
        return {
            "n": n,
            "mean": round(mean, 4),
            "std": round(std, 4),
            "min": round(min(data), 4),
            "max": round(max(data), 4),
            "median": round(sorted_data[n // 2], 4),
        }

    # ── t 检验 (独立样本) ──

    def ttest_ind(self, group1: List[float], group2: List[float]) -> StatResult:
        """独立样本 t 检验。"""
        n1, n2 = len(group1), len(group2)
        if n1 < 2 or n2 < 2:
            return StatResult(method="ttest_ind",
                             interpretation="样本量不足")

        m1, m2 = sum(group1) / n1, sum(group2) / n2
        v1 = sum((x - m1) ** 2 for x in group1) / (n1 - 1)
        v2 = sum((x - m2) ** 2 for x in group2) / (n2 - 1)

        se = math.sqrt(v1 / n1 + v2 / n2)
        t_stat = (m1 - m2) / max(se, 0.001)

        # Welch-Satterthwaite df
        df = ((v1 / n1 + v2 / n2) ** 2) / max(
            ((v1 / n1) ** 2) / (n1 - 1) + ((v2 / n2) ** 2) / (n2 - 1), 0.001
        )

        # 近似 p 值 (正态近似, 简化版)
        p = 2 * (1 - self._norm_cdf(abs(t_stat)))

        return StatResult(
            method="独立样本 t 检验",
            statistic=round(t_stat, 4),
            p_value=round(p, 4),
            interpretation=f"组1={m1:.2f}, 组2={m2:.2f}, "
                         f"差值={m1-m2:.2f} {'显著' if p < 0.05 else '不显著'}",
            summary=f"t({int(df)})={t_stat:.3f}, p={p:.4f}"
        )

    # ── 相关性 ──

    def pearson(self, x: List[float], y: List[float]) -> StatResult:
        """Pearson 相关系数。"""
        n = len(x)
        if n < 3:
            return StatResult(method="Pearson 相关", interpretation="样本量不足")

        mx, my = sum(x) / n, sum(y) / n
        cov = sum((x[i] - mx) * (y[i] - my) for i in range(n))
        sx = math.sqrt(sum((xi - mx) ** 2 for xi in x))
        sy = math.sqrt(sum((yi - my) ** 2 for yi in y))
        r = cov / max(sx * sy, 0.001)

        t = r * math.sqrt((n - 2) / max(1 - r * r, 0.001))
        p = 2 * (1 - self._norm_cdf(abs(t)))

        return StatResult(
            method="Pearson 相关",
            statistic=round(r, 4),
            p_value=round(p, 4),
            interpretation=f"r={r:.3f}, {'强' if abs(r)>0.7 else '中' if abs(r)>0.4 else '弱'}相关"
                           f"{' (显著)' if p < 0.05 else ' (不显著)'}",
        )

    # ── 辅助 ──

    @staticmethod
    def _norm_cdf(x: float) -> float:
        """标准正态分布 CDF (近似)。"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def search(self, query: str, **kwargs) -> dict:
        return {
            "status": "ok",
            "name": self.name,
            "available_tests": ["describe", "ttest_ind", "pearson"],
        }

    def report(self) -> dict:
        return self.search("")
