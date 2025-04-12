
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

# 导入必要的库
import bisect # 用于在排序列表中进行二分查找和插入
import hashlib # 用于生成哈希值
import logging # 用于日志记录
from os.path import abspath, dirname, join # 用于处理文件路径
import random # 用于生成随机数

# 获取当前文件所在目录的绝对路径
BASE_DIR = dirname(abspath(__file__))
# 调试时使用的产品数量限制（None 表示不限制）
DEBUG_PROD_SIZE = None

# 定义默认文件路径常量
DEFAULT_ATTR_PATH = join(BASE_DIR, "../data/items_ins_v2.json") # 默认属性文件路径 (似乎重复定义了)
DEFAULT_FILE_PATH = join(BASE_DIR, "../data/items_shuffle.json") # 默认产品数据文件路径
DEFAULT_REVIEW_PATH = join(BASE_DIR, "../data/reviews.json") # 默认评论文件路径
FEAT_CONV = join(BASE_DIR, "../data/feat_conv.pt") # 特征转换文件路径 (.pt 通常是 PyTorch 文件)
FEAT_IDS = join(BASE_DIR, "../data/feat_ids.pt") # 特征 ID 文件路径
HUMAN_ATTR_PATH = join(BASE_DIR, "../data/items_human_ins.json") # 人类标注属性文件路径


def random_idx(cum_weights):
    """根据累积权重随机生成索引。

    首先从总权重中均匀采样一个位置，然后使用 bisect 找到保持列表排序的位置，
    最后取该位置和倒数第二个索引值中的较小者。
    """
    # 在 [0, 总权重] 范围内生成一个随机浮点数
    pos = random.uniform(0, cum_weights[-1])
    # 使用二分查找找到 pos 在 cum_weights 中应插入的位置
    idx = bisect.bisect(cum_weights, pos)
    # 确保索引不超过列表的有效范围（最大为倒数第二个索引）
    idx = min(idx, len(cum_weights) - 2)
    return idx


def setup_logger(session_id, user_log_dir):
    """为给定的 session ID 创建日志文件和日志记录器对象。"""
    # 获取指定 session_id 的日志记录器
    logger = logging.getLogger(session_id)
    # 定义日志格式
    formatter = logging.Formatter("%(message)s") # 只记录消息本身
    # 创建文件处理器，将日志写入指定目录下的文件（覆盖模式 'w'）
    file_handler = logging.FileHandler(user_log_dir / f"{session_id}.jsonl", mode="w")
    # 设置文件处理器的格式化器
    file_handler.setFormatter(formatter)
    # 设置日志记录器的级别为 INFO
    logger.setLevel(logging.INFO)
    # 将文件处理器添加到日志记录器
    logger.addHandler(file_handler)
    return logger


def generate_mturk_code(session_id: str) -> str:
    """为完成会话的 MTurk 工作人员生成与 session ID 对应的兑换码。"""
    # 使用 SHA1 算法计算 session_id 的哈希值
    sha = hashlib.sha1(session_id.encode())
    # 取哈希值的前 10 个字符并转换为大写作为兑换码
    return sha.hexdigest()[:10].upper()


