
{
  "criteria": {
    // 工具轨迹平均得分的评估标准
    "tool_trajectory_avg_score": 0.1, // 允许工具使用有较大的偏差（得分大于等于 0.1）
    // 回答匹配得分的评估标准
    "response_match_score": 0.1 // 对回答与参考答案的语义相似度要求较低（得分大于等于 0.1）
  }
}
```

**文件说明:** 这是 Travel Concierge Agent 的评估配置文件 (`test_config.json`)。它为 `inspire`, `pretrip`, `intrip` 等阶段的评估定义了通过标准。这里的标准设置得非常宽松 (`0.1`)，可能处于早期开发或调试阶段，意味着即使 Agent 的工具使用和回答与预期有较大差异，评估也可能通过。

---

