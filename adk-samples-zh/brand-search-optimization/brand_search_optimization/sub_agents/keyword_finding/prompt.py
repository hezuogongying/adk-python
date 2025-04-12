
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

"""定义关键词查找 Agent。"""

# 导入 ADK 的 Agent 类
from google.adk.agents.llm_agent import Agent

# 从上层目录的共享库导入常量
from ...shared_libraries import constants
# 从上层目录的工具模块导入 BigQuery 连接器工具
from ...tools import bq_connector
# 从当前目录导入 prompt
from . import prompt

# 定义关键词查找 Agent (keyword_finding_agent)
keyword_finding_agent = Agent(
    # 指定使用的 LLM 模型
    model=constants.MODEL,
    # Agent 名称
    name="keyword_finding_agent",
    # Agent 描述：一个用于查找关键词的有用 Agent
    description="一个用于查找关键词的有用 Agent",
    # Agent 指令 (从 prompt 模块获取)
    instruction=prompt.KEYWORD_FINDING_AGENT_PROMPT,
    # Agent 可用的工具列表
    tools=[
        # 用于从 BigQuery 获取品牌产品详情的工具
        bq_connector.get_product_details_for_brand,
    ],
)


