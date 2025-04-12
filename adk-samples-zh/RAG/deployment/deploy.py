
[
    {
        // 用户查询/输入
        "query": "帮我查找女士牛仔裤，只返回搜索结果。",
        // 预期的工具使用情况
        "expected_tool_use": [
          {
            "tool_name": "search", // 预期使用的工具名称
            "tool_input": { // 预期传递给工具的输入参数
              "keywords": "women's denim jeans" // 预期的搜索关键词
            }
          }
        ],
        // 参考回答/预期最终输出（用于评估 response_match_score）
        "reference": "我找到了 xx 条关于女士牛仔裤的结果。" // xx 是一个占位符，表示结果数量
      }
]
```

**文件说明:** 这是 ADK 的工具评估数据集文件 (`tools.test.json`)。它包含一个或多个测试用例，每个用例定义了：
*   `query`: 模拟的用户输入。
*   `expected_tool_use`: 一个列表，描述了 Agent 在响应此查询时预期会调用的工具及其参数。
*   `reference`: 一个参考答案，用于评估 Agent 最终回复的质量（通常使用语义相似度）。

---

