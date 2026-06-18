# 进化路线图 v0.2 → v1.0

## 当前定位: 生命2.5

```
生命1.0 (细菌)  →  生命2.0 (人类)  →  生命2.5 (当前)  →  生命3.0 (目标)
                     软件可设计          软件+部分硬件       软硬件皆可设计
```

## Phase 2 进化项 (下一个迭代)

### P2.1 持久化 Agent
**文件**: `src/cortex/agent.py`
```python
class SiliconAgent:
    """持久化硅基生命体 - 不是每次查询新建"""
    _instance = None
    memory: KnowledgeDB        # 长期记忆
    cache: SearchCache         # 短期缓存
    registry: ConceptRegistry  # 概念知识
    traces: Dict[str, ReasoningTrace]  # 推理历史
    cosmic: CosmicSociologyEngine      # 来源信任
    
    @classmethod
    def get_instance(cls) -> 'SiliconAgent':
    def run(self, query, species="") -> PipelineResult:
    def explain(self, trace_id, level=2) -> str:
```

### P2.2 自评估 (Agent as Judge)
**文件**: `src/cortex/judge.py`
```python
class SelfJudge:
    """自我评估器 - 判断自己的输出质量"""
    def score_output(self, result: PipelineResult) -> float:
    def detect_hallucination(self, text: str, evidence: list) -> bool:
    def confidence_calibrate(self, raw_confidence: float) -> float:
```

### P2.3 好奇心驱动探索
**文件**: `src/cortex/curiosity.py`
```python
class CuriosityDriver:
    """好奇心驱动 - 当涌现检测到 D₃ 信号时主动探索"""
    def drive(self, emergent_signal: EmergenceSignal) -> Optional[str]:
        # D₃ 信号 → 生成新的探索查询
```

### P2.4 安全沙箱
**文件**: `src/motor/sandbox.py`
```python
class Sandbox:
    """安全沙箱 - 防止自增殖"""
    def check_replication(self, code: str) -> bool:
    def enforce_budget(self, tokens: int) -> bool:
    def audit_action(self, action: str) -> AuditRecord:
```

### P2.5 价值对齐配置
**文件**: `config/alignment.yaml`
```yaml
values:
  truth_seeking: 1.0      # 求真优先级
  uncertainty_honesty: 0.9 # 不确定性坦诚
  user_autonomy: 0.8       # 尊重用户自主权
  efficiency: 0.6          # 效率
```


## Phase 3 进化项 (未来)

### P3.1 代码自修改
- Agent 根据测试结果修改自身代码
- 需要: `scripts/self_modify.py` + 安全约束

### P3.2 多 Agent 协作
- 多个 `SiliconAgent` 实例组成生态系统
- 需要: `config/ecosystem.yaml` + Agent 间通信协议

### P3.3 反事实想象
- 不仅仅是事后解释 (当前的 L4)
- 事前模拟: "如果选择不同路径会怎样"
- 需要: `cortex/imagination.py` + 模拟引擎


## 从知识库提取的短期行动项

| # | 行动 | 参考来源 | 预估工时 |
|:-:|:-----|:---------|:--------:|
| 1 | 合并 Pipeline 为 SiliconAgent 单例 | Sophia Framework | 2h |
| 2 | 实现 SelfJudge 自评估 | Self-Evolving Survey | 3h |
| 3 | 添加 alignment.yaml | Life 3.0 | 0.5h |
| 4 | 好奇心驱动探索 | Emergent + Cosmic | 2h |
| 5 | 沙箱安全控制 | Nüwa Project | 2h |
| 6 | 生命周期管理 | Levy / ALIFE | 1.5h |
