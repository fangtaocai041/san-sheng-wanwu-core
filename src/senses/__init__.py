"""
senses — 感受器层

每个模块对应一个感知通道，将外部信息源的响应
规范化为统一的数据结构送入 cortex。
"""

from .scholar import ScholarSense
from .cnki import CnkiSense
from .ncbi import NcbiSense
from .fishbase import FishBaseSense
from .web import WebSense

__all__ = [
    "ScholarSense", "CnkiSense", "NcbiSense",
    "FishBaseSense", "WebSense",
]
