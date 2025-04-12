
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
# limitations under the License.§

"""客户服务 Agent 的 Agent 模块。"""

# 导入日志和警告处理模块
import logging
import warnings
# 导入 ADK 的 Agent 类
from google.adk import Agent
# 从当前包导入配置类
from .config import Config
# 从当前包导入 prompts
from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION
# 从共享库导入回调函数
from .shared_libraries.callbacks import (
    rate_limit_callback, #速率限制回调
    before_agent,       # Agent 调用前回调
    before_tool,        # 工具调用前回调
)
# 从工具模块导入所有定义的工具
from .tools.tools import (
    send_call_companion_link,   # 发送通话伴侣链接
    approve_discount,          # 批准折扣
    sync_ask_for_approval,      # 同步请求批准
    update_salesforce_crm,     # 更新 Salesforce CRM
    access_cart_information,   # 访问购物车信息
    modify_cart,               # 修改购物车
    get_product_recommendations,# 获取产品推荐
    check_product_availability,# 检查产品可用性
    schedule_planting_service, # 安排种植服务
    get_available_planting_times,# 获取可用种植时间
    send_care_instructions,    # 发送养护说明
    generate_qr_code,          # 生成二维码
)

# 忽略 pydantic 相关的 UserWarning
warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

# 加载配置
configs = Config()

# 配置日志记录器
logger = logging.getLogger(__name__)


# 定义根 Agent (root_agent)
root_agent = Agent(
    # 使用配置中指定的模型
    model=configs.agent_settings.model,
    # 全局指令
    global_instruction=GLOBAL_INSTRUCTION,
    # 主要指令
    instruction=INSTRUCTION,
    # Agent 名称 (从配置中获取)
    name=configs.agent_settings.name,
    # Agent 可用的工具列表
    tools=[
        send_call_companion_link,
        approve_discount,
        sync_ask_for_approval,
        update_salesforce_crm,
        access_cart_information,
        modify_cart,
        get_product_recommendations,
        check_product_availability,
        schedule_planting_service,
        get_available_planting_times,
        send_care_instructions,
        generate_qr_code,
    ],
    # 注册工具调用前的回调函数
    before_tool_callback=before_tool,
    # 注册 Agent 调用前的回调函数
    before_agent_callback=before_agent,
    # 注册模型调用前的回调函数（用于速率限制）
    before_model_callback=rate_limit_callback,
)


