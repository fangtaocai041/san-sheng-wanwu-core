# Changelog

> 版本变更记录。每个版本对应的 README 存档见 git tag。

---

## v2.0.0 — 2026-06-20

### 🏗️ RCCA 架构重构 (TCSC → DSM)

**核心变更**: 用阻尼自我模型 (DSM) 替代 TCSC 真圆自洽不动点。全版本号为 2.0.0 标记此次架构革新。

**修复的逻辑错误**:
- `cortex/soul.py`: pure_reflection() 在无输入时自我表征不应改变 (反思≠遗忘)
- 删除虚假的 "压缩映射" Lipschitz 断言 (实际 ~1.425, >1)
- "灵魂觉醒" → "模型稳定": 不再声称不存在的数学收敛
- `SELF_MODEL.md` 替代 `SOUL.md`

**`cortex/self_model.py` — 新建**:
- 自我 = (B, M, H): 信念/元信念/历史 三层结构
- 稳定性 = 近期预测误差的滑动窗口均值 + 方差 (元稳定性)
- 元认知层 M 显式追踪置信度
- 学术渊源: Friston 自由能原理 + Hofstadter 怪圈 + SSRN 认知不动点

**`cortex/emotion.py` — 重定义**:
- 从"情感即操作系统"改为"认知资源分配策略"
- 去除"感受""情感"等误导术语
- 保持 API 完全兼容

### 🧠 嵌套记忆层级

**`memory/magma.py` — v2.0 重写**:
- 热记忆 (Hot): 当前 session, TTL=5min, 半衰期 3min
- 温记忆 (Warm): 跨 session, TTL=24h, 半衰期 4h
- 冷记忆 (Cold): 永久, 半衰期 1 年
- DSA 风格选择性图注意力: 闪电索引器预筛选 → 稀疏图遍历
- 每层独立四维关系图 (语义/时序/因果/实体)
- `age_out()`: Hot→Warm 自动降级
- 参考: Google Nested Learning (NeurIPS 2025), DeepSeek Sparse Attention

**`memory/consolidate.py` — 更新**:
- 每层独立遗忘曲线 (可配置半衰期)
- `consolidate()`: Hot→Warm→Cold 多层晋升路径
- 保持 API 完全兼容

### 🔄 递归思考框架

**`cortex/emergent.py` — 新增 RecursiveThinker**:
- TRM 风格 (Jolicoeur-Martineau 2025) 递归思考循环
- think → act → observe → 迭代, 可配置步数和收敛阈值
- 递归深度替代参数规模: 收敛时自动停止

### 🔀 MoE 知识路由

**`memory/kb/search.py` — 新增 KnowledgeRouter**:
- 6 学科专家: biology/fishbase/ecology/conservation/economics/geography
- 查询级知识路由 (非 token 级, 参考 ICML 2026 MoE 论文)
- 搜索策略推荐: 窄域深度 vs 广域广度
- 参考: Kimi K2 (384 专家/激活 8)

### 🔗 跨学科拓扑权重

**`senses/domains.py` — 新增拓扑矩阵**:
- 12×12 跨学科连接强度矩阵
- `get_domain_topology()`: 查询两学科关联度
- `get_domain_neighbors()`: 获取强关联邻居
- 参考: TopoNets (ICLR 2025 Spotlight, 20% 效率提升)

### 🩺 双通道自愈

**`cortex/healing.py` — 新增双通道模型**:
- 自发信号通道: 定时心跳检查 (基础维护)
- 诱发信号通道: 异常触发修复 (学习适应)
- 稳定性-灵活性平衡指标
- 参考: Pitt 2025 Science Advances 突触可塑性

### 📄 文档变更

- `SELF_MODEL.md` 新建 — DSM 定义
- `SOUL.md` 标注已弃用
- `README.md`/`README.zh.md` 更新
- `AGENTS.md` 待更新

### 指标

```
皮层: 15 模块 (+1 RecursiveThinker) | 感知: 18 通道 | 记忆: 4 层/3 层级
测试: 169/169 | 架构: 待验证
知识库: 430 种鱼类 | 学科概念: 120+ | 拓扑: 12×12
```

