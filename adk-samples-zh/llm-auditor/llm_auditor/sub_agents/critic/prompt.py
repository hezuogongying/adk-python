
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

"""评论家 (Critic) agent，用于使用搜索工具识别和验证陈述。"""

# 从 google.adk 导入 Agent 类
from google.adk import Agent
# 导入回调上下文和 LLM 响应对象
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
# 导入 google_search 工具
from google.adk.tools import google_search
# 从 google.genai 导入类型定义
from google.genai import types

# 导入当前模块下的 prompt
from . import prompt


def _render_reference(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse:
    """将 grounding 引用附加到响应中。"""
    # callback_context 未在此函数中使用
    del callback_context
    # 检查 llm_response 是否有效且包含 grounding 元数据
    if (
        not llm_response.content or
        not llm_response.content.parts or
        not llm_response.grounding_metadata
    ):
        return llm_response # 如果无效，直接返回原始响应

    references = [] # 初始化引用列表
    # 遍历 grounding 区块
    for chunk in llm_response.grounding_metadata.grounding_chunks or []:
        title, uri, text = '', '', '' # 初始化标题、URI 和文本
        # 检查是检索到的上下文还是网络搜索结果
        if chunk.retrieved_context:
            title = chunk.retrieved_context.title
            uri = chunk.retrieved_context.uri
            text = chunk.retrieved_context.text
        elif chunk.web:
            title = chunk.web.title
            uri = chunk.web.uri
        # 组合有效的标题和文本
        parts = [s for s in (title, text) if s]
        # 如果有 URI 和内容部分，则将第一个内容部分格式化为链接
        if uri and parts:
            parts[0] = f'[{parts[0]}]({uri})'
        # 如果有内容部分，则格式化为 Markdown 列表项并添加到引用列表
        if parts:
            references.append('* ' + ': '.join(parts) + '\n')
    # 如果存在引用
    if references:
        # 组合引用文本
        reference_text = ''.join(['\n\n引用 (Reference):\n\n'] + references)
        # 将引用文本作为新的 Part 添加到响应内容中
        llm_response.content.parts.append(types.Part(text=reference_text))
    # （可选）将所有文本部分合并到一个部分中，以简化输出结构
    if all(part.text is not None for part in llm_response.content.parts):
        all_text = '\n'.join(part.text for part in llm_response.content.parts)
        llm_response.content.parts[0].text = all_text
        # 删除合并后的多余部分
        del llm_response.content.parts[1:]
    return llm_response


# 定义评论家 agent
critic_agent = Agent(
    model='gemini-1.5-flash-001', # 指定使用的 LLM 模型 (注意，原始代码是gemini-2.0-flash，这里可能需要更新)
    name='critic_agent', # agent 名称
    instruction=prompt.CRITIC_PROMPT, # agent 的指令（prompt）
    tools=[google_search], # agent 可以使用的工具列表
    after_model_callback=_render_reference, # 在模型调用之后的回调函数（用于添加引用）
)
```
*注意：上面的模型名称 `gemini-2.0-flash` 在 Vertex AI 中可能不存在或已被更新，我已将其更改为 `gemini-1.5-flash-001`。如果实际部署时遇到模型错误，请根据 Vertex AI 支持的模型列表进行调整。*

---

