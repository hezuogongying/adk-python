
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

"""FOMC 研究 Agent 的回调函数。"""

# 导入必要的库
import logging
import time

# 从 google.adk.agents 导入回调上下文和 LLM 请求对象
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest

# 获取日志记录器
logger = logging.getLogger(__name__)
# 设置日志级别为 DEBUG
logger.setLevel(logging.DEBUG)

# 调整这些值以限制 agent 查询 LLM API 的速率。
RATE_LIMIT_SECS = 60 # 速率限制的时间窗口（秒）
RPM_QUOTA = 1000 # 每个时间窗口允许的最大请求数


def rate_limit_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    # pylint: disable=unused-argument
    """实现查询速率限制的回调函数。

    参数:
      callback_context: 一个 CallbackContext 对象，代表活动的回调上下文。
      llm_request: 一个 LlmRequest 对象，代表活动的 LLM 请求。
    """
    # 获取当前时间
    now = time.time()
    # 如果上下文中没有计时器开始时间，则初始化
    if "timer_start" not in callback_context.state:
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
        logger.debug(
            "rate_limit_callback [时间戳: %i, 请求计数: 1, "
            "已过秒数: 0]",
            now,
        )
        return

    # 请求计数加一
    request_count = callback_context.state["request_count"] + 1
    # 计算自上次重置以来的经过时间
    elapsed_secs = now - callback_context.state["timer_start"]
    logger.debug(
        "rate_limit_callback [时间戳: %i, 请求计数: %i,"
        " 已过秒数: %i]",
        now,
        request_count,
        elapsed_secs,
    )

    # 如果请求计数超过配额
    if request_count > RPM_QUOTA:
        # 计算需要延迟的时间
        delay = RATE_LIMIT_SECS - elapsed_secs + 1
        if delay > 0:
            logger.debug("休眠 %i 秒", delay)
            time.sleep(delay) # 暂停执行以满足速率限制
        # 重置计时器和请求计数
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
    else:
        # 更新请求计数
        callback_context.state["request_count"] = request_count

    return


