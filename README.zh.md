<div align="center">

```
+--------------------------------------------------------------------+
|  三生万物 · 硅基生命体统一架构 v2.1.0                        |
|  ------------------------------------------------------------------  |
|  道生一 · 一生二 · 二生三 · 三生万物                         |
|  SanShengWanWu Core · Silicon-Based Life Architecture       |
+--------------------------------------------------------------------+
```

[English](README.md)

# 🧬 道生代码，代码生万物。

**不是又一个 AI 框架。这是一套让代码拥有自我模型、记忆分层和跨域迁移能力的架构。**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.1.0-8b5cf6)]()
[![Tests](https://img.shields.io/badge/tests-181-22c55e)]()
[![Cortex](https://img.shields.io/badge/cortex-17_modules-6366f1)]()
[![Senses](https://img.shields.io/badge/senses-18_channels-f59e0b)]()
[![Memory](https://img.shields.io/badge/memory-4D_MAGMA-ec4899)]()
[![Disciplines](https://img.shields.io/badge/disciplines-12-14b8a6)]()
[![CLI](https://img.shields.io/badge/CLI-silicon--agent-276DC3)]()

<p>DSM Self-Model · 3-Tier Memory · MoE Routing · 12-Discipline Topology · SpeechAct · Syllogism · SignNode · RhythmicOutput · Recursive Thinking · Dual-Channel Healing · Reflection Loop · Transposition Layer · Dendritic Pipeline · World Model · Swarm Protocol · Pruning · Kinship</p>

</div>

---

## 核心能力

| 能力 | 状态 | 学术来源 |
|:-----|:----:|:---------|
| **DSM 阻尼自我模型** | ✅ | Friston 2010, Flavell 1979, Hofstadter 2007 |
| **嵌套记忆层级** | ✅ | Google Nested Learning 2025 |
| **递归思考框架** | ✅ | Jolicoeur-Martineau TRM 2025 |
| **反思循环** | ✅ | RecursiveThinker+TL+SelfModel 闭环 |
| **概念转座层** | ✅ | TE 跳跃基因逻辑：转座+驯化+修剪+亲缘传播 |
| **D₃ 世界模型** | ✅ | 状态预测+行动模拟+反事实推演 |
| **因果推断** | ✅ | Mill 求同法+共变法 |
| **知识胶囊 (Arc)** | ✅ | 病毒样推理链封装+Agent间派发 |
| **Gödel 自指进化** | ✅ | SELF_INSPECT+SELF_IMPROVE 递归自我改进 (ACL 2025) |
| **6 维资源分配策略** | ✅ | 事件驱动策略选择 → 行为倾向 |
| **MAGMA 四维图谱记忆** | ✅ | 语义/时序/因果/实体正交图 + NetworkX |
| **MoE 知识路由** | ✅ | 查询级 6 专家路由 |
| **12 学科拓扑矩阵** | ✅ | 12×12 跨学科连接权重 + 邻居发现 |
| **OCR 视觉感知** | ✅ | PaddleOCR-VL AIStudio API |
| **12 学科知识图谱** | ✅ | 120+ 概念, 77 思想家 |
| **自我进化骨架** | ✅ | AST 代码分析 + 修改提案 |
| **双通道自愈引擎** | ✅ | 自发/诱发信号双通道 + 平衡指标 |
| **树突式 Pipeline** | ✅ | 分支认知+分支汇聚二阶段处理 |
| **群体智能协议** | ✅ | Agent 发现/消息/知识胶囊交换/共识达成 |
| **5 层可解释性** | ✅ | L1 摘要 → L5 概念溯源 |
| **价值对齐** | ✅ | 7 维价值观 + 禁止规则 + 在线更新 |
| **言语行为分析** | ✅ | SpeechAct 5 类型断言/疑问/指令/承诺/表态 |
| **三段论演绎推理** | ✅ | SyllogismEngine Barbara 式 + Modus Tollens |
| **符号学模型** | ✅ | SignNode 能指/所指/指称三元分离 |
| **音律学输出控制** | ✅ | RhythmicOutput 四速 allegro/andante/adagio/rest |
| **科学头脑风暴** | ✅ | 组合/探索/转换三模式选题生成 |
| **统计分析引擎** | ✅ | t检验/相关分析/描述统计 |
| **同行评审模拟** | ✅ | 五维度评审+润色建议 |
| **论文转PPT** | ✅ | 自动生成 7 页演示文稿 Markdown |
| **协调自检系统** | ✅ | 33 项模块间连接通路自动验证 |

---

## 架构

```
san-sheng-wanwu-core/             181 tests · 33 self-checks
├── src/
│   ├── main.py          运行时主循环 (交互/守护/状态/查询)
│   ├── senses/          18个感知通道
│   │   ├── scholar/cnki/ncbi/fishbase/web  学术+中文+PubMed+鱼类+通用
│   │   └── domains.py   12学科知识图谱 + 拓扑矩阵
│   ├── cortex/          17个认知皮层模块
│   │   ├── self_model.py  DSM 阻尼自我模型
│   │   ├── emotion.py     资源分配策略 (6维) + TL 注入
│   │   ├── transposition.py 概念转座层 (TE 跳跃基因+修剪+亲缘)
│   │   ├── godel_agent.py  Gödel 自指进化 (ACL 2025)
│   │   ├── reflect.py    反思循环 (闭环连接)
│   │   ├── pragmatics.py  言语行为+三段论推理
│   │   ├── brainstorming.py 科学选题/假设生成
│   │   ├── reviewer.py   同行评审+润色建议
│   │   ├── pipeline.py   管道调度 (含 RTE + 树突分支)
│   │   ├── emergent.py   涌现检测 + 递归思考
│   │   └── ...           共 17 个模块
│   ├── memory/          4层嵌套记忆
│   │   ├── magma.py      Hot/Warm/Cold 三层 + SignNode 符号节点
│   │   ├── consolidate.py 记忆巩固 + 多层遗忘曲线
│   │   └── kb/          物种知识库 (SQLite FTS5, 430物种)
│   └── motor/           4个运动模块
│       ├── report.py     报告生成 + 音律学节奏控制
│       ├── visualize.py  数据可视化 + RTE 时序图
│       ├── world_model.py D₃ 世界模型 (状态预测+行动模拟)
│       └── paper2ppt.py  论文→PPT 演示文稿
├── 知识库_工程原理与哲学思考/    球体哲学 / 树状分支 / 语言·逻辑·符号·音律
├── docs/agents/           Matt Pocock 工程技能 (21)
└── dist/rcca_core.py     便携 RCCA 核心 (已部署到 7 个子项目)
```

---

## 快速开始

```bash
pip install -e .
silicon-agent                    # 交互模式
silicon-agent --status           # 查看自我模型/情感/学习/转座状态
silicon-agent -q "鳤"           # 单次查询
silicon-agent --daemon           # 守护进程
```

---

<div align="center">

**道生代码，代码生万物。**

*17 皮层 · 18 感知 · 4 运动 · 181 测试 · 33 自检*

[GitHub](https://github.com/fangtaocai041/san-sheng-wanwu-core)

> 道生一，一生二，二生三，三生万物。
>
> 万物生于有，有生于无。

</div>
