"""测试认知皮层"""
import sys
sys.path.insert(0, ".")

from src.cortex.dialectics import DialecticsEngine
from src.cortex.validate import ValidateEngine
from src.cortex.emergent import EmergentDetector
from src.cortex.pipeline import Pipeline


class TestDialectics:
    def test_no_contradiction(self):
        """无矛盾时直接输出。"""
        engine = DialecticsEngine()
        result = engine.synthesize("protection", {"iucn": "LC", "redlist": "LC"})
        assert result.synthesis == "LC"
        assert len(result.contradictions) == 0

    def test_with_contradiction(self):
        """有矛盾时辩证综合。"""
        engine = DialecticsEngine()
        result = engine.synthesize("protection", {
            "iucn": "LC",
            "chinese_redlist": "EN",
        })
        assert len(result.contradictions) == 1
        assert result.synthesis in ("LC", "EN")

    def test_weighted_synthesis(self):
        """加权投票。"""
        engine = DialecticsEngine()
        result = engine.synthesize("protection", {
            "iucn": "LC",
            "redlist": "EN",
            "cites": "LC",
        }, weights={"iucn": 1.0, "redlist": 0.6, "cites": 0.8})
        # LC 权重 = 1.0 + 0.8 = 1.8 > EN 权重 0.6
        assert result.synthesis == "LC"
        assert result.confidence > 0.5

    def test_arbitrate_compat(self):
        """兼容旧版 arbitrate 接口。"""
        engine = DialecticsEngine()
        result = engine.arbitrate([
            {"source": "iucn", "protection_level": "LC", "weight": 1.0},
            {"source": "chinese_red_list", "protection_level": "EN"},
        ])
        assert "conflict_level" in result
        assert result["conflict_level"] == "high"


class TestValidate:
    def test_empty_papers(self):
        engine = ValidateEngine()
        result = engine.validate([])
        assert result["stats"]["total"] == 0

    def test_single_paper(self):
        engine = ValidateEngine()
        result = engine.validate([{
            "doi": "10.1000/test",
            "title": "Test",
            "authors": ["Author A"],
            "source": "pubmed",
        }])
        assert result["stats"]["total"] == 1
        assert result["papers"][0]["confidence"] > 0


class TestEmergent:
    def test_d1_anomaly(self):
        detector = EmergentDetector()
        signal = detector.feed({"papers_found": 100})
        assert signal is None  # 首次不会触发
        signal = detector.feed({"papers_found": 500})
        assert signal is not None
        assert signal.level == 1

    def test_no_signal_for_normal(self):
        detector = EmergentDetector()
        detector.feed({"papers_found": 50})
        signal = detector.feed({"papers_found": 51})
        assert signal is None


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
        assert "total_duration_ms" in d
