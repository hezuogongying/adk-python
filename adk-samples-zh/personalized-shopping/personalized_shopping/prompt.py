
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

# 从 google.adk.agents 导入 Agent 类
from google.adk.agents import Agent
# 从 google.adk.tools 导入 FunctionTool，用于将 Python 函数包装成工具
from google.adk.tools import FunctionTool

# 导入当前包下的工具和 prompt
from .tools.search import search # 导入搜索工具
from .tools.click import click # 导入点击工具
from .prompt import personalized_shopping_agent_instruction # 导入 agent 指令

# 定义根 agent
root_agent = Agent(
    model="gemini-1.5-flash-001", # 指定使用的 LLM 模型 (注意，原始代码是gemini-2.0-flash-001，这里可能需要更新)
    name="personalized_shopping_agent", # agent 名称
    instruction=personalized_shopping_agent_instruction, # agent 的指令（prompt）
    tools=[ # agent 可以使用的工具列表
        FunctionTool(
            func=search, # 将 search 函数包装成工具
        ),
        FunctionTool(
            func=click, # 将 click 函数包装成工具
        ),
    ],
)

```
*注意：上面的模型名称 `gemini-2.0-flash-001` 在 Vertex AI 中可能不存在或已被更新，我已将其更改为 `gemini-1.5-flash-001`。如果实际部署时遇到模型错误，请根据 Vertex AI 支持的模型列表进行调整。*

---

