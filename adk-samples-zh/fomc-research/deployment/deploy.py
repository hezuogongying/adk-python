
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

"""BigQuery 表创建脚本。"""

# 导入必要的库
import csv
from collections.abc import Sequence # 用于类型提示

# 从 absl 库导入 app 和 flags，用于处理命令行参数
from absl import app, flags
# 导入 Google Cloud BigQuery 客户端库
from google.cloud import bigquery
# 导入 google 异常处理库
from google.cloud.exceptions import Conflict, GoogleCloudError, NotFound

# 定义命令行标志 (flags)
FLAGS = flags.FLAGS
# 定义 GCP 项目 ID 标志
flags.DEFINE_string("project_id", None, "GCP 项目 ID。")
# 定义 BigQuery 数据集 ID 标志
flags.DEFINE_string("dataset_id", None, "BigQuery 数据集 ID。")
# 定义数据文件路径标志
flags.DEFINE_string("data_file", None, "数据文件的路径。")
# 定义数据集位置标志，默认为 us-central1
flags.DEFINE_string("location", "us-central1", "数据集的位置。")
# 将 project_id 和 dataset_id 标记为必需标志
flags.mark_flags_as_required(["project_id", "dataset_id"])


def create_bigquery_dataset(
    client: bigquery.Client,
    dataset_id: str,
    location: str,
    description: str = None,
    exists_ok: bool = True,
) -> bigquery.Dataset:
    """创建一个新的 BigQuery 数据集。

    参数:
        client: 一个 BigQuery 客户端对象。
        dataset_id: 要创建的数据集的 ID。
        location: 数据集的位置 (例如, "US", "EU")。
            默认为 "US"。
        description: 数据集的可选描述。
        exists_ok: 如果为 True，则在数据集已存在时不要抛出异常。

    返回:
        新创建的 bigquery.Dataset 对象。

    抛出异常:
        google.cloud.exceptions.Conflict: 如果数据集已存在且 exists_ok 为 False。
        Exception: 对于任何其他错误。
    """

    # 创建数据集引用
    dataset_ref = bigquery.DatasetReference(client.project, dataset_id)
    # 创建数据集对象
    dataset = bigquery.Dataset(dataset_ref)
    # 设置数据集位置
    dataset.location = location
    # 如果提供了描述，则设置描述
    if description:
        dataset.description = description

    try:
        # 尝试创建数据集
        dataset = client.create_dataset(dataset)
        print(f"数据集 {dataset.dataset_id} 已在 {dataset.location} 创建。")
        return dataset
    except Conflict as e:
        # 处理数据集已存在的冲突
        if exists_ok:
            print(f"数据集 {dataset.dataset_id} 已存在。")
            # 如果允许存在，则获取并返回现有数据集
            return client.get_dataset(dataset_ref)
        else:
            # 如果不允许存在，则抛出冲突异常
            raise e


def create_bigquery_table(
    client: bigquery.Client,
    dataset_id: str,
    table_id: str,
    schema: list[bigquery.SchemaField],
    description: str = None,
    exists_ok: bool = False,
) -> bigquery.Table:
    """创建一个新的 BigQuery 表。

    参数:
        client: 一个 BigQuery 客户端对象。
        dataset_id: 包含该表的数据集的 ID。
        table_id: 要创建的表的 ID。
        schema: 定义表结构的 bigquery.SchemaField 对象列表。
        description: 表的可选描述。
        exists_ok: 如果为 True，则在表已存在时不要抛出异常。

    返回:
        新创建的 bigquery.Table 对象。

    抛出异常:
        ValueError: 如果 schema 为空。
        google.cloud.exceptions.Conflict: 如果表已存在且 exists_ok 为 False。
        google.cloud.exceptions.NotFound: 如果数据集不存在。
        Exception: 对于任何其他错误。
    """

    # 检查 schema 是否为空
    if not schema:
        raise ValueError("Schema 不能为空。")

    # 创建表引用
    table_ref = bigquery.TableReference(
        bigquery.DatasetReference(client.project, dataset_id), table_id
    )
    # 创建表对象，并指定 schema
    table = bigquery.Table(table_ref, schema=schema)

    # 如果提供了描述，则设置描述
    if description:
        table.description = description

    try:
        # 尝试创建表
        table = client.create_table(table)
        print(
            f"表 {table.project}.{table.dataset_id}.{table.table_id} "
            "已创建。"
        )
        return table
    except Exception as e:  # pylint: disable=broad-exception-caught
        # 处理数据集未找到的错误
        if isinstance(e, NotFound):
            raise NotFound(
                f"在项目 {client.project} 中未找到数据集 {dataset_id}"
            ) from e
        # 处理表已存在的错误
        if "Already Exists" in str(e) and exists_ok:
            print(
                f"表 {table.project}.{table.dataset_id}.{table.table_id} "
                "已存在。"
            )
            # 如果允许存在，则获取并返回现有表
            return client.get_table(table_ref)
        else:
            # 对于其他错误，抛出通用异常
            # pylint: disable=broad-exception-raised
            raise Exception(f"创建表时出错: {e}") from e


