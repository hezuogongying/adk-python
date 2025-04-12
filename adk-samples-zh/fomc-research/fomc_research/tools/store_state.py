
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

"""FOMC 研究示例 agent 的 'fetch_transcript' 工具"""

# 导入必要的库
import logging

# 从 google.adk.tools 导入 ToolContext
from google.adk.tools import ToolContext
# 从 google.genai.types 导入 Part，用于处理 artifact 数据
from google.genai.types import Part

# 导入当前包下的共享库
from ..shared_libraries import file_utils

# 获取日志记录器
logger = logging.getLogger(__name__)


def fetch_transcript_tool(tool_context: ToolContext) -> dict:
    """从美联储网站检索美联储新闻发布会记录。

    参数:
      tool_context: ToolContext 对象。

    返回:
      一个包含 "status" 和（可选）"error_message" 键的字典。
    """
    # 美联储网站的主机名
    fed_hostname = "https://www.federalreserve.gov"
    # 从工具上下文中获取会议记录 URL
    transcript_url = tool_context.state.get("transcript_url")
    # 如果 URL 不是以 https 开头，则添加主机名
    if transcript_url and not transcript_url.startswith("https"):
        transcript_url = fed_hostname + transcript_url

    # 检查 URL 是否有效
    if not transcript_url:
        logger.error("在状态中未找到 'transcript_url'。")
        return {
            "status": "error",
            "error_message": "未找到会议记录 URL",
        }

    # 从 URL 下载 PDF 文件到 artifact
    pdf_path = file_utils.download_file_from_url(
        transcript_url, "transcript.pdf", tool_context
    )
    # 检查下载是否成功
    if pdf_path is None:
        logger.error("未能从 URL 下载 PDF，中止操作")
        return {
            "status": "error",
            "error_message": "未能从 URL 下载 PDF", # 之前错误信息是 GCS，已更正
        }

    # 从 PDF artifact 中提取文本
    text = file_utils.extract_text_from_pdf_artifact(pdf_path, tool_context)
    # 检查文本提取是否成功
    if text is None:
        logger.error("未能从 PDF 中提取文本，中止操作")
        return {
            "status": "error",
            "error_message": "未能从 PDF 中提取文本",
        }

    # 定义 artifact 文件名
    filename = "transcript_fulltext" # 会议记录全文
    # 将提取的文本保存为 artifact
    version = tool_context.save_artifact(
        filename=filename, artifact=Part(text=text)
    )
    logger.info("已保存 artifact %s, 版本 %i", filename, version)
    # 返回成功状态
    return {"status": "ok"}


