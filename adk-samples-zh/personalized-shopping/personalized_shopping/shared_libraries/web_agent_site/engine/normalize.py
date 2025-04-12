
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

"""用于指定目标和计算奖励的函数。"""

# 导入必要的库
from collections import defaultdict # 用于创建默认值为特定类型的字典
import itertools # 用于创建迭代器进行高效循环（例如排列组合）
import random # 用于生成随机数
from rich import print # 用于美化输出（可选）
import spacy # 用于自然语言处理（词性标注）
from thefuzz import fuzz # 用于模糊字符串匹配
from .normalize import normalize_color # 导入颜色规范化函数

# 加载 spaCy 英语模型 (en_core_web_sm 是一个小模型)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("正在下载 spaCy 模型 'en_core_web_sm'...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


# 定义价格范围列表，用于生成价格上限目标
PRICE_RANGE = [10.0 * i for i in range(1, 100)]


def get_goals(all_products, product_prices, human_goals=True):
    """根据 human_goals 标志获取人类目标或合成目标。"""
    if human_goals:
        return get_human_goals(all_products, product_prices)
    else:
        return get_synthetic_goals(all_products, product_prices)


def get_human_goals(all_products, product_prices):
    """从人类标注数据中提取目标。"""
    goals = [] # 初始化目标列表
    cnt_atts = defaultdict(int) # 统计每个属性出现的次数（未使用？）
    cnt = 0 # 统计跳过的项目数
    for item in all_products:
        asin = item["asin"]
        # 跳过没有 "instructions" 字段的项目
        if "instructions" not in item or not item["instructions"]:
            continue
        # 遍历每个项目的多个指令（目标）
        for product_goal_data in item["instructions"]:
            attributes = product_goal_data.get("instruction_attributes", [])
            # 跳过没有属性的目标
            if len(attributes) == 0:
                cnt += 1
                continue

            # 处理价格上限
            price_upper = 1000000 # 默认价格上限为无穷大
            price_text = "" # 默认价格文本为空
            if product_prices is not None and asin in product_prices:
                price = product_prices[asin]
                # 找到比当前价格高的价格范围
                valid_price_range = [p for p in PRICE_RANGE if p > price]
                # 如果至少有两个更高的价格点
                if len(valid_price_range) >= 2:
                    # 从前 4 个更高的价格点中随机选 2 个，取较大的作为上限
                    sample_range = valid_price_range[:4]
                    if len(sample_range) >= 2:
                        _, price_upper = sorted(random.sample(sample_range, 2))
                        price_text = f", 价格低于 {price_upper:.2f} 美元"
                    elif len(sample_range) == 1: # 如果只有一个更高的价格点
                        price_upper = sample_range[0]
                        price_text = f", 价格低于 {price_upper:.2f} 美元"


            # 构建目标字典
            goals.append(
                {
                    "asin": asin, # 目标商品 ASIN
                    "category": item.get("category"), # 类别
                    "query": item.get("query"), # 原始查询
                    "name": item.get("Title"), # 商品名称 (使用处理后的 Title)
                    "product_category": item.get("product_category"), # 产品类别路径
                    "instruction_text": product_goal_data.get("instruction", "").strip(".") + price_text, # 指令文本 + 价格文本
                    "attributes": attributes, # 目标属性
                    "price_upper": price_upper, # 价格上限
                    "goal_options": product_goal_data.get("instruction_options", {}), # 目标选项
                }
            )
            # 统计属性出现次数（未使用？）
            for att in attributes:
                cnt_atts[att] += 1
    # 为每个目标设置权重为 1（人类目标权重相同）
    for goal in goals:
        goal["weight"] = 1
    print(f"{cnt} 个目标因缺少属性而被跳过。")
    return goals


