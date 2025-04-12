
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

"""数据科学 Agent 的部署脚本。"""

import logging # 导入日志模块
import os # 导入操作系统交互模块
import sys # 导入系统模块，用于路径操作

import vertexai # 导入 Vertex AI SDK
from absl import app, flags # 导入 absl 库，用于命令行参数处理
from dotenv import load_dotenv # 导入 dotenv 库，用于加载 .env 文件
from google.api_core import exceptions as google_exceptions # 导入 Google API 核心异常
from google.cloud import storage # 导入 Google Cloud Storage 客户端库
from vertexai import agent_engines # 导入 Vertex AI Agent Engines 功能
from vertexai.preview.reasoning_engines import AdkApp # 导入 ADK 应用类（预览版）

# 动态添加项目根目录到 Python 路径，以便导入 data_science 包
# 这假设脚本在 deployment 目录下运行
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # 导入数据科学 Agent 的根 Agent 对象
    from data_science.agent import root_agent
except ImportError as e:
    print(f"无法导入 data_science.agent: {e}")
    print(f"请确保您在项目根目录下运行此脚本，或者项目结构正确。当前路径: {sys.path}")
    sys.exit(1)


# 定义命令行标志
FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP 项目 ID。如果未提供，将尝试从环境变量 GOOGLE_CLOUD_PROJECT 读取。")
flags.DEFINE_string("location", None, "GCP 位置（区域）。如果未提供，将尝试从环境变量 GOOGLE_CLOUD_LOCATION 读取。")
flags.DEFINE_string(
    "bucket", None, "GCP 存储桶名称（不含 gs:// 前缀）。如果未提供，将尝试从环境变量 GOOGLE_CLOUD_STORAGE_BUCKET 读取，或使用默认值 '项目ID-adk-staging'。"
)
flags.DEFINE_string("resource_id", None, "要操作（例如删除）的 ReasoningEngine 资源 ID。")

flags.DEFINE_bool("create", False, "创建并部署一个新的 Agent。")
flags.DEFINE_bool("delete", False, "删除一个已存在的 Agent。")
# 标记 --create 和 --delete 为互斥标志
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])

# 定义 Agent 的 wheel 文件名
AGENT_WHL_FILE = "data_science-0.1-py3-none-any.whl"
# 构建 wheel 文件的预期路径（假设在 deployment 目录下）
AGENT_WHL_PATH = os.path.join(os.path.dirname(__file__), AGENT_WHL_FILE)


# 配置日志记录
logging.basicConfig(level=logging.INFO) # 设置日志级别为 INFO
logger = logging.getLogger(__name__) # 获取当前模块的 logger


好的，我们来逐个处理您提供的文件，将英文注释、prompt和参数描述等翻译成中文，并保留必要的专业术语和变量名称。

---

