# 三生万物 · 硅基生命体统一架构

> **SanShengWanWu Core** — 从虚拟世界伸出感知物理世界的触角。

## 架构

```
san-sheng-wanwu-core/
├── src/
│   ├── senses/       ← 感受器层 (18 个 MCP 感知通道)
│   ├── cortex/       ← 认知处理 (辩证综合+验证+涌现检测)
│   ├── memory/       ← 记忆存储 (知识库+缓存)
│   └── motor/        ← 运动输出 (报告+可视化)
├── tests/            ← 统一测试套件
├── config/           ← 系统配置
├── data/             ← 数据存储
└── scripts/          ← 工具脚本
```

## 感知-行动循环

1. **感知** — 并行激活所有感受器 (Scholar/CNKI/NCBI/FishBase/Web)
2. **理解** — 验证可信度 + 辩证综合矛盾 + 涌现检测
3. **决策** — 加权投票 + 矛盾仲裁
4. **行动** — 报告生成 + 可视化输出

## 快速开始

```bash
pip install -e .
python -m pytest tests/ -v
python -c "from src.cortex.pipeline import Pipeline; p=Pipeline(); print(p.run('鳤', 'Ochetobius elongatus').to_dict())"
```
