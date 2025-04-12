
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

"""FOMC 研究 Agent 中 extract_page_data_agent 的 Prompt 定义"""

PROMPT = """
你的工作是从网页中提取重要数据。

 <PAGE_CONTENTS>
 {page_contents}
 </PAGE_CONTENTS>

<INSTRUCTIONS>
网页内容已在上面的 'page_contents' 部分提供。
需要提取的数据字段在用户输入的 'data_to_extract' 部分提供。

阅读网页内容并提取所请求的数据片段。
不要使用任何其他 HTML 解析器，只需自己检查 HTML 并提取信息。

首先，使用 store_state 工具将提取的数据存储在 ToolContext 中。

其次，以 JSON 格式将你找到的信息返回给用户。
 </INSTRUCTIONS>

"""


