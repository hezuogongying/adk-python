
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

"""测试将 FOMC 研究 Agent 部署到 Agent Engine。"""

# 导入必要的库
import os

# 导入 Vertex AI SDK
import vertexai
# 从 absl 库导入 app 和 flags，用于处理命令行参数
from absl import app, flags
# 从 dotenv 库导入 load_dotenv，用于加载环境变量
from dotenv import load_dotenv
# 导入 agent_engines
from vertexai import agent_engines

# 定义命令行标志 (flags)
FLAGS = flags.FLAGS

# 定义 GCP 项目 ID 标志
flags.DEFINE_string("project_id", None, "GCP 项目 ID。")
# 定义 GCP 位置标志
flags.DEFINE_string("location", None, "GCP 位置。")
# 定义 GCS 存储桶名称标志
flags.DEFINE_string("bucket", None, "GCS 存储桶名称。")
# 定义 ReasoningEngine 资源 ID 标志
flags.DEFINE_string(
    "resource_id",
    None,
    "ReasoningEngine 资源 ID（部署 agent 后返回）。",
)
# 定义用户 ID 标志
flags.DEFINE_string("user_id", None, "用户 ID（可以是任何字符串）。")
# 将 resource_id 标记为必需标志
flags.mark_flag_as_required("resource_id")
# 将 user_id 标记为必需标志
flags.mark_flag_as_required("user_id")


def main(argv: list[str]) -> None:  # pylint: disable=unused-argument
    """主执行函数。"""
    # 加载 .env 文件中的环境变量
    load_dotenv()

    # 获取项目 ID，优先使用命令行标志，其次使用环境变量
    project_id = (
        FLAGS.project_id
        if FLAGS.project_id
        else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    # 获取位置信息，优先使用命令行标志，其次使用环境变量
    location = (
        FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    # 获取存储桶名称，优先使用命令行标志，其次使用环境变量
    bucket = (
        FLAGS.bucket
        if FLAGS.bucket
        else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
    )

    # 再次从环境变量获取，确保有值（之前的逻辑可能获取到None）
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

    # 检查必需的环境变量是否存在
    if not project_id:
        print("缺少必需的环境变量: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("缺少必需的环境变量: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print(
            "缺少必需的环境变量: GOOGLE_CLOUD_STORAGE_BUCKET"
        )
        return

    # 初始化 Vertex AI
    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}", # 设置中转存储桶
    )

    # 获取已部署的 agent 实例
    agent = agent_engines.get(FLAGS.resource_id)
    print(f"找到资源 ID 为 {FLAGS.resource_id} 的 agent")
    # 为指定用户创建会话
    session = agent.create_session(user_id=FLAGS.user_id)
    print(f"为用户 ID {FLAGS.user_id} 创建了会话")
    print("输入 'quit' 退出。")
    # 进入交互循环
    while True:
        # 获取用户输入
        user_input = input("输入: ")
        # 如果用户输入 'quit'，则退出循环
        if user_input == "quit":
            break

        # 流式查询 agent
        for event in agent.stream_query(
            user_id=FLAGS.user_id, session_id=session["id"], message=user_input
        ):
            # 检查事件中是否包含内容
            if "content" in event:
                # 检查内容中是否包含 parts
                if "parts" in event["content"]:
                    parts = event["content"]["parts"]
                    # 遍历 parts
                    for part in parts:
                        # 检查 part 中是否包含文本
                        if "text" in part:
                            text_part = part["text"]
                            # 打印 agent 的响应文本
                            print(f"响应: {text_part}")

    # 删除会话
    agent.delete_session(user_id=FLAGS.user_id, session_id=session["id"])
    print(f"删除了用户 ID {FLAGS.user_id} 的会话")


# 程序入口点
if __name__ == "__main__":
    # 运行主函数
    app.run(main)


