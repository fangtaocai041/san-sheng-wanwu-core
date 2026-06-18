"""OCR using PaddleOCR AIStudio API"""
import json, os, requests, sys, time

TOKEN = "97fc64ceff2e3df3511f7d61607247a390a092c5"
MODEL = "PaddleOCR-VL-1.6"
JOB_URL = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
FILE_PATH = r"C:\Users\小陶\AppData\Roaming\reasonix\global-workspace\.reasonix\attachments\clipboard-20260619-011728.426485-000029.jpg"

headers = {"Authorization": f"bearer {TOKEN}"}
print(f"Uploading: {FILE_PATH}")

with open(FILE_PATH, "rb") as f:
    files = {"file": f}
    data = {
        "model": MODEL,
        "optionalPayload": json.dumps({
            "useDocOrientationClassify": False,
            "useDocUnwarping": False,
            "useChartRecognition": False,
        }),
    }
    resp = requests.post(JOB_URL, headers=headers, data=data, files=files, timeout=30)

print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Error: {resp.text[:500]}")
    sys.exit(1)

jobId = resp.json()["data"]["jobId"]
print(f"Job ID: {jobId}")

for attempt in range(60):
    r = requests.get(f"{JOB_URL}/{jobId}", headers=headers, timeout=15)
    state = r.json()["data"]["state"]
    if state == "done":
        jsonl_url = r.json()["data"]["resultUrl"]["jsonUrl"]
        print(f"Done! Fetching results...")
        jr = requests.get(jsonl_url, timeout=30)
        for line in jr.text.strip().split("\n"):
            if line.strip():
                result = json.loads(line)["result"]
                for res in result["layoutParsingResults"]:
                    text = res["markdown"]["text"]
                    print(text)
        break
    elif state == "failed":
        err = r.json()["data"].get("errorMsg", "unknown")
        print(f"Failed: {err}")
        break
    else:
        print(f"  Status: {state} (attempt {attempt+1})")
        time.sleep(3)
