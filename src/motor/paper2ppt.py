"""
motor/paper2ppt.py — 论文→演示文稿转换器

对应 Codex 科研工作流: nature-paper2ppt (汇报)

功能:
  1. 将研究结论转换为幻灯片结构
  2. 自动生成标题页/背景/方法/结果/讨论/结论
  3. 支持 Markdown 输出,可导入 PowerPoint/Google Slides

使用:
    ppt = Paper2Ppt()
    slides = ppt.convert(title="鳤的种群动态研究", abstract="...", results="...")
    print(slides)  # Markdown 格式, 每页用 --- 分隔
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime


class Paper2Ppt:
    """论文→演示文稿转换器。

    将研究结果自动重组为可演示的幻灯片结构。
    输出为 Markdown, 每个 `---` 分隔符代表一页幻灯片。
    可导入 PowerPoint (Paste Special) 或 Google Slides。
    """

    MAX_BULLETS_PER_SLIDE = 5
    MAX_CHARS_PER_SLIDE = 500

    def __init__(self):
        self.name = "paper2ppt"

    def convert(self, title: str = "", abstract: str = "",
                methods: str = "", results: str = "",
                conclusion: str = "", references: str = "") -> str:
        """将论文段落转换为演示文稿 Markdown。

        Returns:
            Markdown 格式, `---` 分隔每页幻灯片
        """
        slides = []

        # Slide 1: 标题页
        slides.append(f"# {title or '研究报告'}\n\n{abstract[:300]}")

        # Slide 2: 研究背景
        bg = self._extract_background(abstract)
        slides.append(f"## 研究背景\n\n{bg}")

        # Slide 3: 方法
        if methods:
            slides.append(f"## 方法\n\n{methods[:400]}")

        # Slide 4-5: 结果 (可能分多页)
        if results:
            result_slides = self._split_results(results)
            for i, rs in enumerate(result_slides):
                slides.append(f"## 结果 ({i+1}/{len(result_slides)})\n\n{rs[:400]}")

        # Slide 6: 讨论与局限
        slides.append(f"## 讨论与局限\n\n- 主要发现\n- 局限性\n- 未来方向")

        # Slide 7: 结论
        if conclusion:
            slides.append(f"## 结论\n\n{conclusion[:400]}")
        else:
            slides.append(f"## 结论\n\n{abstract[:200]}")

        # Slide 8: 致谢
        slides.append("## 致谢\n\n感谢所有贡献者和审稿人。")

        return "\n\n---\n\n".join(slides)

    def _extract_background(self, abstract: str) -> str:
        """从摘要中提取研究背景 (第一句)。"""
        if not abstract:
            return "本研究聚焦于物种智能分析领域。"
        sentences = abstract.split("。")
        return sentences[0] + "。" if sentences[0] else abstract[:200]

    def _split_results(self, results: str) -> List[str]:
        """将结果拆分为多个幻灯片 (每页最多 5 行要点)。"""
        lines = [l.strip("- ").strip() for l in results.split("\n") if l.strip()]
        if not lines:
            return [results[:400]]
        slides = []
        for i in range(0, len(lines), self.MAX_BULLETS_PER_SLIDE):
            chunk = "\n".join(f"- {l}" for l in lines[i:i + self.MAX_BULLETS_PER_SLIDE])
            slides.append(chunk)
        return slides or [results[:400]]

    def convert_from_pipeline(self, pipeline_result: dict) -> str:
        """从 Pipeline 结果直接生成演示文稿。"""
        title = pipeline_result.get("query", "研究报告")
        stages = pipeline_result.get("stages", {})

        # 从各阶段提取信息
        kb = stages.get("kb_lookup", {})
        dialectics = stages.get("dialectics", {})
        emergent = stages.get("emergent", {})

        abstract = f"关于{title}的多源综合分析。"
        results_parts = []

        kb_data = kb.get("data", {})
        if isinstance(kb_data, dict):
            if kb_data.get("chinese"):
                results_parts.append(f"知识库匹配: {kb_data['chinese']}")
            if kb_data.get("family"):
                results_parts.append(f"科属: {kb_data['family']}")

        dialectics_data = dialectics.get("data", {})
        if isinstance(dialectics_data, dict):
            syntheses = dialectics_data.get("syntheses", {})
            for k, v in syntheses.items():
                if isinstance(v, dict):
                    results_parts.append(f"辩证综合 {k}: {v.get('synthesis', '')}")

        emergent_data = emergent.get("data", {})
        if isinstance(emergent_data, dict):
            signals = emergent_data.get("signals", [])
            if signals:
                results_parts.append(f"涌现信号: {len(signals)} 个")

        results = "\n".join(results_parts) if results_parts else "分析完成"
        conclusion = f"对{title}的多源分析已完成。"
        return self.convert(title=title, abstract=abstract,
                          results=results, conclusion=conclusion)

    def search(self, query: str, **kwargs) -> dict:
        slides = self.convert(title=query)
        return {
            "status": "ok",
            "slides": slides.split("\n\n---\n\n"),
            "slide_count": len(slides.split("\n\n---\n\n")),
        }

    def report(self) -> dict:
        return {"status": "ok", "name": self.name}
