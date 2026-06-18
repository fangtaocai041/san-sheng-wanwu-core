"""
cortex/cosmic.py — 宇宙社会学: 刘慈欣概念框架的代码化实现

从《三体》《黑暗森林》《死神永生》中提取的认知模式,
转化为可执行的算法结构。不是哲学隐喻——是计算模式。

核心公理 (宇宙社会学 → 知识社会学):
  公理1: 认知的生存是智能的第一需要 (任何结论都要可复现)
  公理2: 认知资源是有限的 (带宽/时间/能量)

概念清单:
  黑暗森林     — 多源独立性检测与信任衰减
  猜疑链       — 跨源验证的信任传递衰减
  降维打击     — 高维数据投影到可分析低维
  智子         — 常驻监测器 (全通道背景感知)
  技术爆炸     — 递归自改进 (测试→修复→回归)
  威慑         — 测试套件即威慑 (改变代码→测试失败)
  归零者       — 系统重置 (缓存清除/知识库重载)
  曲率驱动     — 搜索空间优化 (弯曲查询空间)
  二向箔       — 复杂问题平面化 (投影到简单表示)
  黑暗森林打击  — 熔断机制 (永不可信来源标记)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from datetime import datetime
import math
import time
import uuid


# ═══════════════════════════════════════════════════════════════
# 基础数据结构
# ═══════════════════════════════════════════════════════════════

@dataclass
class SourceRecord:
    """一个信息来源在黑暗森林中的记录。

    每个源是一个"文明"——有自己的偏见、延迟、盲区。
    黑暗森林法则: 任何源都可能是猎人, 也可能是猎物。
    """
    name: str
    trust: float = 0.5          # 初始信任 0-1 (中性)
    hits: int = 0               # 正确次数
    misses: int = 0             # 错误/矛盾次数
    last_seen: str = ""
    blacklisted: bool = False   # 被黑暗森林打击标记
    blacklist_reason: str = ""  # 打击原因

    @property
    def reliability(self) -> float:
        """源的可信度 = Beta 后验期望。

        使用 Beta(1+hits, 1+misses) 分布。
        新源默认为 0.5 (无先验偏见)。
        """
        if self.hits + self.misses == 0:
            return 0.5
        alpha = 1.0 + self.hits
        beta = 1.0 + self.misses
        return alpha / (alpha + beta)


@dataclass
class CosmicEvent:
    """宇宙事件记录。"""
    type: str        # strike | deterrence | explosion | return | dimensional_attack
    source: str = ""    # 事件源
    target: str = ""    # 事件目标
    description: str = ""
    severity: float = 0.0  # 0-1
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ═══════════════════════════════════════════════════════════════
# 核心引擎
# ═══════════════════════════════════════════════════════════════

class CosmicSociologyEngine:
    """宇宙社会学引擎 — 知识空间中的文明交互。

    将每个知识源视为一个"文明", 每个搜索视为一次"广播",
    每次验证是一次"外交接触"。
    """

    def __init__(self):
        self.name = "cosmic_sociology"
        self._sources: Dict[str, SourceRecord] = {}
        self._events: List[CosmicEvent] = []
        self._chain_of_suspicion_decay = 0.85  # 猜疑链衰减系数

    # ── 来源管理 ──

    def register_source(self, name: str, initial_trust: float = 0.5) -> SourceRecord:
        """注册一个新的信息来源。"""
        src = SourceRecord(name=name, trust=initial_trust)
        self._sources[name] = src
        return src

    def get_source(self, name: str) -> Optional[SourceRecord]:
        return self._sources.get(name)

    def all_sources(self) -> List[SourceRecord]:
        return list(self._sources.values())

    # ── 黑暗森林法则 ──

    def dark_forest_check(self, values: Dict[str, Any]) -> Dict[str, Any]:
        """黑暗森林状态检查: 检测独立源的共识程度。

        输入: {source_name: value}
        输出:
          - consensus: 共识值 (加权投票)
          - consensus_level: 共识强度 (0-1)
          - outliers: 偏离共识的源
          - strikes: 被标记的源
        """
        if not values:
            return {"consensus": None, "consensus_level": 0.0,
                    "outliers": [], "strikes": []}

        # 加权投票
        weight_sum = 0.0
        value_weights: Dict[str, float] = {}
        for src_name, value in values.items():
            src = self._sources.get(src_name)
            if src and src.blacklisted:
                continue  # 被打击的源不参与投票
            weight = src.reliability if src else 0.5
            key = str(value)
            value_weights[key] = value_weights.get(key, 0.0) + weight
            weight_sum += weight

        if weight_sum == 0:
            return {"consensus": None, "consensus_level": 0.0,
                    "outliers": [], "strikes": []}

        # 共识 = 权重最高的值
        consensus_value = max(value_weights, key=value_weights.get)
        consensus_weight = value_weights[consensus_value]
        consensus_level = consensus_weight / weight_sum

        # 检测离群值
        outliers = []
        strikes = []
        for src_name, value in values.items():
            src = self._sources.get(src_name)
            if src and src.blacklisted:
                continue
            if str(value) != consensus_value:
                outliers.append(src_name)
                # 离群 → 记录一次 miss
                if src:
                    src.misses += 1
                    src.last_seen = datetime.now().isoformat()
                    # 如果 reliability 降为 0 → 黑暗森林打击
                    if src.reliability < 0.1:
                        self._dark_forest_strike(src_name,
                            reason=f"可靠性降至 {src.reliability:.2f}")
                        strikes.append(src_name)
            else:
                if src:
                    src.hits += 1
                    src.last_seen = datetime.now().isoformat()

        return {
            "consensus": consensus_value,
            "consensus_level": round(consensus_level, 3),
            "outliers": outliers,
            "strikes": strikes,
        }

    def _dark_forest_strike(self, source_name: str, reason: str = ""):
        """黑暗森林打击: 标记一个源为永不可信。"""
        src = self._sources.get(source_name)
        if src:
            src.blacklisted = True
            src.blacklist_reason = reason
            self._events.append(CosmicEvent(
                type="strike",
                source=source_name,
                description=f"黑暗森林打击: {source_name}. 原因: {reason}",
                severity=1.0,
            ))

    # ── 猜疑链 ──

    def chain_of_suspicion(self, source_chain: List[str]) -> float:
        """猜疑链信任衰减。

        当通过链式验证时 (A→B→C→D), 信任随链长指数衰减。
        trust = trust_orig * decay^chain_length

        参数:
          source_chain: [源头, 验证者1, 验证者2, ...]

        返回: 最终信任值 (0-1)
        """
        if not source_chain:
            return 0.0
        base_trust = self._sources.get(source_chain[0], SourceRecord(name=source_chain[0])).reliability
        chain_length = len(source_chain) - 1
        decayed = base_trust * (self._chain_of_suspicion_decay ** chain_length)
        return round(decayed, 3)

    # ── 降维打击 ──

    def dimensional_reduction(self, data: Dict[str, List[float]],
                               method: str = "projection") -> Dict[str, Any]:
        """降维打击: 将高维数据投影到低维空间进行分析。

        在知识空间中: 当多个维度的数据无法直接比较时,
        投影到可比较的低维空间。

        参数:
          data: {dimension_name: [values]}
          method: "projection" | "consensus"

        返回:
          {dimension: {original, projected, info_loss}}
        """
        results = {}
        for dim, values in data.items():
            if not values:
                continue
            if method == "projection":
                # 投影 = 归一化到 [0, 1]
                mn, mx = min(values), max(values)
                if mx - mn == 0:
                    projected = [0.5 for _ in values]
                else:
                    projected = [(v - mn) / (mx - mn) for v in values]
                info_loss = 1.0 - (len(set(projected)) / max(len(set(values)), 1))
            elif method == "consensus":
                mean_v = sum(values) / len(values)
                projected = [round(1.0 / (1.0 + abs(v - mean_v)), 3) for v in values]
                info_loss = 0.0
            else:
                projected = values
                info_loss = 0.0

            results[dim] = {
                "original_count": len(values),
                "projected": projected,
                "info_loss": round(info_loss, 3),
            }

        return results

    # ── 归零者 (系统重置) ──

    def return_to_zero(self, keep_sources: bool = True) -> Dict[str, Any]:
        """归零者: 系统重置。

        清空事件记录, 可选重置所有来源的信任状态。
        """
        stats = {
            "sources_cleared": len(self._sources),
            "events_cleared": len(self._events),
        }
        self._events = []
        if not keep_sources:
            for src in self._sources.values():
                src.hits = 0
                src.misses = 0
                src.blacklisted = False
                src.blacklist_reason = ""
            stats["trust_reset"] = True
        self._events.append(CosmicEvent(
            type="return",
            description="归零者触发: 系统重置",
            severity=0.5,
        ))
        return stats

    # ── 智子 (常驻监测) ──

    def sophon_monitor(self, sense_data: Dict[str, Any]) -> Dict[str, Any]:
        """智子: 全通道常驻感知监测。

        持续监测所有感受器通道的状态：
          - 哪些通道活动/静默
          - 各通道的响应延迟
          - 异常模式检测
        """
        active = 0
        silent = 0
        delays = []
        for channel, data in sense_data.items():
            if isinstance(data, dict) and data.get("status") == "ok":
                active += 1
                if "duration_ms" in data:
                    delays.append(data["duration_ms"])
            else:
                silent += 1

        return {
            "active_channels": active,
            "silent_channels": silent,
            "total_channels": active + silent,
            "avg_delay_ms": round(sum(delays) / max(len(delays), 1), 1) if delays else 0,
            "alert": silent > active,  # 静默通道多于活动 → 警报
        }

    # ── 降维打击: 矛盾解决 ──

    def dimensional_attack(self, claims: Dict[str, str]) -> Dict[str, Any]:
        """矛盾降维打击: 将不同维度的声明投影到同一尺度。

        当来源A说"保护等级=LC", 来源B说"保护等级=EN"时,
        这不是冲突——它们是不同维度 (全球vs中国) 的投影。

        输出: 更高维度的综合理解
        """
        if not claims:
            return {"synthesis": "无数据", "dimensions": []}

        # 将不同声明分类到维度
        dimensions: Dict[str, list] = {}
        for src, value in claims.items():
            dim = "未知"
            if "iucn" in src.lower():
                dim = "全球评估"
            elif "china" in src.lower() or "chinese" in src.lower():
                dim = "中国评估"
            elif "cites" in src.lower():
                dim = "国际贸易管制"
            elif "fishbase" in src.lower():
                dim = "生态评估"
            dimensions.setdefault(dim, []).append(f"{src}={value}")

        # 生成综合理解
        if len(dimensions) >= 2:
            synthesis = f"多维综合: " + "; ".join(
                f"{dim}下有{len(v)}个声明" for dim, v in dimensions.items()
            )
        else:
            synthesis = f"单维: " + "; ".join(
                f"{dim}={claims.get(list(claims.keys())[0], '?')}"
                for dim in dimensions
            )

        return {
            "synthesis": synthesis,
            "dimensions": list(dimensions.keys()),
            "dimension_count": len(dimensions),
            "original_claims": claims,
        }

    # ── 工具接口 ──

    def source_summary(self) -> str:
        """生成所有来源的黑暗森林状态报告。"""
        lines = ["## 黑暗森林状态报告", ""]
        for src in sorted(self._sources.values(), key=lambda s: s.reliability):
            status = "🛡️ 正常" if not src.blacklisted else "💀 已被打击"
            lines.append(
                f"- {src.name}: "
                f"可信度 {src.reliability:.1%} | "
                f"H/M {src.hits}/{src.misses} | "
                f"{status}"
            )
        lines.append(f"\n宇宙事件记录: {len(self._events)} 次")
        return "\n".join(lines)

    def search(self, query: str, **kwargs) -> dict:
        """兼容 adapter 接口。"""
        return {
            "status": "ok",
            "engine": self.name,
            "sources": [
                {"name": s.name, "reliability": s.reliability,
                 "blacklisted": s.blacklisted}
                for s in self._sources.values()
            ],
            "events_count": len(self._events),
        }

# ═══════════════════════════════════════════════════════════════
# 独立函数: 可直接使用的宇宙社会学工具
# ═══════════════════════════════════════════════════════════════

def dark_forest_trust(sources: List[str], weights: Optional[List[float]] = None) -> float:
    """计算一组独立源的联合可信度。

    黑暗森林公理: 两个独立源达成共识比一个源可信 N 倍。
    trust = 1 - prod(1 - w_i) 多个独立源
    """
    if not sources:
        return 0.0
    if weights is None:
        weights = [0.5] * len(sources)
    cumulative_doubt = 1.0
    for w in weights:
        cumulative_doubt *= (1.0 - w)
    return 1.0 - cumulative_doubt


def chain_of_suspicion_decay(chain_length: int, base_trust: float = 0.8,
                              decay: float = 0.85) -> float:
    """猜疑链衰减: trust = base * decay^length"""
    return base_trust * (decay ** chain_length)


def dimensional_projection(values: List[float]) -> List[float]:
    """降维投影: 归一化到 [0, 1]"""
    if not values:
        return []
    mn, mx = min(values), max(values)
    if mx == mn:
        return [0.5] * len(values)
    return [(v - mn) / (mx - mn) for v in values]


def technology_explosion_curve(generations: int, base: float = 2.0) -> List[float]:
    """技术爆炸曲线: 递归自改进的 S 型增长。"""
    return [1.0 / (1.0 + math.exp(-base * (i - generations / 2)))
            for i in range(generations)]
