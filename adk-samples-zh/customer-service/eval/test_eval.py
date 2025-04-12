
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

# 导入日志、参数解析和系统模块
import logging
import argparse
import sys
# 导入 Vertex AI SDK
import vertexai
# 从 customer_service 包导入根 Agent 和配置
from customer_service.agent import root_agent
from customer_service.config import Config
# 从 Vertex AI 导入 agent_engines 和 AdkApp
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp
# 导入 Google API 核心异常
from google.api_core.exceptions import NotFound

# 配置基本日志记录
logging.basicConfig(level=logging.DEBUG)
# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)

# 加载配置
configs = Config()

# 定义暂存存储桶名称
STAGING_BUCKET = f"gs://{configs.CLOUD_PROJECT}-adk-customer-service-staging"

# 定义 ADK 和 Agent 的 wheel 文件路径（注意：这些文件需要存在）
# ADK_WHL_FILE = (
#     "./google_adk-0.0.2.dev20250404+nightly743987168-py3-none-any.whl" # 示例 ADK wheel 文件
# )
AGENT_WHL_FILE = "./customer_service-0.1.0-py3-none-any.whl" # Agent 的 wheel 文件

# 初始化 Vertex AI SDK
vertexai.init(
    project=configs.CLOUD_PROJECT,        # 项目 ID
    location=configs.CLOUD_LOCATION,      # 位置
    staging_bucket=STAGING_BUCKET,       # 暂存存储桶
)

# 创建参数解析器
parser = argparse.ArgumentParser(description="简单的示例应用")

# 添加 --delete 参数，用于删除已部署的 Agent
parser.add_argument(
    "--delete",
    action="store_true", # 设为布尔标志
    dest="delete",       # 存储到 args.delete
    required=False,      # 非必需参数
    help="删除已部署的 Agent",
)
# 添加 --resource_id 参数，用于指定要删除的 Agent 资源 ID
parser.add_argument(
    "--resource_id",
    # 如果命令行参数中包含 '--delete'，则此参数为必需
    required="--delete" in sys.argv,
    action="store",      # 存储参数值
    dest="resource_id",  # 存储到 args.resource_id
    help=(
        "要删除的 Agent 的资源 ID，格式为 "
        "projects/PROJECT_ID/locations/LOCATION/reasoningEngines/REASONING_ENGINE_ID"
    ),
)


# 解析命令行参数
args = parser.parse_args()

# 如果指定了 --delete 参数
if args.delete:
    try:
        # 尝试获取指定资源 ID 的 Agent Engine
        agent_engines.get(resource_name=args.resource_id)
        # 如果找到，则删除该 Agent Engine
        agent_engines.delete(resource_name=args.resource_id)
        print(f"Agent {args.resource_id} 已成功删除")
    except NotFound as e:
        # 如果未找到 Agent Engine，打印错误信息
        print(e)
        print(f"未找到 Agent {args.resource_id}")
    except Exception as e: # 捕获其他可能的异常
        print(f"删除 Agent 时发生错误: {e}")

# 如果没有指定 --delete 参数（即创建或更新 Agent）
else:
    logger.info("正在部署应用...")
    # 创建 AdkApp 实例
    app = AdkApp(agent=root_agent, enable_tracing=False) # 禁用跟踪

    # 检查 Agent wheel 文件是否存在
    if not os.path.exists(AGENT_WHL_FILE):
        logger.error(f"Agent wheel 文件未找到: {AGENT_WHL_FILE}")
        logger.error("请先构建 wheel 文件 (例如: poetry build --format wheel)")
        sys.exit(1) # 退出脚本

    logging.debug("正在将 Agent 部署到 Agent Engine:")
    # 创建或更新 Agent Engine
    remote_app = agent_engines.create(
        app,
        # 指定部署所需的依赖项（Agent 的 wheel 文件）
        requirements=[
            AGENT_WHL_FILE,
            # 可以添加其他运行时依赖，例如 "google-cloud-bigquery>=3.0.0"
        ],
        # 指定需要上传的额外本地包（Agent 的 wheel 文件）
        extra_packages=[AGENT_WHL_FILE],
    )

    logging.debug("正在测试部署:")
    # 创建一个测试会话
    session = remote_app.create_session(user_id="123")
    # 发送一个简单的查询以测试部署是否成功
    test_message = "hello!"
    print(f"发送测试消息: '{test_message}' 到 Agent Engine: {remote_app.resource_name}")
    has_content = False
    for event in remote_app.stream_query(
        user_id="123",
        session_id=session["id"],
        message=test_message,
    ):
        # 检查事件中是否有内容
        if event.get("content", None):
            print(f"收到来自 Agent 的响应: {event['content']}")
            has_content = True
            # 可以在这里添加更具体的响应内容断言

    if has_content:
         print(
            f"Agent 已成功部署，资源名称为: {remote_app.resource_name}"
        )
    else:
        print(f"警告：测试查询未收到任何内容响应。请检查 Agent Engine 日志。资源名称: {remote_app.resource_name}")

    # 可以选择删除测试会话
    try:
        remote_app.delete_session(user_id="123", session_id=session['id'])
        print("测试会话已删除。")
    except Exception as e:
        print(f"删除测试会话时出错: {e}")


