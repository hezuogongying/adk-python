
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

"""此文件包含数据库 Agent 使用的工具。"""

# 导入日期时间、日志、操作系统和正则表达式模块
import datetime
import logging
import os
import re

# 从项目中导入获取环境变量的工具函数
from data_science.utils.utils import get_env_var
# 导入 ADK 工具上下文
from google.adk.tools import ToolContext
# 导入 BigQuery 客户端库
from google.cloud import bigquery
# 导入 Google Generative AI 客户端
from google.genai import Client # 修正：应为 vertexai.preview.generative_models.GenerativeModel 或类似

# 从 chase_sql 子模块导入常量
from .chase_sql import chase_constants

# 假设 `BQ_PROJECT_ID` 已在环境中设置。有关更多详细信息，请参阅 `data_agent` README。
project = os.getenv("BQ_PROJECT_ID", None)
# 从环境变量获取区域，默认为 'us-central1'
region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

# 注意：这里的 Client 初始化方式可能需要根据实际使用的 genai 或 vertexai 版本调整
# 建议使用 vertexai.preview.generative_models.GenerativeModel
try:
    # 尝试使用 Vertex AI 初始化 LLM 客户端
    from vertexai.preview.generative_models import GenerativeModel
    llm_client = GenerativeModel("gemini-1.5-flash-exp") # 使用 agent 中定义的模型
except ImportError:
    print("警告：无法导入 Vertex AI GenerativeModel。将尝试使用 google.genai.Client。")
    # 回退到 google.genai.Client，但这可能与 ADK 的集成方式不完全匹配
    # 需要确保 google-genai 库已安装且配置正确
    # llm_client = Client(vertexai=True, project=project, location=region) # 这行可能需要调整
    llm_client = None # 暂时设为 None，避免启动时出错

# 设置 BigQuery 返回的最大行数
MAX_NUM_ROWS = 80


# 全局变量用于存储数据库设置和 BigQuery 客户端
database_settings = None
bq_client = None

# 获取 BigQuery 客户端的函数
def get_bq_client():
    """获取 BigQuery 客户端。"""
    global bq_client
    # 如果客户端尚未初始化
    if bq_client is None:
        # 使用环境变量中的项目 ID 初始化 BigQuery 客户端
        bq_client = bigquery.Client(project=get_env_var("BQ_PROJECT_ID"))
    return bq_client


# 获取数据库设置的函数
def get_database_settings():
    """获取数据库设置。"""
    global database_settings
    # 如果设置尚未加载
    if database_settings is None:
        # 更新数据库设置
        database_settings = update_database_settings()
    return database_settings


# 更新数据库设置的函数
def update_database_settings():
    """更新数据库设置。"""
    global database_settings
    # 获取 BigQuery schema
    ddl_schema = get_bigquery_schema(
        get_env_var("BQ_DATASET_ID"),     # 数据集 ID
        client=get_bq_client(),           # BigQuery 客户端
        project_id=get_env_var("BQ_PROJECT_ID"), # 项目 ID
    )
    # 构建数据库设置字典
    database_settings = {
        "bq_project_id": get_env_var("BQ_PROJECT_ID"), # BigQuery 项目 ID
        "bq_dataset_id": get_env_var("BQ_DATASET_ID"), # BigQuery 数据集 ID
        "bq_ddl_schema": ddl_schema,                 # BigQuery DDL schema
        # 包含 ChaseSQL 特定的常量
        **chase_constants.chase_sql_constants_dict,
    }
    return database_settings


# 获取 BigQuery schema 的函数
好的，我会将您提供的代码注释、prompt 和参数值转换成中文版，并提供详细的中文注释，同时保留必要的专业术语和变量名称。

---

import datetime # 导入 datetime 模块，用于处理日期和时间
import logging # 导入 logging 模块，用于记录日志信息
import re # 导入 re 模块，用于正则表达式操作
from google.cloud import bigquery # 从 google.cloud 库导入 bigquery 模块，用于与 BigQuery 交互
import pandas as pd # 导入 pandas 库，并使用别名 pd，用于数据处理和分析，特别是 DataFrame 操作

