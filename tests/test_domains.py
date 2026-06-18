"""测试学科领域感受器"""
import sys
sys.path.insert(0, ".")

from src.senses.domains import (
    MathSense, PhysicsSense, PhilosophySense,
    ChinesePhilosophySense, MarxismSense,
    create_all_domains, create_domain,
)


class TestDomainSenses:
    def test_math_sense(self):
        s = MathSense()
        r = s.search("微积分")
        assert r["domain"] == "mathematics"
        assert len(r["concepts_found"]) >= 1
        assert "微积分" in r["concepts_found"][0]["concept"]

    def test_physics_sense(self):
        s = PhysicsSense()
        r = s.search("量子力学")
        assert r["domain"] == "physics"
        assert len(r["concepts_found"]) >= 1

    def test_philosophy_sense(self):
        s = PhilosophySense()
        r = s.search("辩证法")
        assert r["domain"] == "philosophy"
        assert len(r["concepts_found"]) >= 1

    def test_chinese_philosophy_dao(self):
        s = ChinesePhilosophySense()
        r = s.search("道")
        assert r["domain"] == "chinese_philosophy"
        assert len(r["concepts_found"]) >= 1

    def test_chinese_philosophy_confucius(self):
        s = ChinesePhilosophySense()
        r = s.search("仁")
        assert len(r["concepts_found"]) >= 1

    def test_chinese_philosophy_three_teachings(self):
        s = ChinesePhilosophySense()
        r = s.search("儒释道")
        assert len(r["concepts_found"]) >= 1

    def test_chinese_philosophy_thinkers(self):
        s = ChinesePhilosophySense()
        r = s.search("王阳明")
        assert len(r["thinkers_found"]) >= 1

    def test_marxism_sense(self):
        s = MarxismSense()
        r = s.search("辩证唯物主义")
        assert r["domain"] == "marxism"
        assert len(r["concepts_found"]) >= 1

    def test_marxism_mao(self):
        s = MarxismSense()
        r = s.search("毛泽东")
        assert len(r["thinkers_found"]) >= 1

    def test_thinkers_search(self):
        s = PhilosophySense()
        r = s.search("康德")
        assert len(r["thinkers_found"]) >= 1

    def test_create_all(self):
        senses = create_all_domains()
        assert len(senses) == 12  # 12 domain senses

    def test_create_single(self):
        s = create_domain("math")
        assert s is not None
        assert s.domain == "mathematics"

    def test_create_invalid(self):
        s = create_domain("nonexistent")
        assert s is None

    def test_is_wired(self):
        s = MathSense()
        assert not s.is_wired  # no MCP injected
        s2 = MathSense(search_fn=lambda q: {"results": []})
        assert s2.is_wired
