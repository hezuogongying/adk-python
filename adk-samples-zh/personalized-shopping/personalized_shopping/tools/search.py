
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


def click(button_name: str, tool_context: ToolContext) -> str:
    """点击具有给定名称的按钮。

    Args:
      button_name(str): 要点击的按钮的名称（或可点击元素的文本）。
      tool_context(ToolContext): 函数上下文，用于访问状态和保存 Artifact。

    Returns:
      str: 点击按钮后的网页观测内容（文本模式）。
    """
    # 初始化状态字典
    status = {"reward": None, "done": False}
    # 构建传递给环境的动作字符串
    action_string = f"click[{button_name}]"
    # 调用环境的 step 方法执行点击动作
    _, status["reward"], status["done"], _ = webshop_env.step(action_string)

    # 获取点击后的观测结果
    ob = webshop_env.observation
    # 尝试查找 "Back to Search" 文本，如果找到，则截取其后的内容
    # 这可能是为了简化观测，去除页面顶部的通用部分
    index = ob.find("Back to Search")
    if index >= 0:
        ob = ob[index:]

    # 打印调试信息
    print("#" * 50)
    print("点击结果:")
    print(f"状态: {status}")
    print(f"观测: {ob}")
    print("#" * 50)

    # 特殊处理 "Back to Search" 按钮的点击
    if button_name == "Back to Search":
        # TODO: 这是临时的 hacky 方式，应移除。
        # 强制设置服务器的 assigned_instruction_text，这会影响下次页面渲染时的指令显示
        webshop_env.server.assigned_instruction_text = "Back to Search"

    # 在 ADK UI 中显示 HTML Artifact。
    tool_context.save_artifact(
        f"html", # Artifact 名称
        # 从文件 URI 创建 Part 对象，webshop_env.state["html"] 包含当前页面的 HTML 源码（这似乎有点奇怪，应该是内容而不是 URI）
        # Mime 类型设置为 text/html
        # ---
        # 更正：webshop_env.state['html'] 存储的是 HTML 字符串本身，而不是文件 URI。
        # 但 Part.from_uri 可能需要一个 URI。如果 webshop_env.state['html'] 是内容，
        # 应该使用 types.Part.from_text(webshop_env.state['html'], mime_type='text/html')
        # 或者先将 HTML 保存到临时文件再用 from_uri。
        # 假设这里的实现是将其视为内容而非文件路径：
        types.Part.from_text(text=webshop_env.state["html"], mime_type="text/html"),
        # 如果 webshop_env.state["html"] *确实* 是文件路径（虽然不太可能），则原始代码正确：
        # types.Part.from_uri(file_uri=webshop_env.state["html"], mime_type="text/html"),
    )
    # 返回处理后的观测文本
    return ob


