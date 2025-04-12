
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

"""数据库 Agent：使用 NL2SQL 从数据库（BigQuery）获取数据。"""

import os
# 导入 Google Generative AI 类型库
from google.genai import types

# 导入 ADK Agent 类和回调上下文
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

# 从当前目录导入 prompt 函数和工具函数
from .prompts import return_instructions_bigquery
from . import tools
# 从 chase_sql 子模块导入 ChaseSQL 相关工具
from .chase_sql import chase_db_tools

# 从环境变量获取 NL2SQL 方法，默认为 "BASELINE"
NL2SQL_METHOD = os.getenv("NL2SQL_METHOD", "BASELINE")


# 定义 Agent 调用前的设置函数
def setup_before_agent_call(callback_context: CallbackContext) -> None:
    """设置 Agent。"""

    # 如果会话状态中没有数据库设置，则获取并存储
    if "database_settings" not in callback_context.state:
        callback_context.state["database_settings"] = tools.get_database_settings()


# 定义数据库 Agent (database_agent)
database_agent = Agent(
    # 使用的模型名称
    model="gemini-1.5-flash-exp", # 注意：使用了实验性模型
    # Agent 名称
    name="database_agent",
    # Agent 指令 (从 prompts 模块获取)
    instruction=return_instructions_bigquery(),
    # Agent 可用的工具列表
    tools=[
        # 根据 NL2SQL_METHOD 选择不同的初始 SQL 生成工具
        (
            chase_db_tools.initial_bq_nl2sql # 如果使用 CHASE 方法
            if NL2SQL_METHOD == "CHASE"
            else tools.initial_bq_nl2sql      # 否则使用基线方法
        ),
        # BigQuery SQL 验证工具
        tools.run_bigquery_validation,
    ],
    # 注册 Agent 调用前的回调函数
    before_agent_callback=setup_before_agent_call,
    # 配置生成内容参数，设置温度为 0.01 以获得更确定的输出
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)


