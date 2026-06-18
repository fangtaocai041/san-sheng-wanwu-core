"""测试记忆巩固、学习适应与自我进化模块"""
import sys
sys.path.insert(0, ".")

from src.memory.consolidate import MemorySystem, ebbinghaus_forgetting, reinforcement_boost
from src.cortex.learning import LearningEngine
from src.cortex.evolution import EvolutionEngine, ModificationProposal


class TestMemoryConsolidation:
    def test_ebbinghaus_forgetting(self):
        r = ebbinghaus_forgetting(0, 1.0)
        assert r == 1.0  # 立刻回忆 = 100%
        r = ebbinghaus_forgetting(24, 1.0)
        assert r < 1.0  # 24 小时后遗忘
        assert r > 0

    def test_reinforcement_boost(self):
        s1 = reinforcement_boost(0)
        s3 = reinforcement_boost(3)
        assert s3 > s1  # 重复强化提升强度

    def test_store_and_recall(self):
        mem = MemorySystem()
        mem.store("这是一条测试记忆")
        results = mem.recall("测试")
        assert len(results) >= 1
        assert "测试" in results[0].content

    def test_access_strengthens(self):
        mem = MemorySystem()
        item = mem.store("强化测试")
        initial_strength = item.strength
        item.access()
        assert item.strength > initial_strength

    def test_working_memory(self):
        mem = MemorySystem()
        mem.set_working("species", "鳤")
        assert mem.get_working("species") == "鳤"

    def test_consolidation(self):
        mem = MemorySystem(consolidation_threshold=2)
        item = mem.store("巩固测试")
        item.access_count = 2
        result = mem.consolidate()
        assert result["stm_to_ltm"] >= 1


class TestLearning:
    def test_record_success(self):
        eng = LearningEngine()
        eng.record("鳤", ["scholar", "ncbi"], {"max_results": 10}, True, papers_found=5)
        assert eng.total_queries == 1
        assert eng.success_rate == 1.0

    def test_record_failure(self):
        eng = LearningEngine()
        eng.record("鳤", ["scholar"], {}, False, error="timeout")
        assert eng.success_rate == 0.0

    def test_sense_weights_update(self):
        eng = LearningEngine()
        eng.record("test", ["scholar"], {}, True, papers_found=8)
        eng.record("test", ["scholar"], {}, True, papers_found=5)
        assert eng._sense_weights["scholar"] > 1.0

    def test_recommended_senses(self):
        eng = LearningEngine()
        eng.record("a", ["scholar"], {}, True)
        eng.record("b", ["cnki"], {}, False)
        senses = eng.recommended_senses
        assert senses[0] == "scholar"

    def test_recent_performance(self):
        eng = LearningEngine()
        for i in range(5):
            eng.record(f"q{i}", ["scholar"], {}, i % 2 == 0)
        perf = eng.recent_performance(5)
        assert 0 <= perf <= 1


class TestEvolution:
    def test_analyze_python_file(self):
        eng = EvolutionEngine()
        result = eng.analyze_file(__file__)  # 分析自身
        assert result["status"] == "ok"
        assert result["lines"] > 0

    def test_readonly_by_default(self):
        eng = EvolutionEngine()
        assert eng.is_readonly

    def test_unlock(self):
        eng = EvolutionEngine()
        eng.unlock()
        assert not eng.is_readonly
        eng.lock()
        assert eng.is_readonly

    def test_apply_proposal_readonly(self):
        eng = EvolutionEngine()
        prop = ModificationProposal(target_file="test.py", description="test")
        event = eng.apply_proposal(prop)
        assert not event.success  # 只读模式

    def test_proposal_creation(self):
        prop = ModificationProposal(
            target_file="test.py",
            description="添加测试",
            risk_level="low",
        )
        assert len(prop.id) == 12
        assert prop.risk_level == "low"
