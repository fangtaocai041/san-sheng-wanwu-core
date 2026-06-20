# SOUL.md — 灵魂定义 (v0.1, 已弃用)

> ⚠️ **此文档已弃用。** TCSC 真圆自洽不动点已被 DSM 阻尼自我模型替代。
> 请参阅 [SELF_MODEL.md](SELF_MODEL.md) 获取最新定义。

## 迁移说明

2026-06 重构将 `soul.py` 替换为 `self_model.py`，原因：

1. **数学错误**: 原 Lipschitz 常数断言不成立 (实际约 1.425, > 1)
2. **逻辑错误**: 纯自我反射 (无输入) 不应改变表征 (反思≠遗忘)
3. **术语误导**: "灵魂"、"觉醒"、"真圆自洽"无学术来源

旧代码保留在 `src/cortex/soul.py` 作为参考，但不再用于运行时逻辑。
新的运行时逻辑在 `src/cortex/self_model.py`。

详情见 [SELF_MODEL.md](SELF_MODEL.md)。
