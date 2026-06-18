"""Visualizer — 数据可视化输出"""

from __future__ import annotations
from typing import Any, Dict, List, Optional


class Visualizer:
    """将感知数据和认知结果可视化。
    
    通过 echarts-mcp 生成图表。
    """

    def __init__(self):
        self.name = "visualizer"

    def species_traits_radar(self, traits: Dict[str, float]) -> dict:
        """生成物种性状雷达图配置。"""
        return {
            "type": "radar",
            "data": [{"name": k, "value": v} for k, v in traits.items()],
            "title": "物种性状轮廓",
        }

    def search_timeline(self, papers_by_year: Dict[int, int]) -> dict:
        """生成论文发表时间线。"""
        data = [{"time": str(year), "value": count} for year, count in sorted(papers_by_year.items())]
        return {
            "type": "area",
            "data": data,
            "title": "文献发表时间分布",
        }

    def conflict_matrix(self, syntheses: List[dict]) -> dict:
        """生成矛盾矩阵图。"""
        return {
            "type": "heatmap",
            "data": [],
            "title": "跨源矛盾矩阵",
        }
