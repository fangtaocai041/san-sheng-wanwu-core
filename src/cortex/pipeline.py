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
        result.stages["validate"] = self._phase_validate(sense_data)
        result.stages["dialectics"] = self._phase_dialectics(sense_data)
        result.stages["emergent"] = self._phase_emergent(sense_data)

        # Phase 3: 运动输出
        result.stages["report"] = self._phase_report(result)

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

    def search(self, query: str, species: str = "", **kwargs) -> dict:
        result = self.run(query, species)
        return result.to_dict()
