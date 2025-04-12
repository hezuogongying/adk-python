
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

# 导入 gym 库，用于创建和管理环境
import gym
# 从当前目录下的 web_agent_site 库导入 WebAgentTextEnv 类
from .web_agent_site.envs.web_agent_text_env import WebAgentTextEnv


def init_env(num_products):
    """初始化 WebAgentTextEnv 环境。

    参数:
        num_products (int): 环境中包含的产品数量。

    返回:
        gym.Env: 初始化后的环境实例。
    """
    # 使用 gym.make 创建 WebAgentTextEnv-v0 环境实例
    env = gym.make(
        "WebAgentTextEnv-v0", # 环境 ID
        observation_mode="text", # 设置观察模式为文本
        num_products=num_products, # 设置产品数量
    )
    return env


# 设置产品项目数量
num_product_items = 50000
# 初始化 WebShop 环境
webshop_env = init_env(num_product_items)
# 重置环境状态
webshop_env.reset()
# 打印初始化完成信息
print(f"已完成初始化 WebshopEnv，包含 {num_product_items} 个项目。")


