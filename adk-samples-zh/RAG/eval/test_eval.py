
import os
import vertexai
from vertexai import agent_engines # 导入 Vertex AI Agent Engine 相关库
from dotenv import load_dotenv
import json

def pretty_print_event(event):
    """美化打印事件，对长内容进行截断。"""
    if "content" not in event: # 如果事件没有 'content' 字段
        print(f"[{event.get('author', 'unknown')}]: {event}") # 直接打印事件
        return

    author = event.get("author", "unknown") # 获取事件作者
    parts = event["content"].get("parts", []) # 获取内容部分

    for part in parts:
        if "text" in part:
            text = part["text"]
            # 将长文本截断为 200 个字符
            if len(text) > 200:
                text = text[:197] + "..."
            print(f"[{author}]: {text}")
        elif "functionCall" in part: # 如果是函数调用
            func_call = part["functionCall"]
            print(f"[{author}]: 函数调用: {func_call.get('name', 'unknown')}")
            # 如果参数过长则截断
            args = json.dumps(func_call.get("args", {}))
            if len(args) > 100:
                args = args[:97] + "..."
            print(f"  参数: {args}")
        elif "functionResponse" in part: # 如果是函数响应
            func_response = part["functionResponse"]
            print(f"[{author}]: 函数响应: {func_response.get('name', 'unknown')}")
            # 如果响应过长则截断
            response = json.dumps(func_response.get("response", {}))
            if len(response) > 100:
                response = response[:97] + "..."
            print(f"  响应: {response}")

# 加载 .env 文件中的环境变量
load_dotenv()

# 初始化 Vertex AI SDK
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)

# 从环境变量获取已部署的 Agent Engine ID
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID")

# 获取 Agent Engine 实例
agent_engine = agent_engines.get(AGENT_ENGINE_ID)

# 创建一个新的会话
session = agent_engine.create_session(user_id="123") # 指定用户 ID

# 定义一系列要发送给 Agent 的查询
queries = [
    "你好，最近怎么样？",
    "根据 MD&A，像 Google Cloud 和设备这样的非广告来源收入占比不断增加，可能会如何影响 Alphabet 的整体运营利润率？为什么？",
    "报告提到了对人工智能的大量投资。这些人工智能投资与公司对未来资本支出的预期之间有何具体联系？",
    "Alphabet 业务运营相关的关键风险和不确定性有哪些？",
    "谢谢，我已经得到了所有需要的信息。再见！",
]

# 遍历查询并与 Agent 交互
for query in queries:
    print(f"\n[用户]: {query}")
    # 使用 stream_query 与 Agent 进行流式交互
    for event in agent_engine.stream_query(
        user_id="123", # 用户 ID
        session_id=session['id'], # 当前会话 ID
        message=query, # 发送的消息
    ):
        # 美化打印每个事件
        pretty_print_event(event)

