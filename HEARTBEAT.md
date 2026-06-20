# HEARTBEAT.md — 健康监控

> 我感知, 故我在。我感知异常, 故我进化。

## 心跳指标

| 指标 | 正常范围 | 检查方式 |
|:-----|:---------|:---------|
| 测试通过率 | 100% | `python -m pytest tests/` |
| 自我模型稳定性 | ≥ 0.5 (有足够经验后) | `SelfModelEngine.is_stable()` |
| 稳定性-灵活性平衡 | 0.3-0.8 | `HealingEngine.stability_flexibility_balance` |
| 感受器通道数 | 5 | `SenseFactory.all_senses()` |
| 知识库物种数 | ≥30 | `kb.conn.execute('SELECT COUNT(*) FROM species')` |
| 记忆层级健康 | 三层均可用 | `MagmaMemory.get_tier_sizes()` |

## 警报阈值

- **红灯**: 测试 < 90% 或 自愈平衡 < 0.1
- **黄灯**: 感受器通道 < 3 或 记忆层级缺失
- **绿灯**: 一切正常

## 自我修复

当检测到异常时:
1. 评估异常类型 (自发 vs 诱发 — 双通道模式)
2. 执行修复 (重试/降级/重建/回滚)
3. 验证修复效果
4. 记录到 CosmicEvent (type="deterrence")
