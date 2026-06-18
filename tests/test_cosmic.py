"""测试宇宙社会学模块"""
import sys
sys.path.insert(0, ".")

from src.cortex.cosmic import (
    CosmicSociologyEngine,
    dark_forest_trust,
    chain_of_suspicion_decay,
    dimensional_projection,
)


class TestDarkForest:
    def test_register_source(self):
        e = CosmicSociologyEngine()
        e.register_source("iucn", initial_trust=0.9)
        src = e.get_source("iucn")
        assert src.name == "iucn"
        assert src.trust == 0.9  # trust 字段存初始值
        assert src.reliability == 0.5  # reliability 用 Beta(1,1) = 0.5

    def test_consensus_all_agree(self):
        e = CosmicSociologyEngine()
        e.register_source("a", 0.8)
        e.register_source("b", 0.7)
        e.register_source("c", 0.6)
        r = e.dark_forest_check({"a": "LC", "b": "LC", "c": "LC"})
        assert r["consensus"] == "LC"
        assert r["consensus_level"] == 1.0
        assert len(r["outliers"]) == 0

    def test_consensus_majority(self):
        e = CosmicSociologyEngine()
        e.register_source("a", 0.9)
        e.register_source("b", 0.8)
        e.register_source("c", 0.7)
        r = e.dark_forest_check({"a": "LC", "b": "LC", "c": "EN"})
        assert r["consensus"] == "LC"
        assert "c" in r["outliers"]

    def test_blacklist_on_low_reliability(self):
        e = CosmicSociologyEngine()
        e.register_source("bad", 0.5)
        # 多次错误 → 可靠性下降 → 被打击
        for _ in range(20):
            e.dark_forest_check({"good": "A", "bad": "B", "ref": "A"})
        src = e.get_source("bad")
        assert src.blacklisted

    def test_strikes_dont_participate(self):
        e = CosmicSociologyEngine()
        e.register_source("dead", 0.5)
        e.register_source("alive", 0.8)
        e._dark_forest_strike("dead")
        r = e.dark_forest_check({"dead": "X", "alive": "Y"})
        assert r["consensus"] == "Y"  # dead 不参与投票

    def test_chain_of_suspicion(self):
        e = CosmicSociologyEngine()
        e.register_source("original", 0.9)
        trust = e.chain_of_suspicion(["original", "verifier_a", "verifier_b", "verifier_c"])
        assert trust < 0.9  # 链越长, 信任越低
        assert trust > 0  # 但仍然大于 0

    def test_dimensional_reduction(self):
        e = CosmicSociologyEngine()
        r = e.dimensional_reduction({"length": [10, 20, 30, 100]})
        assert "length" in r
        assert len(r["length"]["projected"]) == 4
        assert max(r["length"]["projected"]) == 1.0
        assert min(r["length"]["projected"]) == 0.0

    def test_dimensional_attack(self):
        e = CosmicSociologyEngine()
        r = e.dimensional_attack({"iucn": "LC", "chinese_redlist": "EN"})
        assert "综合" in r["synthesis"]
        assert len(r["dimensions"]) >= 1

    def test_return_to_zero(self):
        e = CosmicSociologyEngine()
        e.register_source("a")
        e._events.append(0)  # force event
        stats = e.return_to_zero(keep_sources=True)
        assert stats["events_cleared"] > 0

    def test_sophon_monitor(self):
        e = CosmicSociologyEngine()
        result = e.sophon_monitor({
            "scholar": {"status": "ok", "duration_ms": 100},
            "cnki": {"status": "ok", "duration_ms": 200},
            "ncbi": {"status": "error"},
        })
        assert result["active_channels"] == 2
        assert result["silent_channels"] == 1
        assert result["avg_delay_ms"] == 150.0

    def test_source_summary(self):
        e = CosmicSociologyEngine()
        e.register_source("a")
        summary = e.source_summary()
        assert "黑暗森林" in summary

    def test_search_compat(self):
        e = CosmicSociologyEngine()
        e.register_source("test")
        r = e.search("test")
        assert r["status"] == "ok"


class TestCosmicFunctions:
    def test_dark_forest_trust(self):
        t = dark_forest_trust(["a", "b", "c"])
        assert 0 < t < 1

    def test_dark_forest_trust_single(self):
        t = dark_forest_trust(["a"], [0.5])
        assert t == 0.5

    def test_chain_decay(self):
        t = chain_of_suspicion_decay(3, base_trust=0.9, decay=0.85)
        expected = round(0.9 * (0.85 ** 3), 3)
        assert abs(t - expected) < 0.001

    def test_dimensional_projection(self):
        p = dimensional_projection([10, 20, 30, 40])
        assert p[0] == 0.0
        assert p[-1] == 1.0

    def test_dimensional_projection_single(self):
        p = dimensional_projection([5])
        assert p == [0.5]
