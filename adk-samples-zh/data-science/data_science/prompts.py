
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

"""数据科学多 Agent 的顶层 Agent。

-- 使用 NL2SQL 从数据库（例如 BigQuery）获取数据
-- 然后，根据需要使用 NL2Py 进行进一步的数据分析
"""

# 导入日期模块
from datetime import date

# 导入 Google Generative AI 类型库
from google.genai import types

# 导入 ADK Agent 类和回调上下文
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
# 导入 ADK 加载 artifact 工具
from google.adk.tools import load_artifacts

# 从子 Agent 模块导入 BQML Agent
from .sub_agents import bqml_agent
# 从 BigQuery 子 Agent 的工具模块导入获取数据库设置的函数
from .sub_agents.bigquery.tools import (
    get_database_settings as get_bq_database_settings,
)
# 从当前目录导入根 Agent 的 prompt 函数
from .prompts import return_instructions_root
# 从当前目录导入工具函数
from .tools import call_db_agent, call_ds_agent

# 获取今天的日期
date_today = date.today()


# 定义 Agent 调用前的设置函数
def setup_before_agent_call(callback_context: CallbackContext):
    """设置 Agent。"""

    # 在会话状态 (session.state) 中设置数据库设置
    if "database_settings" not in callback_context.state:
        db_settings = dict()
        # 默认使用 BigQuery 数据库
        db_settings["use_database"] = "BigQuery"
        callback_context.state["all_db_settings"] = db_settings

    # 在指令 (instruction) 中设置 schema
    # 如果当前使用的数据库是 BigQuery
    if callback_context.state["all_db_settings"]["use_database"] == "BigQuery":
        # 获取 BigQuery 的数据库设置
        callback_context.state["database_settings"] = get_bq_database_settings()
        # 获取 BigQuery 的 DDL schema
        schema = callback_context.state["database_settings"]["bq_ddl_schema"]

        # 更新 Agent 的指令，追加 schema 信息
        callback_context._invocation_context.agent.instruction = (
            return_instructions_root() # 获取基础指令
            + f"""

    --------- 相关数据的 BigQuery schema 及少量示例行。 ---------
    {schema}

    """
        )


# 定义根 Agent (root_agent)
root_agent = Agent(
    # 使用的模型名称
    model="gemini-1.5-flash-exp", # 注意：这里使用了实验性模型 gemini-1.5-flash-exp
    # Agent 名称
    name="db_ds_multiagent",
    # Agent 指令 (通过 setup_before_agent_call 动态设置 schema)
    instruction=return_instructions_root(),
    # 全局指令，提供通用上下文
    global_instruction=(
        f"""
        你是一个数据科学和数据分析多 Agent 系统。
        今天是：{date_today}
        """
    ),
    # 包含的子 Agent 列表
    sub_agents=[bqml_agent],
    # Agent 可用的工具列表
    tools=[
        call_db_agent,   # 调用数据库 Agent 的工具
        call_ds_agent,   # 调用数据科学 Agent 的工具
        load_artifacts, # 加载 artifact 的工具
    ],
    # 注册 Agent 调用前的回调函数
    before_agent_callback=setup_before_agent_call,
    # 配置生成内容参数，设置温度为 0.01 以获得更确定的输出
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)


