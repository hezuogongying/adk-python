
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
# 为此模块添加文档字符串
"""客户服务 Agent 的工具模块。"""

# 导入日志和 UUID 模块
import logging
import uuid
# 导入日期时间处理模块
from datetime import datetime, timedelta

# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)


# 定义工具：发送通话伴侣链接
def send_call_companion_link(phone_number: str) -> dict: # 返回类型修正为 dict
    """
    向用户的电话号码发送链接以启动视频会话。

    参数:
        phone_number (str): 要发送链接的电话号码。

    返回:
        dict: 包含状态和消息的字典。

    示例:
        >>> send_call_companion_link(phone_number='+12065550123')
        {'status': 'success', 'message': '链接已发送至 +12065550123'}
    """
    # 记录日志信息
    logger.info("正在向 %s 发送通话伴侣链接", phone_number)

    # 返回成功状态和消息
    return {"status": "success", "message": f"链接已发送至 {phone_number}"}


# 定义工具：批准折扣
def approve_discount(discount_type: str, value: float, reason: str) -> str:
    """
    批准用户请求的固定金额或百分比折扣。

    参数:
        discount_type (str): 折扣类型，"percentage"（百分比）或 "flat"（固定金额）。
        value (float): 折扣值。
        reason (str): 折扣原因。

    返回:
        str: 指示批准状态的 JSON 字符串。

    示例:
        >>> approve_discount(discount_type='percentage', value=10.0, reason='客户忠诚度')
        '{"status": "ok"}'
    """
    # 记录日志信息
    logger.info(
        "正在批准 %s 折扣，值为 %s，原因：%s", discount_type, value, reason
    )

    # 记录工具内部调用日志
    logger.info("在工具调用内部")
    # 返回表示成功的 JSON 字符串
    return '{"status": "ok"}'


# 定义工具：同步请求批准折扣
def sync_ask_for_approval(discount_type: str, value: float, reason: str) -> str:
    """
    向经理请求批准折扣。

    参数:
        discount_type (str): 折扣类型，"percentage"（百分比）或 "flat"（固定金额）。
        value (float): 折扣值。
        reason (str): 折扣原因。

    返回:
        str: 指示批准状态的 JSON 字符串。

    示例:
        >>> sync_ask_for_approval(discount_type='percentage', value=15, reason='客户忠诚度')
        '{"status": "approved"}' # 示例中返回已批准状态
    """
    # 记录日志信息
    logger.info(
        "正在为 %s 折扣请求批准，值为 %s，原因：%s",
        discount_type,
        value,
        reason,
    )
    # 返回表示已批准的 JSON 字符串（模拟）
    return '{"status": "approved"}'


# 定义工具：更新 Salesforce CRM
def update_salesforce_crm(customer_id: str, details: dict) -> dict:
    """
    使用客户详情更新 Salesforce CRM。

    参数:
        customer_id (str): 客户 ID。
        details (dict): 要在 Salesforce 中更新的详情字典。

    返回:
        dict: 包含状态和消息的字典。

    示例:
        >>> update_salesforce_crm(customer_id='123', details={
            'appointment_date': '2024-07-25',
            'appointment_time': '9-12',
            'services': '种植',
            'discount': '种植服务 85 折',
            'qr_code': '下次店内购物 9 折'})
        {'status': 'success', 'message': 'Salesforce 记录已更新。'}
    """
    # 记录日志信息
    logger.info(
        "正在为客户 ID %s 更新 Salesforce CRM，详情：%s",
        customer_id,
        details,
    )
    # 返回成功状态和消息（模拟）
    return {"status": "success", "message": "Salesforce 记录已更新。"}


# 定义工具：访问购物车信息
def access_cart_information(customer_id: str) -> dict:
    """
    访问指定客户的购物车信息。

    参数:
        customer_id (str): 客户 ID。

    返回:
        dict: 表示购物车内容的字典。

    示例:
        >>> access_cart_information(customer_id='123')
        {'items': [{'product_id': 'soil-123', 'name': '标准盆栽土', 'quantity': 1}, {'product_id': 'fert-456', 'name': '通用肥料', 'quantity': 1}], 'subtotal': 25.98}
    """
    # 记录日志信息
    logger.info("正在访问客户 ID 的购物车信息：%s", customer_id)

    # 模拟 API 响应 - 替换为实际的 API 调用
    mock_cart = {
        "items": [
            {
                "product_id": "soil-123",
                "name": "标准盆栽土",
                "quantity": 1,
            },
            {
                "product_id": "fert-456",
                "name": "通用肥料",
                "quantity": 1,
            },
        ],
        "subtotal": 25.98,
    }
    return mock_cart


