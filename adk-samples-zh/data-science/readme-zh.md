# 文件: data-science\README.md

# 数据科学代理程序

此代理程序扮演数据科学助手的角色，能够使用自然语言查询数据库（在此示例中特指 BigQuery），并利用 Python 代码执行（通过 Vertex AI 代码执行器）和 BigQuery ML 执行进一步的数据分析或机器学习任务。

## 功能

-   **自然语言转 SQL (NL2SQL)：** 理解用户关于存储在 BigQuery 中数据的问题，并使用 `database_agent` 将其转换为 SQL 查询。支持基线 (baseline) 和 CHASE-SQL 方法以提高准确性。
-   **自然语言转 Python (NL2Py)：** 对于超出 SQL 能力的更复杂分析，生成 Python 代码，并使用 `data_science_agent` 和 Vertex AI 代码执行器安全地执行它。
-   **BigQuery ML (BQML) 集成：** 可以通过 `bqml_agent` 利用 BQML 执行数据库内机器学习任务，如模型训练、评估和预测。使用 RAG（检索增强生成）获取相关的 BQML 文档。
-   **模块化设计：** 由一个根代理程序构建，该代理程序协调用于不同任务（数据库查询、数据科学分析、BQML）的子代理程序。
-   **数据库模式感知：** 读取 BigQuery 模式以指导 SQL 生成和分析。

## 快速开始

请遵循[顶层 README.md](../../README.md) 中的说明来设置项目。

### 先决条件

-   **BigQuery 数据集：** 您需要一个包含代理程序可访问的表的 BigQuery 数据集。
    -   此示例使用包含 `train.csv` 和 `test.csv` 的样本数据集 (`forecasting_sticker_sales`)。运行设置脚本：
        ```bash
        poetry run python -m data_science.utils.create_bq_table
        ```
    -   确保运行代理程序的服务账号在数据集/表上具有必要的 BigQuery 角色（例如，“BigQuery Data Viewer”、“BigQuery User”）。
-   **（可选）用于 BQML 的 RAG 语料库：** 如果使用 `bqml_agent`，您需要一个包含 BQML 文档的 Vertex AI RAG 语料库。
    -   运行设置脚本：
        ```bash
        poetry run python -m data_science.utils.reference_guide_RAG
        ```
    -   此脚本将创建语料库（如果不存在）并上传示例 BQML 文档 (`gs://cloud-samples-data/adk-samples/data-science/bqml`)。
    -   它还会使用 `BQML_RAG_CORPUS_NAME` 更新您的 `.env` 文件。确保服务账号具有管理 RAG 语料库的权限。
-   **代码解释器扩展：** `data_science_agent` 需要 Vertex AI 代码解释器扩展。在 Google Cloud Console 或通过 API 创建一个，并在您的 `.env` 文件中设置 `CODE_INTERPRETER_EXTENSION_NAME` 环境变量（例如 `projects/your-project/locations/your-location/extensions/your-extension-id`）。确保服务账号具有“Vertex AI Extensions User”角色。

### 依赖项

*   `google-adk`
*   `google-cloud-aiplatform`
*   `google-cloud-bigquery`
*   `google-auth`
*   `pydantic`
*   `requests`
*   `python-dotenv`
*   `google-genai`
*   `sqlglot`
*   `regex`
*   `immutabledict`
*   `pandas`
*   `absl-py`

### 环境变量

确保在您的 `.env` 文件中设置了以下变量：

*   `GOOGLE_CLOUD_PROJECT`：您的 GCP 项目 ID。
*   `GOOGLE_CLOUD_LOCATION`：GCP 区域（例如 `us-central1`）。
*   `GOOGLE_CLOUD_STORAGE_BUCKET`：用于暂存的 GCS 存储桶。
*   `BQ_PROJECT_ID`：包含 BigQuery 数据集的项目 ID。
*   `BQ_DATASET_ID`：BigQuery 数据集名称（例如 `forecasting_sticker_sales`）。
*   `NL2SQL_METHOD`：（可选）设置为 `CHASE` 以使用 CHASE-SQL，默认为 `BASELINE`。
*   `BQML_RAG_CORPUS_NAME`：（如果使用 BQML 则必需）您的 Vertex AI RAG 语料库的完整资源名称。
*   `CODE_INTERPRETER_EXTENSION_NAME`：（必需）您的 Vertex AI 代码解释器扩展的完整资源名称。

### 部署代理程序

1.  构建代理程序包：
    ```bash
    poetry build --format=wheel --output=deployment
    ```
2.  确保已设置所需的环境变量（见上文）。
3.  使用脚本部署代理程序：
    ```bash
    poetry run python -m deployment.deploy --create
    ```
    请记下返回的 `resource_id`。

### 运行评估

确保您的环境变量已设置（包括 BigQuery、RAG 和代码解释器详细信息）。

```bash
poetry run pytest eval/test_eval.py
```

### 测试已部署的代理程序

```bash
poetry run python -m deployment.test_deployment --resource_id <your-resource-id> --user_id test-user
```

### 删除已部署的代理程序

```bash
poetry run python -m deployment.deploy --delete --resource_id <your-resource-id>
```

## 自定义

-   **数据库：**
    -   要使用不同的 BigQuery 数据集，请更新 `BQ_PROJECT_ID` 和 `BQ_DATASET_ID` 环境变量，如果需要加载新数据，可能还需要更新 `create_bq_table.py` 脚本。
    -   要支持其他数据库（例如 PostgreSQL），您需要：
        -   创建一个新的数据库代理程序，类似于 `sub_agents/bigquery/agent.py`，为该数据库提供适当的工具和提示。
        -   更新 `root_agent` (`agent.py`)，以根据配置或用户输入有条件地使用新的数据库代理程序。
        -   实现相应的数据库连接和查询执行工具。
-   **NL2SQL 方法：** 在 `BASELINE` 和 `CHASE` 之间更改 `NL2SQL_METHOD` 环境变量以切换 NL2SQL 方法。
-   **提示：** 修改 `prompts.py` 和子代理程序提示文件（例如 `sub_agents/bigquery/prompts.py`）中的提示，以调整代理程序行为和 SQL/Python 生成风格。
-   **工具：** 在 `tools.py` 和子代理程序工具文件中添加或修改工具。更新代理程序配置以包含新工具。
-   **BQML：** 修改 `sub_agents/bqml/` 中与 BQML 相关的提示和工具。如果使用不同的文档，请更新 RAG 语料库设置脚本 (`utils/reference_guide_RAG.py`)。
-   **代码执行：** `data_science_agent` 使用 Vertex AI 代码执行器。如果需要，您可以将其替换为其他代码执行环境，但这需要对代理程序和工具定义进行重大更改。
```
