# 文件: fomc-research\README.md

# FOMC 研究代理程序

此代理程序充当虚拟研究助理，专门分析联邦公开市场委员会 (FOMC) 会议。它能检索会议数据、比较声明、获取会议纪要、计算市场概率，并生成分析报告。

## 功能

-   **会议数据检索：** 从美联储网站获取 FOMC 会议日程、声明 URL 和会议纪要 URL。
-   **声明比较：** 下载所请求会议及其前一次会议的 FOMC 声明 (PDF)，进行比较，并生成一个 HTML 红线文档，突出显示变更内容。
-   **会议纪要获取：** 下载新闻发布会会议纪要 PDF。
-   **会议总结：** 总结会议纪要的内容和基调。
-   **概率计算：** 从 BigQuery（在此示例中为模拟）获取相关时间序列数据，并计算会议前后市场隐含的利率变动概率。
-   **分析报告生成：** 将所有收集到的信息综合成一份简洁的分析报告。
-   **模块化设计：** 使用子代理程序执行特定任务（数据检索、研究协调、总结、分析）。

## 快速开始

请遵循[顶层 README.md](../../README.md) 中的说明来设置项目。

### 先决条件

-   **BigQuery 数据集（可选，但建议用于完整功能）：** `compute_rate_move_probability` 工具从 BigQuery 获取数据。
    -   如果您没有数据集，该工具将优雅地处理错误，但概率计算将无法工作。
    -   设置示例数据：
        1.  创建一个 BigQuery 数据集（例如 `fomc_research_agent`）。在您的 `.env` 文件中将 `GOOGLE_CLOUD_BQ_DATASET` 环境变量设置为此数据集 ID。
        2.  运行设置脚本，提供您的项目 ID 和数据集 ID：
            ```bash
            poetry run python -m deployment.bigquery_setup --project_id <your-gcp-project-id> --dataset_id <your-bq-dataset-id> --data_file ./fomc_research/data/sample_timeseries.csv
            ```
        3.  确保运行代理程序的服务账号在创建的表 (`<your-bq-dataset-id>.timeseries_data`) 上具有“BigQuery Data Viewer”和“BigQuery User”角色。

### 依赖项

*   `google-adk`
*   `google-cloud-aiplatform`
*   `pydantic`
*   `requests`
*   `python-dotenv`
*   `google-genai`
*   `google-cloud-bigquery`
*   `absl-py`
*   `pdfplumber`
*   `diff-match-patch`

### 环境变量

确保在您的 `.env` 文件中设置了以下变量：

*   `GOOGLE_CLOUD_PROJECT`：您的 GCP 项目 ID。
*   `GOOGLE_CLOUD_LOCATION`：GCP 区域（例如 `us-central1`）。
*   `GOOGLE_CLOUD_STORAGE_BUCKET`：用于暂存的 GCS 存储桶。
*   `GOOGLE_CLOUD_BQ_DATASET`：（可选）用于时间序列数据的 BigQuery 数据集 ID。
*   `GOOGLE_GENAI_FOMC_AGENT_TIMESERIES_CODES`：（可选）用于概率计算的逗号分隔的时间序列代码（默认为 `SFRH5,SFRZ5`）。

### 部署代理程序

1.  构建代理程序包：
    ```bash
    poetry build --format=wheel --output=deployment
    ```
2.  确保已设置所需的环境变量。
3.  使用脚本部署代理程序：
    ```bash
    poetry run python -m deployment.deploy --create
    ```
    请记下返回的 `resource_id`。

### 运行评估

确保您的环境变量已设置（包括可选的 BigQuery 详细信息，如果使用）。

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

-   **提示：** 修改 `root_agent_prompt.py` 和子代理程序提示文件（例如 `sub_agents/analysis_agent_prompt.py`）中的提示，以更改代理程序行为、说明或报告结构。
-   **工具：**
    -   修改 `tools/` 目录中的现有工具。
    -   添加新工具（例如，用于获取不同类型的经济数据）。请记得更新相关代理程序的工具列表。
-   **数据源：**
    -   如果美联储网站结构发生变化，请更改 `retrieve_meeting_data_agent_prompt.py` 中使用的 URL。
    -   修改 `shared_libraries/price_utils.py` 以从不同的 BigQuery 表或其他数据源获取数据用于概率计算。相应地更新 `GOOGLE_CLOUD_BQ_DATASET` 和 `GOOGLE_GENAI_FOMC_AGENT_TIMESERIES_CODES` 环境变量。
-   **分析逻辑：** 更新 `analysis_agent_prompt.py` 以更改最终分析报告的重点或深度。
-   **代理程序流程：** 修改 `root_agent_prompt.py` 或 `research_agent_prompt.py` 中的说明，以更改子代理程序和工具的顺序或选择。
```