def get_synthetic_goals(all_products, product_prices):
    """基于产品属性和选项生成合成目标。"""
    goals = [] # 初始化目标列表
    cnt_atts = defaultdict(int) # 统计每个属性出现的次数，用于计算权重
    for product in all_products:
        # 跳过没有指令文本或属性的项目
        if "instruction_text" not in product or product["instruction_text"] is None or \
           "instruction_attributes" not in product or not product["instruction_attributes"]:
            continue

        product_goals = [] # 当前产品的目标列表
        asin = product["asin"]
        attributes = product["instruction_attributes"]
        assert len(attributes) > 0 # 确保至少有一个属性

        # 处理价格上限（逻辑同 get_human_goals）
        price_upper = 1000000
        price_text = ""
        if product_prices is not None and asin in product_prices:
            price = product_prices[asin]
            valid_price_range = [p for p in PRICE_RANGE if p > price]
            if len(valid_price_range) >= 2:
                sample_range = valid_price_range[:4]
                if len(sample_range) >= 2:
                     _, price_upper = sorted(random.sample(sample_range, 2))
                     price_text = f", 价格低于 {price_upper:.2f} 美元"
                elif len(sample_range) == 1:
                    price_upper = sample_range[0]
                    price_text = f", 价格低于 {price_upper:.2f} 美元"

        instruction_text = product["instruction_text"]

        # 处理选项组合
        options = product.get("options", {})
        option_names = sorted(options.keys())
        # 生成所有选项值的笛卡尔积（组合）
        option_value_lists = [options[name] for name in option_names]
        combinations = list(itertools.product(*option_value_lists))

        # 如果没有选项，也创建一个空组合的目标
        if not combinations:
            combinations = [()]

        # 为每个选项组合创建一个目标
        for combination in combinations:
            goal_options = dict() # 当前组合的目标选项
            option_texts = [] # 当前组合的选项文本片段
            for i, opt_value in enumerate(combination):
                opt_name = option_names[i]
                goal_options[opt_name] = opt_value
                option_texts.append(f"{opt_name}: {opt_value}")
            option_text = ", ".join(option_texts)
            option_text_suffix = f" 带有 {option_text}" if option_text else "" # 格式化选项文本后缀

            # 构建目标字典
            product_goals.append(
                {
                    "asin": asin,
                    "category": product.get("category"),
                    "query": product.get("query"),
                    "name": product.get("Title"), # 使用处理后的 Title
                    "product_category": product.get("product_category"),
                    "instruction_text": f"{instruction_text}{option_text_suffix}{price_text}", # 组合指令文本
                    "attributes": attributes,
                    "price_upper": price_upper,
                    "goal_options": goal_options,
                }
            )
            # 统计属性出现次数
            for att in attributes:
                cnt_atts[att] += 1
        goals.extend(product_goals) # 将当前产品的所有目标添加到总列表

    # 计算每个目标的权重（基于属性的稀有度）
    for goal in goals:
        if not goal["attributes"]: # 避免除零错误
            goal["weight"] = 0
        else:
            goal["weight"] = sum(1.0 / cnt_atts[att] for att in goal["attributes"] if cnt_atts[att] > 0) / len(goal["attributes"])
    return goals


def get_type_reward(purchased_product, goal):
    """确定类型奖励 - 捕捉所选产品是否与目标属于同一类别或类型。

    参数:
        purchased_product (dict): 购买的产品信息。
        goal (dict): 目标信息。

    返回:
        dict: 包含类型奖励 (r_type) 和匹配详情的字典。
    """
    # 检查原始查询是否匹配
    query_match = purchased_product.get("query") == goal.get("query")

    # 检查产品类别路径匹配
    purchased_product_category_str = purchased_product.get("product_category", "")
    goal_product_category_str = goal.get("product_category", "")
    purchased_product_category = [x.strip() for x in purchased_product_category_str.split("›")] if purchased_product_category_str else []
    goal_product_category = [x.strip() for x in goal_product_category_str.split("›")] if goal_product_category_str else []
    # 至少需要两个类别层级匹配
    category_match = (
        len(set(purchased_product_category) & set(goal_product_category)) >= 2
    ) if purchased_product_category and goal_product_category else False

    # 检查产品名称（类型）相似度
    purchased_type = purchased_product.get("Title", "") # 使用处理后的 Title
    desired_type = goal.get("name", "")

    # 使用 spaCy 进行词性标注，提取名词和专有名词
    purchased_type_parse = nlp(purchased_type)
    desired_type_parse = nlp(desired_type)

    purchased_type_nouns = [
        t.text.lower()
        for t in purchased_type_parse
        if t.pos_ in ("NOUN", "PROPN") # PNOUN 不标准，改为 NOUN, PROPN
    ]
    desired_type_nouns = [
        t.text.lower()
        for t in desired_type_parse
        if t.pos_ in ("NOUN", "PROPN")
    ]

    # 计算名词交集与目标名词数量的比例
    n_intersect_type = len(set(purchased_type_nouns) & set(desired_type_nouns))
    if len(desired_type_nouns) == 0: # 如果目标名称没有名词
        title_score = 0.2 # 给一个基础分？或者 0？
    else:
        title_score = n_intersect_type / len(desired_type_nouns)

    # 根据匹配情况调整类型奖励 r_type
    r_type = 1.0 # 默认为 1
    match = query_match or category_match or title_score > 0.2
    if not match: # 如果查询、类别、标题相似度都不满足
        r_type = 0.5
    if title_score < 0.1: # 如果标题相似度很低
        r_type = 0.1
    if title_score == 0.0: # 如果标题完全不相似
        r_type = 0.0

    # 返回包含奖励和匹配详情的字典
    return dict(
        r_type=r_type,
        query_match=query_match,
        category_match=category_match,
        title_score=title_score,
    )


