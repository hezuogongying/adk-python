
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

# 导入时间模块
import time
# 导入 PIL 库用于图像处理
from PIL import Image

# 导入 Selenium 相关库
import selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# 导入 ADK 相关库
from google.adk.agents.llm_agent import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.load_artifacts_tool import load_artifacts_tool
# 导入 Google Generative AI 类型库
from google.genai import types

# 从当前目录导入 prompt
from . import prompt
# 从上层目录的共享库导入常量
from ...shared_libraries import constants

# 导入 warnings 模块用于忽略警告
import warnings

# 忽略 Pydantic 相关的 UserWarning
warnings.filterwarnings("ignore", category=UserWarning)

# 如果常量 DISABLE_WEB_DRIVER 未设置（即为 0），则初始化 Selenium WebDriver
if not constants.DISABLE_WEB_DRIVER:
    # 创建 Chrome WebDriver 选项
    options = Options()
    # 设置窗口大小
    options.add_argument("--window-size=1920x1080")
    # 启用详细日志
    options.add_argument("--verbose")
    # 指定用户数据目录
    options.add_argument("user-data-dir=/tmp/selenium")

    # 初始化 Chrome WebDriver
    driver = selenium.webdriver.Chrome(options=options)


# 定义一个工具函数：导航到指定 URL
def go_to_url(url: str) -> str:
    """使用浏览器导航到给定的 URL。"""
    # 打印导航日志
    print(f"🌐 正在导航到 URL: {url}")
    # WebDriver 执行导航操作
    driver.get(url.strip())
    # 返回导航状态信息
    return f"已导航到 URL: {url}"


# 定义一个工具函数：截屏并保存为 artifact
def take_screenshot(tool_context: ToolContext) -> dict:
    """截屏并使用给定的文件名保存。之后调用 'load artifacts' 来加载图像。"""
    # 生成带时间戳的文件名
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    # 打印截屏日志
    print(f"📸 正在截屏并另存为: {filename}")
    # WebDriver 保存截屏
    driver.save_screenshot(filename)

    # 使用 PIL 打开图像文件
    image = Image.open(filename)

    # 将图像文件保存为 artifact
    tool_context.save_artifact(
        filename,
        # 从字节数据创建 Part 对象，指定 MIME 类型为 PNG
        types.Part.from_bytes(data=image.tobytes(), mime_type="image/png"),
    )

    # 返回状态和文件名
    return {"status": "ok", "filename": filename}


# 定义一个工具函数：在指定坐标点击
def click_at_coordinates(x: int, y: int) -> str:
    """在屏幕上的指定坐标处点击。"""
    # 执行 JavaScript 滚动到指定坐标
    driver.execute_script(f"window.scrollTo({x}, {y});")
    # 在 body 元素上模拟点击
    driver.find_element(By.TAG_NAME, "body").click()


# 定义一个工具函数：查找包含指定文本的元素
def find_element_with_text(text: str) -> str:
    """在页面上查找包含给定文本的元素。"""
    # 打印查找日志
    print(f"🔍 正在查找包含文本的元素: '{text}'")

    try:
        # 使用 XPath 查找元素
        element = driver.find_element(By.XPATH, f"//*[text()='{text}']")
        # 如果找到元素，返回成功信息
        if element:
            return "找到元素。"
        # 如果未找到，返回未找到信息
        else:
            return "未找到元素。"
    # 捕获未找到元素的异常
    except selenium.common.exceptions.NoSuchElementException:
        return "未找到元素。"
    # 捕获元素不可交互的异常
    except selenium.common.exceptions.ElementNotInteractableException:
        return "元素不可交互，无法点击。"


# 定义一个工具函数：点击包含指定文本的元素
def click_element_with_text(text: str) -> str:
    """点击页面上包含给定文本的元素。"""
    # 打印点击日志
    print(f"🖱️ 正在点击包含文本的元素: '{text}'")

    try:
        # 使用 XPath 查找元素
        element = driver.find_element(By.XPATH, f"//*[text()='{text}']")
        # 点击元素
        element.click()
        # 返回点击成功信息
        return f"已点击包含文本的元素: {text}"
    # 捕获未找到元素的异常
    except selenium.common.exceptions.NoSuchElementException:
        return "未找到元素，无法点击。"
    # 捕获元素不可交互的异常
    except selenium.common.exceptions.ElementNotInteractableException:
        return "元素不可交互，无法点击。"
    # 捕获点击被拦截的异常
    except selenium.common.exceptions.ElementClickInterceptedException:
        return "元素点击被拦截，无法点击。"


