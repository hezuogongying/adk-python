
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

"""fed_research_agent 的文件相关工具函数。"""

# 导入必要的库
import base64 # 用于 Base64 编码和解码
import binascii # 用于处理二进制和 ASCII 之间的转换错误
import io # 用于处理内存中的二进制流
import logging
import mimetypes # 用于猜测文件的 MIME 类型
from collections.abc import Sequence # 用于类型提示

# 导入 diff_match_patch 用于文本比较
import diff_match_patch as dmp
# 导入 pdfplumber 用于提取 PDF 文本
import pdfplumber
# 导入 requests 用于发送 HTTP 请求
import requests
# 从 absl 库导入 app，用于可能的命令行应用
from absl import app
# 从 google.adk.tools 导入 ToolContext
from google.adk.tools import ToolContext
# 从 google.genai.types 导入 Blob 和 Part，用于处理 artifact 数据
from google.genai.types import Blob, Part

# 获取日志记录器
logger = logging.getLogger(__name__)


def download_file_from_url(
    url: str, output_filename: str, tool_context: ToolContext
) -> str:
    """从 URL 下载文件并将其存储在 artifact 中。

    参数:
      url: 要从中检索文件的 URL。
      output_filename: 用于存储文件的 artifact 的名称。
      tool_context: 工具上下文对象。

    返回:
      artifact 的名称。如果下载失败则返回 None。
    """
    logger.info("正在从 %s 下载文件到 %s", url, output_filename)
    try:
        # 发送 GET 请求下载文件，设置超时时间
        response = requests.get(url, timeout=10)
        # 如果请求失败（状态码不是 2xx），则抛出异常
        response.raise_for_status()

        # 将文件内容进行 Base64 编码
        file_bytes = base64.b64encode(response.content)
        # 获取文件的 MIME 类型，优先从响应头获取，否则根据 URL猜测
        mime_type = response.headers.get(
            "Content-Type", mimetypes.guess_type(url)[0] # mimetypes.guess_type 返回 (type, encoding)
        )
        # 创建 artifact 对象
        artifact = Part(inline_data=Blob(data=file_bytes, mime_type=mime_type))
        # 将 artifact 保存到工具上下文中
        tool_context.save_artifact(filename=output_filename, artifact=artifact)
        logger.info("已从 %s 下载文件到 artifact %s", url, output_filename)
        return output_filename

    except requests.exceptions.RequestException as e:
        # 处理下载过程中的请求异常
        logger.error("从 URL 下载文件时出错: %s", e)
        return None


def extract_text_from_pdf_artifact(
    pdf_path: str, tool_context: ToolContext
) -> str:
    """从存储在 artifact 中的 PDF 文件提取文本"""
    # 从工具上下文中加载 PDF artifact
    pdf_artifact = tool_context.load_artifact(pdf_path)
    try:
        # 将 Base64 编码的 PDF 数据解码，并放入内存中的 BytesIO 对象
        with io.BytesIO(
            base64.b64decode(pdf_artifact.inline_data.data)
        ) as pdf_file_obj:
            pdf_text = ""
            # 使用 pdfplumber 打开 PDF 文件对象
            with pdfplumber.open(pdf_file_obj) as pdf:
                # 遍历 PDF 的每一页
                for page in pdf.pages:
                    # 提取当前页的文本并追加到 pdf_text
                    pdf_text += page.extract_text()
            return pdf_text
    except binascii.Error as e:
        # 处理 Base64 解码错误
        logger.error("解码 PDF 时出错: %s", e)
        return None


def create_html_redline(text1: str, text2: str) -> str:
    """创建 text1 和 text2 之间差异的 HTML 红线（redline）文档。"""
    # 初始化 diff_match_patch 对象
    d = dmp.diff_match_patch()
    # 计算两个文本之间的差异 (以 text2 为基准，比较 text1 的变化)
    diffs = d.diff_main(text2, text1)
    # 清理差异结果，使其更符合语义
    d.diff_cleanupSemantic(diffs)

    html_output = ""
    # 遍历差异结果
    for op, text in diffs:
        if op == dmp.DIFF_DELETE:  # 如果是删除操作 (-1)
            # 添加带删除线和红色背景的 HTML 标签
            html_output += (
                f'<del style="background-color: #ffcccc;">{text}</del>'
            )
        elif op == dmp.DIFF_INSERT:  # 如果是插入操作 (1)
            # 添加带下划线和绿色背景的 HTML 标签
            html_output += (
                f'<ins style="background-color: #ccffcc;">{text}</ins>'
            )
        else:  # 如果是相等操作 (0)
            # 直接添加文本
            html_output += text

    return html_output


def save_html_to_artifact(
    html_content: str, output_filename: str, tool_context: ToolContext
) -> str:
    """将 HTML 内容以 UTF-8 编码保存到 artifact 中。

    参数:
      html_content: 要保存的 HTML 内容。
      output_filename: 用于存储 HTML 的 artifact 的名称。
      tool_context: 工具上下文对象。

    返回:
      artifact 的名称。
    """
    # 创建包含 HTML 文本的 artifact Part
    artifact = Part(text=html_content)
    # 将 artifact 保存到工具上下文中
    tool_context.save_artifact(filename=output_filename, artifact=artifact)
    logger.info("HTML 内容已成功保存到 %s", output_filename)
    return output_filename


# 主函数，用于可能的命令行调用，此处为空实现
def main(argv: Sequence[str]) -> None:
    """主执行函数（空）。"""
    if len(argv) > 1:
        raise app.UsageError("命令行参数过多。")


if __name__ == "__main__":
    # 如果作为主脚本运行，则执行 app.run(main)
    app.run(main)


