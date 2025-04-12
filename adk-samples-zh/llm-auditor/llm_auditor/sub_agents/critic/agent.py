
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

"""LLM Auditor，用于使用网络验证和优化 LLM 生成的答案。"""

# 从 google.adk.agents 导入 SequentialAgent 类
from google.adk.agents import SequentialAgent

# 导入当前包下的子 agent
from .sub_agents.critic import critic_agent # 评论家 agent
from .sub_agents.reviser import reviser_agent # 修订者 agent


# 定义 LLM Auditor agent，它是一个顺序 agent
llm_auditor = SequentialAgent(
    name='llm_auditor', # agent 名称
    description=( # agent 描述
        '评估 LLM 生成的答案，使用网络验证事实准确性，并优化响应以确保与现实世界知识保持一致。'
    ),
    sub_agents=[critic_agent, reviser_agent], # 按顺序执行的子 agent 列表
)

# 将 llm_auditor 设为根 agent，以便部署和调用
root_agent = llm_auditor


