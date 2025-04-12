# 项目文件概述 (README-zh.md)

本文档概述了项目中包含的各个 Python 脚本和相关文件的功能及技术特点。

## brand-search-optimization (品牌搜索优化代理)

| 文件路径                                                                     | 功能简述                                       | 技术特点                         |
| :--------------------------------------------------------------------------- | :--------------------------------------------- | :------------------------------- |
| `brand-search-optimization\brand_search_optimization\agent.py`               | 定义品牌搜索优化主代理（根代理），编排子代理       | ADK Agent, 编排, 导入子代理        |
| `brand-search-optimization\brand_search_optimization\prompt.py`              | 定义根代理的核心指令提示                         | Python 字符串, 代理指令定义        |
| `brand-search-optimization\brand_search_optimization\shared_libraries\constants.py` | 定义共享常量（模型、项目ID、位置等）                 | Python, dotenv, 配置管理         |
| `brand-search-optimization\brand_search_optimization\sub_agents\comparison\agent.py` | 定义比较子代理（包括生成器和批评家）                 | ADK Agent, 子代理, 分层结构      |
| `brand-search-optimization\brand_search_optimization\sub_agents\comparison\prompt.py` | 定义比较子代理及其组件的指令提示                   | Python 字符串, 子代理指令        |
| `brand-search-optimization\brand_search_optimization\sub_agents\keyword_finding\agent.py` | 定义关键词发现子代理，使用 BigQuery 工具           | ADK Agent, 子代理, 工具集成 (BQ) |
| `brand-search-optimization\brand_search_optimization\sub_agents\keyword_finding\prompt.py` | 定义关键词发现子代理的指令提示                   | Python 字符串, 子代理指令        |
| `brand-search-optimization\brand_search_optimization\sub_agents\search_results\agent.py` | 定义搜索结果子代理，使用 Selenium 进行网页浏览和交互 | ADK Agent, 子代理, Selenium, Web |
| `brand-search-optimization\brand_search_optimization\sub_agents\search_results\prompt.py` | 定义搜索结果子代理的指令提示                   | Python 字符串, 子代理指令        |
| `brand-search-optimization\brand_search_optimization\tools\bq_connector.py`  | 定义连接 BigQuery 并获取产品详情的工具             | ADK Tool, BigQuery API         |
| `brand-search-optimization\deployment\bq_populate_data.py`                 | 用于向 BigQuery 填充示例产品数据的脚本             | Python, BigQuery API, 数据填充   |
| `brand-search-optimization\deployment\deploy.py`                           | 用于在 Vertex AI Agent Engines 上部署/删除代理的脚本 | Python, Vertex AI SDK, 部署脚本  |
| `brand-search-optimization\eval\eval.py`                                     | 使用 AgentEvaluator 评估代理性能的脚本           | ADK Evaluation, pytest, 评估脚本 |
| `brand-search-optimization\eval\data\eval_data1.evalset.json`              | 包含用于评估代理的具体场景测试数据                 | JSON, ADK EvalSet, 测试数据      |
| `brand-search-optimization\eval\data\test_config.json`                     | 定义评估标准的配置文件（如分数阈值）                 | JSON, ADK Eval Config, 评估配置  |
| `brand-search-optimization\tests\unit\test_tools.py`                       | 针对代理工具（如 BQ 连接器）的单元测试             | Python, unittest, pytest, 单元测试 |

## customer-service (客户服务代理)

