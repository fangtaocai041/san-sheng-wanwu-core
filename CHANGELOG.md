# Changelog

> 版本变更记录。每个版本对应的 README 保存在 `.reasonix/readme-versions/`。

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
