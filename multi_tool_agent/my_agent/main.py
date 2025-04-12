# 导入必要的库
from google.adk.agents.sequential_agent import SequentialAgent  # 导入顺序代理
from google.adk.agents.llm_agent import LlmAgent  # 导入LLM代理
from google.adk.agents import Agent  # 导入基础代理类
from google.genai import types  # 导入类型定义
from google.adk.sessions import InMemorySessionService  # 导入内存会话服务
from google.adk.runners import Runner  # 导入运行器
from google.adk.tools import FunctionTool  # 导入函数工具，用于创建自定义工具

# --- 常量定义 ---
APP_NAME = "code_pipeline_app"  # 应用名称
USER_ID = "dev_user_01"  # 用户ID
SESSION_ID = "pipeline_session_01"  # 会话ID
GEMINI_MODEL = "gemini-2.0-flash-exp"  # 使用的Gemini模型

# --- 1. 定义代码处理管道的各个阶段子代理 ---
# 代码编写代理
# 接收初始规格说明(来自用户查询)并编写代码
code_writer_agent = LlmAgent(
    name="CodeWriterAgent",  # 代理名称
    model=GEMINI_MODEL,  # 使用的模型
    instruction="""你是一个代码编写AI。
    根据用户的请求，编写初始Python代码。
    只输出原始代码块。
    """,  # 代理指令（中文版）
    description="根据规格说明编写初始代码。",  # 代理描述
    # 将其输出(生成的代码)存储到会话状态中
    # 键名为'generated_code'
    output_key="generated_code"  # 输出键，用于存储代理输出到会话状态
)

# 代码审查代理
# 读取上一个代理生成的代码(从状态中读取)并提供反馈
code_reviewer_agent = LlmAgent(
    name="CodeReviewerAgent",  # 代理名称
    model=GEMINI_MODEL,  # 使用的模型
    instruction="""你是一个代码审查AI。
    审查会话状态中键名为'generated_code'的Python代码。
    提供关于潜在错误、风格问题或改进的建设性反馈。
    注重清晰度和正确性。
    仅输出审查评论。
    """,  # 代理指令（中文版）
    description="审查代码并提供反馈。",  # 代理描述
    # 将其输出(审查评论)存储到会话状态中
    # 键名为'review_comments'
    output_key="review_comments"  # 输出键，用于存储代理输出到会话状态
)

# 代码重构代理
# 获取原始代码和审查评论(从状态中读取)并重构代码
code_refactorer_agent = LlmAgent(
    name="CodeRefactorerAgent",  # 代理名称
    model=GEMINI_MODEL,  # 使用的模型
    instruction="""你是一个代码重构AI。
    获取会话状态键'generated_code'中的原始Python代码
    以及会话状态键'review_comments'中的审查评论。
    重构原始代码以解决反馈并提高其质量。
    仅输出最终的、重构后的代码块。
    """,  # 代理指令（中文版）
    description="根据审查评论重构代码。",  # 代理描述
    # 将其输出(重构的代码)存储到会话状态中
    # 键名为'refactored_code'
    output_key="refactored_code"  # 输出键，用于存储代理输出到会话状态
)

# --- 2. 创建顺序代理 ---
# 这个代理通过按顺序运行子代理来编排流水线
code_pipeline_agent = SequentialAgent(
    name="CodePipelineAgent",  # 顺序代理名称
    sub_agents=[code_writer_agent, code_reviewer_agent, code_refactorer_agent]
    # 子代理将按提供的顺序运行：编写器 -> 审查器 -> 重构器
)

# --- 3. 创建一个函数作为工具 ---
def process_code_request(request: str) -> str:
    """
    使用代码处理管道处理用户的代码请求。

    Args:
        request (str): 用户的代码请求，如"创建一个计算加法的函数"

    Returns:
        str: 处理后的最终代码
    """
    print(f"处理代码请求: {request}")
    # 这个函数实际上不会被执行，而是被LLM用来理解它应该如何使用code_pipeline_agent
    # 真正的执行是通过root_agent对code_pipeline_agent的委托实现的
    return "最终的代码将在这里返回"

# --- 4. 创建根代理 ---
root_agent = Agent(
    name="CodeAssistant",  # 根代理名称
    model=GEMINI_MODEL,  # 使用的模型
    instruction="""你是一个代码助手AI。
    你的角色是通过三步流水线帮助用户改进代码：
    1. 根据规格说明编写初始代码
    2. 审查代码以发现问题和改进
    3. 根据审查反馈重构代码

    当用户请求代码帮助时，使用code_pipeline_agent来处理请求。
    将最终的、重构后的代码作为你的响应呈现给用户。
    """,  # 根代理指令（中文版）
    description="通过编写-审查-重构流水线改进代码的助手。",  # 根代理描述
    # 不在工具中添加code_pipeline_agent，而是作为子代理
    tools=[],  # 这里可以为空，或者添加其他工具
    sub_agents=[code_pipeline_agent]  # 将code_pipeline_agent作为子代理
)

# 会话和运行器设置
session_service = InMemorySessionService()  # 创建内存会话服务
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)  # 创建会话
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)  # 创建运行器

# 代理交互函数
def call_agent(query):
    """
    调用代理并处理用户查询

    Args:
        query (str): 用户的查询文本
    """
    content = types.Content(role='user', parts=[types.Part(text=query)])  # 创建用户内容
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)  # 运行代理
    for event in events:  # 遍历事件
        if event.is_final_response():  # 如果是最终响应
            final_response = event.content.parts[0].text  # 获取响应文本
            print("代理响应: ", final_response)  # 打印响应

# 调用代理进行测试
call_agent("执行数学加法")  # 测试查询
