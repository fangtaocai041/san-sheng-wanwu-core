"""
cortex — 认知处理核心

感受器输入 → 皮质加工 → 运动皮层输出

各模块功能:
  dialectics.py   辩证矛盾检测与综合 (原 conflict-arbiter)
  validate.py     文献验证与可信度评估 (原 cognitive-search-engine)
  emergent.py     涌现信号检测 (原 infrastructure/unified_emergence)
  pipeline.py     统一执行链调度 (原 eon-core cross_project)
  score.py        综合可信度评分
"""

from .dialectics import DialecticsEngine
from .validate import ValidateEngine
from .emergent import EmergentDetector
from .pipeline import Pipeline

__all__ = [
    "DialecticsEngine", "ValidateEngine",
    "EmergentDetector", "Pipeline",
]
