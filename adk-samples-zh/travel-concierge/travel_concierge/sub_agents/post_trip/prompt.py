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

"""旅行后 (Post-trip) agent。这是一个预订后 (post-booking) agent，负责处理旅行结束后的用户体验。"""

from google.adk.agents import Agent

from travel_concierge.sub_agents.post_trip import prompt # 导入旅行后相关的 prompt
from travel_concierge.tools.memory import memorize # 导入记忆工具

# 定义旅行后 agent (post_trip_agent)
post_trip_agent = Agent(
    model="gemini-2.0-flash", # 使用的模型
    name="post_trip_agent", # agent 名称
    description="一个用于跟进用户体验的 agent；通过了解用户反馈，改进用户未来的旅行规划和旅行中体验。", # agent 功能描述
    instruction=prompt.POSTTRIP_INSTR, # agent 的指令 (prompt)
    tools=[memorize], # 该 agent 可使用的工具列表 (目前只有记忆工具)
)

