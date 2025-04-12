# Agent开发套件(ADK)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

<html>
    <h1 align="center">
      <img src="assets/agent-development-kit.png" width="256"/>
    </h1>
    <h3 align="center">
      一个开源的、代码优先的Python工具包，用于灵活可控地构建、评估和部署复杂AI智能体
    </h3>
    <h3 align="center">
      重要链接:
      <a href="https://google.github.io/adk-docs/">文档</a> &
      <a href="https://github.com/google/adk-samples">示例</a>.
    </h3>
</html>

Agent开发套件(ADK)专为开发者设计，可在与Google Cloud服务紧密集成的同时，提供细粒度控制和灵活性来构建高级AI智能体。它允许您直接在代码中定义智能体行为、编排和工具使用，支持从本地到云端的强大调试、版本控制和部署能力。

---

## ✨ 主要特性

* **代码优先开发:** 通过代码定义智能体、工具和编排逻辑，实现最大控制力、可测试性和版本管理
* **多智能体架构:** 通过组合多个专业智能体构建模块化和可扩展的应用程序
* **丰富工具生态:** 为智能体配备多样化能力，可使用预构建工具、自定义Python函数、API规范或集成现有工具
* **灵活编排:** 使用内置智能体定义可预测的工作流，或利用LLM驱动的动态路由实现自适应行为
* **集成开发体验:** 通过CLI和可视化Web UI在本地开发、测试和调试
* **内置评估:** 通过评估响应质量和逐步执行轨迹来衡量智能体性能
* **部署就绪:** 将智能体容器化并部署到任何地方 - 可扩展到Vertex AI Agent Engine、Cloud Run或Docker
* **原生流式支持:** 通过原生双向流式传输(文本和音频)支持构建实时交互体验
* **状态、记忆与工件:** 管理短期会话上下文，配置长期记忆，处理文件上传/下载
* **可扩展性:** 通过回调深度自定义智能体行为，轻松集成第三方工具和服务

## 🚀 安装

使用`pip`安装ADK:

```bash
pip install google-adk
```

## 🏁 快速开始

创建您的第一个智能体(`my_agent/agent.py`):

```python
# my_agent/agent.py
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="search_assistant",
    model="gemini-2.0-flash-exp", # 或您偏好的Gemini模型
    instruction="您是一个乐于助人的助手。需要时使用Google搜索回答用户问题。",
    description="一个可以进行网络搜索的助手。",
    tools=[google_search]
)
```

创建`my_agent/__init__.py`:

```python
# my_agent/__init__.py
from . import agent
```

通过CLI运行(从*包含*`my_agent`的目录):

```bash
adk run my_agent
```

或从包含`my_agent`文件夹的目录启动Web UI:

```bash
adk web
```

完整的分步指南，请查看[快速开始](https://google.github.io/adk-docs/get-started/quickstart/)或[示例智能体](https://github.com/google/adk-samples)。

## 📚 资源

探索完整文档获取构建、评估和部署智能体的详细指南:

*   **[开始使用](https://google.github.io/adk-docs/get-started/)**
*   **[浏览示例智能体](https://github.com/google/adk-samples)**
*   **[评估智能体](https://google.github.io/adk-docs/evaluate/)**
*   **[部署智能体](https://google.github.io/adk-docs/deploy/)**
*   **[API参考](https://google.github.io/adk-docs/api-reference/)**

## 🤝 贡献

我们欢迎社区贡献！无论是错误报告、功能请求、文档改进还是代码贡献，请参阅我们的[**贡献指南**](./CONTRIBUTING.md)开始。

## 📄 许可证

本项目采用Apache 2.0许可证 - 详情请见[LICENSE](LICENSE)文件。

---

*祝您智能体开发愉快！*
