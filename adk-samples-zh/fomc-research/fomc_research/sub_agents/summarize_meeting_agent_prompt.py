
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

"""总结 FOMC 会议记录的内容。"""

# 从 google.adk.agents 导入 Agent 类
from google.adk.agents import Agent

# 导入当前包下的模块
from ..agent import MODEL # 导入共享的模型配置
from ..shared_libraries.callbacks import rate_limit_callback # 导入速率限制回调函数
from ..tools.store_state import store_state_tool # 导入存储状态工具
from . import summarize_meeting_agent_prompt # 导入总结会议 agent 的 prompt

# 定义总结会议 Agent
SummarizeMeetingAgent = Agent(
    name="summarize_meeting_agent", # agent 名称
    model=MODEL, # 指定使用的 LLM 模型
    description=( # agent 描述
        "总结最近一次 FOMC 会议的内容和情绪。"
    ),
    instruction=summarize_meeting_agent_prompt.PROMPT, # agent 的指令（prompt）
    tools=[ # agent 可以使用的工具列表
        store_state_tool,
    ],
    before_model_callback=rate_limit_callback, # 在调用模型之前的回调函数（用于速率限制）
)


