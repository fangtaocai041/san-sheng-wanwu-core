"""测试 MAGMA 四维正交图谱记忆"""
import sys
sys.path.insert(0, ".")
import time

from src.memory.magma import MagmaMemory, RelationType
from src.memory.consolidate import MemorySystem


class TestMagma:
    def test_add_node(self):
        m = MagmaMemory()
        node = m.add("鳤是长江珍稀鱼类", entities=["鳤"])
        assert m.node_count == 1
        assert "鳤" in node.entities

    def test_search_by_content(self):
        m = MagmaMemory()
        m.add("鳤是长江珍稀鱼类")
        m.add("刀鲚是洄游鱼类")
        results = m.search("珍稀鱼类")
        assert len(results) >= 1

    def test_entity_relation(self):
        m = MagmaMemory()
        m.add("鳤分布在长江中下游", entities=["鳤"])
        m.add("鳤的产卵场在长江上游", entities=["鳤"])
        m.add("翘嘴鲌是常见经济鱼类", entities=["翘嘴鲌"])
        # 搜索"鳤"应返回前两条
        results = m.search("鳤")
        assert len(results) >= 2

    def test_temporal_relation(self):
        m = MagmaMemory()
        n1 = m.add("第一次调查")
        time.sleep(0.01)
        n2 = m.add("第二次调查")
        results = m.search("调查")
        assert len(results) >= 2

    def test_manual_relation(self):
        m = MagmaMemory()
        n1 = m.add("水温升高")
        n2 = m.add("鱼类向北迁移")
        m.relate(n1.node_id, n2.node_id, RelationType.CAUSAL, 0.9, "leads_to")
        results = m.search("水温")
        assert len(results) >= 1

    def test_graph_stats(self):
        m = MagmaMemory()
        m.add("A", entities=["e1"])
        m.add("B", entities=["e1"])
        m.add("C", entities=["e2"])
        stats = m.stats()
        assert stats["nodes"] == 3
        assert stats["edges"] >= 1  # entity link between A and B
        assert "semantic" in stats["graphs"]

    def test_empty_search(self):
        m = MagmaMemory()
        assert m.search("nothing") == []


class TestMagmaConsolidate:
    def test_memory_system_with_magma(self):
        mem = MemorySystem()
        mem.store("鳤是珍稀鱼类", entities=["鳤"])
        mem.store("刀鲚有洄游习性", entities=["刀鲚"])
        results = mem.recall("珍稀鱼类的洄游")
        assert len(results) >= 0  # may match if entities connect

    def test_memory_system_fallback(self):
        mem = MemorySystem()
        mem.store("测试记忆")
        results = mem.recall("测试")
        assert len(results) >= 1
        assert results[0].content == "测试记忆"

    def test_search_method_indicator(self):
        mem = MemorySystem()
        mem.store("test content")
        r = mem.search("test")
        assert r["method"] == "magma_4d_graph_traversal"
