# MCP 接线指南 — 如何连接真实外部工具

> 硅基生命体的感受器需要 MCP 工具注入才能感知真实世界。
> 本文档说明每个感受器需要什么 MCP 工具、如何获取、如何注入。

---

## 原理

```python
# 每个感受器接受可选的 search_fn 参数
sense = ScholarSense(search_literature=my_mcp_tool)

# 无注入 = stub 模式 (使用内置知识图谱, 不联网)
sense = ScholarSense()
```

## MCP 工具清单

### 1. ScholarSense — 学术文献

| 注入参数 | 所需 MCP 服务器 | 获取方式 |
|:---------|:----------------|:---------|
| `search_literature` | article-mcp / scholarly-mcp | `npx -y scholar-mcp` |
| `fetch_details` | article-mcp | `npx -y article-mcp` |

### 2. CnkiSense — 中文知网

| 注入参数 | 所需 MCP 服务器 | 获取方式 |
|:---------|:----------------|:---------|
| `search_cnki` | cnki-mcp | 已预编译, 见 `.reasonix/mcp-servers/cnki/` |

### 3. NcbiSense — PubMed/NCBI

| 注入参数 | 所需 MCP 服务器 | 获取方式 |
|:---------|:----------------|:---------|
| `search_pubmed` | ncbi-mcp | `node ncbi-mcp.mjs` |

### 4. FishBaseSense — 鱼类性状

| 注入参数 | 所需 MCP 服务器 | 获取方式 |
|:---------|:----------------|:---------|
| `search_fishbase` | fishbase-scraper | 内置 species.db (430 种) |

### 5. WebSense — 通用网络

| 注入参数 | 所需 MCP 服务器 | 获取方式 |
|:---------|:----------------|:---------|
| `search_web` | tavily-mcp / exa-mcp | `npx -y tavily-mcp@latest` |

### 6. 学科领域感受器 (12 个)

领域感受器内置知识图谱，无需 MCP 注入即可搜索。
需要联网搜索时, 可注入 `search_fn` 连接到学科 API。

| 领域 | 外部 API 或 MCP | 备注 |
|:-----|:----------------|:------|
| math | math-mcp (GitHub: EthanHenrickson/math-mcp) | 数学计算 |
| physics | arXiv API / SPIRES | 物理文献 |
| chemistry | PubChem API | 化合物数据 |
| biology | NCBI / UniProt | 生物信息学 |
| cs | arXiv API / DBLP | 计算机文献 |
| literature | OpenLibrary API | 图书数据 |

## 自动注入

在 Reasonix 环境中, 所有 MCP 工具通过依赖注入自动连接:

```python
# 在 Reasonix 环境中运行时
from src.cortex.pipeline import Pipeline
p = Pipeline()

# 批量注入已连接的 MCP 工具
# (由 Reasonix 环境自动提供)
p.inject_mcp({
    "search_literature": mcp_search_literature,
    "search_pubmed": mcp_search_pubmed,
    "search_web": mcp_search_web,
})

result = p.run("鳤")
```

## 验证接线状态

```python
from src.senses import ScholarSense
sense = ScholarSense()
print(sense.is_wired)  # False = stub 模式

# 注入后
sense = ScholarSense(search_literature=some_fn)
print(sense.is_wired)  # True = 真实连接
```
