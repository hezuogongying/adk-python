
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

"""该代码包含 CHASE-SQL Agent 的 LLM 工具函数。"""

from concurrent.futures import as_completed # 用于等待并发任务完成
from concurrent.futures import ThreadPoolExecutor # 用于创建线程池执行并发任务
import functools # 用于函数工具，如此处的 wraps 装饰器
import os # 用于与操作系统交互，如获取环境变量
import random # 用于生成随机数，如此处用于延迟和区域选择
import time # 用于时间相关操作，如 sleep
from typing import Callable, List, Optional # 用于类型注解

import dotenv # 用于加载 .env 文件中的环境变量
from google.cloud import aiplatform # Google Cloud AI Platform 客户端库
import vertexai # Vertex AI SDK
from vertexai.generative_models import GenerationConfig # 生成配置类
from vertexai.generative_models import HarmBlockThreshold, HarmCategory # 安全设置相关的类
from vertexai.preview import caching # Vertex AI 缓存功能（预览版）
from vertexai.preview.generative_models import GenerativeModel # 生成模型类（预览版）


# 加载 .env 文件中的环境变量，如果存在则覆盖现有变量
dotenv.load_dotenv(override=True)

# 定义安全过滤器配置，将所有有害内容的阻止阈值设置为 BLOCK_NONE（不阻止）
# 警告：在生产环境中使用时应谨慎配置安全设置
SAFETY_FILTER_CONFIG = {
    HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
}

# 从环境变量获取 GCP 项目 ID 和区域
GCP_PROJECT = os.getenv('GCP_PROJECT')
GCP_REGION = os.getenv('GCP_REGION')

# Gemini 模型可用的 GCP 区域列表
GEMINI_AVAILABLE_REGIONS = [
    'europe-west3', 'australia-southeast1', 'us-east4', 'northamerica-northeast1',
    'europe-central2', 'us-central1', 'europe-north1', 'europe-west8', 'us-south1',
    'us-east1', 'asia-east2', 'us-west1', 'europe-west9', 'europe-west2',
    'europe-west6', 'europe-southwest1', 'us-west4', 'asia-northeast1',
    'asia-east1', 'europe-west1', 'europe-west4', 'asia-northeast3',
    'asia-south1', 'asia-southeast1', 'southamerica-east1',
]
# Gemini 模型 URL 模板，用于在不同区域分发请求
GEMINI_URL = 'projects/{GCP_PROJECT}/locations/{region}/publishers/google/models/{model_name}'

# 初始化 AI Platform SDK
aiplatform.init(
    project=GCP_PROJECT,
    location=GCP_REGION,
)
# 初始化 Vertex AI SDK
vertexai.init(project=GCP_PROJECT, location=GCP_REGION)


def retry(max_attempts=8, base_delay=1, backoff_factor=2):
    """为函数添加重试逻辑的装饰器。

    Args:
        max_attempts (int): 最大尝试次数。
        base_delay (int): 指数退避的基础延迟时间（秒）。
        backoff_factor (int): 每次后续尝试延迟时间的乘数因子。

    Returns:
        Callable: 装饰器函数。
    """

    def decorator(func):
        # 保留原函数的元信息（如函数名、文档字符串等）
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    # 尝试执行原函数
                    return func(*args, **kwargs)
                except Exception as e:  # pylint: disable=broad-exception-caught # 捕获所有异常
                    # 打印失败信息
                    print(f'尝试 {attempts + 1} 失败，错误: {e}')
                    attempts += 1
                    # 如果达到最大尝试次数，则抛出异常
                    if attempts >= max_attempts:
                        raise e
                    # 计算指数退避延迟时间
                    delay = base_delay * (backoff_factor**attempts)
                    # 添加随机抖动，防止惊群效应
                    delay = delay + random.uniform(0, 0.1 * delay)
                    # 等待指定时间
                    time.sleep(delay)

        return wrapper

    return decorator


