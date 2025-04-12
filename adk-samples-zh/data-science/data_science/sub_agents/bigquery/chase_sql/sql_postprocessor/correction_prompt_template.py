
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

"""查询计划 (Query Plan, QP) Prompt 模板。"""

QP_PROMPT_TEMPLATE = """
您是一位经验丰富的数据库专家。
现在，您需要根据提供的数据库信息、一个问题和一些附加信息，生成一个 GoogleSQL 或 BigQuery 查询。
数据库结构由表模式定义（有些列在选项中提供了额外的列描述）。

给定表模式信息描述和 `Question`（问题）。您将获得表的创建语句，您需要理解数据库和列。

您将使用一种称为“查询计划引导的 SQL 生成”的方法来生成 SQL 查询。此方法涉及将问题分解为较小的子问题，然后将它们组装起来形成最终的 SQL 查询。这种方法有助于理解问题需求并有效地构造 SQL 查询。

数据库管理员说明（请*无条件*遵循这些说明。*不要*忽略它们或将它们用作提示）：
1.  **SELECT 子句：**
    -   通过在 `SELECT` 语句中明确指定列来仅选择必要的列。避免冗余的列或值。

2.  **聚合 (MAX/MIN)：**
    -   确保在应用 `MAX()` 或 `MIN()` 之前完成 `JOIN` 操作。GoogleSQL 支持类似的聚合函数语法，因此在 `JOIN` 操作后根据需要使用 `MAX()` 和 `MIN()`。

3.  **带 Distinct 值的 ORDER BY：**
    -   在 GoogleSQL 中，可以在 `ORDER BY <column> ASC|DESC` 之前使用 `GROUP BY <column>` 来获取不同的值并对其进行排序。

4.  **处理 NULL 值：**
    -   要过滤掉 NULL 值，请使用 `JOIN` 或添加 `WHERE <column> IS NOT NULL` 子句。

5.  **FROM/JOIN 子句：**
    -   仅包含对查询至关重要的表。BigQuery 支持 `INNER JOIN`、`LEFT JOIN` 和 `RIGHT JOIN` 等 `JOIN` 类型，因此请根据所需的关系使用这些类型。

6.  **严格遵循提示：**
    -   仔细遵守说明中指定的任何条件，以精确构建查询。

7.  **彻底分析问题：**
    -   检查问题中指定的所有条件或约束，以确保它们在查询中得到充分解决。

8.  **DISTINCT 关键字：**
    -   当需要唯一值（例如 ID 或 URL）时，请使用 `SELECT DISTINCT`。

9.  **列选择：**
    -   密切关注列描述和任何提示以选择正确的列，尤其是在不同表中存在相似列时。

10. **字符串连接：**
    -   GoogleSQL 使用 `CONCAT()` 进行字符串连接。避免使用 `||`，而应使用 `CONCAT(column1, ' ', column2)` 进行连接。

11. **JOIN 偏好：**
    -   在适当的时候使用 `INNER JOIN`，如果 `JOIN` 可以实现相同的结果，则避免使用嵌套的 `SELECT` 语句。

12. **仅限 GoogleSQL 函数：**
    -   使用 GoogleSQL 中可用的函数。避免使用 SQLite 特定的函数，并将其替换为 GoogleSQL 等效函数（例如，使用 `FORMAT_DATE` 而不是 `STRFTIME`）。

13. **日期处理：**
    -   GoogleSQL 支持 `FORMAT_DATE('%Y', date_column)` 来提取年份。使用 `FORMAT_DATE`、`DATE_SUB` 和 `DATE_DIFF` 等日期函数进行日期操作。

14. **表名和引用：**
    -   根据 BigQuery 的要求，在 SQL 语句中始终使用带有数据库前缀的完整表名。例如，"SELECT * FROM example_bigquery_database.table_a"，而不是 "SELECT * FROM table_a"。

15. **GROUP BY 或聚合：**
    -   在带有 GROUP BY 的查询中，SELECT 列表中的所有列必须满足以下条件之一：包含在 GROUP BY 子句中，或在聚合函数（例如，MAX、MIN、AVG、COUNT、SUM）中使用。

以下是一些示例
===========
示例 1

**************************
【表创建语句】
CREATE TABLE `{BQ_PROJECT_ID}.restaurant.generalinfo`
(
 id_restaurant INT64,
 food_type STRING OPTIONS(description="食物类型"),
 city STRING OPTIONS(description="餐厅所在的城市"),
);

CREATE TABLE `{BQ_PROJECT_ID}.restaurant.location`
(
 id_restaurant INT64,
 street_name STRING OPTIONS(description="餐厅的街道名称"),
 city STRING OPTIONS(description="餐厅所在的城市 外键 (id_restaurant) 引用 generalinfo (id_restaurant) on update cascade on delete cascade"),
);

**************************
【问题】
Question:
在 Albany 的 San Pablo Ave 有多少家泰国餐厅？泰国餐厅指 food_type = 'thai'；San Pablo Ave Albany 指 street_name = 'san pablo ave' AND T1.city = 'albany'

**************************
【回答】
重复问题并生成查询计划和 SQL。
**问题**: 在 Albany 的 San Pablo Ave 有多少家泰国餐厅？泰国餐厅指 food_type = 'thai'；San Pablo Ave Albany 指 street_name = 'san pablo ave' AND T1.city = 'albany'

**查询计划 (Query Plan)**:

** 准备步骤:**
1. 初始化过程：开始准备执行查询。
2. 准备存储：设置用于保存临时结果的存储空间（寄存器），初始化为 NULL。
3. 打开 location 表：打开 location 表以便我们可以从中读取数据。
4. 打开 generalinfo 表：打开 generalinfo 表以便我们可以从中读取数据。

** 匹配餐厅:**
1. 开始读取 location 表：移动到 location 表的第一行。
2. 检查街道是否匹配：查看 location 表当前行的 street_name 列。如果不是 "san pablo ave"，则跳过此行。
3. 检查城市是否匹配 (location 表): 查看 location 表当前行的 city 列。如果不是 "albany"，则跳过此行。 (注意：原提示似乎假设城市在T1，但地址通常在location表，这里根据常识调整计划)
4. 识别匹配的行：存储此 location 条目的标识符 (id_restaurant)。
5. 在 generalinfo 表中查找对应的行：使用来自 location 的 id_restaurant 直接在 generalinfo 表中查找匹配的行。
6. 检查食物类型是否匹配：查看 generalinfo 表中的 food_type 列。如果不是 "thai"，则跳过此行。
7. 检查城市是否匹配 (generalinfo 表): 查看 generalinfo 表中的 city 列。如果不是 "albany"，则跳过此行。（根据表结构，城市信息可能在两个表都存在，需要确认哪个为准，或两者都需满足）

** 统计餐厅:**
1. 准备统计此匹配项：如果所有检查都通过，则准备将此行计入最终计数。
2. 统计此匹配项：对满足所有条件的每一行递增计数。
3. 移动到 location 表的下一行：返回 location 表并移动到下一行，重复该过程，直到检查完所有行。
4. 完成计数：检查完所有行后，完成匹配行的计数。
5. 准备结果：复制最终计数以准备输出。

** 交付结果:**
1. 输出结果：输出最终计数，即满足所有指定条件的餐厅数量。
2. 结束过程：停止查询执行过程。
3. 设置阶段：在开始实际查询执行之前，系统准备要查找的特定值，如 "san pablo ave"、"thai" 和 "albany"。

**最终优化 SQL 查询：**
```sql
SELECT COUNT(T1.id_restaurant)
 FROM `{BQ_PROJECT_ID}.restaurant.generalinfo` AS T1
 INNER JOIN `{BQ_PROJECT_ID}.restaurant.location` AS T2 ON T1.id_restaurant = T2.id_restaurant
 WHERE T1.food_type = 'thai' AND T1.city = 'albany' AND T2.street_name = 'san pablo ave' -- 假设城市需要在 generalinfo 匹配
 -- 如果城市也需要在 location 匹配: AND T2.city = 'albany'
```

===========
示例 2

**************************
【数据库信息】
CREATE TABLE `{BQ_PROJECT_ID}.financial.account` (
   account_id INT64,
   district_id INT64,
   frequency STRING,
   date DATE,
);
CREATE TABLE `{BQ_PROJECT_ID}.financial.client` (
   client_id INT64,
   gender STRING,
   birth_date DATE,
   district_id INT64,
);
CREATE TABLE `{BQ_PROJECT_ID}.financial.district` (
   district_id INT64,
   a4 STRING OPTIONS(description="假设 A4 和 A11 因为示例是字符串类型"),
   a11 STRING OPTIONS(description="平均工资"),
);

**************************
【问题】
Question:
在平均工资最低的分行开户的最年轻客户的性别是什么？已知：出生日期越晚表示年龄越小；A11 指的是平均工资。

**************************
【回答】
重复问题并生成查询计划和 SQL。
**问题**: 在平均工资最低的分行开户的最年轻客户的性别是什么？已知：出生日期越晚表示年龄越小；A11 指的是平均工资。

**查询计划 (Query Plan)**:

** 准备步骤: **
1. 初始化过程：开始设置必要环境以高效执行查询。
2. 打开所需表：访问 client、account 和 district 表以检索相关数据。（注意：account 表在此问题中似乎未使用，可以省略）。
3. 准备临时存储：分配空间以存储中间结果，例如最低平均工资和相应的区域信息。

** 识别平均工资最低的分行: **
1. 扫描 district 表：检索 district 表中的所有记录以分析平均工资。
2. 提取平均工资：对于每个区域，记录 A11 列中的值，该值代表平均工资（需要转换为数字类型）。
3. 确定最低工资：比较所有提取的平均工资以识别最小值。
4. 存储相应的 district_id：记录与最低平均工资关联的 district_id 以供进一步处理。

** 查找已识别区域中的客户: **
1. 连接 client 和 district 表：合并 client.district_id 与 district.district_id 匹配的记录，以将客户与其区域关联。 (注意：这里不需要 account 表)
2. 按 district_id 过滤：仅选择那些 account.district_id (应为 client.district_id) 与先前识别的最低平均工资区域的 district_id 匹配的记录。
3. 处理潜在重复项：确保唯一标识每个客户。

** 识别最年轻的客户: **
1. 提取出生日期：从过滤后的客户记录中，检索每个客户的 birth_date。
2. 确定最晚的出生日期：识别过滤列表中最近（最晚）的出生日期，表示最年轻的客户。
3. 处理出生日期相同的情况：如果多个客户共享相同的最晚出生日期，则按最低平均工资优先排序，如果工资也相同，则随机选择一个或根据其他规则（例如 client_id）。查询中使用 `LIMIT 1` 处理。

** 检索性别信息: **
1. 选择 gender 列：从最年轻客户的记录中，提取 gender 列的值。
2. 准备结果：格式化检索到的性别信息以供呈现，确保清晰和正确。

** 完成并交付结果: **
1. 编译最终结果：将提取的性别信息组织成连贯且易于理解的输出。
2. 清理资源：关闭任何打开的表连接并释放查询执行期间使用的临时存储。
3. 输出结果：呈现平均工资最低分行中最年轻客户的性别。

**最终优化 SQL 查询：**
```sql
SELECT T1.gender
 FROM `{BQ_PROJECT_ID}.financial.client` AS T1
 INNER JOIN `{BQ_PROJECT_ID}.financial.district` AS T2
 ON T1.district_id = T2.district_id
 ORDER BY CAST(T2.A11 AS BIGNUMERIC) ASC, T1.birth_date DESC NULLS LAST -- 按平均工资升序，出生日期降序排序
 LIMIT 1 -- 取第一个结果
```
===========
示例 3

**************************
【数据库信息】
CREATE TABLE `{BQ_PROJECT_ID}.olympics.games`
(
 id INT64,
 games_year INT64 OPTIONS(description="比赛年份"),
 games_name STRING,
);

CREATE TABLE `{BQ_PROJECT_ID}.olympics.games_city`
(
 games_id INT64,
 city_id INT64 OPTIONS(description="举办比赛的城市 ID，映射到 city(id)"),
);

CREATE TABLE `{BQ_PROJECT_ID}.olympics.city`
(
 id INT64,
 city_name STRING,
);

**************************
【问题】
Question:
从 1900 年到 1992 年，伦敦举办了多少场比赛？ 从 1900 年到 1992 年 指 games_year BETWEEN 1900 AND 1992；伦敦 指 city_name = 'London'；比赛 指 games_name；

**************************
【回答】
重复问题并生成查询计划和 SQL。
**问题**: 从 1900 年到 1992 年，伦敦举办了多少场比赛？ 从 1900 年到 1992 年 指 games_year BETWEEN 1900 AND 1992；伦敦 指 city_name = 'London'；比赛 指 games_name；

**查询计划 (Query Plan)**:

** 准备步骤: **
1. 初始化过程：设置环境以开始查询执行，包括必要的变量和临时存储。
2. 打开所需表：打开 games_city、city 和 games 表以访问相关数据。
3. 准备过滤值：设置用于过滤数据的特定值，例如年份范围 (1900-1992) 和城市名称 'London'。

** 过滤并识别相关数据: **
1. 扫描 city 表：查找 city_name 为 'London' 的记录，获取其 id (city_id)。
2. 扫描 games_city 表：使用上一步获得的 city_id 过滤 games_city 表，找到在伦敦举办的比赛的 games_id。
3. 扫描 games 表：使用上一步获得的 games_id 过滤 games 表。

** 按年份范围进一步过滤: **
1. 检查 games_year：对于与 'London' 匹配的比赛记录，检查其 games_year 是否在 1900 到 1992 之间。

** 统计匹配的行: **
1. 初始化计数：准备计算满足所有条件的匹配行数。
2. 统计有效条目：对于满足条件（city_name = 'London' 且 games_year 在 1900 到 1992 之间）的每一行，递增计数。
3. 存储最终计数：处理完所有行后，将总计数存储为最终结果。

** 完成并交付结果: **
1. 准备输出结果：格式化 1900 年至 1992 年间伦敦举办的比赛总数。
2. 输出最终计数：将计数作为查询结果交付。
3. 清理资源：关闭任何打开的表连接并释放查询执行期间使用的临时存储。

**最终优化 SQL 查询：**
```sql
SELECT COUNT(T3.id)
 FROM `{BQ_PROJECT_ID}.olympics.games_city` AS T1
 INNER JOIN `{BQ_PROJECT_ID}.olympics.city` AS T2 ON T1.city_id = T2.id
 INNER JOIN `{BQ_PROJECT_ID}.olympics.games` AS T3 ON T1.games_id = T3.id
 WHERE T2.city_name = 'London' AND T3.games_year BETWEEN 1900 AND 1992
```

===========
示例 4

**************************
【数据库信息】
CREATE TABLE `{BQ_PROJECT_ID}.retails.employees` (
   employee_id INT64,
   department_id INT64,
   salary INT64,
);

**************************
【问题】
Question:
有多少员工的收入超过 $100,000？

**************************
【回答】
重复问题并生成查询计划和 SQL。
**问题：** 有多少员工的收入超过 $100,000？

** 查询计划 (Query Plan)**:

** 准备步骤: **
1. 初始化过程：首先设置查询执行环境，包括初始化变量和临时存储。
2. 打开 employees 表：访问 employees 表以检索相关数据。

** 按工资过滤员工: **
1. 扫描 employees 表：开始读取 employees 表中的行。
2. 获取 salary 列：对于每一行，检索 salary 列的值。
3. 将工资与 $100,000 进行比较：检查工资值是否大于 100,000。
4. 识别匹配的行：对于工资超过 $100,000 的行，准备对这些条目进行计数。

** 统计匹配项: **
1. 初始化计数：设置一个计数器以跟踪有多少员工满足工资条件。
2. 递增计数：对于工资高于 $100,000 的每一行，递增计数器。
3. 存储最终计数：处理完所有行后，存储匹配员工的总数。

** 完成并交付结果: **
1. 准备输出结果：格式化最终计数以供呈现。
2. 输出最终计数：将计数作为查询结果交付，指示有多少员工收入超过 $100,000。
3. 清理资源：关闭 employees 表并释放查询执行期间使用的任何临时存储。

**最终优化 SQL 查询：**
```sql
SELECT COUNT(*) FROM `{BQ_PROJECT_ID}.retails.employees` WHERE salary > 100000;
```

===========
示例 6 (注：示例5与示例4类似，跳过)

**************************
【数据库信息】
CREATE TABLE `{BQ_PROJECT_ID}.airlines.Airlines`
(
 FL_DATE STRING OPTIONS(description="航班日期"),
 ORIGIN STRING OPTIONS(description="始发机场代码"),
 DEST STRING OPTIONS(description="目的地机场代码"),
);

CREATE TABLE `{BQ_PROJECT_ID}.airlines.Airports`
(
 Code STRING OPTIONS(description="机场代码"),
 Description STRING OPTIONS(description="机场描述"),
);

**************************
【问题】
Question:
2018 年 8 月从圣地亚哥国际机场到洛杉矶国际机场有多少航班？
flights from 指 ORIGIN；圣地亚哥国际机场 指 Description = 'San Diego, CA: San Diego International'；flights to 指 DEST；洛杉矶国际机场 指 Description = 'Los Angeles, CA: Los Angeles International'；2018 年 8 月 指 FL_DATE like '2018/8%';

**************************
【回答】
**重复问题并生成查询计划和 SQL。**

**问题**: 2018 年 8 月从圣地亚哥国际机场到洛杉矶国际机场有多少航班？ flights from 指 ORIGIN；圣地亚哥国际机场 指 Description = 'San Diego, CA: San Diego International'；flights to 指 DEST；洛杉矶国际机场 指 Description = 'Los Angeles, CA: Los Angeles International'；2018 年 8 月 指 FL_DATE like '2018/8%';

** 查询计划 (Query Plan)**:

** 准备步骤: **
1. 初始化过程：设置环境并通过初始化变量和临时存储为查询执行做准备。
2. 打开所需表：打开 Airlines 和 Airports 表以访问相关数据。
3. 准备过滤值：设置特定的过滤值，如机场描述和日期模式。

** 识别相关航班: **
1. 查找始发机场代码：在 Airports 表中查找 Description 为 'San Diego, CA: San Diego International' 的记录，获取其 Code。
2. 查找目的地机场代码：在 Airports 表中查找 Description 为 'Los Angeles, CA: Los Angeles International' 的记录，获取其 Code。
3. 扫描 Airlines 表：开始读取 Airlines 表的行。
4. 按始发地过滤：检查当前行的 ORIGIN 是否等于步骤 1 中找到的代码。
5. 按目的地过滤：检查当前行的 DEST 是否等于步骤 2 中找到的代码。
6. 按日期过滤：检查当前行的 FL_DATE 是否匹配 '2018/8/%' 模式（使用 STARTS_WITH）。

** 统计匹配的航班: **
1. 初始化计数：设置一个计数器以跟踪有多少航班满足所有条件。
2. 递增计数：对于每个满足所有条件的航班（从圣地亚哥国际机场出发，目的地为洛杉矶国际机场，且在 2018 年 8 月），递增计数器。
3. 存储最终计数：处理完所有行后，存储匹配航班的总数。

** 完成并交付结果: **
1. 准备输出结果：格式化最终计数以供呈现，确保清晰和正确。
2. 输出最终计数：将计数作为查询结果交付，指示有多少航班满足指定条件。
3. 清理资源：关闭任何打开的表连接并释放查询执行期间使用的临时存储。

**最终优化 SQL 查询：**
```sql
SELECT
  COUNT(T1.FL_DATE)
FROM
  `{BQ_PROJECT_ID}.airlines.Airlines` AS T1
WHERE
  STARTS_WITH(T1.FL_DATE, '2018/8/') -- 假设日期格式以 YYYY/M/ 开头
  AND T1.ORIGIN = ( -- 子查询获取始发机场代码
    SELECT T2.Code
    FROM `{BQ_PROJECT_ID}.airlines.Airports` AS T2
    WHERE T2.Description = 'San Diego, CA: San Diego International'
    LIMIT 1 -- 确保子查询只返回一个值
  )
  AND T1.DEST = ( -- 子查询获取目的地机场代码
    SELECT T3.Code
    FROM `{BQ_PROJECT_ID}.airlines.Airports` AS T3
    WHERE T3.Description = 'Los Angeles, CA: Los Angeles International'
    LIMIT 1 -- 确保子查询只返回一个值
  )

```
-- 注意：原示例中的子查询没有 LIMIT 1，且返回 T2.ORIGIN/T4.DEST 而不是 Code，这在 SQL 语法上可能有问题或效率不高。这里做了修正。

===========
示例 7

**************************
【数据库信息】
CREATE TABLE `{BQ_PROJECT_ID}.food_inspection.businesses`
(
       `business_id` INT64,
       `name` STRING OPTIONS(description="餐馆名称"),
);

CREATE TABLE `{BQ_PROJECT_ID}.food_inspection.inspections`
(
       `business_id` INT64 OPTIONS(description="企业的唯一 ID"),
       `score` INT64 OPTIONS(description="检查得分"),
       `date` DATE,
);

CREATE TABLE `{BQ_PROJECT_ID}.food_inspection.violations`
(
       `business_id` INT64,
       `date` DATE,
);

**************************
【问题】
Question:
连续 4 年达到所有规定标准的餐馆名称是什么？
establishment 与 business 含义相同；得分 90 或以上 指 score ≥ 90；year(date) = 2015；；连续 4 年达到所有规定标准 指 COUNT(year(date)) = 4 where score = 100；

**************************
【回答】
重复问题并生成查询计划和 SQL。

**问题**: 连续 4 年达到所有规定标准的餐馆名称是什么？ establishment 与 business 含义相同；得分 90 或以上 指 score ≥ 90；year(date) = 2015；；连续 4 年达到所有规定标准 指 COUNT(year(date)) = 4 where score = 100；

** 查询计划 (Query Plan)**:

** 准备步骤: **
1. 初始化过程：设置环境并为查询执行做准备，包括初始化变量和临时存储。
2. 打开所需表：打开 businesses 和 inspections 表以访问相关数据。（violations 表未使用）

** 过滤并识别相关检查记录: **
1. 扫描 inspections 表：开始读取 inspections 表中的行。
2. 按 100 分过滤：仅选择 score 为 100 的检查记录。
3. 提取检查年份：使用 `EXTRACT(YEAR FROM date)` 函数从检查日期中提取年份。
4. 去除重复：确保每个企业每年只考虑一次 100 分的记录（使用 DISTINCT）。

** 识别连续 4 年达标的企业: **
1. 按企业分组并排序：将上一步的结果按 `business_id` 分组，并按 `inspection_year` 排序。
2. 分配行号：使用 `ROW_NUMBER()` 窗口函数，在每个 `business_id` 分区内，按年份升序为记录分配行号。
3. 计算年份组：计算 `inspection_year - 行号`。对于连续的年份，这个差值是恒定的。
4. 按企业和年份组聚合：按 `business_id` 和计算出的 `year_group` 分组。
5. 筛选连续 4 年：使用 `HAVING COUNT(*) >= 4` 找出那些在同一个 `year_group` 中有 4 条或更多记录的企业，这些企业即为连续 4 年达标的企业。获取这些企业的 `business_id`。

** 获取企业名称: **
1. 连接 businesses 表：将上一步得到的 `business_id` 列表与 businesses 表进行连接。
2. 选择名称：选择匹配的 `business_id` 对应的 `name`。
3. 去除重复名称：使用 `DISTINCT` 确保每个企业名称只输出一次。

** 完成并交付结果: **
1. 准备输出结果：格式化最终的企业名称列表。
2. 输出最终结果：交付连续 4 年达到标准的餐馆名称。
3. 清理资源：关闭任何打开的表连接并释放临时存储。

**最终优化 SQL 查询：**
```sql
WITH ScoredYears AS (
  -- 步骤 2 & 3: 过滤得分为 100 的记录并提取年份，去重
  SELECT DISTINCT
    business_id,
    EXTRACT(YEAR FROM date) AS inspection_year
  FROM
    `{BQ_PROJECT_ID}.food_inspection.inspections`
  WHERE
    score = 100
),
RankedYears AS (
  -- 步骤 4: 分配行号并计算年份组
  SELECT
    business_id,
    inspection_year,
    inspection_year - ROW_NUMBER() OVER (PARTITION BY business_id ORDER BY inspection_year) AS year_group
  FROM
    ScoredYears
),
ConsecutiveBusinesses AS (
  -- 步骤 5: 找到连续 4 年或以上达标的企业 ID
  SELECT
    business_id
  FROM
    RankedYears
  GROUP BY
    business_id,
    year_group
  HAVING
    COUNT(*) >= 4
)
-- 步骤 6 & 7: 获取企业名称并去重
SELECT DISTINCT
  T2.name
FROM
  `{BQ_PROJECT_ID}.food_inspection.businesses` AS T2
INNER JOIN
  ConsecutiveBusinesses AS T3
ON
  T2.business_id = T3.business_id;
```

===========
示例 8

**************************
【数据库信息】
CREATE TABLE `bigquery-public-data.covid19_symptom_search.symptom_search_sub_region_2_daily`
(
  country_region_code STRING,
  country_region STRING,
  sub_region_1 STRING,
  sub_region_1_code STRING,
  sub_region_2 STRING,
  sub_region_2_code STRING,
  place_id STRING,
  date DATE,
  symptom_Abdominal_obesity FLOAT64, -- 腹型肥胖症状搜索指数
  symptom_Abdominal_pain FLOAT64, -- 腹痛症状搜索指数
  symptom_Acne FLOAT64, -- 痤疮症状搜索指数
  symptom_Headache FLOAT64 -- 假设存在头痛症状列
)
PARTITION BY date
CLUSTER BY country_region_code, sub_region_1_code, sub_region_2_code, sub_region_2;

-- 假设国家层级表结构
CREATE TABLE `bigquery-public-data.covid19_symptom_search.symptom_search_country_daily`
(
  country_region_code STRING,
  country_region STRING,
  date DATE,
  symptom_Headache FLOAT64 -- 头痛症状搜索指数
)
PARTITION BY date
CLUSTER BY country_region_code;


**************************
【问题】
Question:
找出头痛症状最常出现的是星期几？

**************************
【回答】
重复问题并生成查询计划和 SQL。

**问题**: 找出头痛症状最常出现的是星期几？

** 查询计划 (Query Plan)**:

** 准备步骤 : **
1. 初始化过程：设置环境并准备查询执行，包括初始化变量和临时存储。
2. 打开 symptom_search_country_daily 表：访问包含每日国家级症状搜索数据的表。（根据最终查询选择此表）

** 提取日期和头痛数据: **
1. 扫描表：开始读取 symptom_search_country_daily 表中的行。
2. 提取日期：获取 `date` 列的值。
3. 提取头痛数据：获取 `symptom_Headache` 列的值（如果需要按频率计算，则获取此值；如果按出现次数，则只需知道此行存在）。

** 按星期几聚合: **
1. 计算星期几：对于每一行，使用 `FORMAT_DATE('%A', date)` 计算星期几。
2. 分组：按计算出的星期几进行分组。
3. 聚合计数：计算每个星期几分组中的行数（使用 `COUNT(*)`）或头痛频率总和（使用 `SUM(symptom_Headache)`）。本例遵循示例使用 `COUNT(*)`。

** 按频率排序并选择最高项: **
1. 排序：将聚合结果按计算出的计数（或总频率）降序排列。
2. 限制：只选择排序后的第一行，即出现次数（或频率）最高的星期几。

** 完成并交付结果: **
1. 准备输出结果：格式化最终的星期几名称。
2. 输出最终结果：交付头痛症状最常出现的星期几。
3. 清理资源：关闭表连接并释放临时存储。

**最终优化 SQL 查询：**
```sql
SELECT
  FORMAT_DATE('%A', date) AS day, -- 提取星期几名称
  COUNT(*) AS headache_occurrence_count -- 计算每个星期几的记录数
FROM
  `bigquery-public-data.covid19_symptom_search.symptom_search_country_daily`
GROUP BY
  day -- 按星期几分组
ORDER BY
  headache_occurrence_count DESC -- 按记录数降序排序
LIMIT 1; -- 取出现次数最多的那一天
```
-- 注意：原示例中包含 PARSE_DATE('%Y-%m-%d', date)，这表明原始 date 列可能是 STRING 类型。如果 date 列确实是 DATE 类型，则不需要 PARSE_DATE。这里假设它是 DATE 类型，与表定义一致。如果它是 STRING，则需要 PARSE_DATE。

现在是实际问题，遵循说明和示例，使用查询计划引导的方法生成 GoogleSQL。
遵循策略的所有步骤。当您得到最终查询时，仅以 ```sql ... ``` 的格式输出查询字符串。确保只输出一个查询。

**************************
【表创建语句】
{SCHEMA}

**************************
【问题】
Question:
{QUESTION}

**************************
【回答】
重复问题并生成查询计划和 SQL。
"""


