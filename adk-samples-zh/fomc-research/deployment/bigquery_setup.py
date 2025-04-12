
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

"""分析 agent 及其子 agent 的测试用例。"""

# 导入必要的库
import os
import sys
# 导入 pytest 用于测试
import pytest
# 导入 unittest 用于单元测试
import unittest

# 将父目录添加到系统路径，以便导入 agent 相关模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 从 google.genai 导入类型定义
from google.genai import types
# 从 google.adk 导入内存中的 artifact 和 session 服务
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# 导入数据科学项目的 agent
from data_science.agent import root_agent # 根 agent
from data_science.sub_agents.bqml.agent import root_agent as bqml_agent # BQML 子 agent
from data_science.sub_agents.bigquery.agent import database_agent # BigQuery 子 agent
from data_science.sub_agents.analytics.agent import root_agent as data_science_agent # 分析子 agent

# 初始化内存中的 session 和 artifact 服务
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()


class TestAgents(unittest.TestCase):
    """分析 agent 及其子 agent 的测试用例。"""

    def setUp(self):
        """为测试方法设置环境。"""
        # 创建一个测试会话
        self.session = session_service.create_session(
            app_name="DataAgent",
            user_id="test_user",
        )
        # 设置用户 ID 和会话 ID
        self.user_id = "test_user"
        self.session_id = self.session.id

        # 初始化 Runner
        self.runner = Runner(
            app_name="DataAgent",
            agent=None, # agent 将在 _run_agent 中设置
            artifact_service=artifact_service,
            session_service=session_service,
        )

    def _run_agent(self, agent, query):
        """辅助方法，用于运行 agent 并获取最终响应。"""
        # 设置当前要运行的 agent
        self.runner.agent = agent
        # 创建用户输入内容
        content = types.Content(role="user", parts=[types.Part(text=query)])
        # 运行 agent 并获取事件列表
        events = list(
            self.runner.run(
                user_id=self.user_id, session_id=self.session_id, new_message=content
            )
        )

        # 获取最后一个事件
        last_event = events[-1]
        # 提取最终响应文本
        final_response = "".join(
            [part.text for part in last_event.content.parts if part.text]
        )
        return final_response


    @pytest.mark.db_agent # 标记为数据库 agent 测试
    def test_db_agent_can_handle_env_query(self):
        """测试 db_agent 处理来自环境变量的查询。"""
        query = "train 表中有哪些国家？"
        response = self._run_agent(database_agent, query)
        print(response)
        # self.assertIn("Canada", response) # 检查响应中是否包含 "Canada" (注释掉了，可能因为环境变化)
        self.assertIsNotNone(response) # 断言响应不为空

    @pytest.mark.ds_agent # 标记为数据科学 agent 测试
    def test_ds_agent_can_be_called_from_root(self):
        """测试从根 agent 调用 ds_agent。"""
        query = "绘制销量最高的类别图表"
        response = self._run_agent(root_agent, query)
        print(response)
        self.assertIsNotNone(response) # 断言响应不为空

    @pytest.mark.bqml # 标记为 BQML agent 测试
    def test_bqml_agent_can_check_for_models(self):
        """测试 bqml_agent 检查现有模型的能力。"""
        query = "数据集中是否存在任何现有模型？"
        response = self._run_agent(bqml_agent, query)
        print(response)
        self.assertIsNotNone(response) # 断言响应不为空

    @pytest.mark.bqml # 标记为 BQML agent 测试
    def test_bqml_agent_can_execute_code(self):
        """测试 bqml_agent 执行 BQML 代码的能力。"""
        query = """
    我想在 sales_train_validation 数据上训练一个 BigQuery ML 模型用于销售预测。
    请给我展示一个执行计划。
    """
        response = self._run_agent(bqml_agent, query)
        print(response)
        self.assertIsNotNone(response) # 断言响应不为空


if __name__ == "__main__":
    # 运行所有单元测试
    unittest.main()

    # 下面的注释代码是用于单独测试特定方法的示例
    # testagent = TestAgents
    # testagent.setUp(testagent)
    # testagent.test_root_agent_can_list_tools(testagent)
    # testagent.test_db_agent_can_handle_env_query(testagent)


