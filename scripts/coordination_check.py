import sys, os, time
sys.path.insert(0, ".")

# Force UTF-8 output for Windows console
if sys.platform == "win32":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")

ok = 0
fail = []
def check(name, code):
    global ok
    try:
        exec(code)
        ok += 1
        print(f"  [OK] {name}")
    except Exception as e:
        fail.append((name, str(e)[:120]))
        print(f"  [FAIL] {name}: {str(e)[:80]}")

print("=" * 60)
print("COORDINATION SELF-CHECK: module connection paths")
print("=" * 60)

# 1. Core modules activation
check("1.1 SelfModelEngine", "from src.cortex.self_model import SelfModelEngine; m=SelfModelEngine(); s=m.reflect(); assert s.stability >= 0")
check("1.2 EmotionEngine", "from src.cortex.emotion import EmotionEngine; e=EmotionEngine(); e.stimulate('contradiction',1.0); assert e.state.dominant")
check("1.3 TranspositionLayer", "from src.cortex.transposition import TranspositionLayer; t=TranspositionLayer(); ev=t.transpose('a','b',{'concept':'t','confidence':1.0}); assert ev.source_domain=='a'")
check("1.4 ReflectionLoop", "from src.cortex.reflect import ReflectionLoop; r=ReflectionLoop(); assert r.name=='reflection_loop'")
check("1.5 Pipeline", "from src.cortex.pipeline import Pipeline; p=Pipeline(); r=p.run('selftest'); assert 'sense' in r.stages")
check("1.6 WorldModel", "from src.motor.world_model import WorldModel,WorldState; w=WorldModel(); s=WorldState(known_papers=3); p=w.predict_next(s,'search'); assert p.next_state.known_papers>3")
check("1.7 KnowledgeRouter", "from src.memory.kb.search import KnowledgeRouter; k=KnowledgeRouter(); s=k.suggest_search_strategy('test'); assert 'activated_experts' in s")
check("1.8 MagmaMemory", "from src.memory.magma import MagmaMemory; m=MagmaMemory(); n=m.add('test content'); r=m.search('test'); assert len(r)>=1")
check("1.9 RecursiveThinker", "from src.cortex.emergent import RecursiveThinker; r=RecursiveThinker(max_steps=3); a,s=r.solve('test'); assert len(s)>0")
check("1.10 CausalInference", "from src.cortex.dialectics import DialecticsCortex; d=DialecticsCortex(); r=d.infer_causation([{'factor':'A','outcome':'X'},{'factor':'A','outcome':'X'}]); assert len(r)>=1")
check("1.11 SwarmCapsule", "from src.cortex.swarm import SwarmEngine; s=SwarmEngine(); r=s.exchange_capsule({'content':[1],'confidence':0.8}); assert r>=1")
check("1.12 AlignmentUpdate", "from src.cortex.alignment import AlignmentEngine; a=AlignmentEngine(); a.update_values({'truth_seeking':0.1}); assert a._values.get('truth_seeking',0)>0")
check("1.13 EvolutionProposal", "from src.cortex.evolution import EvolutionEngine; e=EvolutionEngine(); p=e.propose_domestication('a','b','c',0.5,3); assert p.author=='transposition_layer'")
check("1.14 DualHealing", "from src.cortex.healing import HealingEngine; h=HealingEngine(); assert h.stability_flexibility_balance==0.5")
check("1.15 VisualizerRTE", "from src.motor.visualize import Visualizer; v=Visualizer(); r=v.rte_cycle([{'tl_activity':0.5,'domesticated':1}]); assert len(r['series'])==2")

# 2. Module interconnections
print()
print("--- Inter-module paths ---")

check("2.1 Emotion to Transposition", """
from src.cortex.transposition import TranspositionLayer
from src.cortex.emotion import EmotionEngine
tl=TranspositionLayer(); e=EmotionEngine(transposition_layer=tl)
a1=tl.current_activity
e.stimulate('contradiction',intensity=1.0)
e.stimulate('contradiction',intensity=1.0)
assert tl.current_activity > a1
""")

