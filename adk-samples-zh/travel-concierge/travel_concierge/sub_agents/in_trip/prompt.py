
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

"""行程中 Agent。一个预订后的 Agent，负责处理旅行期间的用户体验。"""

from google.adk.agents import Agent # 导入 ADK Agent 类
from google.adk.tools.agent_tool import AgentTool # 导入 Agent 工具包装器

from travel_concierge.sub_agents.in_trip import prompt # 导入行程中相关的提示
# 导入行程中阶段使用的工具
from travel_concierge.sub_agents.in_trip.tools import (
    transit_coordination, # 交通协调工具（动态生成指令）
    flight_status_check, # 航班状态检查工具
    event_booking_check, # 事件预订检查工具
    weather_impact_check, # 天气影响检查工具
)

from travel_concierge.tools.memory import memorize # 导入 memorize 工具


# 当天事务处理 Agent (Day-of Agent)
# 预期该子 Agent 在临近旅行时每天被调用，并在旅行期间每天频繁调用数次。
day_of_agent = Agent(
    model="gemini-2.0-flash", # 使用的模型
    name="day_of_agent", # Agent 名称
    description="Day_of Agent 是处理旅行交通后勤的 Agent。", # Agent 描述
    instruction=transit_coordination, # 指令由 transit_coordination 函数动态生成
)


# 行程监控 Agent (Trip Monitor Agent)
trip_monitor_agent = Agent(
    model="gemini-2.0-flash",
    name="trip_monitor_agent",
    description="监控行程的各个方面，并提醒用户注意需要更改的项目",
    instruction=prompt.TRIP_MONITOR_INSTR, # 设置指令
    # 提供给监控 Agent 的工具
    tools=[flight_status_check, event_booking_check, weather_impact_check],
    output_key="daily_checks",  # 输出可以存储在状态中，例如用于发送电子邮件。
)


# 主行程中 Agent (In-trip Agent)
in_trip_agent = Agent(
    model="gemini-2.0-flash",
    name="in_trip_agent",
    description="提供用户在旅途中所需的信息。",
    instruction=prompt.INTRIP_INSTR, # 设置主行程中 Agent 的指令
    # 可以将 trip_monitor_agent 作为子 Agent 调用
    # 这里为了演示目的将其包含在 sub_agents 列表中，但它也可以通过 AgentTool 调用
    sub_agents=[
        trip_monitor_agent
    ],
    # 提供给行程中 Agent 的工具
    tools=[
        AgentTool(agent=day_of_agent), # 将 day_of_agent 包装成工具
        memorize # 添加 memorize 工具
    ],
)


