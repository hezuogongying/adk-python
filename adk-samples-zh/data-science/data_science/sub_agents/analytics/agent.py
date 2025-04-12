
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

"""数据科学多 Agent 的顶层 Agent 的工具。

-- 使用 NL2SQL 从数据库（例如 BigQuery）获取数据
-- 然后，根据需要使用 NL2Py 进行进一步的数据分析
"""

# 导入 ADK 工具上下文和 Agent 工具
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

# 从子 Agent 模块导入数据科学 Agent 和数据库 Agent
from .sub_agents import ds_agent, db_agent


# 定义异步工具函数：调用数据库 Agent
async def call_db_agent(
    question: str,               # 用户提出的问题
    tool_context: ToolContext,   # ADK 工具上下文
):
    """调用数据库 (nl2sql) Agent 的工具。"""
    # 打印当前使用的数据库类型
    print(
        "\n call_db_agent.use_database:"
        f' {tool_context.state["all_db_settings"]["use_database"]}'
    )

    # 创建 AgentTool 实例，包装数据库 Agent (db_agent)
    agent_tool = AgentTool(agent=db_agent)

    # 异步运行数据库 Agent 工具，传入问题和工具上下文
    db_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    # 将数据库 Agent 的输出存储在工具上下文的状态中
    tool_context.state["db_agent_output"] = db_agent_output
    # 返回数据库 Agent 的输出
    return db_agent_output


# 定义异步工具函数：调用数据科学 Agent
async def call_ds_agent(
    question: str,               # 用户提出的问题
    tool_context: ToolContext,   # ADK 工具上下文
):
    """调用数据科学 (nl2py) Agent 的工具。"""

    # 如果问题是 "N/A"，表示不需要进行数据科学分析，直接返回数据库 Agent 的输出
    if question == "N/A":
        return tool_context.state.get("db_agent_output", "没有可用的数据库输出") # 添加默认值

    # 从工具上下文的状态中获取先前查询的结果数据
    input_data = tool_context.state.get("query_result") # 使用 .get() 避免 KeyError

    # 如果没有查询结果，则无法进行分析
    if input_data is None:
        return "错误：找不到先前步骤的数据来进行分析。"

    # 构建包含问题和数据的完整输入字符串，传递给数据科学 Agent
    question_with_data = f"""
  要回答的问题：{question}

  用于分析先前问题的实际数据已包含在以下内容中：
  {input_data}

  """

    # 创建 AgentTool 实例，包装数据科学 Agent (ds_agent)
    agent_tool = AgentTool(agent=ds_agent)

    # 异步运行数据科学 Agent 工具，传入包含问题和数据的字符串以及工具上下文
    ds_agent_output = await agent_tool.run_async(
        args={"request": question_with_data}, tool_context=tool_context
    )
    # 将数据科学 Agent 的输出存储在工具上下文的状态中
    tool_context.state["ds_agent_output"] = ds_agent_output
    # 返回数据科学 Agent 的输出
    return ds_agent_output


