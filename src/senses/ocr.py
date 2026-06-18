"""
senses/ocr.py — OCR 视觉感受器 (PaddleOCR-VL)

感知模态: 从图像中提取文本信息。
将物理世界的像素转化为数字世界的结构化文本。

MCP 注入 (重启后):
  config in reasonix.toml:
    [[plugins]]
    name = "paddleocr"
    command = "uvx"
    args = ["--from", "paddleocr-mcp", "paddleocr_mcp"]
    env = { PADDLEOCR_MCP_MODEL = "PaddleOCR-VL-1.6", ... }

直接 API 模式 (无需 MCP):
  OcrSense(api_token="...")
  result = sense.recognize("path/to/image.jpg")
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import os
import time
import requests


@dataclass
class OcrResult:
    """OCR 识别结果。"""
    text: str = ""
    images_found: int = 0
    pages: int = 0
    duration_ms: float = 0.0
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "text": self.text[:500],
            "text_length": len(self.text),
            "images_found": self.images_found,
            "pages": self.pages,
            "duration_ms": round(self.duration_ms, 1),
            "error": self.error,
        }


class OcrSense:
    """OCR 视觉感受器 — 将图像转化为文本。

    两种模式:
      1. MCP 注入: OcrSense(ocr_tool=mcp_tool_fn)
      2. 直接 API: OcrSense(api_token="...")

    用法:
        sense = OcrSense(api_token="97fc...")
        result = sense.recognize("image.jpg")
        print(result.text)
    """

    def __init__(self, ocr_tool: Optional[Callable] = None,
                 api_token: str = ""):
        self.name = "ocr"
        self._tool = ocr_tool
        self._token = api_token
        self._api_url = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"

    @property
    def is_wired(self) -> bool:
        return self._tool is not None or bool(self._token)

    def recognize(self, image_path: str) -> OcrResult:
        """识别图像中的文本。"""
        t0 = time.time()

        if self._tool:
            return self._via_mcp(image_path, t0)
        elif self._token:
            return self._via_api(image_path, t0)
        else:
            return OcrResult(error="No OCR tool or API token injected (stub mode)")

    def _via_api(self, image_path: str, t0: float) -> OcrResult:
        """通过 AIStudio REST API 识别。"""
        if not os.path.exists(image_path):
            return OcrResult(error=f"File not found: {image_path}",
                            duration_ms=(time.time() - t0) * 1000)

        headers = {"Authorization": f"bearer {self._token}"}

        try:
            with open(image_path, "rb") as f:
                files = {"file": f}
                data = {
                    "model": "PaddleOCR-VL-1.6",
                    "optionalPayload": json.dumps({
                        "useDocOrientationClassify": False,
                        "useDocUnwarping": False,
                        "useChartRecognition": False,
                    }),
                }
                resp = requests.post(
                    self._api_url, headers=headers,
                    data=data, files=files, timeout=30
                )

            if resp.status_code != 200:
                return OcrResult(
                    error=f"API error {resp.status_code}: {resp.text[:200]}",
                    duration_ms=(time.time() - t0) * 1000,
                )

            job_id = resp.json()["data"]["jobId"]

            # Poll for result
            for _ in range(60):
                r = requests.get(
                    f"{self._api_url}/{job_id}",
                    headers=headers, timeout=15
                )
                state = r.json()["data"]["state"]

                if state == "done":
                    jsonl_url = r.json()["data"]["resultUrl"]["jsonUrl"]
                    jr = requests.get(jsonl_url, timeout=30)
                    texts = []
                    for line in jr.text.strip().split("\n"):
                        if line.strip():
                            result = json.loads(line)["result"]
                            for res in result["layoutParsingResults"]:
                                texts.append(res["markdown"]["text"])

                    return OcrResult(
                        text="\n".join(texts),
                        pages=len(texts),
                        duration_ms=(time.time() - t0) * 1000,
                    )

                elif state == "failed":
                    err = r.json()["data"].get("errorMsg", "unknown")
                    return OcrResult(
                        error=f"OCR failed: {err}",
                        duration_ms=(time.time() - t0) * 1000,
                    )

                time.sleep(3)

            return OcrResult(
                error="Timeout waiting for OCR result",
                duration_ms=(time.time() - t0) * 1000,
            )

        except Exception as e:
            return OcrResult(
                error=str(e),
                duration_ms=(time.time() - t0) * 1000,
            )

    def _via_mcp(self, image_path: str, t0: float) -> OcrResult:
        """通过 MCP 工具识别 (重启后可用)。"""
        try:
            result = self._tool(image_path)
            if isinstance(result, dict):
                text = result.get("text", result.get("markdown", ""))
                return OcrResult(
                    text=text,
                    duration_ms=(time.time() - t0) * 1000,
                )
        except Exception as e:
            return OcrResult(error=str(e), duration_ms=(time.time() - t0) * 1000)

    def search(self, query: str, **kwargs) -> dict:
        """兼容感受器统一接口。"""
        image_path = kwargs.get("image", kwargs.get("path", ""))
        if not image_path:
            return {"status": "error", "error": "No image path provided"}
        result = self.recognize(image_path)
        return {
            "status": "ok" if not result.error else "error",
            "domain": "ocr",
            "text": result.text[:500],
            "text_length": len(result.text),
            "pages": result.pages,
            "duration_ms": result.duration_ms,
            "error": result.error,
        }
