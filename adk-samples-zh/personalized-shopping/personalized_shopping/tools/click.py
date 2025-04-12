
import gym
import random
import string
import time
from collections import defaultdict

import numpy as np
import torch
from bs4 import BeautifulSoup, Comment

# 导入 WebShop 应用程序和相关常量
from personalized_shopping.shared_libraries.web_agent_site.app import app, ACTION_TO_TEMPLATE, END_BUTTON, BACK_TO_SEARCH, NEXT_PAGE, PREV_PAGE
# 导入 WebShop 相关工具函数
from personalized_shopping.shared_libraries.web_agent_site.utils import (
    parse_action,
    get_top_n_product_from_keywords,
    get_product_per_page,
    map_action_to_html,
    init_search_engine,
    load_products,
    get_goals,
    get_reward,
    random_idx,
)
# 导入 Gym 注册函数
from gym.envs.registration import register
import json
from personalized_shopping.shared_libraries.web_agent_site.config import DEFAULT_FILE_PATH, FEAT_CONV, FEAT_IDS


class WebAgentTextEnv(gym.Env):
    """用于 WebShop 环境文本模式的 Gym 环境"""

    def __init__(
        self,
        observation_mode="html", # 观测模式，可选 'html', 'text', 'text_rich', 'url'
        file_path=DEFAULT_FILE_PATH, # 数据文件路径
        server=None, # 可选的预初始化 SimServer 实例
        **kwargs, # 其他可选参数
    ):
        """文本环境的构造函数

        参数:

        observation_mode (`str`): 观测模式，可选 ['html' | 'text' | 'text_rich' | 'url'] (默认为 'html')。决定 `step` 函数返回的观测内容的格式。
        file_path (`str`): 指向包含产品、目标等数据的文件的路径。
        server (`SimServer`, optional): 如果提供，则使用此预先初始化的模拟服务器实例，否则将创建一个新的。
        **kwargs: 接受一系列可选关键字参数，用于进一步配置环境和模拟服务器/浏览器。这些参数包括：
            get_image (`int`): 是否加载图像特征（默认为 0，不加载）。如果为 1，则加载图像特征和 ID。
            filter_goals (`callable`, optional): 一个函数，用于根据自定义标准筛选可用的目标。
            limit_goals (`int`, optional): 限制可用目标的数量（默认为 -1，不限制）。
            num_products (`int`, optional): 限制环境中可搜索的产品数量。
            human_goals (`bool`, optional): 如果为 True，加载人工标注的目标；否则加载合成目标。
            session (`str`, optional): 指定要使用的会话 ID。如果未提供，则随机生成。
            session_prefix (`str`, optional): 添加到会话 ID 前缀的字符串。
            show_attrs (`bool`, optional): 是否在产品页面上显示属性（默认为 False）。
            num_prev_obs (`int`, optional): 在状态中包含先前观测的数量（默认为 0）。
            num_prev_actions (`int`, optional): 在状态中包含先前动作的数量（默认为 0）。
        """
        super(WebAgentTextEnv, self).__init__()
        self.observation_mode = observation_mode # 存储观测模式
        self.kwargs = kwargs # 存储其他关键字参数

        self.file_path = file_path # 存储文件路径

        self.base_url = "http://127.0.0.1:3000" # 模拟服务器的基础 URL
        # 初始化模拟服务器 (SimServer)，如果未提供 server 参数，则创建一个新的
        self.server = (
            SimServer(
                self.base_url,
                self.file_path,
                self.kwargs.get("filter_goals"), # 获取 filter_goals 参数
                self.kwargs.get("limit_goals", -1), # 获取 limit_goals 参数，默认为 -1
                self.kwargs.get("num_products"), # 获取 num_products 参数
                self.kwargs.get("human_goals"), # 获取 human_goals 参数
                self.kwargs.get("show_attrs", False), # 获取 show_attrs 参数，默认为 False
            )
            if server is None # 如果没有提供 server
            else server # 否则使用提供的 server
        )
        # 初始化模拟浏览器 (SimBrowser)，使用上面创建或提供的服务器
        self.browser = SimBrowser(self.server)

        # 获取会话 ID 和前缀
        self.session = self.kwargs.get("session")
        self.session_prefix = self.kwargs.get("session_prefix")
        # 如果 get_image 参数为真，则加载图像特征和 ID
        if self.kwargs.get("get_image", 0):
            self.feats = torch.load(FEAT_CONV) # 加载图像特征
            self.ids = torch.load(FEAT_IDS) # 加载图像 ID
            # 将图像 ID 列表转换为 URL 到索引的字典，以便快速查找
            self.ids = {url: idx for idx, url in enumerate(self.ids)}
        # 初始化用于存储先前观测和动作的列表
        self.prev_obs = []
        self.prev_actions = []
        # 获取要包含的先前观测和动作的数量
        self.num_prev_obs = self.kwargs.get("num_prev_obs", 0)
        self.num_prev_actions = self.kwargs.get("num_prev_actions", 0)
        # 重置环境状态
        self.reset()

    def step(self, action):
        """执行一个动作，更新 WebShop 环境，并返回 (observation, reward, done, info)

        参数:

        action (`str`): 一个动作应该具有以下结构之一：
          - search[关键词] (例如: search[red dress])
          - click[值] (例如: click[buy now], click[b07w4t7f8c])
        如果动作无效，则不执行任何操作。

        返回:
          tuple: 包含以下元素的元组：
            - observation (`str`): 当前环境状态的观测，格式由 `observation_mode` 决定。包含了当前页面的内容以及根据设置包含的历史动作和观测。
            - reward (`float`): 执行动作后获得的奖励值。
            - done (`bool`): 指示会话是否结束（例如，点击了 "Buy Now"）。
            - info (`dict`, optional): 包含额外信息的字典（当前实现为 None）。
        """
        info = None # 初始化额外信息为 None
        self.get_available_actions() # 获取当前页面可用的动作

        # 解析动作类型（点击、搜索）和参数
        action_name, action_arg = parse_action(action)
        if action_arg is not None:
            action_arg = action_arg.lower() # 将动作参数转换为小写

        # 根据动作类型执行相应的浏览器操作
        if action_name == "search" and action_arg is not None and action_arg != "":
            # 如果是搜索动作且有关健词
            status = self.browser.search(action_arg)
        elif (
            action_name == "click" # 如果是点击动作
            and action_arg in self.text_to_clickable.keys() # 并且点击的目标在可点击元素列表中
            and action_arg != "search" # 并且点击的目标不是 "search" 按钮本身（虽然通常按钮文本不会是 "search"）
        ):
            # 执行点击操作
            status = self.browser.click(action_arg, self.text_to_clickable)
        else:
            # 如果动作无效或不符合条件，设置状态为无奖励且未结束
            status = dict(reward=0, done=False)

        # 更新观测和状态
        ob = self.observation # 获取当前的观测
        text_list = [ob] # 初始化包含当前观测的状态文本列表
        self.prev_actions.append(action) # 将当前动作添加到历史动作列表

        # 根据配置，将指定数量的先前动作和观测添加到状态文本列表中
        for i in range(1, 1 + max(self.num_prev_obs, self.num_prev_actions)):
            if len(self.prev_actions) >= i and self.num_prev_actions >= i:
                text_list.append(self.prev_actions[-i]) # 添加倒数第 i 个动作
            if len(self.prev_obs) >= i and self.num_prev_obs >= i:
                text_list.append(self.prev_obs[-i]) # 添加倒数第 i 个观测

        # 将状态文本列表反转并用 "[SEP]" 连接，形成最终的状态表示
        # 反转是为了让最新的观测在最前面，历史记录按时间倒序排列
        state = " [SEP] ".join(text_list[::-1])
        self.prev_obs.append(ob) # 将当前观测添加到历史观测列表

        # 返回状态、奖励、结束标志和信息
        return state, status["reward"], status["done"], info

    def get_available_actions(self):
        """返回当前步骤可用的动作列表"""
        html_obj = self._parse_html() # 解析当前页面的 HTML

        # 收集可点击的元素：搜索框、按钮、链接和选项
        search_bar = html_obj.find(id="search_input") # 查找搜索输入框
        has_search_bar = True if search_bar is not None else False # 判断是否存在搜索框
        buttons = html_obj.find_all(class_="btn") # 查找所有 class="btn" 的按钮
        product_links = html_obj.find_all(class_="product-link") # 查找所有 class="product-link" 的产品链接
        buying_options = html_obj.select('input[type="radio"]') # 查找所有 type="radio" 的购买选项

        # 创建一个字典，将元素的文本内容（小写）映射到元素本身
        self.text_to_clickable = {
            f"{b.get_text()}".lower(): b for b in buttons + product_links # 处理按钮和产品链接
        }
        # 处理购买选项（单选按钮）
        for opt in buying_options:
            opt_value = opt.get("value") # 获取选项的值
            self.text_to_clickable[f"{opt_value}"] = opt # 将选项值（通常是文本）映射到元素

        # 返回包含可用动作信息的字典
        return dict(
            has_search_bar=has_search_bar, # 是否有搜索框
            clickables=list(self.text_to_clickable.keys()), # 可点击元素的文本列表
        )

    def get_image(self):
        """从页面 HTML 中抓取图像并返回其特征向量 (如果已加载)"""
        html_obj = self._parse_html(self.browser.page_source) # 解析当前页面 HTML
        image_url_tag = html_obj.find(id="product-image") # 查找 ID 为 "product-image" 的图像标签

        # 如果找到了图像标签并且图像特征已加载
        if image_url_tag is not None:
            image_url = image_url_tag["src"] # 获取图像 URL
            # 如果图像 URL 在已加载的 ID 字典中
            if image_url in self.ids:
                image_idx = self.ids[image_url] # 获取图像索引
                image = self.feats[image_idx] # 从特征张量中获取对应的特征向量
                return image # 返回图像特征向量
        # 如果未找到图像或未加载特征，返回一个零向量
        return torch.zeros(512)

    def get_instruction_text(self):
        """获取当前环境会话对应的指令文本"""
        html_obj = self._parse_html(self.browser.page_source) # 解析当前页面 HTML
        # 查找 ID 为 "instruction-text" 的元素下的 h4 标签的文本
        instruction_text = html_obj.find(id="instruction-text").h4.text
        return instruction_text

    def _parse_html(self, html=None):
        """返回包装在 BeautifulSoup 对象中的网页请求结果

        参数:

        html (`str`, optional): 如果未提供 html，则使用当前状态中的 HTML (`self.state['html']`) 进行解析。
        """
        if html is None:
            html = self.state["html"] # 如果未提供 html，使用当前状态的 html
        # 使用 BeautifulSoup 解析 HTML
        html_obj = BeautifulSoup(html, "html.parser")
        return html_obj

    @property
    def observation(self):
        """将状态编译成 `html`、`text`、`text_rich` 或 `url` 观测模式"""
        html = self.state["html"] # 获取当前状态的 HTML
        if self.observation_mode == "html":
            return html # 直接返回 HTML
        elif self.observation_mode == "text":
            # 将 HTML 转换为简化版的纯文本
            return self.convert_html_to_text(html, simple=True)
        elif self.observation_mode == "text_rich":
            # 将 HTML 转换为带有特殊标记的富文本
            return self.convert_html_to_text(html, simple=False)
        elif self.observation_mode == "url":
            # 返回当前页面的 URL
            return self.state["url"]
        else:
            # 如果观测模式不支持，则抛出错误
            raise ValueError(f"不支持的观测模式 {self.observation_mode}")

    @property
    def state(self):
        """包含所有信息的完整状态。

        实际的观测 (`observation`) 可能是状态的一个子集或简化形式。
        """
        return dict(
            url=self.browser.current_url, # 当前页面的 URL
            html=self.browser.page_source, # 当前页面的 HTML 源码
            instruction_text=self.instruction_text, # 当前任务的指令文本
        )

    def convert_html_to_text(self, html, simple=False):
        """去除 HTML 标签并添加分隔符，将观测转换为纯文本模式"""
        # 查找 HTML 中所有文本节点
        texts = self._parse_html(html).findAll(text=True)
        # 过滤掉不可见的文本（例如 <script>, <style> 中的内容）
        visible_texts = filter(tag_visible, texts)
        if simple:
            # 对于 `simple`（简化）模式，仅使用 [SEP] 作为分隔符连接可见文本
            # t.strip() 去除首尾空白，t != "\n" 过滤掉纯换行符
            return " [SEP] ".join(t.strip() for t in visible_texts if t != "\n")
        else:
            # 对于 `text_rich`（富文本）模式，使用特定的、唯一的标记来区分不同类型的元素
            observation = ""
            for t in visible_texts:
                if t == "\n": # 跳过纯换行符
                    continue
                parent = t.parent # 获取文本节点的父元素
                parent_name = parent.name # 获取父元素的标签名
                parent_class = parent.get("class") # 获取父元素的 class 属性

                # 根据父元素的类型添加特殊标记
                if parent_name == "button":  # 按钮
                    processed_t = f"[button] {t} [button_]"
                elif parent_name == "label":  # 选项（通常是 radio button 的标签）
                    # 检查该选项是否已被点击（通过检查其值是否在当前 URL 中，这是一种模拟点击状态的方式）
                    if f'"{t}"' in self.state["url"]:
                        processed_t = f"  [clicked button] {t} [clicked button_]"
                        # 在观测开头添加一条消息表明用户点击了该选项
                        observation = f"您已点击 {t}。\n" + observation
                    else:
                        processed_t = f"  [button] {t} [button_]"
                elif parent_class == ["product-link"]:  # 产品链接 (ASINs)
                    # 检查该产品是否在当前会话的已访问产品列表中
                    # `self.server.user_sessions[self.session]["asins"]` 存储了用户访问过的产品 ASIN
                    if f"{t}" in self.server.user_sessions[self.session]["asins"]:
                        processed_t = f"\n[clicked button] {t} [clicked button_]"
                    else:
                        processed_t = f"\n[button] {t} [button_]"
                else:  # 普通的、不可点击的文本
                    processed_t = str(t)
                # 将处理后的文本追加到观测字符串中，并添加换行符
                observation += processed_t + "\n"
            return observation

    def reset(self, session=None, instruction_text=None):
        """创建一个新会话并重置环境变量

        参数:
          session (`str` or `int`, optional): 指定要使用的会话 ID。如果是整数，它可能用于选择特定的预定义目标。如果为 None，则随机生成一个会话 ID。
          instruction_text (`str`, optional): 指定要使用的指令文本。如果为 None，则从新会话的目标中获取。

        返回:
          tuple: 包含初始观测 (`obs`) 和额外信息 (`info`，当前为 None) 的元组。
        """
        session_int = None # 初始化整数会话 ID 为 None
        if session is not None:
            # 如果提供了会话 ID
            self.session = str(session) # 将会话 ID 存储为字符串
            if isinstance(session, int):
                session_int = session # 如果是整数，也存储整数形式
        else:
            # 如果未提供会话 ID，随机生成一个 10 位小写字母的 ID
            self.session = "".join(random.choices(string.ascii_lowercase, k=10))
        # 如果设置了会话前缀，则添加到会话 ID 前面
        if self.session_prefix is not None:
            self.session = self.session_prefix + self.session

        # 构建初始 URL，格式为 base_url/session_id
        init_url = f"{self.base_url}/{self.session}"
        # 使用模拟浏览器访问初始 URL，并传递会话 ID 和可能的整数 ID
        # 这会触发 SimServer 为此会话 ID 创建或加载目标和状态
        self.browser.get(init_url, session_id=self.session, session_int=session_int)

        # 重置可点击元素映射
        self.text_to_clickable = None
        # 获取或设置指令文本
        self.instruction_text = (
            self.get_instruction_text() # 如果未提供 instruction_text，则从页面获取
            if instruction_text is None
            else instruction_text # 否则使用提供的 instruction_text
        )
        # 获取初始观测
        obs = self.observation
        # 重置先前观测和动作列表，将初始观测加入
        self.prev_obs = [obs]
        self.prev_actions = []
        # 返回初始观测和 None (info)
        return obs, None

    def render(self, mode="human"):
        """渲染环境（当前未实现）"""
        pass

    def close(self):
        """关闭环境（当前未实现）"""
        pass


