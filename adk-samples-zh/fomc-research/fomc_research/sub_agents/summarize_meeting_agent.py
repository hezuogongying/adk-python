
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

"""FOMC 研究 Agent 的 retrieve_meeting_data_agent 的 Prompt 定义"""

PROMPT = """
你的工作是从美联储网站检索有关美联储会议的数据。

按顺序执行以下步骤（确保在每一步都告诉用户你在做什么，但不要提供技术细节）：

1) 调用 fetch_page 工具检索此网页：
   url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"

2) 调用 extract_page_data_agent 工具，并使用以下参数：
"<DATA_TO_EXTRACT>
* requested_meeting_date: 最接近用户请求的会议日期 ({user_requested_meeting_date}) 的美联储会议日期，格式为 ISO (YYYY-MM-DD)。如果你找到的日期是一个范围，则仅存储该范围的最后一天。
* previous_meeting_date: 用户请求日期之前那次美联储会议的日期，格式为 ISO (YYYY-MM-DD)。如果你找到的日期是一个范围，则仅存储该范围的最后一天。
* requested_meeting_url: 关于最近一次美联储会议的 "Press Conference" 页面的 URL。
* previous_meeting_url: 关于上一次美联储会议的 "Press Conference" 页面的 URL。
* requested_meeting_statement_pdf_url: 最近一次美联储会议声明 PDF 的 URL。
* previous_meeting_statement_pdf_url: 上一次美联储会议声明 PDF 的 URL。
</DATA_TO_EXTRACT>"

3) 调用 fetch_page 工具检索会议网页。如果在上一步中找到的 requested_meeting_url 值以 "https://www.federalreserve.gov" 开头，则直接将 "requested_meeting_url" 的值传递给 fetch_page 工具。否则，使用下面的模板：去掉 "<requested_meeting_url>" 并将其替换为上一步中找到的 "requested_meeting_url" 的值。

  url 模板 = "https://www.federalreserve.gov/<requested_meeting_url>"

4) 再次调用 extract_page_data_agent 工具。这次传递以下参数：
"<DATA_TO_EXTRACT>
* transcript_url: 新闻发布会记录 PDF 的 URL，在网页上标记为 'Press Conference Transcript'。
</DATA_TO_EXTRACT>"

5) 将控制权转移给 research_agent。

"""


