
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
"""客户服务 Agent 的配置模块。"""

import os
import logging
# 导入 Pydantic 相关库用于设置和数据模型验证
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field


# 配置基本日志记录
logging.basicConfig(level=logging.DEBUG)
# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)


# 定义 Agent 模型设置的数据模型
class AgentModel(BaseModel):
    """Agent 模型设置。"""
    # Agent 名称，默认为 "customer_service_agent"
    name: str = Field(default="customer_service_agent")
    # 使用的 LLM 模型，默认为 "gemini-2.0-flash-001"
    model: str = Field(default="gemini-2.0-flash-001")


# 定义主配置类，继承自 BaseSettings
class Config(BaseSettings):
    """客户服务 Agent 的配置设置。"""

    # Pydantic 设置配置
    model_config = SettingsConfigDict(
        # 指定 .env 文件路径，相对于当前文件
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../.env"
        ),
        # 环境变量前缀
        env_prefix="GOOGLE_",
        # 是否区分大小写
        case_sensitive=True,
    )
    # Agent 设置，使用上面定义的 AgentModel 作为默认值
    agent_settings: AgentModel = Field(default=AgentModel())
    # 应用名称
    app_name: str = "customer_service_app"
    # Google Cloud 项目 ID，默认为 "my_project"
    CLOUD_PROJECT: str = Field(default="my_project")
    # Google Cloud 位置（区域），默认为 "us-central1"
    CLOUD_LOCATION: str = Field(default="us-central1")
    # 是否使用 Vertex AI，默认为 "1" (表示使用)
    GENAI_USE_VERTEXAI: str = Field(default="1")
    # API 密钥，默认为空字符串或 None
    API_KEY: str | None = Field(default="")


