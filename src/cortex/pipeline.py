"""Pipeline — 统一执行链 (感知-行动循环)"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime
import time
import uuid


@dataclass
class PipelineStage:
    name: str
    status: str = "pending"  # pending | sensing | processing | completed | failed
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

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "query": self.query,
            "species": self.species,
            "stages": {k: asdict(v) for k, v in self.stages.items()},
            "total_duration_ms": round(self.total_duration_ms, 1),
            "completed": sum(1 for s in self.stages.values() if s.status == "completed"),
            "failed": sum(1 for s in self.stages.values() if s.status == "failed"),
        }


class Pipeline:
    """感知-行动循环的统一调度器。
    
    执行顺序:
      1. sense: 并行激活所有感受器
      2. cortex: 辩证综合 + 验证 + 涌现检测
      3. motor: 输出结果
    """

    def __init__(self):
        self.trace_id = uuid.uuid4().hex

    def run(self, query: str, species: str = "", sense_only: bool = False) -> PipelineResult:
        t0 = time.time()
        result = PipelineResult(
            trace_id=self.trace_id, query=query, species=species or query
        )

        # Phase 1: 感知 — 激活所有感受器
        result.stages["sense"] = self._phase_sense(query, species)

        if sense_only:
            result.total_duration_ms = (time.time() - t0) * 1000
            return result

        # Phase 2: 认知处理
        result.stages["validate"] = self._phase_validate(result.stages["sense"].data)
        result.stages["dialectics"] = self._phase_dialectics(result.stages["sense"].data)
        result.stages["emergent"] = self._phase_emergent(result.stages["sense"].data)

        # Phase 3: 运动输出
        result.stages["report"] = self._phase_report(result)

        result.total_duration_ms = round((time.time() - t0) * 1000, 1)
        return result

    def _phase_sense(self, query: str, species: str) -> PipelineStage:
        """激活所有感受器并行感知。"""
        stage = PipelineStage(name="sense", status="processing")
        t1 = time.time()
        all_data = {}
        errors = []

        from src.senses import ScholarSense, CnkiSense, NcbiSense, FishBaseSense, WebSense
        senses = [
            ("scholar", ScholarSense()),
            ("cnki", CnkiSense()),
            ("ncbi", NcbiSense()),
            ("fishbase", FishBaseSense()),
            ("web", WebSense()),
        ]

        for name, sense in senses:
            try:
                sense_inp = type("SenseInput", (), {
                    "query": query, "species": species or None,
                    "max_results": 10, "sources": [],
                    "time_range": None,
                })()
                result_data = sense.search(query, species=species)
                all_data[name] = result_data
            except Exception as e:
                errors.append(f"{name}: {e}")

        stage.duration_ms = round((time.time() - t1) * 1000, 1)
        stage.status = "completed" if len(all_data) > 0 else "failed"
        stage.data = all_data
        stage.summary = f"Sensed {len(all_data)}/{len(senses)} channels"
        if errors:
            stage.error = "; ".join(errors[:2])
        return stage

    def _phase_validate(self, sense_data: dict) -> PipelineStage:
        """验证感知到的数据。"""
        from src.cortex.validate import ValidateEngine
        stage = PipelineStage(name="validate", status="processing")
        t1 = time.time()
        try:
            engine = ValidateEngine()
            all_papers = []
            for channel, data in sense_data.items():
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
        """辩证综合多源矛盾。"""
        from src.cortex.dialectics import DialecticsEngine
        stage = PipelineStage(name="dialectics", status="processing")
        t1 = time.time()
        try:
            engine = DialecticsEngine()
            syntheses = {}
            # 提取各源头的保护等级声明进行综合
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
            stage.summary = f"Dialectic synthesis: {len(syntheses)} dimensions"
        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)
        stage.duration_ms = round((time.time() - t1) * 1000, 1)
        return stage

    def _phase_emergent(self, sense_data: dict) -> PipelineStage:
        """涌现检测。"""
        from src.cortex.emergent import EmergentDetector
        stage = PipelineStage(name="emergent", status="processing")
        t1 = time.time()
        try:
            detector = EmergentDetector()
            # 构建指标
            metrics = {}
            for channel, data in sense_data.items():
                if isinstance(data, dict):
                    metrics[f"{channel}_found"] = data.get("total", 0)
            signal = detector.detect(metrics)
            stage.status = "completed"
            stage.data = signal
            stage.summary = signal.get("signal", {}).get("description", "No signal") if signal.get("signal") else "Normal"
        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)
        stage.duration_ms = round((time.time() - t1) * 1000, 1)
        return stage

    def _phase_report(self, result: PipelineResult) -> PipelineStage:
        """生成输出报告。"""
        stage = PipelineStage(name="report", status="completed")
        stage.summary = f"Pipeline {result.trace_id[:8]}: {result.completed}/{len(result.stages)} stages"
        stage.data = result.to_dict()
        return stage

    def search(self, query: str, species: str = "", **kwargs) -> dict:
        """兼容旧版 adapter 搜索接口。"""
        result = self.run(query, species)
        return result.to_dict()