# 定义常量
MAX_NUM_ROWS = 100 # 定义常量 MAX_NUM_ROWS，限制从 BigQuery 返回的最大行数

# 初始化 BigQuery 客户端的全局变量
bq_client = None

def get_bq_client():
    """获取 BigQuery 客户端单例。"""
    global bq_client
    if bq_client is None:
        # 如果客户端尚未初始化，则创建一个新的 BigQuery 客户端实例
        # 注意：这里可能需要配置项目 ID，例如 bigquery.Client(project='your-project-id')
        bq_client = bigquery.Client()
    return bq_client

def get_bigquery_schema(dataset_id, client=None, project_id=None):
    """检索 BigQuery 数据集的模式，并生成包含示例值的数据定义语言（DDL）语句。

    Args:
        dataset_id (str): BigQuery 数据集的 ID (例如, 'my_dataset')。
        client (bigquery.Client, optional): 一个 BigQuery 客户端对象。如果未提供，则会创建一个新的客户端。默认为 None。
        project_id (str, optional): 您的 Google Cloud 项目的 ID。如果 client 为 None，则需要此 ID 来创建客户端。默认为 None。

    Returns:
        str: 一个包含生成的 DDL 语句及示例数据的字符串。
    """

    if client is None:
        # 如果没有提供 BigQuery 客户端，则使用项目 ID 创建一个新的客户端
        client = bigquery.Client(project=project_id)

    # 创建数据集引用对象
    # dataset_ref = client.dataset(dataset_id) # 另一种创建方式
    dataset_ref = bigquery.DatasetReference(project_id, dataset_id)

    ddl_statements = "" # 初始化 DDL 语句字符串

    # 遍历数据集中的所有表
    for table in client.list_tables(dataset_ref):
        # 创建表引用对象
        table_ref = dataset_ref.table(table.table_id)
        # 获取表对象，包含表的元数据和模式信息
        table_obj = client.get_table(table_ref)

        # 检查表类型，如果不是物理表（TABLE），则跳过（例如视图 VIEW）
        if table_obj.table_type != "TABLE":
            continue

        # 开始构建 CREATE OR REPLACE TABLE DDL 语句
        # 使用反引号 ` ` 来包围表引用，这是 BigQuery 的标准做法
        ddl_statement = f"CREATE OR REPLACE TABLE `{table_ref}` (\n"

        # 遍历表模式中的每个字段（列）
        for field in table_obj.schema:
            # 添加字段名和字段类型
            ddl_statement += f"  `{field.name}` {field.field_type}"
            # 如果字段模式是 REPEATED（数组），则添加 ARRAY 关键字
            if field.mode == "REPEATED":
                ddl_statement += " ARRAY"
            # 如果字段有描述信息，则添加 COMMENT
            if field.description:
                # 注意：描述中的特殊字符可能需要转义，但这里简化处理
                ddl_statement += f" COMMENT '{field.description}'"
            # 每个字段定义后添加逗号和换行符
            ddl_statement += ",\n"

        # 移除最后一个字段定义后的逗号和换行符，并添加右括号和分号
        ddl_statement = ddl_statement[:-2] + "\n);\n\n"

        # 尝试获取表示例数据（最多5行）并转换为 Pandas DataFrame
        try:
            # 使用 list_rows 获取数据，并通过 to_dataframe() 转换为 DataFrame
            rows = client.list_rows(table_ref, max_results=5).to_dataframe()
        except Exception as e:
            # 如果获取数据时出错（例如权限问题、表不存在等），记录错误并继续处理下一个表
            print(f"获取表 {table_ref} 的示例数据时出错: {e}")
            rows = pd.DataFrame() # 创建一个空的 DataFrame

        # 如果 DataFrame 不为空，则添加 INSERT INTO 语句作为示例值
        if not rows.empty:
            ddl_statement += f"-- 表 `{table_ref}` 的示例值:\n"
            # 遍历 DataFrame 的每一行
            for _, row in rows.iterrows():
                ddl_statement += f"INSERT INTO `{table_ref}` VALUES\n"
                example_row_str = "(" # 开始构建值列表
                # 遍历行中的每个值
                for value in row.values: # row 是一个 pandas Series 对象
                    # 根据值的类型进行格式化
                    if isinstance(value, str):
                        # 字符串需要用单引号包围，注意处理字符串内的单引号（此处简化，未处理）
                        # BigQuery 推荐使用 ''' 或 """ 来包围可能包含引号的字符串，或者使用 r''
                        # 更安全的处理是使用参数化查询或库提供的转义函数
                        escaped_value = value.replace("'", "\\'") # 基本的单引号转义
                        example_row_str += f"'{escaped_value}',"
                    elif value is None or pd.isna(value): # 处理 None 或 Pandas 的 NA 值
                        # 空值表示为 NULL
                        example_row_str += "NULL,"
                    elif isinstance(value, (list, tuple, np.ndarray)): # 处理数组/列表类型
                        # 将数组转换为 BigQuery 数组语法的字符串表示
                        # 例如：['a', 'b'] -> "['a', 'b']" 或 ARRAY<STRING>['a', 'b']
                        # 这里简化处理，直接使用 Python 的字符串表示，可能需要根据具体类型调整
                        # 对数组内的元素也需要进行类型判断和格式化
                        array_str = "["
                        for item in value:
                            if isinstance(item, str):
                                escaped_item = item.replace("'", "\\'")
                                array_str += f"'{escaped_item}',"
                            elif item is None or pd.isna(item):
                                array_str += "NULL,"
                            else: # 其他类型（数字、布尔等）
                                array_str += f"{item},"
                        if len(value) > 0:
                             array_str = array_str[:-1] # 移除最后一个逗号
                        array_str += "]"
                        example_row_str += f"{array_str},"
                    elif isinstance(value, datetime.date): # 处理日期类型
                        example_row_str += f"DATE('{value.isoformat()}')," # 格式化为 DATE 'YYYY-MM-DD'
                    elif isinstance(value, datetime.datetime): # 处理日期时间类型
                        example_row_str += f"TIMESTAMP('{value.isoformat()}')," # 格式化为 TIMESTAMP 'YYYY-MM-DD HH:MM:SS.ffffff[+HH:MM]'
                    else:
                        # 其他类型（如数字、布尔值）直接转换为字符串
                        example_row_str += f"{value},"
                # 移除最后一个值后面的逗号，并添加右括号和换行符
                example_row_str = example_row_str[:-1] + ");\n"
                ddl_statement += example_row_str
            ddl_statement += "\n" # 在 INSERT 语句块后添加一个空行

        # 将当前表的 DDL 语句和示例数据追加到总的 DDL 字符串中
        ddl_statements += ddl_statement

    # 返回包含所有表 DDL 和示例数据的完整字符串
    return ddl_statements


