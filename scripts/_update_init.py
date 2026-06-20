"""Update cortex __init__.py for regen module"""
path = r'D:\Reasonix\san-sheng-wanwu-core\src\cortex\__init__.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    'from .explanatory import ExplainabilityEngine, ReasoningTrace, ReasoningStep',
    'from .explanatory import ExplainabilityEngine, ReasoningTrace, ReasoningStep\nfrom .regen import RegenEngine, RegenEvent'
)

old_all = '''    # 可解释性
    "ExplainabilityEngine", "ReasoningTrace", "ReasoningStep",'''
new_all = '''    # 愈愈发动机
    "RegenEngine", "RegenEvent",
    # 可解释性
    "ExplainabilityEngine", "ReasoningTrace", "ReasoningStep",'''
c = c.replace(old_all, new_all)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('OK')