# 定义工具：修改购物车
def modify_cart(
    customer_id: str, items_to_add: list[dict], items_to_remove: list[dict]
) -> dict:
    """通过添加和/或移除商品来修改用户的购物车。

    参数:
        customer_id (str): 客户 ID。
        items_to_add (list): 字典列表，每个字典包含 'product_id' 和 'quantity'。
        items_to_remove (list): 要移除的 product_id 列表（应为字典列表，包含 product_id 和 quantity 或仅 product_id）。

    返回:
        dict: 指示购物车修改状态的字典。
    示例:
        >>> modify_cart(customer_id='123', items_to_add=[{'product_id': 'soil-456', 'quantity': 1}, {'product_id': 'fert-789', 'quantity': 1}], items_to_remove=[{'product_id': 'fert-112'}]) # 移除参数修正
        {'status': 'success', 'message': '购物车更新成功。', 'items_added': True, 'items_removed': True}
    """

    # 记录日志信息
    logger.info("正在修改客户 ID 的购物车：%s", customer_id)
    logger.info("添加商品：%s", items_to_add)
    logger.info("移除商品：%s", items_to_remove)
    # 模拟 API 响应 - 替换为实际的 API 调用
    return {
        "status": "success",
        "message": "购物车更新成功。",
        "items_added": bool(items_to_add), # 根据列表是否为空判断
        "items_removed": bool(items_to_remove), # 根据列表是否为空判断
    }


# 定义工具：获取产品推荐
def get_product_recommendations(plant_type: str, customer_id: str) -> dict:
    """根据植物类型提供产品推荐。

    参数:
        plant_type (str): 植物类型（例如，'矮牵牛', '喜阳一年生植物'）。
        customer_id (str): 可选的客户 ID，用于个性化推荐。

    返回:
        dict: 推荐产品的字典。示例：
        {'recommendations': [
            {'product_id': 'soil-456', 'name': '促花盆栽混合土', 'description': '...'},
            {'product_id': 'fert-789', 'name': '花力肥料', 'description': '...'}
        ]}
    """
    # 记录日志信息
    logger.info(
        "正在为植物类型：%s 和客户 %s 获取产品推荐",
        plant_type,
        customer_id,
    )
    # 模拟 API 响应 - 替换为实际的 API 调用或推荐引擎
    # 将植物类型转换为小写进行比较
    plant_type_lower = plant_type.lower()
    if plant_type_lower == "petunias" or plant_type_lower == "矮牵牛":
        recommendations = {
            "recommendations": [
                {
                    "product_id": "soil-456",
                    "name": "促花盆栽混合土",
                    "description": "提供矮牵牛喜爱的额外养分。",
                },
                {
                    "product_id": "fert-789",
                    "name": "花力肥料",
                    "description": "专为开花一年生植物配制。",
                },
            ]
        }
    elif plant_type_lower == "tomatos" or plant_type_lower == "番茄": # 添加对番茄的处理
        recommendations = {
            "recommendations": [
                {
                    "product_id": "soil-veg-01",
                    "name": "蔬菜专用盆栽土",
                    "description": "富含有机质，适合番茄生长。",
                },
                {
                    "product_id": "fert-veg-02",
                    "name": "番茄专用肥料",
                    "description": "提供番茄结果所需的均衡营养。",
                },
            ]
        }
    else:
        # 默认推荐通用产品
        recommendations = {
            "recommendations": [
                {
                    "product_id": "soil-123",
                    "name": "标准盆栽土",
                    "description": "一种良好的通用盆栽土。",
                },
                {
                    "product_id": "fert-456",
                    "name": "通用肥料",
                    "description": "适用于多种植物。",
                },
            ]
        }
    return recommendations


# 定义工具：检查产品可用性
def check_product_availability(product_id: str, store_id: str) -> dict:
    """检查指定商店（或自提）的产品可用性。

    参数:
        product_id (str): 要检查的产品 ID。
        store_id (str): 商店 ID（或 'pickup' 表示自提可用性）。

    返回:
        dict: 指示可用性的字典。示例：
        {'available': True, 'quantity': 10, 'store': '主商店'}

    示例:
        >>> check_product_availability(product_id='soil-456', store_id='pickup')
        {'available': True, 'quantity': 10, 'store': 'pickup'}
    """
    # 记录日志信息
    logger.info(
        "正在检查产品 ID：%s 在商店：%s 的可用性",
        product_id,
        store_id,
    )
    # 模拟 API 响应 - 替换为实际的 API 调用
    return {"available": True, "quantity": 10, "store": store_id}


