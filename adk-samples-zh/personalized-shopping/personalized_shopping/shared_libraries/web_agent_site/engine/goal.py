
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

"""WebShop 引擎核心逻辑。"""

# 导入必要的库
from ast import literal_eval # 用于安全地评估字符串表达式（例如列表）
from collections import defaultdict # 用于创建默认值为特定类型的字典
from decimal import Decimal # 用于精确的十进制运算（处理价格）
import json # 用于处理 JSON 数据
import os # 用于操作系统相关功能（路径处理）
import random # 用于生成随机数
import re # 用于正则表达式操作

# 从 flask 导入 render_template_string 用于渲染 HTML 模板字符串
from flask import render_template_string
# 从 pyserini 导入 LuceneSearcher 用于基于 Lucene 的搜索
from pyserini.search.lucene import LuceneSearcher
# 从 rich 导入 print 用于美化输出（可选）
from rich import print
# 从 tqdm 导入 tqdm 用于显示进度条
from tqdm import tqdm

# 导入当前包下的工具函数和常量
from ..utils import (
    BASE_DIR, # 基础目录路径
    DEFAULT_ATTR_PATH, # 默认属性文件路径
    HUMAN_ATTR_PATH, # 人类标注属性文件路径
)

# 定义模板文件所在的目录
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

# 定义常量
SEARCH_RETURN_N = 50 # 搜索返回结果的数量
PRODUCT_WINDOW = 10 # 每页显示的产品数量
TOP_K_ATTR = 10 # （未使用）可能用于显示热门属性

# 定义特殊按钮的文本
END_BUTTON = "Buy Now" # 立即购买
NEXT_PAGE = "Next >" # 下一页
PREV_PAGE = "< Prev" # 上一页
BACK_TO_SEARCH = "Back to Search" # 返回搜索

# 定义操作名称到 HTML 模板文件的映射
ACTION_TO_TEMPLATE = {
    "Description": "description_page.html", # 描述页面
    "Features": "features_page.html", # 功能页面
    "Reviews": "review_page.html", # 评论页面
    "Attributes": "attributes_page.html", # 属性页面
}


def map_action_to_html(action, **kwargs):
    """根据操作名称和参数渲染相应的 HTML 页面。

    参数:
        action (str): 操作字符串，例如 "search[keyword]" 或 "click[button_name]"。
        **kwargs: 传递给 HTML 模板的其他参数。

    返回:
        str: 渲染后的 HTML 字符串。
    """
    # 解析操作字符串获取操作名称和参数
    action_name, action_arg = parse_action(action)
    # 根据不同的操作渲染不同的模板
    if action_name == "start": # 开始页面（搜索页）
        path = os.path.join(TEMPLATE_DIR, "search_page.html")
        html = render_template_string(
            read_html_template(path=path),
            session_id=kwargs["session_id"],
            instruction_text=kwargs["instruction_text"],
        )
    elif action_name == "search": # 搜索结果页
        path = os.path.join(TEMPLATE_DIR, "results_page.html")
        html = render_template_string(
            read_html_template(path=path),
            session_id=kwargs["session_id"],
            products=kwargs["products"], # 当前页的产品列表
            keywords=kwargs["keywords"], # 搜索关键词
            page=kwargs["page"], # 当前页码
            total=kwargs["total"], # 搜索结果总数
            instruction_text=kwargs["instruction_text"], # 指令文本
        )
    elif action_name == "click" and action_arg == END_BUTTON: # 完成页面（购买后）
        path = os.path.join(TEMPLATE_DIR, "done_page.html")
        html = render_template_string(
            read_html_template(path),
            session_id=kwargs["session_id"],
            reward=kwargs["reward"], # 奖励分数
            asin=kwargs["asin"], # 购买的商品 ASIN
            options=kwargs["options"], # 选择的商品选项
            reward_info=kwargs.get("reward_info"), # 奖励的详细信息
            goal_attrs=kwargs.get("goal_attrs"), # 目标属性
            purchased_attrs=kwargs.get("purchased_attrs"), # 购买商品的属性
            goal=kwargs.get("goal"), # 目标信息
            mturk_code=kwargs.get("mturk_code"), # MTurk 兑换码
            query=kwargs.get("query"), # 原始查询
            category=kwargs.get("category"), # 类别
            product_category=kwargs.get("product_category"), # 产品类别路径
        )
    elif action_name == "click" and action_arg in ACTION_TO_TEMPLATE: # 商品子页面（描述、功能、评论、属性）
        path = os.path.join(TEMPLATE_DIR, ACTION_TO_TEMPLATE[action_arg])
        html = render_template_string(
            read_html_template(path),
            session_id=kwargs["session_id"],
            product_info=kwargs["product_info"], # 商品信息
            keywords=kwargs["keywords"], # 搜索关键词
            page=kwargs["page"], # 返回搜索结果时的页码
            asin=kwargs["asin"], # 商品 ASIN
            options=kwargs["options"], # 已选选项
            instruction_text=kwargs.get("instruction_text"), # 指令文本
        )
    elif action_name == "click": # 商品详情页
        path = os.path.join(TEMPLATE_DIR, "item_page.html")
        html = render_template_string(
            read_html_template(path),
            session_id=kwargs["session_id"],
            product_info=kwargs["product_info"], # 商品信息
            keywords=kwargs["keywords"], # 搜索关键词
            page=kwargs["page"], # 返回搜索结果时的页码
            asin=kwargs["asin"], # 商品 ASIN
            options=kwargs["options"], # 已选选项
            instruction_text=kwargs.get("instruction_text"), # 指令文本
            show_attrs=kwargs["show_attrs"], # 是否显示属性
        )
    else:
        raise ValueError("无法识别的操作名称。")
    return html


