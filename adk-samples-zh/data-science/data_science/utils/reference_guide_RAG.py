
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


import os # 导入 os 模块，用于路径操作和环境变量
import pandas as pd # 导入 pandas 库，用于数据处理（虽然在此脚本中未直接使用其数据处理功能）
from google.cloud import bigquery # 导入 BigQuery 客户端库
from pathlib import Path # 导入 Path 对象，用于更方便地处理文件路径
from dotenv import load_dotenv # 导入 load_dotenv 函数，用于加载 .env 文件

# 定义 .env 文件的路径
# Path(__file__) 获取当前脚本文件的路径
# .parent 获取父目录（utils）
# .parent.parent 获取上上级目录（data_science）
# .parent 获取上上上级目录（项目根目录）
# / ".env" 将根目录与 .env 文件名拼接起来
env_file_path = Path(__file__).parent.parent.parent / ".env"
print(f".env 文件路径: {env_file_path}") # 打印 .env 文件路径

# 从指定的 .env 文件加载环境变量
load_dotenv(dotenv_path=env_file_path)


def load_csv_to_bigquery(project_id, dataset_name, table_name, csv_filepath):
    """将 CSV 文件加载到 BigQuery 表中。

    Args:
        project_id (str): Google Cloud 项目的 ID。
        dataset_name (str): BigQuery 数据集的名称。
        table_name (str): BigQuery 表的名称。
        csv_filepath (str): CSV 文件的路径。
    """

    # 初始化 BigQuery 客户端，指定项目 ID
    client = bigquery.Client(project=project_id)

    # 创建数据集引用和表引用
    dataset_ref = client.dataset(dataset_name)
    table_ref = dataset_ref.table(table_name)

    # 配置加载作业
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV, # 指定源文件格式为 CSV
        skip_leading_rows=1,  # 跳过 CSV 文件中的标题行
        autodetect=True,  # 自动检测表的模式（列名和类型）
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE, # 指定写入模式为覆盖表（如果表已存在）
                                                                   # 可选值: WRITE_APPEND (追加), WRITE_EMPTY (仅当表为空时写入)
    )

    # 以二进制读取模式打开 CSV 文件
    with open(csv_filepath, "rb") as source_file:
        # 从文件加载数据到 BigQuery 表
        job = client.load_table_from_file(
            source_file, table_ref, job_config=job_config
        )

    # 等待加载作业完成
    job.result()

    # 打印加载结果信息
    print(
        f"已加载 {job.output_rows} 行数据到表"
        f" {project_id}.{dataset_name}.{table_name}"
    )


def create_dataset_if_not_exists(project_id, dataset_name):
    """如果 BigQuery 数据集不存在，则创建它。

    Args:
        project_id (str): Google Cloud 项目的 ID。
        dataset_name (str): BigQuery 数据集的名称。
    """
    # 初始化 BigQuery 客户端
    client = bigquery.Client(project=project_id)
    # 构建完整的数据集 ID
    dataset_id = f"{project_id}.{dataset_name}"

    try:
        # 尝试获取数据集，如果存在则不执行任何操作
        client.get_dataset(dataset_id)  # 发起 API 请求
        print(f"数据集 {dataset_id} 已存在")
    except Exception as e: # 捕获所有异常，更精确的是捕获 google.cloud.exceptions.NotFound
        # 如果获取数据集时出错（通常是 NotFound），则创建数据集
        print(f"数据集 {dataset_id} 不存在或获取时出错 ({e})，正在创建...")
        # 创建数据集对象
        dataset = bigquery.Dataset(dataset_id)
        # 设置数据集的位置（例如："US", "EU", "asia-northeast1"）
        dataset.location = "US"  # 可以根据需要修改
        # 创建数据集，设置超时时间
        dataset = client.create_dataset(dataset, timeout=30)  # 发起 API 请求
        print(f"已创建数据集 {dataset.project}.{dataset.dataset_id}")


def main():
    """主函数，将 CSV 文件加载到 BigQuery。"""

    # 打印当前工作目录（用于调试路径问题）
    current_directory = os.getcwd()
    print(f"当前工作目录: {current_directory}")

    # 从环境变量获取项目 ID
    project_id = os.getenv("BQ_PROJECT_ID")
    # 如果环境变量未设置，则抛出错误
    if not project_id:
        raise ValueError("环境变量 BQ_PROJECT_ID 未设置。")

    # 定义数据集名称和 CSV 文件路径
    dataset_name = "forecasting_sticker_sales" # 贴纸销售预测数据集
    # 假设脚本从项目根目录运行，或者已正确设置 Python 路径
    train_csv_filepath = "data_science/utils/data/train.csv" # 训练数据文件路径
    test_csv_filepath = "data_science/utils/data/test.csv"   # 测试数据文件路径

    # 检查 CSV 文件是否存在
    if not Path(train_csv_filepath).is_file():
        raise FileNotFoundError(f"训练数据文件未找到: {train_csv_filepath} (相对于 {current_directory})")
    if not Path(test_csv_filepath).is_file():
        raise FileNotFoundError(f"测试数据文件未找到: {test_csv_filepath} (相对于 {current_directory})")

    # 如果数据集不存在，则创建它
    print("正在检查并创建数据集...")
    create_dataset_if_not_exists(project_id, dataset_name)

    # 加载训练数据
    print("正在加载训练数据表...")
    load_csv_to_bigquery(project_id, dataset_name, "train", train_csv_filepath)

    # 加载测试数据
    print("正在加载测试数据表...")
    load_csv_to_bigquery(project_id, dataset_name, "test", test_csv_filepath)

    print("数据加载完成。")


if __name__ == "__main__":
    # 如果脚本作为主程序运行，则调用 main 函数
    main()


