
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

import vertexai
from vertexai import agent_engines # 导入 Vertex AI Agent Engine 相关库
from vertexai.preview.reasoning_engines import AdkApp # 导入 ADK 应用包装器
from rag.agent import root_agent # 从 RAG 模块导入根 Agent
import logging
import os
from dotenv import set_key # 用于更新 .env 文件

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 从环境变量加载配置
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET") # GCS Staging Bucket 用于部署
# 定义 .env 文件的相对路径
ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))

# 初始化 Vertex AI SDK
vertexai.init(
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
    staging_bucket=STAGING_BUCKET,
)

# 函数：更新 .env 文件
def update_env_file(agent_engine_id, env_file_path):
    """使用 Agent Engine ID 更新 .env 文件。"""
    try:
        # 使用 dotenv 的 set_key 更新或添加 AGENT_ENGINE_ID
        set_key(env_file_path, "AGENT_ENGINE_ID", agent_engine_id)
        print(f"已将 {env_file_path} 中的 AGENT_ENGINE_ID 更新为 {agent_engine_id}")
    except Exception as e:
        print(f"更新 .env 文件时出错: {e}")

logger.info("正在部署应用...")
# 创建 AdkApp 实例，包装 RAG Agent
app = AdkApp(
    agent=root_agent, # 要部署的 Agent
    enable_tracing=True, # 启用追踪以便调试
)

logging.debug("正在将 Agent 部署到 Agent Engine:")

# 使用 agent_engines.create 创建并部署 Agent
remote_app = agent_engines.create(
    app, # 要部署的 AdkApp
    # 指定部署所需的 Python 依赖库
    requirements=[
        "google-cloud-aiplatform[adk,agent-engines]==1.88.0",
        "google-adk",
        "python-dotenv",
        "google-auth",
        "tqdm",
        "requests",
    ],
    # 指定需要一起打包上传的本地 Python 包（包含 Agent 代码）
    extra_packages=[
        "./rag", # RAG Agent 的代码包
    ],
)

# 记录部署结果
logging.info(f"已成功将 Agent 部署到 Vertex AI Agent Engine，资源名称: {remote_app.resource_name}")

# 将新创建的 Agent Engine ID 更新到 .env 文件中
update_env_file(remote_app.resource_name, ENV_FILE_PATH)

