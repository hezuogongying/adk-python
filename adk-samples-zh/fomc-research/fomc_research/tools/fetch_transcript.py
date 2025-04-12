
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

"""FOMC 研究示例 agent 的 'fetch_page' 工具"""

# 导入必要的库
import logging
import urllib.request # 用于发送 HTTP 请求和处理 URL
import urllib.error # 用于处理 URL 错误

# 从 google.adk.tools 导入 ToolContext
from google.adk.tools import ToolContext

# 获取日志记录器
logger = logging.getLogger(__name__)


def fetch_page_tool(url: str, tool_context: ToolContext) -> dict[str, str]:
    """检索 'url' 的内容并将其存储在 ToolContext 中。

    参数:
      url: 要获取的 URL。
      tool_context: ToolContext 对象。

    返回:
      一个包含 "status" 和（可选）"message" 键的字典。
    """
    try:
        # 构建一个 OpenerDirector 实例，模拟浏览器行为
        opener = urllib.request.build_opener()
        # 添加 User-Agent 头，防止被某些网站阻止
        opener.addheaders = [("User-Agent", "Mozilla/5.0")]
        # 安装 opener 作为全局默认 opener
        urllib.request.install_opener(opener)
        logger.debug("正在获取页面: %s", url)

        # 打开 URL 并读取页面内容
        page = urllib.request.urlopen(url, timeout=10) # 添加超时
        # 将页面内容解码为 UTF-8 字符串
        page_text = page.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        # 处理 HTTP 错误
        errmsg = f"获取页面 {url} 失败: {err}"
        logger.error(errmsg)
        return {"status": "错误 (ERROR)", "message": errmsg}
    except urllib.error.URLError as err:
        # 处理 URL 错误 (例如，无法连接)
        errmsg = f"获取页面 {url} 时发生 URL 错误: {err.reason}"
        logger.error(errmsg)
        return {"status": "错误 (ERROR)", "message": errmsg}
    except Exception as e:
        # 处理其他可能的异常
        errmsg = f"获取页面 {url} 时发生未知错误: {e}"
        logger.error(errmsg)
        return {"status": "错误 (ERROR)", "message": errmsg}

    # 将获取到的页面内容更新到工具上下文的状态中
    tool_context.state.update({"page_contents": page_text})
    # 返回成功状态
    return {"status": "成功 (OK)"}


