
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

"""FOMC 研究示例 agent 的 'store_state' 工具"""

# 导入必要的库
import logging
import typing # 用于类型提示

# 从 google.adk.tools 导入 ToolContext
from google.adk.tools import ToolContext

# 获取日志记录器
logger = logging.getLogger(__name__)


def store_state_tool(
    state: dict[str, typing.Any], tool_context: ToolContext
) -> dict[str, str]:
    """将新的状态值存储在 ToolContext 中。

    参数:
      state: 包含新状态值的字典。
      tool_context: ToolContext 对象。

    返回:
      一个包含 "status" 键的字典（表示成功）。
    """
    logger.info("store_state_tool(): 存储状态 %s", state)
    # 更新 ToolContext 中的状态
    tool_context.state.update(state)
    # 返回成功状态
    return {"status": "ok"}


