
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

# 导入必要的库
import vertexai # Vertex AI SDK
from vertexai.preview.reasoning_engines import AdkApp # ADK 应用类
from vertexai import agent_engines # Agent Engine 相关功能
from dotenv import load_dotenv # 加载环境变量
import os # 操作系统相关功能

# 导入个性化购物 agent
from personalized_shopping.agent import root_agent

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量获取 GCP 配置
cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION")
storage_bucket = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

# 打印配置信息
print(f"cloud_project={cloud_project}")
print(f"cloud_location={cloud_location}")
print(f"storage_bucket={storage_bucket}")

# 初始化 Vertex AI
vertexai.init(
    project=cloud_project,
    location=cloud_location,
    staging_bucket=f"gs://{storage_bucket}", # 设置中转存储桶
)

print("-" * 50)
print("开始部署应用...")
# 创建 AdkApp 实例
app = AdkApp(
    agent=root_agent,
    enable_tracing=True, # 启用追踪
)

# 定义 agent wheel 文件的路径
AGENT_WHL_FILE = "./personalized_shopping-0.1.0-py3-none-any.whl"

print("正在将 agent 部署到 agent engine...")
# 使用 agent_engines 创建远程 agent
remote_app = agent_engines.create(
    app,
    requirements=[ # 指定依赖项
        AGENT_WHL_FILE,
    ],
    extra_packages=[ # 指定额外的包
        AGENT_WHL_FILE,
    ],
)
print("将 agent 部署到 agent engine 完成。")
print("-" * 50)

# 测试部署
print("测试部署:")
# 创建一个测试会话
session = remote_app.create_session(user_id="123")
# 发送一个简单的查询并流式打印事件
for event in remote_app.stream_query(
    user_id="123",
    session_id=session["id"],
    message="你好!", # 测试消息
):
    print(event)
print("测试部署完成！")
print("-" * 50)