def get_attribute_reward(purchased_product, goal):
    """确定购买的产品与目标共享多少属性。

    参数:
        purchased_product (dict): 购买的产品信息。
        goal (dict): 目标信息。

    返回:
        tuple: 包含属性奖励 (r_attr) 和匹配的属性数量 (num_attr_matches) 的元组。
    """
    purchased_attrs = purchased_product.get("Attributes", [])
    goal_attrs = goal.get("attributes", [])

    if not goal_attrs: # 如果目标没有属性
        return 1.0, 0 # 奖励为 1，匹配数为 0

    num_attr_matches = 0
    # 遍历目标属性
    for g_attr in goal_attrs:
        if not isinstance(g_attr, str): continue # 跳过非字符串属性
        g_attr_lower = g_attr.lower() # 转小写比较
        matched = False
        # 检查目标属性是否在购买产品的属性列表中（使用模糊匹配）
        for p_attr in purchased_attrs:
            if not isinstance(p_attr, str): continue # 跳过非字符串属性
            # 使用 token_set_ratio 进行模糊匹配，忽略词序和重复
            score = fuzz.token_set_ratio(p_attr.lower(), g_attr_lower)
            if score > 85: # 设定匹配阈值
                num_attr_matches += 1
                matched = True
                break
        # 如果在属性列表中未找到，则在标题、要点、描述中查找（精确包含）
        if not matched:
             title = purchased_product.get("Title", "").lower()
             bullet_points = " ".join(purchased_product.get("BulletPoints", [])).lower()
             description = purchased_product.get("Description", "").lower()
             if (g_attr_lower in title or
                 g_attr_lower in bullet_points or
                 g_attr_lower in description):
                 num_attr_matches += 1
                 matched = True

    # 计算属性奖励（匹配数 / 目标属性总数）
    r_attr = num_attr_matches / len(goal_attrs)
    return r_attr, num_attr_matches


def get_option_reward(purchased_options, goal_options):
    """计算购买产品的选项与目标选项的奖励。

    参数:
        purchased_options (list[str]): 购买产品选择的选项值列表。
        goal_options (dict | list[tuple]): 目标选项，可以是 {名称: 值} 或 [(名称, 值)]。

    返回:
        tuple: 包含选项奖励 (r_option) 和匹配的选项数量 (num_option_matches) 的元组。
               如果目标没有选项，r_option 为 None。
    """
    # 规范化选项值（例如颜色）
    purchased_option_values = [normalize_color(str(o)) for o in purchased_options]

    # 处理目标选项，提取目标选项值列表
    goal_option_values = []
    if isinstance(goal_options, dict):
        goal_option_values = [normalize_color(str(v)) for v in goal_options.values()]
    elif isinstance(goal_options, list): # 假设是 [(key, value), ...]
        goal_option_values = [normalize_color(str(item[1])) for item in goal_options if len(item) > 1]

    # 如果目标没有选项
    if not goal_option_values:
        return None, 0 # 选项奖励不适用

    # 使用模糊匹配计算匹配的选项数量
    num_option_matches = 0
    for g_option_val in goal_option_values:
        for p_option_val in purchased_option_values:
            # 使用 token_set_ratio 进行模糊匹配
            score = fuzz.token_set_ratio(p_option_val, g_option_val)
            if score > 85: # 设定匹配阈值
                num_option_matches += 1
                break # 找到一个匹配即可

    # 计算选项奖励（匹配数 / 目标选项总数）
    r_option = num_option_matches / len(goal_option_values)
    return r_option, num_option_matches


