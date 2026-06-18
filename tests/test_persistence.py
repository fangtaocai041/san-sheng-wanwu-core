"""测试持久化引擎与主循环"""
import sys
sys.path.insert(0, ".")
import os
import tempfile
import time

from src.memory.persistence import PersistenceEngine, AgentSnapshot


class TestPersistence:
    def test_init_db(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            p = PersistenceEngine(db_path=db_path)
            assert p.db_path.exists()
            stats = p.stats()
            assert "stm" in stats
        finally:
            os.unlink(db_path)

    def test_save_and_load(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            p = PersistenceEngine(db_path=db_path)
            snap = AgentSnapshot(
                soul={"identity": {"truth_seeking": 0.9}, "convergence": 0.99},
                emotion={"values": {"urgency": 0.3}, "dominant": "neutral"},
                memory_stm=[{"id": "m1", "content": "test", "type": "stm", "strength": 1.0,
                           "access_count": 1, "created_at": 100.0, "metadata": {}}],
                cosmic_sources=[{"name": "source_a", "trust": 0.8, "hits": 5,
                                "misses": 1, "blacklisted": False, "blacklist_reason": ""}],
                learning_history=[{"query": "test", "senses_used": ["scholar"],
                                  "success": True, "papers_found": 3, "duration_ms": 100,
                                  "quality_score": 0.8, "created_at": 100.0}],
            )
            p.save(snap)
            loaded = p.load()
            assert loaded.soul["identity"]["truth_seeking"] == 0.9
            assert loaded.emotion["dominant"] == "neutral"
            assert len(loaded.memory_stm) >= 1
            assert loaded.memory_stm[0]["id"] == "m1"
            assert len(loaded.cosmic_sources) >= 1
            assert len(loaded.learning_history) >= 1
        finally:
            os.unlink(db_path)

    def test_empty_load(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            p = PersistenceEngine(db_path=db_path)
            snap = p.load()
            assert snap.soul == {}
            assert snap.emotion == {}
            assert snap.memory_stm == []
        finally:
            os.unlink(db_path)

    def test_needs_save(self):
        p = PersistenceEngine(auto_save_interval=99999)
        p._last_save = time.time()  # mark as just saved
        assert not p.needs_save