| 文件路径                                                     | 功能简述                                         | 技术特点                               |
| :----------------------------------------------------------- | :----------------------------------------------- | :------------------------------------- |
| `customer-service\customer_service\agent.py`                 | 定义客户服务主代理及其使用的工具和回调函数                 | ADK Agent, 工具集成, 回调函数            |
| `customer-service\customer_service\config.py`                | 定义代理的配置设置（模型、项目ID、API密钥等）          | Pydantic, 配置管理, dotenv             |
| `customer-service\customer_service\prompts.py`               | 定义客户服务代理的全局指令和核心指令提示                   | Python 字符串, 代理指令定义            |
| `customer-service\customer_service\entities\customer.py`     | 定义客户数据结构（地址、购买历史、偏好等）                 | Pydantic, 数据模型定义                   |
| `customer-service\customer_service\shared_libraries\callbacks.py` | 定义代理生命周期中的回调函数（如速率限制、工具调用前处理） | ADK Callbacks, 状态管理, 速率限制      |
| `customer-service\customer_service\tools\tools.py`           | 定义客户服务代理使用的各种工具函数（如发送链接、更新 CRM 等） | ADK Tools (函数), 模拟 API 调用        |
| `customer-service\deployment\deploy.py`                      | 用于在 Vertex AI Agent Engines 上部署/删除代理的脚本       | Python, Vertex AI SDK, 部署脚本, argparse |
| `customer-service\eval\test_eval.py`                         | 使用 AgentEvaluator 评估代理性能的脚本               | ADK Evaluation, pytest, 评估脚本       |
| `customer-service\eval\eval_data\full_conversation.test.json` | 包含用于评估代理的完整对话场景测试数据                   | JSON, ADK EvalSet, 测试数据            |
| `customer-service\eval\eval_data\simple.test.json`           | 包含用于评估代理的简单交互场景测试数据                   | JSON, ADK EvalSet, 测试数据            |
| `customer-service\eval\eval_data\test_config.json`           | 定义评估标准的配置文件                               | JSON, ADK Eval Config, 评估配置        |
| `customer-service\eval\sessions\123.session.json`          | 一个示例会话日志文件，记录了用户与代理的交互             | JSON, 会话日志                         |
| `customer-service\tests\unit\test_config.py`                 | 针对配置加载的单元测试                               | Python, pytest, 单元测试               |
| `customer-service\tests\unit\test_tools.py`                  | 针对客户服务工具函数的单元测试                         | Python, unittest, pytest, 单元测试     |

## data-science (数据科学代理)

