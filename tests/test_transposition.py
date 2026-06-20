"""测试概念转座层 (TranspositionLayer)"""
import sys
sys.path.insert(0, ".")

from src.cortex.transposition import TranspositionLayer, TranspositionEvent


class TestTransposition:
    def test_default_activity(self):
        tl = TranspositionLayer()
        assert 0.2 <= tl.current_activity <= 0.4
        assert not tl.is_hyperactive

    def test_stress_raises_activity(self):
        tl = TranspositionLayer(base_activity=0.3)
        tl.set_stress_level(uncertainty=0.9, confusion=0.8)
        assert tl.current_activity > 0.5
        assert tl._stress_boost > 0

    def test_hyperactive_at_high_stress(self):
        tl = TranspositionLayer(base_activity=0.8)
        tl.set_stress_level(uncertainty=1.0, confusion=1.0)
        assert tl.is_hyperactive

    def test_transpose_returns_event(self):
        tl = TranspositionLayer(base_activity=1.0)  # force high activity
        event = tl.transpose("biology", "conservation",
                            {"concept": "测试概念", "confidence": 1.0})
        assert isinstance(event, TranspositionEvent)
        assert event.source_domain == "biology"
        assert event.target_domain == "conservation"

    def test_transpose_low_activity_skips(self):
        tl = TranspositionLayer(base_activity=0.0)
        event = tl.transpose("biology", "conservation",
                            {"concept": "测试", "confidence": 0.5})
        assert not event.success

    def test_domestication_tracking(self):
        tl = TranspositionLayer(base_activity=1.0, domestication_threshold=3)
        # 强制驯化: 直接操作 _domesticated 使其达到阈值
        from src.cortex.transposition import DomesticatedPattern
        key = "biology→conservation:concept"
        tl._domesticated[key] = DomesticatedPattern(
            pattern_id=key,
            source_domain="biology",
            target_domain="conservation",
            pattern_type="concept",
            success_count=3,
            avg_fitness_delta=0.2,
        )
        assert tl.is_domesticated("biology", "conservation")

    def test_domestication_via_repeated_transposition(self):
        tl = TranspositionLayer(base_activity=1.0, domestication_threshold=2)
        pattern = {"concept": "瓶颈效应", "confidence": 0.9, "type": "concept"}
        # 多次转座
        for _ in range(5):
            tl.transpose("biology", "conservation", pattern)
        # 至少应有一次触发驯化
        assert len(tl._domesticated) >= 1

    def test_domestication_rate(self):
        tl = TranspositionLayer(base_activity=1.0)
        assert tl.domestication_rate == 0.0  # no attempts yet

    def test_package_and_unpack(self):
        tl = TranspositionLayer()
        chain = [{"step": 1, "action": "search"}, {"step": 2, "action": "validate"}]
        capsule = tl.package_knowledge(chain, confidence=0.9)
        assert capsule["type"] == "reasoning_capsule"
        assert len(capsule["capsule_id"]) == 12

        unpacked = tl.unpack_knowledge(capsule)
        assert len(unpacked) == 2

    def test_unpack_invalid(self):
        tl = TranspositionLayer()
        result = tl.unpack_knowledge({"type": "invalid"})
        assert result == []

    def test_report(self):
        tl = TranspositionLayer()
        r = tl.report()
        assert r["status"] == "ok"
        assert "activity" in r
        assert "domesticated_pathways" in r

    def test_search_compat(self):
        tl = TranspositionLayer()
        r = tl.search("test")
        assert r["status"] == "ok"
