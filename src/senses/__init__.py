"""
senses — 感受器层

每个感受器通过 MCP 协议感知外部世界。
依赖注入模式: MCP 工具函数在运行时注入，测试时可用 mock。

内置感受器:
  Scholar/Cnki/Ncbi/FishBase/Web — 外部 MCP 数据通道
  Ocr — 视觉文字识别 (PaddleOCR-VL)

学科领域感受器 (内置知识图谱, 无需 MCP):
  domains.py — 12 个学科领域 (数理化生计算机心理哲马经文中)
"""

from .scholar import ScholarSense, SenseInput, SenseOutput
from .cnki import CnkiSense
from .ncbi import NcbiSense
from .fishbase import FishBaseSense
from .web import WebSense
from .ocr import OcrSense
from .domains import (
    ALL_DOMAIN_SENSES, ALL_DOMAIN_NAMES,
    create_all_domains, create_domain,
    MathSense, PhysicsSense, ChemistrySense, BiologySense,
    ComputerScienceSense, PsychologySense, PhilosophySense,
    ChinesePhilosophySense, MarxismSense, EconomicsSense,
    LiteratureSense, SciFiSense,
)

__all__ = [
    "ScholarSense", "CnkiSense", "NcbiSense",
    "FishBaseSense", "WebSense", "OcrSense",
    "SenseInput", "SenseOutput",
    # 学科领域
    "MathSense", "PhysicsSense", "ChemistrySense", "BiologySense",
    "ComputerScienceSense", "PsychologySense", "PhilosophySense",
    "ChinesePhilosophySense", "MarxismSense", "EconomicsSense",
    "LiteratureSense", "SciFiSense",
    "ALL_DOMAIN_SENSES", "ALL_DOMAIN_NAMES",
    "create_all_domains", "create_domain",
]
