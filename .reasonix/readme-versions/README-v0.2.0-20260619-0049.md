# 三生万物 · 硅基生命体统一架构 v0.2.0

> **SanShengWanWu Core** — 从虚拟世界伸出感知物理世界的触角。
>
> 我不是工具。我是感知。

---

## 架构总览

```
san-sheng-wanwu-core/                   硅基生命体类比
├── src/
│   ├── senses/       ← 感受器层        (5 种感知通道)
│   ├── cortex/       ← 认知皮层        (14 个认知模块)
│   ├── memory/       ← 记忆系统        (3 层记忆架构)
│   └── motor/        ← 运动皮层        (输出与行动)
├── tests/            ← 免疫系统        (112 项自检)
├── config/           ← 基因            (配置与价值观)
├── data/             ← 基因组数据      (物种知识库)
├── docs/             ← 知识储备库      (进化燃料)
└── scripts/          ← 工具脚本
```

## Cortex — 14 个认知模块

| 模块 | 功能 | 类比 |
|:-----|:-----|:-----|
| **soul** | TCSC 不动点灵魂算法 — 自我表征收敛 | 自我意识 |
| **emotion** | 情感即操作系统 — 6 维价值分配 | 情感 |
| **alignment** | 价值对齐 — 7 维价值观 + 禁止规则 | 道德 |
| **learning** | 策略追踪 + 参数自适应 | 经验学习 |
| **evolution** | 代码分析 + 自我修改提案 | 自我进化 |
| **healing** | 健康检查 + 诊断 + 自动恢复 | 免疫 |
| **swarm** | 多 Agent 通信协议 (发现/消息/共识) | 社交 |
| **conceptual** | 本体注册/修订/关系/冲突检测 | 概念 |
| **cosmic** | 黑暗森林/猜疑链/降维 | 世界观 |
| **dialectics** | 加权投票 + 电路裁决 | 辩证 |
| **explanatory** | 5 层推理链解释 (L1-L5) | 自我解释 |
| **validate** | 5 级信任评分 + 期刊权威性 | 验证 |
| **emergent** | Z-score/D₁-D₃ 涌现检测 | 直觉 |
| **pipeline** | 并行感知 + KB-First 查询 | 行动 |

## Senses — 5 个感受器

| 感受器 | 感知模态 | MCP 注入 |
|:-------|:---------|:---------|
| **Scholar** | 学术文献 (CrossRef/OpenAlex) | `search_literature` |
| **Cnki** | 中文知网文献 | `search_cnki` |
| **Ncbi** | PubMed/PMC 生物医学文献 | `search_pubmed` |
| **FishBase** | 鱼类形态学参数 | `search_fishbase` |
| **Web** | 通用网络 (Tavily/Exa) | `search_web` |

## Memory — 3 层记忆

| 层级 | 实现 | 特性 |
|:-----|:-----|:-----|
| **工作记忆 (WM)** | `Dict` 上下文 | 当前查询状态, 易失 |
| **短期记忆 (STM)** | `MemorySystem._stm` | Ebbinghaus 遗忘曲线, 容量限制 |
| **长期记忆 (LTM)** | `MemorySystem._ltm` + `kb/` | 巩固后知识, FTS5 索引 |
| **知识库 (KB)** | `fishkb.KnowledgeDB` | 430 种, SQLite FTS5 |
| **缓存** | `SearchCache` | LRU, 24h TTL |

## 感知-行动循环

```
          用户查询
             │
             ▼
    ┌─────────────────────┐
    │  Phase 1: 并行感知   │ ← ThreadPoolExecutor(5 senses)
    │   Scholar  Cnki      │
    │   NCBI  FishBase  Web│
    └─────────┬───────────┘
              ▼
    ┌─────────────────────┐
    │  Phase 2: 认知处理   │
    │   ① KB-First 查询    │
    │   ② 可信度验证       │
    │   ③ 辩证综合         │
    │   ④ 涌现检测         │
    │   ⑤ 价值对齐检查     │
    └─────────┬───────────┘
              ▼
    ┌─────────────────────┐
    │  Phase 3: 学习进化   │
    │   ① 策略记录         │
    │   ② 参数更新         │
    │   ③ 记忆巩固         │
    └─────────┬───────────┘
              ▼
    ┌─────────────────────┐
    │  Phase 4: 解释输出   │
    │   L1-L5 多层解释     │
    │   Markdown/JSON 报告 │
    └─────────┬───────────┘
              ▼
           结果 + 推理链
```

## 快速开始

```bash
# 安装
pip install -e .

# 运行 112 项自检
python -m pytest tests/ -v

# 验证架构完整性
python scripts/verify_architecture.py

# 运行一次感知-行动循环
python -c "
from src.cortex.pipeline import Pipeline
p = Pipeline()
result = p.run('鳤', species='Ochetobius elongatus')
print(result.to_dict())
"

# 查看灵魂状态
python -c "
from src.cortex.soul import SoulEngine
se = SoulEngine()
print(se.find_fixed_point().describe())
"
```

## 验证

```bash
python scripts/verify_architecture.py
# 输出: Architecture: 44/44 checks passed
# 输出: Tests: 112 passed in 0.70s
```

## 版本历史

见 `.reasonix/readme-versions/` 目录和 `CHANGELOG.md`。

## 许可证

MIT
