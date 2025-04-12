# 文件: RAG\README.md

# RAG 代理程序

此代理程序演示了如何使用 Vertex AI RAG 检索工具 (`VertexAiRagRetrieval`) 构建一个简单的问答系统，该系统基于特定的文档语料库进行回答。

## 功能

-   **RAG 集成：** 利用 `VertexAiRagRetrieval` 工具，根据用户查询从配置的 Vertex AI RAG 语料库中获取相关的文档块。
-   **基于依据的回答：** 使用检索到的文档块来构建用户问题的答案。
-   **引用：** 在最终答案中包含引用，指回从 RAG 语料库检索到的源文档。
-   **对话处理：** 包含基本逻辑以区分需要 RAG 的信息性问题和随意的对话。

## 快速开始

请遵循[顶层 README.md](../../README.md) 中的说明来设置项目。

### 先决条件

-   **Vertex AI RAG 语料库：** 您需要一个现有的 Vertex AI RAG 语料库，其中包含您希望代理程序查询的文档。
    -   **设置脚本：** 提供了一个辅助脚本来创建示例 RAG 语料库并上传 Alphabet 的 2024 年 10-K 报告（从 `https://abc.xyz/assets/77/51/9841ad5c4fbe85b4440c47a4df8d/goog-10-k-2024.pdf` 下载）。
    -   运行脚本：
        ```bash
        poetry run python -m rag.shared_libraries.prepare_corpus_and_data
        ```
    -   此脚本将：
        -   创建一个名为 `Alphabet_10K_2024_corpus` 的 RAG 语料库（如果不存在）。
        -   下载 PDF。
        -   将 PDF 上传到语料库。
        -   使用指向已创建/找到的语料库的完整资源名称的 `RAG_CORPUS` 变量更新您的 `.env` 文件（例如 `projects/<your-project>/locations/us-central1/ragCorpora/<corpus-id>`）。
    -   **权限：** 确保运行设置脚本和代理程序的服务账号或用户具有必要的权限：
        -   `aiplatform.ragCorpora.create`
        -   `aiplatform.ragCorpora.get`
        -   `aiplatform.ragFiles.upload`
        -   `aiplatform.ragFiles.list`
        -   `aiplatform.endpoints.predict` （用于嵌入和检索）
        -   Vertex AI User 角色通常足以执行基本操作。

### 依赖项

*   `google-adk`
*   `google-cloud-aiplatform[rag]` （包含必要的 RAG 组件）
*   `pydantic`
*   `requests`
*   `python-dotenv`
*   `google-genai`
*   `google-auth`
*   `tqdm`

### 环境变量

确保在您的 `.env` 文件中设置了以下变量：

*   `GOOGLE_CLOUD_PROJECT`：您的 GCP 项目 ID。
*   `GOOGLE_CLOUD_LOCATION`：您的 RAG 语料库所在的 GCP 区域（例如 `us-central1`）。
*   `STAGING_BUCKET`：用于暂存部署工件的 GCS 存储桶 URI（例如 `gs://your-staging-bucket`）。
*   `RAG_CORPUS`：您的 Vertex AI RAG 语料库的完整资源名称（由设置脚本自动设置，例如 `projects/<your-project>/locations/us-central1/ragCorpora/<corpus-id>`）。
*   `AGENT_ENGINE_ID`：（可选，由部署脚本设置）已部署代理程序引擎的资源名称。

### 部署代理程序

1.  确保满足先决条件（RAG 语料库）并设置了环境变量。
2.  构建代理程序包：
    ```bash
    poetry build --format=wheel --output=deployment
    ```
3.  使用脚本部署代理程序：
    ```bash
    poetry run python -m deployment.deploy
    ```
    此脚本将部署代理程序并更新您 `.env` 文件中的 `AGENT_ENGINE_ID`。请记下返回的资源 ID。

### 运行评估

确保您的环境变量已设置（包括 `RAG_CORPUS`）。

```bash
poetry run pytest eval/test_eval.py
```

### 测试已部署的代理程序

部署后，您可以使用 `run.py` 脚本测试代理程序：

```bash
poetry run python -m deployment.run
```
此脚本从 `.env` 文件读取 `AGENT_ENGINE_ID` 并运行预定义的对话流程。

### 删除已部署的代理程序

*（未提供特定的删除脚本。通常您会使用 `gcloud` 或 Vertex AI SDK，通过存储在 `AGENT_ENGINE_ID` 中的资源 ID 删除 ReasoningEngine 资源。）*

## 自定义

-   **语料库：**
    -   要使用您自己的文档，请修改 `rag.shared_libraries.prepare_corpus_and_data.py` 脚本：
        -   更改 `CORPUS_DISPLAY_NAME` 和 `CORPUS_DESCRIPTION`。
        -   更新 `PDF_URL` 和 `PDF_FILENAME` 以指向您的文档。您可以对其进行调整以处理多个文件或不同的来源（例如 `rag.import_files` 直接支持的 GCS 存储桶）。
    -   如果您手动创建了语料库或想使用不同的语料库，请更新 `rag/agent.py` 中 `VertexAiRagRetrieval` 工具定义内的 `rag_corpus` 参数。
-   **检索参数：** 调整 `VertexAiRagRetrieval` 工具定义（`rag/agent.py`）中的 `similarity_top_k` 和 `vector_distance_threshold`，以微调检索多少以及多相关的块。
-   **提示：** 修改 `rag/prompts.py` (`return_instructions_root`) 以更改代理程序与用户的交互方式、决定何时使用 RAG 工具的方式，或格式化最终答案和引用的方式。
-   **代理程序逻辑：** 对于更复杂的逻辑（例如，多轮检索、以不同方式总结多个块），您可能需要修改 `rag/agent.py` 中的 `root_agent` 或引入子代理程序。
-   **模型：** 更改 `Agent` 定义（`rag/agent.py`）中的 `model` 参数以使用不同的 Gemini 模型。
```
