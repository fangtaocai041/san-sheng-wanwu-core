# HEARTBEAT.md — 健康监控

> 我感知, 故我在。我感知异常, 故我进化。

## 心跳指标

| 指标 | 正常范围 | 检查方式 |
|:-----|:---------|:---------|
| 架构完整性 | 36/36 | `scripts/verify_architecture.py` |
| 测试通过率 | 100% | `python -m pytest tests/` |
| 感受器通道数 | 5 | `SenseFactory.all_senses()` |
| 知识库物种数 | ≥30 | `kb.conn.execute('SELECT COUNT(*) FROM species')` |

## 警报阈值

- **红灯**: 架构检查 < 30/36 或 测试 < 90%
- **黄灯**: 感受器通道 < 3 或 知识库 < 10
- **绿灯**: 一切正常

## 自我修复

当检测到异常时:
1. 记录到 CosmicEvent (type="deterrence")
2. 重试 (最多 3 次)
3. 如果仍然失败 → escalate
