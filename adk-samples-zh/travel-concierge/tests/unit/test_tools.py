
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

"""这是一个基础示例，展示了如何将 ADK Agent 作为服务器端点进行交互。"""

import json
import requests # 用于发送 HTTP 请求

#
# 此客户端连接到一个已存在的端点，该端点通过运行 `adk api_server <agent package>` 创建。
# 此客户端还演示了如何使用从服务器端流式传输的 ADK 事件来通知用户界面组件。
#

# 通过运行 `adk api_server travel_concierge` 创建的端点
RUN_ENDPOINT = "http://127.0.0.1:8000/run_sse" # SSE (Server-Sent Events) 运行端点
HEADERS = { # 请求头
    "Content-Type": "application/json; charset=UTF-8", # 内容类型为 JSON
    "Accept": "text/event-stream", # 接受 SSE 事件流
}

# 如果会话不存在则创建会话
SESSION_ENDPOINT = "http://127.0.0.1:8000/apps/travel_concierge/users/traveler0115/sessions/session_2449" # 会话管理端点
response = requests.post(SESSION_ENDPOINT) # 发送 POST 请求创建或获取会话
print("会话", response.json()) # 打印会话信息

# 我们将与 Concierge 进行两轮对话
user_inputs = [
    "给我一些关于马尔代夫的旅行灵感",
    "给我展示一些芭环礁附近的活动",
]

# 遍历用户输入
for user_input in user_inputs:

    # 构建发送给运行端点的数据
    DATA = {
        "session_id": "session_2449", # 会话 ID
        "app_name": "travel_concierge", # 应用名称
        "user_id": "traveler0115", # 用户 ID
        "new_message": { # 新的用户消息
            "role": "user", # 角色为用户
            "parts": [
                {
                    "text": user_input, # 消息文本
                }
            ],
        },
    }

    print(f'\n[用户]: "{user_input}"')

    # 发送 POST 请求到运行端点，启用流式传输
    with requests.post(
        RUN_ENDPOINT, data=json.dumps(DATA), headers=HEADERS, stream=True
    ) as r:
        # 迭代处理从服务器接收到的 SSE 事件
        for chunk in r.iter_lines():
            # 这些事件及其内容可以被检查和利用。
            # 这是应用程序集成的基础；
            if not chunk: # 跳过空块
                continue
            # 解码 SSE 数据部分（移除 "data: " 前缀）并解析为 JSON
            json_string = chunk.decode("utf-8").removeprefix("data: ").strip()
            event = json.loads(json_string)

            # {'error': 'Function activities_agent is not found in the tools_dict.'} # 错误事件示例
            if "content" not in event: # 如果事件没有内容（可能是错误或其他类型的事件）
                print(event)
                continue

            author = event["author"] # 获取事件作者
            # 取消注释以查看完整的事件负载
            # print(f"\n[{author}]: {json.dumps(event)}")
            # continue

            # 从事件内容中提取函数调用和函数响应
            function_calls = [
                e["functionCall"]
                for e in event["content"]["parts"]
                if "functionCall" in e
            ]
            function_responses = [
                e["functionResponse"]
                for e in event["content"]["parts"]
                if "functionResponse" in e
            ]

            # 打印文本响应
            if "text" in event["content"]["parts"][0]:
                text_response = event["content"]["parts"][0]["text"]
                print(f"\n{author} {text_response}")

            # 打印函数调用信息
            if function_calls:
                for function_call in function_calls:
                    name = function_call["name"]
                    args = function_call["args"]
                    print(
                        f'\n{author}\n函数调用: "{name}"\n参数: {json.dumps(args,indent=2)}\n'
                    )

            # 打印函数响应信息
            elif function_responses:
                for function_response in function_responses:
                    function_name = function_response["name"]
                    # 将响应内容格式化为 JSON 字符串以便打印
                    application_payload = json.dumps(
                        function_response["response"], indent=2
                    )
                    print(
                        # 修正：这里的 name 应该是 function_name
                        f'\n{author}\n来自 "{function_name}" 的响应:\n响应内容: {application_payload}\n'
                    )

                    # 应用程序可以根据响应来自哪个 Agent/工具来采取行动。
                    # 使用 switch case 语句根据 function_name 进行判断
                    match function_name:
                        case "place_agent":
                            print("\n[应用]: 渲染目的地轮播图")
                        case "map_tool":
                            print("\n[应用]: 渲染兴趣点地图")
                        case "flight_selection_agent":
                            print("\n[应用]: 渲染航班列表")
                        case "hotel_selection_agent":
                            print("\n[应用]: 渲染酒店列表")
                    # ... 等等


