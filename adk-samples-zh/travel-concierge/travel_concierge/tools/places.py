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

"""'memorize' (记忆) 工具，供多个 agent 用来影响会话状态 (session states)。"""

from datetime import datetime
import json
import os
from typing import Dict, Any, Union # 引入 Union

from google.adk.agents.callback_context import CallbackContext
from google.adk.sessions.state import State
from google.adk.tools import ToolContext

from travel_concierge.shared_libraries import constants # 导入常量

# 定义示例场景文件的路径，从环境变量获取，若未设置则使用默认值
SAMPLE_SCENARIO_PATH = os.getenv(
    "TRAVEL_CONCIERGE_SCENARIO", "eval/itinerary_empty_default.json"
)


def memorize_list(key: str, value: str, tool_context: ToolContext):
    """
    记忆（存储）信息片段，将值添加到指定键的列表中。
    如果值已存在于列表中，则不重复添加。

    Args:
        key: 索引记忆的标签（键名），值将存储在此键对应的列表中。
        value: 要存储的信息。
        tool_context: ADK 工具上下文 (ToolContext)，包含会话状态 (state)。

    Returns:
        一个包含状态消息的字典。
    """
    mem_dict = tool_context.state # 获取当前会话状态字典
    # 如果键不存在于状态中，初始化为空列表
    if key not in mem_dict:
        mem_dict[key] = []
    # 如果值不在列表中，则添加它
    if value not in mem_dict[key]:
        mem_dict[key].append(value)
    # 返回操作状态信息
    return {"status": f'已存储 "{key}": "{value}" (作为列表项)'}


def memorize(key: str, value: Any, tool_context: ToolContext): # value 类型改为 Any
    """
    记忆（存储）信息片段，一次存储一个键值对。
    如果键已存在，则覆盖旧值。

    Args:
        key: 索引记忆的标签（键名）。
        value: 要存储的信息 (可以是任何类型)。
        tool_context: ADK 工具上下文 (ToolContext)，包含会话状态 (state)。

    Returns:
        一个包含状态消息的字典。
    """
    mem_dict = tool_context.state # 获取当前会话状态字典
    mem_dict[key] = value # 直接设置键值对，会覆盖已有值
    # 返回操作状态信息
    # 注意：如果 value 是复杂对象 (如字典)，可能需要更友好的日志记录
    value_str = str(value)
    if len(value_str) > 50: # 避免打印过长的值
        value_str = value_str[:50] + "..."
    return {"status": f'已存储 "{key}": "{value_str}"'}


def forget(key: str, value: str, tool_context: ToolContext):
    """
    遗忘（移除）信息片段。仅适用于值为列表的情况。

    Args:
        key: 索引记忆的标签（键名），其值应为列表。
        value: 要从列表中移除的信息。
        tool_context: ADK 工具上下文 (ToolContext)，包含会话状态 (state)。

    Returns:
        一个包含状态消息的字典。
    """
    # 检查键是否存在且其值是否为列表
    if key in tool_context.state and isinstance(tool_context.state[key], list):
        # 如果值存在于列表中，则移除它
        if value in tool_context.state[key]:
            tool_context.state[key].remove(value)
            return {"status": f'已移除 "{key}" 中的值: "{value}"'}
        else:
            return {"status": f'值 "{value}" 不在列表 "{key}" 中'}
    else:
        # 如果键不存在或值不是列表，返回错误或提示信息
        if key not in tool_context.state:
             return {"status": f'键 "{key}" 不存在'}
        else:
             return {"status": f'键 "{key}" 的值不是列表，无法移除元素'}


# 类型提示 Union[State, dict[str, Any]] 用于兼容不同上下文
def _set_initial_states(source: Dict[str, Any], target: Union[State, dict[str, Any]]):
    """
    根据给定的 JSON 对象设置初始会话状态。

    Args:
        source: 包含状态信息的 JSON 对象（通常来自配置文件）。
        target: 要插入状态的目标会话状态对象 (State 或普通字典)。
    """
    # 如果系统中尚未设置时间，则设置当前时间
    if constants.SYSTEM_TIME not in target:
        target[constants.SYSTEM_TIME] = str(datetime.now())

    # 确保只初始化一次
    if constants.ITIN_INITIALIZED not in target or not target[constants.ITIN_INITIALIZED]:
        target[constants.ITIN_INITIALIZED] = True # 标记为已初始化

        # 将 source 中的所有键值对更新到 target 中
        # 注意：这可能会覆盖 target 中已有的同名键
        target.update(source)

        # 从加载的行程信息中提取关键日期并存入状态
        itinerary = source.get(constants.ITIN_KEY, {}) # 获取行程信息，如果不存在则为空字典
        if itinerary: # 确保行程信息存在
            # 存储行程开始日期
            if constants.START_DATE in itinerary:
                target[constants.ITIN_START_DATE] = itinerary[constants.START_DATE]
            # 存储行程结束日期
            if constants.END_DATE in itinerary:
                target[constants.ITIN_END_DATE] = itinerary[constants.END_DATE]
            # 存储或初始化行程的当前模拟日期时间，默认为开始日期
            # 这通常用于 day_of agent 模拟当天进程
            if constants.START_DATE in itinerary:
                target[constants.ITIN_DATETIME] = itinerary[constants.START_DATE] + " 00:00" # 假设初始时间为开始日期的午夜


def _load_precreated_itinerary(callback_context: CallbackContext):
    """
    设置初始状态。
    将其设置为 root_agent 的 before_agent_call 回调函数。
    此函数在构建系统指令 (system instruction) 之前被调用。

    Args:
        callback_context: 回调上下文 (CallbackContext)，包含会话状态 (state)。
    """
    data = {}
    try:
        # 从指定的 JSON 文件加载初始状态数据
        with open(SAMPLE_SCENARIO_PATH, "r", encoding='utf-8') as file: # 指定编码
            data = json.load(file)
            print(f"\n加载初始状态: {SAMPLE_SCENARIO_PATH}\n内容: {json.dumps(data, indent=2, ensure_ascii=False)}\n") # 打印加载信息

        # 使用加载的数据设置初始会话状态
        _set_initial_states(data.get("state", {}), callback_context.state) # 确保传入 state 部分

    except FileNotFoundError:
        print(f"\n错误：找不到初始状态文件: {SAMPLE_SCENARIO_PATH}\n将使用空状态初始化。\n")
        # 即使文件不存在，也尝试设置默认状态或标记
        _set_initial_states({}, callback_context.state)
    except json.JSONDecodeError:
        print(f"\n错误：解析初始状态文件失败: {SAMPLE_SCENARIO_PATH}\n文件可能不是有效的 JSON。\n将使用空状态初始化。\n")
        _set_initial_states({}, callback_context.state)
    except Exception as e:
        print(f"\n加载初始状态时发生未知错误: {e}\n将使用空状态初始化。\n")
        _set_initial_states({}, callback_context.state)