def read_html_template(path):
    """读取 HTML 模板文件内容。"""
    with open(path) as f:
        template = f.read()
    return template


def parse_action(action):
    """解析操作字符串为操作名称及其参数。
       例如 "search[keyword]" -> ("search", "keyword")
             "click[button]" -> ("click", "button")
             "start" -> ("start", None)
    """
    pattern = re.compile(r"(.+)\[(.+)\]") # 正则表达式匹配 "name[arg]" 格式
    m = re.match(pattern, action)
    if m is None: # 如果不匹配，则认为只有操作名称
        action_name = action
        action_arg = None
    else: # 如果匹配，则提取名称和参数
        action_name, action_arg = m.groups()
    return action_name, action_arg


def convert_web_app_string_to_var(name, string):
    """将从 Web 应用获取的字符串转换为适当的变量类型（已弃用或未使用？）。"""
    if name == "keywords":
        keywords = string
        if keywords.startswith("["): # 如果是列表形式的字符串
            keywords = literal_eval(keywords) # 安全地评估为列表
        else:
            keywords = [keywords] # 否则视为单个关键词的列表
        var = keywords
    elif name == "page":
        page = string
        page = int(page) # 转换为整数
        var = page
    else:
        raise ValueError("无法识别的变量名称。")
    return var


