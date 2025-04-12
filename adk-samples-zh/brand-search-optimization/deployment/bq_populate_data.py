
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

"""定义品牌搜索优化 Agent 的工具"""

# 导入 BigQuery 客户端库
from google.cloud import bigquery
# 导入 ADK 工具上下文
from google.adk.tools import ToolContext

# 从上层目录的共享库导入常量
from ..shared_libraries import constants

# 在函数外部初始化 BigQuery 客户端
try:
    # 仅初始化一次客户端
    client = bigquery.Client()
except Exception as e:
    # 如果初始化失败，打印错误并设置客户端为 None
    print(f"初始化 BigQuery 客户端时出错: {e}")
    client = None


# 定义一个工具函数：为指定品牌获取产品详情
def get_product_details_for_brand(tool_context: ToolContext):
    """
    从 BigQuery 表中检索指定品牌的产品详情（标题、描述、属性和品牌）。

    参数:
        tool_context (ToolContext): 用于搜索的工具上下文 (使用 LIKE '%brand%' 查询)。

    返回:
        str: 包含产品详情的 markdown 表格，如果 BigQuery 客户端初始化失败，则返回错误消息。
             表格包括 '标题'、'描述'、'属性' 和 '品牌' 列。
             最多返回 3 个结果。

    示例:
        >>> get_product_details_for_brand(tool_context)
        '| 标题 | 描述 | 属性 | 品牌 |\\n|---|---|---|---|\\n| 耐克 Air Max | 舒适的跑鞋 | 尺码: 10, 颜色: 蓝色 | 耐克\\n| 耐克运动 T 恤 | 棉混纺，短袖 | 尺码: L, 颜色: 黑色 | 耐克\\n| 耐克 Pro 训练短裤 | 吸湿排汗面料 | 尺码: M, 颜色: 灰色 | 耐克\\n'
    """
    # 从 tool_context 获取用户输入的品牌名称
    brand = tool_context.user_content.parts[0].text
    # 检查客户端是否初始化失败
    if client is None:
        return "BigQuery 客户端初始化失败。无法执行查询。"

    # 构建 BigQuery SQL 查询语句
    # 使用 f-string 格式化查询，包含项目 ID、数据集 ID 和表 ID，并使用 LIKE 进行模糊匹配
    # 限制结果数量为 3
    query = f"""
        SELECT
            Title,                  -- 选择标题列
            Description,            -- 选择描述列
            Attributes,             -- 选择属性列
            Brand                   -- 选择品牌列
        FROM
            `{constants.PROJECT}.{constants.DATASET_ID}.{constants.TABLE_ID}` -- 指定完整的表名
        WHERE LOWER(brand) LIKE LOWER('%{brand}%') -- 使用 LIKE 进行不区分大小写的品牌模糊匹配
        LIMIT 3                     -- 限制返回结果数量为 3
    """
    # 定义查询作业配置，设置查询参数（尽管这里未使用参数化查询，但保留了结构）
    query_job_config = bigquery.QueryJobConfig(
        query_parameters=[
            # 定义一个名为 parameter1 的字符串类型参数，值为 brand (实际查询未使用)
            bigquery.ScalarQueryParameter("parameter1", "STRING", brand)
        ]
    )

    # 执行查询（未使用参数化配置，直接执行 query 字符串）
    # query_job = client.query(query, job_config=query_job_config) # 这行被注释掉了
    query_job = client.query(query)
    # 获取查询结果
    results = query_job.result()

    # 初始化 markdown 表格字符串，包含表头
    markdown_table = "| 标题 | 描述 | 属性 | 品牌 |\n"
    # 添加 markdown 表格的分隔行
    markdown_table += "|---|---|---|---|\n"

    # 遍历查询结果的每一行
    for row in results:
        # 获取标题，如果为空则使用 "N/A"
        title = row.Title if row.Title else "N/A"
        # 获取描述，如果为空则使用 "N/A"
        description = row.Description if row.Description else "N/A"
        # 获取属性，如果为空则使用 "N/A"
        attributes = row.Attributes if row.Attributes else "N/A"
        # 获取品牌名称（从原始输入获取，因为查询结果中的 Brand 列可能与输入不完全一致）
        # brand_name = brand # 这行似乎多余，因为 brand 变量在上面已经定义

        # 将行数据格式化为 markdown 表格的一行，并追加到表格字符串中
        markdown_table += (
            f"| {title} | {description} | {attributes} | {brand}\n"
        )

    # 返回最终生成的 markdown 表格字符串
    return markdown_table


