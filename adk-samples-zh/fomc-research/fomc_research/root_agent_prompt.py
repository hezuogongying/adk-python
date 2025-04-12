
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

"""FOMC 研究示例 agent。"""

# 导入必要的库
import logging
import warnings

# 从 google.adk.agents 导入 Agent 类
from google.adk.agents import Agent

# 导入当前包下的模块
from . import MODEL, root_agent_prompt # 模型和根 agent 的 prompt
from .shared_libraries.callbacks import rate_limit_callback # 共享库中的回调函数
from .sub_agents.analysis_agent import AnalysisAgent # 分析子 agent
from .sub_agents.research_agent import ResearchAgent # 研究子 agent
from .sub_agents.retrieve_meeting_data_agent import RetrieveMeetingDataAgent # 检索会议数据子 agent
from .tools.store_state import store_state_tool # 存储状态工具

# 忽略 pydantic 相关的 UserWarning
warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

# 获取日志记录器
logger = logging.getLogger(__name__)
# 记录使用的模型
logger.debug("正在使用模型: %s", MODEL)


# 定义根 agent
root_agent = Agent(
    model=MODEL, # 指定使用的 LLM 模型
    name="root_agent", # agent 名称
    description=( # agent 描述
        "使用提供的工具和其他 agent 生成关于最近 FOMC 会议的分析报告。"
    ),
    instruction=root_agent_prompt.PROMPT, # agent 的指令（prompt）
    tools=[store_state_tool], # agent 可以使用的工具列表
    sub_agents=[ # agent 可以调用的子 agent 列表
        RetrieveMeetingDataAgent,
        ResearchAgent,
        AnalysisAgent,
    ],
    before_model_callback=rate_limit_callback, # 在调用模型之前的回调函数（用于速率限制）
)


