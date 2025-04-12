
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

"""针对单个工具的基本测试。"""

import unittest # Python 单元测试框架

from dotenv import load_dotenv # 加载 .env 文件
# 导入 ADK 调用上下文
from google.adk.agents.invocation_context import InvocationContext
# 导入内存 Artifact 服务
from google.adk.artifacts import InMemoryArtifactService
# 导入内存会话服务
from google.adk.sessions import InMemorySessionService
# 导入 ADK 工具上下文
from google.adk.tools import ToolContext
import pytest # 测试框架 (主要用于 fixture)
from travel_concierge.agent import root_agent # 导入根 Agent
from travel_concierge.tools.memory import memorize # 导入 memorize 工具
from travel_concierge.tools.places import map_tool # 导入 map_tool 工具


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """(自动执行的会话级 fixture) 加载 .env 文件中的环境变量"""
    load_dotenv()


# 初始化内存服务实例
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()


class TestAgents(unittest.TestCase): # 使用 unittest.TestCase 作为基类
    """Travel Concierge Agent 群组的测试用例。"""

    def setUp(self):
        """为测试方法设置环境。"""
        super().setUp()
        # 创建一个内存会话
        self.session = session_service.create_session(
            app_name="Travel_Concierge",
            user_id="traveler0115",
        )
        self.user_id = "traveler0115"
        self.session_id = self.session.id

        # 创建调用上下文 (InvocationContext)
        self.invoc_context = InvocationContext(
            session_service=session_service,
            invocation_id="ABCD", # 模拟的调用 ID
            agent=root_agent, # 关联的 Agent
            session=self.session, # 当前会话
        )
        # 创建工具上下文 (ToolContext)
        self.tool_context = ToolContext(invocation_context=self.invoc_context)

    def test_memory(self):
        """测试 memorize 工具。"""
        # 调用 memorize 工具
        result = memorize(
            key="itinerary_datetime", # 要存储的键
            value="12/31/2025 11:59:59", # 要存储的值
            tool_context=self.tool_context, # 传递工具上下文
        )
        # 断言结果包含 'status' 键
        self.assertIn("status", result)
        # 断言状态中已正确存储值
        self.assertEqual(
            self.tool_context.state["itinerary_datetime"], "12/31/2025 11:59:59"
        )

    @unittest.skipIf(not os.getenv("GOOGLE_PLACES_API_KEY"), "需要 GOOGLE_PLACES_API_KEY 才能运行此测试")
    def test_places(self):
        """测试 map_tool 工具（需要 Places API 密钥）。"""
        # 在工具上下文中设置模拟的 POI 数据
        self.tool_context.state["poi"] = {
            "places": [{"place_name": "Machu Picchu", "address": "Machu Picchu, Peru"}]
        }
        # 调用 map_tool 工具
        result = map_tool(key="poi", tool_context=self.tool_context)
        print(result) # 打印结果以供检查
        # 断言返回的 POI 列表中第一个元素的 'place_id' 存在
        self.assertIn("place_id", result[0])
        # 断言获取到的 place_id 与预期值一致（这个值可能会变化，测试可能不稳定）
        self.assertEqual(
            result[0]["place_id"], # 从 map_tool 返回结果中获取 place_id
            # 预期值
            "ChIJVVVViV-abZERJxqgpA43EDo",
        )
        # 也可以检查状态是否被更新
        # self.assertEqual(
        #     self.tool_context.state["poi"]["places"][0]["place_id"],
        #     "ChIJVVVViV-abZERJxqgpA43EDo",
        # )



