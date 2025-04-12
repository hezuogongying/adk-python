
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
import json # 用于处理 JSON 数据
import sys # 用于系统相关操作，如此处的路径添加
from tqdm import tqdm # 用于显示进度条

# 将父目录添加到系统路径，以便导入 web_agent_site 模块
sys.path.insert(0, "../")

# 从 web_agent_site.engine 导入加载产品数据的函数
from web_agent_site.engine.engine import load_products

# 加载产品数据，filepath 指向原始产品数据文件
# _* 用于忽略 load_products 返回的其他值
all_products, *_ = load_products(filepath="../data/items_shuffle.json")

docs = [] # 初始化用于存储处理后文档的列表
# 使用 tqdm 显示处理进度
for p in tqdm(all_products, total=len(all_products)):
    option_texts = [] # 初始化选项文本列表
    # 获取产品的选项信息，默认为空字典
    options = p.get("options", {})
    # 遍历选项名称和内容
    for option_name, option_contents in options.items():
        # 将选项内容连接成字符串
        option_contents_text = ", ".join(option_contents)
        # 格式化选项文本
        option_texts.append(f"{option_name}: {option_contents_text}")
    # 将所有选项文本连接成一个字符串
    option_text = ", and ".join(option_texts)

    doc = dict() # 初始化文档字典
    doc["id"] = p["asin"] # 设置文档 ID 为产品 ASIN
    # 组合产品标题、描述、要点和选项文本作为文档内容，并转换为小写
    doc["contents"] = " ".join(
        [
            p.get("Title", ""), # 使用 get 避免 KeyError
            p.get("Description", ""),
            p.get("BulletPoints", [""])[0], # 取第一个要点，处理列表为空的情况
            option_text,
        ]
    ).lower()
    doc["product"] = p # 将原始产品信息也存入文档
    docs.append(doc) # 将处理后的文档添加到列表

# 将前 100 个文档写入 resources_100/documents.jsonl 文件
with open("./resources_100/documents.jsonl", "w+") as f:
    for doc in docs[:100]:
        f.write(json.dumps(doc) + "\n") # 每个文档写入一行 JSON

# 将前 1000 个文档写入 resources_1k/documents.jsonl 文件
with open("./resources_1k/documents.jsonl", "w+") as f:
    for doc in docs[:1000]:
        f.write(json.dumps(doc) + "\n")

# 将前 10000 个文档写入 resources_10k/documents.jsonl 文件
with open("./resources_10k/documents.jsonl", "w+") as f:
    for doc in docs[:10000]:
        f.write(json.dumps(doc) + "\n")

# 将前 50000 个文档写入 resources_50k/documents.jsonl 文件
with open("./resources_50k/documents.jsonl", "w+") as f:
    for doc in docs[:50000]:
        f.write(json.dumps(doc) + "\n")

```
*注意：上述脚本的目的是将原始的产品数据 (`items_shuffle.json`) 转换为适用于 Pyserini 搜索引擎的格式 (`documents.jsonl`)。它提取了产品的关键信息（标题、描述、要点、选项）作为搜索内容，并保留了原始产品信息。然后，它根据不同的产品数量（100, 1k, 10k, 50k）创建了多个版本的 `documents.jsonl` 文件。*

---

