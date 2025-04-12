
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

"""LLM Auditor 的部署脚本。"""

# 导入必要的库
import os

# 从 absl 库导入 app 和 flags，用于处理命令行参数
from absl import app
from absl import flags
# 从 dotenv 库导入 load_dotenv，用于加载环境变量
from dotenv import load_dotenv
# 导入 LLM Auditor 项目的根 agent
from llm_auditor.agent import root_agent
# 导入 Vertex AI SDK
import vertexai
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

# 定义是否列出所有 agent 的标志
flags.DEFINE_bool("list", False, "列出所有 agent。")
# 定义是否创建新 agent 的标志
flags.DEFINE_bool("create", False, "创建新的 agent。")
# 定义是否删除现有 agent 的标志
flags.DEFINE_bool("delete", False, "删除现有的 agent。")
# 将 --create 和 --delete 标志标记为互斥，两者只能选其一
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])

# 定义 Vertex AI Python SDK 的特定 Git 提交版本（可能用于解决兼容性问题）
_AI_PLATFORM_GIT = (
    "git+https://github.com/googleapis/python-aiplatform.git@copybara_738852226"
)


def create() -> None:
    """为 LLM Auditor 创建一个 agent engine。"""
    # 使用根 agent 创建 AdkApp 实例
    adk_app = AdkApp(agent=root_agent, enable_tracing=True) # 启用追踪

    # 使用 agent_engines 创建远程 agent
    remote_agent = agent_engines.create(
        adk_app,
        display_name=root_agent.name, # 设置显示名称
        requirements=[ # 指定依赖项
            "google-adk (>=0.0.2)",
            f"google-cloud-aiplatform[agent_engines] @ {_AI_PLATFORM_GIT}", # 使用特定版本的 SDK
            "google-genai (>=1.5.0,<2.0.0)",
            "pydantic (>=2.10.6,<3.0.0)",
            "absl-py (>=2.2.1,<3.0.0)",
        ],
        extra_packages=["./llm_auditor"], # 指定额外的包（包含 agent 代码）
    )
    print(f"已创建远程 agent: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    """删除指定的 agent。"""
    # 获取远程 agent 实例
    remote_agent = agent_engines.get(resource_id)
    # 强制删除 agent
    remote_agent.delete(force=True)
    print(f"已删除远程 agent: {resource_id}")


def list_agents() -> None:
    """列出所有远程 agent。"""
    # 获取所有远程 agent 列表
    remote_agents = agent_engines.list()
    # 定义打印模板
    TEMPLATE = '''
{agent.name} ("{agent.display_name}")
- 创建时间: {agent.create_time}
- 更新时间: {agent.update_time}
'''
    # 格式化并拼接 agent 信息字符串
    remote_agents_string = '\n'.join(TEMPLATE.format(agent=agent) for agent in remote_agents)
    print(f"所有远程 agent:\n{remote_agents_string}")

def main(argv: list[str]) -> None:
    """主执行函数。"""
    del argv  # 未使用的参数
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
        FLAGS.bucket if FLAGS.bucket
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

    # 根据命令行标志执行相应操作
    if FLAGS.list:
        list_agents()
    elif FLAGS.create:
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


