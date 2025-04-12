
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

"""FOMC 研究 Agent 的研究协调 agent。"""

# 从 google.adk.agents 导入 Agent 类
from google.adk.agents import Agent

# 导入当前包下的模块
from ..agent import MODEL # 导入共享的模型配置
from ..shared_libraries.callbacks import rate_limit_callback # 导入速率限制回调函数
from ..tools.compare_statements import compare_statements_tool # 导入比较声明工具
from ..tools.compute_rate_move_probability import compute_rate_move_probability_tool # 导入计算利率变动概率工具
from ..tools.fetch_transcript import fetch_transcript_tool # 导入获取会议记录工具
from ..tools.store_state import store_state_tool # 导入存储状态工具
from . import research_agent_prompt # 导入研究 agent 的 prompt
from .summarize_meeting_agent import SummarizeMeetingAgent # 导入总结会议子 agent

# 定义研究 Agent
ResearchAgent = Agent(
    model=MODEL, # 指定使用的 LLM 模型
    name="research_agent", # agent 名称
    description=( # agent 描述
        "研究最新的 FOMC 会议，为分析提供信息。"
    ),
    instruction=research_agent_prompt.PROMPT, # agent 的指令（prompt）
    sub_agents=[ # agent 可以调用的子 agent 列表
        SummarizeMeetingAgent,
    ],
    tools=[ # agent 可以使用的工具列表
        store_state_tool,
        compare_statements_tool,
        fetch_transcript_tool,
        compute_rate_move_probability_tool,
    ],
    before_model_callback=rate_limit_callback, # 在调用模型之前的回调函数（用于速率限制）
)