def get_top_n_product_from_keywords(
    keywords,
    search_engine,
    all_products,
    product_item_dict,
    attribute_to_asins=None, # (未使用)
):
    """根据关键词从搜索引擎或预定义列表中获取前 N 个产品。

    参数:
        keywords (list[str]): 关键词列表。特殊前缀 <r>, <a>, <c>, <q> 有特殊含义。
        search_engine (LuceneSearcher): Pyserini 搜索引擎实例。
        all_products (list[dict]): 所有产品的列表（用于特殊查询）。
        product_item_dict (dict): ASIN 到产品信息的映射。
        attribute_to_asins (dict, optional): 属性到 ASIN 列表的映射 (未使用)。

    返回:
        list[dict]: 搜索到的产品信息列表。
    """
    if keywords[0] == "<r>": # 随机返回 N 个产品
        top_n_products = random.sample(all_products, k=SEARCH_RETURN_N)
    elif keywords[0] == "<a>": # 根据属性查找产品 (未使用)
        attribute = " ".join(keywords[1:]).strip()
        asins = attribute_to_asins[attribute]
        top_n_products = [p for p in all_products if p["asin"] in asins]
    elif keywords[0] == "<c>": # 根据类别查找产品
        category = keywords[1].strip()
        top_n_products = [p for p in all_products if p.get("category") == category] # 使用 get 避免 KeyError
    elif keywords[0] == "<q>": # 根据预设查询查找产品
        query = " ".join(keywords[1:]).strip()
        top_n_products = [p for p in all_products if p.get("query") == query] # 使用 get 避免 KeyError
    else: # 执行常规关键词搜索
        keywords_str = " ".join(keywords)
        # 使用 Pyserini 搜索引擎进行搜索
        hits = search_engine.search(keywords_str, k=SEARCH_RETURN_N)
        # 获取命中文档
        docs = [search_engine.doc(hit.docid) for hit in hits]
        # 从文档中提取 ASIN
        top_n_asins = [json.loads(doc.raw())["id"] for doc in docs]
        # 根据 ASIN 从 product_item_dict 中获取产品信息
        top_n_products = [
            product_item_dict[asin] for asin in top_n_asins if asin in product_item_dict
        ]
    # 确保返回列表长度不超过 SEARCH_RETURN_N (虽然搜索时已限制，但特殊查询可能超出)
    return top_n_products[:SEARCH_RETURN_N]


def get_product_per_page(top_n_products, page):
    """根据页码从产品列表中获取当前页的产品。"""
    start_index = (page - 1) * PRODUCT_WINDOW
    end_index = page * PRODUCT_WINDOW
    return top_n_products[start_index:end_index]


def generate_product_prices(all_products):
    """为所有产品生成（或提取）价格。"""
    product_prices = dict()
    for product in all_products:
        asin = product["asin"]
        pricing = product.get("pricing") # 从预处理后的 product 字典获取价格信息
        if not pricing: # 如果没有价格信息
            price = 100.0 # 设为默认值
        elif isinstance(pricing, list) and len(pricing) == 1: # 如果是单个价格
            price = pricing[0]
        elif isinstance(pricing, list) and len(pricing) >= 2: # 如果是价格范围
            price = random.uniform(*pricing[:2]) # 在范围内随机取值
        else: # 其他情况（例如字符串价格，理论上不应发生在此阶段）
            price = 100.0 # 设为默认值
        product_prices[asin] = price
    return product_prices


def init_search_engine(num_products=None):
    """根据产品数量初始化 Pyserini 搜索引擎。"""
    # 根据产品数量选择索引目录
    if num_products == 100:
        indexes = "indexes_100"
    elif num_products == 1000:
        indexes = "indexes_1k"
    elif num_products == 10000:
        indexes = "indexes_10k"
    elif num_products == 50000:
        indexes = "indexes_50k"
    elif num_products is None: # 默认使用 1k
        indexes = "indexes_1k"
    else:
        raise NotImplementedError(
            f"产品数量 {num_products} 尚不支持。"
        )
    # 获取索引路径
    index_path = os.path.join(BASE_DIR, f"../search_engine/{indexes}")
    # 检查索引是否存在
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"未找到 Pyserini 索引目录: {index_path}。请先运行 convert_product_file_format.py 和 Pyserini 索引脚本。")
    # 初始化并返回 LuceneSearcher
    search_engine = LuceneSearcher(index_path)
    return search_engine


def clean_product_keys(products):
    """清理产品字典中不再需要的键（可选步骤）。"""
    keys_to_remove = [
        "product_information", "brand", "brand_url", "list_price",
        "availability_quantity", "availability_status", "total_reviews",
        "total_answered_questions", "seller_id", "seller_name",
        "fulfilled_by_amazon", "fast_track_message", "aplus_present",
        "small_description_old"
    ]
    for product in products:
        for key in keys_to_remove:
            product.pop(key, None) # 使用 pop 的第二个参数避免 KeyError
    print("已清理产品键。")
    return products


