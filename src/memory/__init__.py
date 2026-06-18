"""
memory — 记忆与知识存储

  kb/           物种知识库包 (原 fish-ecology-assistant/fishkb):
                  KnowledgeDB      — SQLite FTS5 物种知识库
                  FishSpeciesMatcher — KB-first 模糊物种匹配
                  CredibilityScorer  — 三角验证文献可信度评分
                  SpeciesVariants    — 物种拼写变体注册表
                  核心类型: AnalysisFinding, SourceEntry, ResearchContext ...
  cache.py      搜索缓存 (LRU, 24h TTL)
  consolidate.py 记忆巩固系统 (MAGMA 四维图谱 + WM/STM/LTM)
  magma.py      四维正交图谱记忆引擎 (语义/时序/因果/实体)
  persistence.py 状态持久化 (SQLite)
"""

from .kb import (
    KnowledgeDB, get_db,
    FishSpeciesMatcher, KbFirstResult, get_matcher,
    CredibilityScorer,
    detect_journal_tier, format_credibility, is_predatory,
    score_paper, score_papers,
    SpeciesVariants, get_variants,
    JOURNAL_WHITELIST, build_search_queries, generate_ocr_variants,
    AnalysisFinding, ConfidenceLevel, EmergenceSignal, EvidenceQuality,
    PipelinePhase, PipelineStats, ResearchContext, ReviewReport,
    ReviewResult, SessionResult, SourceEntry,
)
from .cache import SearchCache
from .consolidate import MemorySystem, MemoryItem, ebbinghaus_forgetting, reinforcement_boost
from .magma import MagmaMemory, MemoryNode, Relation, RelationType
from .persistence import PersistenceEngine, AgentSnapshot

__all__ = [
    "KnowledgeDB", "get_db",
    "FishSpeciesMatcher", "KbFirstResult", "get_matcher",
    "CredibilityScorer",
    "detect_journal_tier", "format_credibility", "is_predatory",
    "score_paper", "score_papers",
    "SpeciesVariants", "get_variants",
    "JOURNAL_WHITELIST", "build_search_queries", "generate_ocr_variants",
    "AnalysisFinding", "ConfidenceLevel", "EmergenceSignal", "EvidenceQuality",
    "PipelinePhase", "PipelineStats", "ResearchContext", "ReviewReport",
    "ReviewResult", "SessionResult", "SourceEntry",
    "SearchCache",
    "MemorySystem", "MemoryItem",
    "ebbinghaus_forgetting", "reinforcement_boost",
    "MagmaMemory", "MemoryNode", "Relation", "RelationType",
    "PersistenceEngine", "AgentSnapshot",
]
