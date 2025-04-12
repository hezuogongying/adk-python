
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

"""定义常量。"""

import os
# 导入 dotenv 用于加载 .env 文件中的环境变量
import dotenv

# 加载 .env 文件中的环境变量
dotenv.load_dotenv()

# Agent 名称
AGENT_NAME = "brand_search_optimization"
# Agent 描述
DESCRIPTION = "一个用于品牌搜索优化的有用助手。"
# Google Cloud 项目 ID，如果环境变量未设置，则默认为 "EMPTY"
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "EMPTY")
# Google Cloud 位置（区域），如果环境变量未设置，则默认为 "global"
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
# 使用的 LLM 模型名称，如果环境变量未设置，则默认为 "gemini-2.0-flash-001"
MODEL = os.getenv("MODEL", "gemini-2.0-flash-001")
# BigQuery 数据集 ID，如果环境变量未设置，则默认为 "products_data_agent"
DATASET_ID = os.getenv("DATASET_ID", "products_data_agent")
# BigQuery 表 ID，如果环境变量未设置，则默认为 "shoe_items"
TABLE_ID = os.getenv("TABLE_ID", "shoe_items")
# 是否禁用 WebDriver（用于 Selenium），0 表示不禁用，1 表示禁用。如果环境变量未设置，则默认为 0
DISABLE_WEB_DRIVER = int(os.getenv("DISABLE_WEB_DRIVER", 0))
# ADK wheel 文件名，如果环境变量未设置，则为空字符串
WHL_FILE_NAME = os.getenv("ADK_WHL_FILE", "")
# 用于暂存文件的 Google Cloud Storage 存储桶名称，如果环境变量未设置，则为空字符串
STAGING_BUCKET = os.getenv("STAGING_BUCKET", "")


