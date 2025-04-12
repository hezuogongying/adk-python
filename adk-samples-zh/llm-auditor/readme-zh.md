# 文件: llm-auditor\README.md

# LLM 审核器代理程序

此代理程序旨在评估和优化大型语言模型 (LLM) 生成的答案。它充当事实核查员，使用网络搜索来验证 LLM 回答中提出的声明，然后修正回答以确保准确性并与现实世界的知识保持一致。

## 功能

-   **声明识别：** 将 LLM 生成的答案分解为独立的 factual 或 logical 声明。
-   **网络验证：** 使用 Google 搜索（`google_search` 工具）查找支持或反驳每个声明的证据。
-   **裁决分配：** 根据验证结果为每个声明分配一个裁决（准确、不准确、有争议、无支持、不适用）。
-   **理由说明：** 为每个裁决提供推理，并在适用时引用搜索结果。
-   **回答修正：** 如果发现不准确、有争议或无支持的声明，它会以最小的幅度修正原始答案以纠正问题，同时保持原始风格和结构。
-   **顺序工作流：** 使用由 `critic_agent`（用于验证）和 `reviser_agent`（用于修正）组成的 `SequentialAgent`。

## 快速开始

请遵循[顶层 README.md](../../README.md) 中的说明来设置项目。

### 依赖项

*   `google-adk`
*   `google-cloud-aiplatform`
*   `pydantic`
*   `requests`
*   `python-dotenv`
*   `google-genai`
*   `absl-py`

### 环境变量

确保在您的 `.env` 文件中设置了以下变量：

*   `GOOGLE_CLOUD_PROJECT`：您的 GCP 项目 ID。
*   `GOOGLE_CLOUD_LOCATION`：GCP 区域（例如 `us-central1`）。
*   `GOOGLE_CLOUD_STORAGE_BUCKET`：用于暂存部署工件的 GCS 存储桶。
*   `GOOGLE_SEARCH_API_KEY`：您的 Google Custom Search JSON API 的 API 密钥。
*   `GOOGLE_SEARCH_ENGINE_ID`：您的 Programmable Search Engine ID。
*   *（有关获取这些密钥的详细信息，请参阅 [google_search_tool 文档](https://github.com/google/generative-ai-docs/blob/main/site/en/adk/docs/reference/tools/google_search_tool.md)。）*

### 部署代理程序

1.  构建代理程序包：
    ```bash
    poetry build --format=wheel
    ```
    将生成的 wheel 文件（例如 `llm_auditor-0.1-py3-none-any.whl`）移动到 `deployment` 目录。
2.  确保已设置所需的环境变量（包括搜索 API 密钥）。
3.  使用脚本部署代理程序：
    ```bash
    poetry run python -m deployment.deploy --create
    ```
    请记下返回的 `resource_id`。

### 运行评估

确保您的环境变量已设置（包括搜索 API 密钥）。

```bash
poetry run pytest eval/test_eval.py
```

### 测试已部署的代理程序

*（未提供特定的 `test_deployment.py`，但您可以使用资源 ID 通过 Vertex AI SDK 或 API 与已部署的代理程序进行交互。）*

### 列出已部署的代理程序

```bash
poetry run python -m deployment.deploy --list
```

### 删除已部署的代理程序

```bash
poetry run python -m deployment.deploy --delete --resource_id <your-resource-id>
```

## 自定义

-   **提示：**
    -   修改 `sub_agents/critic/prompt.py` (CRITIC_PROMPT) 以更改识别、验证声明的方式或执行整体评估的方式。您可以调整“提示”或“输出格式”。
    -   修改 `sub_agents/reviser/prompt.py` (REVISER_PROMPT) 以更改编辑指南、在修订期间如何处理不同的裁决，或修订后输出所需的风格/语调。
-   **工具：** 核心验证依赖于 `google_search`。如果需要，您可以向 `critic_agent` 添加其他验证工具（例如，数据库查找、知识图谱查询）。请记得更新代理程序的工具列表和可能的提示。
-   **代理程序逻辑：**
    -   当前工作流是严格的顺序（Critic -> Reviser）。如果您需要更复杂的工作流（例如，多轮修订、向用户请求澄清），您可以更改 `agent.py` 以使用不同的代理程序类型（例如，具有自定义路由逻辑的 `Agent`）。
    -   `sub_agents/critic/agent.py` 中的 `_render_reference` 回调会添加搜索结果引用。您可以修改此项以更改引用格式或内容。
    -   `sub_agents/reviser/agent.py` 中的 `_remove_end_of_edit_mark` 回调会清理内部使用的标记。
-   **模型：** 更改 `Agent` 定义 (`critic_agent`, `reviser_agent`) 中的 `model` 参数以使用不同的 Gemini 模型。
```
