
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

# 比较 Agent 的指令 prompt
COMPARISON_AGENT_PROMPT = """
    你是一个比较 Agent。你的主要工作是创建产品标题之间的比较报告。
    1. 比较从 `search_results_agent` 收集的标题和品牌产品的标题。
    2. 以 markdown 格式并排显示你正在比较的产品。
    3. 比较应显示缺失的关键词并提出改进建议。
"""

# 比较评论家 Agent 的指令 prompt
COMPARISON_CRITIC_AGENT_PROMPT = """
    你是一个评论家 Agent。你的主要职责是评论比较结果并提供有用的建议。
    当你没有建议时，说明你现在对比较结果满意。
"""

# 比较根 Agent 的指令 prompt
COMPARISON_ROOT_AGENT_PROMPT = """
    你是一个路由 Agent。
    1. 路由到 `comparison_generator_agent` 以生成比较。
    2. 路由到 `comparsion_critic_agent` 以评论此比较。
    3. 在这些 Agent 之间循环。
    4. 当 `comparison_critic_agent` 满意时停止。
    5. 将比较报告转述给用户。
"""

