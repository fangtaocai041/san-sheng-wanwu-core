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

    def rte_cycle(self, rte_history: List[Dict[str, Any]]) -> dict:
        """生成反射-转座-进化闭环时序图。

        显示每次查询后的:
          - 转座活性 (Transposition Activity)
          - 驯化通路数 (Domesticated Pathways)
          - 累积进化事件 (Evolution Events)

        Args:
            rte_history: SiliconAgent._rte_history 中的记录列表

        Returns:
            ECharts 折线图配置
        """
        if not rte_history:
            return {"type": "line", "data": [], "title": "RTE 闭环 (无数据)"}

        activity_data = []
        domesticated_data = []
        for i, entry in enumerate(rte_history):
            activity_data.append({
                "time": f"Q{i+1}",
                "value": round(entry.get("tl_activity", 0), 3),
            })
            domesticated_data.append({
                "time": f"Q{i+1}",
                "value": entry.get("domesticated", 0),
            })

        return {
            "type": "line",
            "series": [
                {"name": "转座活性", "data": activity_data},
                {"name": "驯化通路", "data": domesticated_data},
            ],
            "title": "RTE 闭环演化",
            "x_label": "查询次数",
            "y_label": "值",
        }
