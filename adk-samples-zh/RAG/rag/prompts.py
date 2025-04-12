
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

import os

from google.adk.agents import Agent # 导入 ADK Agent 类
# 导入 Vertex AI RAG 检索工具
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag # 导入 Vertex AI RAG 相关库

from dotenv import load_dotenv
from .prompts import return_instructions_root # 从本地 prompts 模块导入指令生成函数

# 加载 .env 文件中的环境变量
load_dotenv()

# 创建 Vertex AI RAG 检索工具实例
ask_vertex_retrieval = VertexAiRagRetrieval(
    name='retrieve_rag_documentation', # 工具名称
    description=( # 工具描述，告知 Agent 何时使用此工具
        '使用此工具从 RAG 语料库中检索文档和参考资料以回答问题。'
    ),
    # 指定 RAG 资源（语料库）
    rag_resources=[
        rag.RagResource(
            # 请填写您自己的 RAG 语料库 ID
            # 这里是一个用于测试目的的示例 RAG 语料库 ID
            # 例如 projects/123/locations/us-central1/ragCorpora/456
            rag_corpus=os.environ.get("RAG_CORPUS") # 从环境变量获取 RAG_CORPUS ID
        )
    ],
    similarity_top_k=10, # 检索最相似的 top K 个文档块
    vector_distance_threshold=0.6, # 向量距离阈值，用于过滤相关性较低的文档块
)

# 创建根 Agent 实例
root_agent = Agent(
    model='gemini-2.0-flash-001', # 指定使用的 LLM 模型
    name='ask_rag_agent', # Agent 名称
    instruction=return_instructions_root(), # 设置 Agent 的指令（从 prompts 模块获取）
    # 将 RAG 检索工具添加到 Agent 可用的工具列表中
    tools=[
        ask_vertex_retrieval,
    ]
)

