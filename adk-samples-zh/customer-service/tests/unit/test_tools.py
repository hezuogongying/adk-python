
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

# 导入 pytest 测试框架
import pytest
# 从项目中导入配置类
from customer_service.config import Config
# 导入日志模块
import logging


# 定义一个 pytest fixture，用于创建 Config 实例
@pytest.fixture
def conf():
    """返回一个 Config 实例的 fixture。"""
    configs = Config()
    return configs


# 定义一个测试函数，用于测试配置加载
def test_settings_loading(conf):
    """测试配置设置是否正确加载。"""
    # 记录加载的配置信息（使用 Pydantic 的 model_dump 进行序列化）
    logging.info(conf.model_dump())
    # 断言：检查 Agent 模型名称是否以 "gemini" 开头
    assert conf.agent_settings.model.startswith("gemini")
    # 可以添加更多断言来检查其他配置项


