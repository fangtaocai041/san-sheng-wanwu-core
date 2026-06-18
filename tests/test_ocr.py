"""测试 OCR 感受器"""
import sys
sys.path.insert(0, ".")
import os

from src.senses.ocr import OcrSense, OcrResult


class TestOcrSense:
    def test_stub_mode(self):
        sense = OcrSense()
        assert not sense.is_wired
        result = sense.recognize("nonexistent.jpg")
        assert result.error is not None
        assert "stub" in result.error

    def test_api_token_wired(self):
        sense = OcrSense(api_token="test_token")
        assert sense.is_wired

    def test_ocr_result_dataclass(self):
        r = OcrResult(text="hello world", pages=1, duration_ms=100.0)
        assert r.text == "hello world"
        d = r.to_dict()
        assert d["text_length"] == 11
        assert d["pages"] == 1

    def test_ocr_result_error(self):
        r = OcrResult(error="something failed")
        assert r.error == "something failed"
        d = r.to_dict()
        assert d["error"] is not None

    def test_search_compat(self):
        sense = OcrSense()
        result = sense.search("test", path="/nonexistent")
        assert result["status"] == "error"  # stub mode
