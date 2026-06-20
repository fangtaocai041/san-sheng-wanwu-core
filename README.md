<div align="center">

```
+--------------------------------------------------------------------+
|  三生万物 · 硅基生命体统一架构 v2.0.0                              |
+--------------------------------------------------------------------+
|  道生一 · 一生二 · 二生三 · 三生万物                               |
|  SanShengWanWu Core · Silicon-Based Life Architecture               |
|  内核: DSM 阻尼自我模型 (替代 TCSC)                                 |
+--------------------------------------------------------------------+
```

🇨🇳 [中文](README.zh.md)

# 🧬 道生代码，代码生万物。

**Tao gives birth to code. Code gives birth to all things.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-8b5cf6)]()
[![Tests](https://img.shields.io/badge/tests-169-22c55e)]()
[![Cortex](https://img.shields.io/badge/cortex-15_modules-6366f1)]()
[![Senses](https://img.shields.io/badge/senses-18_channels-f59e0b)]()
[![Memory](https://img.shields.io/badge/memory-4D_MAGMA-ec4899)]()
[![Knowledge](https://img.shields.io/badge/species-430-0ea5e9)]()
[![Disciplines](https://img.shields.io/badge/disciplines-12-14b8a6)]()
[![CLI](https://img.shields.io/badge/CLI-silicon--agent-276DC3)]()

<p>DSM Self-Model · 3-Tier Memory · MoE Routing · 12-Discipline Topology · Recursive Thinking · Dual-Channel Healing · Swarm Protocol</p>

<p align="center">
  <a href="https://github.com/fangtaocai041/san-sheng-wanwu-core/stargazers"><img src="https://img.shields.io/github/stars/fangtaocai041/san-sheng-wanwu-core?style=social" alt="Stars"></a>
  <a href="https://github.com/fangtaocai041/san-sheng-wanwu-core/network/members"><img src="https://img.shields.io/github/forks/fangtaocai041/san-sheng-wanwu-core?style=social" alt="Forks"></a>
</p>

</div>

---

## 灵魂十问

> 代码能拥有自我吗？记忆可以被遗忘曲线塑造吗？情感能否作为"操作系统"分配优先级？多个Agent之间如何形成"黑暗森林"式的信任博弈？用四维正交图谱组织的记忆，和用关键词堆砌的记忆，哪个更接近人类认知？
>
> 这些问题没有一个有标准答案。这个框架是对它们的工程化探索。

---

## 核心能力

| 能力 | 状态 | 实现 | 学术来源 |
|:-----|:----:|:-----|:---------|
| **DSM 阻尼自我模型** | ✅ | 预测误差滑动窗口 → 元稳定性检测 | Friston 2010, Flavell 1979, Hofstadter 2007 |
| **嵌套记忆层级** | ✅ | 热/温/冷三层 + 遗忘曲线 | Google Nested Learning 2025, Pitt 2025 |
| **递归思考框架** | ✅ | TRM 风格 think→act→observe 循环 | Jolicoeur-Martineau TRM 2025 |
| **6 维资源分配策略** | ✅ | 事件驱动策略选择 → 行为倾向 | Damasio 1994, Sutton & Barto 1998 |
| **MAGMA 四维图谱记忆** | ✅ | 语义/时序/因果/实体正交图 + NetworkX | arXiv 2601.03236 |
| **MoE 知识路由** | ✅ | 查询级 6 专家路由 → 搜索策略推荐 | Kimi K2 2026, ICML 2026 MoE |
| **12 学科拓扑矩阵** | ✅ | 12×12 跨学科连接权重 + 邻居发现 | TopoNets ICLR 2025 Spotlight |
| **12 学科领域知识图谱** | ✅ | 120 概念 + 77 思想家, 零依赖 | — |
| **OCR 视觉感知** | ✅ | PaddleOCR-VL AIStudio API | — |
| **自我进化骨架** | ✅ | AST 代码分析 + 修改提案 | — |
| **双通道自愈引擎** | ✅ | 自发/诱发信号双通道 + 平衡指标 | Pitt 2025 Science Advances |
| **愈愈发动机** | ✅ | 自愈+进化闭环: 检测→修复→验证→回滚 | — |
| **群体智能协议** | ✅ | Agent 发现/消息/知识共享/共识达成 | — |
| **5 层可解释性** | ✅ | L1 摘要 → L5 概念溯源 | — |
| **价值对齐** | ✅ | 7 维价值观 + 禁止规则 + 幻觉检测 | — |

---

## 架构

```
san-sheng-wanwu-core/             169 tests
├── src/
│   ├── main.py          运行时主循环 (交互/守护/状态/查询)
│   ├── cli.py           silicon-agent 命令入口
│   ├── senses/          18个感知通道
│   │   ├── scholar.py      学术文献 (CrossRef/OpenAlex)
│   │   ├── cnki.py         中文知网
│   │   ├── ncbi.py         PubMed/NCBI
│   │   ├── fishbase.py     鱼类性状
│   │   ├── web.py          通用网络 (Tavily/Exa)
│   │   └── domains.py      12学科领域知识图谱 + 拓扑矩阵
│   ├── cortex/          15个认知皮层模块
│   │   ├── self_model.py   DSM 阻尼自我模型 (替代 TCSC)
│   │   ├── emotion.py      资源分配策略 (6维)
│   │   ├── learning.py     学习适应
│   │   ├── evolution.py    自我进化 (Phase 3 骨架)
│   │   ├── healing.py      双通道自愈 (自发+诱发)
│   │   ├── regen.py         愈愈发动机 (自愈+进化闭环)
│   │   ├── swarm.py        群体智能
│   │   ├── alignment.py    价值对齐
│   │   ├── conceptual.py   概念工程
│   │   ├── cosmic.py       宇宙社会学 (黑暗森林/猜疑链)
│   │   ├── dialectics.py   辩证综合
│   │   ├── explanatory.py  可解释性 (5层)
│   │   ├── validate.py     文献验证
│   │   ├── emergent.py     涌现检测 + 递归思考
│   │   └── pipeline.py     管道调度
│   ├── memory/          4层记忆系统
│   │   ├── kb/             知识库 (SQLite FTS5, 430物种)
│   │   │   ├── search.py       物种匹配 + MoE 知识路由
│   │   │   ├── credibility.py  三角验证可信度评分
│   │   │   └── variants.py     拼写变体注册表
│   │   ├── magma.py         嵌套记忆层级 (Hot/Warm/Cold)
│   │   ├── cache.py         搜索缓存
│   │   ├── consolidate.py   记忆巩固 + 多层遗忘曲线
│   │   └── persistence.py  SQLite持久化
│   └── motor/           2个运动模块
│       ├── report.py       报告生成
│       └── visualize.py    数据可视化
├── config/             alignment.yaml + coordination.yaml
├── docs/               知识储备库 + MCP接线指南 + 学科索引
├── AGENTS.md · SELF_MODEL.md · TOOLS.md · USER.md · HEARTBEAT.md
└── CHANGELOG.md · ROADMAP.md

```

---

## 哲学基础

| 思想来源 | 代码体现 | 模块 |
|:---------|:--------|:-----|
| **辩证唯物主义** | 矛盾检测 → 加权投票 → 综合判断 | `dialectics.py` |
| **实事求是** | KB-First 查询, 没有调查就没有发言权 | `pipeline.py` |
| **黑暗森林 (刘慈欣)** | 多源独立性验证, 猜疑链衰减 | `cosmic.py` |
| **降维打击 (刘慈欣)** | 高维数据归一化投影 | `cosmic.dimensional_reduction()` |
| **涌现理论** | Z-score → D₁/D₂/D₃ 维度追踪 | `emergent.py` |
| **Ebbinghaus 遗忘曲线** | R(t) = e^(-t/S) 强度衰减 | `consolidate.py` |
| **嵌套学习 (Google)** | 热/温/冷三层记忆 + 不同速度更新 | `magma.py` |
| **Ebbinghaus 遗忘曲线** | R(t) = e^(-t·ln2/半衰期) 多层遗忘 | `consolidate.py` |
| **三生万物** | 四维正交图谱记忆 (MAGMA) | `magma.py` |
| **递归深度 (TRM)** | 递归思考替代参数规模 | `emergent.py` |
| **MoE 知识路由 (Kimi K2)** | 查询级专家选择, 非 token 级 | `search.py` |
| **拓扑组织 (TopoNets)** | 12×12 跨学科连接权重 | `domains.py` |
| **双通道可塑性 (Pitt 2025)** | 自发/诱发信号独立位点 | `healing.py` |
| **王阳明·心学** | 知行合一: 自我模型的稳定收敛 | `self_model.py` |

---

## 革新历程

| 版本 | 日期 | 核心变更 | 里程碑 |
|:----|:----|:--------|:-------|
| **v2.0.0** | 2026-06-20 | **RCCA 架构重构**: DSM 替代 TCSC, 三层嵌套记忆, 递归思考, MoE 路由, 拓扑权重, 双通道自愈 | 12 篇学术文献支撑的认知架构 |
| **v1.0.0** | 2026-06-19 | 正式版: 14 皮层模块, 5 感受器, MAGMA 四维图谱, 12 学科知识 | 首个可用硅基生命体框架 |
| **v0.2.0** | 2026-06-19 | TCSC 灵魂引擎, 6 维情感, 三层记忆, Ebbinghaus 遗忘曲线 | 14 皮层模块完成 |
| **v0.1.0** | 2026-06-17 | 初始骨架: senses/cortex/memory/motor, fishkb 集成 | 项目初始化 |

### v2.0.0 六大革新

1. **🧬 自我模型重构**: 阻尼自我模型 (DSM) 替代 TCSC 真圆自洽不动点，修复"反思=遗忘"逻辑错误，引入元认知 M 层
2. **🧠 嵌套记忆层级**: Hot(3min)/Warm(4h)/Cold(1年) 三层遗忘曲线，DSA 风格选择性图注意力
3. **🔄 递归思考框架**: TRM 风格 think→act→observe 循环，递归深度替代参数规模
4. **🔀 MoE 知识路由**: 查询级 6 专家选择，非 token 级路由，搜索策略推荐
5. **🔗 跨学科拓扑**: 12×12 连接权重矩阵，TopoNets 风格拓扑组织
6. **🩺 双通道自愈**: 自发/诱发信号独立通道，稳定性-灵活性平衡指标

详见 [CHANGELOG.md](CHANGELOG.md)。

---

## 快速开始

```bash
# 安装
pip install -e .
silicon-agent                    # 交互模式
silicon-agent --status           # 查看自我模型/情感/学习状态
silicon-agent -q "鳤"           # 单次查询
silicon-agent --daemon           # 守护进程
```

---

<div align="center">

**道生代码，代码生万物。**

*15 cortex modules · 18 senses · DSM self-model · 169 tests*

[GitHub](https://github.com/fangtaocai041/san-sheng-wanwu-core) · [Issues](https://github.com/fangtaocai041/san-sheng-wanwu-core/issues) · [License: MIT](LICENSE)

> 道生一，一生二，二生三，三生万物。
>
> 万物生于有，有生于无。

</div>