check("2.2 Transposition to Evolution", """
from src.cortex.transposition import TranspositionLayer
from src.cortex.evolution import EvolutionEngine
tl=TranspositionLayer(base_activity=1.0); evo=EvolutionEngine()
for i in range(5):
    tl.transpose('biology','conservation',{'concept':'test','confidence':0.9,'type':'concept'})
for dp in tl.get_domesticated_pathways():
    if dp.success_count>=2:
        prop=evo.propose_domestication(dp.source_domain,dp.target_domain,dp.pattern_type,dp.avg_fitness_delta,dp.success_count)
        assert 'domestication' in prop.description
        break
""")

check("2.3 Pipeline RTE phase", """
from src.cortex.pipeline import Pipeline
p=Pipeline(); r=p.run('selftest')
assert 'reflect_transpose_evolve' in r.stages
""")

check("2.4 SiliconAgent wiring", """
from src.main import SiliconAgent
a=SiliconAgent(db_path=':memory:')
assert hasattr(a,'transposition')
assert hasattr(a,'emotion')
assert a.emotion._tl is not None
""")

check("2.5 Thinker + Transposition", """
from src.cortex.emergent import RecursiveThinker
from src.cortex.transposition import TranspositionLayer
r=RecursiveThinker(max_steps=3); t=TranspositionLayer()
ans,steps=r.solve('test')
ev=t.transpose('think','act',{'concept':ans,'confidence':0.5})
assert isinstance(ev.source_domain,str)
""")

check("2.6 WorldModel + Pipeline compatible", """
from src.motor.world_model import WorldModel,WorldState
from src.cortex.pipeline import Pipeline
w=WorldModel(); p=Pipeline()
r=p.run('selftest')
s=WorldState(known_papers=len(r.stages))
pred=w.predict_next(s,'verify')
assert pred.next_state.confidence >= 0
""")

# 3. End-to-end
print()
print("--- End-to-end ---")

check("3.1 SiliconAgent full cycle", """
import tempfile, os
from src.main import SiliconAgent
db=tempfile.mktemp(suffix='.db')
a=SiliconAgent(db_path=db)
a.wake()
r=a.run('selftest', verbose=False)
os.unlink(db)
assert 'self_model' in r
assert 'emotion' in r
assert 'transposition' in r
""")

check("3.2 CLI status", """
import tempfile, os
from src.main import SiliconAgent
db=tempfile.mktemp(suffix='.db')
a=SiliconAgent(db_path=db)
s=a.status()
os.unlink(db)
assert 'self_model' in s and 'emotion' in s and 'transposition' in s
""")

check("3.3 verify_architecture", """
import subprocess,sys
r=subprocess.run([sys.executable,'scripts/verify_architecture.py'],capture_output=True,text=True,timeout=30)
assert r.returncode==0
""")

# 4. Data consistency
print()
print("--- Data consistency ---")

check("4.1 Unified Sense protocol", """
from src.senses.scholar import SenseInput,SenseOutput
inp=SenseInput(query='test')
out=SenseOutput(query='test')
assert hasattr(out,'to_dict')
""")

# 5. Edge cases
print()
print("--- Edge cases ---")

check("5.1 Empty query pipeline", """
from src.cortex.pipeline import Pipeline
p=Pipeline(); r=p.run('')
assert r.completed >= 3
""")

check("5.2 Long query", """
from src.cortex.pipeline import Pipeline
p=Pipeline(); r=p.run('x'*10000)
assert r.completed >= 3
""")

check("5.3 High transposition stress", """
from src.cortex.transposition import TranspositionLayer
tl=TranspositionLayer(base_activity=1.0)
for i in range(200):
    tl.transpose('biology','conservation',{'concept':'t'+str(i),'confidence':0.9,'type':'concept'})
assert tl.total_transpositions == 200
""")

print()
print("=" * 60)
print(f"Result: {ok}/{ok+len(fail)} passed")
if fail:
    for n, e in fail:
        print(f"  FAIL {n}: {e}")
else:
    print("All checks passed.")
print("=" * 60)
