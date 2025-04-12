
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

# 导入 BigQuery 客户端库
from google.cloud import bigquery

# 从 brand_search_optimization 的共享库导入常量
from brand_search_optimization.shared_libraries import constants

# 从常量中获取配置信息
PROJECT = constants.PROJECT           # Google Cloud 项目 ID
TABLE_ID = constants.TABLE_ID         # BigQuery 表 ID
LOCATION = constants.LOCATION       # Google Cloud 位置
DATASET_ID = constants.DATASET_ID     # BigQuery 数据集 ID
# TABLE_ID = constants.TABLE_ID       # 重复定义，可以移除

# 初始化 BigQuery 客户端，指定项目 ID
client = bigquery.Client(project=PROJECT)

# 定义要插入的示例数据
data_to_insert = [
    {
        "Title": "儿童慢跑鞋",
        "Description": "舒适且支撑性强的跑鞋，适合活泼的孩子。透气网眼鞋面保持脚部凉爽，耐用的外底提供出色的抓地力。",
        "Attributes": "尺码: 10 幼儿, 颜色: 蓝色/绿色",
        "Brand": "BSOAgentTestBrand",  # 用于测试的品牌名称
    },
    {
        "Title": "闪光运动鞋",
        "Description": "有趣时尚的运动鞋，带有孩子们会喜欢的闪光功能。支撑性强，舒适适合全天玩耍。",
        "Attributes": "尺码: 13 幼儿, 颜色: 银色",
        "Brand": "BSOAgentTestBrand",
    },
    {
        "Title": "校鞋",
        "Description": "多功能舒适的鞋子，非常适合在学校日常穿着。耐用的结构，具有支撑性设计。",
        "Attributes": "尺码: 12 学龄前, 颜色: 黑色",
        "Brand": "BSOAgentTestBrand",
    },
]


def create_dataset_if_not_exists():
    """如果 BigQuery 数据集不存在，则创建它。"""
    # 构建 BigQuery 客户端对象。
    # 构造完整的数据集 ID（项目名.数据集名）
    dataset_id = f"{client.project}.{DATASET_ID}"
    # 创建数据集对象
    dataset = bigquery.Dataset(dataset_id)
    # 设置数据集位置
    dataset.location = "US"
    # 删除已存在的数据集（如果存在），包括其内容，忽略未找到错误。
    client.delete_dataset(
        dataset_id, delete_contents=True, not_found_ok=True
    )  # 发起 API 请求。
    # 创建新的数据集
    dataset = client.create_dataset(dataset)  # 发起 API 请求。
    print(f"已创建数据集 {client.project}.{dataset.dataset_id}")
    return dataset


def populate_bigquery_table():
    """使用提供的数据填充 BigQuery 表。"""
    # 创建或获取数据集引用
    dataset_ref = create_dataset_if_not_exists()
    if not dataset_ref:
        print("数据集创建或获取失败，无法填充表格。")
        return

    # 根据您的 CREATE TABLE 语句定义表结构 (schema)
    schema = [
        bigquery.SchemaField("Title", "STRING", description="产品标题"),
        bigquery.SchemaField("Description", "STRING", description="产品描述"),
        bigquery.SchemaField("Attributes", "STRING", description="产品属性，如尺码、颜色"),
        bigquery.SchemaField("Brand", "STRING", description="产品品牌"),
    ]
    # 构造完整的表 ID（项目名.数据集名.表名）
    table_id = f"{PROJECT}.{DATASET_ID}.{TABLE_ID}"
    # 创建表对象
    table = bigquery.Table(table_id, schema=schema)
    # 删除已存在的表（如果存在），忽略未找到错误。
    client.delete_table(table_id, not_found_ok=True)  # 发起 API 请求。
    print(f"已删除表 '{table_id}'.")
    # 创建新的表
    table = client.create_table(table)  # 发起 API 请求。
    print(
        f"已创建表 {PROJECT}.{table.dataset_id}.{table.table_id}"
    )

    # 将数据以 JSON 格式插入到表中
    errors = client.insert_rows_json(table=table, json_rows=data_to_insert)

    # 检查插入过程中是否发生错误
    if not errors:
        print(
            f"成功将 {len(data_to_insert)} 行插入到 {PROJECT}.{DATASET_ID}.{TABLE_ID}"
        )
    else:
        print("插入行时发生错误:")
        for error in errors:
            print(error)


# 如果此脚本作为主程序运行
if __name__ == "__main__":
    # 调用函数填充 BigQuery 表
    populate_bigquery_table()
    # 打印提示信息，告知用户如何在 customiztion.md 文件中找到添加 BQ 表权限的说明
    print(
        "\n--- 如何向 BQ 表添加权限的说明在 customiztion.md 文件中 ---"
    )


