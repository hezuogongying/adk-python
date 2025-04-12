
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

"""一个演示 travel-concierge Agent 如何整合 MCP 工具的示例。"""

import asyncio # 用于异步操作
import json # 用于处理 JSON 数据

from dotenv import load_dotenv # 加载 .env 文件
# 导入内存 Artifact 服务
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner # 导入 ADK Runner
from google.adk.sessions import InMemorySessionService # 导入内存会话服务
from google.adk.tools.agent_tool import AgentTool # 导入 Agent 工具包装器
# 导入 MCP 工具集和标准输入输出服务器参数
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.genai import types # 导入 Gemini 类型
from travel_concierge.agent import root_agent # 导入 Travel Concierge 根 Agent


load_dotenv() # 加载环境变量


async def get_tools_async():
    """异步地从 MCP 服务器获取工具。"""
    # 使用 StdioServerParameters 启动本地 MCP 服务器（这里是 Airbnb 的示例服务器）
    # `npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt` 会下载并运行 Airbnb MCP 服务器
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command="npx", # 命令
            args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"], # 参数
        )
    )
    # MCP 需要维持与本地 MCP 服务器的连接。
    # 使用 exit_stack 在退出前清理服务器连接。
    return tools, exit_stack


def find_agent(agent, targat_name):
    """一个辅助函数，用于从现有的 Agent 图中查找指定名称的 Agent。"""
    result = None
    print("正在匹配...", agent.name)
    if agent.name == targat_name: # 如果当前 Agent 名称匹配
        return agent
    # 递归查找子 Agent
    for sub_agent in agent.sub_agents:
        result = find_agent(sub_agent, targat_name)
        if result:
            break
    # 递归查找工具中的 Agent (AgentTool)
    if not result: # 仅在尚未找到时继续查找工具
        for tool in agent.tools:
            if isinstance(tool, AgentTool):
                result = find_agent(tool.agent, targat_name)
                if result:
                    break
    return result


async def get_agent_async():
    """创建一个包含来自 MCP 服务器工具的 ADK Agent。"""
    tools, exit_stack = await get_tools_async() # 获取 MCP 工具
    print("\n正在将 Airbnb MCP 工具插入 Travel-Concierge...")
    # 查找名为 "planning_agent" 的子 Agent
    planner = find_agent(root_agent, "planning_agent")
    if planner:
        print("已找到", planner.name)
        # 将获取到的 MCP 工具添加到 planning_agent 的工具列表中
        planner.tools.extend(tools)
    else:
        print("未找到 planning_agent")
    # 返回修改后的根 Agent 和用于清理连接的 exit_stack
    return root_agent, exit_stack


async def async_main(question):
    """执行一轮 travel_concierge Agent 对话，查询会触发 MCP 工具。"""
    session_service = InMemorySessionService() # 使用内存会话服务
    artifacts_service = InMemoryArtifactService() # 使用内存 Artifact 服务
    # 创建一个新会话
    session = session_service.create_session(
        state={}, app_name="travel-concierge", user_id="traveler0115"
    )

    query = question # 用户输入
    print("[用户]: ", query)
    # 构建用户消息内容
    content = types.Content(role="user", parts=[types.Part(text=query)])

    # 获取集成了 MCP 工具的 Agent
    agent, exit_stack = await get_agent_async()
    # 创建 Runner 实例
    runner = Runner(
        app_name="travel-concierge",
        agent=agent, # 使用集成了 MCP 工具的 Agent
        artifact_service=artifacts_service,
        session_service=session_service,
    )

    # 异步运行 Agent
    events_async = runner.run_async(
        session_id=session.id, user_id="traveler0115", new_message=content
    )

    # 处理结果
    async for event in events_async:
        # {'error': 'Function activities_agent is not found in the tools_dict.'} # 示例错误信息
        if not event.content: # 跳过没有内容的事件
            continue

        # print(event) # 打印原始事件（用于调试）
        author = event.author # 获取事件作者

        # 提取函数调用和函数响应
        function_calls = [
            e.function_call for e in event.content.parts if hasattr(e, 'function_call') and e.function_call
        ]
        function_responses = [
            e.function_response for e in event.content.parts if hasattr(e, 'function_response') and e.function_response
        ]

        # 打印文本响应
        if event.content.parts and hasattr(event.content.parts[0], 'text') and event.content.parts[0].text:
            text_response = event.content.parts[0].text
            print(f"\n[{author}]: {text_response}")

        # 打印函数调用信息
        if function_calls:
            for function_call in function_calls:
                print(
                    f"\n[{author}]: {function_call.name}( {json.dumps(function_call.args)} )"
                )

        # 打印函数响应信息（对 airbnb_search 做特殊处理）
        elif function_responses:
            for function_response in function_responses:
                function_name = function_response.name
                # 处理不同的响应负载结构
                application_payload = function_response.response
                # 如果是 airbnb_search 工具的响应，提取其内部文本内容
                if function_name == "airbnb_search":
                    # 检查 payload 结构是否符合预期
                    if isinstance(application_payload, dict) and "result" in application_payload and \
                       isinstance(application_payload["result"], types.Content) and \
                       application_payload["result"].parts and \
                       hasattr(application_payload["result"].parts[0], 'text'):
                        application_payload = application_payload["result"].parts[0].text
                    else:
                        # 如果结构不符，打印原始 payload 以便调试
                        application_payload = json.dumps(application_payload)
                else:
                     application_payload = json.dumps(application_payload) # 其他工具直接打印 JSON

                print(
                    f"\n[{author}]: {function_name} 响应 -> {application_payload}"
                )

    # 关闭与 MCP 服务器的连接
    await exit_stack.aclose()


if __name__ == "__main__":
    # 运行主函数，并传入一个会触发 Airbnb 搜索的查询
    asyncio.run(
        async_main(
            (
                "帮我在圣地亚哥找一个 airbnb，4 月 9 日到 4 月 13 日，不需要航班和行程。"
                "无需确认，直接返回 5 个选择，记得包含 URL。"
            )
        )
    )