def get_reward(purchased_product, goal, price, options, **kwargs):
    """计算购买产品相对于目标的总奖励分数。

    参数:
        purchased_product (dict): 购买的产品信息。
        goal (dict): 目标信息。
        price (float): 购买产品的价格。
        options (dict): 购买产品时选择的选项 {选项名称: 选项值}。
        **kwargs: 其他参数，例如 verbose=True 用于返回详细信息。

    返回:
        float | tuple: 如果 verbose=False，返回总奖励分数。
                      如果 verbose=True，返回 (总奖励分数, 详细信息字典)。
    """
    # 1. 计算类型奖励
    r_type_dict = get_type_reward(purchased_product, goal)

    # 2. 计算价格奖励
    goal_price_upper = goal.get("price_upper", -1) # 获取价格上限，默认为 -1
    r_price = (price <= goal_price_upper) if goal_price_upper > 0 and price is not None else None
    # 价格奖励权重因子 (1 表示价格是必需的)
    price_weight_factor = 1 if r_price is not None else 0

    # 3. 计算属性奖励
    r_att, num_attr_matches = get_attribute_reward(purchased_product, goal)
    num_goal_attrs = len(goal.get("attributes", []))

    # 4. 计算选项奖励
    goal_options = goal.get("goal_options", {})
    num_goal_options = len(goal_options)
    purchased_option_values = list(options.values()) if isinstance(options, dict) else []
    r_option, num_option_matches = get_option_reward(
        purchased_option_values, goal_options
    )
    # 选项奖励权重因子 (1 表示选项是必需的)
    option_weight_factor = 1 if r_option is not None else 0

    # 5. 计算总奖励
    # 分子：匹配的属性数 + 匹配的选项数 + 价格是否满足 (1 或 0)
    # 分母：目标属性数 + 目标选项数 + 价格是否必需 (1 或 0)
    denominator = num_goal_attrs + num_goal_options * option_weight_factor + price_weight_factor
    if denominator == 0: # 避免除零错误 (当目标没有属性、选项且价格不重要时)
        total_reward = r_type_dict['r_type'] # 此时奖励仅取决于类型匹配
    else:
        numerator = num_attr_matches + num_option_matches * option_weight_factor + (1 if r_price else 0) * price_weight_factor
        # 先计算属性、选项、价格的综合得分
        combined_score = numerator / denominator
        # 再乘以类型奖励
        total_reward = combined_score * r_type_dict['r_type']

    # 如果需要详细信息，则构建并返回 info 字典
    if kwargs.get("verbose", False):
        info = {
            "r_type": r_type_dict["r_type"],
            "query_match": r_type_dict["query_match"],
            "category_match": r_type_dict["category_match"],
            "title_score": r_type_dict["title_score"],
        }
        if denominator > 0: # 只有当分母不为零时，属性、选项、价格权重才有意义
             info["r_att"] = r_att
             info["w_att"] = num_goal_attrs / denominator if num_goal_attrs > 0 else 0
             if r_option is not None:
                 info["r_option"] = r_option
                 info["w_option"] = num_goal_options / denominator if num_goal_options > 0 else 0
             if r_price is not None:
                 info["r_price"] = float(r_price) # 转为 float
                 info["w_price"] = 1 / denominator
        else: # 如果分母为零，这些奖励和权重不适用
            info["r_att"] = None
            info["w_att"] = 0
            info["r_option"] = None
            info["w_option"] = 0
            info["r_price"] = None
            info["w_price"] = 0

        return total_reward, info
    # 否则只返回总奖励分数
    return total_reward


