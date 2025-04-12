
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

"""FOMC 研究 agent 的部署脚本。"""

# 导入必要的库
import os

# 导入 Vertex AI SDK
import vertexai
# 从 absl 库导入 app 和 flags，用于处理命令行参数
from absl import app, flags
# 从 dotenv 库导入 load_dotenv，用于加载环境变量
from dotenv import load_dotenv
# 导入 FOMC 研究项目的根 agent
from fomc_research.agent import root_agent
# 导入 agent_engines 和 AdkApp
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

# 定义命令行标志 (flags)
FLAGS = flags.FLAGS
# 定义 GCP 项目 ID 标志
flags.DEFINE_string("project_id", None, "GCP 项目 ID。")
# 定义 GCP 位置标志
flags.DEFINE_string("location", None, "GCP 位置。")
# 定义 GCS 存储桶名称标志
flags.DEFINE_string("bucket", None, "GCS 存储桶名称。")
# 定义 ReasoningEngine 资源 ID 标志
flags.DEFINE_string("resource_id", None, "ReasoningEngine 资源 ID。")

# 定义是否创建新 agent 的标志
flags.DEFINE_bool("create", False, "创建新的 agent。")
# 定义是否删除现有 agent 的标志
flags.DEFINE_bool("delete", False, "删除现有的 agent。")
# 将 --create 和 --delete 标志标记为互斥，两者只能选其一
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])

# 定义 agent wheel 文件的名称
AGENT_WHL_FILE = "fomc_research-0.1-py3-none-any.whl"


def create() -> None:
    """创建并部署 agent。"""
    # 使用根 agent 创建 AdkApp 实例
    adk_app = AdkApp(
        agent=root_agent,
        enable_tracing=False, # 禁用追踪
    )

    # 使用 agent_engines 创建远程 agent
    remote_agent = agent_engines.create(
        adk_app,
        requirements=[f"./{AGENT_WHL_FILE}"], # 指定依赖项（wheel 文件）
        extra_packages=[f"./{AGENT_WHL_FILE}"], # 指定额外的包（wheel 文件）
    )
    print(f"已创建远程 agent: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    """删除指定的 agent。"""
    # 获取远程 agent 实例
    remote_agent = agent_engines.get(resource_id)
    # 强制删除 agent
    remote_agent.delete(force=True)
    print(f"已删除远程 agent: {resource_id}")


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

    # 打印使用的配置信息
    print(f"PROJECT: {project_id}")
    print(f"LOCATION: {location}")
    print(f"BUCKET: {bucket}")

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

    # 根据命令行标志执行创建或删除操作
    if FLAGS.create:
        create()
    elif FLAGS.delete:
        # 删除操作需要 resource_id
        if not FLAGS.resource_id:
            print("删除操作需要 resource_id")
            return
        delete(FLAGS.resource_id)
    else:
        print("未知命令")

# 程序入口点
if __name__ == "__main__":
    # 运行主函数
    app.run(main)


