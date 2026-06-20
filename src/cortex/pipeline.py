"""Pipeline — 统一执行链 (感知-行动循环)

Sense → Cortex → Motor 三级流水线。
MCP 工具通过依赖注入传入，运行时由 Reasonix 环境提供。
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time
import uuid


# ── 数据结构 ──

@dataclass
class PipelineStage:
    name: str
    status: str = "pending"
    duration_ms: float = 0.0
    summary: str = ""
    error: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    trace_id: str = ""
    query: str = ""
    species: str = ""
    stages: Dict[str, PipelineStage] = field(default_factory=dict)
    total_duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def completed(self) -> int:
        return sum(1 for s in self.stages.values() if s.status == "completed")

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "query": self.query,
            "species": self.species,
            "stages": {k: asdict(v) for k, v in self.stages.items()},
            "total_duration_ms": round(self.total_duration_ms, 1),
            "completed": self.completed,
            "failed": sum(1 for s in self.stages.values() if s.status == "failed"),
        }


# ── Sense 工厂 ──

class SenseFactory:
    """感受器工厂 — 注入 MCP 工具或创建 stub。"""

    @staticmethod
    def create_scholar(search_fn: Optional[Callable] = None):
        from src.senses import ScholarSense
        return ScholarSense(search_literature=search_fn)

    @staticmethod
    def create_cnki(search_fn: Optional[Callable] = None):
        from src.senses import CnkiSense
        return CnkiSense(search_cnki=search_fn)

    @staticmethod
    def create_ncbi(search_fn: Optional[Callable] = None):
        from src.senses import NcbiSense
        return NcbiSense(search_pubmed=search_fn)

    @staticmethod
    def create_fishbase(search_fn: Optional[Callable] = None):
        from src.senses import FishBaseSense
        return FishBaseSense(search_fishbase=search_fn)

    @staticmethod
    def create_web(search_fn: Optional[Callable] = None):
        from src.senses import WebSense
        return WebSense(search_web=search_fn)

    @staticmethod
    def all_senses():
        """返回所有感受器 (stub 模式)。"""
        from src.senses import ScholarSense, CnkiSense, NcbiSense, FishBaseSense, WebSense
        return [
            ("scholar", ScholarSense()),
            ("cnki", CnkiSense()),
            ("ncbi", NcbiSense()),
            ("fishbase", FishBaseSense()),
            ("web", WebSense()),
        ]


# ── 记忆初始化 ──

_KB_INSTANCE = None


def get_knowledge_base(db_path: Optional[str] = None):
    """获取或初始化知识库实例 (单例)。"""
    global _KB_INSTANCE
    if _KB_INSTANCE is not None:
        return _KB_INSTANCE

    from src.memory.kb import KnowledgeDB
    if db_path:
        path = Path(db_path)
    else:
        path = Path(__file__).resolve().parent.parent.parent / "data" / "species.db"

    if path.exists():
        _KB_INSTANCE = KnowledgeDB(str(path))
    else:
        _KB_INSTANCE = KnowledgeDB(":memory:")
    return _KB_INSTANCE


# ── 管道 ──

class Pipeline:
    """感知-行动循环的统一调度器。

    用法:
        p = Pipeline()
        # 注入 MCP 工具:
        p.inject_sense("scholar", search_literature=my_search_fn)
        # 运行:
        result = p.run("鳤", species="Ochetobius elongatus")
    """

    def __init__(self):
        self.trace_id = uuid.uuid4().hex
        self._sense_map: Dict[str, Any] = {}
        self._kb = None

    def inject_sense(self, name: str, **kwargs):
        """注入感受器的 MCP 工具。"""
        factory_map = {
            "scholar": SenseFactory.create_scholar,
            "cnki": SenseFactory.create_cnki,
            "ncbi": SenseFactory.create_ncbi,
            "fishbase": SenseFactory.create_fishbase,
            "web": SenseFactory.create_web,
        }
        factory = factory_map.get(name)
        if factory:
            self._sense_map[name] = factory(**kwargs)

    def inject_mcp(self, mcp_tools: Dict[str, Callable]):
        """批量注入 MCP 工具字典。"""
        mapping = {
            "search_literature": "scholar",
            "search_cnki": "cnki",
            "search_pubmed": "ncbi",
            "search_fishbase": "fishbase",
            "search_web": "web",
        }
        for mcp_name, sense_name in mapping.items():
            if mcp_name in mcp_tools:
                self.inject_sense(sense_name, **{mcp_name: mcp_tools[mcp_name]})

    def use_kb(self, db_path: str):
        """设置知识库路径。"""
        self._kb = db_path

    def run(self, query: str, species: str = "", sense_only: bool = False) -> PipelineResult:
        t0 = time.time()
        result = PipelineResult(
            trace_id=self.trace_id, query=query, species=species or query
        )

        # Phase 1: 并行感知
        result.stages["sense"] = self._phase_sense_parallel(query, species)

        if sense_only:
            result.total_duration_ms = round((time.time() - t0) * 1000, 1)
            return result

        # Phase 2: 认知处理
        sense_data = result.stages["sense"].data
        result.stages["kb_lookup"] = self._phase_kb_lookup(query, species)

        # Phase 2a: 分支认知 (Dendritic Branch Cognition)
        # 每个感知通道独立进行辩证综合，模拟树突分支的独立计算
        result.stages["branch_cognition"] = self._phase_branch_cognition(sense_data)

        # Phase 2b: 分支汇聚 (Dendritic Branch Convergence)
        # 所有分支结果汇聚融合，模拟胞体级的信号整合
        result.stages["branch_convergence"] = self._phase_branch_convergence(sense_data)

        result.stages["validate"] = self._phase_validate(sense_data)
        result.stages["dialectics"] = self._phase_dialectics(sense_data)
        result.stages["emergent"] = self._phase_emergent(sense_data)

        # Phase 3: 运动输出
        result.stages["report"] = self._phase_report(result)

        # Phase 4: 反射-转座-进化闭环 (RTE)
        result.stages["reflect_transpose_evolve"] = self._phase_reflect_transpose_evolve(sense_data)

        result.total_duration_ms = round((time.time() - t0) * 1000, 1)
        return result

    def _phase_sense_parallel(self, query: str, species: str) -> PipelineStage:
        """并行激活所有感受器。"""
        stage = PipelineStage(name="sense", status="processing")
        t1 = time.time()

        senses = self._sense_map if self._sense_map else SenseFactory.all_senses()
        if isinstance(senses, dict):
            senses = list(senses.items())

        from src.senses import SenseInput
        all_data = {}
        errors = []

        with ThreadPoolExecutor(max_workers=len(senses)) as executor:
            futures = {}
            for name, sense in senses:
                if isinstance(sense, tuple):
                    name, sense = sense
                inp = SenseInput(query=query, species=species or None)
                futures[executor.submit(sense.sense, inp)] = name

            for future in as_completed(futures):
                name = futures[future]
                try:
                    out = future.result()
                    all_data[name] = out.to_dict()
                except Exception as e:
                    errors.append(f"{name}: {e}")

        stage.duration_ms = round((time.time() - t1) * 1000, 1)
        stage.status = "completed" if len(all_data) > 0 else "failed"
        stage.data = all_data
        wired = sum(1 for n, s in senses if getattr(s, 'is_wired', False))
        stage.summary = f"Sensed {len(all_data)}/{len(senses)} channels ({wired} wired, {len(senses)-wired} stub)"
        if errors:
            stage.error = "; ".join(errors[:3])
        return stage

    def _phase_kb_lookup(self, query: str, species: str) -> PipelineStage:
        """知识库查询 (KB-First)."""
        stage = PipelineStage(name="kb_lookup", status="processing")
        t1 = time.time()
        try:
            kb = get_knowledge_base(self._kb)
            species_name = species or query
            row = kb.conn.execute(
                "SELECT scientific, chinese, family FROM species WHERE scientific=? OR chinese=? LIMIT 1",
                (species_name, query)
            ).fetchone()
            stage.status = "completed"
            if row:
                stage.data = dict(row)
                stage.summary = f"KB hit: {row['chinese']} ({row['scientific']})"
            else:
                stage.summary = "KB miss — no local data"
        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)
        stage.duration_ms = round((time.time() - t1) * 1000, 1)
        return stage

    def _phase_branch_cognition(self, sense_data: dict) -> PipelineStage:
        """Phase 2a: 树突分支认知 — 每个感知通道独立辩证综合。

        对应生物学: 树突的每个分支可以独立执行局部计算 (AND/OR/XOR)。
        每个通道的结果暂存，不在此融合。
        """
        stage = PipelineStage(name="branch_cognition", status="processing")
        t1 = time.time()
        branches = {}
        for ch, data in sense_data.items():
            if isinstance(data, dict):
                papers = data.get("papers", data.get("items", []))
                branches[ch] = {
                    "channel": ch,
                    "papers_found": len(papers),
                    "status": data.get("status", "unknown"),
                }
        stage.status = "completed"
        stage.data = branches
        stage.summary = f"Branch cognition: {len(branches)} channels"
        stage.duration_ms = round((time.time() - t1) * 1000, 1)
        return stage

    def _phase_branch_convergence(self, sense_data: dict) -> PipelineStage:
        """Phase 2b: 树突分支汇聚 — 所有分支结果 RRF 融合。

        对应生物学: 所有树突分支的信号在胞体汇聚整合。
        使用 RRF (Reciprocal Rank Fusion) 融合多源结果。
        """
        stage = PipelineStage(name="branch_convergence", status="processing")
        t1 = time.time()
        try:
            all_items = {}
            for ch, data in sense_data.items():
                if isinstance(data, dict):
                    papers = data.get("papers", data.get("items", []))
                    for rank, paper in enumerate(papers):
                        doi = paper.get("doi", paper.get("title", str(rank)))
                        if doi not in all_items:
                            all_items[doi] = 0.0
                        all_items[doi] += 1.0 / (rank + 1)

            ranked = sorted(all_items, key=all_items.get, reverse=True)
            stage.status = "completed"
            stage.data = {"fused_count": len(ranked), "top_sources": ranked[:5]}
            stage.summary = f"Convergence: {len(ranked)} unique items from {len(sense_data)} branches"
        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)
        stage.duration_ms = round((time.time() - t1) * 1000, 1)
        return stage

    def _phase_validate(self, sense_data: dict) -> PipelineStage:
        from src.cortex.validate import ValidateCortex
        stage = PipelineStage(name="validate", status="processing")
        t1 = time.time()
        try:
            engine = ValidateCortex()
            all_papers = []
            for ch, data in sense_data.items():
                papers = data.get("papers", data.get("items", []))
                all_papers.extend(papers)
            result = engine.validate(all_papers)
            stage.status = "completed"
            stage.data = result
            stage.summary = f"Validated {result['stats']['total']} papers"
        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)
        stage.duration_ms = round((time.time() - t1) * 1000, 1)
        return stage

    def _phase_dialectics(self, sense_data: dict) -> PipelineStage:
        from src.cortex.dialectics import DialecticsCortex
        stage = PipelineStage(name="dialectics", status="processing")
        t1 = time.time()
        try:
            engine = DialecticsCortex()
            syntheses = {}
            claims = {}
            weights = {}
            for channel, data in sense_data.items():
                status = data.get("status", "")
                if status == "ok":
                    claims[channel] = status
                    weights[channel] = 0.8 if channel in ("scholar", "ncbi") else 0.5
            if claims:
                syntheses["overall"] = engine.synthesize(
                    "service_status", claims, weights
                ).to_dict()
            stage.status = "completed"
            stage.data = {"syntheses": syntheses}
            stage.summary = f"Synthesis: {len(syntheses)} dims"
        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)
        stage.duration_ms = round((time.time() - t1) * 1000, 1)
        return stage

    def _phase_emergent(self, sense_data: dict) -> PipelineStage:
        from src.cortex.emergent import EmergenceMonitor
        stage = PipelineStage(name="emergent", status="processing")
        t1 = time.time()
        try:
            detector = EmergenceMonitor(emergence_threshold_sigma=3.0, min_sources=3)
            metrics = {}
            for channel, data in sense_data.items():
                if isinstance(data, dict):
                    metrics[f"{channel}_found"] = data.get("total", 0)
            # Feed data to monitor
            detector.record("batch_scan", 1.0)
            signals = detector.check_emergence()
            stage.status = "completed"
            stage.data = {"signals": [str(s) for s in signals]} if signals else {"signals": []}
            stage.summary = f"Emergence: {len(signals)} signals" if signals else "Emergence: normal"
        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)
        stage.duration_ms = round((time.time() - t1) * 1000, 1)
        return stage

    def _phase_report(self, result: PipelineResult) -> PipelineStage:
        from src.motor.report import ReportGenerator
        stage = PipelineStage(name="report", status="completed")
        reporter = ReportGenerator()
        stage.summary = f"Pipeline {result.trace_id[:8]}: {result.completed}/{len(result.stages)} stages"
        stage.data = {"report": reporter.generate(result.to_dict(), format="markdown")}
        return stage

    def _phase_reflect_transpose_evolve(self, sense_data: dict) -> PipelineStage:
        """Phase 4: 反射-转座-进化闭环 (Reflect-Transpose-Evolve)。

        每次查询后自动运行:
          1. 评估认知压力 (从感知阶段的矛盾/错误率)
          2. 将成功的推理模式转座到相关领域
          3. 检测驯化机会 → 提交进化提案

        对应生物学: 突触可塑性 → TE 转座 → 基因组适应性进化。
        """
        stage = PipelineStage(name="reflect_transpose_evolve", status="processing")
        t1 = time.time()

        try:
            # 1. 计算认知压力: 从感知结果推导 uncertainty/confusion
            error_count = sum(1 for ch, d in sense_data.items()
                            if isinstance(d, dict) and d.get("errors"))
            total_channels = max(len(sense_data), 1)
            uncertainty = min(1.0, error_count / total_channels * 1.5)

            contradictory = sum(1 for ch, d in sense_data.items()
                              if isinstance(d, dict) and len(d.get("papers", [])) > 5)
            confusion = min(1.0, contradictory / total_channels)

            # 2. 运行转座层
            from src.cortex.transposition import TranspositionLayer
            tl = TranspositionLayer()
            tl.set_stress_level(uncertainty=uncertainty, confusion=confusion)

            # 转座: 从高频通道到低频通道
            channels = [ch for ch in sense_data.keys()]
            transpositions = 0
            for i in range(len(channels)):
                for j in range(len(channels)):
                    if i != j and tl.current_activity > 0.3:
                        pattern = {
                            "type": "search_strategy",
                            "concept": f"{channels[i]}→{channels[j]}",
                            "confidence": max(0.3, 1.0 - uncertainty),
                        }
                        event = tl.transpose(channels[i], channels[j], pattern)
                        if event.success:
                            transpositions += 1

            # 3. 驯化检测 → 进化提案
            domesticated = tl.get_domesticated_pathways()
            from src.cortex.evolution import EvolutionEngine
            evo = EvolutionEngine()
            proposals = []
            for dp in domesticated:
                if dp.success_count >= 2:  # 至少成功 2 次才提案
                    prop = evo.propose_domestication(
                        dp.source_domain, dp.target_domain,
                        dp.pattern_type, dp.avg_fitness_delta,
                        dp.success_count,
                    )
                    proposals.append(prop.description)

            # 4. 修剪: 清理低 fitness 转座通路 (树状分支原理)
            pruned = tl.prune()
            # 亲缘传播: 驯化通路提升邻域权重
            propagated = 0
            for dp in domesticated[:1]:  # 每次只传播最强的那个
                propagated = tl.propagate_domestication(
                    dp.source_domain, dp.target_domain
                )

            stage.status = "completed"
            stage.summary = (
                f"RTE: stress={uncertainty:.1f}/{confusion:.1f}, "
                f"transposed={transpositions}, "
                f"domesticated={len(proposals)}, "
                f"pruned={pruned}, propagated={propagated}"
            )
            stage.data = {
                "uncertainty": round(uncertainty, 3),
                "confusion": round(confusion, 3),
                "transpositions": transpositions,
                "proposals": proposals,
            }

        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)

        stage.duration_ms = round((time.time() - t1) * 1000, 1)
        return stage

    def search(self, query: str, species: str = "", **kwargs) -> dict:
        result = self.run(query, species)
        return result.to_dict()
