
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

"""FOMC 研究 Agent 的价格相关工具函数。"""

# 导入必要的库
import datetime
import logging
import math
import os
from collections.abc import Sequence # 用于类型提示

# 从 absl 库导入 app，用于可能的命令行应用
from absl import app
# 导入 Google Cloud BigQuery 客户端库
from google.cloud import bigquery

# 初始化 BigQuery 客户端
bqclient = bigquery.Client()
# 获取日志记录器
logger = logging.getLogger(__name__)

# 定义利率变动幅度（基点）
MOVE_SIZE_BP = 25
# 从环境变量获取 BigQuery 数据集名称，如果未设置则使用默认值
DATASET_NAME = os.getenv("GOOGLE_CLOUD_BQ_DATASET")
if not DATASET_NAME:
    DATASET_NAME = "fomc_research_agent" # 默认数据集名称
# 从环境变量获取时间序列代码，如果未设置则使用默认值
TIMESERIES_CODES = os.getenv("GOOGLE_GENAI_FOMC_AGENT_TIMESERIES_CODES")
if not TIMESERIES_CODES:
    TIMESERIES_CODES = "SFRH5,SFRZ5" # 默认时间序列代码


def fetch_prices_from_bq(
    timeseries_codes: list[str], dates: list[datetime.date]
) -> dict[str, dict[datetime.date, float]]: # 返回类型：字典嵌套字典 {代码: {日期: 价格}}
    """从 BigQuery 获取价格数据。

    参数:
      timeseries_codes: 要获取的时间序列代码列表。
      dates: 要获取的日期列表。

    返回:
      一个字典，键是时间序列代码，值是另一个字典，键是日期，值是价格。
    """

    logger.debug("fetch_prices_from_bq: 时间序列代码: %s", timeseries_codes)
    logger.debug("fetch_prices_from_bq: 日期: %s", dates)

    # 构建 BigQuery 查询语句
    query = f"""
SELECT DISTINCT timeseries_code, date, value
FROM `{DATASET_NAME}`.timeseries_data -- 使用反引号处理可能的特殊字符
WHERE timeseries_code IN UNNEST(@timeseries_codes)
  AND date IN UNNEST(@dates)
"""

    # 配置查询参数
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter(
                "timeseries_codes", "STRING", timeseries_codes # 时间序列代码数组参数
            ),
            bigquery.ArrayQueryParameter("dates", "DATE", dates), # 日期数组参数
        ]
    )

    prices = {} # 初始化价格字典
    # 执行查询
    query_job = bqclient.query(query, job_config=job_config)
    # 获取查询结果
    results = query_job.result()
    # 遍历结果行
    for row in results:
        logger.debug(
            "代码: %s, 日期: %s, 值: %s",
            row.timeseries_code,
            row.date,
            row.value,
        )
        # 将价格存入嵌套字典
        if row.timeseries_code not in prices:
            prices[row.timeseries_code] = {row.date: row.value}
        else:
            prices[row.timeseries_code][row.date] = row.value

    return prices


def number_of_moves(
    front_ff_future_px: float, back_ff_future_px: float
) -> float:
    """根据两个联邦基金期货价格计算预期的利率变动次数。

    参数:
      front_ff_future_px: 近期联邦基金期货价格。
      back_ff_future_px: 远期联邦基金期货价格。

    返回:
      预期的利率变动次数。

    计算细节请参考：
    https://www.biancoresearch.com/bianco/samples/SR2v1.pdf

    """

    # 计算每次变动的百分比
    move_size_pct = MOVE_SIZE_BP / 100
    # 计算隐含利率
    front_implied_rate = 100 - front_ff_future_px
    back_implied_rate = 100 - back_ff_future_px
    # 计算利率差
    rate_delta = back_implied_rate - front_implied_rate
    # 计算变动次数
    num_moves = rate_delta / move_size_pct
    return num_moves