| 文件路径                                                                 | 功能简述                                                           | 技术特点                                       |
| :----------------------------------------------------------------------- | :----------------------------------------------------------------- | :--------------------------------------------- |
| `data-science\data_science\agent.py`                                     | 定义数据科学多代理系统的主（根）代理，协调数据库和数据科学子代理               | ADK Agent, 多代理编排, 回调函数, 状态管理      |
| `data-science\data_science\prompts.py`                                   | 定义根代理的指令提示，指导意图分类和任务分发                             | Python 字符串, 代理指令定义                    |
| `data-science\data_science\tools.py`                                     | 定义调用数据库代理 (NL2SQL) 和数据科学代理 (NL2Py) 的工具函数          | ADK AgentTool, 异步函数 (async)                |
| `data-science\data_science\sub_agents\analytics\agent.py`                | 定义数据科学子代理 (NL2Py)，使用代码执行器运行 Python 代码进行分析        | ADK Agent, 代码执行器 (Vertex AI), NL2Py       |
| `data-science\data_science\sub_agents\analytics\prompts.py`              | 定义数据科学子代理的指令提示，强调代码生成和执行的规范                     | Python 字符串, 子代理指令                      |
| `data-science\data_science\sub_agents\bigquery\agent.py`                 | 定义数据库子代理 (NL2SQL)，用于从 BigQuery 获取数据                     | ADK Agent, NL2SQL, 工具集成 (BQ), ChaseSQL (可选) |
| `data-science\data_science\sub_agents\bigquery\prompts.py`               | 定义数据库子代理的指令提示，指导 SQL 生成和验证流程                     | Python 字符串, 子代理指令                      |
| `data-science\data_science\sub_agents\bigquery\tools.py`                 | 定义数据库子代理使用的工具（如获取 BQ 模式、生成 SQL、验证 SQL）           | ADK Tools (函数), BigQuery API, NL2SQL         |
| `data-science\data_science\sub_agents\bigquery\chase_sql\chase_constants.py` | 定义 ChaseSQL 算法使用的常量                                         | Python, 配置, ChaseSQL                       |
| `data-science\data_science\sub_agents\bigquery\chase_sql\chase_db_tools.py` | 实现 ChaseSQL 算法的核心工具函数，用于高级 NL2SQL                      | Python, ChaseSQL, LLM 调用 (Gemini), SQLGlot |
| `data-science\data_science\sub_agents\bigquery\chase_sql\dc_prompt_template.py` | 定义 ChaseSQL 分治法 (Divide-and-Conquer) 的提示模板                | Python 字符串, 提示工程, ChaseSQL              |
| `data-science\data_science\sub_agents\bigquery\chase_sql\llm_utils.py`   | 封装调用 Gemini 模型的工具类，包含重试逻辑                             | Python, Vertex AI SDK, LLM 调用, 重试机制        |
| `data-science\data_science\sub_agents\bigquery\chase_sql\qp_prompt_template.py` | 定义 ChaseSQL 查询计划 (Query Plan) 的提示模板                      | Python 字符串, 提示工程, ChaseSQL              |
| `data-science\data_science\sub_agents\bigquery\chase_sql\sql_postprocessor\correction_prompt_template.py` | 定义用于修正 SQL 翻译错误的提示模板                                  | Python 字符串, 提示工程, SQLGlot             |
| `data-science\data_science\sub_agents\bigquery\chase_sql\sql_postprocessor\sql_translator.py` | 实现 SQL 方言转换器（如 SQLite 到 BigQuery），使用 SQLGlot 和 LLM 进行修正 | Python, SQLGlot, LLM 调用, SQL 方言转换        |
| `data-science\data_science\sub_agents\bqml\agent.py`                     | 定义 BigQuery ML 子代理，处理 BQML 相关任务                         | ADK Agent, BQML, 工具集成, RAG               |
| `data-science\data_science\sub_agents\bqml\prompts.py`                   | 定义 BigQuery ML 子代理的指令提示                                   | Python 字符串, 子代理指令                      |
| `data-science\data_science\sub_agents\bqml\tools.py`                     | 定义 BQML 子代理使用的工具（如检查模型、执行 BQML 代码、RAG 检索）     | ADK Tools (函数), BigQuery API, Vertex AI RAG  |
| `data-science\data_science\utils\create_bq_table.py`                     | 用于创建 BigQuery 数据集和表，并从 CSV 加载数据的脚本                   | Python, BigQuery API, 数据准备                 |
| `data-science\data_science\utils\reference_guide_RAG.py`                 | 用于创建和管理 Vertex AI RAG 语料库的脚本，用于 BQML 参考指南         | Python, Vertex AI RAG API, RAG 语料库管理    |
| `data-science\data_science\utils\utils.py`                               | 提供通用工具函数（如获取环境变量、读取图片、提取 JSON）                   | Python, 实用工具函数                         |
| `data-science\deployment\deploy.py`                                      | 用于在 Vertex AI Agent Engines 上部署/删除数据科学代理的脚本             | Python, Vertex AI SDK, 部署脚本, absl        |
| `data-science\deployment\test_deployment.py`                             | 用于测试已部署代理的交互式脚本                                     | Python, Vertex AI SDK, 交互式测试              |
| `data-science\eval\test_eval.py`                                         | 使用 AgentEvaluator 评估代理性能的脚本                               | ADK Evaluation, pytest, 评估脚本             |
| `data-science\eval\eval_data\simple.test.json`                           | 包含用于评估代理的简单交互场景测试数据                               | JSON, ADK EvalSet, 测试数据                  |
| `data-science\eval\eval_data\test_config.json`                           | 定义评估标准的配置文件                                             | JSON, ADK Eval Config, 评估配置              |
| `data-science\tests\test_agents.py`                                      | 针对数据科学代理及其子代理的集成测试/单元测试                           | Python, unittest, pytest, 集成测试           |

