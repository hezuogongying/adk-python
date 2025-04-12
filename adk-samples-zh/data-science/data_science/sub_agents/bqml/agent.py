
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""从 SQLite 到 BigQuery 的翻译器。"""

import os # 导入 os 模块，用于环境变量等操作系统交互
import re # 导入 re 模块，用于正则表达式操作
from typing import Any, Final, Tuple, List, Dict, Union # 导入类型注解相关的类型

import regex # 导入 regex 模块，提供更强大的正则表达式功能（例如递归匹配）
import sqlglot # 导入 sqlglot 库，用于 SQL 解析、转译和优化
import sqlglot.optimizer # 导入 sqlglot 的优化器模块

# 从相对路径导入 GeminiModel 和修正提示模板
from ..llm_utils import GeminiModel  # pylint: disable=g-importing-member
from .correction_prompt_template import CORRECTION_PROMPT_TEMPLATE_V1_0  # pylint: disable=g-importing-member

# 定义类型别名，提高代码可读性
ColumnSchemaType = Tuple[str, str] # 列模式类型：(列名, 列类型) 的元组
AllColumnsSchemaType = List[ColumnSchemaType] # 所有列模式类型：列模式元组的列表
TableSchemaType = Tuple[str, AllColumnsSchemaType] # 表模式类型：(表名, 所有列模式列表) 的元组
DDLSchemaType = List[TableSchemaType] # DDL 模式类型：表模式元组的列表

SQLGlotColumnsDictType = Dict[str, str] # SQLGlot 使用的列字典类型：{列名: 列类型}
SQLGlotSchemaType = Dict[str, Any] # SQLGlot 使用的模式类型：嵌套字典 {catalog: {db: {table: {column: type}}}}

# BIRD 数据集样本类型（这里用字典表示，具体结构取决于 BIRD 数据格式）
BirdSampleType = Dict[str, Any]


def _isinstance_list_of_str_tuples_lists(obj: Any) -> bool:
  """检查对象是否为字符串元组或列表的列表。"""
  # 检查 obj 是否是列表
  return (
      isinstance(obj, list)
      # 检查列表中的所有元素是否都是元组或列表
      and all([isinstance(v, (tuple, list)) for v in obj])
      # 检查每个元组/列表的第一个和第二个元素是否都是字符串
      and all([isinstance(v[0], str) and isinstance(v[1], str) for v in obj])
  )


def _isinstance_ddl_schema_type(obj: Any) -> bool:
  """检查对象是否为 DDLSchemaType 类型。"""
  # pylint: disable=g-complex-comprehension # 禁用关于复杂列表推导的 pylint 警告
  return (
      # 检查 obj 是否是列表
      isinstance(obj, list)
      # 检查列表中的所有元素是否都是元组或列表
      and all([isinstance(v, (tuple, list)) for v in obj])
      # 检查每个元组/列表的第一个元素是否是字符串（表名）
      # 并且第二个元素是否是列表（列信息列表）
      and all([isinstance(v[0], str) and isinstance(v[1], list) for v in obj])
      # 检查每个表模式元组/列表中的第二个元素（列信息列表）
      # 是否符合 _isinstance_list_of_str_tuples_lists 定义的格式
      and all([_isinstance_list_of_str_tuples_lists(v[1]) for v in obj])
  )
  # pylint: enable=g-complex-comprehension # 重新启用 pylint 警告


def _isinstance_sqlglot_schema_type(obj: Any) -> bool:
  """检查对象是否为 SQLGlotSchemaType 类型（嵌套字典）。"""
  # pylint: disable=g-complex-comprehension
  # 检查 obj 是否是字典
  return (
      isinstance(obj, dict)
      # 递归检查：检查字典的所有值是否也都是字典（支持 catalog 和 db 层级）
      and all([isinstance(v, dict) for v in obj.values()])
      # 检查最内层字典（表级）的键（列名）是否都是字符串
      and all([isinstance(c, str) for d in obj.values() for c, _ in d.items()])
      # 检查最内层字典（表级）的值（列类型）是否都是字符串
      and all([isinstance(t, str) for d in obj.values() for _, t in d.items()])
  )
  # pylint: enable=g-complex-comprehension
  # 注意：这个检查比较基础，没有严格检查嵌套层级，假设至少有 table 层级。


def _isinstance_bird_sample_type(obj: Any) -> bool:
  """检查对象是否为 BirdSampleType 类型（字典但不是 SQLGlot 模式）。"""
  # 检查 obj 是否是字典，并且不是 SQLGlot 模式类型
  return isinstance(obj, dict) and not _isinstance_sqlglot_schema_type(obj)


class SqlTranslator:
  """从 SQLite 到 BigQuery 的翻译器。

  此类用于将 SQL 查询从输入 SQL 方言（如 SQLite）翻译为输出 SQL 方言（如 BigQuery）。
  它使用 SQLGlot 库作为工具来执行翻译。

  翻译通过以下步骤完成：
  1. （可选）如果输入 SQL 查询中存在错误，则首先由 LLM 修改输入 SQL 查询以解决错误。
  2. 然后，通过工具将输入 SQL 查询翻译为输出 SQL 方言的 SQL 查询。
  3. （可选）如果工具输出的 SQL 查询中存在错误，则由 LLM 修改工具输出的 SQL 查询以解决错误。

  类属性:
    INPUT_DIALECT: 输入 SQL 方言。
    OUTPUT_DIALECT: 输出 SQL 方言。

  属性:
    _model: 用于 LLM 的模型对象或模型名称。
    _temperature: 用于 LLM 的温度参数。
    _process_input_errors: 如果为 True，则应由 LLM 处理输入 SQL 查询中的任何错误。
    _process_tool_output_errors: 如果为 True，则应由 LLM 处理工具输出 SQL 查询中的任何错误。
    _input_errors: 存储检测到的输入 SQL 错误。
    _tool_output_errors: 存储检测到的工具输出 SQL 错误。
  """

  INPUT_DIALECT: Final[str] = "sqlite" # 定义输入方言为 SQLite
  OUTPUT_DIALECT: Final[str] = "bigquery" # 定义输出方言为 BigQuery

  def __init__(
      self,
      model: Union[str, GeminiModel] = "gemini-1.5-flash", # 模型名称或 GeminiModel 实例
      temperature: float = 0.5, # LLM 温度参数
      process_input_errors: bool = False, # 是否处理输入错误
      process_tool_output_errors: bool = False, # 是否处理输出错误
  ):
    """初始化翻译器。"""
    self._process_input_errors: bool = process_input_errors
    self._process_tool_output_errors: bool = process_tool_output_errors
    self._input_errors: Optional[str] = None # 初始化输入错误为 None
    self._tool_output_errors: Optional[str] = None # 初始化输出错误为 None
    self._temperature: float = temperature
    # 如果传入的是模型名称字符串，则创建一个 GeminiModel 实例
    if isinstance(model, str):
      self._model = GeminiModel(model_name=model, temperature=self._temperature)
    # 否则，直接使用传入的 GeminiModel 实例
    else:
      self._model = model

  @classmethod
  def _parse_response(cls, text: str) -> Optional[str]:
    """从响应文本中提取 SQL 查询。"""
    # 定义匹配 Markdown SQL 代码块的正则表达式模式
    pattern = r"```sql(.*?)```"
    # 在文本中搜索模式，忽略换行符 (re.DOTALL)
    match = re.search(pattern, text, re.DOTALL)
    # 如果找到匹配项
    if match:
      # 返回捕获组 1（即代码块内的内容），并去除首尾空白
      return match.group(1).strip()
    # 如果未找到匹配项，返回 None
    return None

  @classmethod
  def _apply_heuristics(cls, sql_query: str) -> str:
    """对 SQL 查询应用启发式规则进行修正。"""
    # 将 SQLite 中的连续单引号 ('') 替换为 BigQuery 中转义的单引号 (\\')
    # 注意：BigQuery 标准 SQL 中通常使用 \' 或 \\' 来转义单引号，或使用 r'' 或 """/'''
    # 这里的替换可能不是最优的，但作为一种启发式规则
    if "''" in sql_query:
      sql_query = sql_query.replace("''", "\\'")
    return sql_query

  @classmethod
  def _extract_schema_from_ddl_statement(
      cls, ddl_statement: str
  ) -> Optional[TableSchemaType]:
    """从单个 DDL 语句中提取模式。"""
    # 定义用于分割 DDL 语句的正则表达式模式
    # 匹配 CREATE [OR REPLACE] TABLE [`]<table_name>[`] (<all_columns>);
    splitter_pattern = (
        # 匹配 "CREATE TABLE" 或 "CREATE OR REPLACE TABLE"，忽略前导/尾随空格和大小写
        r"^\s*CREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+"
        # 匹配表名，可以包含字母、数字、下划线、点、连字符，可选地用反引号包围
        r"(?:`)?(?P<table_name>[\w\d\-\_\.]+)(?:`)?\s*"
        # 匹配括号内的所有列定义
        r"\((?P<all_columns>.*?)\)\s*;?\s*$" # 使用非贪婪匹配 .*?，并允许可选的分号和空格
    )
    # 使用 regex 模块进行搜索，支持更复杂的模式，并启用 DOTALL, VERBOSE, MULTILINE 标志
    split_match = regex.search(
        splitter_pattern,
        ddl_statement,
        flags=re.DOTALL | re.VERBOSE | re.MULTILINE | re.IGNORECASE, # 增加 IGNORECASE
    )
    # 如果 DDL 语句不匹配模式，返回 None
    if not split_match:
      print(f"Warning: DDL statement did not match splitter pattern: {ddl_statement}")
      return None # 返回 None 而不是 (None, None)

    # 提取表名和所有列定义的字符串
    table_name = split_match.group("table_name")
    all_columns_str = split_match.group("all_columns").strip()
    # 如果表名或列定义为空，返回 None
    if not table_name or not all_columns_str:
      return None # 返回 None

    # 从列定义字符串中提取列信息
    # 匹配模式： `column_name` column_type [OPTIONS(...)] [COMMENT '...'] ,
    # 改进模式以处理 OPTIONS 和 COMMENT
    column_pattern = (
        r"\s*`?(?P<column_name>\w+)`?\s+" # 列名（可选反引号）
        r"(?P<column_type>\w+(?:<[^>]+>)?)"+ # 列类型（可能包含 < > 如 ARRAY<STRING>）
        r"(?:\s+OPTIONS\s*\(.*?\))?" + # 可选的 OPTIONS 子句
        r"(?:\s+COMMENT\s*'.*?')?" + # 可选的 COMMENT 子句
        r"(?:\s*NOT\s+NULL)?" + # 可选的 NOT NULL
        r"(?:\s*DEFAULT\s+.*?)?"+ # 可选的 DEFAULT 子句
        r",?\s*" # 可选的逗号和空格
    )
    # 使用 findall 查找所有匹配的列定义
    columns_matches = regex.findall(column_pattern, all_columns_str, flags=re.IGNORECASE)
    # 将匹配结果转换为 (列名, 列类型) 的元组列表
    columns = [(match[0], match[1].upper()) for match in columns_matches] # 将类型转为大写

    # 如果没有提取到列，返回 None
    if not columns:
      print(f"Warning: No columns extracted from DDL: {ddl_statement}")
      return None

    return table_name, columns

  @classmethod
  def extract_schema_from_ddls(cls, ddls: str) -> DDLSchemaType:
    """从包含多个 DDL 语句的字符串中提取模式。"""
    # 按分号和换行符分割 DDL 语句
    ddl_statements = ddls.split(";\n")
    # 清理每个语句，去除首尾空白，并过滤掉空语句
    ddl_statements = [ddl.strip() for ddl in ddl_statements if ddl.strip()]
    schema: DDLSchemaType = [] # 初始化模式列表
    # 遍历每个 DDL 语句
    for ddl_statement in ddl_statements:
      if ddl_statement:
        # 尝试从单个 DDL 语句中提取表模式
        extracted = cls._extract_schema_from_ddl_statement(ddl_statement + ";") # 加上可能被 split 去掉的分号
        if extracted: # 确保提取成功
            table_name, columns = extracted
            # 如果表名和列都有效，则添加到模式列表中
            if table_name and columns:
                schema.append((table_name, columns))
            else:
                print(f"Warning: Failed to extract schema from: {ddl_statement}")
        else:
             print(f"Warning: Failed to parse DDL statement: {ddl_statement}")
    return schema

  @classmethod
  def _get_schema_from_bird_sample(
      cls, sample: BirdSampleType
  ) -> SQLGlotSchemaType:
    """从 Bird 数据集示例中获取模式信息，并格式化为 SQLGlot 模式。"""
    # BIRD 数据类型到 SQLGlot/通用 SQL 类型的映射
    col_types_map: Dict[str, str] = {
        "text": "STRING", # BIRD 'text' 映射到 STRING
        "number": "FLOAT64", # BIRD 'number' 映射到 FLOAT64 (或 NUMERIC/BIGNUMERIC)
        "time": "TIME",     # BIRD 'time' 映射到 TIME
        "boolean": "BOOL",  # BIRD 'boolean' 映射到 BOOL
        "others": "STRING", # BIRD 'others' (可能表示外键等) 映射到 STRING
        # BIRD 可能没有直接的 DATE/DATETIME/TIMESTAMP，需要根据实际情况调整
        # "date": "DATE",
        # "datetime": "DATETIME",
        # "timestamp": "TIMESTAMP",
    }
    # 获取表名列表
    tables = sample["table_names_original"] # 使用原始表名
    # 获取列所属表的 ID 列表（跳过 '*' 列）
    table_ids = sample["column_names_original"]["table_id"][1:]
    # 获取列名列表（跳过 '*' 列）
    column_names = sample["column_names_original"]["column_name"][1:]
    # 获取列类型列表（跳过 '*' 列）
    column_types = sample["column_types"][1:]
    # 将 BIRD 类型映射到 SQL 类型
    mapped_column_types = [col_types_map.get(col_type, "STRING") for col_type in column_types] # 提供默认值 STRING

    # 断言确保列名和列类型列表长度一致
    assert len(column_names) == len(mapped_column_types)
    # 将列名和映射后的类型组合成元组列表
    cols_and_types: List[Tuple[str, str]] = list(
        zip(column_names, mapped_column_types)
    )

    # 构建 SQLGlot 格式的模式字典
    tables_to_columns: SQLGlotSchemaType = {}
    # 遍历每个列
    for id_pos, table_id in enumerate(table_ids):
        # 获取当前列对应的表名
        table_name = tables[table_id]
        # 如果表名尚未在字典中，则创建一个新的表条目（空字典）
        if table_name not in tables_to_columns:
            tables_to_columns[table_name] = {}
        # 将当前列名和类型添加到对应表的字典中
        column_name, column_type = cols_and_types[id_pos]
        tables_to_columns[table_name][column_name] = column_type

    # BIRD 数据集通常不包含 catalog 和 db 信息，直接返回表级字典
    return tables_to_columns

  @classmethod
  def _get_table_parts(
      cls, table_name: str
  ) -> Tuple[Optional[str], Optional[str], str]:
    """从表名中提取项目（catalog）、数据集（db）和表（table）部分。"""
    # 使用 '.' 分割表名
    table_parts = table_name.split(".")
    num_parts = len(table_parts)
    # 根据分割后的部分数量判断
    if num_parts == 3:
      # project.dataset.table
      return table_parts[0], table_parts[1], table_parts[2]
    elif num_parts == 2:
      # dataset.table
      return None, table_parts[0], table_parts[1]
    elif num_parts == 1:
      # table
      return None, None, table_parts[0]
    else:
      # 无效的表名格式
      raise ValueError(f"无效的表名格式: {table_name}")

  @classmethod
  def format_schema(cls, schema: DDLSchemaType) -> SQLGlotSchemaType:
    """将 DDLSchemaType 格式化为 SQLGlotSchemaType。"""
    schema_dict: Dict[str, Any] = {}
    catalog: Optional[str] = None
    db: Optional[str] = None

    # 遍历从 DDL 提取的每个 (表名, 列列表) 元组
    for table_name_full, columns in schema:
        # 提取项目、数据集和表名
        current_catalog, current_db, table_name_only = cls._get_table_parts(table_name_full)

        # 确定 catalog 和 db
        if catalog is None and current_catalog is not None:
            catalog = current_catalog
        if db is None and current_db is not None:
            db = current_db

        # 处理潜在的冲突或不一致
        if current_catalog is not None and catalog != current_catalog:
            print(f"Warning: Inconsistent catalog found ('{catalog}' vs '{current_catalog}'). Using '{catalog}'.")
        if current_db is not None and db != current_db:
            print(f"Warning: Inconsistent database/dataset found ('{db}' vs '{current_db}'). Using '{db}'.")

        # 构建嵌套字典的层级
        if catalog:
            if catalog not in schema_dict:
                schema_dict[catalog] = {}
            db_level = schema_dict[catalog]
        else:
            db_level = schema_dict # 如果没有 catalog，则直接在顶层

        if db:
            if db not in db_level:
                db_level[db] = {}
            table_level = db_level[db]
        else:
            table_level = db_level # 如果没有 db，则在 catalog 层或顶层

        # 添加表和列信息
        table_level[table_name_only] = {}
        for column_name, column_type in columns:
            table_level[table_name_only][column_name] = column_type

    return schema_dict

  @classmethod
  def rewrite_schema_for_sqlglot(
      cls, schema: Union[str, SQLGlotSchemaType, BirdSampleType, DDLSchemaType]
  ) -> Optional[SQLGlotSchemaType]:
    """将不同格式的模式重写为 SQLGlot 可用的格式。"""
    schema_dict: Optional[SQLGlotSchemaType] = None
    if schema:
      if isinstance(schema, str):
        # 如果是字符串，假定是 DDL 语句，提取并格式化
        ddl_schema_extracted = cls.extract_schema_from_ddls(schema)
        if ddl_schema_extracted: # 确保提取成功
             schema_dict = cls.format_schema(ddl_schema_extracted)
      elif _isinstance_sqlglot_schema_type(schema):
        # 如果已经是 SQLGlot 格式，直接使用
        schema_dict = schema
      elif _isinstance_bird_sample_type(schema):
         # 如果是 BIRD 样本格式，提取并格式化
         # 注意： BIRD 提取的格式可能已经是 SQLGlot 兼容的，根据 _get_schema_from_bird_sample 实现
         schema_dict = cls._get_schema_from_bird_sample(schema)
      elif _isinstance_ddl_schema_type(schema):
         # 如果是 DDLSchemaType 格式，直接格式化
         schema_dict = cls.format_schema(schema)
      else:
        # 不支持的模式类型
        raise TypeError(f"不支持的模式类型: {type(schema)}")
    return schema_dict

  @classmethod
  def _check_for_errors(
      cls,
      sql_query: str,
      sql_dialect: str,
      db: Optional[str] = None,
      catalog: Optional[str] = None,
      schema_dict: Optional[SQLGlotSchemaType] = None,
  ) -> Tuple[Optional[str], str]:
    """检查 SQL 查询中是否存在错误。

    Args:
      sql_query: 要检查错误的 SQL 查询。
      sql_dialect: SQL 查询的方言。
      db: 用于翻译的数据库（数据集）。可选。
      catalog: 用于翻译的目录（项目 ID）。可选。
      schema_dict: 用于翻译的 DDL 模式（SQLGlot 格式）。可选。

    Returns:
      包含 SQL 查询中的错误信息（如果没有错误则为 None）和优化后（或原始）SQL 查询的元组。
    """
    try:
        # 1. 解析 SQL 查询为 SQLGlot 抽象语法树 (AST)
        #    设置 error_level 为 IMMEDIATE 以立即报告解析错误
        sql_query_ast = sqlglot.parse_one(
            sql=sql_query,
            read=sql_dialect.lower(),
            error_level=sqlglot.ErrorLevel.RAISE, # 改为 RAISE 以便捕获异常
        )

        # 2. (可选) 为 AST 中的所有表添加数据库和目录信息
        #    这有助于后续优化器理解表的完整路径
        if db or catalog:
            for table in sql_query_ast.find_all(sqlglot.exp.Table):
                # 只有在提供了 catalog/db 时才设置
                if catalog and not table.catalog: # 避免覆盖已有的 catalog
                     table.set("catalog", sqlglot.exp.Identifier(this=catalog, quoted=True))
                if db and not table.db: # 避免覆盖已有的 db
                     table.set("db", sqlglot.exp.Identifier(this=db, quoted=True))

        # 3. (可选) 尝试优化 SQL 查询
        #    优化器可以进行列限定、简化表达式等操作
        #    同样设置 error_level 以捕获优化过程中的错误
        if schema_dict: # 只有在提供了模式信息时才进行优化
            sql_query_ast = sqlglot.optimizer.optimize(
                sql_query_ast,
                dialect=sql_dialect.lower(),
                schema=schema_dict,
                db=db,
                catalog=catalog,
                error_level=sqlglot.ErrorLevel.RAISE, # 改为 RAISE
            )

        # 4. 将（可能优化后的）AST 转换回 SQL 字符串
        optimized_sql_query = sql_query_ast.sql(dialect=sql_dialect.lower(), pretty=True) # pretty=True 格式化输出
        # 如果没有错误，返回 None 和优化后的 SQL
        return None, optimized_sql_query
    except sqlglot.errors.SqlglotError as e:
        # 如果在解析或优化过程中发生 SQLGlot 错误，返回错误信息和原始 SQL 查询
        return str(e), sql_query

  def _fix_errors(
      self,
      sql_query: str,
      sql_dialect: str,
      apply_heuristics: bool,
      db: Optional[str] = None,
      catalog: Optional[str] = None,
      ddl_schema: Union[str, SQLGlotSchemaType, BirdSampleType, DDLSchemaType, None] = None,
      number_of_candidates: int = 1,
  ) -> str:
    """修正 SQL 查询中的错误。

    Args:
      sql_query: 要修正的 SQL 查询。
      sql_dialect: 输入 SQL 方言。
      apply_heuristics: 如果为 True，则应用启发式规则。
      db: 用于翻译的数据库。可选。
      catalog: 用于翻译的目录（项目 ID）。可选。
      ddl_schema: 用于翻译的 DDL 模式。可以是 SQLGlot 格式、DDLSchemaType、
                   BIRD 数据集示例或包含多个 DDL 语句的字符串。可选。
      number_of_candidates: 要生成的候选修正查询数量，默认为 1。

    Returns:
      str: 修正后的 SQL 查询。
    """
    # 如果需要，应用启发式规则
    if apply_heuristics:
      sql_query = self._apply_heuristics(sql_query)

    # 重写模式（如果提供）为 SQLGlot 格式
    # 这会移除注释和 INSERT INTO 语句
    schema_dict = self.rewrite_schema_for_sqlglot(ddl_schema)

    # 检查当前 SQL 查询是否存在错误
    errors, checked_sql_query = self._check_for_errors(
        sql_query=sql_query,
        sql_dialect=sql_dialect, # 使用目标方言检查
        db=db,
        catalog=catalog,
        schema_dict=schema_dict,
    )

    # 默认返回经过检查（可能优化过）的 SQL
    final_sql_query = checked_sql_query

    # 如果检测到错误
    if errors:
      print(f"检测到 SQL 错误，尝试使用 LLM 修正: {errors}")
      # 准备插入到 Prompt 中的模式信息
      schema_insert = ""
      if schema_dict:
          # 将模式字典转换为字符串插入 Prompt
          # 可以考虑使用 json.dumps 或更友好的格式
          schema_insert = f"\n数据库模式为:\n```sql\n{schema_dict}\n```\n" # 使用代码块格式化

      # 格式化修正 Prompt
      prompt: str = CORRECTION_PROMPT_TEMPLATE_V1_0.format(
          sql_dialect=sql_dialect.lower(), # 目标方言
          errors=errors,                  # 检测到的错误
          sql_query=checked_sql_query,    # 经过检查的 SQL
          schema_insert=schema_insert,    # 插入的模式信息
      )
      # 创建请求列表
      requests: List[str] = [prompt for _ in range(number_of_candidates)]
      # 并行调用 LLM 生成修正后的 SQL
      responses: List[Optional[str]] = self._model.call_parallel(
          requests, parser_func=self._parse_response # 使用解析函数提取 SQL
      )

      # 处理 LLM 的响应
      if responses:
          # 过滤掉 None 的响应
          valid_responses = [r for r in responses if r is not None and r.strip()]
          if valid_responses:
              # pylint: disable=g-bad-todo
              # TODO: 如果 number_of_candidates > 1，这里可能需要更复杂的选择逻辑，
              # 例如，再次检查哪个响应是有效的 SQL，或者选择最常见的响应。
              # pylint: enable=g-bad-todo
              # 目前简单地选择第一个有效的响应
              final_sql_query = valid_responses[0]
              print(f"LLM 修正后的 SQL: {final_sql_query}")
          else:
              print("Warning: LLM 未能提供有效的修正 SQL，将返回原始（经检查的）SQL。")
    # 返回最终的 SQL 查询（可能是修正后的，也可能是检查后的）
    return final_sql_query

  def translate(
      self,
      sql_query: str,
      db: Optional[str] = None,
      catalog: Optional[str] = None,
      ddl_schema: Union[str, SQLGlotSchemaType, BirdSampleType, DDLSchemaType, None] = None,
  ) -> str:
    """将 SQL 查询翻译为输出 SQL 方言。

    Args:
      sql_query: 要翻译的 SQL 查询。
      db: 用于翻译的数据库。可选。
      catalog: 用于翻译的目录（项目 ID）。可选。
      ddl_schema: 用于翻译的 DDL 模式。可以是 SQLGlot 格式、DDLSchemaType、
                   BIRD 数据集示例或包含多个 DDL 语句的字符串。可选。

    Returns:
      翻译后的 SQL 查询。
    """
    print("****** 进入翻译器时的 sql_query:", sql_query)
    # 步骤 1: （可选）处理输入错误
    if self._process_input_errors:
      print("****** 正在处理输入错误...")
      sql_query = self._fix_errors(
          sql_query,
          sql_dialect=self.INPUT_DIALECT, # 使用输入方言修正
          apply_heuristics=True,
          db=db,
          catalog=catalog,
          ddl_schema=ddl_schema,
      )
    print("****** 修正输入错误（如果执行）后的 sql_query:", sql_query)

    # 步骤 2: 使用 SQLGlot 进行方言转译
    try:
      # 调用 sqlglot.transpile 进行翻译
      transpiled_sqls = sqlglot.transpile(
          sql=sql_query,
          read=self.INPUT_DIALECT.lower(),   # 指定输入方言
          write=self.OUTPUT_DIALECT.lower(), # 指定输出方言
          # error_level=sqlglot.ErrorLevel.RAISE, # 可以在转译时捕获错误
          pretty=True # 格式化输出
      )
      # transpile 返回一个列表，通常只包含一个结果
      if transpiled_sqls:
         sql_query = transpiled_sqls[0]
      else:
         print("Warning: SQLGlot transpile 返回空列表。")
         # 保留原始 sql_query 或进行其他错误处理
    except sqlglot.errors.SqlglotError as e:
      print(f"SQLGlot 转译出错: {e}")
      # 保留原始 sql_query 或进行其他错误处理

    print("****** 转译后的 sql_query:", sql_query)

    # 步骤 3: （可选）处理工具输出错误
    if self._tool_output_errors:
      print("****** 正在处理工具输出错误...")
      sql_query = self._fix_errors(
          sql_query,
          sql_dialect=self.OUTPUT_DIALECT, # 使用输出方言修正
          apply_heuristics=True, # 再次应用启发式规则
          db=db,
          catalog=catalog,
          ddl_schema=ddl_schema,
      )
    print("****** 修正输出错误（如果执行）后的 sql_query:", sql_query)

    # 最终清理
    # 移除首尾空白，并将双引号替换为 BigQuery 更常用的反引号
    sql_query = sql_query.strip().replace('"', "`")
    # 再次应用启发式规则（可能冗余，但确保一致性）
    sql_query = self._apply_heuristics(sql_query)
    print("****** 最终返回的 sql_query:", sql_query)

    return sql_query


