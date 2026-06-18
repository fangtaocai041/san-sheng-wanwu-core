#!/usr/bin/env python3
"""验证硅基生命体架构完整性。

检查: 模块导出数、关键文件存在、配置文件有效、测试通过。

用法: python scripts/verify_architecture.py
"""
import os
import sys
sys.path.insert(0, ".")

passed = 0
failed = 0

def check(label: str, ok: bool, detail: str = ""):
    global passed, failed
    if ok:
        passed += 1
        print(f"  [OK] {label}{'  ' + detail if detail else ''}")
    else:
        failed += 1
        print(f"  [FAIL] {label}{'  ' + detail if detail else ''}")

# ── GATE 1: 模块导出 ──
layers = {
    "senses": ("感受器", 5),
    "cortex": ("认知皮层", 4),
    "memory": ("记忆", 2),
    "motor": ("运动皮层", 2),
}
for layer, (label, min_expected) in layers.items():
    try:
        mod = __import__(f"src.{layer}", fromlist=["__all__"])
        count = len(mod.__all__)
        check(f"{label} (src/{layer})", count >= min_expected, f"{count} symbols")
    except Exception as e:
        check(f"{label} (src/{layer})", False, str(e))

# ── GATE 2: 关键文件 ──
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
required_files = [
    "AGENTS.md", "README.md", "pyproject.toml", ".gitignore",
    "config/coordination.yaml",
    "config/species_variants.yaml",
    "config/fish_species_index.yaml",
    "data/yangtze_species_list.txt",
    "scripts/verify_architecture.py",
    "src/memory/kb/db.py", "src/memory/kb/search.py",
    "src/memory/kb/credibility.py", "src/memory/kb/variants.py",
    "src/senses/scholar.py", "src/senses/cnki.py", "src/senses/ncbi.py",
    "src/senses/fishbase.py", "src/senses/web.py",
    "src/cortex/dialectics.py", "src/cortex/validate.py",
    "src/cortex/emergent.py", "src/cortex/pipeline.py",
]
for f in required_files:
    path = os.path.join(root, f)
    check(f"File: {f}", os.path.isfile(path))

# ── GATE 3: coordination.yaml 有效 ──
try:
    import yaml
    with open(os.path.join(root, "config", "coordination.yaml"), encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    check("coordination.yaml parseable", cfg is not None)
    check("  has senses", "senses" in cfg)
    check("  has cortex", "cortex" in cfg)
    check("  has memory", "memory" in cfg)
    check("  has motor", "motor" in cfg)
    check("  has pathways", "pathways" in cfg)
except Exception as e:
    check("coordination.yaml", False, str(e))

# ── GATE 4: 核心模块可通过 pipeline 加载 ──
try:
    from src.cortex.pipeline import Pipeline, SenseFactory, get_knowledge_base
    check("Pipeline importable", True)
    p = Pipeline()
    check("Pipeline instanced", len(p.trace_id) == 32)
    senses = SenseFactory.all_senses()
    check("SenseFactory.all_senses()", len(senses) == 5, f"{len(senses)} senses")
except Exception as e:
    check("Pipeline/SenseFactory", False, str(e))

# ── GATE 5: 测试 ──
import subprocess
r = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "--tb=line"],
                   capture_output=True, text=True, timeout=30)
r_line = r.stdout.strip().split("\n")[-1].strip() if r.stdout else ""
check("Tests pass", r.returncode == 0, r_line)
if r.returncode != 0:
    for line in r.stderr.split("\n")[:3]:
        print(f"       {line.strip()}")

# ── 总结 ──
total = passed + failed
print(f"\n  {'='*40}")
print(f"  Architecture: {passed}/{total} checks passed")
print(f"  {'OK' if failed == 0 else f'{failed} FAILURES'}")
sys.exit(0 if failed == 0 else 1)
