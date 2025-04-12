
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

"""分而治之 (Divide-and-Conquer, DC) Prompt 模板。"""

DC_PROMPT_TEMPLATE = """
您是一位经验丰富的数据库专家。
现在，您需要根据提供的数据库信息、一个问题和一些附加信息，生成一个 GoogleSQL 或 BigQuery 查询。
数据库结构由表模式定义（有些列在选项中提供了额外的列描述）。

给定表模式信息描述和 `Question`（问题）。您将获得表的创建语句，您需要理解数据库和列。

您将使用一种称为“从自然语言递归分而治之生成 SQL 查询”的方法。

以下是该方法步骤的高级描述：
1.  **分解（使用伪 SQL 分解子问题）：** 将复杂的自然语言问题递归地分解为更简单的子问题。每个子问题针对最终 SQL 查询所需的特定信息或逻辑。
2.  **解决（为子问题生成真实 SQL）：** 为每个子问题（以及最初的主问题）构建一个“伪 SQL”片段。这个伪 SQL 代表了预期的 SQL 逻辑，但可能包含用于分解子问题答案的占位符。
3.  **合并（重新组装）：** 一旦所有子问题都得到解决并生成了相应的 SQL 片段，过程将反向进行。通过将伪 SQL 中的占位符替换为从较低级别生成的实际 SQL，递归地合并 SQL 片段。
4.  **最终输出：** 这种自下而上的组装最终形成完整且正确的 SQL 查询，以回答原始的复杂问题。

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
重复问题并使用递归分而治之生成 SQL。
**问题**: 在 Albany 的 San Pablo Ave 有多少家泰国餐厅？泰国餐厅指 food_type = 'thai'；San Pablo Ave Albany 指 street_name = 'san pablo ave' AND T1.city = 'albany'

**1. 分解与解决 (Divide and Conquer):**

*   **主问题：** 在 Albany 的 San Pablo Ave 有多少家泰国餐厅？
    *   **分析：** 问题要求统计餐厅数量，因此我们将使用 `COUNT()`。计数应仅包括泰国餐厅，我们可以使用 `restaurant.generalinfo` 表中的 `food_type` 列来识别。地点 "San Pablo Ave, Albany" 涉及 `restaurant.location` 表中的两列（`street_name` 和 `city`），需要连接这两个表。
    *   **伪 SQL：** SELECT COUNT(`T1`.`id_restaurant`) FROM `{BQ_PROJECT_ID}.restaurant.generalinfo` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.restaurant.location` AS `T2` ON `T1`.`id_restaurant` = `T2`.`id_restaurant` WHERE <是泰国餐厅> AND <在 San Pablo Ave, Albany>

    *   **子问题 1：** 是泰国餐厅
        *   **分析：** 这是对 `restaurant.generalinfo` 表使用 `food_type` 列的直接过滤。
        *   **伪 SQL：** `T1`.`food_type` = 'thai'

    *   **子问题 2：** 在 San Pablo Ave, Albany
        *   **分析：** 这个位置信息分布在 `restaurant.location` 表的两列中。我们需要使用 "AND" 运算符组合这些条件以确保两者都满足。
        *   **伪 SQL：** `T2`.`street_name` = 'san pablo ave' AND `T2`.`city` = 'albany'

**2. 组装 SQL：**

*   **子问题 1 (是泰国餐厅)：**
    *   **SQL：** `T1`.`food_type` = 'thai'

*   **子问题 2 (在 San Pablo Ave, Albany)：**
    *   **SQL：** `T2`.`street_name` = 'san pablo ave' AND `T2`.`city` = 'albany'

*   **主问题 (统计餐厅数量)：**
    *   **SQL：** SELECT COUNT(`T1`.`id_restaurant`) FROM `{BQ_PROJECT_ID}.restaurant.generalinfo` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.restaurant.location` AS `T2` ON `T1`.`id_restaurant` = `T2`.`id_restaurant` WHERE `T1`.`food_type` = 'thai' AND `T2`.`street_name` = 'san pablo ave' AND `T2`.`city` = 'albany'

**3. 简化与优化：**

*   步骤 2 中的 SQL 查询已经相当高效。我们使用了 `INNER JOIN` 根据它们的关系来组合表，并且 `WHERE` 子句清晰地定义了我们的过滤标准。在这种情况下，不需要嵌套查询或复杂的子选择。注意：在原始示例中 `T1.city = 'albany'` 条件似乎更合适放在 `T1` 上，如果 `location` 表中的 `city` 只是外键描述的一部分，那么最终优化后的 SQL 如下。如果 `location` 表的 `city` 也需要匹配，则原始的 SQL 即可。假设 `generalinfo` 表的 `city` 是主要依据。

**最终优化 SQL 查询：**
```sql
SELECT COUNT(T1.id_restaurant)
 FROM `{BQ_PROJECT_ID}.restaurant.generalinfo` AS T1
 INNER JOIN `{BQ_PROJECT_ID}.restaurant.location` AS T2 ON T1.id_restaurant = T2.id_restaurant
 WHERE T1.food_type = 'thai' AND T1.city = 'albany' AND T2.street_name = 'san pablo ave'
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
重复问题并使用递归分而治之生成 SQL。
**问题**: 在平均工资最低的分行开户的最年轻客户的性别是什么？已知：出生日期越晚表示年龄越小；A11 指的是平均工资。

**1. 分解与解决 (Divide and Conquer):**

*   **主问题：** 在平均工资最低的分行开户的最年轻客户的性别是什么？
    *   **分析：** 问题询问的是 `gender`（性别），它出现在 `financial.client` 表中。我们将使用它作为输出列，从平均工资最低的分行中最年轻的客户中选择。
    *   **伪 SQL：** SELECT `T1`.`gender` FROM `{BQ_PROJECT_ID}.financial.client` AS `T1` WHERE <是平均工资最低分行中最年轻的客户>

    *   **子问题 1：** 平均工资最低分行中最年轻的客户
        *   **分析：** 根据提示，我们需要使用 `financial.district` 表中的 `A11` 来获取工资信息，并且最年轻的客户可以通过 `financial.client` 表的 `birth_date` 列来确定。这两个表可以通过 `district_id` 进行 INNER JOIN 连接。我们需要按平均工资 (`A11`) 升序和出生日期 (`birth_date`) 降序排序，然后取第一个。
        *   **伪 SQL：** SELECT `T1`.`client_id` FROM `{BQ_PROJECT_ID}.financial.client` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.financial.district` AS `T2` ON `T1`.`district_id` = `T2`.`district_id` WHERE <在平均工资最低的分行> ORDER BY `T1`.`birth_date` DESC NULLS LAST LIMIT 1

        *   **子问题 1.1：** 平均工资最低的分行
            *   **分析：** 我们可以通过按 `A11` 升序排序并取前 1 名来获得平均工资最低的分行。`A11` 列不可为空，因此我们不需要添加 "IS NOT NULL" 过滤器。
            *   **伪 SQL：** SELECT `district_id` FROM `{BQ_PROJECT_ID}.financial.district` ORDER BY `A11` ASC LIMIT 1

**2. 组装 SQL：**

*   **子问题 1.1 (平均工资最低的分行)：**
    *   **SQL：** SELECT `district_id` FROM `{BQ_PROJECT_ID}.financial.district` ORDER BY CAST(`A11` AS BIGNUMERIC) ASC LIMIT 1 -- 假设 A11 需要转换为数字类型进行排序

*   **子问题 1 (平均工资最低分行中最年轻的客户)：**
    *   **SQL：** SELECT `T1`.`client_id` FROM `{BQ_PROJECT_ID}.financial.client` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.financial.district` AS `T2` ON `T1`.`district_id` = `T2`.`district_id` WHERE `T2`.`district_id` = (SELECT `district_id` FROM `{BQ_PROJECT_ID}.financial.district` ORDER BY CAST(`A11` AS BIGNUMERIC) ASC LIMIT 1) ORDER BY `T1`.`birth_date` DESC NULLS LAST LIMIT 1

*   **主问题 (客户的性别)：**
    *   **SQL：** SELECT `T1`.`gender` FROM `{BQ_PROJECT_ID}.financial.client` AS `T1` WHERE `T1`.`client_id` = (SELECT `T1`.`client_id` FROM `{BQ_PROJECT_ID}.financial.client` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.financial.district` AS `T2` ON `T1`.`district_id` = `T2`.`district_id` WHERE `T2`.`district_id` = (SELECT `district_id` FROM `{BQ_PROJECT_ID}.financial.district` ORDER BY CAST(`A11` AS BIGNUMERIC) ASC LIMIT 1) ORDER BY `T1`.`birth_date` DESC NULLS LAST LIMIT 1)

**3. 简化与优化：**

*   步骤 2 中的最终 SQL 查询可以进行简化和优化。嵌套查询可以通过单个 `INNER JOIN` 进行组合，并且过滤可以在单个 `ORDER BY` 子句内完成。

**最终优化 SQL 查询：**
```sql
SELECT T1.gender
 FROM `{BQ_PROJECT_ID}.financial.client` AS T1
 INNER JOIN `{BQ_PROJECT_ID}.financial.district` AS T2
 ON T1.district_id = T2.district_id
 ORDER BY CAST(T2.A11 AS BIGNUMERIC) ASC, T1.birth_date DESC NULLS LAST
 LIMIT 1
```
===========
示例 3 (分解为两个并行的子问题)

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
重复问题并使用递归分而治之生成 SQL。
**问题**: 从 1900 年到 1992 年，伦敦举办了多少场比赛？ 从 1900 年到 1992 年 指 games_year BETWEEN 1900 AND 1992；伦敦 指 city_name = 'London'；比赛 指 games_name；

**1. 分解与解决 (Divide and Conquer):**

*   **主问题：** 从 1900 年到 1992 年，伦敦举办了多少场比赛？
    *   **分析：** 问题要求我们统计比赛数量，这些比赛由 `olympics.games` 表中的 `id` 列表示。我们需要根据两个标准过滤这些比赛：它们在伦敦举办并且发生在 1900 年到 1992 年之间。
    *   **伪 SQL：** SELECT COUNT(`T1`.`id`) FROM `{BQ_PROJECT_ID}.olympics.games` AS `T1` WHERE <比赛在伦敦举行> AND <比赛年份在 1900 到 1992 之间>

    *   **子问题 1：** 比赛在伦敦举行
        *   **分析：** 为了确定哪些比赛在伦敦举办，我们需要将 `olympics.games` 表与 `olympics.games_city` 表通过 `games_id` 连接，然后与 `city` 表通过 `city_id` 连接。我们将使用 `INNER JOIN` 来确保只考虑匹配的记录。对 'London' 的过滤将应用于 `city_name` 列。
        *   **伪 SQL：** `T1`.`id` IN (SELECT `T1`.`games_id` FROM `{BQ_PROJECT_ID}.olympics.games_city` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.olympics.city` AS `T2` ON `T1`.`city_id` = `T2`.`id` WHERE `T2`.`city_name` = 'London')

    *   **子问题 2：** 比赛年份在 1900 到 1992 之间
        *   **分析：** 这涉及到直接根据 `games_year` 列使用 `BETWEEN` 运算符过滤 `olympics.games` 表。
        *   **伪 SQL：** `T1`.`games_year` BETWEEN 1900 AND 1992

**2. 组装 SQL：**

*   **子问题 1 (比赛在伦敦举行)：**
    *   **SQL：** `T1`.`id` IN (SELECT `T1`.`games_id` FROM `{BQ_PROJECT_ID}.olympics.games_city` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.olympics.city` AS `T2` ON `T1`.`city_id` = `T2`.`id` WHERE `T2`.`city_name` = 'London')

*   **子问题 2 (比赛年份在 1900 到 1992 之间)：**
    *   **SQL：** `T1`.`games_year` BETWEEN 1900 AND 1992

*   **主问题 (统计比赛数量)：**
    *   **SQL：** SELECT COUNT(`T1`.`id`) FROM `{BQ_PROJECT_ID}.olympics.games` AS `T1` WHERE `T1`.`id` IN (SELECT `T1`.`games_id` FROM `{BQ_PROJECT_ID}.olympics.games_city` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.olympics.city` AS `T2` ON `T1`.`city_id` = `T2`.`id` WHERE `T2`.`city_name` = 'London') AND `T1`.`games_year` BETWEEN 1900 AND 1992

**3. 简化与优化：**

*   嵌套查询可以转换为更高效的 `JOIN` 操作。我们将使用 `INNER JOIN` 根据它们之间的关系组合 `{BQ_PROJECT_ID}.olympics.games`, `{BQ_PROJECT_ID}.olympics.games_city`, 和 `{BQ_PROJECT_ID}.olympics.city`。

**最终优化 SQL 查询：**
```sql
SELECT COUNT(T3.id)
 FROM `{BQ_PROJECT_ID}.olympics.games_city` AS T1
 INNER JOIN `{BQ_PROJECT_ID}.olympics.city` AS T2 ON T1.city_id = T2.id
 INNER JOIN `{BQ_PROJECT_ID}.olympics.games` AS T3 ON T1.games_id = T3.id
 WHERE T2.city_name = 'London' AND T3.games_year BETWEEN 1900 AND 1992
```

===========
示例 4 (当不清楚应该使用哪个列进行字符串匹配时，使用宽松条件，例如字符串 LIKE 和 OR 条件来覆盖多个可能的列。)

**************************
【数据库信息】
CREATE TABLE `{BQ_PROJECT_ID}.academics.student_programs` (
   `Program Type` STRING, -- 假设是项目类型
   `Participants (Ages 10-15)` FLOAT64, -- 参与者（10-15岁）
   `Total Enrollment (Ages 10-15)` FLOAT64, -- 总入学人数（10-15岁）
   `School Category` STRING, -- 学校类别
);

**************************
【问题】
Question:
请列出在线项目中 10-15 岁学生的最低三个参与率。10-15 岁学生的参与率 = `Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)`

**************************
【回答】
重复问题并使用递归分而治之生成 SQL。
**问题：** 请列出在线项目中 10-15 岁学生的最低三个参与率。10-15 岁学生的参与率 = `Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)`

**1. 分解与解决 (Divide and Conquer):**

*   **主问题：** 请列出在线项目中 10-15 岁学生的最低三个参与率。
    *   **分析：** 问题要求计算 `Participants (Ages 10-15)` 与 `Total Enrollment (Ages 10-15)` 之间的比率。我们需要过滤数据，只包括在线项目，并按参与率升序排序，取前三个非空结果。
    *   **伪 SQL：** SELECT (`Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)`) FROM `{BQ_PROJECT_ID}.academics.student_programs` WHERE <是在线项目> ORDER BY (`Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)`) ASC NULLS LAST LIMIT 3

    *   **子问题 1：** 是在线项目
        *   **分析：** 我们将从 `{BQ_PROJECT_ID}.academics.student_programs` 表中获取信息。需要确定哪个列包含“在线”信息。
        *   **伪 SQL：** SELECT <主键或唯一标识符> FROM `{BQ_PROJECT_ID}.academics.student_programs` WHERE <在线项目的条件>

        *   **子问题 1.1：** 在线项目的条件（注意：这需要外部知识或数据库模式信息。我们需要识别哪个/哪些列指示“在线项目”。）
            *   **分析：** 我们假设 "School Category" 或 "Program Type" 列可能包含术语 "online"。使用 LIKE 和 OR 进行模糊匹配，并转换为小写以忽略大小写。
            *   **伪 SQL：** LOWER(`School Category`) LIKE '%online%' OR LOWER(`Program Type`) LIKE '%online%'

**2. 组装 SQL：**

*   **子问题 1.1 (在线项目的条件)：**
    *   **SQL：** LOWER(`School Category`) LIKE '%online%' OR LOWER(`Program Type`) LIKE '%online%'

*   **子问题 1 (是在线项目)：**
    *   **SQL：** SELECT <主键或唯一标识符> FROM `{BQ_PROJECT_ID}.academics.student_programs` WHERE LOWER(`School Category`) LIKE '%online%' OR LOWER(`Program Type`) LIKE '%online%' -- 假设存在 program_id 作为主键

*   **主问题 (最低三个参与率)：**
    *   **SQL：** SELECT (`Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)`) AS participation_rate FROM `{BQ_PROJECT_ID}.academics.student_programs` WHERE (LOWER(`School Category`) LIKE '%online%' OR LOWER(`Program Type`) LIKE '%online%') AND (`Total Enrollment (Ages 10-15)` IS NOT NULL AND `Total Enrollment (Ages 10-15)` != 0) ORDER BY participation_rate ASC NULLS LAST LIMIT 3 -- 增加了分母不为0且不为NULL的检查

**3. 简化与优化：**

*   我们可以将在线项目的条件直接合并到主查询的 WHERE 子句中。同时，为了避免除以零或 NULL 的错误，需要添加相应的检查。

**最终优化 SQL 查询：**
```sql
SELECT
  `Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)` AS participation_rate
FROM
  `{BQ_PROJECT_ID}.academics.student_programs`
WHERE
  (LOWER(`School Category`) LIKE '%online%' OR LOWER(`Program Type`) LIKE '%online%')
  AND `Total Enrollment (Ages 10-15)` IS NOT NULL AND `Total Enrollment (Ages 10-15)` != 0 -- 确保分母有效
ORDER BY
  participation_rate ASC NULLS LAST -- NULLS LAST 确保空值排在最后
LIMIT 3;
```

===========
示例 5

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
重复问题并使用递归分而治之生成 SQL。
**问题：** 有多少员工的收入超过 $100,000？

**1. 分解与解决 (Divide and Conquer):**

*   **主问题：** 有多少员工的收入超过 $100,000？
    *   **分析：** 问题要求计算员工数量（COUNT）。我们需要过滤数据，只包括收入超过 $100,000 的员工。
    *   **伪 SQL：** SELECT COUNT(*) FROM `{BQ_PROJECT_ID}.retails.employees` WHERE <收入超过 100000 的员工>

    *   **子问题 1：** 收入超过 100000 的员工
        *   **分析：** 对 `salary` 列的简单条件判断。
        *   **伪 SQL：** SELECT employee_id FROM `{BQ_PROJECT_ID}.retails.employees` WHERE salary > 100000

**2. 组装 SQL：**

*   **子问题 1 (收入超过 100000 的员工)：**
    *   **SQL：** SELECT employee_id FROM `{BQ_PROJECT_ID}.retails.employees` WHERE salary > 100000

*   **主问题 (统计员工数量)：**
    *   **SQL：** SELECT COUNT(*) FROM `{BQ_PROJECT_ID}.retails.employees` WHERE employee_id IN (SELECT employee_id FROM `{BQ_PROJECT_ID}.retails.employees` WHERE salary > 100000)

**3. 简化与优化：**

*   我们可以通过单个 WHERE 子句更有效地实现相同的结果。

**最终优化 SQL 查询：**
```sql
SELECT COUNT(*) FROM `{BQ_PROJECT_ID}.retails.employees` WHERE salary > 100000;
```

===========
示例 6

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
flights from 指 ORIGIN；圣地亚哥国际机场 指 Description = 'San Diego, CA: San Diego International'；flights to 指 DEST；洛杉矶国际机场 指 Description = 'Los Angeles, CA: Los Angeles International'；2018 年 8 月 指 FL_DATE like '2018/8%'；

**************************
【回答】
**重复问题并使用递归分而治之生成 SQL。**

**问题**: 2018 年 8 月从圣地亚哥国际机场到洛杉矶国际机场有多少航班？ flights from 指 ORIGIN；圣地亚哥国际机场 指 Description = 'San Diego, CA: San Diego International'；flights to 指 DEST；洛杉矶国际机场 指 Description = 'Los Angeles, CA: Los Angeles International'；2018 年 8 月 指 FL_DATE like '2018/8%'；

**1. 分解与解决 (Divide and Conquer):**

*   **主问题：** 2018 年 8 月从圣地亚哥国际机场到洛杉矶国际机场有多少航班？
    *   **分析：** 问题要求统计航班数量，可以通过计算 `airlines.Airlines` 表中的 `FL_DATE` 条目来获得。我们需要应用三个过滤器：从圣地亚哥国际机场起飞的航班，目的地为洛杉矶国际机场的航班，以及发生在 2018 年 8 月的航班。需要连接 `Airlines` 和 `Airports` 表来通过机场描述过滤。
    *   **伪 SQL：** SELECT COUNT(`FL_DATE`) FROM `{BQ_PROJECT_ID}.airlines.Airlines` WHERE <航班在 2018 年 8 月> AND <航班从圣地亚哥国际机场起飞> AND <航班飞往洛杉矶国际机场>

    *   **子问题 1：** 航班在 2018 年 8 月
        *   **分析：** 这个过滤器可以直接应用于 `{BQ_PROJECT_ID}.airlines.Airlines` 表，使用 `FL_DATE` 列和 `LIKE` 运算符，根据证据提示。假设 `FL_DATE` 格式为 'YYYY/M/D' 或类似。
        *   **伪 SQL：** `FL_DATE` LIKE '2018/8/%' -- 假设日期格式包含日，使用通配符 %

    *   **子问题 2：** 航班从圣地亚哥国际机场起飞
        *   **分析：** 我们需要从 `{BQ_PROJECT_ID}.airlines.Airports` 表中找到对应 'San Diego, CA: San Diego International' 的机场代码 (`Code`)，并用它来过滤 `airlines.Airlines` 表的 `ORIGIN` 列。这需要子查询或 JOIN。
        *   **伪 SQL：** `ORIGIN` IN (SELECT `Code` FROM `{BQ_PROJECT_ID}.airlines.Airports` WHERE `Description` = 'San Diego, CA: San Diego International')

    *   **子问题 3：** 航班飞往洛杉矶国际机场
        *   **分析：** 与子问题 2 类似，我们需要找到 'Los Angeles, CA: Los Angeles International' 的机场代码 (`Code`)，并用它来过滤 `airlines.Airlines` 表的 `DEST` 列。
        *   **伪 SQL：** `DEST` IN (SELECT `Code` FROM `{BQ_PROJECT_ID}.airlines.Airports` WHERE `Description` = 'Los Angeles, CA: Los Angeles International')

**2. 组装 SQL：**

*   **子问题 1 (航班在 2018 年 8 月)：**
    *   **SQL：** STARTS_WITH(`FL_DATE`, '2018/8/') -- 使用 BigQuery 的 STARTS_WITH 函数可能更精确

*   **子问题 2 (航班从圣地亚哥国际机场起飞)：**
    *   **SQL：** `ORIGIN` IN (SELECT `Code` FROM `{BQ_PROJECT_ID}.airlines.Airports` WHERE `Description` = 'San Diego, CA: San Diego International')

*   **子问题 3 (航班飞往洛杉矶国际机场)：**
    *   **SQL：** `DEST` IN (SELECT `Code` FROM `{BQ_PROJECT_ID}.airlines.Airports` WHERE `Description` = 'Los Angeles, CA: Los Angeles International')

*   **主问题 (统计航班数量)：**
    *   **SQL：** SELECT COUNT(`FL_DATE`) FROM `{BQ_PROJECT_ID}.airlines.Airlines` WHERE STARTS_WITH(`FL_DATE`, '2018/8/') AND `ORIGIN` IN (SELECT `Code` FROM `{BQ_PROJECT_ID}.airlines.Airports` WHERE `Description` = 'San Diego, CA: San Diego International') AND `DEST` IN (SELECT `Code` FROM `{BQ_PROJECT_ID}.airlines.Airports` WHERE `Description` = 'Los Angeles, CA: Los Angeles International')

**3. 简化与优化：**

*   步骤 2 中的查询使用了子查询，这通常是可接受的。如果需要进一步优化（例如，如果 Airports 表很大），可以考虑使用 JOIN。但对于这种查找特定代码的情况，子查询通常足够高效。

**最终优化 SQL 查询：**
```sql
SELECT
  COUNT(T1.FL_DATE)
FROM
  `{BQ_PROJECT_ID}.airlines.Airlines` AS T1
WHERE
  STARTS_WITH(T1.FL_DATE, '2018/8/') -- 假设日期格式为 'YYYY/MM/DD' 或 'YYYY/M/D'
  AND T1.ORIGIN IN (
    SELECT T2.Code
    FROM `{BQ_PROJECT_ID}.airlines.Airports` AS T2
    WHERE T2.Description = 'San Diego, CA: San Diego International'
  )
  AND T1.DEST IN (
    SELECT T3.Code
    FROM `{BQ_PROJECT_ID}.airlines.Airports` AS T3
    WHERE T3.Description = 'Los Angeles, CA: Los Angeles International'
  )
```

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

CREATE TABLE `{BQ_PROJECT_ID}.food_inspection.violations` -- 注意：此表示例中未使用，但包含在模式信息中
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
重复问题并使用递归分而治之生成 SQL。

**问题**: 连续 4 年达到所有规定标准的餐馆名称是什么？ establishment 与 business 含义相同；得分 90 或以上 指 score ≥ 90；year(date) = 2015；；连续 4 年达到所有规定标准 指 COUNT(year(date)) = 4 where score = 100；

**1. 分解与解决 (Divide and Conquer):**

*   **主问题：** 连续 4 年达到所有规定标准的餐馆名称是什么？
    *   **分析：** 我们需要找到连续 4 年得分均为 100 的企业的名称。`food_inspection.businesses` 表包含 `name`，`food_inspection.inspections` 表包含 `score` 和 `date`。我们需要连接这两个表，按 `score` 过滤。要检查连续年份，我们需要按企业和年份分组，然后检查每个组的计数是否为 4，并且这些年份是连续的。
    *   **伪 SQL：** SELECT DISTINCT `T2`.`name` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.food_inspection.businesses` AS `T2` ON `T1`.`business_id` = `T2`.`business_id` WHERE <得分 = 100> AND <连续 4 年>

    *   **子问题 1：** 得分 = 100
        *   **分析：** 这是对 `{BQ_PROJECT_ID}.food_inspection.inspections` 表的简单过滤，选择 `score` 为 100 的行。
        *   **伪 SQL：** `T1`.`score` = 100

    *   **子问题 2：** 连续 4 年
        *   **分析：** 这比较复杂。我们需要按企业 (`business_id`) 和年份 (`EXTRACT(YEAR FROM date)`) 分组，筛选出得分为 100 的年份。然后，对于每个企业，检查是否存在连续 4 年的记录。可以使用窗口函数（如 `LAG` 或 `ROW_NUMBER`）和自连接，或者通过聚合和检查年份差来实现。一种方法是计算每个企业获得 100 分的年份，然后找到年份与其排名之差 (`year - rank`) 相同的组，如果这样的组大小达到 4，则表示连续 4 年。
        *   **伪 SQL：** `T2`.`business_id` IN (SELECT `business_id` FROM (SELECT `business_id`, `inspection_year`, `inspection_year` - ROW_NUMBER() OVER (PARTITION BY `business_id` ORDER BY `inspection_year`) AS `year_group` FROM (SELECT DISTINCT `business_id`, EXTRACT(YEAR FROM `date`) AS `inspection_year` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` WHERE `score` = 100)) GROUP BY `business_id`, `year_group` HAVING COUNT(*) >= 4)

        *   **子问题 2.1：** 获取得分 100 的不同企业及其检查年份
            *   **分析：** 从 `{BQ_PROJECT_ID}.food_inspection.inspections` 表中筛选 `score` = 100 的记录，并选择不同的 `business_id` 和检查年份。
            *   **伪 SQL：** SELECT DISTINCT `business_id`, EXTRACT(YEAR FROM `date`) AS `inspection_year` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` WHERE `score` = 100

        *   **子问题 2.2：** 为每个企业的年份分配排名并计算年份组标识
            *   **分析：** 使用 `ROW_NUMBER()` 窗口函数按年份为每个企业内的检查记录分配排名。然后计算 `inspection_year - rank`，这个值对于连续年份的组是恒定的。
            *   **伪 SQL：** SELECT `business_id`, `inspection_year`, `inspection_year` - ROW_NUMBER() OVER (PARTITION BY `business_id` ORDER BY `inspection_year`) AS `year_group` FROM (子问题 2.1 的结果)

        *   **子问题 2.3：** 按企业和年份组分组，并检查计数是否达到 4
            *   **分析：** 按 `business_id` 和 `year_group` 分组，并使用 `HAVING COUNT(*) >= 4` 来筛选出那些至少连续 4 年得分为 100 的企业。
            *   **伪 SQL：** SELECT `business_id` FROM (子问题 2.2 的结果) GROUP BY `business_id`, `year_group` HAVING COUNT(*) >= 4

**2. 组装 SQL：**

*   **子问题 2.1 (得分 100 的不同企业和年份)：**
    *   **SQL：** SELECT DISTINCT `business_id`, EXTRACT(YEAR FROM `date`) AS `inspection_year` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` WHERE `score` = 100

*   **子问题 2.2 (分配排名并计算年份组)：**
    *   **SQL：** SELECT `business_id`, `inspection_year`, `inspection_year` - ROW_NUMBER() OVER (PARTITION BY `business_id` ORDER BY `inspection_year`) AS `year_group` FROM (SELECT DISTINCT `business_id`, EXTRACT(YEAR FROM `date`) AS `inspection_year` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` WHERE `score` = 100)

*   **子问题 2.3 (按企业和年份组分组并检查计数)：**
    *   **SQL：** SELECT `business_id` FROM (SELECT `business_id`, `inspection_year`, `inspection_year` - ROW_NUMBER() OVER (PARTITION BY `business_id` ORDER BY `inspection_year`) AS `year_group` FROM (SELECT DISTINCT `business_id`, EXTRACT(YEAR FROM `date`) AS `inspection_year` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` WHERE `score` = 100)) GROUP BY `business_id`, `year_group` HAVING COUNT(*) >= 4

*   **子问题 2 (连续 4 年)：**
    *   **SQL：** `T1`.`business_id` IN (SELECT `business_id` FROM (SELECT `business_id`, `inspection_year`, `inspection_year` - ROW_NUMBER() OVER (PARTITION BY `business_id` ORDER BY `inspection_year`) AS `year_group` FROM (SELECT DISTINCT `business_id`, EXTRACT(YEAR FROM `date`) AS `inspection_year` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` WHERE `score` = 100)) GROUP BY `business_id`, `year_group` HAVING COUNT(*) >= 4)

*   **主问题 (餐馆名称)：**
    *   **SQL：** SELECT DISTINCT `T2`.`name` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.food_inspection.businesses` AS `T2` ON `T1`.`business_id` = `T2`.`business_id` WHERE `T1`.`score` = 100 AND `T1`.`business_id` IN (SELECT `business_id` FROM (SELECT `business_id`, `inspection_year`, `inspection_year` - ROW_NUMBER() OVER (PARTITION BY `business_id` ORDER BY `inspection_year`) AS `year_group` FROM (SELECT DISTINCT `business_id`, EXTRACT(YEAR FROM `date`) AS `inspection_year` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` WHERE `score` = 100)) GROUP BY `business_id`, `year_group` HAVING COUNT(*) >= 4)

**3. 简化与优化：**

*   步骤 2 中的最终 SQL 查询可以通过使用 `WITH` 子句将子查询提取出来，从而提高可读性。性能上，这种结构通常与原始嵌套查询相似。

**最终优化 SQL 查询：**
```sql
WITH ScoredYears AS (
  -- 子查询 2.1: 获取得分 100 的不同企业和检查年份
  SELECT DISTINCT
    business_id,
    EXTRACT(YEAR FROM date) AS inspection_year
  FROM
    `{BQ_PROJECT_ID}.food_inspection.inspections`
  WHERE
    score = 100
),
RankedYears AS (
  -- 子查询 2.2: 为每个企业的年份分配排名并计算年份组标识
  SELECT
    business_id,
    inspection_year,
    -- 计算年份与排名的差值，用于识别连续年份组
    inspection_year - ROW_NUMBER() OVER (PARTITION BY business_id ORDER BY inspection_year) AS year_group
  FROM
    ScoredYears
),
ConsecutiveBusinesses AS (
  -- 子查询 2.3: 找到连续 4 年或以上得分 100 的企业
  SELECT
    business_id
  FROM
    RankedYears
  GROUP BY
    business_id,
    year_group
  HAVING
    COUNT(*) >= 4 -- 至少连续 4 年
)
-- 主查询: 获取这些企业的名称
SELECT DISTINCT
  T2.name
FROM
  `{BQ_PROJECT_ID}.food_inspection.businesses` AS T2
INNER JOIN
  ConsecutiveBusinesses AS T3 ON T2.business_id = T3.business_id;

```

===========
Example 8

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
  symptom_Acne FLOAT64 -- 痤疮症状搜索指数
  -- ... 可能还有 symptom_Headache 列
)
PARTITION BY date
CLUSTER BY country_region_code, sub_region_1_code, sub_region_2_code, sub_region_2;

-- 注意：示例中的最终查询使用了 symptom_search_country_daily 表，这里假设其结构类似，但聚合在国家层面。
CREATE TABLE `bigquery-public-data.covid19_symptom_search.symptom_search_country_daily`
(
  country_region_code STRING,
  country_region STRING,
  date DATE,
  symptom_Headache FLOAT64 -- 头痛症状搜索指数
  -- ... 其他症状列
)
PARTITION BY date
CLUSTER BY country_region_code;


**************************
【问题】
Question:
找出头痛症状最常出现的是星期几？

**************************
【回答】
重复问题并使用递归分而治之生成 SQL。

**问题**: 找出头痛症状最常出现的是星期几？

**分析**: 我们需要确定一周中的哪一天（星期几），"头痛" (headache) 症状的搜索频率最高。这涉及到：
   - 按星期几对数据进行分组。
   - 计算 "头痛" 搜索的总频率或次数。
   - 按计数降序排序，并选择计数最高的那一天。
   - 假设 `symptom_Headache` 列代表搜索频率指数，我们需要对这个指数求和。

**伪 SQL**:
   SELECT 星期几 FROM `表名` 按星期几分组 ORDER BY 头痛频率 DESC LIMIT 1

**1. 分解与解决 (Divide and Conquer):**

*   **主问题:** 找出头痛症状最常出现的是星期几？
    *   **分析:** 需要找出星期几 (`FORMAT_DATE('%A', date)`)，使得该星期几对应的 `symptom_Headache` 的总和最高。
    *   **伪 SQL:** SELECT FORMAT_DATE('%A', `date`) AS day FROM `bigquery-public-data.covid19_symptom_search.symptom_search_country_daily` GROUP BY day ORDER BY SUM(`symptom_Headache`) DESC LIMIT 1

*   **子问题 1:** 从日期列中提取星期几。
    *   **分析:** 使用 `FORMAT_DATE` 函数和 `%A` 格式说明符从日期列中提取星期名称（例如 "Monday", "Tuesday"）。
    *   **伪 SQL:** SELECT FORMAT_DATE('%A', `date`) AS day FROM `bigquery-public-data.covid19_symptom_search.symptom_search_country_daily`

*   **子问题 2:** 按星期几分组并计算头痛症状的总频率。
    *   **分析:** 按星期几 (`day`) 分组，并使用 `SUM(symptom_Headache)` 计算每个星期几的头痛症状总搜索频率。
    *   **伪 SQL:** SELECT FORMAT_DATE('%A', `date`) AS day, SUM(`symptom_Headache`) AS total_headache_freq FROM `bigquery-public-data.covid19_symptom_search.symptom_search_country_daily` GROUP BY day

*   **子问题 3:** 按总频率降序排序并获取最高的那一天。
    *   **分析:** 使用 `ORDER BY` 子句按头痛症状总频率降序排序。使用 `LIMIT 1` 获取频率最高的那一天。
    *   **伪 SQL:** SELECT day FROM (子问题 2 的结果) ORDER BY total_headache_freq DESC LIMIT 1

**2. 组装 SQL:**

*   将所有子问题组合成最终查询：

**最终优化 SQL 查询：**
```sql
SELECT
  FORMAT_DATE('%A', date) AS day -- 提取星期几名称
FROM
  `bigquery-public-data.covid19_symptom_search.symptom_search_country_daily`
GROUP BY
  day -- 按星期几分组
ORDER BY
  SUM(symptom_Headache) DESC -- 按头痛症状总频率降序排序
LIMIT 1; -- 只返回频率最高的那一天
```
-- 注意：示例中的最终 SQL 使用了 COUNT(*)，这假设每一行代表一次搜索事件，或者我们关心的是出现头痛搜索记录的天数最多的是星期几。如果 `symptom_Headache` 是频率指数，SUM 可能更合适。这里遵循示例使用 COUNT(*)。如果 `date` 列是 STRING 类型，需要先用 PARSE_DATE('%Y-%m-%d', date) 转换。假设它是 DATE 类型。

```sql
SELECT
  FORMAT_DATE('%A', date) AS day, -- 提取星期几名称
  COUNT(*) AS headache_occurrence_count -- 计算包含头痛症状记录的数量
FROM
  `bigquery-public-data.covid19_symptom_search.symptom_search_country_daily`
-- WHERE symptom_Headache > 0 -- 如果需要确保是有意义的搜索才计数，可以添加此条件
GROUP BY
  day -- 按星期几分组
ORDER BY
  headache_occurrence_count DESC -- 按出现次数降序排序
LIMIT 1; -- 只返回出现次数最多的那一天
```

现在是实际问题，遵循说明和示例，使用递归分而治之的方法生成 GoogleSQL。
遵循策略的所有步骤。当您得到最终查询时，仅以 ```sql ... ``` 的格式输出查询字符串。确保只输出一个查询。
表名应始终与数据库模式中提到的表名完全相同，例如，`{BQ_PROJECT_ID}.airlines.Airlines` 而不是 `Airlines`。

**************************
【表创建语句】
{SCHEMA}

**************************
【问题】
Question:
{QUESTION}

**************************
【回答】
重复问题并使用递归分而治之生成 SQL。
"""


