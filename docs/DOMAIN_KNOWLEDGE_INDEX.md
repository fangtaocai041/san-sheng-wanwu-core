# 学科知识库索引

> 硅基生命体的学科感知储备。每个领域对应 `src/senses/domains.py` 中的一个 `*Sense` 类。

---

## 领域清单 (12 个)

| # | 领域 | 类名 | 核心概念数 | 思想家数 |
|:-:|:-----|:-----|:---------:|:--------:|
| 1 | 数学 | `MathSense` | 10 | 8 |
| 2 | 物理 | `PhysicsSense` | 10 | 8 |
| 3 | 化学 | `ChemistrySense` | 6 | 4 |
| 4 | 生物学 | `BiologySense` | 10 | 5 |
| 5 | 计算机科学 | `ComputerScienceSense` | 12 | 8 |
| 6 | 心理学 | `PsychologySense` | 7 | 5 |
| 7 | 哲学 | `PhilosophySense` | 10 | 10 |
| 8 | **中国哲学** | `ChinesePhilosophySense` | **22** | **8** |
| 9 | 马克思主义 | `MarxismSense` | 10 | 6 |
| 10 | 经济学 | `EconomicsSense` | 8 | 8 |
| 11 | 文学 | `LiteratureSense` | 7 | 7 |
| 12 | 科幻 | `SciFiSense` | 8 | 10 |
| | **合计** | **12 类** | **120** | **77** |

## 中国哲学领域详情

### 道家核心概念
- **道** — 宇宙万物的本源和运行规律
- **无为** — 顺应自然规律而不妄为
- **阴阳** — 宇宙中对立统一的两大基本力量
- **五行** — 金木水火土相生相克
- **气** — 构成宇宙万物的基本能量
- **自然** — 道的本质特征: 自己如此, 自然而然

### 儒家核心概念
- **仁** — 核心德性: 爱人、推己及人
- **礼** — 社会秩序和行为规范
- **中庸** — 不偏不倚、调和折中的处世哲学
- **天命** — 儒家伦理的形上基础
- **修身齐家治国平天下** — 儒家八条目
- **四书五经** — 核心经典体系

### 儒释道三教合一
- **禅宗** — 佛教中国化, 直指人心见性成佛
- **理学** — 程朱理学/陆王心学
- **心学** — 心即理、致良知、知行合一
- **周易** — 群经之首

### 关键思想家
老子(道)、孔子(儒)、庄子(道)、孟子(儒)、慧能(禅)、朱熹(理)、王阳明(心)、苏轼(三教融合)

## 外部 MCP 服务器

| 领域 | 可用 MCP 服务器 | GitHub | 集成状态 |
|:-----|:----------------|:-------|:---------|
| 数学 | math-mcp | EthanHenrickson/math-mcp | 待注入 |
| 通用 | wolfram-alpha | 社区 | 待调研 |

## 使用方式

```python
from src.senses import ChinesePhilosophySense, create_domain

# 直接使用
sense = ChinesePhilosophySense()
result = sense.search("知行合一")
print(result["concepts_found"])  # → [心学, 知行合一]

# 按名称创建
sense = create_domain("chinese_philosophy")

# 注入 MCP 工具
sense = ChinesePhilosophySense(search_fn=my_mcp_search)
```
