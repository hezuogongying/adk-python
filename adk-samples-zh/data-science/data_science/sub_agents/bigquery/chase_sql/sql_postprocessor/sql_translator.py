
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

"""用于对 SQL 翻译进行任何修正的 Prompt 模板。"""

# 版本 1.0 的修正 Prompt 模板
CORRECTION_PROMPT_TEMPLATE_V1_0 = """
您是一位精通多种数据库和 SQL 方言的专家。
给定一个针对 SQL 方言 `{sql_dialect}` 格式化的 SQL 查询：

{sql_query}
{schema_insert}
此 SQL 查询可能包含以下错误：
{errors}

请修正该 SQL 查询，确保其格式对于 SQL 方言 `{sql_dialect}` 是正确的。

不要更改查询中的任何表名或列名。但是，您可以用表名来限定列名（例如 `table.column`）。
不要更改查询中的任何字面量（literal values）。
您*只能*重写查询，使其格式对指定的 SQL 方言 `{sql_dialect}` 是正确的。
除了修正后的 SQL 查询之外，不要返回任何其他信息。

修正后的 SQL 查询：
"""
# {sql_dialect}: 将被替换为目标 SQL 方言的名称（例如 'bigquery'）。
# {sql_query}: 将被替换为需要修正的 SQL 查询字符串。
# {schema_insert}: 将被替换为数据库模式信息（如果提供），或者为空字符串。
# {errors}: 将被替换为检测到的 SQL 错误信息。


