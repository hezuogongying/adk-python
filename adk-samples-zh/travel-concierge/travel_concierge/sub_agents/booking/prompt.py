
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

"""预订 Agent 和子 Agent，处理可预订事件的确认和支付。"""

from google.adk.agents import Agent # 导入 ADK Agent 类
from google.adk.tools.agent_tool import AgentTool # 导入 Agent 工具包装器
from google.genai.types import GenerateContentConfig # 导入生成配置

from travel_concierge.sub_agents.booking import prompt # 导入预订相关的提示


# 创建预订 Agent
create_reservation = Agent(
    model="gemini-2.0-flash-001", # 使用的模型
    name="create_reservation", # Agent 名称
    description="""为所选项目创建预订。""", # Agent 描述
    instruction=prompt.CONFIRM_RESERVATION_INSTR, # 设置指令
)

# 支付选择 Agent
payment_choice = Agent(
    model="gemini-2.0-flash-001",
    name="payment_choice",
    description="""向用户显示可用的支付选项。""",
    instruction=prompt.PAYMENT_CHOICE_INSTR,
)

# 处理支付 Agent
process_payment = Agent(
    model="gemini-2.0-flash-001",
    name="process_payment",
    description="""根据选择的支付方式处理支付，完成交易。""",
    instruction=prompt.PROCESS_PAYMENT_INSTR,
)


# 主预订 Agent (Booking Agent)
booking_agent = Agent(
    model="gemini-2.0-flash-001",
    name="booking_agent",
    description="给定一个行程，通过处理支付选项和流程来完成项目预订。",
    instruction=prompt.BOOKING_AGENT_INSTR, # 设置主预订 Agent 的指令
    # 将上面定义的子 Agent 作为工具提供给 booking_agent
    tools=[
        AgentTool(agent=create_reservation),
        AgentTool(agent=payment_choice),
        AgentTool(agent=process_payment),
    ],
    # 配置生成参数，降低温度以获得更确定的输出
    generate_content_config=GenerateContentConfig(
        temperature=0.0, top_p=0.5 # 较低的温度和 top_p 使输出更具确定性
    )
)


