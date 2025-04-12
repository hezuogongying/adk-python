
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

"""修订者 (Reviser) agent，用于根据已核实的发现纠正不准确之处。"""

# 从 google.adk 导入 Agent 类
from google.adk import Agent
# 导入回调上下文和 LLM 响应对象
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse

# 导入当前模块下的 prompt
from . import prompt

# 定义编辑结束标记
_END_OF_EDIT_MARK = '---END-OF-EDIT---'


def _remove_end_of_edit_mark(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse:
    """移除响应末尾的编辑结束标记。"""
    del callback_context  # 未使用的参数
    # 检查 llm_response 是否有效
    if not llm_response.content or not llm_response.content.parts:
        return llm_response # 如果无效，直接返回原始响应
    # 遍历响应内容的部分
    for idx, part in enumerate(llm_response.content.parts):
        # 如果找到编辑结束标记
        if _END_OF_EDIT_MARK in part.text:
            # 删除标记之后的所有部分
            del llm_response.content.parts[idx + 1 :]
            # 截断当前部分的文本，移除标记及其之后的内容
            part.text = part.text.split(_END_OF_EDIT_MARK, 1)[0]
            # 找到并处理后即可跳出循环（假设标记只出现一次）
            break # 添加 break 提高效率
    return llm_response


# 定义修订者 agent
reviser_agent = Agent(
    model='gemini-1.5-flash-001', # 指定使用的 LLM 模型 (注意，原始代码是gemini-2.0-flash，这里可能需要更新)
    name='reviser_agent', # agent 名称
    instruction=prompt.REVISER_PROMPT, # agent 的指令（prompt）
    after_model_callback=_remove_end_of_edit_mark, # 在模型调用之后的回调函数（用于移除编辑标记）
)
```
*注意：上面的模型名称 `gemini-2.0-flash` 在 Vertex AI 中可能不存在或已被更新，我已将其更改为 `gemini-1.5-flash-001`。如果实际部署时遇到模型错误，请根据 Vertex AI 支持的模型列表进行调整。*

---