def initial_bq_nl2sql(
    question: str,
    tool_context: ToolContext,
) -> str:
    """根据自然语言问题生成初始的 BigQuery SQL 查询。

    Args:
        question (str): 自然语言问题。
        tool_context (ToolContext): 用于生成 SQL 查询的工具上下文对象，
                                    其中应包含数据库设置（如模式信息）。

    Returns:
        str: 用于回答问题的 BigQuery SQL 语句。
    """

    # 定义用于生成 SQL 的 Prompt 模板
    prompt_template = """
您是一位 BigQuery SQL 专家，任务是通过生成 GoogleSql 方言的 SQL 查询来回答用户关于 BigQuery 表的问题。您的任务是编写一个 BigQuery SQL 查询，该查询在回答以下问题的同时，利用提供的上下文信息。

**指南:**

- **表引用:** 在 SQL 语句中始终使用带有数据库前缀的完整表名。表应使用完全限定名称引用，并用反引号（`）括起来，例如 `project_name.dataset_name.table_name`。表名区分大小写。
- **连接 (Joins):** 尽量少地连接表。连接表时，请确保所有连接列具有相同的数据类型。分析提供的数据库和表模式，以理解列和表之间的关系。
- **聚合 (Aggregations):** 在 `GROUP BY` 子句中使用 `SELECT` 语句中所有未聚合的列。
- **SQL 语法:** 返回语法和语义上正确的 BigQuery SQL，并具有正确的关联映射（即 project_id、owner、table 和 column 的关系）。在需要时，使用 SQL 的 `AS` 语句为表列甚至表临时分配新名称。始终将子查询和联合查询括在括号中。
- **列的使用:** *仅* 使用表模式 (Table Schema) 中提到的列名 (column_name)。*不要* 使用任何其他列名。仅将表模式中提到的 `column_name` 与表模式下指定的 `table_name` 相关联。
- **过滤 (FILTERS):** 您应该有效地编写查询，以减少并最小化要返回的总行数。例如，您可以在 SQL 查询中使用过滤器（如 `WHERE`、`HAVING` 等）或聚合函数（如 'COUNT'、'SUM' 等）。
- **限制行数 (LIMIT ROWS):** 返回的最大行数应小于 {MAX_NUM_ROWS}。

**模式 (Schema):**

数据库结构由以下表模式定义（可能包含示例行）：

```
{SCHEMA}
```

**自然语言问题:**

```
{QUESTION}
```

**逐步思考 (Think Step-by-Step):** 仔细考虑上述模式、问题、指南和最佳实践，以生成正确的 BigQuery SQL。
"""

    # 从工具上下文中获取数据库设置中的 DDL 模式信息
    # 假设 tool_context.state 结构为: {'database_settings': {'bq_ddl_schema': '...'}}
    ddl_schema = tool_context.state["database_settings"]["bq_ddl_schema"]

    # 使用模式信息和问题格式化 Prompt 模板
    prompt = prompt_template.format(
        MAX_NUM_ROWS=MAX_NUM_ROWS, # 将最大行数常量插入模板
        SCHEMA=ddl_schema,        # 将 DDL 模式插入模板
        QUESTION=question         # 将用户问题插入模板
    )

    # 调用大语言模型 (LLM) 客户端生成内容
    # 假设 llm_client 是一个已经初始化的、可以调用 Gemini 模型的客户端对象
    response = llm_client.models.generate_content(
        model="gemini-1.5-flash", # 指定使用的模型
        contents=prompt,         # 提供格式化后的 Prompt
        generation_config={"temperature": 0.1}, # 配置生成参数，temperature=0.1 表示更确定的输出
        # safety_settings=... # 可能需要配置安全设置
    )

    # 从 LLM 响应中提取生成的 SQL 文本
    sql = response.text
    # 清理 SQL 文本：移除常见的代码块标记 ```sql 和 ```，并去除首尾空白
    if sql:
        sql = sql.replace("```sql", "").replace("```", "").strip()

    # 打印生成的 SQL（用于调试或日志记录）
    print("\n sql:", sql)

    # 将生成的 SQL 查询存储在工具上下文的状态中，以便后续步骤使用
    tool_context.state["sql_query"] = sql

    # 返回生成的 SQL 查询字符串
    return sql


