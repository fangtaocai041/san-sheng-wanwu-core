"""
cortex — 认知处理核心

感受器输入 → 皮质加工 → 运动皮层输出

各模块功能:
  dialectics.py  辩证矛盾检测与综合 (原 conflict-arbiter)
  validate.py    文献验证与可信度评估 (原 cognitive-search-engine)
  emergent.py    涌现信号检测 (原 infrastructure/unified_emergence)
  pipeline.py    统一执行链调度
"""

from .dialectics import DialecticsCortex
from .validate import ValidateCortex, calc_trust_score, calc_credibility_score
from .emergent import (
    EmergenceMonitor, DimensionalEmergenceMonitor, EmergenceEngine,
    EmergenceSignal, DetectionResult, DimensionalLevel, EmergenceType,
)
from .pipeline import Pipeline, PipelineResult, PipelineStage

__all__ = [
    "DialecticsCortex",
    "ValidateCortex", "calc_trust_score", "calc_credibility_score",
    "EmergenceMonitor", "DimensionalEmergenceMonitor", "EmergenceEngine",
    "EmergenceSignal", "DetectionResult", "DimensionalLevel", "EmergenceType",
    "Pipeline", "PipelineResult", "PipelineStage",
]
