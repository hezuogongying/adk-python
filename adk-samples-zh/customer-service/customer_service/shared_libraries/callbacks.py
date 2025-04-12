
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
"""客户实体模块。"""

# 导入类型提示
from typing import List, Dict, Optional
# 导入 Pydantic 用于数据验证和模型定义
from pydantic import BaseModel, Field, ConfigDict


# 定义地址数据模型
class Address(BaseModel):
    """
    表示客户的地址。
    """
    street: str           # 街道
    city: str             # 城市
    state: str            # 州/省
    zip: str              # 邮政编码
    model_config = ConfigDict(from_attributes=True) # Pydantic 配置，允许从属性创建模型


# 定义产品数据模型
class Product(BaseModel):
    """
    表示客户购买历史中的产品。
    """
    product_id: str       # 产品 ID
    name: str             # 产品名称
    quantity: int         # 数量
    model_config = ConfigDict(from_attributes=True)


# 定义购买记录数据模型
class Purchase(BaseModel):
    """
    表示客户的购买记录。
    """
    date: str             # 购买日期
    items: List[Product]  # 购买的商品列表
    total_amount: float   # 总金额
    model_config = ConfigDict(from_attributes=True)


# 定义通讯偏好数据模型
class CommunicationPreferences(BaseModel):
    """
    表示客户的通讯偏好。
    """
    email: bool = True            # 是否接收邮件，默认为 True
    sms: bool = True              # 是否接收短信，默认为 True
    push_notifications: bool = True # 是否接收推送通知，默认为 True
    model_config = ConfigDict(from_attributes=True)


# 定义花园资料数据模型
class GardenProfile(BaseModel):
    """
    表示客户的花园资料。
    """
    type: str             # 花园类型（例如：后院）
    size: str             # 花园大小（例如：中等）
    sun_exposure: str     # 日照情况（例如：全日照）
    soil_type: str        # 土壤类型（例如：未知）
    interests: List[str]  # 园艺兴趣（例如：["花卉", "蔬菜"]）
    model_config = ConfigDict(from_attributes=True)


# 定义客户数据模型
class Customer(BaseModel):
    """
    表示一个客户。
    """
    account_number: str             # 账户号码
    customer_id: str                # 客户 ID
    customer_first_name: str        # 客户名字
    customer_last_name: str         # 客户姓氏
    email: str                      # 电子邮件
    phone_number: str               # 电话号码
    customer_start_date: str        # 成为客户的日期
    years_as_customer: int          # 成为客户的年数
    billing_address: Address        # 账单地址
    purchase_history: List[Purchase]# 购买历史
    loyalty_points: int             # 忠诚度积分
    preferred_store: str            # 偏好的商店
    communication_preferences: CommunicationPreferences # 通讯偏好
    garden_profile: GardenProfile   # 花园资料
    # 已安排的预约，默认为空字典
    scheduled_appointments: Dict = Field(default_factory=dict)
    model_config = ConfigDict(from_attributes=True)

    def to_json(self) -> str:
        """
        将 Customer 对象转换为 JSON 字符串。

        返回:
            表示 Customer 对象的 JSON 字符串。
        """
        # 使用 Pydantic 的 model_dump_json 方法，设置缩进为 4
        return self.model_dump_json(indent=4)

    @staticmethod
    def get_customer(current_customer_id: str) -> Optional["Customer"]:
        """
        根据客户 ID 检索客户。

        参数:
            current_customer_id: 要检索的客户的 ID。

        返回:
            如果找到则返回 Customer 对象，否则返回 None。
        """
        # 在实际应用中，这会涉及数据库查找。
        # 在此示例中，我们只返回一个虚拟客户。
        return Customer(
            customer_id=current_customer_id,
            account_number="428765091",
            customer_first_name="Alex",
            customer_last_name="Johnson",
            email="alex.johnson@example.com",
            phone_number="+1-702-555-1212", # 示例电话号码
            customer_start_date="2022-06-10",
            years_as_customer=2,
            billing_address=Address(
                street="123 Main St", city="Anytown", state="CA", zip="12345" # 示例地址
            ),
            purchase_history=[  # 示例购买历史
                Purchase(
                    date="2023-03-05",
                    items=[
                        Product(
                            product_id="fert-111",
                            name="通用肥料",
                            quantity=1,
                        ),
                        Product(
                            product_id="trowel-222",
                            name="园艺小铲",
                            quantity=1,
                        ),
                    ],
                    total_amount=35.98,
                ),
                Purchase(
                    date="2023-07-12",
                    items=[
                        Product(
                            product_id="seeds-333",
                            name="番茄种子 (多品种装)",
                            quantity=2,
                        ),
                        Product(
                            product_id="pots-444",
                            name="陶土花盆 (6英寸)",
                            quantity=4,
                        ),
                    ],
                    total_amount=42.5,
                ),
                Purchase(
                    date="2024-01-20",
                    items=[
                        Product(
                            product_id="gloves-555",
                            name="园艺手套 (皮革)",
                            quantity=1,
                        ),
                        Product(
                            product_id="pruner-666",
                            name="修枝剪",
                            quantity=1,
                        ),
                    ],
                    total_amount=55.25,
                ),
            ],
            loyalty_points=133,
            preferred_store="Anytown Garden Store", # 示例偏好商店
            communication_preferences=CommunicationPreferences(
                email=True, sms=False, push_notifications=True # 示例通讯偏好
            ),
            garden_profile=GardenProfile(
                type="后院",
                size="中等",
                sun_exposure="全日照",
                soil_type="未知",
                interests=["花卉", "蔬菜"], # 示例园艺兴趣
            ),
            scheduled_appointments={}, # 初始无预约
        )


