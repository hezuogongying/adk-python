
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

"""ChaseSQL 算法使用的常量。"""

from typing import Any # 导入 Any 类型，用于类型注解
import immutabledict # 导入 immutabledict 库，用于创建不可变字典

# ChaseSQL 的参数。
# 使用 immutabledict 确保这些常量在运行时不会被意外修改。
chase_sql_constants_dict: immutabledict.immutabledict[str, Any] = (
    immutabledict.immutabledict({
        # 是否将 SQL 转译为 BigQuery 方言。
        'transpile_to_bigquery': True,
        # 是否处理输入错误（例如，使用 LLM 修正输入 SQL 中的错误）。
        'process_input_errors': True,
        # 是否处理 SQLGlot 工具输出的错误（例如，使用 LLM 修正转译后的 SQL 错误）。
        'process_tool_output_errors': True,
        # 生成候选 SQL 查询的数量。
        'number_of_candidates': 1,
        # 用于生成 SQL 的模型名称。
        'model': 'gemini-1.5-flash', # 模型更新为 1.5 Flash
        # 生成时使用的温度参数（控制随机性，较低的值表示更确定的输出）。
        'temperature': 0.5,
        # SQL 生成方法的类型 ('dc' 表示 Divide and Conquer，'qp' 表示 Query Plan)。
        'generate_sql_type': 'dc',
    })
)


