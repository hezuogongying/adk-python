
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

"""此代码包含用于 CHASE-SQL Agent 的工具实现。"""

import enum # 导入 enum 模块，用于创建枚举类型
import os # 导入 os 模块，用于与操作系统交互，如此处获取环境变量

from google.adk.tools import ToolContext # 从 ADK 导入 ToolContext，用于工具函数上下文

# pylint: disable=g-importing-member # 禁用特定的 pylint 检查（允许从模块导入成员）
from .dc_prompt_template import DC_PROMPT_TEMPLATE # 从当前目录的 dc_prompt_template 模块导入 DC_PROMPT_TEMPLATE
from .llm_utils import GeminiModel # 从当前目录的 llm_utils 模块导入 GeminiModel 类
from .qp_prompt_template import QP_PROMPT_TEMPLATE # 从当前目录的 qp_prompt_template 模块导入 QP_PROMPT_TEMPLATE
from .sql_postprocessor import sql_translator # 从当前目录的 sql_postprocessor 子包导入 sql_translator 模块

# pylint: enable=g-importing-member # 重新启用特定的 pylint 检查

# 从环境变量中获取 BigQuery 项目 ID
BQ_PROJECT_ID = os.getenv("BQ_PROJECT_ID")


class GenerateSQLType(enum.Enum):
    """SQL 生成方法类型的枚举。

    DC: Divide and Conquer (分而治之) ICL (In-Context Learning) prompting
    QP: Query Plan (查询计划) based prompting
    """

    DC = "dc" # 分而治之方法的值
    QP = "qp" # 查询计划方法的值


def exception_wrapper(func):
    """一个装饰器，用于捕获函数中的异常并将异常作为字符串返回。

    Args:
       func (callable): 要包装的函数。

    Returns:
       callable: 包装后的函数。
    """

    def wrapped_function(*args, **kwargs):
        """包装后的函数逻辑。"""
        try:
            # 尝试执行原函数
            return func(*args, **kwargs)
        except Exception as e:  # pylint: disable=broad-exception-caught # 捕获所有类型的异常
            # 如果发生异常，返回包含函数名和错误信息的字符串
            return f"函数 {func.__name__} 中发生异常: {str(e)}"

    # 返回包装后的函数
    return wrapped_function


def parse_response(response: str) -> str:
    """解析输出以从响应中提取 SQL 内容。

    Args:
       response (str): 包含 SQL 查询的输出字符串。

    Returns:
       str: 从响应中提取的 SQL 查询。
    """
    query = response # 默认情况下，查询就是完整的响应
    try:
        # 检查响应是否包含 Markdown 的 SQL 代码块标记
        if "```sql" in response and "```" in response:
            # 如果包含，则分割字符串以提取 SQL 代码块
            query = response.split("```sql")[1].split("```")[0]
    except ValueError as e:
        # 如果分割失败（例如，格式不规范），打印错误信息
        print(f"解析响应时出错: {e}")
        query = response # 在出错的情况下，仍然返回原始响应
    # 返回提取或原始的查询，并去除首尾空白
    return query.strip()


# @exception_wrapper # 可以选择性地应用异常包装器
def initial_bq_nl2sql(
    question: str,
    tool_context: ToolContext,
) -> str:
    """根据自然语言问题生成初始的 SQL 查询。

    Args:
      question (str): 自然语言问题。
      tool_context (ToolContext): 函数上下文，包含状态信息如数据库设置。

    Returns:
      str: 用于回答该问题的 SQL 语句。
    """
    print("****** 正在使用 ChaseSQL 算法运行 Agent。")
    # 从 tool_context.state 中提取数据库相关的设置和 ChaseSQL 参数
    ddl_schema = tool_context.state["database_settings"]["bq_ddl_schema"]
    project = tool_context.state["database_settings"]["bq_project_id"]
    db = tool_context.state["database_settings"]["bq_dataset_id"]
    transpile_to_bigquery = tool_context.state["database_settings"][
        "transpile_to_bigquery"
    ]
    process_input_errors = tool_context.state["database_settings"][
        "process_input_errors"
    ]
    process_tool_output_errors = tool_context.state["database_settings"][
        "process_tool_output_errors"
    ]
    number_of_candidates = tool_context.state["database_settings"][
        "number_of_candidates"
    ]
    model_name_from_context = tool_context.state["database_settings"]["model"] # 变量名区分
    temperature = tool_context.state["database_settings"]["temperature"]
    generate_sql_type = tool_context.state["database_settings"]["generate_sql_type"]

    # 根据指定的 SQL 生成类型选择相应的 Prompt 模板
    if generate_sql_type == GenerateSQLType.DC.value:
        # 使用分而治之 (DC) 的 Prompt 模板
        prompt = DC_PROMPT_TEMPLATE.format(
            SCHEMA=ddl_schema, QUESTION=question, BQ_PROJECT_ID=BQ_PROJECT_ID
        )
    elif generate_sql_type == GenerateSQLType.QP.value:
        # 使用查询计划 (QP) 的 Prompt 模板
        prompt = QP_PROMPT_TEMPLATE.format(
            SCHEMA=ddl_schema, QUESTION=question, BQ_PROJECT_ID=BQ_PROJECT_ID
        )
    else:
        # 如果类型不支持，则抛出 ValueError
        raise ValueError(f"不支持的 generate_sql_type: {generate_sql_type}")

    # 初始化 Gemini 模型
    model = GeminiModel(model_name=model_name_from_context, temperature=temperature)
    # 创建请求列表，数量等于 number_of_candidates
    requests = [prompt for _ in range(number_of_candidates)]
    # 并行调用模型生成 SQL 查询，并使用 parse_response 解析结果
    responses = model.call_parallel(requests, parser_func=parse_response)
    # 目前仅取第一个响应结果
    # TODO: 如果 number_of_candidates > 1，这里可能需要选择最佳响应的逻辑
    response_sql = responses[0] # 变量名区分

    # 如果需要将生成的 SQL 转译为 BigQuery 方言
    if transpile_to_bigquery:
        # 初始化 SQL 翻译器
        translator = sql_translator.SqlTranslator(
            model=model, # 复用之前创建的 GeminiModel 实例
            temperature=temperature,
            process_input_errors=process_input_errors,
            process_tool_output_errors=process_tool_output_errors,
        )
        # pylint: disable=g-bad-todo # 暂时禁用 TODO 相关的 pylint 检查
        # TODO: 考虑为 translate 方法添加更多上下文信息或改进错误处理
        # pylint: enable=g-bad-todo # 重新启用 TODO 相关的 pylint 检查
        # 调用翻译器的 translate 方法进行转译
        response_sql: str = translator.translate(
            response_sql, ddl_schema=ddl_schema, db=db, catalog=project
        )

    # 返回最终（可能已转译）的 SQL 查询
    return response_sql


