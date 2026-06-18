"""
motor — 运动皮层: 输出与行动

  report.py     报告生成
  visualize.py  数据可视化 (echarts wrapper)
  deploy.py     部署发布
"""

from .report import ReportGenerator
from .visualize import Visualizer

__all__ = ["ReportGenerator", "Visualizer"]
