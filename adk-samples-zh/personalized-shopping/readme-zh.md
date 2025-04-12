# 文件: personalized-shopping\README.md

# 个性化购物代理程序

此代理程序在一个简化的网店环境中模拟个性化购物体验。它协助用户根据文本查询或图像查找产品，探索产品详情（描述、功能、评论），并引导他们完成模拟的购买过程。

该代理程序与基于 [WebShop](https://github.com/princeton-nlp/WebShop) 项目的模拟网络环境 (`WebAgentTextEnv`) 进行交互。

## 功能

-   **产品搜索：** 使用模拟搜索引擎 (`pyserini`) 根据文本关键词查找产品。
-   **交互式导航：** 模拟在网店环境中点击按钮和链接（例如，选择产品、查看描述/功能/评论、导航页面）。
-   **产品探索：** 从不同的产品页面部分收集并总结信息。
-   **购买模拟：** 引导用户选择选项（如尺寸/颜色）并确认模拟购买。
-   **基于图像的搜索（概念性）：** 提示允许进行图像输入分析，尽管当前实现侧重于模拟环境中的基于文本的交互。

## 快速开始

请遵循[顶层 README.md](../../README.md) 中的说明来设置项目。

### 先决条件

-   **搜索索引：** 搜索工具依赖于预先构建的 Pyserini Lucene 索引。您需要下载并放置索引文件。
    -   从 [WebShop GitHub Releases](https://github.com/princeton-nlp/WebShop/releases/tag/v.1.0.1) 下载所需产品数量的索引（例如，1000 个产品的 `indexes_1k.tar.gz`）。
    -   解压下载的压缩文件（例如 `tar -xzf indexes_1k.tar.gz`）。
    -   将解压后的 `indexes_1k` 目录移动到此项目中的 `personalized-shopping/shared_libraries/search_engine/` 目录。*注意：路径 `personalized-shopping/shared_libraries/search_engine/indexes_1k` 必须存在。*
-   **产品数据：** 模拟环境需要产品数据文件。
    -   从 [WebShop GitHub Releases](https://github.com/princeton-nlp/WebShop/releases/tag/v.1.0.1) 下载 `items_shuffle.json.zip`。
    -   解压 zip 文件。
    -   将解压后的 `items_shuffle.json` 文件移动到 `personalized-shopping/data/` 目录。*注意：路径 `personalized-shopping/data/items_shuffle.json` 必须存在。*

### 依赖项

*   `google-adk`
*   `google-cloud-aiplatform`
*   `pydantic`
*   `requests`
*   `python-dotenv`
*   `google-genai`
*   `gymnasium` (注意: `gym` 常用，但 `gymnasium` 是维护的分支)
*   `beautifulsoup4`
*   `lxml` (BeautifulSoup 解析所需)
*   `pyserini` (需要安装 Java 11+)
*   `faiss-cpu` (如果支持 GPU，则为 `faiss-gpu`)
*   `torch`
*   `tqdm`
*   `thefuzz`
*   `spacy`
*   下载 `en_core_web_sm` spaCy 模型: `python -m spacy download en_core_web_sm`

*安装说明:* `pyserini` 需要 Java 11 或更高版本。确保已安装并在环境的 PATH 中可访问。

### 环境变量

确保在您的 `.env` 文件中设置了以下变量：

*   `GOOGLE_CLOUD_PROJECT`：您的 GCP 项目 ID。
*   `GOOGLE_CLOUD_LOCATION`：GCP 区域（例如 `us-central1`）。
*   `GOOGLE_CLOUD_STORAGE_BUCKET`：用于暂存部署工件的 GCS 存储桶。

### 部署代理程序

1.  构建代理程序包：
    ```bash
    poetry build --format=wheel --output=deployment
    ```
    *（部署脚本假定 wheel 文件名为 `personalized_shopping-0.1.0-py3-none-any.whl` 并且位于 `deployment` 目录中。如果需要，请调整脚本或文件名。）*
2.  确保已设置所需的环境变量。
3.  使用脚本部署代理程序：
    ```bash
    poetry run python -m deployment.deploy
    ```
    请记下返回的 `resource_id`。

### 运行评估

确保您的环境变量已设置。

```bash
poetry run pytest eval/test_eval.py
```

### 测试已部署的代理程序

*（未提供特定的 `test_deployment.py`，但 `deploy.py` 脚本在部署后包含一个基本的测试交互。）*

### 删除已部署的代理程序

*（未提供特定的删除脚本。通常您会使用 `gcloud` 或 Vertex AI SDK，通过其资源 ID 删除 ReasoningEngine 资源。）*

## 自定义

-   **提示：** 修改 `prompt.py` (`personalized_shopping_agent_instruction`) 以更改代理程序的交互流程、角色设定或处理搜索结果、产品探索或购买确认的具体说明。
-   **工具：**
    -   核心工具是 `search` (`tools/search.py`) 和 `click` (`tools/click.py`)，它们与模拟的 `WebAgentTextEnv` 交互。修改这些工具需要理解环境的 API (`step` 方法)。
    -   您可以添加新工具，例如与真实的外部 API 集成（例如，真实的产品搜索 API、支付网关），但这将取代部分模拟功能。
-   **网络环境：**
    -   环境模拟逻辑主要在 `shared_libraries/web_agent_site/` 中。修改 `engine/engine.py` 会改变搜索结果的生成方式或页面的渲染方式。
    -   更改产品数据 (`data/items_shuffle.json`) 或搜索索引 (`shared_libraries/search_engine/`) 会改变可用产品和搜索行为。如果产品数据发生重大变化，您需要重建搜索索引。请参阅 Pyserini 文档了解索引。
    -   目标生成逻辑在 `engine/goal.py` 中。您可以修改 `get_human_goals` 或 `get_synthetic_goals` 以更改代理程序在评估或模拟设置期间可能被赋予的购物任务类型。
-   **观察模式：** 可以使用不同的 `observation_mode` 值 (`html`, `text`, `text_rich`, `url`) 初始化 `WebAgentTextEnv`。这会影响代理程序接收到的观察格式。当前的代理程序提示是为 `text` 模式设计的。更改模式可能需要调整提示。
-   **产品数量：** 调整 `shared_libraries/init_env.py` 中的 `num_product_items` 变量，并确保您已下载相应的搜索索引，以更改模拟网店的规模。
```
