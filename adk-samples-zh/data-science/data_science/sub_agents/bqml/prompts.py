
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

"""数据科学 Agent V2：生成 nl2py（自然语言到 Python）并使用代码解释器运行代码。"""
# 注意：此文件描述的是 BQML Agent，不是 nl2py。nl2py 可能在其他 Agent 或工具中实现。

from google.adk.agents import Agent # 导入 ADK Agent 类
from google.adk.tools import ToolContext # 导入 ADK ToolContext 类
from google.adk.tools.agent_tool import AgentTool # 导入 ADK AgentTool，用于将一个 Agent 作为另一个 Agent 的工具
from google.adk.agents.callback_context import CallbackContext # 导入回调上下文类

# 从当前目录的 tools 模块导入 BQML 相关工具函数
from data_science.sub_agents.bqml.tools import (
    check_bq_models,
    execute_bqml_code,
    rag_response,
)
# 从当前目录的 prompts 模块导入 BQML Agent 的指令 Prompt 函数
from .prompts import return_instructions_bqml

# 从 BigQuery 子 Agent 导入数据库 Agent 和获取数据库设置的工具
from data_science.sub_agents.bigquery.agent import database_agent as bq_db_agent
from data_science.sub_agents.bigquery.tools import (
    get_database_settings as get_bq_database_settings,
)

# 定义 Agent 调用之前的设置回调函数
def setup_before_agent_call(callback_context: CallbackContext):
    """设置 Agent。

    在 Agent 处理用户请求之前执行此函数，用于初始化或配置 Agent 的状态和指令。

    Args:
        callback_context: 回调上下文对象，包含会话状态 (state) 和调用上下文 (invocation_context)。
    """

    # 在会话状态 (session.state) 中设置数据库设置
    # 检查 'database_settings' 是否已存在于状态中
    # 注意：这里的逻辑似乎是设置 'all_db_settings' 而不是 'database_settings'
    if "all_db_settings" not in callback_context.state:
        db_settings = dict()
        # 假设默认或当前使用的数据库是 BigQuery
        db_settings["use_database"] = "BigQuery"
        callback_context.state["all_db_settings"] = db_settings

    # 在指令中设置模式信息
    # 检查状态中指定的数据库类型
    if callback_context.state["all_db_settings"]["use_database"] == "BigQuery":
        # 如果是 BigQuery，调用函数获取 BigQuery 的特定设置
        callback_context.state["database_settings"] = get_bq_database_settings()
        # 从获取的设置中提取 DDL 模式信息
        schema = callback_context.state["database_settings"]["bq_ddl_schema"]

        # 更新 Agent 的指令 (instruction)
        # 将从 prompts 模块获取的基础指令与包含模式信息的字符串拼接起来
        # 这使得 Agent 在处理请求时能够“看到”相关的数据库模式
        callback_context._invocation_context.agent.instruction = (
            return_instructions_bqml() # 获取基础 BQML 指令
            + f"""

   </BQML 参考信息结束>

    <相关数据的 BigQuery 模式及少量示例行>
    {schema}
    </相关数据的 BigQuery 模式及少量示例行>
    """
        )
    # else:
        # 可以添加对其他数据库类型（如 PostgreSQL）的处理逻辑
        # callback_context.state["database_settings"] = get_pg_database_settings()
        # ... 更新指令 ...

# 定义一个异步工具函数，用于调用数据库 Agent (nl2sql)
async def call_db_agent(
    question: str, # 自然语言问题
    tool_context: ToolContext, # 工具上下文
):
    """调用数据库 (nl2sql) Agent 的工具。

    根据会话状态中指定的数据库类型，选择并调用相应的数据库 Agent 来将自然语言问题转换为 SQL 查询。

    Args:
        question: 用户提出的自然语言问题。
        tool_context: 工具上下文，包含会话状态。

    Returns:
        数据库 Agent 的输出（通常是生成的 SQL 查询或查询结果/错误信息）。
    """
    # 打印当前使用的数据库类型（用于调试）
    print(
        "\n call_db_agent.use_database:"
        f' {tool_context.state["all_db_settings"]["use_database"]}'
    )
    # 根据状态选择数据库 Agent
    database_agent = (
        bq_db_agent # 如果是 BigQuery，选择 bq_db_agent
        if tool_context.state["all_db_settings"]["use_database"] == "BigQuery"
        # else pg_db_agent # 如果是 PostgreSQL，选择 pg_db_agent (此处注释掉了)
        else None # 其他情况暂不支持
    )
    # 如果没有找到合适的数据库 Agent，可以抛出错误或返回提示信息
    if database_agent is None:
        return "错误：未找到或不支持当前配置的数据库 Agent。"

    # 将选定的数据库 Agent 包装成 AgentTool
    agent_tool = AgentTool(agent=database_agent)
    # 异步运行 AgentTool，传递问题作为参数，并传入当前的工具上下文
    db_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    # 将数据库 Agent 的输出存储在当前工具上下文的状态中，供后续步骤使用
    tool_context.state["db_agent_output"] = db_agent_output
    # 返回数据库 Agent 的输出
    return db_agent_output


# 定义根 Agent (BQML Agent)
root_agent = Agent(
    model="gemini-1.5-flash", # 指定使用的 LLM 模型
    name="bq_ml_agent", # Agent 的名称
    instruction=return_instructions_bqml(), # 设置 Agent 的指令 Prompt
    before_agent_callback=setup_before_agent_call, # 设置 Agent 调用前的回调函数
    # 列出 Agent 可以使用的工具
    tools=[
        execute_bqml_code, # 执行 BQML 代码的工具
        check_bq_models,   # 检查现有 BQML 模型的工具
        call_db_agent,     # 调用数据库 Agent (nl2sql) 的工具
        rag_response       # 从 RAG 语料库检索信息的工具
        ],
)