class GeminiModel:
    """Gemini 模型类。"""

    def __init__(
        self,
        model_name: str = 'gemini-1.5-pro', # 默认模型名称
        finetuned_model: bool = False, # 是否为微调模型
        distribute_requests: bool = False, # 是否将请求分发到不同区域
        cache_name: str | None = None, # 缓存名称（如果使用缓存）
        temperature: float = 0.01, # 生成温度
        **kwargs, # 其他传递给 GenerationConfig 的参数
    ):
        """初始化 GeminiModel。

        Args:
            model_name (str): 要使用的 Gemini 模型名称。
            finetuned_model (bool): 如果模型是微调过的，则设为 True。
            distribute_requests (bool): 如果为 True，则在可用区域之间随机分发请求。
            cache_name (str | None): 要使用的缓存内容的名称。如果为 None，则不使用缓存。
            temperature (float): 控制生成随机性的温度值。
            **kwargs: 传递给 vertexai.generative_models.GenerationConfig 的其他参数。
        """
        self.model_name = model_name
        self.finetuned_model = finetuned_model
        self.arguments = kwargs # 存储额外的生成参数
        self.distribute_requests = distribute_requests
        self.temperature = temperature
        resolved_model_name = self.model_name # 解析后的模型名称

        # 如果不是微调模型且需要分发请求
        if not self.finetuned_model and self.distribute_requests:
            # 从可用区域列表中随机选择一个区域
            random_region = random.choice(GEMINI_AVAILABLE_REGIONS)
            # 构建包含区域信息的模型 URL
            resolved_model_name = GEMINI_URL.format(
                GCP_PROJECT=GCP_PROJECT,
                region=random_region,
                model_name=self.model_name,
            )

        # 如果指定了缓存名称
        if cache_name is not None:
            # 创建缓存内容对象
            cached_content = caching.CachedContent(cached_content_name=cache_name)
            # 从缓存内容加载模型
            self.model = GenerativeModel.from_cached_content(
                cached_content=cached_content
            )
        else:
            # 否则，直接使用模型名称初始化模型
            self.model = GenerativeModel(model_name=resolved_model_name)

    # 应用重试装饰器
    @retry(max_attempts=12, base_delay=2, backoff_factor=2)
    def call(self, prompt: str, parser_func: Optional[Callable[[str], str]] = None) -> str:
        """使用给定的 Prompt 调用 Gemini 模型。

        Args:
            prompt (str): 用于调用模型的 Prompt。
            parser_func (callable, optional): 处理 LLM 输出的函数。
                                              它接收模型的响应作为输入并返回处理后的结果。
                                              默认为 None。

        Returns:
            str: 来自模型的处理后的响应。
        """
        # 调用模型的 generate_content 方法
        response = self.model.generate_content(
            prompt,
            # 配置生成参数
            generation_config=GenerationConfig(
                temperature=self.temperature,
                **self.arguments, # 传入初始化时存储的其他参数
            ),
            # 配置安全设置
            safety_settings=SAFETY_FILTER_CONFIG,
        )
        # 提取响应文本
        response_text = ""
        # 检查 response.candidates 是否存在且不为空
        if response.candidates:
            # 检查第一个 candidate 的 content.parts 是否存在且不为空
            if response.candidates[0].content.parts:
                # 提取第一个 part 的文本
                response_text = response.candidates[0].content.parts[0].text
            # else:
                # 处理 parts 为空的情况，可以记录日志或返回空字符串/默认值
                # print("Warning: Response parts are empty.")
        # else:
             # 处理 candidates 为空的情况，可以记录日志或返回空字符串/默认值
             # print("Warning: No candidates found in the response.")

        # 如果提供了 parser_func，则使用它处理响应文本
        if parser_func:
            return parser_func(response_text)
        # 否则直接返回响应文本
        return response_text

    def call_parallel(
        self,
        prompts: List[str], # Prompt 列表
        parser_func: Optional[Callable[[str], str]] = None, # 可选的解析函数
        timeout: int = 60, # 每个线程的超时时间（秒）
        max_retries: int = 5, # 超时线程的最大重试次数
    ) -> List[Optional[str]]: # 返回响应列表，失败的为 None
        """使用带有重试逻辑的线程并行调用 Gemini 模型处理多个 Prompt。

        Args:
            prompts (List[str]): 用于调用模型的 Prompt 列表。
            parser_func (callable, optional): 处理每个响应的函数。默认为 None。
            timeout (int): 每个线程的最大等待时间（秒）。默认为 60。
            max_retries (int): 超时线程的最大重试次数。默认为 5。

        Returns:
            List[Optional[str]]: 响应列表，对于失败的线程返回 None 或错误信息字符串。
        """
        # 初始化结果列表，长度与 prompts 相同，初始值为 None
        results = [None] * len(prompts)

        def worker(index: int, prompt: str):
            """线程工作函数，用于调用模型并存储结果，包含重试逻辑。"""
            retries = 0
            while retries <= max_retries:
                try:
                    # 调用单个模型的 call 方法
                    return self.call(prompt, parser_func)
                except Exception as e:  # pylint: disable=broad-exception-caught # 捕获所有异常
                    print(f'Prompt {index} 出错: {str(e)}')
                    retries += 1
                    if retries <= max_retries:
                        print(f'正在重试 ({retries}/{max_retries}) Prompt {index}')
                        time.sleep(1)  # 重试前短暂延迟
                    else:
                        # 达到最大重试次数后返回错误信息
                        return f'重试后出错: {str(e)}'

        # 创建线程池，最大工作线程数等于 prompts 的数量
        # max_workers 可以根据需要调整，例如设置为 os.cpu_count() 或一个固定值
        with ThreadPoolExecutor(max_workers=len(prompts)) as executor:
            # 提交所有任务到线程池，并创建一个 future 到索引的映射
            future_to_index = {
                executor.submit(worker, i, prompt): i
                for i, prompt in enumerate(prompts)
            }

            # 等待任务完成（或超时）
            # as_completed 会在任务完成时立即返回 future
            for future in as_completed(future_to_index, timeout=timeout):
                index = future_to_index[future]
                try:
                    # 获取任务结果并存储到 results 列表
                    results[index] = future.result()
                except Exception as e:  # pylint: disable=broad-exception-caught # 捕获 future.result() 可能抛出的异常
                    print(f'Prompt {index} 发生未处理错误: {e}')
                    results[index] = '未处理错误' # 标记为未处理错误

        # 处理超时后仍未完成的任务
        for future, index in future_to_index.items():
            if not future.done():
                print(f'Prompt {index} 发生超时')
                results[index] = '超时' # 标记为超时
                # 可以选择取消任务 future.cancel()，但这不保证线程会立即停止

        # 返回包含所有结果（或 None/错误信息）的列表
        return results


