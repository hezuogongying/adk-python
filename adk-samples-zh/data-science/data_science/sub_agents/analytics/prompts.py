
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

"""数据科学 Agent V2：生成 nl2py（自然语言转 Python）并使用代码解释器运行代码。"""

# 导入 ADK 代码执行器和 Agent 类
from google.adk.code_executors import VertexAiCodeExecutor
from google.adk.agents import Agent
# 从当前目录导入 prompt 函数
from .prompts import return_instructions_ds
# 从 utils 导入获取环境变量的函数
from data_science.utils.utils import get_env_var

# 定义根 Agent (在此上下文中，是数据科学 Agent)
root_agent = Agent(
    # 使用的模型名称
    model="gemini-1.5-flash-exp", # 注意：使用了实验性模型
    # Agent 名称
    name="data_science_agent",
    # Agent 指令 (从 prompts 模块获取)
    instruction=return_instructions_ds(),
    # 配置代码执行器
    code_executor=VertexAiCodeExecutor(
        # 指定代码解释器扩展的名称，从环境变量获取
        name=get_env_var("CODE_INTERPRETER_EXTENSION_NAME"),
        # 优化数据文件传输
        optimize_data_file=True,
        # 启用有状态执行（保持变量和状态）
        stateful=True,
    ),
)


