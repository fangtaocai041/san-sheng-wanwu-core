"""
memory/persistence.py — 硅基生命体状态持久化

保存和加载:
  - 自我模型状态 (SelfModelEngine, DSM 稳定性结果)
  - 情感状态 (EmotionEngine, 6 维向量)
  - 记忆系统 (MemorySystem, STM/LTM 条目)
  - 学习历史 (LearningEngine, 策略记录)
  - 来源信任 (CosmicSociologyEngine, 来源记录)

存储: SQLite + JSON 双保险
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import sqlite3
import time


DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "agent_state.db"


# ── 状态容器 ──

@dataclass
class AgentSnapshot:
    """硅基生命体的完整状态快照。"""
    soul: dict = None
    emotion: dict = None
    memory_stm: List[dict] = None
    memory_ltm: List[dict] = None
    cosmic_sources: List[dict] = None
    learning_history: List[dict] = None
    alignment: dict = None
    saved_at: float = 0.0

    def __post_init__(self):
        if self.saved_at is None:
            self.saved_at = time.time()
        if self.soul is None: self.soul = {}
        if self.emotion is None: self.emotion = {}
        if self.memory_stm is None: self.memory_stm = []
        if self.memory_ltm is None: self.memory_ltm = []
        if self.cosmic_sources is None: self.cosmic_sources = []
        if self.learning_history is None: self.learning_history = []


# ── 持久化引擎 ──

class PersistenceEngine:
    """状态持久化引擎。

    保存: agent.save() → 写入 SQLite + JSON
    加载: agent.load() → 从 SQLite 或 JSON 恢复
    自动保存间隔: auto_save_interval 秒
    """

    def __init__(self, db_path: Optional[str] = None, auto_save_interval: int = 300):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.auto_save_interval = auto_save_interval
        self._last_save = 0.0
        self._init_db()

    def _init_db(self):
        """初始化 SQLite 表结构。"""
        conn = sqlite3.connect(str(self.db_path))
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS agent_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS memory_items (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                strength REAL DEFAULT 1.0,
                access_count INTEGER DEFAULT 0,
                created_at REAL NOT NULL,
                metadata TEXT DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS cosmic_sources (
                name TEXT PRIMARY KEY,
                trust REAL DEFAULT 0.5,
                hits INTEGER DEFAULT 0,
                misses INTEGER DEFAULT 0,
                blacklisted INTEGER DEFAULT 0,
                blacklist_reason TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS learning_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                senses_used TEXT,
                success INTEGER,
                papers_found INTEGER,
                duration_ms REAL,
                quality_score REAL,
                created_at REAL
            );
        """)
        conn.commit()
        conn.close()

    # ── 保存 ──

    def save(self, snapshot: AgentSnapshot):
        """保存完整状态快照。"""
        conn = sqlite3.connect(str(self.db_path))
        now = time.time()

        # 灵魂和情感 → JSON
        self._set(conn, "soul", json.dumps(snapshot.soul), now)
        self._set(conn, "emotion", json.dumps(snapshot.emotion), now)
        self._set(conn, "alignment", json.dumps(snapshot.alignment or {}), now)

        # 记忆 → 逐条插入
        conn.execute("DELETE FROM memory_items")
        for item in snapshot.memory_stm + snapshot.memory_ltm:
            conn.execute(
                "INSERT OR REPLACE INTO memory_items VALUES (?,?,?,?,?,?,?)",
                (item.get("id", ""), item.get("content", ""),
                 item.get("type", "stm"), float(item.get("strength", 1.0)),
                 int(item.get("access_count", 0)),
                 float(item.get("created_at", now)),
                 json.dumps(item.get("metadata", {})))
            )

        # 来源信任 → 逐条插入
        conn.execute("DELETE FROM cosmic_sources")
        for src in snapshot.cosmic_sources:
            conn.execute(
                "INSERT OR REPLACE INTO cosmic_sources VALUES (?,?,?,?,?,?)",
                (src.get("name", ""), float(src.get("trust", 0.5)),
                 int(src.get("hits", 0)), int(src.get("misses", 0)),
                 int(src.get("blacklisted", False)),
                 src.get("blacklist_reason", ""))
            )

        # 学习历史 → 批量插入
        conn.execute("DELETE FROM learning_history")
        for rec in snapshot.learning_history:
            conn.execute(
                "INSERT INTO learning_history(query, senses_used, success, papers_found, duration_ms, quality_score, created_at) VALUES (?,?,?,?,?,?,?)",
                (rec.get("query", ""), json.dumps(rec.get("senses_used", [])),
                 int(rec.get("success", False)), int(rec.get("papers_found", 0)),
                 float(rec.get("duration_ms", 0)), float(rec.get("quality_score", 0)),
                 float(rec.get("created_at", now)))
            )

        conn.commit()
        conn.close()
        self._last_save = now

    # ── 加载 ──

    def load(self) -> AgentSnapshot:
        """从 SQLite 加载完整状态。"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row

        snapshot = AgentSnapshot()

        row = self._get(conn, "soul")
        if row: snapshot.soul = json.loads(row)

        row = self._get(conn, "emotion")
        if row: snapshot.emotion = json.loads(row)

        row = self._get(conn, "alignment")
        if row: snapshot.alignment = json.loads(row)

        for row in conn.execute("SELECT * FROM memory_items"):
            item = {
                "id": row["id"], "content": row["content"],
                "type": row["memory_type"], "strength": row["strength"],
                "access_count": row["access_count"],
                "created_at": row["created_at"],
                "metadata": json.loads(row["metadata"]),
            }
            if row["memory_type"] == "ltm":
                snapshot.memory_ltm.append(item)
            else:
                snapshot.memory_stm.append(item)

        for row in conn.execute("SELECT * FROM cosmic_sources"):
            snapshot.cosmic_sources.append({
                "name": row["name"], "trust": row["trust"],
                "hits": row["hits"], "misses": row["misses"],
                "blacklisted": bool(row["blacklisted"]),
                "blacklist_reason": row["blacklist_reason"],
            })

        for row in conn.execute("SELECT * FROM learning_history"):
            snapshot.learning_history.append({
                "query": row["query"],
                "senses_used": json.loads(row["senses_used"]) if row["senses_used"] else [],
                "success": bool(row["success"]),
                "papers_found": row["papers_found"],
                "duration_ms": row["duration_ms"],
                "quality_score": row["quality_score"],
                "created_at": row["created_at"],
            })

        conn.close()
        return snapshot

    def _set(self, conn, key: str, value: str, ts: float):
        conn.execute("INSERT OR REPLACE INTO agent_state VALUES (?,?,?)", (key, value, ts))

    def _get(self, conn, key: str) -> Optional[str]:
        row = conn.execute("SELECT value FROM agent_state WHERE key=?", (key,)).fetchone()
        return row[0] if row else None

    # ── 统计 ──

    @property
    def needs_save(self) -> bool:
        return time.time() - self._last_save > self.auto_save_interval

    def stats(self) -> dict:
        conn = sqlite3.connect(str(self.db_path))
        stm = conn.execute("SELECT COUNT(*) FROM memory_items WHERE memory_type='stm'").fetchone()[0]
        ltm = conn.execute("SELECT COUNT(*) FROM memory_items WHERE memory_type='ltm'").fetchone()[0]
        src = conn.execute("SELECT COUNT(*) FROM cosmic_sources").fetchone()[0]
        hist = conn.execute("SELECT COUNT(*) FROM learning_history").fetchone()[0]
        conn.close()
        return {"stm": stm, "ltm": ltm, "sources": src, "history": hist}

    def search(self, query: str, **kwargs) -> dict:
        return {"status": "ok", "stats": self.stats()}
