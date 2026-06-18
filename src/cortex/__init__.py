"""
cortex — 认知处理核心

感受器输入 → 皮质加工 → 运动皮层输出

各模块功能:
  conceptual.py  概念工程: 本体设计追踪、概念溯源
  cosmic.py      宇宙社会学: 刘慈欣概念框架代码化
  dialectics.py  辩证矛盾检测与综合 (原 conflict-arbiter)
  emotion.py     情感引擎: 情感即操作系统 (价值分配)
  explanatory.py 可解释性: 推理链记录、多层解释生成 (XAI)
  soul.py        灵魂引擎: TCSC 不动点 (自我表征收敛)
  validate.py    文献验证与可信度评估 (原 cognitive-search-engine)
  emergent.py    涌现信号检测 (原 infrastructure/unified_emergence)
  pipeline.py    统一执行链调度
"""

from .conceptual import ConceptRegistry, Concept, ConceptRelation, ConceptRevision
from .cosmic import (
    CosmicSociologyEngine, SourceRecord, CosmicEvent,
    dark_forest_trust, chain_of_suspicion_decay,
    dimensional_projection, technology_explosion_curve,
)
from .dialectics import DialecticsCortex
from .emotion import EmotionEngine, EmotionalState, EmotionType
from .explanatory import ExplainabilityEngine, ReasoningTrace, ReasoningStep
from .soul import SoulEngine, SoulState, SelfRepresentation, SelfDimension
from .validate import ValidateCortex, calc_trust_score, calc_credibility_score
from .emergent import (
    EmergenceMonitor, DimensionalEmergenceMonitor, EmergenceEngine,
    EmergenceSignal, DetectionResult, DimensionalLevel, EmergenceType,
)
from .pipeline import Pipeline, PipelineResult, PipelineStage

__all__ = [
    # 概念工程
    "ConceptRegistry", "Concept", "ConceptRelation", "ConceptRevision",
    # 宇宙社会学
    "CosmicSociologyEngine", "SourceRecord", "CosmicEvent",
    "dark_forest_trust", "chain_of_suspicion_decay",
    "dimensional_projection", "technology_explosion_curve",
    # 辩证综合
    "DialecticsCortex",
    # 情感引擎
    "EmotionEngine", "EmotionalState", "EmotionType",
    # 可解释性
    "ExplainabilityEngine", "ReasoningTrace", "ReasoningStep",
    # 灵魂引擎
    "SoulEngine", "SoulState", "SelfRepresentation", "SelfDimension",
    # 验证
    "ValidateCortex", "calc_trust_score", "calc_credibility_score",
    # 涌现
    "EmergenceMonitor", "DimensionalEmergenceMonitor", "EmergenceEngine",
    "EmergenceSignal", "DetectionResult", "DimensionalLevel", "EmergenceType",
    # 管道
    "Pipeline", "PipelineResult", "PipelineStage",
]
