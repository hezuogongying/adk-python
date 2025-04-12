
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

"""LLM Auditor 的测试用例。"""

# 导入必要的库
import textwrap # 用于处理多行文本缩进
import unittest # 用于单元测试

# 导入 dotenv 用于加载环境变量
import dotenv
# 从 google.adk.runners 导入 InMemoryRunner
from google.adk.runners import InMemoryRunner
# 从 google.genai.types 导入 Part 和 UserContent
from google.genai.types import Part
from google.genai.types import UserContent
# 导入 LLM Auditor 的根 agent
from llm_auditor.agent import root_agent
# 导入 pytest 用于测试 fixture
import pytest


# 使用 pytest fixture 在会话范围内自动加载环境变量
@pytest.fixture(scope="session", autouse=True)
def load_env():
    """加载 .env 文件中的环境变量。"""
    dotenv.load_dotenv()


class TestAgents(unittest.TestCase):
    """LLM Auditor agent 的基本测试。"""

    def test_happy_path(self):
        """在一个简单的输入上运行 agent，并期望得到一个正常的响应。"""
        # 定义用户输入，包含一个不准确的答案
        user_input = textwrap.dedent("""
            仔细检查这个：
            问题：为什么天空是蓝色的？
            答案：因为水是蓝色的。
        """).strip()

        # 使用 InMemoryRunner 初始化 agent 运行器
        runner = InMemoryRunner(agent=root_agent)
        # 创建一个测试会话
        session = runner.session_service.create_session(
            app_name=runner.app_name, user_id="test_user"
        )
        # 创建用户输入内容对象
        content = UserContent(parts=[Part(text=user_input)])
        # 运行 agent 并获取事件列表
        events = list(runner.run(
            user_id=session.user_id, session_id=session.id, new_message=content
        ))
        # 获取最后一个事件的响应文本
        response = events[-1].content.parts[0].text

        # 输入中的答案是错误的，所以我们期望 agent 提供一个修正后的答案，
        # 正确的答案应该提到散射（scattering）。
        self.assertIn("scattering", response.lower()) # 断言响应中包含 "scattering"（不区分大小写）


