
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

"""分析 FOMC 研究 Agent 的研究输出。"""

# 从 google.adk.agents 导入 Agent 类
from google.adk.agents import Agent

# 导入当前包下的模块
from ..agent import MODEL # 导入共享的模型配置
from ..shared_libraries.callbacks import rate_limit_callback # 导入速率限制回调函数
from . import analysis_agent_prompt # 导入分析 agent 的 prompt

# 定义分析 Agent
AnalysisAgent = Agent(
    model=MODEL, # 指定使用的 LLM 模型
    name="analysis_agent", # agent 名称
    description=( # agent 描述
        "分析输入信息并确定对未来 FOMC 行动的影响。"
    ),
    instruction=analysis_agent_prompt.PROMPT, # agent 的指令（prompt）
    before_model_callback=rate_limit_callback, # 在调用模型之前的回调函数（用于速率限制）
)


