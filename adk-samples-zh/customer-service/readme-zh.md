# 文件: customer-service\README.md

# 客户服务代理程序

此代理程序旨在为家居和园艺零售商提供卓越的客户服务。它利用客户资料信息和各种工具，协助客户进行产品识别、推荐、订单管理、预约安排和一般支持。

## 功能

-   **个性化协助：** 向回头客打招呼，利用购买历史和购物车数据。
-   **产品处理：** 识别植物（包括通过视频），推荐相关产品（土壤、肥料），检查可用性。
-   **订单管理：** 访问和修改购物车，告知促销信息。
-   **追加销售：** 建议相关服务（例如，种植服务）。
-   **折扣：** 处理折扣请求，包括经理批准。
-   **安排：** 预订种植等服务的预约。
-   **支持：** 发送养护说明，生成折扣二维码。

## 快速开始

请遵循[顶层 README.md](../../README.md) 中的说明来设置项目。

### 依赖项

*   `google-adk`
*   `google-cloud-aiplatform`
*   `pydantic`
*   `requests`
*   `python-dotenv`
*   `google-genai`

### 部署代理程序

1.  确保您的 `.env` 文件已配置 `GOOGLE_CLOUD_PROJECT` 和 `GOOGLE_CLOUD_LOCATION`。
2.  构建代理程序包：
    ```bash
    poetry build --format=wheel
    ```
    将生成的 wheel 文件（例如 `customer_service-0.1.0-py3-none-any.whl`）移动到 `deployment` 目录。
3.  设置一个 GCS 存储桶用于暂存（例如 `gs://<your-project-id>-adk-customer-service-staging`）。确保该存储桶存在。
4.  使用脚本部署代理程序：
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

*（已部署代理程序的测试说明 - 如果适用。`deploy.py` 脚本包含一个基本测试。）*

### 删除已部署的代理程序

```bash
poetry run python -m deployment.deploy --delete --resource_id <your-resource-id>
```

## 自定义

-   **提示：** 修改 `prompts.py` 以更改代理程序的角色设定、核心能力或约束。更新 `GLOBAL_INSTRUCTION` 以更改客户资料的呈现方式。
-   **工具：** 在 `tools/tools.py` 中添加或修改工具。请记得更新 `agent.py` 中的工具列表，并可能需要更新 `prompts.py` 中的 `INSTRUCTION` 提示。
-   **客户数据：** 更新 `entities/customer.py` 文件，特别是 `get_customer` 静态方法，以从您的后端系统获取真实的客户数据，而不是使用虚拟数据。
-   **配置：** 在 `config.py` 中调整设置，例如模型名称。
-   **回调：** 修改 `shared_libraries/callbacks.py` 以在代理程序或工具执行之前/之后实现自定义逻辑（例如，自定义速率限制、工具前验证）。
```
