"""测试愈愈发动机 (自愈+进化闭环)"""
import sys
sys.path.insert(0, ".")
from src.cortex.regen import RegenEngine, RegenEvent


class TestRegen:
    def test_regen_no_issues(self):
        eng = RegenEngine()
        result = eng.run()
        assert result["detected"] == 0

    def test_regen_with_healing(self):
        from src.cortex.healing import HealingEngine, HealthCheck
        h = HealingEngine()
        h._checks = [HealthCheck(component="sense/x", status="failed", error="timeout")]
        eng = RegenEngine(healing_engine=h, max_cycles=1)
        result = eng.run()
        assert result["detected"] >= 1

    def test_regen_cycle_event(self):
        e = RegenEvent(cycle=1, phase="detect", action="scan", success=True)
        assert e.cycle == 1
        assert e.phase == "detect"

    def test_regen_events_logged(self):
        from src.cortex.healing import HealingEngine, HealthCheck
        h = HealingEngine()
        h._checks = [HealthCheck(component="sense/x", status="failed")]
        eng = RegenEngine(healing_engine=h)
        eng.run(targets=["sense/x"])
        assert len(eng.events) > 0

    def test_max_cycles(self):
        eng = RegenEngine(max_cycles=3)
        eng._detect = lambda t=None: [{"target": "x", "detail": "issue", "severity": "failed"}]
        eng._fix = lambda i: {"action": "retry", "success": True}
        eng._verify_fix = lambda t: False
        result = eng.run()
        assert result["cycles"] <= 3
