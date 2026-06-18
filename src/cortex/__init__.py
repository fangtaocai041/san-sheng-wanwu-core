"""
cortex — 认知处理核心

感受器输入 → 皮质加工 → 运动皮层输出

各模块功能:
  alignment.py   价值对齐: 价值观配置、冲突检测、决策前检查
  conceptual.py  概念工程: 本体设计追踪、概念溯源
  cosmic.py      宇宙社会学: 刘慈欣概念框架代码化
  dialectics.py  辩证矛盾检测与综合 (原 conflict-arbiter)
  emotion.py     情感引擎: 情感即操作系统 (价值分配)
  evolution.py   自我进化: 代码分析与修改提案 (Phase 3 骨架)
  explanatory.py 可解释性: 推理链记录、多层解释生成 (XAI)
  healing.py     自愈引擎: 健康检查、异常诊断、自动恢复
  learning.py    学习适应: 策略追踪、参数自适应、感受器权重
  soul.py        灵魂引擎: TCSC 不动点 (自我表征收敛)
  swarm.py       群体智能: 多 Agent 通信协议 (发现/消息/协作)
  validate.py    文献验证与可信度评估 (原 cognitive-search-engine)
  emergent.py    涌现信号检测 (原 infrastructure/unified_emergence)
  pipeline.py    统一执行链调度
"""

from .alignment import AlignmentEngine, AlignmentViolation
from .conceptual import ConceptRegistry, Concept, ConceptRelation, ConceptRevision
from .cosmic import (
    CosmicSociologyEngine, SourceRecord, CosmicEvent,
    dark_forest_trust, chain_of_suspicion_decay,
    dimensional_projection, technology_explosion_curve,
)
from .dialectics import DialecticsCortex
from .emotion import EmotionEngine, EmotionalState, EmotionType
from .evolution import EvolutionEngine, ModificationProposal, EvolutionEvent
from .explanatory import ExplainabilityEngine, ReasoningTrace, ReasoningStep
from .healing import HealingEngine, HealthCheck, HealingAction
from .learning import LearningEngine, StrategyRecord, ParameterConfig
from .soul import SoulEngine, SoulState, SelfRepresentation, SelfDimension
from .swarm import SwarmEngine, AgentIdentity, AgentMessage, KnowledgeShare
from .validate import ValidateCortex, calc_trust_score, calc_credibility_score
from .emergent import (
    EmergenceMonitor, DimensionalEmergenceMonitor, EmergenceEngine,
    EmergenceSignal, DetectionResult, DimensionalLevel, EmergenceType,
)
from .pipeline import Pipeline, PipelineResult, PipelineStage

__all__ = [
    # 价值对齐
    "AlignmentEngine", "AlignmentViolation",
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
    # 自我进化
    "EvolutionEngine", "ModificationProposal", "EvolutionEvent",
    # 可解释性
    "ExplainabilityEngine", "ReasoningTrace", "ReasoningStep",
    # 自愈引擎
    "HealingEngine", "HealthCheck", "HealingAction",
    # 学习适应
    "LearningEngine", "StrategyRecord", "ParameterConfig",
    # 灵魂引擎
    "SoulEngine", "SoulState", "SelfRepresentation", "SelfDimension",
    # 群体智能
    "SwarmEngine", "AgentIdentity", "AgentMessage", "KnowledgeShare",
    # 验证
    "ValidateCortex", "calc_trust_score", "calc_credibility_score",
    # 涌现
    "EmergenceMonitor", "DimensionalEmergenceMonitor", "EmergenceEngine",
    "EmergenceSignal", "DetectionResult", "DimensionalLevel", "EmergenceType",
    # 管道
    "Pipeline", "PipelineResult", "PipelineStage",
]
