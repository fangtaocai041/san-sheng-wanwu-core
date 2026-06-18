"""测试群体智能、价值对齐与自愈引擎"""
import sys
sys.path.insert(0, ".")
from pathlib import Path

from src.cortex.swarm import SwarmEngine, AgentMessage
from src.cortex.alignment import AlignmentEngine
from src.cortex.healing import HealingEngine, HealthCheck


class TestSwarm:
    def test_agent_identity(self):
        swarm = SwarmEngine("test-agent", ["search"])
        assert swarm.agent_id is not None
        assert "search" in swarm._identity.capabilities

    def test_discovery(self):
        a1 = SwarmEngine("agent-1")
        a2 = SwarmEngine("agent-2")
        peers = a1.discover()
        assert len(peers) >= 2

    def test_send_message(self):
        a1 = SwarmEngine("sender")
        a2 = SwarmEngine("receiver")
        msg = a1.send(a2.agent_id, "query/request", {"q": "鳤"})
        assert msg.msg_type == "query/request"

    def test_receive_message(self):
        a1 = SwarmEngine("a")
        a2 = SwarmEngine("b")
        a1.send(a2.agent_id, "test/msg", {"data": 1})
        msgs = a2.receive(msg_type="test/msg")
        assert len(msgs) >= 1

    def test_knowledge_share(self):
        a1 = SwarmEngine("source")
        a1.share_knowledge("species/鳤", "珍稀鱼类", confidence=0.8)
        results = a1.query_knowledge("species/鳤")
        assert len(results) >= 1
        assert results[0].confidence == 0.8

    def test_consensus(self):
        a1 = SwarmEngine("a")
        a1.share_knowledge("topic", "value_x", confidence=0.9)
        a1.share_knowledge("topic", "value_x", confidence=0.8)
        consensus = a1.reach_consensus("topic")
        assert consensus == "value_x"

    def test_delegate(self):
        a1 = SwarmEngine("manager", ["plan"])
        SwarmEngine("worker", ["search", "plan"])
        result = a1.delegate("search task", {"q": "test"}, "search")
        assert result is None or len(result) > 0


class TestAlignment:
    def test_load_config(self):
        eng = AlignmentEngine()
        config_path = str(Path(__file__).resolve().parent.parent / "config" / "alignment.yaml")
        if Path(config_path).exists():
            result = eng.load_config(config_path)
            assert result
            assert len(eng._values) > 0

    def test_check_forbidden(self):
        eng = AlignmentEngine()
        eng._forbidden = ["编造"]
        assert not eng.check_decision("在不确定时编造答案")
        assert eng.check_decision("如实说不知道")

    def test_value_priorities(self):
        eng = AlignmentEngine()
        eng._values = {"truth": 1.0, "efficiency": 0.5}
        assert eng._values["truth"] > eng._values["efficiency"]

    def test_hallucination_check(self):
        eng = AlignmentEngine()
        eng._values = {"uncertainty_honesty": 0.9}
        assert not eng.check_hallucination("不确定的陈述", [])
        assert eng.check_hallucination("有证据的陈述", ["证据1"])


class TestHealing:
    def test_health_check(self):
        eng = HealingEngine()
        check = HealthCheck(component="test", status="healthy")
        assert check.status == "healthy"

    def test_diagnose_failed(self):
        eng = HealingEngine()
        actions = eng.diagnose([
            HealthCheck(component="sense/x", status="failed", error="timeout")
        ])
        assert len(actions) >= 1
        assert actions[0].action == "restart"

    def test_diagnose_degraded(self):
        eng = HealingEngine()
        actions = eng.diagnose([
            HealthCheck(component="sense/y", status="degraded")
        ])
        assert len(actions) >= 1
        assert actions[0].action == "degrade"

    def test_healthy_no_action(self):
        eng = HealingEngine()
        actions = eng.diagnose([
            HealthCheck(component="test", status="healthy")
        ])
        assert len(actions) == 0

    def test_health_summary(self):
        eng = HealingEngine()
        eng._checks = [
            HealthCheck(component="a", status="healthy"),
            HealthCheck(component="b", status="healthy"),
            HealthCheck(component="c", status="degraded"),
        ]
        summary = eng.health_summary
        assert "健康" in summary or "healthy" in summary
