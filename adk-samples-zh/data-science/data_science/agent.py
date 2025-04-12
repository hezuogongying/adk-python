
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

# 导入 pytest 测试框架
import pytest
# 从 unittest.mock 导入 patch 用于模拟
from unittest.mock import patch
# 从项目中导入所有工具函数
from customer_service.tools.tools import (
    send_call_companion_link,
    approve_discount,
    sync_ask_for_approval,
    update_salesforce_crm,
    access_cart_information,
    modify_cart,
    get_product_recommendations,
    check_product_availability,
    schedule_planting_service,
    get_available_planting_times,
    send_care_instructions,
    generate_qr_code,
)
# 导入日期时间处理模块
from datetime import datetime, timedelta
# 导入日志模块
import logging

# 配置测试文件的日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 测试发送通话伴侣链接工具
def test_send_call_companion_link():
    """测试 send_call_companion_link 工具函数。"""
    phone_number = "+1-555-123-4567"
    result = send_call_companion_link(phone_number)
    # 断言返回结果是否符合预期
    assert result == {
        "status": "success",
        "message": f"链接已发送至 {phone_number}",
    }


# 测试批准折扣工具
def test_approve_discount():
    """测试 approve_discount 工具函数。"""
    result = approve_discount(
        discount_type="percentage", value=10.0, reason="测试折扣"
    )
    # 断言返回结果是否为表示成功的 JSON 字符串
    assert result == '{"status": "ok"}'


# 测试同步请求批准工具
# def test_sync_ask_for_approval(): # 此函数在回调中被拦截，可能不需要直接测试，或者需要模拟回调行为
#     """测试 sync_ask_for_approval 工具函数。"""
#     result = sync_ask_for_approval(
#         discount_type="percentage", value=15.0, reason="测试忠诚度折扣"
#     )
#     # 断言返回结果是否为表示批准的 JSON 字符串（模拟）
#     assert result == '{"status": "approved"}'


# 测试更新 Salesforce CRM 工具
def test_update_salesforce_crm():
    """测试 update_salesforce_crm 工具函数。"""
    customer_id = "123"
    details = {"notes": "更新的客户详情"} # 使用字典作为详情
    result = update_salesforce_crm(customer_id, details)
    # 断言返回结果是否符合预期（模拟）
    assert result == {
        "status": "success",
        "message": "Salesforce 记录已更新。",
    }


# 测试访问购物车信息工具
def test_access_cart_information():
    """测试 access_cart_information 工具函数。"""
    customer_id = "123"
    result = access_cart_information(customer_id)
    # 断言返回结果是否与模拟购物车数据一致
    assert result == {
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


# 测试修改购物车（添加和移除）工具
def test_modify_cart_add_and_remove():
    """测试 modify_cart 工具函数（同时添加和移除商品）。"""
    customer_id = "123"
    items_to_add = [{"product_id": "tree-789", "quantity": 1}]
    items_to_remove = [{"product_id": "soil-123"}] # 移除参数应为列表
    result = modify_cart(customer_id, items_to_add, items_to_remove)
    # 断言返回结果是否符合预期（模拟）
    assert result == {
        "status": "success",
        "message": "购物车更新成功。",
        "items_added": True,
        "items_removed": True,
    }


# 测试获取产品推荐（矮牵牛）工具
def test_get_product_recommendations_petunias():
    """测试 get_product_recommendations 工具函数（植物类型：矮牵牛）。"""
    plant_type = "petunias"
    customer_id = "123"
    result = get_product_recommendations(plant_type, customer_id)
    # 断言返回结果是否与模拟的矮牵牛推荐数据一致
    assert result == {
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


# 测试获取产品推荐（其他植物）工具
def test_get_product_recommendations_other():
    """测试 get_product_recommendations 工具函数（其他植物类型）。"""
    plant_type = "other"
    customer_id = "123"
    result = get_product_recommendations(plant_type, customer_id)
    # 断言返回结果是否与模拟的通用推荐数据一致
    assert result == {
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


# 测试检查产品可用性工具
def test_check_product_availability():
    """测试 check_product_availability 工具函数。"""
    product_id = "soil-123"
    store_id = "主商店"
    result = check_product_availability(product_id, store_id)
    # 断言返回结果是否符合预期（模拟）
    assert result == {"available": True, "quantity": 10, "store": store_id}


# 测试安排种植服务工具
def test_schedule_planting_service():
    """测试 schedule_planting_service 工具函数。"""
    customer_id = "123"
    date = "2024-07-29"
    time_range = "9-12"
    details = "种植矮牵牛"
    result = schedule_planting_service(customer_id, date, time_range, details)
    # 断言返回结果的状态、日期和时间范围是否正确
    assert result["status"] == "success"
    assert result["date"] == date
    assert result["time"] == time_range
    # 断言返回结果中包含 appointment_id 和 confirmation_time
    assert "appointment_id" in result
    assert "confirmation_time" in result


# 测试获取可用种植时间工具
def test_get_available_planting_times():
    """测试 get_available_planting_times 工具函数。"""
    date = "2024-07-29"
    result = get_available_planting_times(date)
    # 断言返回结果是否与模拟的时间段列表一致
    assert result == ["9-12", "13-16"]


# 测试发送养护说明工具
def test_send_care_instructions():
    """测试 send_care_instructions 工具函数。"""
    customer_id = "123"
    plant_type = "矮牵牛"
    delivery_method = "email"
    result = send_care_instructions(customer_id, plant_type, delivery_method)
    # 断言返回结果是否符合预期（模拟）
    assert result == {
        "status": "success",
        "message": f"{plant_type} 的养护说明已通过 {delivery_method} 发送。",
    }


# 测试生成二维码工具
def test_generate_qr_code():
    """测试 generate_qr_code 工具函数。"""
    customer_id = "123"
    discount_value = 10.0
    discount_type = "percentage"
    expiration_days = 30
    result = generate_qr_code(
        customer_id, discount_value, discount_type, expiration_days
    )
    # 断言返回结果的状态和模拟二维码数据是否正确
    assert result["status"] == "success"
    assert result["qr_code_data"] == "MOCK_QR_CODE_DATA"
    # 断言返回结果中包含 expiration_date
    assert "expiration_date" in result
    # 计算预期的过期日期
    expected_expiration_date = datetime.now() + timedelta(days=expiration_days)
    # 断言返回的过期日期是否与计算的预期日期一致（格式化为 YYYY-MM-DD）
    assert result["expiration_date"] == expected_expiration_date.strftime("%Y-%m-%d")


