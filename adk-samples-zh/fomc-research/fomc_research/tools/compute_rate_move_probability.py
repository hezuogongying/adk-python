
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

"""FOMC 研究示例 agent 的 'compare_statements' 工具。"""

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


def compare_statements_tool(tool_context: ToolContext) -> dict[str, str]:
    """比较请求的声明和之前的声明，并生成 HTML 红线（redline）。

    参数:
      tool_context: ToolContext 对象。

    返回:
      一个包含 "status" 和（可选）"error_message" 键的字典。
    """
    # 美联储网站的主机名
    fed_hostname = "https://www.federalreserve.gov"

    # 从工具上下文中获取请求的声明 PDF URL
    reqd_statement_url = tool_context.state.get(
        "requested_meeting_statement_pdf_url"
    )
    # 如果 URL 不是以 https 开头，则添加主机名
    if reqd_statement_url and not reqd_statement_url.startswith("https"):
        reqd_statement_url = fed_hostname + reqd_statement_url
    # 从工具上下文中获取之前的声明 PDF URL
    prev_statement_url = tool_context.state.get(
        "previous_meeting_statement_pdf_url"
    )
    # 如果 URL 不是以 https 开头，则添加主机名
    if prev_statement_url and not prev_statement_url.startswith("https"):
        prev_statement_url = fed_hostname + prev_statement_url

    # 检查 URL 是否有效
    if not reqd_statement_url or not prev_statement_url:
        logger.error("缺少声明 URL，中止操作")
        return {
            "status": "error",
            "error_message": "未能找到声明文件的 URL",
        }

    # 从 URL 下载 PDF 文件到 artifact
    reqd_pdf_path = file_utils.download_file_from_url(
        reqd_statement_url, "curr.pdf", tool_context
    )
    prev_pdf_path = file_utils.download_file_from_url(
        prev_statement_url, "prev.pdf", tool_context
    )

    # 检查下载是否成功
    if reqd_pdf_path is None or prev_pdf_path is None:
        logger.error("未能下载文件，中止操作")
        return {
            "status": "error",
            "error_message": "未能下载声明文件",
        }

    # 从 PDF artifact 中提取文本
    reqd_pdf_text = file_utils.extract_text_from_pdf_artifact(
        reqd_pdf_path, tool_context
    )
    prev_pdf_text = file_utils.extract_text_from_pdf_artifact(
        prev_pdf_path, tool_context
    )

    # 检查文本提取是否成功
    if reqd_pdf_text is None or prev_pdf_text is None:
        logger.error("未能从 PDF 中提取文本，中止操作")
        return {
            "status": "error",
            "error_message": "未能从 PDF 中提取文本",
        }

    # 将提取的文本保存为 artifact
    tool_context.save_artifact(
        filename="requested_statement_fulltext", # 请求的声明全文
        artifact=Part(text=reqd_pdf_text),
    )
    tool_context.save_artifact(
        filename="previous_statement_fulltext", # 之前的声明全文
        artifact=Part(text=prev_pdf_text),
    )

    # 创建 HTML 红线差异
    redline_html = file_utils.create_html_redline(reqd_pdf_text, prev_pdf_text)
    # 将 HTML 红线保存为 artifact
    file_utils.save_html_to_artifact(
        redline_html, "statement_redline", tool_context # 声明红线
    )

    # 返回成功状态
    return {"status": "ok"}


