
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
from pathlib import Path # 导入 Path 对象，用于更方便地处理文件路径
from dotenv import load_dotenv, set_key # 导入 load_dotenv 和 set_key 函数，用于加载和设置 .env 文件
import vertexai # 导入 Vertex AI SDK
from vertexai import rag # 从 Vertex AI SDK 导入 RAG 相关功能


# 定义 .env 文件的路径 (与 create_bq_table.py 中类似)
env_file_path = Path(__file__).parent.parent.parent / ".env"
print(f".env 文件路径: {env_file_path}")

# 从指定的 .env 文件加载环境变量
load_dotenv(dotenv_path=env_file_path)

# 从环境变量获取项目 ID 和 RAG 语料库名称
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") # 项目 ID
if not PROJECT_ID:
    raise ValueError("环境变量 GOOGLE_CLOUD_PROJECT 未设置。")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1") # 区域，默认为 us-central1
corpus_name_from_env = os.getenv("BQML_RAG_CORPUS_NAME") # 已存在的语料库名称

# 定义 RAG 语料库的显示名称和数据源路径
display_name = "bqml_referenceguide_corpus" # 语料库的显示名称
# 数据源路径，这里指向一个 GCS 存储桶中的目录
# 可以是 GCS 路径 (gs://...) 或 Google Drive 链接
paths = [
    "gs://cloud-samples-data/adk-samples/data-science/bqml"
]

# 初始化 Vertex AI API（确保每个会话只初始化一次）
# 如果在其他地方已经初始化过，这里可以省略，但重复初始化通常是安全的
try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    print(f"Vertex AI SDK 已初始化，项目: {PROJECT_ID}, 位置: {LOCATION}")
except Exception as e:
    print(f"Vertex AI SDK 初始化失败: {e}")
    # 根据需要处理初始化失败的情况


def create_RAG_corpus():
    """创建 RAG 语料库。

    Returns:
        str: 创建的 RAG 语料库的资源名称 (例如 projects/.../ragCorpora/...)。
             如果创建失败，则返回 None。
    """
    print(f"尝试创建 RAG 语料库，显示名称: {display_name}")
    try:
        # 配置嵌入模型，例如使用 "text-embedding-004"
        # embedding_model_config = rag.RagEmbeddingModelConfig(
        #     vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
        #         # 使用Vertex AI Prediction Endpoint发布模型
        #         publisher_model="publishers/google/models/textembedding-gecko@003" # 使用推荐的嵌入模型 gecko
        #     )
        # )
        # 新版SDK可能简化了配置
        embedding_model_config = rag.EmbeddingModelConfig(
             publisher_model="publishers/google/models/text-embedding-004" # 或者 gecko@003
        )


        # 创建 RAG 语料库
        bqml_corpus = rag.create_corpus(
            display_name=display_name,
            # description="BQML 参考指南语料库", # 可选：添加描述
            embedding_model_config=embedding_model_config, # 应用嵌入模型配置
            # vector_db_config=backend_config, # 旧版参数，新版可能直接配置 embedding_model_config
        )
        print(f"RAG 语料库创建成功: {bqml_corpus.name}")

        # 将新创建的语料库名称写入 .env 文件
        write_to_env(bqml_corpus.name)

        return bqml_corpus.name
    except Exception as e:
        print(f"创建 RAG 语料库失败: {e}")
        # 检查是否是因为语料库已存在
        if "already exists" in str(e).lower():
             print("语料库可能已存在。尝试查找现有语料库...")
             corpora = rag.list_corpora(display_name=display_name)
             if corpora:
                 existing_corpus_name = corpora[0].name
                 print(f"找到现有语料库: {existing_corpus_name}")
                 # 更新 .env 文件以防万一
                 write_to_env(existing_corpus_name)
                 return existing_corpus_name
             else:
                 print("未能找到具有该显示名称的现有语料库。")
                 return None
        else:
            return None


