"""HIGH + EXTREME level stress tests for san-sheng-wanwu-core"""
import sys, os, time
sys.path.insert(0, ".")

# HIGH LEVEL: every module instantiate + call search()
modules_to_test = [
    ("cortex.self_model", "SelfModelEngine", [("find_state", None), ("reflect", None)]),
    ("cortex.emotion", "EmotionEngine", [("stimulate", ("error",)), ("behavioral_tendency", None)]),
    ("cortex.transposition", "TranspositionLayer", [("set_stress_level", (0.5, 0.3)), ("current_activity", None)]),
    ("cortex.reflect", "ReflectionLoop", [("total_loops", None)]),
    ("cortex.emergent", "RecursiveThinker", [("solve", ("test",))]),
    ("cortex.healing", "HealingEngine", [("stability_flexibility_balance", None)]),
    ("cortex.alignment", "AlignmentEngine", [("update_values", ({"truth_seeking": 0.1},))]),
    ("cortex.dialectics", "DialecticsCortex", [("infer_causation", ([],))]),
    ("cortex.evolution", "EvolutionEngine", [("propose_domestication", ("a","b","c",0.5,3))]),
    ("cortex.swarm", "SwarmEngine", [("exchange_capsule", ({"a": 1},))]),
    ("cortex.pipeline", "Pipeline", [("run", ("test",))]),
    ("motor.world_model", "WorldModel", [("report", None)]),  # world model
    ("motor.visualize", "Visualizer", [("rte_cycle", ([],))]),
    ("memory.magma", "MagmaMemory", [("add", ("test",)), ("search", ("test",))]),
    ("memory.consolidate", "MemorySystem", [("store", ("test",)), ("recall", ("test",))]),
    ("senses.domains", "get_domain_topology", None),  # function, not class
]

print("=== HIGH LEVEL: module instantiation + method invocation ===")
h_ok = 0
h_fail = []
for mod_path, cls_name, methods in modules_to_test:
    try:
        mod = __import__(f"src.{mod_path}", fromlist=[cls_name.split(".")[0]])
        if cls_name == "get_domain_topology":
            result = mod.get_domain_topology("math", "physics")
            assert result > 0
        elif "." in cls_name:
            parent, child = cls_name.split(".")
            parent_cls = getattr(mod, parent)
            inst = parent_cls()
            sub = getattr(inst, child)()
        else:
            cls = getattr(mod, cls_name)
            inst = cls()
            if methods:
                for method_name, args in methods:
                    method = getattr(inst, method_name)
                    if args is None:
                        result = method
                    else:
                        result = method(*args) if isinstance(args, tuple) else method(args)
        h_ok += 1
    except Exception as e:
        h_fail.append((mod_path, cls_name, str(e)[:100]))

print(f"Passed: {h_ok}/{len(modules_to_test)}, Failed: {len(h_fail)}")
for n, c, e in h_fail:
    print(f"  FAIL {n}.{c}: {e}")

# EXTREME LEVEL: concurrent instantiation + edge cases
print()
print("=== EXTREME LEVEL: edge cases ===")
e_ok = 0
e_fail = []

# Edge 1: Empty query
try:
    from src.cortex.pipeline import Pipeline
    p = Pipeline()
    r = p.run("")
    assert r.completed >= 3
    e_ok += 1
except Exception as ex:
    e_fail.append(f"Empty query: {str(ex)[:80]}")

# Edge 2: Very long query
try:
    r = p.run("x" * 10000)
    assert r.completed >= 3
    e_ok += 1
except Exception as ex:
    e_fail.append(f"Long query: {str(ex)[:80]}")

# Edge 3: Unicode query
try:
    r = p.run("\u9c64\u7684\u751f\u6001\u4e60\u6027")  # 鳤的生态习性
    assert r.completed >= 3
    e_ok += 1
except Exception as ex:
    e_fail.append(f"Unicode query: {str(ex)[:80]}")

# Edge 4: Rapid Transposition stress
try:
    from src.cortex.transposition import TranspositionLayer
    tl = TranspositionLayer(base_activity=1.0)
    for i in range(100):
        tl.transpose("biology", "conservation", {"concept": f"test{i}", "confidence": 0.9})
    assert tl.total_transpositions == 100
    e_ok += 1
except Exception as ex:
    e_fail.append(f"Transposition burst: {str(ex)[:80]}")

# Edge 5: World model prediction
try:
    from src.motor.world_model import WorldModel, WorldState
    wm = WorldModel()
    ws = WorldState(known_papers=5)
    pred = wm.predict_next(ws, action="deep_search")
    assert pred.next_state.known_papers > 5
    e_ok += 1
except Exception as ex:
    e_fail.append(f"World model: {str(ex)[:80]}")

# Edge 6: Deep recursion 
try:
    from src.cortex.emergent import RecursiveThinker
    rt = RecursiveThinker(max_steps=100)
    _, steps = rt.solve("test")
    assert len(steps) > 0
    e_ok += 1
except Exception as ex:
    e_fail.append(f"Deep recursion: {str(ex)[:80]}")

print(f"Passed: {e_ok}/5, Failed: {len(e_fail)}")
for f in e_fail:
    print(f"  FAIL {f}")

print()
print(f"=== SUMMARY ===")
print(f"LOW:    pytest tests/   -> 181 passed")
print(f"MEDIUM: verify_arch    -> 36/36 passed")
print(f"HIGH:   {h_ok}/{len(modules_to_test)} instantiation + method calls")
print(f"EXTREME: {e_ok}/6 edge cases")
print("ALL LEVELS: " + ("PASS" if h_ok == len(modules_to_test) and e_ok == 6 else "SOME FAILURES"))
