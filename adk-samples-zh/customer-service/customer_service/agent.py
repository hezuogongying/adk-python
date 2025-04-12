
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

"""工具的单元测试"""

# 从 unittest.mock 导入 MagicMock 和 patch 用于模拟对象和打补丁
from unittest.mock import MagicMock, patch

# 导入 ADK 工具上下文
from google.adk.tools import ToolContext

# 从项目中导入 BigQuery 连接器工具
from brand_search_optimization.tools import bq_connector
# 从项目中导入共享库中的常量
from brand_search_optimization.shared_libraries import constants

# 定义测试类
class TestBrandSearchOptimization:

    # 使用 patch 装饰器模拟 bq_connector 中的 client 对象
    @patch("brand_search_optimization.tools.bq_connector.client")
    def test_get_product_details_for_brand_success(self, mock_client):
        """测试 get_product_details_for_brand 函数成功获取数据的情况。"""
        # 模拟 ToolContext 对象
        mock_tool_context = MagicMock(spec=ToolContext)
        # 设置用户输入内容，模拟用户输入品牌 "cymbal"
        mock_tool_context.user_content.parts = [MagicMock(text="cymbal")]

        # 模拟 BigQuery 查询结果的行数据
        mock_row1 = MagicMock()
        mock_row1.Title = "cymbal Air Max"
        mock_row1.Description = "舒适的跑鞋"
        mock_row1.Attributes = "尺码: 10, 颜色: 蓝色"
        mock_row1.Brand = "cymbal"

        mock_row2 = MagicMock()
        mock_row2.Title = "cymbal 运动 T 恤"
        mock_row2.Description = "棉混纺，短袖"
        mock_row2.Attributes = "尺码: L, 颜色: 黑色"
        mock_row2.Brand = "cymbal"

        # 模拟一个不属于 "cymbal" 品牌的数据行，用于测试 LIMIT 和 WHERE 子句
        mock_row3 = MagicMock()
        mock_row3.Title = "neuravibe Pro 训练短裤"
        mock_row3.Description = "吸湿排汗面料"
        mock_row3.Attributes = "尺码: M, 颜色: 灰色"
        mock_row3.Brand = "neuravibe"

        # 将模拟的行数据放入列表
        mock_results = [mock_row1, mock_row2, mock_row3] # 实际查询应该只返回 mock_row1 和 mock_row2

        # 模拟 QueryJob 对象及其 result 方法
        mock_query_job = MagicMock()
        # 让 result() 方法返回我们模拟的结果列表
        mock_query_job.result.return_value = [mock_row1, mock_row2] # 修正：只返回匹配品牌的结果
        # 让 client.query() 方法返回模拟的 QueryJob 对象
        mock_client.query.return_value = mock_query_job

        # 模拟常量值，以隔离测试环境
        with patch.object(constants, "PROJECT", "test_project"):
            with patch.object(constants, "TABLE_ID", "test_table"):
                # 调用被测试的函数
                markdown_output = bq_connector.get_product_details_for_brand(
                    mock_tool_context
                )
                # 断言：检查不属于 "cymbal" 品牌的产品标题是否未出现在输出中
                assert "neuravibe Pro" not in markdown_output
                # 断言：检查属于 "cymbal" 品牌的产品标题是否出现在输出中
                assert "cymbal Air Max" in markdown_output
                assert "cymbal 运动 T 恤" in markdown_output
                # 断言：检查输出是否包含正确的表头
                assert "| 标题 | 描述 | 属性 | 品牌 |" in markdown_output


