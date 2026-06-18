# TOOLS.md — 工具集定义

硅基生命体通过感受器 (Senses) 和 MCP 协议与外部世界交互。

## 感受器清单

| 感受器 | MCP 工具 | 感知模态 | 依赖注入名 |
|:-------|:---------|:---------|:-----------|
| ScholarSense | article-mcp / scholarly-mcp | 学术文献 | search_literature |
| CnkiSense | cnki-mcp (待装) | 中文文献 | search_cnki |
| NcbiSense | ncbi-mcp | 生物医学文献 | search_pubmed |
| FishBaseSense | FishBase HTTP API | 鱼类形态学 | search_fishbase |
| WebSense | tavily-mcp / exa-mcp | 通用网络 | search_web |

## 注入方式

```python
from src.senses import ScholarSense

# 无注入 = stub 模式 (测试用)
sense = ScholarSense()

# 有注入 = 真实 MCP 调用
sense = ScholarSense(search_literature=mcp_tool_fn)
```

## 算力预算

每次查询的默认预算:
- Token: 4096
- 时间: 30s
- 感受器通道: 5 (并行)
