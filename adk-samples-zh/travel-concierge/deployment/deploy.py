
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

from google.auth import default # 用于获取默认认证凭据
import vertexai
from vertexai.preview import rag # 导入 Vertex AI RAG 相关库
import os
from dotenv import load_dotenv, set_key # 用于加载和更新 .env 文件
import requests # 用于下载文件
import tempfile # 用于创建临时目录

# 从 .env 文件加载环境变量
load_dotenv()

# --- 请填写您的配置 ---
# 从环境变量中检索 PROJECT_ID。
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError(
        "未设置 GOOGLE_CLOUD_PROJECT 环境变量。请在您的 .env 文件中设置。"
    )
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
if not LOCATION:
    raise ValueError(
        "未设置 GOOGLE_CLOUD_LOCATION 环境变量。请在您的 .env 文件中设置。"
    )
CORPUS_DISPLAY_NAME = "Alphabet_10K_2024_corpus" # RAG 语料库的显示名称
CORPUS_DESCRIPTION = "包含 Alphabet 2024 年 10-K 文档的语料库" # 语料库描述
PDF_URL = "https://abc.xyz/assets/77/51/9841ad5c4fbe85b4440c47a4df8d/goog-10-k-2024.pdf" # 要下载的 PDF 文档 URL
PDF_FILENAME = "goog-10-k-2024.pdf" # 保存 PDF 的文件名
# .env 文件的绝对路径
ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


# --- 脚本开始 ---
def initialize_vertex_ai():
  """初始化 Vertex AI SDK"""
  credentials, _ = default() # 获取默认凭据
  vertexai.init(
      project=PROJECT_ID, location=LOCATION, credentials=credentials
  )


def create_or_get_corpus():
  """创建新语料库或获取现有语料库。"""
  # 配置嵌入模型
  embedding_model_config = rag.EmbeddingModelConfig(
      publisher_model="publishers/google/models/text-embedding-004" # 使用指定的文本嵌入模型
  )
  # 列出现有的语料库
  existing_corpora = rag.list_corpora()
  corpus = None
  # 检查是否有同名的语料库已存在
  for existing_corpus in existing_corpora:
    if existing_corpus.display_name == CORPUS_DISPLAY_NAME:
      corpus = existing_corpus
      print(f"找到显示名称为 '{CORPUS_DISPLAY_NAME}' 的现有语料库")
      break
  # 如果不存在，则创建新语料库
  if corpus is None:
    corpus = rag.create_corpus(
        display_name=CORPUS_DISPLAY_NAME,
        description=CORPUS_DESCRIPTION,
        embedding_model_config=embedding_model_config,
    )
    print(f"创建了显示名称为 '{CORPUS_DISPLAY_NAME}' 的新语料库")
  return corpus


def download_pdf_from_url(url, output_path):
  """从指定 URL 下载 PDF 文件。"""
  print(f"正在从 {url} 下载 PDF...")
  response = requests.get(url, stream=True) # 发起 GET 请求，启用流式下载
  response.raise_for_status()  # 如果发生 HTTP 错误，则引发异常

  # 将下载内容写入本地文件
  with open(output_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192): # 分块写入，避免内存占用过大
      f.write(chunk)

  print(f"PDF 已成功下载到 {output_path}")
  return output_path


def upload_pdf_to_corpus(corpus_name, pdf_path, display_name, description):
  """将 PDF 文件上传到指定的语料库。"""
  print(f"正在将 {display_name} 上传到语料库...")
  try:
    # 调用 RAG API 上传文件
    rag_file = rag.upload_file(
        corpus_name=corpus_name, # 目标语料库名称（资源 ID）
        path=pdf_path, # 本地 PDF 文件路径
        display_name=display_name, # 在语料库中显示的名称
        description=description, # 文件描述
    )
    print(f"已成功将 {display_name} 上传到语料库")
    return rag_file
  except Exception as e:
    print(f"上传文件 {display_name} 时出错: {e}")
    return None

def update_env_file(corpus_name, env_file_path):
    """使用语料库名称更新 .env 文件。"""
    try:
        # 将 RAG_CORPUS 键更新为实际的语料库资源名称（ID）
        set_key(env_file_path, "RAG_CORPUS", corpus_name)
        print(f"已将 {env_file_path} 中的 RAG_CORPUS 更新为 {corpus_name}")
    except Exception as e:
        print(f"更新 .env 文件时出错: {e}")

def list_corpus_files(corpus_name):
  """列出指定语料库中的文件。"""
  files = list(rag.list_files(corpus_name=corpus_name)) # 获取文件列表
  print(f"语料库中的文件总数: {len(files)}")
  for file in files:
    print(f"文件: {file.display_name} - {file.name}") # 打印文件名和资源 ID


def main():
  """主函数，执行语料库创建和文件上传流程"""
  initialize_vertex_ai() # 初始化 Vertex AI
  corpus = create_or_get_corpus() # 创建或获取语料库

  # 使用语料库的资源名称（ID）更新 .env 文件
  update_env_file(corpus.name, ENV_FILE_PATH)

  # 创建一个临时目录来存储下载的 PDF
  with tempfile.TemporaryDirectory() as temp_dir:
    pdf_path = os.path.join(temp_dir, PDF_FILENAME) # 构建 PDF 在临时目录中的完整路径

    # 从 URL 下载 PDF
    download_pdf_from_url(PDF_URL, pdf_path)

    # 将 PDF 上传到语料库
    upload_pdf_to_corpus(
        corpus_name=corpus.name, # 语料库资源名称
        pdf_path=pdf_path, # 本地 PDF 路径
        display_name=PDF_FILENAME, # 显示名称
        description=f"Alphabet 的 2024 年 10-K 文档" # 描述
    )

  # 列出语料库中的所有文件以确认上传
  list_corpus_files(corpus_name=corpus.name)

if __name__ == "__main__":
  main() # 执行主函数


