"""测试语义编码器"""
import sys
sys.path.insert(0, ".")

from src.memory.magma import (
    CharacterNgramEncoder, _char_ngrams, _jaccard,
)
from src.memory import MagmaMemory


class TestSemanticEncoder:
    def test_char_ngram(self):
        ngrams = _char_ngrams("长江鱼类", 2)
        assert "长江" in ngrams
        assert "江鱼" in ngrams
        assert "鱼类" in ngrams

    def test_jaccard(self):
        sim = _jaccard({"a", "b"}, {"a", "c"})
        assert sim == 1/3  # 1 overlap / 3 union

    def test_encoder_similarity(self):
        enc = CharacterNgramEncoder()
        sim = enc.similarity("长江鱼类", "长江鱼类")
        assert sim > 0.9  # 相同文本

    def test_encoder_different(self):
        enc = CharacterNgramEncoder()
        sim = enc.similarity("长江鱼类", "气候变化")
        assert sim < 0.5  # 不同主题

    def test_encoder_partial(self):
        enc = CharacterNgramEncoder()
        sim = enc.similarity("长江鱼类保护", "长江鱼类")
        assert sim > 0.3  # 部分重叠

    def test_empty_text(self):
        enc = CharacterNgramEncoder()
        sim = enc.similarity("", "test")
        assert sim == 0.0

    def test_semantic_search(self):
        mem = MagmaMemory(encoder_backend="char_ngram")
        mem.add("鳤是长江珍稀鱼类")
        mem.add("刀鲚是洄游鱼类")
        mem.add("今天天气很好")
        # "珍稀水生生物" 与第一条语义相关 (共享 "珍稀" "鱼" n-gram)
        results = mem.search("珍稀水生生物")
        assert len(results) >= 1
        assert "鳤" in results[0].content or "珍稀" in results[0].content

    def test_semantic_relation(self):
        mem = MagmaMemory(encoder_backend="char_ngram")
        n1 = mem.add("长江鱼类资源调查与评估方法")
        n2 = mem.add("长江鱼类资源的调查评估报告")
        stats = mem.stats()
        assert stats["graphs"]["semantic"] >= 1