## fomc-research (FOMC 研究代理)

| 文件路径                                                            | 功能简述                                                       | 技术特点                               |
| :------------------------------------------------------------------ | :------------------------------------------------------------- | :------------------------------------- |
| `fomc-research\deployment\bigquery_setup.py`                        | 用于创建 BigQuery 数据集和表，并插入 CSV 数据的脚本                 | Python, BigQuery API, 数据准备, absl     |
| `fomc-research\deployment\deploy.py`                                | 用于在 Vertex AI Agent Engines 上部署/删除 FOMC 研究代理的脚本      | Python, Vertex AI SDK, 部署脚本, absl    |
| `fomc-research\deployment\test_deployment.py`                       | 用于测试已部署的 FOMC 研究代理的交互式脚本                        | Python, Vertex AI SDK, 交互式测试, absl  |
| `fomc-research\fomc_research\agent.py`                              | 定义 FOMC 研究主代理（根代理），编排子代理和工具                   | ADK Agent, 编排, 子代理集成, 工具集成      |
| `fomc-research\fomc_research\root_agent_prompt.py`                  | 定义根代理的核心指令提示                                         | Python 字符串, 代理指令定义              |
| `fomc-research\fomc_research\shared_libraries\callbacks.py`         | 定义代理的速率限制回调函数                                       | ADK Callbacks, 状态管理, 速率限制      |
| `fomc-research\fomc_research\shared_libraries\file_utils.py`        | 提供文件处理工具函数（下载文件、提取 PDF 文本、生成 HTML 红线等）   | Python, requests, pdfplumber, diff_match_patch |
| `fomc-research\fomc_research\shared_libraries\price_utils.py`       | 提供价格相关工具函数（从 BQ 获取价格、计算利率变动概率等）             | Python, BigQuery API, 金融计算           |
| `fomc-research\fomc_research\sub_agents\analysis_agent.py`          | 定义分析子代理，用于分析研究结果并生成报告                       | ADK Agent, 子代理                      |
| `fomc-research\fomc_research\sub_agents\analysis_agent_prompt.py`   | 定义分析子代理的指令提示                                         | Python 字符串, 子代理指令              |
| `fomc-research\fomc_research\sub_agents\extract_page_data_agent.py` | 定义从网页内容中提取特定数据的子代理                             | ADK Agent, 子代理, HTML 解析（隐式）     |
| `fomc-research\fomc_research\sub_agents\extract_page_data_agent_prompt.py` | 定义提取页面数据子代理的指令提示                               | Python 字符串, 子代理指令              |
| `fomc-research\fomc_research\sub_agents\research_agent.py`          | 定义研究协调子代理，负责协调信息检索和总结任务                     | ADK Agent, 子代理编排, 工具集成          |
| `fomc-research\fomc_research\sub_agents\research_agent_prompt.py`   | 定义研究协调子代理的指令提示                                     | Python 字符串, 子代理指令              |
| `fomc-research\fomc_research\sub_agents\retrieve_meeting_data_agent.py` | 定义从 Fed 网站检索会议数据的子代理                            | ADK Agent, 子代理, 工具集成 (Web, Extract) |
| `fomc-research\fomc_research\sub_agents\retrieve_meeting_data_agent_prompt.py` | 定义检索会议数据子代理的指令提示                             | Python 字符串, 子代理指令              |
| `fomc-research\fomc_research\sub_agents\summarize_meeting_agent.py` | 定义总结 FOMC 会议纪要内容的子代理                             | ADK Agent, 子代理, 文本总结            |
| `fomc-research\fomc_research\sub_agents\summarize_meeting_agent_prompt.py` | 定义总结会议纪要子代理的指令提示                             | Python 字符串, 子代理指令              |
| `fomc-research\fomc_research\tools\compare_statements.py`         | 定义比较不同 FOMC 声明并生成 HTML 红线差异的工具               | ADK Tool, 文件处理 (PDF, HTML)         |
| `fomc-research\fomc_research\tools\compute_rate_move_probability.py` | 定义根据价格数据计算市场隐含利率变动概率的工具                   | ADK Tool, 金融计算, BigQuery           |
| `fomc-research\fomc_research\tools\fetch_page.py`                   | 定义从 URL 获取网页内容的工具                                  | ADK Tool, Web 请求 (urllib)           |
| `fomc-research\fomc_research\tools\fetch_transcript.py`             | 定义从 Fed 网站获取新闻发布会文字记录（PDF）并提取文本的工具       | ADK Tool, 文件处理 (PDF), Web 请求     |
| `fomc-research\fomc_research\tools\store_state.py`                  | 定义在工具上下文中存储状态值的工具                               | ADK Tool, 状态管理                   |