def tag_visible(element):
    """判断 BeautifulSoup 元素中的文本是否可见

    用于过滤掉 <style>, <script>, <head>, <title>, <meta> 标签以及 HTML 注释中的文本。
    """
    # 定义需要忽略的标签名集合
    ignore = {"style", "script", "head", "title", "meta", "[document]"}
    # 如果元素的父标签名不在忽略列表中，并且元素本身不是注释，则认为可见
    return element.parent.name not in ignore and not isinstance(element, Comment)


class SimServer:
    """WebShop Flask 应用的轻量级模拟器，用于生成 HTML 观测"""

    def __init__(
        self,
        base_url, # 模拟服务器的基础 URL
        file_path, # 数据文件路径
        filter_goals=None, # 筛选目标的函数
        limit_goals=-1, # 限制目标数量
        num_products=None, # 限制产品数量
        human_goals=0, # 是否使用人工目标
        show_attrs=False, # 是否显示产品属性
    ):
        """模拟服务器的构造函数，用于提供 WebShop 应用服务

        参数:

        base_url (`str`): 模拟服务器的基础 URL。
        file_path (`str`): 包含产品、目标等数据的文件路径。
        filter_goals (`func`, optional): 根据自定义函数的标准选择特定目标进行考虑的函数。该函数应接受索引 `i` 和目标 `goal` 作为参数。
        limit_goals (`int`): 限制可用目标的数量（默认为 -1，不限制）。如果设置，将随机选择指定数量的目标。
        num_products (`int`, optional): 要在其中搜索的产品数量。如果提供，则限制加载的产品数量。
        human_goals (`bool`): 如果为 True，加载人工目标；否则，加载合成目标（默认为 0，即合成目标）。
        show_attrs (`bool`): 如果为 True，在产品页面显示属性（默认为 False）。
        """
        # 加载所有产品、目标和搜索引擎
        self.base_url = base_url
        # 加载产品数据
        self.all_products, self.product_item_dict, self.product_prices, _ = (
            load_products(
                filepath=file_path,
                num_products=num_products,
                human_goals=human_goals,
            )
        )
        # 初始化搜索引擎
        self.search_engine = init_search_engine(num_products=num_products)
        # 获取目标列表
        self.goals = get_goals(self.all_products, self.product_prices, human_goals)
        self.show_attrs = show_attrs # 存储是否显示属性

        # 固定随机种子以确保目标洗牌结果可复现
        random.seed(233)
        random.shuffle(self.goals) # 随机打乱目标列表

        # 如果提供了 filter_goals 函数，则应用它来筛选目标
        if filter_goals is not None:
            self.goals = [
                goal for (i, goal) in enumerate(self.goals) if filter_goals(i, goal)
            ]

        # 如果设置了 limit_goals，则通过加权随机抽样限制目标数量
        if limit_goals != -1 and limit_goals < len(self.goals):
            self.weights = [goal["weight"] for goal in self.goals] # 获取每个目标的权重
            self.cum_weights = [0] + np.cumsum(self.weights).tolist() # 计算累积权重
            idxs = [] # 存储选中的目标索引
            while len(idxs) < limit_goals:
                idx = random_idx(self.cum_weights) # 根据累积权重随机选择一个索引
                if idx not in idxs: # 确保不重复选择
                    idxs.append(idx)
            self.goals = [self.goals[i] for i in idxs] # 更新目标列表为选中的子集
        print(f"已加载 {len(self.goals)} 个目标。")

        # 设置额外的管理变量
        self.weights = [goal["weight"] for goal in self.goals] # 更新权重列表（可能因筛选或限制而改变）
        self.cum_weights = [0] + np.cumsum(self.weights).tolist() # 更新累积权重
        self.user_sessions = dict() # 用于存储用户会话状态的字典
        self.search_time = 0 # 记录搜索所花费的总时间
        self.render_time = 0 # 记录 HTML 渲染所花费的总时间
        self.sample_time = 0 # 记录目标采样所花费的总时间（未使用）
        # TODO: 这是临时的 hacky 方式，应移除。用于强制指定指令文本，覆盖从目标中获取的文本。
        self.assigned_instruction_text = None

    # 注意：以下 @app.route(...) 装饰器是 Flask 框架的用法，
    # 在这个模拟器 (SimServer) 中，这些方法实际上是由 receive 方法根据 URL 模式间接调用的，
    # 而不是通过真正的 HTTP 请求。这里保留装饰器是为了代码结构的可读性。

    # @app.route("/", methods=["GET", "POST"]) # 模拟 Flask 路由
    def index(self, session_id, **kwargs):
        """重定向到具有给定会话 ID 的搜索页面（模拟初始页面）"""
        # 映射 "start" 动作到相应的 HTML
        html = map_action_to_html(
            "start",
            session_id=session_id,
            instruction_text=kwargs["instruction_text"], # 使用传入的指令文本
        )
        # 构建当前页面的 URL
        url = f"{self.base_url}/{session_id}"
        return html, url # 返回 HTML 和 URL

    # @app.route("/", methods=["GET", "POST"]) # 模拟 Flask 路由
    def search_results(self, session_id, **kwargs):
        """初始化会话（如果需要）并返回搜索结果页面"""
        session = self.user_sessions[session_id] # 获取当前会话
        keywords = kwargs["keywords"] # 获取搜索关键词
        # TODO: 为什么这里使用 kwargs？为什么不直接从 session 获取？(原始注释)
        assert isinstance(keywords, list) # 确保关键词是列表
        page = 1 if "page" not in kwargs else kwargs["page"] # 获取页码，默认为 1
        session["page"] = page # 更新会话中的页码
        session["keywords"] = keywords # 更新会话中的关键词
        session["actions"]["search"] += 1 # 记录搜索动作次数
        session["asin"] = None # 重置当前查看的商品 ASIN
        session["options"] = {} # 重置已选商品选项

        # 根据关键词执行搜索并记录时间
        old_time = time.time()
        top_n_products = get_top_n_product_from_keywords(
            keywords,
            self.search_engine,
            self.all_products,
            self.product_item_dict,
        )
        self.search_time += time.time() - old_time # 累加搜索时间

        # 从搜索结果 ASIN 中获取当前页的产品列表
        products = get_product_per_page(top_n_products, page)

        # 构建搜索结果页面的 URL
        keywords_url_string = "+".join(keywords) # 将关键词列表连接成 URL 字符串
        url = (
            f"{self.base_url}/search_results/{session_id}/"
            f"{keywords_url_string}/{page}"
        )

        # 渲染搜索结果页面的 HTML 并记录时间
        old_time = time.time()
        html = map_action_to_html(
            "search", # 动作类型
            session_id=session_id,
            products=products, # 当前页产品列表
            keywords=session["keywords"], # 当前关键词
            page=page, # 当前页码
            total=len(top_n_products), # 总搜索结果数
            # instruction_text=session['goal']['instruction_text'], # 用于奖励计算的原始指令（被注释掉）
            # 使用 assigned_instruction_text（如果存在）或目标中的指令文本来渲染页面
            instruction_text=self.assigned_instruction_text or session['goal']['instruction_text'],
        )
        self.render_time += time.time() - old_time # 累加渲染时间
        return html, url # 返回 HTML 和 URL

    # @app.route("/", methods=["GET", "POST"]) # 模拟 Flask 路由
    def item_page(self, session_id, **kwargs):
        """渲染并返回产品项目页面的 HTML"""
        session = self.user_sessions[session_id] # 获取当前会话
        clickable_name = kwargs["clickable_name"] # 获取被点击元素的名称（小写）
        text_to_clickable = kwargs["text_to_clickable"] # 获取文本到元素的映射
        clickable = text_to_clickable[clickable_name] # 获取被点击的元素对象

        # 更新会话日志，记录最后选择的产品 ASIN 或选项
        # 检查被点击的是否是产品链接
        if (
            clickable.get("class") is not None # 检查 class 属性是否存在
            and clickable.get("class")[0] == "product-link" # 检查 class 是否为 "product-link"
        ):
            session["asin"] = clickable_name.upper() # 将 ASIN 存入会话（转换为大写）
            session["actions"]["asin"] += 1 # 记录点击产品链接的次数
            session["asins"].add(session["asin"]) # 将 ASIN 添加到已访问集合中
        # 检查被点击的是否是选项（如 radio button）
        elif clickable.get("name") is not None:
            clickable_key = clickable["name"].lower() # 获取选项的 name 属性作为键（小写）
            session["options"][clickable_key] = clickable_name # 将选项值存入会话
            session["actions"]["options"] += 1 # 记录点击选项的次数

        # 设置页面的字段和 URL，然后渲染页面的 HTML
        product_info = self.product_item_dict[session["asin"]] # 获取当前 ASIN 的产品信息
        keywords_url_string = "+".join(session["keywords"]) # 获取当前搜索关键词的 URL 字符串
        option_string = json.dumps(session["options"]) # 将选项字典转换为 JSON 字符串

        # 构建产品页面的 URL
        url = (
            f"{self.base_url}/item_page/{session_id}/"
            f'{session["asin"]}/{keywords_url_string}/'
            f'{session["page"]}/{option_string}'
        )

        # 渲染产品页面的 HTML
        html = map_action_to_html(
            "click", # 动作类型
            session_id=session_id,
            product_info=product_info, # 产品信息
            keywords=session["keywords"], # 当前关键词
            page=session["page"], # 当前页码
            asin=session["asin"], # 当前 ASIN
            options=session["options"], # 当前选项
            # instruction_text=session['goal']['instruction_text'], # 用于奖励计算的原始指令（被注释掉）
            # 使用 assigned_instruction_text（如果存在）或目标中的指令文本来渲染页面
            instruction_text=self.assigned_instruction_text or session['goal']['instruction_text'],
            show_attrs=self.show_attrs, # 是否显示属性
        )
        return html, url # 返回 HTML 和 URL

    # @app.route("/", methods=["GET", "POST"]) # 模拟 Flask 路由
    def item_sub_page(self, session_id, **kwargs):
        """渲染并返回产品子页面（例如描述、特性、评论）的 HTML"""
        session = self.user_sessions[session_id] # 获取当前会话
        clickable_name = kwargs["clickable_name"] # 获取被点击元素的名称（例如 "Description", "Features", "Reviews"）

        # 标准化 clickable_name，以匹配 ACTION_TO_TEMPLATE 中的键
        # ACTION_TO_TEMPLATE 可能包含如 "Description", "Features", "Reviews" 等键
        for k in ACTION_TO_TEMPLATE:
            if clickable_name.lower() == k.lower():
                clickable_name = k # 使用 ACTION_TO_TEMPLATE 中的标准名称
                break

        # 设置页面的字段和 URL，然后渲染页面的 HTML
        product_info = self.product_item_dict[session["asin"]] # 获取当前 ASIN 的产品信息
        session["actions"][clickable_name] += 1 # 记录点击子页面标签的次数
        keywords_url_string = "+".join(session["keywords"]) # 获取当前搜索关键词的 URL 字符串

        # 构建产品子页面的 URL
        url = (
            f"{self.base_url}/item_sub_page/{session_id}/"
            f'{session["asin"]}/{keywords_url_string}/{session["page"]}/'
            f'{clickable_name}/{session["options"]}' # options 似乎在此处 URL 中未正确编码，可能是原始代码的笔误
        )
        # 渲染产品子页面的 HTML
        html = map_action_to_html(
            f"click[{clickable_name}]", # 动作类型，格式如 "click[Description]"
            session_id=session_id,
            product_info=product_info, # 产品信息
            keywords=session["keywords"], # 当前关键词
            page=session["page"], # 当前页码
            asin=session["asin"], # 当前 ASIN
            options=session["options"], # 当前选项
            # instruction_text=session['goal']['instruction_text'], # 用于奖励计算的原始指令（被注释掉）
            # 使用 assigned_instruction_text（如果存在）或目标中的指令文本来渲染页面
            instruction_text=self.assigned_instruction_text or session['goal']['instruction_text'],
        )
        return html, url # 返回 HTML 和 URL

    # @app.route("/", methods=["GET", "POST"]) # 模拟 Flask 路由
    def done(self, session_id, **kwargs):
        """渲染并返回完成页面的 HTML"""
        session = self.user_sessions[session_id] # 获取当前会话
        goal = self.user_sessions[session_id]["goal"] # 获取当前会话的目标
        # 获取购买的商品信息
        purchased_product = self.product_item_dict[session["asin"]]
        session["actions"]["purchase"] += 1 # 记录购买动作次数
        price = self.product_prices.get(session["asin"]) # 获取购买商品的价格

        # 计算所选产品的奖励并设置页面详细信息变量
        # get_reward 函数根据购买的产品、目标、价格和选项计算奖励
        reward, info = get_reward(
            purchased_product,
            goal,
            price=price,
            options=session["options"],
            verbose=True, # 获取详细的奖励信息
        )

        # 更新会话状态
        self.user_sessions[session_id]["verbose_info"] = info # 存储详细奖励信息
        self.user_sessions[session_id]["done"] = True # 标记会话为已完成
        self.user_sessions[session_id]["reward"] = reward # 存储最终奖励

        # 构建完成页面的 URL
        url = (
            f"{self.base_url}/done/{session_id}/"
            f'{session["asin"]}/{session["options"]}' # options 似乎在此处 URL 中未正确编码
        )
        # 渲染完成页面的 HTML
        html = map_action_to_html(
            f"click[{END_BUTTON}]", # 动作类型，END_BUTTON 通常是 "Buy Now"
            session_id=session_id,
            reward=reward, # 最终奖励
            asin=session["asin"], # 购买的 ASIN
            options=session["options"], # 购买的选项
            # instruction_text=session['goal']['instruction_text'], # 用于奖励计算的原始指令（被注释掉）
            # 使用 assigned_instruction_text（如果存在）或目标中的指令文本来渲染页面
            instruction_text=self.assigned_instruction_text or session['goal']['instruction_text'],
        )
        return html, url, reward # 返回 HTML、URL 和奖励

    def receive(self, session_id, current_url, session_int=None, **kwargs):
        """将动作映射到相应的页面（模拟请求处理）

        这是 SimServer 的核心方法，根据传入的参数决定调用哪个页面生成函数（index, search_results, item_page 等）。

        参数:
          session_id (`str`): 当前用户会话的 ID。
          current_url (`str`): 当前页面的 URL（用于判断页面类型）。
          session_int (`int`, optional): 会话 ID 的整数形式，可能用于选择特定目标。
          **kwargs: 包含动作信息的关键字参数，例如：
            - instruction_text: 用于初始页面的指令文本。
            - keywords: 搜索关键词列表。
            - page: 搜索结果的页码。
            - clickable_name: 被点击元素的文本内容（小写）。
            - text_to_clickable: 文本到元素的映射字典。

        返回:
          tuple: 包含以下元素的元组：
            - html (`str`): 生成的页面 HTML。
            - url (`str`): 生成的页面 URL。
            - status (`dict`): 包含奖励和完成状态的字典 (例如 `{'reward': 0.0, 'done': False}`)。
        """
        status = dict(reward=0.0, done=False) # 初始化状态字典

        # 使用 Flask 应用上下文，模拟在 Flask 环境中运行
        with app.app_context(), app.test_request_context():
            # --- 会话和目标处理 ---
            if session_id not in self.user_sessions:
                # 如果是新会话 ID
                # 根据 session_int 或累积权重随机选择一个目标
                idx = (
                    session_int
                    if (session_int is not None and isinstance(session_int, int))
                    else random_idx(self.cum_weights)
                )
                goal = self.goals[idx] # 获取选定的目标
                instruction_text = goal["instruction_text"] # 从目标中获取指令文本
                # 初始化会话字典
                self.user_sessions[session_id] = {"goal": goal, "done": False}
            else:
                # 如果是现有会话，获取指令文本
                instruction_text = self.user_sessions[session_id]["goal"][
                    "instruction_text"
                ]
            # TODO: 这是临时的 hacky 方式，应移除。如果设置了 assigned_instruction_text，则强制使用它。
            if self.assigned_instruction_text is not None:
                instruction_text = self.assigned_instruction_text
                # 同时更新会话中的目标指令文本（这会覆盖原始目标文本）
                self.user_sessions[session_id]["goal"][
                    "instruction_text"
                ] = instruction_text
            session = self.user_sessions[session_id] # 获取当前会话字典

            # --- 动作路由 ---
            if not kwargs:
                # 如果没有提供动作参数 (kwargs 为空)，表示是初始加载或重置
                # 重置会话变量
                kwargs["instruction_text"] = instruction_text # 传入指令文本
                html, url = self.index(session_id, **kwargs) # 调用 index 方法生成初始页面
                # 初始化/重置会话中的其他状态
                self.user_sessions[session_id].update(
                    {
                        "keywords": None,
                        "page": None,
                        "asin": None,
                        "asins": set(),
                        "options": dict(),
                        "actions": defaultdict(int), # 使用 defaultdict 方便计数
                    }
                )
            elif "keywords" in kwargs:
                # 如果提供了关键词，表示是搜索动作
                html, url = self.search_results(session_id, **kwargs) # 调用 search_results 方法
            elif "clickable_name" in kwargs:
                # 如果提供了 clickable_name，表示是点击动作
                clickable_name = kwargs["clickable_name"].lower() # 获取点击目标的名称（小写）

                if clickable_name == END_BUTTON.lower(): # END_BUTTON 通常是 "Buy Now"
                    # 如果点击了 "Buy Now"
                    # 调用 done 方法计算奖励并将状态标记为完成
                    html, url, reward = self.done(session_id, **kwargs)
                    status["reward"] = reward # 更新状态中的奖励
                    status["done"] = True # 更新状态中的完成标志
                elif clickable_name == BACK_TO_SEARCH.lower(): # BACK_TO_SEARCH 通常是 "Back to Search"
                    # 如果点击了 "Back to Search"
                    # 递归调用 receive 方法，不带参数，重置到搜索页面
                    html, url, status = self.receive(session_id, current_url)
                elif (
                    clickable_name == NEXT_PAGE.lower() # NEXT_PAGE 通常是 "Next >"
                    and self.get_page_name(current_url) == "search_results" # 且当前在搜索结果页
                ):
                    # 如果在搜索结果页点击了 "Next Page"
                    # 递归调用 receive 方法，传递当前关键词和下一页页码
                    html, url, status = self.receive(
                        session_id,
                        current_url,
                        keywords=session["keywords"],
                        page=session["page"] + 1, # 页码加 1
                    )
                elif (
                    clickable_name == PREV_PAGE.lower() # PREV_PAGE 通常是 "< Prev"
                    and self.get_page_name(current_url) == "search_results" # 且当前在搜索结果页
                ):
                    # 如果在搜索结果页点击了 "Prev Page"
                    # 递归调用 receive 方法，传递当前关键词和上一页页码
                    html, url, status = self.receive(
                        session_id,
                        current_url,
                        keywords=session["keywords"],
                        page=session["page"] - 1, # 页码减 1
                    )
                elif (
                    clickable_name == PREV_PAGE.lower() # "< Prev"
                    and self.get_page_name(current_url) == "item_sub_page" # 且当前在产品子页面
                ):
                    # 如果在产品子页面点击了 "Prev Page"
                    # 返回到对应的产品主页面
                    html, url = self.item_page(session_id, **kwargs)
                elif (
                    clickable_name == PREV_PAGE.lower() # "< Prev"
                    and self.get_page_name(current_url) == "item_page" # 且当前在产品主页面
                ):
                    # 如果在产品主页面点击了 "Prev Page"
                    # 返回到搜索结果页面
                    html, url = self.search_results(
                        session_id,
                        keywords=session["keywords"], # 使用会话中的关键词
                        page=session["page"], # 使用会话中的页码
                        **kwargs, # 传递其他参数（可能包含 text_to_clickable）
                    )
                elif clickable_name in [k.lower() for k in ACTION_TO_TEMPLATE]:
                    # 如果点击的是 "Description", "Features", "Reviews" 等子页面标签
                    # 渲染对应的产品子页面
                    html, url = self.item_sub_page(session_id, **kwargs)
                else:
                    # 否则，认为是点击了产品链接或选项
                    # 渲染当前的产品主页面（item_page 方法会处理 ASIN 和选项的更新）
                    html, url = self.item_page(session_id, **kwargs)
            else:
                 # 如果 kwargs 不为空，但既没有 keywords 也没有 clickable_name，
                 # 这是一种未预期的状态，可以考虑抛出错误或返回初始页面。
                 # 当前代码似乎没有明确处理这种情况，可能会导致意外行为。
                 # 为了安全起见，可以默认返回初始页面：
                 kwargs["instruction_text"] = instruction_text
                 html, url = self.index(session_id, **kwargs)
                 # 或者抛出错误：
                 # raise ValueError("Invalid state: kwargs provided without 'keywords' or 'clickable_name'")

            return html, url, status # 返回生成的 HTML、URL 和状态

    def get_page_name(self, url):
        """根据 URL 判断当前页面的类型（例如 item_page, search_results）"""
        if url is None:
            return None # 如果 URL 为空，返回 None
        page_names = ["search_results", "item_page", "item_sub_page", "done"] # 定义可能的页面类型
        for page_name in page_names:
            if page_name in url: # 检查 URL 字符串中是否包含页面名称
                return page_name # 如果包含，返回页面名称
        return "" # 如果 URL 不包含任何已知页面名称，则假定是初始页面 (index)


