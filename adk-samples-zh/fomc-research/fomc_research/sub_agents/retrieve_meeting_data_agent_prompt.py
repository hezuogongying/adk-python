
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

"""FOMC 研究 Agent 的检索会议数据子 agent"""

# 从 google.adk.agents 导入 Agent 类
from google.adk.agents import Agent
# 从 google.adk.tools 导入 AgentTool，用于将 agent 包装成工具
from google.adk.tools.agent_tool import AgentTool

# 导入当前包下的模块
from ..agent import MODEL # 导入共享的模型配置
from ..shared_libraries.callbacks import rate_limit_callback # 导入速率限制回调函数
from ..tools.fetch_page import fetch_page_tool # 导入获取页面工具
from . import retrieve_meeting_data_agent_prompt # 导入检索会议数据 agent 的 prompt
from .extract_page_data_agent import ExtractPageDataAgent # 导入提取页面数据子 agent

# 定义检索会议数据 Agent
RetrieveMeetingDataAgent = Agent(
    model=MODEL, # 指定使用的 LLM 模型
    name="retrieve_meeting_data_agent", # agent 名称
    description=("从美联储网站检索有关美联储会议的数据"), # agent 描述
    instruction=retrieve_meeting_data_agent_prompt.PROMPT, # agent 的指令（prompt）
    tools=[ # agent 可以使用的工具列表
        fetch_page_tool, # 获取页面工具
        AgentTool(ExtractPageDataAgent), # 将 ExtractPageDataAgent 包装成工具
    ],
    sub_agents=[], # 此 agent 不直接调用其他子 agent
    before_model_callback=rate_limit_callback, # 在调用模型之前的回调函数（用于速率限制）
)


