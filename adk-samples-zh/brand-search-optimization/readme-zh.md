# 品牌搜索优化

品牌搜索优化代理程序旨在帮助用户优化其品牌在电子商务平台上的可见性。它能识别相关关键词，分析搜索结果，并为产品标题提出改进建议，以提升搜索排名。

该代理程序利用 BigQuery 进行产品数据分析，并使用 Selenium 进行网页搜索结果的抓取。

## 快速开始

请遵循[顶层 README.md](../../README.md) 中的说明来设置项目。

### 依赖项

*   `google-adk`
*   `google-cloud-aiplatform`
*   `pydantic`
*   `requests`
*   `python-dotenv`
*   `google-genai`
*   `selenium`
*   `webdriver-manager`
*   `google-cloud-bigquery`
*   `absl-py`
*   `pillow`

### 设置 BigQuery 数据

1.  确保您已在 `.env` 文件中设置了环境变量 `GOOGLE_CLOUD_PROJECT`、`DATASET_ID` 和 `TABLE_ID`（请参考 `.env.example`）。
2.  运行脚本以填充 BigQuery 表：
    ```bash
    poetry run python -m deployment.bq_populate_data
    ```
3.  在您创建的**表** (`<project>.<dataset>.<table>`) 上，为运行代理程序的服务账号授予“BigQuery Data Viewer”和“BigQuery User”角色。请遵循 [IAM 文档](https://cloud.google.com/bigquery/docs/control-access#grant_roles_on_a_resource)中的说明。

### 部署代理程序

1.  设置 `GOOGLE_CLOUD_PROJECT`、`GOOGLE_CLOUD_LOCATION` 和 `GOOGLE_CLOUD_STORAGE_BUCKET` 环境变量。
2.  构建代理程序包：
    ```bash
    poetry build --format=wheel
    ```
    将生成的 wheel 文件（例如 `brand_search_optimization-0.1-py3-none-any.whl`）移动到 `deployment` 目录。
3.  使用脚本部署代理程序：
    ```bash
    poetry run python -m deployment.deploy --create
    ```
    请记下返回的 `resource_id`。

### 运行评估

确保您的环境变量已设置（包括 BigQuery 详细信息）。

```bash
poetry run pytest eval/eval.py
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

有关自定义代理程序、提示、工具和 BigQuery 数据的详细信息，请参阅 `customization.md`。
```