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

"""规划 agent (Planning agent)。这是一个预订前 (pre-booking) agent，负责旅行的规划部分。"""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
# 导入共享库中的类型定义和常量
from travel_concierge.shared_libraries import types
from travel_concierge.sub_agents.planning import prompt # 导入规划相关的 prompt
from travel_concierge.tools.memory import memorize # 导入记忆工具

# 定义行程创建 agent (itinerary_agent)
itinerary_agent = Agent(
    model="gemini-2.0-flash-001", # 使用的模型
    name="itinerary_agent", # agent 名称
    description="创建并持久化存储结构化的 JSON 格式行程", # agent 功能描述
    instruction=prompt.ITINERARY_AGENT_INSTR, # agent 的指令 (prompt)
    disallow_transfer_to_parent=True, # 不允许将任务转交回父 agent
    disallow_transfer_to_peers=True, # 不允许将任务转交给同级 agent
    output_schema=types.Itinerary, # 定义输出应遵循的 Pydantic 模型 (Itinerary)
    output_key="itinerary", # 在状态 (state) 中存储输出结果时使用的键名
    generate_content_config=types.json_response_config, # 生成内容的配置，确保输出 JSON
)

# 定义酒店房间选择 agent (hotel_room_selection_agent)
hotel_room_selection_agent = Agent(
    model="gemini-2.0-flash-001",
    name="hotel_room_selection_agent",
    description="帮助用户选择酒店的房型", # agent 功能描述
    instruction=prompt.HOTEL_ROOM_SELECTION_INSTR, # agent 指令
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=types.RoomsSelection, # 输出模式为 RoomsSelection
    output_key="room", # 输出结果的键名
    generate_content_config=types.json_response_config, # 确保输出 JSON
)

# 定义酒店搜索 agent (hotel_search_agent)
hotel_search_agent = Agent(
    model="gemini-2.0-flash-001",
    name="hotel_search_agent",
    description="帮助用户在特定地理区域查找酒店", # agent 功能描述
    instruction=prompt.HOTEL_SEARCH_INSTR, # agent 指令
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=types.HotelsSelection, # 输出模式为 HotelsSelection
    output_key="hotel", # 输出结果的键名
    generate_content_config=types.json_response_config, # 确保输出 JSON
)

# 定义航班座位选择 agent (flight_seat_selection_agent)
flight_seat_selection_agent = Agent(
    model="gemini-2.0-flash-001",
    name="flight_seat_selection_agent",
    description="帮助用户选择航班座位", # agent 功能描述
    instruction=prompt.FLIGHT_SEAT_SELECTION_INSTR, # agent 指令
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=types.SeatsSelection, # 输出模式为 SeatsSelection
    output_key="seat", # 输出结果的键名
    generate_content_config=types.json_response_config, # 确保输出 JSON
)

# 定义航班搜索 agent (flight_search_agent)
flight_search_agent = Agent(
    model="gemini-2.0-flash-001",
    name="flight_search_agent",
    description="帮助用户查找最优惠的机票", # agent 功能描述
    instruction=prompt.FLIGHT_SEARCH_INSTR, # agent 指令
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=types.FlightsSelection, # 输出模式为 FlightsSelection
    output_key="flight", # 输出结果的键名
    generate_content_config=types.json_response_config, # 确保输出 JSON
)

# 定义主规划 agent (planning_agent)
planning_agent = Agent(
    model="gemini-2.0-flash-001",
    description="""帮助用户进行旅行规划，为他们的假期制定完整的行程，查找最优惠的机票和酒店。""", # agent 功能描述
    name="planning_agent", # agent 名称
    instruction=prompt.PLANNING_AGENT_INSTR, # agent 指令
    tools=[ # 该 agent 可使用的工具列表
        AgentTool(agent=flight_search_agent), # 封装航班搜索 agent 为工具
        AgentTool(agent=flight_seat_selection_agent), # 封装航班座位选择 agent 为工具
        AgentTool(agent=hotel_search_agent), # 封装酒店搜索 agent 为工具
        AgentTool(agent=hotel_room_selection_agent), # 封装酒店房间选择 agent 为工具
        AgentTool(agent=itinerary_agent), # 封装行程创建 agent 为工具
        memorize, # 记忆工具，用于存储用户选择或偏好
    ],
    generate_content_config=GenerateContentConfig( # 内容生成配置
        temperature=0.1, # 控制生成文本的随机性，较低的值使输出更确定
        top_p=0.5 # 控制生成文本的多样性，通过核采样选择概率总和为 0.5 的词汇
    )
)

