
# 导入必要的库
import logging
import os
import sys

# 导入 Google Cloud Storage 客户端库
from google.cloud import storage
# 导入 google 异常处理库
from google.cloud import exceptions as google_exceptions
# 导入 Vertex AI SDK
import vertexai
# 从 absl 库导入 app 和 flags，用于处理命令行参数
from absl import app, flags
# 从 dotenv 库导入 load_dotenv，用于加载环境变量
from dotenv import load_dotenv
# 导入数据科学项目的根 agent
from data_science.agent import root_agent
# 导入 agent_engines 和 AdkApp
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

# 添加父目录到系统路径，以便导入 agent 相关模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 获取日志记录器
logger = logging.getLogger(__name__)

# 定义命令行标志 (flags)
FLAGS = flags.FLAGS
# 定义 GCP 项目 ID 标志
flags.DEFINE_string("project_id", None, "GCP 项目 ID。")
# 定义 GCP 位置标志
flags.DEFINE_string("location", None, "GCP 位置。")
# 定义 GCS 存储桶名称标志
flags.DEFINE_string("bucket", None, "GCS 存储桶名称（不含 gs:// 前缀）。")
# 定义 ReasoningEngine 资源 ID 标志
flags.DEFINE_string(
    "resource_id", None, "ReasoningEngine 资源 ID（部署 agent 后返回）。"
)
# 定义是否创建新 agent 的标志
flags.DEFINE_bool("create", False, "创建新的 agent。")
# 定义是否删除现有 agent 的标志
flags.DEFINE_bool("delete", False, "删除现有的 agent。")
# 将 --create 和 --delete 标志标记为互斥，两者只能选其一
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])

# 定义 agent wheel 文件的路径
AGENT_WHL_FILE = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "dist",
        "data_science-0.1.0-py3-none-any.whl",
    )
)

# 配置日志记录
logging.basicConfig(level=logging.INFO)


def setup_staging_bucket(
    project_id: str, location: str, bucket_name: str
) -> str:
    """
    检查中转存储桶（staging bucket）是否存在，如果不存在则创建它。

    参数:
        project_id: GCP 项目 ID。
        location: 存储桶的 GCP 位置。
        bucket_name: 期望的存储桶名称（不含 gs:// 前缀）。

    返回:
        完整的存储桶路径 (gs://<bucket_name>)。

    抛出异常:
        google_exceptions.GoogleCloudError: 如果存储桶创建失败。
    """
    # 初始化 Storage 客户端
    storage_client = storage.Client(project=project_id)
    try:
        # 检查存储桶是否存在
        bucket = storage_client.lookup_bucket(bucket_name)
        if bucket:
            logger.info("中转存储桶 gs://%s 已存在。", bucket_name)
        else:
            logger.info(
                "未找到中转存储桶 gs://%s。正在创建...", bucket_name
            )
            # 如果存储桶不存在，则创建它
            new_bucket = storage_client.create_bucket(
                bucket_name, project=project_id, location=location
            )
            logger.info(
                "已成功在 %s 创建中转存储桶 gs://%s。",
                new_bucket.name,
                location,
            )
            # 为简化起见，启用统一的存储桶级访问权限
            new_bucket.iam_configuration.uniform_bucket_level_access_enabled = (
                True
            )
            new_bucket.patch()
            logger.info(
                "已为 gs://%s 启用统一的存储桶级访问权限。",
                new_bucket.name,
            )

    except google_exceptions.Forbidden as e:
        # 处理权限错误
        logger.error(
            (
                "存储桶 gs://%s 出现权限被拒绝错误。"
                "请确保服务账号具有 'Storage Admin' 角色。错误信息: %s"
            ),
            bucket_name,
            e,
        )
        raise
    except google_exceptions.Conflict as e:
        # 处理名称冲突错误（可能已被其他项目拥有或最近删除）
        logger.warning(
            (
                "存储桶 gs://%s 可能已存在，但由另一个项目拥有或最近被删除。"
                "错误信息: %s"
            ),
            bucket_name,
            e,
        )
        # 假设如果存储桶存在，即使有冲突警告也可以继续
    except google_exceptions.ClientError as e:
        # 处理其他客户端错误
        logger.error(
            "创建或访问存储桶 gs://%s 失败。错误信息: %s",
            bucket_name,
            e,
        )
        raise

    # 返回完整的存储桶 URI
    return f"gs://{bucket_name}"


