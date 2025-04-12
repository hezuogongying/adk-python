
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

"""品牌搜索优化 Agent 的部署脚本。"""

import os
import sys
# 导入 Vertex AI SDK
import vertexai
# 导入 absl 库用于处理命令行参数
from absl import app, flags
# 从 Agent 模块导入根 Agent
from brand_search_optimization.agent import root_agent
# 从共享库导入常量
from brand_search_optimization.shared_libraries import constants
# 从 Vertex AI 导入 agent_engines 和 AdkApp
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

# 定义命令行标志
FLAGS = flags.FLAGS
# GCP 项目 ID
flags.DEFINE_string("project_id", None, "GCP 项目 ID。")
# GCP 位置
flags.DEFINE_string("location", None, "GCP 位置。")
# GCP 存储桶名称
flags.DEFINE_string("bucket", None, "GCP 存储桶名称 (不带 gs:// 前缀)。") # 修改了标志描述
# ReasoningEngine 资源 ID
flags.DEFINE_string("resource_id", None, "ReasoningEngine 资源 ID。")
# 是否创建新 Agent
flags.DEFINE_bool("create", False, "创建一个新 Agent。")
# 是否删除现有 Agent
flags.DEFINE_bool("delete", False, "删除一个现有 Agent。")
# 确保 'create' 和 'delete' 标志是互斥的
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])

# 检查命令行参数中是否包含 '--delete'
IS_DELETE_REQUESTED = "--delete" in sys.argv

def create() -> None:
    """创建并部署 Agent。"""
    # 创建 AdkApp 实例，包装根 Agent，并启用跟踪
    adk_app = AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    # 定义需要额外打包的本地 Python 包路径
    extra_packages = [f"./brand_search_optimization"]

    # 定义部署 Agent 所需的 Python 依赖项
    requirements = [
        "google-adk",  # ADK 核心库
        # Vertex AI SDK (包含 agent_engines)，指定特定 git commit
        "google-cloud-aiplatform[agent_engines] @ git+https://github.com/googleapis/python-aiplatform.git@copybara_738852226",
        "pydantic==2.10.6", # Pydantic 库，用于数据验证
        "requests",         # HTTP 请求库
        "python-dotenv",    # 加载 .env 文件
        "google-genai",     # Google Generative AI 库
        "selenium",         # Web 自动化库
        "webdriver-manager",# WebDriver 管理库
        "google-cloud-bigquery", # BigQuery 客户端库
        "absl-py",          # Absl Python 库 (用于 flags 等)
        "pillow",           # PIL 图像处理库
    ]

    print("部署 Agent，依赖项:", requirements)
    print("部署 Agent，额外包:", extra_packages)

    # 使用 agent_engines.create 创建远程 Agent
    remote_agent = agent_engines.create(
        app=adk_app,
        requirements=requirements,
        extra_packages=extra_packages,
    )
    print(f"已创建远程 Agent: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    """删除指定的 Agent。"""
    # 获取远程 Agent 对象
    remote_agent = agent_engines.get(resource_id)
    # 强制删除 Agent
    remote_agent.delete(force=True)
    print(f"已删除远程 Agent: {resource_id}")


def main(argv: list[str]) -> None: # pylint: disable=unused-argument (忽略未使用的 argv 参数警告)
    """主执行函数。"""
    # 从命令行标志或环境变量获取配置
    project_id = FLAGS.project_id if FLAGS.project_id else constants.PROJECT
    location = FLAGS.location if FLAGS.location else constants.LOCATION
    bucket = FLAGS.bucket if FLAGS.bucket else constants.STAGING_BUCKET

    print(f"项目: {project_id}")
    print(f"位置: {location}")
    print(f"存储桶: {bucket}")

    # 检查必要的环境变量是否已设置
    if not project_id or project_id == "EMPTY": # 添加对 "EMPTY" 的检查
        print("错误：缺少必需的环境变量或命令行参数：GOOGLE_CLOUD_PROJECT / --project_id")
        return
    elif not location or location == "global": # "global" 可能不是一个有效的具体部署位置
        print("错误：缺少必需的环境变量或命令行参数：GOOGLE_CLOUD_LOCATION / --location (请指定具体区域，如 us-central1)")
        # 注意：虽然 'global' 可以用于某些 Vertex AI 服务，但部署 Agent Engine 通常需要具体区域。
        # 如果 'global' 在您的用例中有效，可以移除此警告。
        # return # 暂时不返回，允许 'global'
    elif not bucket:
        print("错误：缺少必需的环境变量或命令行参数：GOOGLE_CLOUD_STORAGE_BUCKET / --bucket")
        return

    # 初始化 Vertex AI SDK
    vertexai.init(
        project=project_id,
        location=location,
        # 指定暂存存储桶的 GCS URI
        staging_bucket=f"gs://{bucket}",
    )

    # 根据命令行标志执行相应操作
    if FLAGS.create:
        create()
    elif FLAGS.delete:
        # 检查删除操作是否提供了 resource_id
        if not FLAGS.resource_id:
            print("错误：删除操作需要 resource_id")
            return
        delete(FLAGS.resource_id)
    else:
        # 如果没有指定 create 或 delete，则检查是否只提供了 resource_id（可能意图是删除但忘了 --delete）
        if FLAGS.resource_id and not IS_DELETE_REQUESTED:
             print("错误：提供了 resource_id 但未指定 --delete。如果您想删除，请添加 --delete 标志。")
        else:
            print("错误：未知命令。请使用 --create 或 --delete。")

# 如果此脚本作为主程序运行
if __name__ == "__main__":
    # 运行 absl 应用
    app.run(main)