## llm-auditor (LLM 审计代理)

| 文件路径                                                     | 功能简述                                           | 技术特点                             |
| :----------------------------------------------------------- | :------------------------------------------------- | :----------------------------------- |
| `llm-auditor\deployment\deploy.py`                           | 用于在 Vertex AI Agent Engines 上部署/删除/列出 LLM 审计代理的脚本 | Python, Vertex AI SDK, 部署脚本, absl |
| `llm-auditor\eval\test_eval.py`                              | 使用 AgentEvaluator 评估代理性能的脚本                 | ADK Evaluation, pytest, 评估脚本   |
| `llm-auditor\eval\data\blueberries.test.json`                | 包含用于评估蓝莓颜色问题的测试数据                     | JSON, ADK EvalSet, 测试数据          |
| `llm-auditor\eval\data\ice_cream_sandwich.test.json`         | 包含用于评估 Android 版本问题的测试数据                | JSON, ADK EvalSet, 测试数据          |
| `llm-auditor\eval\data\test_config.json`                     | 定义评估标准的配置文件                                 | JSON, ADK Eval Config, 评估配置      |
| `llm-auditor\llm_auditor\agent.py`                           | 定义 LLM 审计主代理（顺序代理），按顺序执行批评家和修订家子代理 | ADK SequentialAgent, 编排            |
| `llm-auditor\llm_auditor\sub_agents\critic\agent.py`         | 定义批评家子代理，使用搜索工具识别和验证陈述                 | ADK Agent, 子代理, Google Search, 回调 |
| `llm-auditor\llm_auditor\sub_agents\critic\prompt.py`        | 定义批评家子代理的指令提示                           | Python 字符串, 子代理指令            |
| `llm-auditor\llm_auditor\sub_agents\reviser\agent.py`        | 定义修订家子代理，根据批评家的发现修正不准确之处             | ADK Agent, 子代理, 回调              |
| `llm-auditor\llm_auditor\sub_agents\reviser\prompt.py`       | 定义修订家子代理的指令提示                           | Python 字符串, 子代理指令            |
| `llm-auditor\tests\test_agents.py`                           | LLM 审计代理的基本单元测试                           | Python, unittest, pytest, 单元测试 |

## personalized-shopping (个性化购物代理)

