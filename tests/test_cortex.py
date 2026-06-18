"""测试认知皮层"""
import sys
sys.path.insert(0, ".")

from src.cortex.dialectics import DialecticsCortex
from src.cortex.validate import ValidateCortex, calc_trust_score, calc_credibility_score
from src.cortex.emergent import EmergenceMonitor, DimensionalLevel, EmergenceSignal
from src.cortex.pipeline import Pipeline


class TestDialectics:
    def test_no_contradiction(self):
        engine = DialecticsCortex()
        result = engine.synthesize("protection", {"iucn": "LC", "redlist": "LC"})
        assert result.synthesis == "LC"
        assert len(result.contradictions) == 0

    def test_with_contradiction(self):
        engine = DialecticsCortex()
        result = engine.synthesize("protection", {
            "iucn": "LC", "chinese_redlist": "EN",
        })
        assert len(result.contradictions) == 1
        assert result.synthesis in ("LC", "EN")

    def test_weighted_synthesis(self):
        engine = DialecticsCortex()
        result = engine.synthesize("protection", {
            "iucn": "LC", "redlist": "EN", "cites": "LC",
        }, weights={"iucn": 1.0, "redlist": 0.6, "cites": 0.8})
        assert result.synthesis == "LC"
        assert result.confidence > 0.5

    def test_circuit_judgment(self):
        engine = DialecticsCortex()
        result = engine.synthesize("status", {
            "a": "ok", "b": "ok", "c": "ok", "d": "fail",
        }, mode="circuit")
        assert result.synthesis == "ok"

    def test_arbitrate_compat(self):
        engine = DialecticsCortex()
        result = engine.arbitrate([
            {"source": "iucn", "protection_level": "LC", "weight": 1.0},
            {"source": "chinese_red_list", "protection_level": "EN"},
        ])
        assert "conflict_level" in result
        assert result["conflict_level"] == "high"

    def test_synthesis_to_dict(self):
        engine = DialecticsCortex()
        result = engine.synthesize("test", {"a": 1, "b": 2})
        d = result.to_dict()
        assert "synthesis" in d
        assert "contradictions" in d


class TestValidate:
    def test_empty_papers(self):
        engine = ValidateCortex()
        result = engine.validate([])
        assert result["stats"]["total"] == 0

    def test_single_paper(self):
        engine = ValidateCortex()
        result = engine.validate([{
            "doi": "10.1000/test",
            "title": "Test Paper",
            "authors": ["Author A"],
            "source": "pubmed",
        }])
        assert result["stats"]["total"] == 1
        assert result["papers"][0]["trust"] > 0

    def test_trust_score(self):
        from src.cortex.validate import Paper
        p = Paper(doi="10.1234/test", pmid="12345")
        score = calc_trust_score(p, species_terms=["鳤"])
        assert score >= 85  # 20(doi) + 15(pmid) + 10(authors=0, no) + 5(journal=0, no) = 85

    def test_credibility_retracted(self):
        from src.cortex.validate import Paper
        p = Paper(journal="A retracted journal")
        score = calc_credibility_score(p)
        assert score == -1

    def test_credibility_normal(self):
        from src.cortex.validate import Paper
        p = Paper(doi="10.1234/test", journal="Nature")
        score = calc_credibility_score(p)
        assert score > 50


class TestEmergent:
    def test_monitor_creation(self):
        mon = EmergenceMonitor(emergence_threshold_sigma=3.0, min_sources=3)
        assert mon is not None

    def test_dimensional_levels(self):
        assert DimensionalLevel.D0.value == 0
        assert DimensionalLevel.D3.value == 3


class TestPipeline:
    def test_pipeline_creation(self):
        p = Pipeline()
        assert len(p.trace_id) == 32

    def test_pipeline_run(self):
        p = Pipeline()
        result = p.run("鳤", sense_only=True)
        assert result.query == "鳤"
        assert "sense" in result.stages

    def test_pipeline_to_dict(self):
        p = Pipeline()
        result = p.run("鳤", sense_only=True)
        d = result.to_dict()
        assert "trace_id" in d
        assert "stages" in d
