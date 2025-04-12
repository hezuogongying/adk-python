
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

"""定义品牌搜索优化 Agent"""

# 导入 ADK 的 Agent 类
from google.adk.agents.llm_agent import Agent

# 从共享库导入常量
from .shared_libraries import constants

# 从子 Agent 模块导入对应的根 Agent 或 Agent 实例
from .sub_agents.comparison.agent import comparison_root_agent
from .sub_agents.search_results.agent import search_results_agent
from .sub_agents.keyword_finding.agent import keyword_finding_agent

# 导入根 Agent 的 prompt
from . import prompt

# 定义根 Agent (root_agent)
root_agent = Agent(
    # 指定 Agent 使用的 LLM 模型 (从常量中获取)
    model=constants.MODEL,
    # Agent 的名称 (从常量中获取)
    name=constants.AGENT_NAME,
    # Agent 的描述 (从常量中获取)
    description=constants.DESCRIPTION,
    # Agent 的指令 (从 prompt 模块获取)
    instruction=prompt.ROOT_PROMPT,
    # Agent 包含的子 Agent 列表
    sub_agents=[
        keyword_finding_agent,      # 关键词查找子 Agent
        search_results_agent,       # 搜索结果子 Agent
        comparison_root_agent,      # 比较根子 Agent
    ],
)