def create(env_vars: dict[str, str]) -> None:
    """创建并部署 agent。"""
    # 使用根 agent 创建 AdkApp 实例
    adk_app = AdkApp(
        agent=root_agent,
        enable_tracing=False, # 禁用追踪
        env_vars=env_vars # 传递环境变量
    )

    # 检查 agent wheel 文件是否存在
    if not os.path.exists(AGENT_WHL_FILE):
        logger.error("在 %s 未找到 Agent wheel 文件。", AGENT_WHL_FILE)
        # 可以在这里添加关于如何构建 wheel 文件的说明
        raise FileNotFoundError(f"未找到 Agent wheel 文件: {AGENT_WHL_FILE}")

    logger.info("正在使用 agent wheel 文件: %s", AGENT_WHL_FILE)

    # 使用 agent_engines 创建远程 agent
    remote_agent = agent_engines.create(
        adk_app,
        requirements=[AGENT_WHL_FILE], # 指定依赖项
        extra_packages=[AGENT_WHL_FILE], # 指定额外的包
    )
    logger.info("已创建远程 agent: %s", remote_agent.resource_name)
    print(f"\n成功创建 agent: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    """删除指定的 agent。"""
    logger.info("尝试删除 agent: %s", resource_id)
    try:
        # 获取远程 agent 实例
        remote_agent = agent_engines.get(resource_id)
        # 强制删除 agent
        remote_agent.delete(force=True)
        logger.info("成功删除远程 agent: %s", resource_id)
        print(f"\n成功删除 agent: {resource_id}")
    except google_exceptions.NotFound:
        # 处理 agent 未找到的情况
        logger.error("未找到资源 ID 为 %s 的 agent。", resource_id)
        print(f"\n未找到 Agent: {resource_id}")
    except Exception as e:
        # 处理其他删除错误
        logger.error(
            "删除 agent %s 时发生错误: %s", resource_id, e
        )
        print(f"\n删除 agent {resource_id} 时出错: {e}")


def main(argv: list[str]) -> None:  # pylint: disable=unused-argument
    """主执行函数。"""
    # 加载 .env 文件中的环境变量
    load_dotenv()
    # 初始化环境变量字典
    env_vars = {}

    # 获取项目 ID，优先使用命令行标志，其次使用环境变量
    project_id = (
        FLAGS.project_id
        if FLAGS.project_id
        else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    # 获取位置信息，优先使用命令行标志，其次使用环境变量
    location = (
        FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    # 设置默认存储桶名称（如果未提供）
    default_bucket_name = f"{project_id}-adk-staging" if project_id else None
    # 获取存储桶名称，优先使用命令行标志，其次使用环境变量，最后使用默认名称
    bucket_name = (
        FLAGS.bucket
        if FLAGS.bucket
        else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET", default_bucket_name)
    )
    # 将必要的配置添加到环境变量字典中
    env_vars["GOOGLE_CLOUD_PROJECT"] = project_id
    env_vars["GOOGLE_CLOUD_LOCATION"] = location
    env_vars["BQ_DATASET_ID"] = os.getenv("BQ_DATASET_ID") # BigQuery 数据集 ID
    env_vars["BQ_PROJECT_ID"] = os.getenv("BQ_PROJECT_ID") # BigQuery 项目 ID
    env_vars["BQML_RAG_CORPUS_NAME"] = os.getenv("BQML_RAG_CORPUS_NAME") # BQML RAG 语料库名称
    env_vars["CODE_INTERPRETER_EXTENSION_NAME"] = os.getenv(
        "CODE_INTERPRETER_EXTENSION_NAME") # 代码解释器扩展名称

    # 记录使用的配置信息
    logger.info("正在使用 PROJECT: %s", project_id)
    logger.info("正在使用 LOCATION: %s", location)
    logger.info("正在使用 BUCKET NAME: %s", bucket_name)

    # --- 输入验证 ---
    if not project_id:
        print("\n错误: 缺少必需的 GCP 项目 ID。")
        print(
            "请设置 GOOGLE_CLOUD_PROJECT 环境变量或使用 --project_id 标志。"
        )
        return
    if not location:
        print("\n错误: 缺少必需的 GCP 位置。")
        print(
            "请设置 GOOGLE_CLOUD_LOCATION 环境变量或使用 --location 标志。"
        )
        return
    if not bucket_name:
        print("\n错误: 缺少必需的 GCS 存储桶名称。")
        print(
            "请设置 GOOGLE_CLOUD_STORAGE_BUCKET 环境变量或使用 --bucket 标志。"
        )
        return
    if not FLAGS.create and not FLAGS.delete:
        print("\n错误: 必须指定 --create 或 --delete 标志。")
        return
    if FLAGS.delete and not FLAGS.resource_id:
        print(
            "\n错误: 使用 --delete 标志时需要指定 --resource_id。"
        )
        return
    # --- 输入验证结束 ---

    try:
        # 设置中转存储桶
        staging_bucket_uri=None
        if FLAGS.create:
            staging_bucket_uri = setup_staging_bucket(
                project_id, location, bucket_name
            )

        # 在存储桶设置和验证之后初始化 Vertex AI
        vertexai.init(
            project=project_id,
            location=location,
            staging_bucket=staging_bucket_uri,  # 中转存储桶现在直接传递给 create/update 方法
        )

        # 根据命令行标志执行创建或删除操作
        if FLAGS.create:
            create(env_vars)
        elif FLAGS.delete:
            delete(FLAGS.resource_id)

    except google_exceptions.Forbidden as e:
        # 处理权限错误
        print(
            "权限错误: 请确保服务账号/用户具有必要的权限"
            " (例如, Storage Admin, Vertex AI User)。"
            f"\n详细信息: {e}"
        )
    except FileNotFoundError as e:
        # 处理文件未找到错误
        print(f"\n文件错误: {e}")
        print(
            "请确保 agent wheel 文件存在于 'deployment' 目录中，"
            "并且您已经运行了构建脚本 "
            "(例如, poetry build --format=wheel --output=deployment)。"
        )
    except Exception as e:
        # 处理其他未预料的错误
        print(f"\n发生未预料的错误: {e}")
        logger.exception(
            "main 函数中未处理的异常:"
        )  # 记录完整的堆栈跟踪

# 程序入口点
if __name__ == "__main__":
    # 运行主函数
    app.run(main)