class SimBrowser:
    """用于渲染 WebShop 环境页面 HTML 源码的模拟浏览器"""

    def __init__(self, server):
        """模拟浏览器的构造函数

        参数:
          server (`SimServer`): 用于处理请求和生成页面的 SimServer 实例。
        """
        self.server = server # 存储 SimServer 实例
        self.current_url = None # 当前浏览器地址栏的 URL
        self.page_source = None # 当前页面的 HTML 源码
        self.session_id = None # 当前会话的 ID

    def get(self, url, session_id=None, session_int=None):
        """设置浏览器变量以对应 URL 的链接和页面 HTML（模拟页面加载）

        参数:
          url (`str`): 要访问的 URL。
          session_id (`str`, optional): 要使用的会话 ID。如果为 None，则尝试从 URL 中提取。
          session_int (`int`, optional): 会话 ID 的整数形式，用于选择特定目标。
        """
        # 从 URL 中提取会话 ID（如果未提供）
        self.session_id = url.split("/")[-1] if session_id is None else session_id
        # 调用服务器的 receive 方法获取初始页面的 HTML、URL 和状态
        # 因为是 get 请求（初始加载），所以 kwargs 为空
        self.page_source, _, _ = self.server.receive(
            self.session_id, self.current_url, session_int=session_int
        )
        # 更新浏览器的当前 URL
        self.current_url = url

    def click(self, clickable_name, text_to_clickable):
        """用于在当前页面执行点击动作的 `receive` 处理程序的包装器

        参数:
          clickable_name (`str`): 被点击元素的小写文本内容。
          text_to_clickable (`dict`): 文本到 BeautifulSoup 元素的映射。

        返回:
          dict: 包含奖励和完成状态的状态字典。
        """
        # 调用服务器的 receive 方法处理点击动作
        self.page_source, self.current_url, status = self.server.receive(
            self.session_id,
            current_url=self.current_url, # 传递当前 URL
            clickable_name=clickable_name, # 传递点击目标的名称
            text_to_clickable=text_to_clickable, # 传递文本到元素的映射
        )
        return status # 返回状态

    def search(self, keywords):
        """用于在当前页面执行搜索动作的 `receive` 处理程序的包装器

        参数:
          keywords (`str` or `list`): 搜索关键词（字符串或列表）。

        返回:
          dict: 包含奖励和完成状态的状态字典。
        """
        # 如果关键词是字符串，则按空格分割成列表
        if isinstance(keywords, str):
            keywords = keywords.split(" ")
        # 调用服务器的 receive 方法处理搜索动作
        self.page_source, self.current_url, status = self.server.receive(
            self.session_id,
            current_url=self.current_url, # 传递当前 URL
            keywords=keywords, # 传递关键词列表
        )
        return status # 返回状态

# 注册 Gym 环境
register(
    id="WebAgentTextEnv-v0", # 环境 ID
    entry_point=( # 环境入口点，指向 WebAgentTextEnv 类
        "personalized_shopping.shared_libraries.web_agent_site.envs.web_agent_text_env:WebAgentTextEnv"
    ),
)


