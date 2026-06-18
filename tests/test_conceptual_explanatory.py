"""测试概念工程与可解释性模块"""
import sys
sys.path.insert(0, ".")

from src.cortex.conceptual import ConceptRegistry, Concept
from src.cortex.explanatory import ExplainabilityEngine, ReasoningTrace, ReasoningStep


class TestConceptualEngineering:
    def test_register_concept(self):
        r = ConceptRegistry()
        c = Concept(name="species", definition="分类学基本单位", domain={"鱼", "鸟", "兽"})
        r.register(c)
        assert r.get("species") is not None
        assert r.get("species").version == 1

    def test_concept_revision(self):
        r = ConceptRegistry()
        c1 = Concept(name="protection", definition="原始定义")
        r.register(c1)
        c2 = Concept(name="protection", definition="修订定义")
        r.register(c2)
        assert r.get("protection").version == 2
        assert r.get("protection").definition == "修订定义"

    def test_concept_relation(self):
        r = ConceptRegistry()
        r.register(Concept(name="species"))
        r.register(Concept(name="organism"))
        rel = r.relate("species", "is_a", "organism")
        assert rel.predicate == "is_a"

    def test_concept_graph(self):
        r = ConceptRegistry()
        r.register(Concept(name="species"))
        r.register(Concept(name="organism"))
        r.register(Concept(name="population"))
        r.relate("species", "is_a", "organism")
        r.relate("population", "part_of", "species")
        graph = r.get_graph("species", depth=2)
        assert "species" in graph["nodes"]
        assert len(graph["edges"]) >= 1

    def test_explain_concept(self):
        r = ConceptRegistry()
        r.register(Concept(name="test_concept", definition="测试概念"))
        exp = r.explain("test_concept")
        assert "test_concept" in exp
        assert "测试概念" in exp

    def test_detect_cycle(self):
        r = ConceptRegistry()
        r.register(Concept(name="A"))
        r.register(Concept(name="B"))
        r.relate("A", "depends_on", "B")
        r.relate("B", "depends_on", "A")
        conflicts = r.detect_conflicts()
        assert len(conflicts) >= 1

    def test_to_dict(self):
        r = ConceptRegistry()
        c = Concept(name="x", definition="y")
        r.register(c)
        d = r.to_dict()
        assert "concepts" in d
        assert "relations" in d
        assert "revisions" in d

    def test_search_compat(self):
        r = ConceptRegistry()
        r.register(Concept(name="compat_test"))
        result = r.search("compat_test")
        assert result["status"] == "ok"


class TestExplainability:
    def test_begin_trace(self):
        e = ExplainabilityEngine()
        trace = e.begin("鳤", "Ochetobius elongatus")
        assert trace.query == "鳤"
        assert trace.species == "Ochetobius elongatus"
        assert len(trace.trace_id) == 32

    def test_record_step(self):
        e = ExplainabilityEngine()
        trace = e.begin("test")
        step = e.record_step(
            trace, phase="validate", action="score",
            input_summary="3 papers", output_summary="avg 0.75",
            confidence=0.8, duration_ms=10.5,
            alternatives=["reject all"],
        )
        assert step.phase == "validate"
        assert trace.step_count == 1

    def test_level1_summary(self):
        e = ExplainabilityEngine()
        trace = e.begin("test")
        e.record_step(trace, "validate", "score", confidence=0.9)
        e.finalize(trace, confidence=0.9)
        summary = e.explain(trace, level=1)
        assert "test" in summary

    def test_level2_reasons(self):
        e = ExplainabilityEngine()
        trace = e.begin("鳤")
        e.record_step(trace, "sense", "search", output_summary="2 papers found")
        e.record_step(trace, "validate", "score", confidence=0.85, output_summary="avg 0.75")
        exp = e.explain(trace, level=2)
        assert "鳤" in exp
        assert "感知" in exp or "sense" in exp

    def test_level3_chain(self):
        e = ExplainabilityEngine()
        trace = e.begin("test")
        e.record_step(trace, "sense", "search", input_summary="query=test")
        e.record_step(trace, "validate", "score", output_summary="verified", evidence=["DOI match"])
        chain = e.explain(trace, level=3)
        assert "Step 1" in chain
        assert "Step 2" in chain

    def test_counterfactual(self):
        e = ExplainabilityEngine()
        trace = e.begin("test")
        e.record_step(trace, "validate", "select",
                      alternatives=["use pubmed", "use cnki"],
                      evidence=["pubmed has higher coverage"])
        cf = e.explain(trace, level=4)
        assert "拒绝了" in cf

    def test_provenance(self):
        e = ExplainabilityEngine()
        trace = e.begin("test")
        e.record_step(trace, "dialectics", "synthesize")
        prov = e.explain(trace, level=5)
        assert "辩证综合" in prov

    def test_finalize(self):
        e = ExplainabilityEngine()
        trace = e.begin("test")
        e.finalize(trace, answer="结果", confidence=0.95)
        assert trace.final_answer == "结果"
        assert trace.overall_confidence == 0.95

    def test_trace_phases(self):
        e = ExplainabilityEngine()
        trace = e.begin("test")
        e.record_step(trace, "sense", "search")
        e.record_step(trace, "validate", "score")
        assert trace.phases_used == ["sense", "validate"]
