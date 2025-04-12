
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

import time # 导入 time 模块，用于计时和暂停
import os # 导入 os 模块，用于与操作系统交互，如获取环境变量
from google.cloud import bigquery # 从 google.cloud 库导入 bigquery 模块
from vertexai import rag # 从 vertexai 库导入 rag 模块，用于与 RAG 服务交互


def check_bq_models(dataset_id: str) -> str:
    """列出 BigQuery 数据集中的模型，并将它们作为字符串返回。

    Args:
        dataset_id (str): BigQuery 数据集的 ID (例如 "project_id.dataset_id")。
                           注意：通常只需要 "dataset_id"，项目 ID 会从客户端配置中获取，
                           或者如果跨项目访问，则需要提供 "project_id.dataset_id"。
                           调用者需要确保格式正确。

    Returns:
        str: 包含字典列表的字符串表示形式，每个字典包含指定数据集中模型的 'name' 和 'type'。
             如果找不到模型，则返回空列表的字符串 "[]"。
             如果发生错误，则返回错误信息字符串。
    """

    try:
        # 创建 BigQuery 客户端
        # 客户端会自动使用配置的默认项目 ID，或者可以通过 bigquery.Client(project='your-project-id') 指定
        client = bigquery.Client()

        # 获取指定数据集中的模型迭代器
        models = client.list_models(dataset_id)
        model_list = []  # 初始化一个空列表来存储模型信息

        print(f"数据集 '{dataset_id}' 中包含的模型:") # 打印日志信息
        # 遍历模型迭代器
        for model in models:
            model_id = model.model_id # 获取模型 ID
            model_type = model.model_type # 获取模型类型
            # 将模型信息添加到列表中
            model_list.append({"name": model_id, "type": model_type})

        # 将模型列表转换为字符串表示形式并返回
        return str(model_list)

    except Exception as e:
        # 如果在过程中发生任何异常，捕获异常并返回错误信息字符串
        return f"发生错误: {str(e)}"


def execute_bqml_code(bqml_code: str, project_id: str, dataset_id: str) -> str:
    """
    执行 BigQuery ML 代码。

    Args:
        bqml_code (str): 要执行的 BigQuery ML 查询语句。
        project_id (str): Google Cloud 项目 ID。
        dataset_id (str): BigQuery 数据集 ID (用于日志或上下文，查询本身应包含完整路径)。

    Returns:
        str: 执行结果的消息。成功时可能是 "BigQuery ML code executed successfully."
             或包含结果摘要的字符串；失败时是错误信息。
    """

    # timeout_seconds = 1500 # 超时时间（秒），当前注释掉了

    # 创建 BigQuery 客户端，指定项目 ID
    client = bigquery.Client(project=project_id)

    try:
        # 提交 BQML 查询作业
        query_job = client.query(bqml_code)
        # 记录作业开始时间
        start_time = time.time()

        # 循环等待作业完成
        while not query_job.done():
            # 计算已用时间
            elapsed_time = time.time() - start_time
            # 检查是否超时（当前注释掉了）
            # if elapsed_time > timeout_seconds:
            #     return (
            #         "超时：BigQuery 作业未在"
            #         f" {timeout_seconds} 秒内完成。作业 ID：{query_job.job_id}"
            #     )

            # 打印作业状态和已用时间
            print(
                f"查询作业状态: {query_job.state}, 已用时间:"
                f" {elapsed_time:.2f} 秒。作业 ID: {query_job.job_id}"
            )
            # 短暂暂停，避免过于频繁地检查状态
            time.sleep(5)

        # 检查作业是否出错
        if query_job.error_result:
            return f"执行 BigQuery ML 代码时出错: {query_job.error_result}"

        # 检查作业是否有异常
        if query_job.exception():
            return f"BigQuery ML 执行期间发生异常: {query_job.exception()}"

        # 作业成功完成，获取结果
        results = query_job.result()
        # 检查是否有结果行
        if results.total_rows > 0:
            result_string = ""
            # 遍历结果行
            for row in results:
                # 将每一行转换为字典并附加到结果字符串
                result_string += str(dict(row.items())) + "\n"
            # 返回成功消息和结果摘要
            return f"BigQuery ML 代码执行成功。结果:\n{result_string}"
        else:
            # 如果没有结果行，返回成功消息
            return "BigQuery ML 代码执行成功。"

    except Exception as e:
        # 捕获执行期间的其他异常
        return f"发生错误: {str(e)}"


def rag_response(query: str) -> str:
    """从 RAG 语料库中检索上下文相关的信息。

    Args:
        query (str): 要在语料库中搜索的查询字符串。

    Returns:
        str: 包含从语料库中检索到的信息的响应字符串。
             注意：原函数返回类型是 vertexai.rag.RagRetrievalQueryResponse，
             这里改为 str 以便直接用作 Agent 工具的输出。将响应对象转换为字符串。
    """
    # 从环境变量中获取 RAG 语料库名称
    corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")
    if not corpus_name:
        return "错误：环境变量 BQML_RAG_CORPUS_NAME 未设置。"

    # 配置 RAG 检索参数
    rag_retrieval_config = rag.RagRetrievalConfig(
        top_k=3,  # 可选：返回最相关的 top_k 个结果，默认为 3
        # filter=rag.Filter(vector_distance_threshold=0.5),  # 可选：根据向量距离阈值过滤结果
    )
    try:
        # 调用 RAG 检索查询 API
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_name, # 指定要查询的语料库
                )
            ],
            text=query, # 要查询的文本
            rag_retrieval_config=rag_retrieval_config, # 传入检索配置
        )
        # 将 RAG 响应对象转换为字符串并返回
        return str(response)
    except Exception as e:
        # 捕获 RAG 查询期间的异常
        return f"RAG 查询时发生错误: {str(e)}"


