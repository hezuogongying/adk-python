# 文件: travel-concierge\README.md

# 旅行管家代理程序

此代理程序充当全面的旅行助手，引导用户完成整个旅行过程：获取灵感、规划、预订、行前准备、行程中协助以及行程后跟进。

## 功能

-   **多阶段支持：** 使用专门的子代理程序处理不同的旅行阶段：
    -   `inspiration_agent`：建议目的地和活动。
    -   `planning_agent`：查找航班和酒店，制定行程。
    -   `booking_agent`：处理模拟的预订和支付确认。
    -   `pre_trip_agent`：提供行前信息（签证、天气、打包清单）。
    -   `in_trip_agent`：在旅行期间提供实时协助（监控、后勤）。
    -   `post_trip_agent`：收集反馈并更新用户偏好。
-   **行程管理：** 创建、存储和利用结构化的旅行行程。
-   **工具集成：** 使用工具执行以下操作：
    -   查找地点和兴趣点（模拟，使用 Google Places API 进行地理编码）。
    -   搜索航班和酒店（模拟）。
    -   选择座位和房间（模拟）。
    -   检查航班状态和活动预订（模拟）。
    -   评估天气影响（模拟）。
    -   通过 Google 搜索获取依据信息。
    -   存储信息（`memorize` 工具）。
    -   对地址进行地理编码（`map_tool` 使用 Google Places API）。
-   **状态管理：** 在整个对话过程中维护用户资料和行程状态。
-   **情境感知：** 使用当前时间和行程日期来确定旅行阶段并适当地委派任务。

## 快速开始

请遵循[顶层 README.md](../../README.md) 中的说明来设置项目。

### 先决条件

-   **Google Places API 密钥：** 此代理程序使用 Google Places API（通过 `map_tool`）对兴趣点的地址进行地理编码。
    -   从 [Google Cloud Console](https://console.cloud.google.com/google/maps-apis/overview) 获取 API 密钥。确保您的项目已启用“Places API”。
    -   在您的 `.env` 文件中设置 `GOOGLE_PLACES_API_KEY` 环境变量。

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
*   `GOOGLE_PLACES_API_KEY`：您的 Google Places API 的 API 密钥。
*   `TRAVEL_CONCIERGE_SCENARIO`：（可选）定义初始会话状态（用户资料、行程）的 JSON 文件的路径。默认为 `eval/itinerary_empty_default.json`。由 `deploy.py` 和 `eval/test_eval.py` 使用。

### 部署代理程序

1.  构建代理程序包：
    ```bash
    poetry build --format=wheel --output=deployment
    ```
    *（部署脚本假定 wheel 文件名为 `travel_concierge-0.1.0-py3-none-any.whl` 并且位于根目录中。如果需要，请进行调整。）*
2.  确保已设置所需的环境变量（包括 Places API 密钥）。如果您想使用特定的起始状态（如西雅图示例）进行部署，请设置 `TRAVEL_CONCIERGE_SCENARIO`。
3.  使用脚本部署代理程序：
    ```bash
    poetry run python -m deployment.deploy --create
    ```
    请记下返回的 `resource_id`。

### 运行评估

确保您的环境变量已设置（包括 `GOOGLE_PLACES_API_KEY`）。评估脚本会针对不同的旅行阶段运行测试，使用不同的初始状态文件（`itinerary_empty_default.json` 和 `itinerary_seattle_example.json`）。

```bash
poetry run pytest eval/test_eval.py
```

### 测试已部署的代理程序

您可以使用 `--quicktest` 标志快速测试已部署的代理程序（单轮交互）：

```bash
poetry run python -m deployment.deploy --quicktest --resource_id <your-resource-id>
```

*（对于更广泛的测试，您通常会使用 Vertex AI SDK 或 API，通过其资源 ID 与已部署的代理程序进行交互。）*

### 删除已部署的代理程序

```bash
poetry run python -m deployment.deploy --delete --resource_id <your-resource-id>
```

## 自定义

-   **提示：** 修改 `prompt.py`（根代理程序）和子代理程序提示文件（例如 `sub_agents/planning/prompt.py`、`sub_agents/in_trip/prompt.py`）中的提示，以更改代理程序行为、特定阶段的说明或交互风格。
-   **工具：**
    -   许多工具目前模拟交互（航班、酒店、预订）。在 `sub_agents/*/agent.py` 中替换这些模拟工具，并在 `tools/` 或 `sub_agents/*/tools.py` 中实现真实的 API 调用，以连接到实际的旅行服务。
    -   如果您需要不同的地点信息或想使用不同的地图服务，请修改 `map_tool` (`tools/places.py`)。
    -   如果您需要不同类型的行前信息，请调整 `google_search_grounding` 工具 (`tools/search.py`) 或其在 `pre_trip_agent` 中的用法。
-   **代理程序逻辑与流程：**
    -   更改 `prompt.py` (ROOT_AGENT_INSTR) 中的委派逻辑，以改变代理程序在旅行阶段之间转换的时间点。
    -   修改每个子代理程序提示中的内部工作流程（例如，`sub_agents/booking/prompt.py` 中的预订流程）。
    -   在 `agent.py` 中添加或删除子代理程序以更改整体功能。
-   **状态与行程：**
    -   修改 `shared_libraries/types.py` 中的数据结构，以更改存储在行程或用户资料中的信息。相应地更新提示和工具。
    -   更改初始状态文件 (`eval/*.json`) 或 `tools/memory.py` (`_load_precreated_itinerary`) 中的逻辑，以使用不同的默认数据启动会话。
-   **模型：** 更改 `Agent` 定义中的 `model` 参数，以为根代理程序或特定的子代理程序使用不同的 Gemini 模型。
-   **MCP 集成：** 请参阅 `tests/mcp_abnb.py`，了解如何集成来自外部 MCP（多代理通信协议）服务器的工具，例如用于 Airbnb 搜索的工具。
```