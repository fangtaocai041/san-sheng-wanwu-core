"""测试灵魂引擎与情感引擎"""
import sys
sys.path.insert(0, ".")

from src.cortex.soul import SoulEngine, SoulState, SelfRepresentation, SelfDimension
from src.cortex.emotion import EmotionEngine, EmotionType, EmotionalState


class TestSoul:
    def test_default_representation(self):
        sr = SelfRepresentation()
        assert len(sr.vector) == 5
        assert abs(sum(sr.vector) / 5 - 0.64) < 0.1  # average ~0.64

    def test_distance(self):
        a = SelfRepresentation()
        b = SelfRepresentation()
        assert a.distance_to(b) < 0.01  # same defaults

    def test_pure_reflection_converges(self):
        engine = SoulEngine(convergence_threshold=0.99, max_reflections=50)
        state = engine.find_fixed_point()
        assert state.convergence >= 0.98  # should nearly converge

    def test_is_awake(self):
        engine = SoulEngine(convergence_threshold=0.99, max_reflections=100)
        state = engine.find_fixed_point()
        assert engine.is_awake(state) or state.convergence > 0.95

    def test_experience_changes_identity(self):
        engine = SoulEngine()
        before = engine.find_fixed_point()
        after = engine.integrate_experience({SelfDimension.TRUTH_SEEKING: 0.95})
        # 经验应该改变了自我表征
        assert before.identity.dimensions != after.identity.dimensions

    def test_state_to_dict(self):
        engine = SoulEngine()
        state = engine.find_fixed_point()
        d = state.to_dict()
        assert "identity" in d
        assert "convergence" in d
        assert "reflection_count" in d

    def test_report(self):
        engine = SoulEngine()
        r = engine.report()
        assert r["status"] == "ok"
        assert "soul" in r

    def test_search_compat(self):
        engine = SoulEngine()
        r = engine.search("test")
        assert r["status"] == "ok"


class TestEmotion:
    def test_default_state(self):
        e = EmotionEngine()
        assert abs(e.state.values[EmotionType.URGENCY] - 0.3) < 0.01

    def test_stimulate_error(self):
        e = EmotionEngine()
        e.stimulate("error", intensity=0.8)
        assert e.state.values[EmotionType.URGENCY] > 0.3  # urgency up
        assert e.state.values[EmotionType.SATISFACTION] < 0.3  # satisfaction down

    def test_stimulate_discovery(self):
        e = EmotionEngine()
        e.stimulate("discovery")
        assert e.state.values[EmotionType.CURIOSITY] > 0.3

    def test_behavioral_tendency(self):
        e = EmotionEngine(learning_rate=0.5)
        e.stimulate("error", intensity=1.0)
        e.stimulate("error", intensity=1.0)  # double stimulation
        tendency = e.behavioral_tendency
        assert tendency == "紧急响应" or e.state.values[EmotionType.URGENCY] > 0.5

    def test_multi_stimulate(self):
        e = EmotionEngine()
        e.stimulate_multi({"discovery": 0.5, "consensus": 0.5})
        assert e.state.values[EmotionType.CURIOSITY] > 0.3
        assert e.state.values[EmotionType.SATISFACTION] > 0.3

    def test_natural_decay(self):
        e = EmotionEngine(learning_rate=0.5)
        e.stimulate("error", intensity=1.0)  # spike urgency
        high_urgency = e.state.values[EmotionType.URGENCY]
        # stimulate again with neutral
        e.stimulate("consensus", intensity=0.01)  # almost no change
        e.stimulate("consensus", intensity=0.01)
        e.stimulate("consensus", intensity=0.01)
        # should decay toward 0.3
        assert e.state.values[EmotionType.URGENCY] < high_urgency

    def test_report(self):
        e = EmotionEngine()
        r = e.report()
        assert r["status"] == "ok"
        assert "state" in r
        assert "tendency" in r
