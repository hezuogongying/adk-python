
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

# 导入 ADK 的 Agent 类
from google.adk.agents.llm_agent import Agent

# 从上层目录的共享库导入常量
from ...shared_libraries import constants
# 从当前目录导入 prompt
from . import prompt

# 定义比较生成器 Agent (comparison_generator_agent)
comparison_generator_agent = Agent(
    # 指定使用的 LLM 模型
    model=constants.MODEL,
    # Agent 名称
    name="comparison_generator_agent",
    # Agent 描述：一个用于生成比较的有用 Agent
    description="一个用于生成比较的有用 Agent。",
    # Agent 指令 (从 prompt 模块获取)
    instruction=prompt.COMPARISON_AGENT_PROMPT,
)

# 定义比较评论家 Agent (comparsion_critic_agent)
comparsion_critic_agent = Agent(
    # 指定使用的 LLM 模型
    model=constants.MODEL,
    # Agent 名称
    name="comparison_critic_agent",
    # Agent 描述：一个用于评论比较的有用 Agent
    description="一个用于评论比较的有用 Agent。",
    # Agent 指令 (从 prompt 模块获取)
    instruction=prompt.COMPARISON_CRITIC_AGENT_PROMPT,
)

# 定义比较根 Agent (comparison_root_agent)
comparison_root_agent = Agent(
    # 指定使用的 LLM 模型
    model=constants.MODEL,
    # Agent 名称
    name="comparison_root_agent",
    # Agent 描述：一个用于比较标题的有用 Agent
    description="一个用于比较标题的有用 Agent。",
    # Agent 指令 (从 prompt 模块获取)
    instruction=prompt.COMPARISON_ROOT_AGENT_PROMPT,
    # 包含的子 Agent 列表
    sub_agents=[comparison_generator_agent, comparsion_critic_agent],
)


