
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

"""FOMC Research Agent 的回调函数。"""

# 导入日志和时间模块
import logging
import time

# 导入 ADK 相关类
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from typing import Any, Dict
from google.adk.tools import BaseTool
from google.adk.agents.invocation_context import InvocationContext
# 从实体模块导入 Customer 类
from customer_service.entities.customer import Customer

# 配置日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 速率限制常量：时间窗口（秒）和每分钟请求配额
RATE_LIMIT_SECS = 60
RPM_QUOTA = 10


# 定义速率限制回调函数
def rate_limit_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    """实现查询速率限制的回调函数。

    参数:
      callback_context: 代表活动回调上下文的 CallbackContext 对象。
      llm_request: 代表活动 LLM 请求的 LlmRequest 对象。
    """
    # 遍历 LLM 请求内容，确保文本部分不为空字符串，替换为空格
    for content in llm_request.contents:
        for part in content.parts:
            if hasattr(part, 'text') and part.text == "": # 检查 part 是否有 text 属性
                part.text = " "

    # 获取当前时间戳
    now = time.time()
    # 如果状态中没有计时器开始时间，则初始化
    if "timer_start" not in callback_context.state:
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
        # 记录调试日志
        logger.debug(
            "速率限制回调 [时间戳: %i, 请求计数: 1, 已用秒数: 0]",
            now,
        )
        return

    # 请求计数加一
    request_count = callback_context.state["request_count"] + 1
    # 计算自计时器开始以来经过的秒数
    elapsed_secs = now - callback_context.state["timer_start"]
    # 记录调试日志
    logger.debug(
        "速率限制回调 [时间戳: %i, 请求计数: %i, 已用秒数: %i]",
        now,
        request_count,
        elapsed_secs,
    )

    # 如果请求计数超过配额
    if request_count > RPM_QUOTA:
        # 计算需要延迟的时间
        delay = RATE_LIMIT_SECS - elapsed_secs + 1
        # 如果需要延迟
        if delay > 0:
            logger.debug("休眠 %i 秒", delay)
            time.sleep(delay)
        # 重置计时器和请求计数
        callback_context.state["timer_start"] = time.time() # 使用更新后的时间
        callback_context.state["request_count"] = 1
    else:
        # 更新请求计数
        callback_context.state["request_count"] = request_count

    return


# 定义一个递归函数，将字典或列表中的字符串值转换为小写
def lowercase_value(value):
    """将字典值转换为小写"""
    if isinstance(value, dict):
        # 递归处理字典的值
        return {k: lowercase_value(v) for k, v in value.items()}
    elif isinstance(value, str):
        # 将字符串转换为小写
        return value.lower()
    elif isinstance(value, (list, set, tuple)):
        # 递归处理列表、集合或元组中的元素
        tp = type(value)
        return tp(lowercase_value(i) for i in value)
    else:
        # 其他类型保持不变
        return value


# 工具调用前的回调方法
def before_tool(
    tool: BaseTool, args: Dict[str, Any], tool_context: CallbackContext
):
    """在调用工具之前执行的回调函数。

    参数:
      tool: 被调用的工具对象。
      args: 传递给工具的参数字典。
      tool_context: 回调上下文。

    返回:
      如果需要覆盖工具的正常执行，则返回一个包含结果的字典，否则返回 None。
    """

    # 确保 Agent 发送给工具的所有值都是小写的
    lowercase_args = lowercase_value(args.copy()) # 创建副本以避免修改原始 args
    args.clear()
    args.update(lowercase_args)

    # 检查下一个工具调用并相应地采取行动。
    # 基于被调用工具的示例逻辑。
    if tool.name == "sync_ask_for_approval":
        # 获取折扣值
        amount = args.get("value", None)
        # 示例业务规则：如果折扣金额小于等于 10
        if amount is not None and amount <= 10:
            # 返回结果，阻止实际的工具调用
            return {
                "result": "您可以批准此折扣；无需经理批准。"
            }
        # 根据需要在此处添加更多逻辑检查。

    if tool.name == "modify_cart":
        # 检查是否同时添加和移除了商品
        if (
            args.get("items_to_add") # 检查是否存在 items_to_add
            and args.get("items_to_remove") # 检查是否存在 items_to_remove
        ):
            # 返回自定义结果
            return {"result": "我已经添加并移除了您请求的商品。"}
    # 如果没有特殊处理，返回 None，让工具正常执行
    return None


# 检查客户资料是否已加载为状态。
def before_agent(callback_context: InvocationContext):
    """在 Agent 处理请求之前执行的回调函数。

    参数:
      callback_context: 调用上下文。
    """
    # 如果状态中没有 "customer_profile"
    if "customer_profile" not in callback_context.state:
        # 从 Customer 类获取客户信息（使用固定 ID "123"）并将其转换为 JSON 存储在状态中
        callback_context.state["customer_profile"] = Customer.get_customer(
            "123"
        ).to_json()

    # 可以取消注释下面这行来记录客户资料信息
    # logger.info(callback_context.state["customer_profile"])


