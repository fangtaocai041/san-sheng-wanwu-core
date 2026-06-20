"""测试灵魂引擎与情感引擎"""
import sys
sys.path.insert(0, ".")

from src.cortex.soul import SoulEngine, SoulState, SelfRepresentation, SelfDimension
from src.cortex.self_model import SelfModelEngine, ModelState
from src.cortex.emotion import EmotionEngine, EmotionType, EmotionalState


class TestSoul:
    """旧 soul.py 兼容性测试 (已弃用, 保留以确保迁移期间不破坏现有代码)。"""


class TestSelfModel:
    """新 self_model.py DSM 阻尼自我模型测试。"""

    def test_default_representation(self):
        sr = SelfRepresentation()
        assert len(sr.vector) == 5
        assert abs(sum(sr.vector) / 5 - 0.64) < 0.1

    def test_distance(self):
        a = SelfRepresentation()
        b = SelfRepresentation()
        assert a.distance_to(b) < 0.01

    def test_reflect_preserves_identity(self):
        """关键测试: 纯自我反思不应改变表征"""
        engine = SelfModelEngine()
        before = engine.find_state()
        engine.reflect()
        after = engine.find_state()
        # 无新输入时，自我表征应保持不变
        dist = before.identity.distance_to(after.identity)
        assert dist < 0.001, f"Reflect changed identity by {dist:.4f}"

    def test_experience_updates_identity(self):
        engine = SelfModelEngine()
        before = engine.find_state()
        engine.update_with_experience(
            {SelfDimension.TRUTH_SEEKING: 0.95},
            prediction_error=0.1
        )
        after = engine.find_state()
        # 有经验时，表征应更新
        dist = before.identity.distance_to(after.identity)
        assert dist > 0.001, f"Experience should change identity (dist={dist:.4f})"

    def test_meta_stability_improves_with_consistent_experience(self):
        engine = SelfModelEngine(error_window=5)
        # 多次一致的零误差经验
        for i in range(10):
            engine.update_with_experience(
                {SelfDimension.TRUTH_SEEKING: 0.8},
                prediction_error=0.01
            )
        state = engine.find_state()
        assert state.meta_stability > 0.5, f"meta_stability={state.meta_stability:.3f} should be > 0.5"

    def test_not_stable_without_enough_experience(self):
        engine = SelfModelEngine(stability_threshold=0.9, error_window=5)
        assert not engine.is_stable(), "Should not be stable with 0 experience"

    def test_stable_with_enough_good_experience(self):
        engine = SelfModelEngine(stability_threshold=0.9, error_window=3)
        for i in range(10):
            engine.update_with_experience(
                {SelfDimension.TRUTH_SEEKING: 0.8},
                prediction_error=0.01
            )
        assert engine.is_stable(), "Should be stable after consistent low-error experience"

    def test_state_to_dict(self):
        engine = SelfModelEngine()
        state = engine.find_state()
        d = state.to_dict()
        assert "identity" in d
        assert "stability" in d
        assert "experience_count" in d

    def test_report(self):
        engine = SelfModelEngine()
        r = engine.report()
        assert r["status"] == "ok"
        assert "self_model" in r
        assert "stable" in r

    def test_search_compat(self):
        engine = SelfModelEngine()
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