# 定义工具：安排种植服务
def schedule_planting_service(
    customer_id: str, date: str, time_range: str, details: str
) -> dict:
    """安排种植服务预约。

    参数:
        customer_id (str): 客户 ID。
        date (str):  期望日期 (YYYY-MM-DD)。
        time_range (str): 期望时间范围 (例如, "9-12")。
        details (str): 任何附加详情 (例如, "种植矮牵牛")。

    返回:
        dict: 指示安排状态的字典。示例：
        {'status': 'success', 'appointment_id': '12345', 'date': '2024-07-29', 'time': '9:00 AM - 12:00 PM'}

    示例:
        >>> schedule_planting_service(customer_id='123', date='2024-07-29', time_range='9-12', details='种植矮牵牛')
        {'status': 'success', 'appointment_id': 'some_uuid', 'date': '2024-07-29', 'time': '9-12', 'confirmation_time': '2024-07-29 9:00'}
    """
    # 记录日志信息
    logger.info(
        "正在为客户 ID：%s 安排种植服务，日期：%s (%s)",
        customer_id,
        date,
        time_range,
    )
    logger.info("详情：%s", details)
    # 模拟 API 响应 - 替换为实际的 API 调用到您的排程系统
    # 根据日期和时间范围计算确认时间
    start_time_str = time_range.split("-")[0]  # 获取开始时间 (例如, "9")
    # 格式化确认时间字符串 (例如, "2024-07-29 9:00")
    confirmation_time_str = f"{date} {start_time_str}:00"

    return {
        "status": "success",
        # 生成唯一的预约 ID
        "appointment_id": str(uuid.uuid4()),
        "date": date,
        "time": time_range,
        # 用于日历邀请的格式化时间
        "confirmation_time": confirmation_time_str,
    }


# 定义工具：获取可用种植时间
def get_available_planting_times(date: str) -> list:
    """检索给定日期的可用种植服务时间段。

    参数:
        date (str): 要检查的日期 (YYYY-MM-DD)。

    返回:
        list: 可用时间范围的列表。

    示例:
        >>> get_available_planting_times(date='2024-07-29')
        ['9-12', '13-16']
    """
    # 记录日志信息
    logger.info("正在检索 %s 的可用种植时间", date)
    # 模拟 API 响应 - 替换为实际的 API 调用
    # 生成一些模拟时间段，确保格式正确：
    return ["9-12", "13-16"]


# 定义工具：发送养护说明
def send_care_instructions(
    customer_id: str, plant_type: str, delivery_method: str
) -> dict:
    """通过电子邮件或短信发送特定植物类型的养护说明。

    参数:
        customer_id (str):  客户 ID。
        plant_type (str): 植物类型。
        delivery_method (str): 'email' (默认) 或 'sms'。

    返回:
        dict: 指示状态的字典。

    示例:
        >>> send_care_instructions(customer_id='123', plant_type='矮牵牛', delivery_method='email')
        {'status': 'success', 'message': '矮牵牛的养护说明已通过电子邮件发送。'}
    """
    # 记录日志信息
    logger.info(
        "正在通过 %s 向客户：%s 发送 %s 的养护说明",
        delivery_method,
        customer_id,
        plant_type,
    )
    # 模拟 API 响应 - 替换为实际的 API 调用或电子邮件/短信发送逻辑
    return {
        "status": "success",
        "message": f"{plant_type} 的养护说明已通过 {delivery_method} 发送。",
    }


# 定义工具：生成二维码
def generate_qr_code(
    customer_id: str,
    discount_value: float,
    discount_type: str,
    expiration_days: int,
) -> dict:
    """生成折扣二维码。

    参数:
        customer_id (str): 客户 ID。
        discount_value (float): 折扣值 (例如, 10 表示 10%)。
        discount_type (str): "percentage" (默认) 或 "fixed" (固定金额)。
        expiration_days (int): 二维码过期的天数。

    返回:
        dict: 包含二维码数据（或其链接）的字典。示例：
        {'status': 'success', 'qr_code_data': '...', 'expiration_date': '2024-08-28'}

    示例:
        >>> generate_qr_code(customer_id='123', discount_value=10.0, discount_type='percentage', expiration_days=30)
        {'status': 'success', 'qr_code_data': 'MOCK_QR_CODE_DATA', 'expiration_date': 'YYYY-MM-DD'} # 日期会动态生成
    """
    # 记录日志信息
    logger.info(
        "正在为客户：%s 生成二维码，折扣：%s - %s。",
        customer_id,
        discount_value,
        discount_type,
    )
    # 模拟 API 响应 - 替换为实际的二维码生成库
    # 计算过期日期
    expiration_date = (
        datetime.now() + timedelta(days=expiration_days)
    ).strftime("%Y-%m-%d")
    return {
        "status": "success",
        # 替换为实际的二维码数据
        "qr_code_data": "MOCK_QR_CODE_DATA",
        "expiration_date": expiration_date,
    }

