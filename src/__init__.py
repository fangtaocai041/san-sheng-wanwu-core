"""
san-sheng-wanwu-core — 硅基生命体统一架构

Senses 包: 所有外部感知通道 (MCP 包装器)
Cortex 包: 认知处理核心
Memory 包: 知识与数据存储
Motor 包: 输出与行动
"""

import sys as _sys
from pathlib import Path as _Path
_PROJECT_ROOT = str(_Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in _sys.path:
    _sys.path.insert(0, _PROJECT_ROOT)