| 文件路径                                                                          | 功能简述                                                         | 技术特点                                       |
| :-------------------------------------------------------------------------------- | :--------------------------------------------------------------- | :--------------------------------------------- |
| `personalized-shopping\deployment\deploy.py`                                      | 用于在 Vertex AI Agent Engines 上部署个性化购物代理的脚本             | Python, Vertex AI SDK, 部署脚本                  |
| `personalized-shopping\eval\test_eval.py`                                         | 使用 AgentEvaluator 评估代理性能的脚本                             | ADK Evaluation, pytest, 评估脚本               |
| `personalized-shopping\eval\eval_data\simple.test.json`                           | 包含用于评估代理的简单交互场景测试数据                               | JSON, ADK EvalSet, 测试数据                    |
| `personalized-shopping\eval\eval_data\test_config.json`                           | 定义评估标准的配置文件                                               | JSON, ADK Eval Config, 评估配置                |
| `personalized-shopping\personalized_shopping\agent.py`                            | 定义个性化购物主代理，包含搜索和点击工具                           | ADK Agent, 工具集成 (FunctionTool)           |
| `personalized-shopping\personalized_shopping\prompt.py`                           | 定义个性化购物代理的核心指令提示，指导交互流程                       | Python 字符串, 代理指令定义                    |
| `personalized-shopping\personalized_shopping\shared_libraries\init_env.py`        | 初始化 WebAgentTextEnv 环境，用于模拟 Web 交互                   | Python, gym, WebAgentSite, 环境初始化          |
| `personalized-shopping\personalized_shopping\shared_libraries\search_engine\convert_product_file_format.py` | 将产品数据文件转换为搜索引擎（Pyserini）所需的格式               | Python, 数据预处理, Pyserini                   |
| `personalized-shopping\personalized_shopping\shared_libraries\web_agent_site\utils.py` | WebAgentSite 环境的通用工具函数（如随机索引、日志记录、MTurk 代码生成） | Python, 实用工具函数                         |
| `personalized-shopping\personalized_shopping\shared_libraries\web_agent_site\engine\engine.py` | WebAgentSite 环境的核心引擎，处理状态、动作、渲染 HTML 等         | Python, Flask (模拟), Pyserini, HTML 渲染, 状态机 |
| `personalized-shopping\personalized_shopping\shared_libraries\web_agent_site\engine\goal.py` | 定义目标生成和奖励计算逻辑                                       | Python, NLP (spaCy), 模糊匹配 (thefuzz), 奖励函数 |
| `personalized-shopping\personalized_shopping\shared_libraries\web_agent_site\engine\normalize.py` | 提供颜色和尺寸规范化的函数                                       | Python, 正则表达式, 数据规范化                 |
| `personalized-shopping\personalized_shopping\shared_libraries\web_agent_site\envs\web_agent_text_env.py` | 定义基于文本的 WebAgentSite Gym 环境                          | Python, gym, WebAgentSite, 环境定义            |
| `personalized-shopping\personalized_shopping\tools\click.py`                      | 定义模拟点击网页按钮的工具                                       | ADK Tool (FunctionTool), WebAgentSite 交互     |
| `personalized-shopping\personalized_shopping\tools\search.py`                     | 定义模拟在 Webshop 中搜索关键词的工具                          | ADK Tool (FunctionTool), WebAgentSite 交互     |
| `personalized-shopping\tests\test_tools.py`                                       | 使用 AgentEvaluator 评估代理工具性能的脚本                       | ADK Evaluation, pytest, 评估脚本               |
| `personalized-shopping\tests\example_interactions\image_search_denim_skirt.session.json` | 记录了基于图像搜索牛仔裙场景的会话日志                           | JSON, 会话日志, 示例交互                     |
| `personalized-shopping\tests\example_interactions\text_search_floral_dress.session.json` | 记录了基于文本搜索碎花裙场景的会话日志                           | JSON, 会话日志, 示例交互                     |
| `personalized-shopping\tests\tools\test_config.json`                              | 定义工具评估标准的配置文件                                         | JSON, ADK Eval Config, 评估配置              |
| `personalized-shopping\tests\tools\tools.test.json`                               | 包含用于评估代理工具（如搜索）的测试数据                           | JSON, ADK EvalSet, 测试数据                  |

## RAG (检索增强生成代理)