def run_bigquery_validation(
    sql_string: str,
    tool_context: ToolContext,
) -> dict: # 返回类型修改为 dict，以包含结果或错误信息
    """验证 BigQuery SQL 语法和功能。

    此函数通过尝试在 BigQuery 中以 dry-run 模式（或实际执行模式，根据代码逻辑判断）
    执行提供的 SQL 字符串来对其进行验证。它执行以下检查：

    1.  **SQL 清理:** 使用 `cleanup_sql` 函数预处理 SQL 字符串。
    2.  **DML/DDL 限制:** 拒绝任何包含 DML（数据操作语言）或 DDL（数据定义语言）
        语句（例如 UPDATE, DELETE, INSERT, CREATE, ALTER）的 SQL 查询，以确保只读操作。
    3.  **语法和执行:** 将清理后的 SQL 发送到 BigQuery 进行验证（实际执行）。
        如果查询语法正确且可执行，它将检索结果。
    4.  **结果分析:** 检查查询是否产生任何结果。如果是，则格式化结果集的前几行以供检查。

    Args:
        sql_string (str): 要验证的 SQL 查询字符串。
        tool_context (ToolContext): 用于验证的工具上下文。

    Returns:
        dict: 包含验证结果的字典。结构如下：
             - {'query_result': [...]} 如果查询有效并返回数据，'...' 是一个包含结果行的列表（每行是一个字典）。
             - {'error_message': "Valid SQL. Query executed successfully (no results)."} 如果查询有效但未返回数据。
             - {'error_message': "Invalid SQL: ..."} 如果查询无效，'...' 是来自 BigQuery 的错误消息。
             - {'error_message': "Invalid SQL: Contains disallowed DML/DDL operations."} 如果包含不允许的操作。
    """

    def cleanup_sql(sql_string):
        """处理 SQL 字符串以获得可打印且有效的 SQL 字符串。"""

        # 1. 移除转义双引号的反斜杠（例如 \\" -> "）
        sql_string = sql_string.replace('\\"', '"')

        # 2. 移除换行符前的反斜杠（修复关键问题） (例如 \\\n -> \n)
        sql_string = sql_string.replace("\\\n", "\n")

        # 3. 替换转义的单引号 (例如 \\' -> ')
        sql_string = sql_string.replace("\\'", "'")

        # 4. 替换转义的换行符（那些前面没有反斜杠的 \n）(例如 \\n -> \n)
        sql_string = sql_string.replace("\\n", "\n")

        # 5. 如果 SQL 语句中不包含 limit 子句（不区分大小写），则添加 limit 子句
        if "limit" not in sql_string.lower():
            sql_string = sql_string + " limit " + str(MAX_NUM_ROWS)

        return sql_string

    # 记录开始验证的 SQL
    logging.info("正在验证 SQL: %s", sql_string)
    # 清理 SQL 字符串
    sql_string = cleanup_sql(sql_string)
    # 记录清理后的 SQL
    logging.info("正在验证 SQL (清理后): %s", sql_string)

    # 初始化最终结果字典
    final_result = {"query_result": None, "error_message": None}

    # 更严格的 BigQuery 检查 - 禁止 DML 和 DDL 操作
    # 使用正则表达式搜索（不区分大小写）常见的 DML/DDL 关键字
    if re.search(
        r"(?i)\b(update|delete|drop|insert|create|alter|truncate|merge)\b", sql_string
    ):
        # 如果找到不允许的操作，设置错误消息并返回
        final_result["error_message"] = (
            "无效 SQL: 包含不允许的 DML/DDL 操作。"
        )
        return final_result

    try:
        # 获取 BigQuery 客户端并执行查询
        query_job = get_bq_client().query(sql_string)
        # 等待查询完成并获取结果迭代器
        results = query_job.result()

        # 检查结果中是否有模式信息（即查询是否返回了列）
        if results.schema:
            # 将 BigQuery RowIterator 转换为字典列表
            # 同时处理日期类型，将其格式化为 'YYYY-MM-DD' 字符串
            rows = [
                {
                    # 遍历每一行的键值对
                    key: (
                        # 如果值是日期类型，格式化为字符串
                        value.strftime("%Y-%m-%d")
                        if isinstance(value, datetime.date)
                        # 否则保持原样
                        else value
                    )
                    for (key, value) in row.items() # row.items() 返回 (列名, 值) 的元组
                }
                # 从结果迭代器中获取每一行 (row 是一个 google.cloud.bigquery.table.Row)
                for row in results
            ][
                :MAX_NUM_ROWS # 限制最终返回的行数
            ]
            # 将查询结果存储在 final_result 字典中
            final_result["query_result"] = rows

            # 同时将结果存储在工具上下文的状态中，供后续使用
            tool_context.state["query_result"] = rows

        else:
            # 如果查询成功执行但没有返回任何行
            final_result["error_message"] = (
                "有效 SQL。查询成功执行（无结果）。"
            )

    # 捕获 BigQuery 执行期间可能发生的任何异常
    except Exception as e:
        # 将异常信息格式化为错误消息
        final_result["error_message"] = f"无效 SQL: {e}"

    # 打印最终验证结果（用于调试或日志记录）
    print("\n run_bigquery_validation final_result: \n", final_result)

    # 返回包含结果或错误的字典
    return final_result


