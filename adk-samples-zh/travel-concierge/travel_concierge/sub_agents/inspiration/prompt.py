
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

"""灵感 Agent。一个预订前的 Agent，负责旅行的构思部分。"""

from google.adk.agents import Agent # 导入 ADK Agent 类
from google.adk.tools.agent_tool import AgentTool # 导入 Agent 工具包装器
# 导入共享库中的 Pydantic 类型和 JSON 响应配置
from travel_concierge.shared_libraries.types import DesintationIdeas, POISuggestions, json_response_config
from travel_concierge.sub_agents.inspiration import prompt # 导入灵感相关的提示
from travel_concierge.tools.places import map_tool # 导入地图工具


# 地点推荐 Agent
place_agent = Agent(
    model="gemini-2.0-flash", # 使用的模型
    name="place_agent", # Agent 名称
    instruction=prompt.PLACE_AGENT_INSTR, # 设置指令
    description="该 Agent 根据用户偏好建议一些目的地", # Agent 描述
    disallow_transfer_to_parent=True, # 禁止转移回父 Agent
    disallow_transfer_to_peers=True, # 禁止转移给同级 Agent
    output_schema=DesintationIdeas, # 指定输出模式 (Pydantic 模型)
    output_key="place", # 将输出存储在状态中的键名
    generate_content_config=json_response_config, # 要求生成 JSON 响应
)

# 兴趣点推荐 Agent
poi_agent = Agent(
    model="gemini-2.0-flash",
    name="poi_agent",
    description="该 Agent 根据目的地建议一些活动和兴趣点",
    instruction=prompt.POI_AGENT_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=POISuggestions, # 指定输出模式
    output_key="poi", # 输出存储的键名
    generate_content_config=json_response_config,
)

# 主灵感 Agent (Inspiration Agent)
inspiration_agent = Agent(
    model="gemini-2.0-flash",
    name="inspiration_agent",
    description="一个旅行灵感 Agent，激发用户灵感，发现他们的下一次假期；提供关于地点、活动、兴趣的信息",
    instruction=prompt.INSPIRATION_AGENT_INSTR, # 设置主灵感 Agent 的指令
    # 将 place_agent, poi_agent 和 map_tool 作为可用工具
    tools=[AgentTool(agent=place_agent), AgentTool(agent=poi_agent), map_tool],
)