| 文件路径                                                        | 功能简述                                           | 技术特点                                 |
| :-------------------------------------------------------------- | :------------------------------------------------- | :--------------------------------------- |
| `RAG\deployment\deploy.py`                                      | 用于在 Vertex AI Agent Engines 上部署 RAG 代理的脚本       | Python, Vertex AI SDK, 部署脚本, dotenv    |
| `RAG\deployment\run.py`                                         | 用于与已部署的 RAG 代理进行交互式对话的脚本             | Python, Vertex AI SDK, 交互式测试, dotenv    |
| `RAG\eval\test_eval.py`                                         | 使用 AgentEvaluator 评估 RAG 代理性能的脚本            | ADK Evaluation, pytest, 评估脚本         |
| `RAG\eval\data\conversation.test.json`                          | 包含用于评估 RAG 代理的完整对话场景测试数据              | JSON, ADK EvalSet, 测试数据              |
| `RAG\eval\data\test_config.json`                                | 定义 RAG 代理评估标准的配置文件                      | JSON, ADK Eval Config, 评估配置          |
| `RAG\rag\agent.py`                                              | 定义 RAG 代理，集成 Vertex AI RAG 检索工具             | ADK Agent, Vertex AI RAG, 工具集成         |
| `RAG\rag\prompts.py`                                            | 定义 RAG 代理的核心指令提示，指导检索和回答流程           | Python 字符串, 代理指令定义              |
| `RAG\rag\shared_libraries\prepare_corpus_and_data.py`           | 用于准备（下载、创建/获取、上传）Vertex AI RAG 语料库的脚本 | Python, Vertex AI RAG API, requests, 数据准备 |

## travel-concierge (旅行规划代理)

