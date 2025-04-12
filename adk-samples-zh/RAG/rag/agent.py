
{
  "criteria": {
    // 工具轨迹平均得分的评估标准
    "tool_trajectory_avg_score": 0.09, // 允许工具使用有一定的偏差（得分大于等于 0.09）
    // 回答匹配得分的评估标准
    "response_match_score": 0.4 // 要求回答与参考答案的语义相似度得分大于等于 0.4
  }
}
```

**文件说明:** 这是 RAG Agent 评估的配置文件 (`test_config.json`)。它定义了评估通过的标准，包括对工具使用准确性 (`tool_trajectory_avg_score`) 和回答内容相关性 (`response_match_score`) 的最低要求。这里的标准比 `personalized-shopping` 的工具测试标准要宽松一些，允许一定的灵活性。

---