def insert_csv_to_bigquery(
    client: bigquery.Client,
    table: bigquery.Table,
    csv_filepath: str,
    write_disposition: str = "WRITE_APPEND",
) -> None:
    """
    读取 CSV 文件并将其内容插入到 BigQuery 表中。

    参数:
        client: 一个 BigQuery 客户端对象。
        table: 一个 BigQuery 表对象。
        csv_filepath: CSV 文件的路径。
        write_disposition: 指定如果目标表已存在时发生的操作。
            有效值包括:
                - "WRITE_APPEND": 将数据追加到表中。
                - "WRITE_TRUNCATE": 覆盖表数据。
                - "WRITE_EMPTY": 仅当表为空时写入。
            默认为 "WRITE_APPEND"。

    抛出异常:
        FileNotFoundError: 如果 CSV 文件不存在。
        ValueError: 如果 write_disposition 无效。
        google.cloud.exceptions.GoogleCloudError: 如果在 BigQuery 操作期间发生任何其他错误。
    """

    # 验证 write_disposition 的值
    if write_disposition not in [
        "WRITE_APPEND",
        "WRITE_TRUNCATE",
        "WRITE_EMPTY",
    ]:
        raise ValueError(
            f"无效的 write_disposition: {write_disposition}。"
            "必须是 'WRITE_APPEND', 'WRITE_TRUNCATE', 或 'WRITE_EMPTY' 之一。"
        )

    try:
        # 打开并读取 CSV 文件
        with open(csv_filepath, "r", encoding="utf-8") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            rows_to_insert = list(csv_reader) # 将 CSV 行转换为字典列表

    except FileNotFoundError:
        # 处理文件未找到的错误
        raise FileNotFoundError(f"未找到 CSV 文件: {csv_filepath}") from None

    # 如果 CSV 文件为空，则不执行任何操作
    if not rows_to_insert:
        print("CSV 文件为空。无需插入。")
        return

    # 将行插入到 BigQuery 表中
    # row_ids 设置为 None，让 BigQuery 自动生成行 ID
    errors = client.insert_rows_json(
        table, rows_to_insert, row_ids=[None] * len(rows_to_insert)
    )

    # 检查插入过程中是否发生错误
    if errors:
        raise GoogleCloudError(
            f"插入行时发生错误: {errors}"
        )
    else:
        print(
            f"成功将 {len(rows_to_insert)} 行插入到 "
            f"{table.table_id}。"
        )


def main(argv: Sequence[str]) -> None:  # pylint: disable=unused-argument
    """主执行函数。"""
    # 定义表 schema
    data_table_name = "timeseries_data" # 表名
    data_table_schema = [ # 表结构
        bigquery.SchemaField("timeseries_code", "STRING", mode="REQUIRED"), # 时间序列代码，字符串，必需
        bigquery.SchemaField("date", "DATE", mode="REQUIRED"), # 日期，日期类型，必需
        bigquery.SchemaField("value", "FLOAT", mode="REQUIRED"), # 值，浮点数，必需
    ]
    data_table_description = "时间序列数据" # 表描述

    # 初始化 BigQuery 客户端
    client = bigquery.Client(project=FLAGS.project_id)

    # 创建 BigQuery 数据集
    dataset = create_bigquery_dataset(
        client,
        FLAGS.dataset_id,
        FLAGS.location,
        description="时间序列数据集",
    )

    # 创建 BigQuery 表
    data_table = create_bigquery_table(
        client,
        dataset.dataset_id,
        data_table_name,
        data_table_schema,
        data_table_description,
        exists_ok=True, # 如果表已存在，不报错
    )

    # 如果提供了数据文件路径，则将 CSV 数据插入表中
    if FLAGS.data_file:
        insert_csv_to_bigquery(client, data_table, FLAGS.data_file)

# 程序入口点
if __name__ == "__main__":
    # 运行主函数
    app.run(main)

