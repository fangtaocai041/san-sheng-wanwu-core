#!/usr/bin/env python3
"""验证硅基生命体架构完整性。

用法: python scripts/verify_architecture.py
"""
import sys
sys.path.insert(0, ".")

checks = {
    "senses": ("感受器", 5),   # 至少 5 个
    "cortex": ("认知皮层", 4), # 至少 4 个类
    "memory": ("记忆", 2),    # 至少 2 个
    "motor": ("运动皮层", 2), # 至少 2 个
}
passed = 0
failed = 0

for layer, (label, min_expected) in checks.items():
    mod = __import__(f"src.{layer}", fromlist=["__all__"])
    try:
        symbols = mod.__all__
        count = len(symbols)
        status = "OK" if count >= min_expected else f"TOO FEW (min {min_expected}, got {count})"
        if "OK" in status:
            passed += 1
        else:
            failed += 1
        print(f"  [{status}] {label} ({layer}): {count} symbols exported")
    except Exception as e:
        print(f"  [ERROR] {layer}: {e}")
        failed += 1

# 测试
import subprocess
r = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "--tb=line"],
                   capture_output=True, text=True, timeout=30)
print(f"\n  Tests: {r.stdout.strip().split(chr(10))[-1].strip()}")
if r.returncode == 0:
    passed += 1
else:
    failed += 1

print(f"\n  {'='*40}")
print(f"  Architecture: {passed}/{passed+failed} checks passed")
print(f"  {'OK' if failed == 0 else 'FAILED'}")
sys.exit(0 if failed == 0 else 1)
