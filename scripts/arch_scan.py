"""Architecture scan for san-sheng-wanwu-core"""
import sys, os
sys.path.insert(0, ".")

root = "src"
modules = {}
for dirpath, dirnames, filenames in os.walk(root):
    py_files = [f for f in filenames if f.endswith(".py") and not f.startswith("__")]
    for f in py_files:
        path = os.path.join(dirpath, f)
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
        pkg = os.path.relpath(dirpath, root).replace(os.sep, ".")
        name = f[:-3]
        full = f"{pkg}.{name}"
        modules[full] = {
            "lines": len(lines),
            "imports": sum(1 for l in lines if l.strip().startswith(("from ", "import "))),
            "functions": sum(1 for l in lines if l.strip().startswith("def ")),
            "classes": sum(1 for l in lines if l.strip().startswith("class ")),
            "todos": sum(1 for l in lines if "TODO" in l or "FIXME" in l),
        }

sorted_mods = sorted(modules.items(), key=lambda x: x[1]["lines"], reverse=True)
print("=== ARCHITECTURE SCAN ===")
print(f"Total modules: {len(modules)}")
total_lines = sum(m["lines"] for m in modules.values())
print(f"Total lines: {total_lines}")
total_funcs = sum(m["functions"] for m in modules.values())
total_classes = sum(m["classes"] for m in modules.values())
print(f"Total functions: {total_funcs}, classes: {total_classes}")
print()

print("Top 10 largest modules:")
for name, stats in sorted_mods[:10]:
    print(f"  {stats['lines']:5d}L {stats['functions']:3d}F {stats['classes']:2d}C  {name}")
print()

todos = [(n, s) for n, s in sorted_mods if s["todos"] > 0]
if todos:
    print(f"Modules with TODOs ({len(todos)}):")
    for name, stats in todos:
        print(f"  {stats['todos']} TODO(s) in {name}")
else:
    print("No TODOs found.")
print()

large = [(n, s) for n, s in sorted_mods if s["lines"] > 300]
print(f"Modules over 300 lines ({len(large)}):")
for name, stats in large:
    print(f"  {stats['lines']}L {name}")
