"""测试代码执行层自进化"""
import sys
sys.path.insert(0, ".")
import os
import tempfile

from src.cortex.evolution import EvolutionEngine, MutationEngine


class TestMutation:
    def test_add_docstring(self):
        from src.cortex.evolution import _mutate_add_docstring
        source = "x = 1"
        result = _mutate_add_docstring(source, "/tmp/test.py")
        assert result is not None
        assert '"""' in result

    def test_no_docstring_if_exists(self):
        from src.cortex.evolution import _mutate_add_docstring
        source = '"""already"""\nx = 1'
        result = _mutate_add_docstring(source, "/tmp/test.py")
        assert result is None

    def test_mutation_engine(self):
        eng = MutationEngine()
        result = eng.apply("x = 1", "/tmp/test.py")
        assert result is not None
        assert result != "x = 1"


class TestEvolution:
    def test_readonly_default(self):
        eng = EvolutionEngine()
        assert eng.is_readonly

    def test_unlock(self):
        eng = EvolutionEngine()
        eng.unlock()
        assert not eng.is_readonly
        eng.lock()
        assert eng.is_readonly

    def test_evolve_locked(self):
        eng = EvolutionEngine()
        ev = eng.evolve_file("/nonexistent.py")
        assert not ev.success  # safety lock

    def test_evolve_nonexistent(self):
        eng = EvolutionEngine(test_cmd="echo ok")
        eng.unlock()
        ev = eng.evolve_file("/nonexistent.py")
        assert not ev.success  # file not found

    def test_evolve_no_mutation(self):
        eng = EvolutionEngine(test_cmd="echo ok")
        eng.unlock()
        import tempfile, os
        fname = os.path.join(os.path.dirname(__file__), "_tmp_test_evolve.py")
        try:
            with open(fname, "w", encoding="utf-8") as f:
                f.write('"""already"""\nx = 1\n')
            ev = eng.evolve_file(fname)
            assert ev.success  # skipped (no mutation applicable)
        finally:
            if os.path.isfile(fname):
                os.unlink(fname)
            if os.path.isfile(fname + ".bak"):
                os.unlink(fname + ".bak")

    def test_analysis_imports(self):
        eng = EvolutionEngine()
        # 分析自身
        result = eng.analyze_file(__file__)
        assert result["status"] == "ok"
        assert result["functions"] > 0
