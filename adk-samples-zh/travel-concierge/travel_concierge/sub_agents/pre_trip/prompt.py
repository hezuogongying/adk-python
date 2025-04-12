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

"""旅行前 (Pre-trip) agent。这是一个预订后 (post-booking) agent，负责处理临近旅行期间的用户体验。"""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from travel_concierge.shared_libraries import types # 导入共享类型
from travel_concierge.sub_agents.pre_trip import prompt # 导入旅行前相关的 prompt
from travel_concierge.tools.search import google_search_grounding # 导入基于 Google 搜索的 grounding 工具

# 定义打包建议 agent (what_to_pack_agent)
what_to_pack_agent = Agent(
    model="gemini-2.0-flash", # 使用的模型
    name="what_to_pack_agent", # agent 名称
    description="为旅行提供携带物品的建议", # agent 功能描述
    instruction=prompt.WHATTOPACK_INSTR, # agent 的指令 (prompt)
    disallow_transfer_to_parent=True, # 不允许将任务转交回父 agent
    disallow_transfer_to_peers=True, # 不允许将任务转交给同级 agent
    output_key="what_to_pack", # 在状态 (state) 中存储输出结果时使用的键名
    output_schema=types.PackingList, # 定义输出应遵循的 Pydantic 模型 (PackingList)
)

# 定义主旅行前 agent (pre_trip_agent)
pre_trip_agent = Agent(
    model="gemini-2.0-flash", # 使用的模型
    name="pre_trip_agent", # agent 名称
    description="给定一个行程，此 agent 会保持信息更新，并在旅行前向用户提供相关的旅行信息。", # agent 功能描述
    instruction=prompt.PRETRIP_AGENT_INSTR, # agent 的指令 (prompt)
    tools=[ # 该 agent 可使用的工具列表
        google_search_grounding, # Google 搜索 grounding 工具
        AgentTool(agent=what_to_pack_agent) # 封装打包建议 agent 为工具
        ],
)