def fed_meeting_probabilities(nmoves: float) -> dict:
    """根据预期的利率变动次数计算美联储会议加息/降息的概率。

    参数:
        nmoves: 预期的利率变动次数。

    返回:
        包含概率信息的字典。
    """
    # 判断是加息还是降息
    move_text = "加息 (hike)" if nmoves > 0 else "降息 (cut)"
    # 如果变动次数大于1，使用复数形式
    if abs(nmoves) > 1: # 使用 abs() 处理复数情况
        move_text = move_text + "s"

    # 计算最大预期变动次数（向上取整）和对应的基点
    max_expected_moves = math.ceil(abs(nmoves))
    max_expected_move_bp = max_expected_moves * MOVE_SIZE_BP
    # 计算最大预期变动发生的概率（取小数部分）
    move_odds = round(math.modf(abs(nmoves))[0], 2)

    # 构建输出字典
    output = {
        f"{max_expected_move_bp}bp {move_text} 的概率": move_odds,
        f"不 {move_text} 的概率": round(1 - move_odds, 2),
    }

    return output


def compute_probabilities(meeting_date_str: str) -> dict:
    """计算特定日期的利率变动概率。

    参数:
      meeting_date_str: 美联储会议日期字符串 (ISO 格式 YYYY-MM-DD)。

    返回:
      包含状态和概率信息的字典。
    """
    # 将日期字符串转换为日期对象
    meeting_date = datetime.date.fromisoformat(meeting_date_str)
    # 获取会议日期的前一天
    meeting_date_day_before = meeting_date - datetime.timedelta(days=1)
    # 解析时间序列代码列表
    timeseries_codes = [x.strip() for x in TIMESERIES_CODES.split(",")]

    # 从 BigQuery 获取所需日期的价格数据
    prices = fetch_prices_from_bq(
        timeseries_codes, [meeting_date, meeting_date_day_before]
    )

    # 检查是否获取到了所有需要的数据
    error = None
    for code in timeseries_codes:
        if code not in prices:
            error = f"缺少 {code} 的数据"
            break
        elif meeting_date not in prices[code]:
            error = f"缺少 {code} 在 {meeting_date} 的数据"
            break
        elif meeting_date_day_before not in prices[code]:
            error = f"缺少 {code} 在 {meeting_date_day_before} 的数据"
            break

    logger.debug("compute_probabilities: 获取到的价格: %s", prices)

    # 如果数据不完整，返回错误信息
    if error:
        return {"status": "错误 (ERROR)", "message": error}

    # 获取近期和远期的时间序列代码
    near_code = timeseries_codes[0]
    far_code = timeseries_codes[1]
    # 计算会议后和会议前的预期利率变动次数
    num_moves_post = number_of_moves(
        prices[near_code][meeting_date], prices[far_code][meeting_date]
    )
    num_moves_pre = number_of_moves(
        prices[near_code][meeting_date_day_before],
        prices[far_code][meeting_date_day_before],
    )

    # 计算会议前后的概率
    probs_pre = fed_meeting_probabilities(num_moves_pre)
    probs_post = fed_meeting_probabilities(num_moves_post)

    # 构建输出字典
    output = {
        (
            "未来一年内利率变动的概率 ",
            "(美联储会议前计算):",
        ): (probs_pre),
        (
            "未来一年内利率变动的概率 ",
            "(美联储会议后计算):",
        ): (probs_post),
    }

    # 返回成功状态和计算结果
    return {"status": "成功 (OK)", "output": output}


# 主函数，用于可能的命令行调用
def main(argv: Sequence[str]) -> None:
    """主执行函数。"""
    if len(argv) > 2:
        raise app.UsageError("命令行参数过多。")

    # 获取会议日期参数
    meeting_date = argv[1]
    print("会议日期 (meeting_date): ", meeting_date)

    # 计算并打印概率
    print(compute_probabilities(meeting_date))


if __name__ == "__main__":
    # 如果作为主脚本运行，则执行 app.run(main)
    app.run(main)