| 文件路径                                                                    | 功能简述                                                               | 技术特点                                       |
| :-------------------------------------------------------------------------- | :--------------------------------------------------------------------- | :--------------------------------------------- |
| `travel-concierge\deployment\deploy.py`                                     | 用于在 Vertex AI Agent Engines 上部署/删除/测试旅行规划代理的脚本               | Python, Vertex AI SDK, 部署脚本, absl, dotenv  |
| `travel-concierge\eval\itinerary_empty_default.json`                        | 定义一个空的默认行程状态，用于评估或初始化                                   | JSON, 初始状态                                 |
| `travel-concierge\eval\itinerary_seattle_example.json`                      | 定义一个包含西雅图行程示例的状态，用于评估或初始化                             | JSON, 初始状态, 示例数据                     |
| `travel-concierge\eval\test_eval.py`                                        | 使用 AgentEvaluator 评估代理在不同阶段（灵感、行前、行中）性能的脚本             | ADK Evaluation, pytest, 评估脚本               |
| `travel-concierge\eval\data\inspire.test.json`                              | 包含用于评估旅行灵感阶段交互的测试数据                                     | JSON, ADK EvalSet, 测试数据                    |
| `travel-concierge\eval\data\intrip.test.json`                               | 包含用于评估行程中阶段交互的测试数据                                     | JSON, ADK EvalSet, 测试数据                    |
| `travel-concierge\eval\data\pretrip.test.json`                              | 包含用于评估行前准备阶段交互的测试数据                                     | JSON, ADK EvalSet, 测试数据                    |
| `travel-concierge\eval\data\test_config.json`                               | 定义旅行规划代理评估标准的配置文件                                         | JSON, ADK Eval Config, 评估配置              |
| `travel-concierge\tests\mcp_abnb.py`                                        | 示例：将 MCP 工具（如 Airbnb）集成到旅行规划代理中                          | Python, ADK MCP Toolset, 异步, 工具扩展      |
| `travel-concierge\tests\programmatic_example.py`                            | 示例：通过 HTTP API 与作为服务器运行的 ADK 代理进行编程交互                  | Python, requests, API 交互                   |
| `travel-concierge\tests\unit\test_tools.py`                                 | 针对旅行规划代理工具（如记忆、地点）的单元测试                             | Python, unittest, pytest, 单元测试           |
| `travel-concierge\travel_concierge\agent.py`                                | 定义旅行规划主代理（根代理），编排各个阶段的子代理                           | ADK Agent, 编排, 子代理集成, 回调函数          |
| `travel-concierge\travel_concierge\prompt.py`                               | 定义根代理的核心指令提示，包含状态和阶段判断逻辑                           | Python 字符串, 代理指令定义, 状态驱动        |
| `travel-concierge\travel_concierge\shared_libraries\constants.py`           | 定义用于会话状态管理的常量键名                                           | Python, 常量定义                             |
| `travel-concierge\travel_concierge\shared_libraries\types.py`               | 定义旅行相关的 Pydantic 数据模型（房间、酒店、航班、目的地、POI、行程等） | Pydantic, 数据模型定义                         |
| `travel-concierge\travel_concierge\sub_agents\booking\agent.py`             | 定义预订子代理及其组件（创建预订、支付选择、处理支付）                         | ADK Agent, 子代理, AgentTool                   |
| `travel-concierge\travel_concierge\sub_agents\booking\prompt.py`            | 定义预订子代理及其组件的指令提示                                         | Python 字符串, 子代理指令                      |
| `travel-concierge\travel_concierge\sub_agents\inspiration\agent.py`         | 定义旅行灵感子代理及其组件（地点推荐、POI 推荐）                           | ADK Agent, 子代理, AgentTool, JSON 输出        |
| `travel-concierge\travel_concierge\sub_agents\inspiration\prompt.py`        | 定义旅行灵感子代理及其组件的指令提示                                       | Python 字符串, 子代理指令                      |
| `travel-concierge\travel_concierge\sub_agents\in_trip\agent.py`             | 定义行程中子代理及其组件（行程监控、当日协调）                               | ADK Agent, 子代理, AgentTool                   |
| `travel-concierge\travel_concierge\sub_agents\in_trip\prompt.py`            | 定义行程中子代理及其组件的指令提示                                         | Python 字符串, 子代理指令                      |
| `travel-concierge\travel_concierge\sub_agents\in_trip\tools.py`             | 定义行程中子代理使用的工具（航班状态检查、预订检查、天气影响检查、交通协调逻辑） | ADK Tools (函数), 模拟 API, 逻辑处理           |
| `travel-concierge\travel_concierge\sub_agents\planning\agent.py`            | 定义行程规划子代理及其组件（航班搜索/选座、酒店搜索/选房、行程生成）           | ADK Agent, 子代理, AgentTool, JSON 输出        |
| `travel-concierge\travel_concierge\sub_agents\planning\prompt.py`           | 定义行程规划子代理及其组件的指令提示                                       | Python 字符串, 子代理指令                      |
| `travel-concierge\travel_concierge\sub_agents\post_trip\agent.py`           | 定义行程后子代理，用于收集用户反馈                                         | ADK Agent, 子代理, 工具集成 (Memory)         |
| `travel-concierge\travel_concierge\sub_agents\post_trip\prompt.py`          | 定义行程后子代理的指令提示                                               | Python 字符串, 子代理指令                      |
| `travel-concierge\travel_concierge\sub_agents\pre_trip\agent.py`            | 定义行前准备子代理及其组件（打包建议）                                   | ADK Agent, 子代理, AgentTool, 工具集成 (Search) |
| `travel-concierge\travel_concierge\sub_agents\pre_trip\prompt.py`           | 定义行前准备子代理及其组件的指令提示                                       | Python 字符串, 子代理指令                      |
| `travel-concierge\travel_concierge\tools\memory.py`                         | 定义用于在会话状态中记忆/遗忘信息的工具，并处理初始状态加载                 | ADK Tool, 状态管理, 初始化                   |
| `travel-concierge\travel_concierge\tools\places.py`                         | 封装 Google Places API，用于查找地点信息和坐标                         | ADK Tool, Google Places API, requests        |
| `travel-concierge\travel_concierge\tools\search.py`                         | 封装 Google Search Grounding 工具，提供带有特定指令的搜索能力            | ADK AgentTool, Google Search               |