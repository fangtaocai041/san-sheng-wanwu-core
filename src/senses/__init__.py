"""
senses — 感受器层

每个感受器通过 MCP 协议感知外部世界。
依赖注入模式: MCP 工具函数在运行时注入，测试时可用 mock。
"""

from .scholar import ScholarSense, SenseInput, SenseOutput
from .cnki import CnkiSense
from .ncbi import NcbiSense
from .fishbase import FishBaseSense
from .web import WebSense

__all__ = [
    "ScholarSense", "CnkiSense", "NcbiSense",
    "FishBaseSense", "WebSense",
    "SenseInput", "SenseOutput",
]