def load_products(filepath, num_products=None, human_goals=True):
    """加载和预处理产品数据。

    参数:
        filepath (str): 原始产品数据文件路径 (items_shuffle.json)。
        num_products (int, optional): 要加载的产品数量。默认为 None（加载全部）。
        human_goals (bool): 是否加载人类标注的目标。默认为 True。

    返回:
        tuple: 包含 all_products, product_item_dict, product_prices, attribute_to_asins 的元组。
    """
    # TODO: 将清理和属性加载移至预处理步骤 -> 强制单一数据源
    try:
        with open(filepath) as f:
            products = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"未找到产品数据文件: {filepath}")
    print("产品已加载。")
    # products = clean_product_keys(products) # 清理键，如果需要的话

    # 加载评论数据（目前注释掉了）
    # all_reviews = dict()
    # all_ratings = dict()
    # try:
    #     with open(DEFAULT_REVIEW_PATH) as f:
    #         reviews = json.load(f)
    #     for r in reviews:
    #         all_reviews[r['asin']] = r['reviews']
    #         all_ratings[r['asin']] = r['average_rating']
    # except FileNotFoundError:
    #     print(f"警告：未找到评论文件 {DEFAULT_REVIEW_PATH}。评论和评分将不可用。")
    all_reviews = {} # 暂时为空
    all_ratings = {} # 暂时为空

    # 加载属性数据
    attributes = {}
    human_attributes = {}
    try:
        with open(DEFAULT_ATTR_PATH) as f:
            attributes = json.load(f)
    except FileNotFoundError:
        print(f"警告：未找到默认属性文件 {DEFAULT_ATTR_PATH}。")
    if human_goals:
        try:
            with open(HUMAN_ATTR_PATH) as f:
                human_attributes = json.load(f)
        except FileNotFoundError:
            print(f"警告：未找到人类标注属性文件 {HUMAN_ATTR_PATH}。人类目标可能不完整。")
    print("属性已加载。")

    asins = set() # 用于跟踪已添加的 ASIN，避免重复
    all_products = [] # 存储处理后的产品列表
    attribute_to_asins = defaultdict(set) # 属性到 ASIN 的映射

    # 根据 num_products 限制产品数量
    if num_products is not None:
        # 假设 items_shuffle.json 中的产品已经打乱
        products = products[:num_products]

    # 遍历原始产品数据进行处理
    for i, p in tqdm(enumerate(products), total=len(products)):
        asin = p.get("asin")
        # 跳过无效或过长的 ASIN
        if asin is None or asin == "nan" or len(asin) > 10:
            continue
        # 跳过重复的 ASIN
        if asin in asins:
            continue
        else:
            asins.add(asin)

        # 提取和格式化所需字段
        product_data = {}
        product_data["asin"] = asin
        product_data["category"] = p.get("category")
        product_data["query"] = p.get("query")
        product_data["product_category"] = p.get("product_category")
        product_data["Title"] = p.get("name") # 重命名为 Title
        product_data["Description"] = p.get("full_description") # 重命名为 Description
        product_data["Reviews"] = all_reviews.get(asin, []) # 获取评论，默认为空列表
        product_data["Rating"] = all_ratings.get(asin, "N.A.") # 获取评分，默认为 "N.A."
        # 格式化评论结构（如果加载了评论数据）
        for r in product_data["Reviews"]:
            if "score" not in r and "stars" in r:
                r["score"] = r.pop("stars")
            if "review" in r and "body" not in r:
                r["body"] = r.pop("review")
            elif "review" not in r and "body" not in r:
                 r["body"] = ""

        # 处理要点 (BulletPoints)
        bullet_points = p.get("small_description")
        if isinstance(bullet_points, list):
            product_data["BulletPoints"] = bullet_points
        elif isinstance(bullet_points, str):
            product_data["BulletPoints"] = [bullet_points]
        else:
            product_data["BulletPoints"] = []

        # 处理价格 (pricing)
        pricing_str = p.get("pricing")
        pricing_list = []
        price_tag = "N/A" # 默认价格标签
        if pricing_str:
            try:
                # 尝试解析价格字符串，例如 "$10.99", "$10.99 to $15.99"
                prices = [
                    float(Decimal(re.sub(r"[^\d.]", "", price)))
                    for price in pricing_str.split("$")[1:] if re.sub(r"[^\d.]", "", price)
                ]
                if len(prices) == 1:
                    pricing_list = prices
                    price_tag = f"${prices[0]:.2f}" # 格式化为两位小数
                elif len(prices) >= 2:
                    pricing_list = sorted(prices[:2]) # 取前两个并排序
                    price_tag = f"${pricing_list[0]:.2f} 到 ${pricing_list[1]:.2f}"
                else: # 如果无法解析出数字价格
                    pricing_list = [100.0] # 设为默认值
                    price_tag = "$100.00"
            except (ValueError, TypeError, IndexError):
                 pricing_list = [100.0] # 解析失败设为默认值
                 price_tag = "$100.00"
        else:
            pricing_list = [100.0] # 无价格信息设为默认值
            price_tag = "$100.00"
        product_data["pricing"] = pricing_list # 存储解析后的价格列表
        product_data["Price"] = price_tag # 存储用于显示的价格标签

        # 处理选项 (options)
        options = dict()
        customization_options = p.get("customization_options")
        option_to_image = dict() # 选项值到图片的映射
        if customization_options and isinstance(customization_options, dict):
            for option_name, option_contents in customization_options.items():
                if option_contents is None or not isinstance(option_contents, list):
                    continue
                option_name_lower = option_name.lower() # 选项名称转小写
                option_values = []
                for option_content in option_contents:
                    if not isinstance(option_content, dict) or "value" not in option_content:
                        continue
                    # 选项值转小写，替换斜杠
                    option_value = (
                        option_content["value"].strip().replace("/", " | ").lower()
                    )
                    option_image = option_content.get("image", None) # 获取选项图片
                    option_values.append(option_value)
                    if option_image:
                        option_to_image[option_value] = option_image
                if option_values: # 只有当有有效选项值时才添加
                    options[option_name_lower] = option_values
        product_data["options"] = options # 存储处理后的选项字典
        product_data["option_to_image"] = option_to_image # 存储选项图片映射

        # 处理属性 (Attributes) 和指令 (instructions)
        product_attributes = attributes.get(asin, {}).get("attributes", [])
        product_data["Attributes"] = product_attributes if product_attributes else ["DUMMY_ATTR"]

        if human_goals:
            # 如果使用人类目标，从 human_attributes 加载指令
            product_data["instructions"] = human_attributes.get(asin, [])
        else:
            # 否则，从 attributes 加载指令文本和属性
            product_data["instruction_text"] = attributes.get(asin, {}).get("instruction")
            product_data["instruction_attributes"] = attributes.get(asin, {}).get("instruction_attributes")

        # 处理主图片 (MainImage)
        images = p.get("images")
        product_data["MainImage"] = images[0] if images and isinstance(images, list) else None

        # 处理查询 (query)
        query = p.get("query")
        product_data["query"] = query.lower().strip() if isinstance(query, str) else None

        # 将处理后的产品数据添加到列表
        all_products.append(product_data)

        # 更新 attribute_to_asins 映射
        for attr in product_data["Attributes"]:
            if attr != "DUMMY_ATTR": # 不添加虚拟属性
                attribute_to_asins[attr].add(asin)

    # 创建 ASIN 到产品信息的映射字典
    product_item_dict = {p["asin"]: p for p in all_products}
    # 生成产品价格字典
    product_prices = generate_product_prices(all_products)

    return all_products, product_item_dict, product_prices, attribute_to_asins