def ingest_files(corpus_name):
    """将文件导入到指定的 RAG 语料库中。

    Args:
        corpus_name (str): 目标 RAG 语料库的资源名称。
    """
    if not corpus_name:
        print("错误：未提供有效的语料库名称，无法导入文件。")
        return

    print(f"开始将文件从 {paths} 导入到语料库 {corpus_name}...")
    try:
        # 配置数据转换，例如分块设置
        transformation_config = rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=512,    # 每个块的大小
                chunk_overlap=100, # 块之间的重叠大小
            ),
        )

        # 导入文件到语料库
        response = rag.import_files(
            corpus_name,
            paths, # 要导入的文件/目录路径列表
            transformation_config=transformation_config,  # 可选：应用转换配置
            # max_embedding_requests_per_min=1000,  # 可选：限制每分钟的嵌入请求数
        )
        print(f"文件导入操作已启动。响应: {response}") # 导入是异步的

        # 可以在这里添加轮询逻辑来检查导入状态，或者让用户手动检查

        # 列出语料库中的文件（可能需要等待导入完成才能看到新文件）
        print(f"当前语料库 {corpus_name} 中的文件列表（可能需要等待导入完成）：")
        list_corpus_files(corpus_name)

    except Exception as e:
        print(f"导入文件到语料库 {corpus_name} 时失败: {e}")


def list_corpus_files(corpus_name):
  """列出指定语料库中的文件。"""
  if not corpus_name:
      print("错误：未提供有效的语料库名称。")
      return
  try:
      files = list(rag.list_files(corpus_name=corpus_name))
      print(f"语料库 '{corpus_name}' 中的文件总数: {len(files)}")
      if not files:
          print("  语料库中没有文件。")
      for file in files:
          # 打印文件名和资源名称
          print(f"  - 文件显示名称: {file.display_name}, 资源名称: {file.name}")
  except Exception as e:
      print(f"列出语料库文件时出错: {e}")

# rag_response 函数与 tools.py 中的重复，这里保留一个作为示例
# def rag_response(query: str) -> str:
#     """从 RAG 语料库中检索上下文相关的信息。
#     Args:
#         query (str): 要在语料库中搜索的查询字符串。
#     Returns:
#         str: 包含从语料库中检索到的信息的响应字符串。
#     """
#     corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")
#     if not corpus_name:
#         return "错误：环境变量 BQML_RAG_CORPUS_NAME 未设置。"
#
#     rag_retrieval_config = rag.RagRetrievalConfig(
#         top_k=3,
#         # filter=rag.Filter(vector_distance_threshold=0.5),
#     )
#     try:
#         response = rag.retrieval_query(
#             rag_resources=[
#                 rag.RagResource(
#                     rag_corpus=corpus_name,
#                 )
#             ],
#             text=query,
#             rag_retrieval_config=rag_retrieval_config,
#         )
#         return str(response)
#     except Exception as e:
#         return f"RAG 查询时发生错误: {str(e)}"


def write_to_env(corpus_resource_name):
    """将语料库资源名称写入指定的 .env 文件。

    Args:
        corpus_resource_name (str): 要写入的语料库资源名称。
    """
    if not corpus_resource_name:
        print("错误：未提供有效的语料库资源名称，无法写入 .env 文件。")
        return

    try:
        # 加载现有的环境变量（如果存在）
        load_dotenv(env_file_path)

        # 设置或更新 .env 文件中的 BQML_RAG_CORPUS_NAME 键值对
        set_key(env_file_path, "BQML_RAG_CORPUS_NAME", corpus_resource_name)
        print(f"已将 BQML_RAG_CORPUS_NAME '{corpus_resource_name}' 写入到 {env_file_path}")
    except Exception as e:
        print(f"写入 .env 文件时出错: {e}")


if __name__ == "__main__":
    # 检查是否已存在 RAG 语料库名称环境变量
    if corpus_name_from_env:
        print(f"检测到环境变量 BQML_RAG_CORPUS_NAME: {corpus_name_from_env}")
        print("假设语料库已存在。如果需要重新创建或导入文件，请先清除该环境变量或手动执行相应函数。")
        # 可以选择性地列出现有语料库中的文件
        # list_corpus_files(corpus_name_from_env)
    else:
        print("未找到环境变量 BQML_RAG_CORPUS_NAME。")
        print("正在创建 RAG 语料库...")
        created_corpus_name = create_RAG_corpus()

        if created_corpus_name:
            print(f"语料库已创建或找到: {created_corpus_name}")
            print(f"正在将文件导入到语料库: {created_corpus_name}")
            ingest_files(created_corpus_name)
            print(f"文件导入流程已启动（可能需要一些时间完成）。")
        else:
            print("未能创建或获取语料库。")

    # 示例 RAG 查询
    # query = "如何使用 BQML 创建一个线性回归模型？"
    # print(f"\n示例 RAG 查询: {query}")
    # response = rag_response(query)
    # print(f"RAG 响应:\n{response}")


