#!/usr/bin/env python3
"""验证硅基生命体架构完整性。

用法: python scripts/verify_architecture.py
"""
import sys
sys.path.insert(0, ".")

checks = {
    "senses": 5,   # 5 个感受器
    "cortex": 4,   # 4 个认知模块
    "memory": 2,   # 2 个记忆模块
    "motor": 2,    # 2 个运动模块
}
passed = 0
failed = 0

for layer, expected in checks.items():
    mod = __import__(f"src.{layer}", fromlist=["__all__"])
    try:
        symbols = mod.__all__
        count = len(symbols)
        status = "OK" if count == expected else f"MISMATCH (expected {expected}, got {count})"
        if "OK" in status:
            passed += 1
        else:
            failed += 1
        print(f"  [{status}] {layer}: {count} modules ({', '.join(symbols)})")
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
