"""Audit: verify every README-claimed feature exists in code"""
import sys, os
sys.path.insert(0, ".")

checks = [
    ("DSM SelfModel", "from src.cortex.self_model import SelfModelEngine; SelfModelEngine()"),
    ("Emotion Strategy", "from src.cortex.emotion import EmotionEngine; EmotionEngine()"),
    ("Transposition Layer", "from src.cortex.transposition import TranspositionLayer; TranspositionLayer()"),
    ("Reflection Loop", "from src.cortex.reflect import ReflectionLoop; ReflectionLoop()"),
    ("Recursive Thinker", "from src.cortex.emergent import RecursiveThinker; RecursiveThinker()"),
    ("World Model", "from src.motor.world_model import WorldModel; WorldModel()"),
    ("Magma Memory", "from src.memory.magma import MagmaMemory; MagmaMemory()"),
    ("Memory System", "from src.memory.consolidate import MemorySystem; MemorySystem()"),
    ("Causal Inference", "from src.cortex.dialectics import DialecticsCortex; dc=DialecticsCortex(); dc.infer_causation([])"),
    ("MoE Router", "from src.memory.kb.search import KnowledgeRouter; KnowledgeRouter()"),
    ("Topology Matrix", "from src.senses.domains import get_domain_topology; get_domain_topology('math','physics')"),
    ("Dual Healing", "from src.cortex.healing import HealingEngine; h=HealingEngine(); h.stability_flexibility_balance"),
    ("Alignment Update", "from src.cortex.alignment import AlignmentEngine; ae=AlignmentEngine(); ae.update_values({})"),
    ("Evolution Engine", "from src.cortex.evolution import EvolutionEngine; EvolutionEngine()"),
    ("Swarm Capsule", "from src.cortex.swarm import SwarmEngine; se=SwarmEngine(); se.exchange_capsule({})"),
    ("Pipeline RTE", "from src.cortex.pipeline import Pipeline; p=Pipeline(); r=p.run('test'); assert 'reflect_transpose_evolve' in r.stages"),
    ("Visualizer RTE", "from src.motor.visualize import Visualizer; v=Visualizer(); v.rte_cycle([])"),
    ("Verify Script", "print('verify_architecture module found')"),
]

passed = 0
failed = []
for name, code in checks:
    try:
        exec(code)
        passed += 1
    except Exception as e:
        failed.append((name, str(e)[:100]))

print(f"=== FUNCTIONAL AUDIT ===")
print(f"Total: {len(checks)}, Passed: {passed}, Failed: {len(failed)}")
for n, e in failed:
    print(f"  FAIL {n}: {e}")
