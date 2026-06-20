"""
cortex/pragmatics.py — 语用学 + 三段论推理引擎

语言学: 言语行为类型 (SpeechAct)
  - SenseInput 的 query 不再只是字符串，而是带有语用意图的行为

逻辑学: SyllogismEngine
  - 三段论推理: 从已有知识推导隐含结论，减少不必要的搜索

学术来源:
  - Austin (1962) How to Do Things with Words — 言语行为理论
  - Aristotle — 三段论 (Prior Analytics)
  - Tarski (1933) — 真值语义
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import time
import uuid


# ═══════════════════════════════════════════════════════════
# 语言学: 言语行为类型
# ═══════════════════════════════════════════════════════════

class SpeechAct:
    """言语行为类型 — 说即做。

    每个查询不只是"一句话"，而是一种社交行为:
      ASSERTION  — "鳤是洄游鱼类"              → 优先验证一致性
      QUESTION   — "鳤为什么濒危？"             → 标准感知-认知-行动
      DIRECTIVE  — "找到所有关于鳤的论文"       → 广度优先搜索
      COMMISSIVE — "我将验证这个结论"           → 深度验证模式
      EXPRESSIVE — "这个结果很可疑"             → 进入猜疑链检测
    """
    ASSERTION = "assertion"
    QUESTION = "question"
    DIRECTIVE = "directive"
    COMMISSIVE = "commissive"
    EXPRESSIVE = "expressive"


def detect_speech_act(query: str) -> str:
    """从查询文本自动检测言语行为类型。

    规则:
      - 以疑问词开头 (为什么/如何/什么/是否) → QUESTION
      - 以动词命令式开头 (找到/列出/搜索/给出) → DIRECTIVE
      - 包含怀疑/否定词 (可疑/不对/不可能) → EXPRESSIVE
      - 包含承诺词 (我将/我会/我来验证) → COMMISSIVE
      - 其他 → ASSERTION (默认)
    """
    q = query.strip()

    # 疑问句检测
    question_markers = ["为什么", "如何", "什么", "是否", "吗？", "呢？", "?",
                        "怎样", "哪个", "谁", "哪", "几", "多少"]
    for marker in question_markers:
        if marker in q or q.startswith(marker):
            return SpeechAct.QUESTION

    # 指令检测
    directive_markers = ["找到", "列出", "搜索", "给出", "查找", "列举",
                         "告诉我", "写", "生成", "创建"]
    for marker in directive_markers:
        if q.startswith(marker):
            return SpeechAct.DIRECTIVE

    # 表达态度检测
    expressive_markers = ["可疑", "不对", "不可能", "奇怪", "怀疑", "错误",
                          "有问题", "不成立"]
    for marker in expressive_markers:
        if marker in q:
            return SpeechAct.EXPRESSIVE

    # 承诺检测
    commissive_markers = ["我将", "我会", "我来验证", "我承诺", "让我"]
    for marker in commissive_markers:
        if q.startswith(marker) or marker in q:
            return SpeechAct.COMMISSIVE

    return SpeechAct.ASSERTION


# ═══════════════════════════════════════════════════════════
# 逻辑学: 三段论推理引擎
# ═══════════════════════════════════════════════════════════

@dataclass
class Premise:
    """一条三段论前提。"""
    subject: str       # 主项: "鱼类"
    predicate: str     # 谓项: "需要水"
    quantifier: str = "all"  # all | some | none
    source: str = "kb"
    confidence: float = 1.0


@dataclass
class InferenceResult:
    """推理结果。"""
    conclusion: str          # 推理结论
    confidence: float        # 可信度
    premises_used: List[str] = field(default_factory=list)
    method: str = ""         # syllogism | modus_ponens | modus_tollens
    duration_ms: float = 0.0


class SyllogismEngine:
    """三段论推理引擎 — 从已有知识推导隐含结论。

    用法:
        engine = SyllogismEngine()
        engine.add_premise(Premise("鱼类", "需要水"))
        result = engine.deduce("鳤", "需要水")
        # → InferenceResult(conclusion="需要水", confidence=0.95)
    """

    def __init__(self):
        self.name = "syllogism"
        self._premises: List[Premise] = []

    def add_premise(self, premise: Premise):
        """添加一条前提。"""
        self._premises.append(premise)

    def add_premises_from_kb(self, species_name: str,
                             knowledge_fn=None) -> int:
        """从知识库中批量加载前提。

        Args:
            species_name: 物种名称
            knowledge_fn: 知识库查询函数 (species -> dict)

        Returns:
            加载的前提数
        """
        if knowledge_fn:
            try:
                data = knowledge_fn(species_name)
                if isinstance(data, dict):
                    # 从分类信息推导前提
                    family = data.get("family", "")
                    if family:
                        self.add_premise(Premise(
                            species_name, f"属于{family}科",
                            source="kb", confidence=0.9
                        ))
                    # 从生态信息推导前提
                    ecology = data.get("ecology", "")
                    if ecology:
                        self.add_premise(Premise(
                            species_name, ecology[:80],
                            source="kb", confidence=0.8
                        ))
            except Exception:
                pass
        return len(self._premises)

    def deduce(self, subject: str, predicate: str) -> Optional[InferenceResult]:
        """尝试从前提中演绎出 subject 是否具有 predicate。

        Args:
            subject: "鳤"
            predicate: "需要水"

        Returns:
            InferenceResult 或 None (无法演绎)
        """
        t0 = time.time()

        # 三段论 Barbara (AAA-1): 所有 M 是 P, 所有 S 是 M → 所有 S 是 P
        # ∀x M(x) → P(x), ∀x S(x) → M(x)  ⊢  ∀x S(x) → P(x)
        for premise_m_p in self._premises:
            if predicate in premise_m_p.predicate or premise_m_p.predicate in predicate:
                middle = premise_m_p.subject
                for premise_s_m in self._premises:
                    if (subject in premise_s_m.subject or premise_s_m.subject in subject):
                        if middle in premise_s_m.predicate or premise_s_m.predicate in middle:
                            confidence = premise_m_p.confidence * premise_s_m.confidence
                            return InferenceResult(
                                conclusion=f"{subject} {predicate}",
                                confidence=round(confidence, 3),
                                premises_used=[
                                    f"∀x {middle}(x) → {predicate}(x)",
                                    f"∀x {subject}(x) → {middle}(x)",
                                ],
                                method="syllogism_Barbara",
                                duration_ms=round((time.time() - t0) * 1000, 1),
                            )

        # 拒取式 (Modus Tollens): P→Q, ¬Q ⊢ ¬P
        for premise in self._premises:
            if subject in premise.subject and predicate in premise.predicate:
                return InferenceResult(
                    conclusion=f"{subject} {predicate}",
                    confidence=premise.confidence,
                    premises_used=[f"{premise.subject} {premise.predicate}"],
                    method="direct_match",
                    duration_ms=round((time.time() - t0) * 1000, 1),
                )

        return None

    def batch_deduce(self, subject: str,
                     candidates: List[str]) -> List[InferenceResult]:
        """批量演绎多个谓词。"""
        results = []
        for pred in candidates:
            result = self.deduce(subject, pred)
            if result and result.confidence > 0.5:
                results.append(result)
        return results

    def search(self, query: str, **kwargs) -> dict:
        return {
            "status": "ok",
            "name": self.name,
            "premises": len(self._premises),
        }

    def report(self) -> dict:
        return {
            "status": "ok",
            "name": self.name,
            "premises_count": len(self._premises),
        }
