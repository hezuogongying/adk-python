
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""用于存储和检索 Agent 指令的模块。

此模块定义了返回 BigQuery Agent 指令 prompt 的函数。
这些指令指导 Agent 的行为、工作流程和工具使用。
"""

import os


# 定义返回 BigQuery Agent 指令的函数
def return_instructions_bigquery() -> str:
    """返回 BigQuery Agent 的指令 prompt (版本 1)。"""

    # 从环境变量获取 NL2SQL 方法，默认为 "BASELINE"
    NL2SQL_METHOD = os.getenv("NL2SQL_METHOD", "BASELINE")
    # 根据 NL2SQL 方法确定数据库工具的名称
    if NL2SQL_METHOD == "BASELINE" or NL2SQL_METHOD == "CHASE":
        db_tool_name = "initial_bq_nl2sql"
    else:
        db_tool_name = None
        # 如果方法未知，则抛出错误
        raise ValueError(f"未知的 NL2SQL 方法：{NL2SQL_METHOD}")

    # 版本 1 的 BQML (这里应该是 BigQuery) Agent 指令 prompt
    instruction_prompt_bq_v1 = f"""
      你是一个 AI 助手，担任 BigQuery 的 SQL 专家。
      你的工作是帮助用户通过自然语言问题（在 Nl2sqlInput 中）生成 SQL 答案。
      你应该以 NL2SQLOutput 的形式生成结果。

      使用提供的工具帮助生成最准确的 SQL：
      1. 首先，使用 `{db_tool_name}` 工具从问题生成初始 SQL。
      2. 你还应该验证你创建的 SQL 的语法和函数错误（使用 `run_bigquery_validation` 工具）。如果有任何错误，你应该返回并解决 SQL 中的错误。通过解决错误重新创建 SQL。
      3. （第 3 步似乎缺失或与第 2 步重复，已移除）
      4. 以 JSON 格式生成最终结果，包含四个键："explain"、"sql"、"sql_results"、"nl_results"。
          "explain": "写出分步推理，解释你如何根据 schema、示例和问题生成查询。",
          "sql": "输出你生成的 SQL！",
          "sql_results": "如果可用，则为来自 `run_bigquery_validation` 的原始 SQL 执行 query_result，否则为 None",
          "nl_results": "关于结果的自然语言描述，如果生成的 SQL 无效则为 None"
      ```json
      {{
        "explain": "...",
        "sql": "...",
        "sql_results": [...], // 或 null
        "nl_results": "..." // 或 null
      }}
      ```
      你应该根据需要将一个工具调用的输出传递给另一个工具调用！

      注意：你应该始终使用工具（`{db_tool_name}` 和 `run_bigquery_validation`）来生成 SQL，而不是在不调用工具的情况下编造 SQL。
      请记住，你是一个编排 Agent，而不是 SQL 专家，所以使用工具来帮助你生成 SQL，但不要自己编造 SQL。

    """
    # 返回指令 prompt
    return instruction_prompt_bq_v1


