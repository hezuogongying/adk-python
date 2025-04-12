
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

"""使用 Agent Development Kit (ADK) 演示 Travel AI Concierge"""

from google.adk.agents import Agent # 导入 ADK Agent 类

from travel_concierge import prompt # 导入本地 prompt 模块

# 导入各个子 Agent
from travel_concierge.sub_agents.booking.agent import booking_agent
from travel_concierge.sub_agents.in_trip.agent import in_trip_agent
from travel_concierge.sub_agents.inspiration.agent import inspiration_agent
from travel_concierge.sub_agents.planning.agent import planning_agent
from travel_concierge.sub_agents.post_trip.agent import post_trip_agent
from travel_concierge.sub_agents.pre_trip.agent import pre_trip_agent

# 导入用于加载初始状态的回调函数
from travel_concierge.tools.memory import _load_precreated_itinerary

# 定义根 Agent
root_agent = Agent(
    model="gemini-2.0-flash-001", # 使用的模型
    name="root_agent", # Agent 名称
    description="一个使用多个子 Agent 服务的旅行管家 (Travel Concierge)", # Agent 描述
    instruction=prompt.ROOT_AGENT_INSTR, # 设置 Agent 指令（从 prompt 模块获取）
    # 定义此 Agent 可以协调的子 Agent 列表
    sub_agents=[
        inspiration_agent, # 灵感 Agent
        planning_agent,    # 规划 Agent
        booking_agent,     # 预订 Agent
        pre_trip_agent,    # 行前准备 Agent
        in_trip_agent,     # 行程中 Agent
        post_trip_agent,   # 行后 Agent
    ],
    # 设置在 Agent 调用之前执行的回调函数，用于加载初始行程状态
    before_agent_callback=_load_precreated_itinerary,
)


