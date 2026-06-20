"""Code audit: check for missing __init__.py and __all__ consistency"""
import sys, os, subprocess
sys.path.insert(0, ".")

issues = []

# Check for missing __init__.py in package dirs
for root, dirs, files in os.walk("src"):
    if "__init__.py" not in files and any(f.endswith(".py") for f in files):
        rel = os.path.relpath(root, "src")
        issues.append(f"MISSING __init__.py in {rel}")

# Check scripts parse
for root, dirs, files in os.walk("scripts"):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            try:
                subprocess.run([sys.executable, "-c", f"import ast; ast.parse(open('{path}','r',encoding='utf-8').read())"],
                             capture_output=True, timeout=5, check=True)
            except:
                issues.append(f"PARSE ERROR: {path}")

# Check __all__ items exist in module content (simplified)
for root, dirs, files in os.walk("src"):
    for f in files:
        if f == "__init__.py":
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read()
            if "__all__" not in content:
                continue
            all_items = []
            in_all = False
            for line in content.split("\n"):
                s = line.strip()
                if "__all__" in s and "=" in s:
                    in_all = True
                elif in_all and s.startswith("]"):
                    break
                elif in_all and '"' in s:
                    parts = s.split('"')
                    if len(parts) >= 2 and parts[1]:
                        all_items.append(parts[1])
            for item in all_items:
                if item not in content:
                    issues.append(f"__all__ item '{item}' not imported in {path}")

# Check tests import correctly
test_errors = []
for f in sorted(os.listdir("tests")):
    if f.startswith("test_") and f.endswith(".py"):
        try:
            subprocess.run([sys.executable, "-m", "pytest", f"tests/{f}", "-q", "--tb=line"],
                         capture_output=True, timeout=30, check=True)
        except subprocess.CalledProcessError as e:
            output = e.stdout.decode() if e.stdout else ""
            failed_count = output.strip().split("\n")[-1] if output else "?"
            test_errors.append(f"TEST FAIL: {f}: {failed_count}")

print(f"Total issues: {len(issues)}")
for i in issues:
    print(f"  {i}")
if not issues:
    print("No issues found.")

print(f"\nTest errors: {len(test_errors)}")
for t in test_errors:
    print(f"  {t}")
if not test_errors:
    print("No test errors found.")
