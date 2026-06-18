"""测试感受器层"""
import sys
sys.path.insert(0, ".")

from src.senses.scholar import ScholarSense, SenseInput
from src.senses.cnki import CnkiSense
from src.senses.fishbase import FishBaseSense
from src.senses.web import WebSense


class TestSenses:
    def test_scholar_input_output_types(self):
        sense = ScholarSense()
        inp = SenseInput(query="鳤", species="Ochetobius elongatus")
        out = sense.sense(inp)
        assert out.query == "鳤"
        assert out.species == "Ochetobius elongatus"
        assert isinstance(out.total_found, int)
        assert isinstance(out.duration_ms, float)

    def test_scholar_simplified_api(self):
        sense = ScholarSense()
        result = sense.search("鳤")
        assert result["status"] == "ok"

    def test_cnki_sense(self):
        sense = CnkiSense()
        inp = SenseInput(query="长江鱼类")
        out = sense.sense(inp)
        assert out.query == "长江鱼类"

    def test_fishbase_sense(self):
        sense = FishBaseSense()
        inp = SenseInput(query="Ochetobius elongatus")
        out = sense.sense(inp)
        assert out.query == "Ochetobius elongatus"
        assert len(out.errors) > 0  # stub mode
        assert "stub" in out.errors[0]

    def test_web_sense(self):
        sense = WebSense()
        inp = SenseInput(query="长江十年禁渔")
        out = sense.sense(inp)
        assert out.query == "长江十年禁渔"
