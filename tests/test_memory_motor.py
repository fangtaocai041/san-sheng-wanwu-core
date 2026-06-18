"""测试记忆与运动模块"""
import sys
sys.path.insert(0, ".")

from src.memory.kb import KnowledgeDB, CredibilityScorer, SpeciesVariants
from src.memory.cache import SearchCache
from src.motor.report import ReportGenerator
from src.motor.visualize import Visualizer


class TestMemory:
    def test_cache_set_get(self):
        cache = SearchCache(ttl_hours=24)
        cache.set("鳤", "Ochetobius elongatus", {"status": "ok"})
        result = cache.get("鳤", "Ochetobius elongatus")
        assert result is not None
        assert result["status"] == "ok"

    def test_cache_miss(self):
        cache = SearchCache()
        assert cache.get("unknown") is None

    def test_cache_clear(self):
        cache = SearchCache()
        cache.set("a", "", {"x": 1})
        cache.clear()
        assert cache.size == 0

    def test_credibility_scorer_importable(self):
        assert CredibilityScorer is not None

    def test_species_variants_importable(self):
        assert SpeciesVariants is not None

    def test_knowledge_db_importable(self):
        assert KnowledgeDB is not None


class TestReport:
    def test_markdown_report(self):
        report = ReportGenerator()
        data = {
            "trace_id": "abc123",
            "query": "鳤",
            "species": "Ochetobius elongatus",
            "stages": {"sense": {"status": "completed", "summary": "ok", "duration_ms": 10.5}},
            "total_duration_ms": 100.5,
            "timestamp": "2026-01-01",
        }
        md = report.generate(data, format="markdown")
        assert "物种" in md
        assert "鳤" in md

    def test_json_report(self):
        report = ReportGenerator()
        data = {"test": True}
        out = report.generate(data, format="json")
        assert '"test": true' in out


class TestVisualizer:
    def test_radar_chart(self):
        viz = Visualizer()
        chart = viz.species_traits_radar({"length": 80, "trophic": 3.5})
        assert chart["type"] == "radar"
        assert len(chart["data"]) == 2

    def test_timeline(self):
        viz = Visualizer()
        chart = viz.search_timeline({2020: 5, 2021: 10})
        assert chart["type"] == "area"
