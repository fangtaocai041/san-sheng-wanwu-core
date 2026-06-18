"""测试感受器层"""
import sys
sys.path.insert(0, ".")

from src.senses.scholar import ScholarSense, SenseInput
from src.senses.cnki import CnkiSense
from src.senses.fishbase import FishBaseSense


class TestSenses:
    def test_scholar_input_output_types(self):
        """感受器输入输出类型正确。"""
        sense = ScholarSense()
        inp = SenseInput(query="鳤", species="Ochetobius elongatus")
        out = sense.sense(inp)
        assert out.query == "鳤"
        assert out.species == "Ochetobius elongatus"
        assert isinstance(out.total_found, int)
        assert isinstance(out.duration_ms, float)

    def test_scholar_simplified_api(self):
        """简化搜索接口兼容旧协议。"""
        sense = ScholarSense()
        result = sense.search("鳤")
        assert result["status"] == "ok"
        assert "total" in result

    def test_cnki_sense(self):
        """CNKI 感受器可实例化。"""
        sense = CnkiSense()
        inp = SenseInput(query="长江鱼类")
        out = sense.sense(inp)
        assert out.query == "长江鱼类"

    def test_fishbase_sense(self):
        """FishBase 感受器可实例化。"""
        sense = FishBaseSense()
        inp = SenseInput(query="Ochetobius elongatus")
        out = sense.sense(inp)
        assert out.sources_used == ["fishbase"]