# 定义一个工具函数：在指定 ID 的元素中输入文本
def enter_text_into_element(text_to_enter: str, element_id: str) -> str:
    """将文本输入到具有给定 ID 的元素中。"""
    # 打印输入日志
    print(
        f"📝 正在将文本 '{text_to_enter}' 输入到 ID 为 {element_id} 的元素中"
    )

    try:
        # 通过 ID 查找输入元素
        input_element = driver.find_element(By.ID, element_id)
        # 在元素中输入文本
        input_element.send_keys(text_to_enter)
        # 返回输入成功信息
        return (
            f"已将文本 '{text_to_enter}' 输入到 ID 为 {element_id} 的元素中"
        )
    # 捕获未找到元素的异常
    except selenium.common.exceptions.NoSuchElementException:
        return "未找到具有给定 ID 的元素。"
    # 捕获元素不可交互的异常
    except selenium.common.exceptions.ElementNotInteractableException:
        return "元素不可交互，无法点击。"


# 定义一个工具函数：向下滚动屏幕
def scroll_down_screen() -> str:
    """向下滚动屏幕一段适中的距离。"""
    # 打印滚动日志
    print("⬇️ 向下滚动屏幕")
    # 执行 JavaScript 向下滚动 500 像素
    driver.execute_script("window.scrollBy(0, 500)")
    # 返回滚动成功信息
    return "已向下滚动屏幕。"


# 定义一个工具函数：获取页面源代码
def get_page_source() -> str:
    """返回当前页面的源代码。"""
    # 设置源代码长度限制
    LIMIT = 1000000
    # 打印获取日志
    print("📄 正在获取页面源代码...")
    # 返回截断后的页面源代码
    return driver.page_source[0:LIMIT]


# 定义一个工具函数：分析网页并决定下一步操作
def analyze_webpage_and_determine_action(
    page_source: str, user_task: str, tool_context: ToolContext
) -> str:
    """分析网页并确定下一步操作（滚动、点击等）。"""
    # 打印分析日志
    print(
        "🤔 正在分析网页并确定下一步操作..."
    )

    # 定义用于分析的 prompt
    analysis_prompt = f"""
    你是一位专业的网页分析师。
    你的任务是控制网络浏览器以实现用户的目标。
    用户的任务是：{user_task}
    这是当前网页的 HTML 源代码：
    ```html
    {page_source}
    ```

    根据网页内容和用户任务，确定下一步最佳操作。
    考虑的操作包括：补全页面源代码，向下滚动以查看更多内容，点击链接或按钮进行导航，或在输入字段中输入文本。

    请按步骤思考：
    1. 简要分析用户任务和网页内容。
    2. 如果源代码似乎不完整，请将其补全为有效的 HTML。保持产品标题不变。仅补全缺失的 HTML 语法。
    3. 识别页面上潜在的可交互元素（链接、按钮、输入字段等）。
    4. 确定是否需要滚动以显示更多内容。
    5. 决定最合乎逻辑的下一步操作，以推进完成用户任务。

    你的响应应该是一个简洁的行动计划，从以下选项中选择：
    - "COMPLETE_PAGE_SOURCE": 如果源代码似乎不完整，请将其补全为有效的 HTML。
    - "SCROLL_DOWN": 如果需要通过滚动加载更多内容。
    - "CLICK: <element_text>": 如果应点击带有文本 <element_text> 的特定元素。将 <element_text> 替换为元素的实际文本。
    - "ENTER_TEXT: <element_id>, <text_to_enter>": 如果需要在输入字段中输入文本。将 <element_id> 替换为输入元素的 ID，将 <text_to_enter> 替换为要输入的文本。
    - "TASK_COMPLETED": 如果你认为用户任务可能已在此页面上完成。
    - "STUCK": 如果你不确定下一步该做什么或无法进一步推进。
    - "ASK_USER": 如果你需要用户澄清下一步该做什么。

    如果你选择 "CLICK" 或 "ENTER_TEXT"，请确保元素文本或 ID 在网页源代码中清晰可辨。如果存在多个相似元素，请根据用户任务选择最相关的元素。
    如果你不确定，或者以上操作都不合适，则默认为 "ASK_USER"。

    示例响应：
    - SCROLL_DOWN
    - CLICK: 了解更多
    - ENTER_TEXT: search_box_id, Gemini API
    - TASK_COMPLETED
    - STUCK
    - ASK_USER

    你的行动计划是什么？
    """
    return analysis_prompt


# 定义搜索结果 Agent (search_results_agent)
search_results_agent = Agent(
    # 指定使用的 LLM 模型
    model=constants.MODEL,
    # Agent 名称
    name="search_results_agent",
    # Agent 描述：使用网页浏览获取关键词的前 3 个搜索结果信息
    description="使用网页浏览获取关键词的前 3 个搜索结果信息",
    # Agent 指令 (从 prompt 模块获取)
    instruction=prompt.SEARCH_RESULT_AGENT_PROMPT,
    # Agent 可用的工具列表
    tools=[
        go_to_url,                          # 导航到 URL
        take_screenshot,                    # 截屏
        find_element_with_text,             # 查找带文本的元素
        click_element_with_text,            # 点击带文本的元素
        enter_text_into_element,           # 输入文本到元素
        scroll_down_screen,                 # 向下滚动屏幕
        get_page_source,                    # 获取页面源代码
        load_artifacts_tool,                # 加载 artifact 工具
        analyze_webpage_and_determine_action, # 分析网页并决定行动
    ],
)

