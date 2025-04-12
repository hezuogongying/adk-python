
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

from google.adk.tools import ToolContext # 导入 ADK 工具上下文
from google.genai import types # 导入 Gemini 类型，用于创建 Artifact

from ..shared_libraries.init_env import webshop_env # 从共享库导入初始化的 webshop 环境实例


def search(keywords: str, tool_context: ToolContext) -> str:
    """在 webshop 中搜索关键词。

    Args:
      keywords(str): 要搜索的关键词。
      tool_context(ToolContext): 函数上下文，用于访问状态和保存 Artifact。

    Returns:
      str: 显示在网页中的搜索结果（文本模式）。
    """
    # 初始化状态字典
    status = {"reward": None, "done": False}
    # 构建传递给环境的动作字符串
    action_string = f"search[{keywords}]"
    # TODO: 这是临时的 hacky 方式，应移除。
    # 强制设置服务器的 assigned_instruction_text，这会影响下次页面渲染时的指令显示
    webshop_env.server.assigned_instruction_text = f"帮我找到 {keywords}。"
    print(f"环境 instruction_text: {webshop_env.instruction_text}") # 打印当前的指令文本（可能是原始的或被覆盖的）
    # 调用环境的 step 方法执行搜索动作
    _, status["reward"], status["done"], _ = webshop_env.step(action_string)

    # 获取搜索后的观测结果
    ob = webshop_env.observation
    # 尝试查找 "Back to Search" 文本，如果找到，则截取其后的内容
    index = ob.find("Back to Search")
    if index >= 0:
        ob = ob[index:]

    # 打印调试信息
    print("#" * 50)
    print("搜索结果:")
    print(f"状态: {status}")
    print(f"观测: {ob}")
    print("#" * 50)

    # 在 ADK UI 中显示 HTML Artifact。
    tool_context.save_artifact(
        f"html", # Artifact 名称
        # 假设 webshop_env.state["html"] 是 HTML 内容
        types.Part.from_text(text=webshop_env.state["html"], mime_type="text/html"),
        # 如果 webshop_env.state["html"] 是文件路径
        # types.Part.from_uri(file_uri=webshop_env.state["html"], mime_type="text/html"),
    )
    # 返回处理后的观测文本
    return ob


