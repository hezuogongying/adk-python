
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

"""FOMC 研究示例 agent 的 'compute_rate_move_probability' 工具。"""

# 导入必要的库
import logging

# 从 google.adk.tools 导入 ToolContext
from google.adk.tools import ToolContext

# 导入当前包下的共享库
from ..shared_libraries import price_utils

# 获取日志记录器
logger = logging.getLogger(__name__)


def compute_rate_move_probability_tool(
    tool_context: ToolContext,
) -> dict[str, str]:
    """计算请求的会议日期的利率变动概率。

    参数:
      tool_context: ToolContext 对象。

    返回:
      一个包含 "status" 和（可选）"message" 键的字典。
    """
    # 从工具上下文中获取请求的会议日期
    meeting_date = tool_context.state.get("requested_meeting_date")
    if not meeting_date:
        logger.error("在状态中未找到 'requested_meeting_date'。")
        return {"status": "错误 (ERROR)", "message": "未提供会议日期。"}

    logger.debug("正在计算 %s 的利率变动概率", meeting_date)
    # 调用 price_utils 中的函数计算概率
    prob_result = price_utils.compute_probabilities(meeting_date)
    # 检查计算结果的状态
    if prob_result["status"] != "成功 (OK)":
        # 如果计算失败，返回错误状态和消息
        return {"status": "错误 (ERROR)", "message": prob_result["message"]}
    # 获取计算出的概率
    probs = prob_result["output"]
    logger.debug("利率变动概率: %s", probs)
    # 将概率结果更新到工具上下文的状态中
    tool_context.state.update({"rate_move_probabilities": probs})
    # 返回成功状态
    return {"status": "成功 (OK)"}


