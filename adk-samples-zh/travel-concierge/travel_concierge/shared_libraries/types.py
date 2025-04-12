
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

"""用作 ADK 会话状态键的常量。"""

# 系统时间键
SYSTEM_TIME = "_time"
# 标记行程是否已初始化的键
ITIN_INITIALIZED = "_itin_initialized"

# 行程数据键
ITIN_KEY = "itinerary"
# 用户个人资料数据键
PROF_KEY = "user_profile"

# 从行程推断出的开始日期键
ITIN_START_DATE = "itinerary_start_date"
# 从行程推断出的结束日期键
ITIN_END_DATE = "itinerary_end_date"
# 当前（模拟）行程日期时间键
ITIN_DATETIME = "itinerary_datetime"

# 行程规划中使用的开始日期键
START_DATE = "start_date"
# 行程规划中使用的结束日期键
END_DATE = "end_date"