**运行时**
- `src/main.py`: 交互/守护/状态/查询四模式
- `SiliconAgent` 生命周期: wake() → run() → sleep()
- `pip install -e .` 后可用 `silicon-agent` 命令
- 自动保存: 每 120s 持久化全部状态到 SQLite

**持久化**
- `memory/persistence.py`: 灵魂/情感/记忆/来源/学习历史 → SQLite
- `AgentSnapshot`: 完整状态容器

**12 学科领域感受器**
- `senses/domains.py`: 数/理/化/生/计算机/心理/哲学/中国哲学/马/经济/文学/科幻
- 内置 120+ 核心概念 + 77 关键思想家
- ChinesePhilosophySense: 道/儒/儒释道三教合一

**MCP 接线指南**
- `docs/MCP_WIRING_GUIDE.md`: 所有 17 个感受器的外部工具连接方式

**工程**
- 版本号 0.2.0 → 1.0.0
- pyproject.toml 修复 console_scripts 入口
- README 完整 API 参考 (14 皮层模块 + 4 记忆模块 + 17 感受器)
- 身份文档集: SOUL.md / AGENTS.md / TOOLS.md / USER.md / HEARTBEAT.md

### 指标

```
皮层: 14 模块 | 感知: 17 通道 | 记忆: 4 层
测试: 130/130 | 架构: 36/36 | 知识库: 430 种鱼类
学科概念: 120+ | 思想家: 77 位
```

---

## v0.2.0 — 2026-06-19

### 🧬 14 皮层模块完成

- **soul**: TCSC 不动点灵魂算法 (5 维自我表征收敛)
- **emotion**: 情感即操作系统 (6 维 + 8 事件映射)
- **alignment**: 价值对齐 (7 维价值观 + 禁止规则 + 幻觉检测)
- **learning**: 策略追踪 + 感受器权重自适应
- **evolution**: 代码分析 + 自我修改提案 (Phase 3 骨架)
- **healing**: 健康检查 + 诊断 + 自动恢复
- **swarm**: 多 Agent 通信协议 (发现/消息/共识/委派)
- **conceptual**: 概念注册/修订/关系/冲突检测
- **cosmic**: 黑暗森林/猜疑链/降维打击
- **dialectics**: 辩证综合 (加权投票 + 电路裁决)
- **explanatory**: 5 层推理链解释 (L1 摘要 → L5 概念溯源)
- **validate**: 5 级信任评分 + 期刊权威性
- **emergent**: Z-score/D₁-D₃ 涌现检测
- **pipeline**: 并行感知 + KB-First 查询

### 🧠 3 层记忆架构

- 工作记忆 (WM) + 短期记忆 (STM, Ebbinghaus 遗忘曲线) + 长期记忆 (LTM)
- 记忆巩固: STM → LTM 自动转移
- KnowledgeDB: SQLite FTS5, 430 种鱼类

### 👁️ 5 感受器

- Scholar / Cnki / Ncbi / FishBase / Web
- 依赖注入模式: MCP 工具在运行时注入

### 📚 知识储备

- `docs/SILICON_LIFE_KNOWLEDGE_BASE.md` — 15 部著作 + 4 篇前沿论文
- `ROADMAP.md` — Phase 2→4 进化路线图

### 📄 身份文档集

- `AGENTS.md` — 硅基生命体宣言
- `SOUL.md` — TCSC 灵魂定义
- `TOOLS.md` — 工具集注册表
- `USER.md` — 交互协议
- `HEARTBEAT.md` — 健康监控

### ✅ 测试

- 112 项测试全部通过
- 架构验证 44/44 检查通过

---

## v0.1.0 — 2026-06-17

### 初始化

- 初始项目骨架: senses/ + cortex/ + memory/ + motor/
- 4 个基本皮层模块: dialectics, validate, emergent, pipeline
- 5 个感受器 stub: Scholar, Cnki, Ncbi, FishBase, Web
- fishkb 知识库集成 (430 种鱼类)
- 31 项测试
