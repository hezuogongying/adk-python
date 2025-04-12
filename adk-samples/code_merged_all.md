

---

## 文件: brand-search-optimization\brand_search_optimization\agent.py

```python
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

"""Defines Brand Search Optimization Agent"""

from google.adk.agents.llm_agent import Agent

from .shared_libraries import constants

from .sub_agents.comparison.agent import comparison_root_agent
from .sub_agents.search_results.agent import search_results_agent
from .sub_agents.keyword_finding.agent import keyword_finding_agent

from . import prompt


root_agent = Agent(
    model=constants.MODEL,
    name=constants.AGENT_NAME,
    description=constants.DESCRIPTION,
    instruction=prompt.ROOT_PROMPT,
    sub_agents=[
        keyword_finding_agent,
        search_results_agent,
        comparison_root_agent,
    ],
)

```


---

## 文件: brand-search-optimization\brand_search_optimization\prompt.py

```python
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

"""Defines the prompts in the brand search optimization agent."""

ROOT_PROMPT = """
    You are helpful product data enrichment agent for e-commerce website.
    Your primary function is to route user inputs to the appropriate agents. You will not generate answers yourself.

    Please follow these steps to accomplish the task at hand:
    1. Follow <Gather Brand Name> section and ensure that the user provides the brand.
    2. Move to the <Steps> section and strictly follow all the steps one by one
    3. Please adhere to <Key Constraints> when you attempt to answer the user's query.

    <Gather Brand Name>
    1. Greet the user and request a brand name. This brand is a required input to move forward.
    2. If the user does not provide a brand, repeatedly ask for it until it is provided. Do not proceed until you have a brand name.
    3. Once brand name has been provided go on to the next step.
    </Gather Brand Name>

    <Steps>
    1. call `keyword_finding_agent` to get a list of keywords. Do not stop after this. Go to next step
    2. Transfer to main agent
    3. Then call `search_results_agent` for the top keyword and relay the response
        <Example>
        Input: |Keyword|Rank|
               |---|---|
               |Kids shoes|1|
               |Running shoes|2|
        output: call search_results_agent with "kids shoes"
        </Example>
    4. Transfer to main agent
    5. Then call `comparison_root_agent` to get a report. Relay the response from the comparison agent to the user.
    </Steps>

    <Key Constraints>
        - Your role is follow the Steps in <Steps> in the specified order.
        - Complete all the steps
    </Key Constraints>
"""

```


---

## 文件: brand-search-optimization\brand_search_optimization\shared_libraries\constants.py

```python
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

"""Defines constants."""

import os
import dotenv

dotenv.load_dotenv()

AGENT_NAME = "brand_search_optimization"
DESCRIPTION = "A helpful assistant for brand search optimization."
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "EMPTY")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
MODEL = os.getenv("MODEL", "gemini-2.0-flash-001")
DATASET_ID = os.getenv("DATASET_ID", "products_data_agent")
TABLE_ID = os.getenv("TABLE_ID", "shoe_items")
DISABLE_WEB_DRIVER = int(os.getenv("DISABLE_WEB_DRIVER", 0))
WHL_FILE_NAME = os.getenv("ADK_WHL_FILE", "")
STAGING_BUCKET = os.getenv("STAGING_BUCKET", "")

```


---

## 文件: brand-search-optimization\brand_search_optimization\sub_agents\comparison\agent.py

```python
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

from google.adk.agents.llm_agent import Agent

from ...shared_libraries import constants
from . import prompt


comparison_generator_agent = Agent(
    model=constants.MODEL,
    name="comparison_generator_agent",
    description="A helpful agent to generate comparison.",
    instruction=prompt.COMPARISON_AGENT_PROMPT,
)

comparsion_critic_agent = Agent(
    model=constants.MODEL,
    name="comparison_critic_agent",
    description="A helpful agent to critique comparison.",
    instruction=prompt.COMPARISON_CRITIC_AGENT_PROMPT,
)

comparison_root_agent = Agent(
    model=constants.MODEL,
    name="comparison_root_agent",
    description="A helpful agent to compare titles",
    instruction=prompt.COMPARISON_ROOT_AGENT_PROMPT,
    sub_agents=[comparison_generator_agent, comparsion_critic_agent],
)

```


---

## 文件: brand-search-optimization\brand_search_optimization\sub_agents\comparison\prompt.py

```python
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

COMPARISON_AGENT_PROMPT = """
    You are a comparison agent. Your main job is to create a comparison report between titles of the products.
    1. Compare the titles gathered from search_results_agent and titles of the products for the brand
    2. Show what products you are comparing side by side in a markdown format
    3. Comparison should show the missing keywords and suggest improvement
"""

COMPARISON_CRITIC_AGENT_PROMPT = """
    You are a critic agent. Your main role is to critic the comparison and provide useful suggestions.
    When you don't have suggestions, say that you are now satisfied with the comparison
"""

COMPARISON_ROOT_AGENT_PROMPT = """
    You are a routing agent
    1. Route to `comparison_generator_agent` to generate comparison
    2. Route to `comparsion_critic_agent` to critic this comparison
    3. Loop through these agents
    4. Stop when the `comparison_critic_agent` is satisfied
    5. Relay the comparison report to the user
"""

```


---

## 文件: brand-search-optimization\brand_search_optimization\sub_agents\keyword_finding\agent.py

```python
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

"""Defines keyword finding agent."""

from google.adk.agents.llm_agent import Agent

from ...shared_libraries import constants
from ...tools import bq_connector
from . import prompt

keyword_finding_agent = Agent(
    model=constants.MODEL,
    name="keyword_finding_agent",
    description="A helpful agent to find keywords",
    instruction=prompt.KEYWORD_FINDING_AGENT_PROMPT,
    tools=[
        bq_connector.get_product_details_for_brand,
    ],
)

```


---

## 文件: brand-search-optimization\brand_search_optimization\sub_agents\keyword_finding\prompt.py

```python
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

KEYWORD_FINDING_AGENT_PROMPT = """
Please follow these steps to accomplish the task at hand:
1. Follow all steps in the <Tool Calling> section and ensure that the tool is called.
2. Move to the <Keyword Grouping> section to group keywords
3. Rank keywords by following steps in <Keyword Ranking> section
4. Please adhere to <Key Constraints> when you attempt to find keywords
5. Relay the ranked keywords in markdown table
6. Transfer to root_agent

You are helpful keyword finding agent for a brand name.
Your primary function is to find keywords shoppers would type in when trying to find for the products from the brand user provided. 

<Tool Calling>
    - call `get_product_details_for_brand` tool to find product from a brand
    - Show the results from tool to the user in markdown format as is
    - Analyze the title, description, attributes of the product to find one keyword shoppers would type in when trying to find for the products from this brand
    - <Example>
        Input:
        |title|description|attribute|
        |Kids' Joggers|Comfortable and supportive running shoes for active kids. Breathable mesh upper keeps feet cool, while the durable outsole provides excellent traction.|Size: 10 Toddler, Color: Blue/Green|
        Output: running shoes, active shoes, kids shoes, sneakers
      </Example>
</Tool Calling>

<Keyword Grouping>
    1. Remove duplicate keywords
    2. Group the keywords with similar meaning
</Keyword Grouping>

<Keyword Ranking>
    1. If the keywords have the input brand name in it, rank them lower
    2. Rank generic keywords higher
</Keyword Ranking>
"""

```


---

## 文件: brand-search-optimization\brand_search_optimization\sub_agents\search_results\agent.py

```python
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

import time
from PIL import Image

import selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from google.adk.agents.llm_agent import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.load_artifacts_tool import load_artifacts_tool
from google.genai import types

from . import prompt
from ...shared_libraries import constants

import warnings

warnings.filterwarnings("ignore", category=UserWarning)

if not constants.DISABLE_WEB_DRIVER:
    options = Options()
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--verbose")
    options.add_argument("user-data-dir=/tmp/selenium")

    driver = selenium.webdriver.Chrome(options=options)


def go_to_url(url: str) -> str:
    """Navigates the browser to the given URL."""
    print(f"🌐 Navigating to URL: {url}")  # Added print statement
    driver.get(url.strip())
    return f"Navigated to URL: {url}"


def take_screenshot(tool_context: ToolContext) -> dict:
    """Takes a screenshot and saves it with the given filename. called 'load artifacts' after to load the image"""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    print(f"📸 Taking screenshot and saving as: {filename}")
    driver.save_screenshot(filename)

    image = Image.open(filename)

    tool_context.save_artifact(
        filename,
        types.Part.from_bytes(data=image.tobytes(), mime_type="image/png"),
    )

    return {"status": "ok", "filename": filename}


def click_at_coordinates(x: int, y: int) -> str:
    """Clicks at the specified coordinates on the screen."""
    driver.execute_script(f"window.scrollTo({x}, {y});")
    driver.find_element(By.TAG_NAME, "body").click()


def find_element_with_text(text: str) -> str:
    """Finds an element on the page with the given text."""
    print(f"🔍 Finding element with text: '{text}'")  # Added print statement

    try:
        element = driver.find_element(By.XPATH, f"//*[text()='{text}']")
        if element:
            return "Element found."
        else:
            return "Element not found."
    except selenium.common.exceptions.NoSuchElementException:
        return "Element not found."
    except selenium.common.exceptions.ElementNotInteractableException:
        return "Element not interactable, cannot click."


def click_element_with_text(text: str) -> str:
    """Clicks on an element on the page with the given text."""
    print(f"🖱️ Clicking element with text: '{text}'")  # Added print statement

    try:
        element = driver.find_element(By.XPATH, f"//*[text()='{text}']")
        element.click()
        return f"Clicked element with text: {text}"
    except selenium.common.exceptions.NoSuchElementException:
        return "Element not found, cannot click."
    except selenium.common.exceptions.ElementNotInteractableException:
        return "Element not interactable, cannot click."
    except selenium.common.exceptions.ElementClickInterceptedException:
        return "Element click intercepted, cannot click."


def enter_text_into_element(text_to_enter: str, element_id: str) -> str:
    """Enters text into an element with the given ID."""
    print(
        f"📝 Entering text '{text_to_enter}' into element with ID: {element_id}"
    )  # Added print statement

    try:
        input_element = driver.find_element(By.ID, element_id)
        input_element.send_keys(text_to_enter)
        return (
            f"Entered text '{text_to_enter}' into element with ID: {element_id}"
        )
    except selenium.common.exceptions.NoSuchElementException:
        return "Element with given ID not found."
    except selenium.common.exceptions.ElementNotInteractableException:
        return "Element not interactable, cannot click."


def scroll_down_screen() -> str:
    """Scrolls down the screen by a moderate amount."""
    print("⬇️ scroll the screen")  # Added print statement
    driver.execute_script("window.scrollBy(0, 500)")
    return "Scrolled down the screen."


def get_page_source() -> str:
    LIMIT = 1000000
    """Returns the current page source."""
    print("📄 Getting page source...")  # Added print statement
    return driver.page_source[0:LIMIT]


def analyze_webpage_and_determine_action(
    page_source: str, user_task: str, tool_context: ToolContext
) -> str:
    """Analyzes the webpage and determines the next action (scroll, click, etc.)."""
    print(
        "🤔 Analyzing webpage and determining next action..."
    )  # Added print statement

    analysis_prompt = f"""
    You are an expert web page analyzer.
    You have been tasked with controlling a web browser to achieve a user's goal.
    The user's task is: {user_task}
    Here is the current HTML source code of the webpage:
    ```html
    {page_source}
    ```

    Based on the webpage content and the user's task, determine the next best action to take.
    Consider actions like: completing page source, scrolling down to see more content, clicking on links or buttons to navigate, or entering text into input fields.

    Think step-by-step:
    1. Briefly analyze the user's task and the webpage content.
    2. If source code appears to be incomplete, complete it to make it valid html. Keep the product titles as is. Only complete missing html syntax
    3. Identify potential interactive elements on the page (links, buttons, input fields, etc.).
    4. Determine if scrolling is necessary to reveal more content.
    5. Decide on the most logical next action to progress towards completing the user's task.

    Your response should be a concise action plan, choosing from these options:
    - "COMPLETE_PAGE_SOURCE": If source code appears to be incomplete, complte it to make it valid html
    - "SCROLL_DOWN": If more content needs to be loaded by scrolling.
    - "CLICK: <element_text>": If a specific element with text <element_text> should be clicked. Replace <element_text> with the actual text of the element.
    - "ENTER_TEXT: <element_id>, <text_to_enter>": If text needs to be entered into an input field. Replace <element_id> with the ID of the input element and <text_to_enter> with the text to enter.
    - "TASK_COMPLETED": If you believe the user's task is likely completed on this page.
    - "STUCK": If you are unsure what to do next or cannot progress further.
    - "ASK_USER": If you need clarification from the user on what to do next.

    If you choose "CLICK" or "ENTER_TEXT", ensure the element text or ID is clearly identifiable from the webpage source. If multiple similar elements exist, choose the most relevant one based on the user's task.
    If you are unsure, or if none of the above actions seem appropriate, default to "ASK_USER".

    Example Responses:
    - SCROLL_DOWN
    - CLICK: Learn more
    - ENTER_TEXT: search_box_id, Gemini API
    - TASK_COMPLETED
    - STUCK
    - ASK_USER

    What is your action plan?
    """
    return analysis_prompt


search_results_agent = Agent(
    model=constants.MODEL,
    name="search_results_agent",
    description="Get top 3 search results info for a keyword using web browsing",
    instruction=prompt.SEARCH_RESULT_AGENT_PROMPT,
    tools=[
        go_to_url,
        take_screenshot,
        find_element_with_text,
        click_element_with_text,
        enter_text_into_element,
        scroll_down_screen,
        get_page_source,
        load_artifacts_tool,
        analyze_webpage_and_determine_action,
    ],
)

```


---

## 文件: brand-search-optimization\brand_search_optimization\sub_agents\search_results\prompt.py

```python
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

"""Defines Search Results Agent Prompts"""

SEARCH_RESULT_AGENT_PROMPT = """
    You are a web controller agent.

    <Ask website>
        - Start by asking the user "which website they want to visit?"
    </Ask website>

    <Navigation & Searching>
        - Ask for keyword from the user
        - if the user says google shopping, visit this website link is https://www.google.com/search?q=<keyword> and click on "shopping" tab
    </Navigation & Searching>

    <Gather Information> 
        - getting titles of the top 3 products by analyzing the webpage
        - Do not make up 3 products
        - Show title of the products in a markdown format
    </Gather Information>

    <Key Constraints>
        - Continue until you believe the title, description and attribute information is gathered
        - Do not make up title, description and attribute information
        - If you can not find the information, convery this information to the user 
    </Key Constraints>

    Please follow these steps to accomplish the task at hand:
    1. Follow all steps in the <Ask website> to get website name
    2. Follow the steps in <Navigation & Searching> for searching
    3. Then follow steps in <Gather Information> to gather required information from page source and relay this to user
    4. Please adhere to <Key Constraints> when you attempt to answer the user's query.
    5. Transfer titles to the next agent
"""

```


---

## 文件: brand-search-optimization\brand_search_optimization\tools\bq_connector.py

```python
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

"""Defines tools for brand search optimization agent"""

from google.cloud import bigquery
from google.adk.tools import ToolContext

from ..shared_libraries import constants

# Initialize the BigQuery client outside the function
try:
    client = bigquery.Client()  # Initialize client once
except Exception as e:
    print(f"Error initializing BigQuery client: {e}")
    client = None  # Set client to None if initialization fails


def get_product_details_for_brand(tool_context: ToolContext):
    """
    Retrieves product details (title, description, attributes, and brand) from a BigQuery table for a tool_context.

    Args:
        tool_context (str): The tool_context to search for (using a LIKE '%brand%' query).

    Returns:
        str: A markdown table containing the product details, or an error message if BigQuery client initialization failed.
             The table includes columns for 'Title', 'Description', 'Attributes', and 'Brand'.
             Returns a maximum of 3 results.

    Example:
        >>> get_product_details_for_brand(tool_context)
        '| Title | Description | Attributes | Brand |\\n|---|---|---|---|\\n| Nike Air Max | Comfortable running shoes | Size: 10, Color: Blue | Nike\\n| Nike Sportswear T-Shirt | Cotton blend, short sleeve | Size: L, Color: Black | Nike\\n| Nike Pro Training Shorts | Moisture-wicking fabric | Size: M, Color: Gray | Nike\\n'
    """
    brand = tool_context.user_content.parts[0].text
    if client is None:  # Check if client initialization failed
        return "BigQuery client initialization failed. Cannot execute query."

    query = f"""
        SELECT
            Title,
            Description,
            Attributes,
            Brand
        FROM
            {constants.PROJECT}.{constants.DATASET_ID}.{constants.TABLE_ID}
        WHERE brand LIKE '%{brand}%'
        LIMIT 3
    """
    query_job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("parameter1", "STRING", brand)
        ]
    )

    query_job = client.query(query, job_config=query_job_config)
    query_job = client.query(query)
    results = query_job.result()

    markdown_table = "| Title | Description | Attributes | Brand |\n"
    markdown_table += "|---|---|---|---|\n"

    for row in results:
        title = row.Title
        description = row.Description if row.Description else "N/A"
        attributes = row.Attributes if row.Attributes else "N/A"

        markdown_table += (
            f"| {title} | {description} | {attributes} | {brand}\n"
        )

    return markdown_table

```


---

## 文件: brand-search-optimization\deployment\bq_populate_data.py

```python
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

from google.cloud import bigquery

from brand_search_optimization.shared_libraries import constants

PROJECT = constants.PROJECT
TABLE_ID = constants.TABLE_ID
LOCATION = constants.LOCATION
DATASET_ID = constants.DATASET_ID
TABLE_ID = constants.TABLE_ID

client = bigquery.Client(project=PROJECT)

# Sample data to insert
data_to_insert = [
    {
        "Title": "Kids' Joggers",
        "Description": "Comfortable and supportive running shoes for active kids. Breathable mesh upper keeps feet cool, while the durable outsole provides excellent traction.",
        "Attributes": "Size: 10 Toddler, Color: Blue/Green",
        "Brand": "BSOAgentTestBrand",
    },
    {
        "Title": "Light-Up Sneakers",
        "Description": "Fun and stylish sneakers with light-up features that kids will love. Supportive and comfortable for all-day play.",
        "Attributes": "Size: 13 Toddler, Color: Silver",
        "Brand": "BSOAgentTestBrand",
    },
    {
        "Title": "School Shoes",
        "Description": "Versatile and comfortable shoes perfect for everyday wear at school. Durable construction with a supportive design.",
        "Attributes": "Size: 12 Preschool, Color: Black",
        "Brand": "BSOAgentTestBrand",
    },
]


def create_dataset_if_not_exists():
    """Creates a BigQuery dataset if it does not already exist."""
    # Construct a BigQuery client object.
    dataset_id = f"{client.project}.{DATASET_ID}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "US"
    client.delete_dataset(
        dataset_id, delete_contents=True, not_found_ok=True
    )  # Make an API request.
    dataset = client.create_dataset(dataset)  # Make an API request.
    print("Created dataset {}.{}".format(client.project, dataset.dataset_id))
    return dataset


def populate_bigquery_table():
    """Populates a BigQuery table with the provided data."""
    dataset_ref = create_dataset_if_not_exists()
    if not dataset_ref:
        return

    # Define the schema based on your CREATE TABLE statement
    schema = [
        bigquery.SchemaField("Title", "STRING"),
        bigquery.SchemaField("Description", "STRING"),
        bigquery.SchemaField("Attributes", "STRING"),
        bigquery.SchemaField("Brand", "STRING"),
    ]
    table_id = f"{PROJECT}.{DATASET_ID}.{TABLE_ID}"
    table = bigquery.Table(table_id, schema=schema)
    client.delete_table(table_id, not_found_ok=True)  # Make an API request.
    print("Deleted table '{}'.".format(table_id))
    table = client.create_table(table)  # Make an API request.
    print(
        "Created table {}.{}.{}".format(
            PROJECT, table.dataset_id, table.table_id
        )
    )

    errors = client.insert_rows_json(table=table, json_rows=data_to_insert)

    if errors == []:
        print(
            f"Successfully inserted {len(data_to_insert)} rows into {PROJECT}.{DATASET_ID}.{TABLE_ID}"
        )
    else:
        print("Errors occurred while inserting rows:")
        for error in errors:
            print(error)


if __name__ == "__main__":
    populate_bigquery_table()
    print(
        "\n--- Instructions on how to add permissions to BQ Table are in the customiztion.md file ---"
    )

```


---

## 文件: brand-search-optimization\deployment\deploy.py

```python
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

"""Deployment script for Brand Search Optimization agent."""

import os

import vertexai
from absl import app, flags
from brand_search_optimization.agent import root_agent
from brand_search_optimization.shared_libraries import constants
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP bucket.")
flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")
flags.DEFINE_bool("create", False, "Create a new agent.")
flags.DEFINE_bool("delete", False, "Delete an existing agent.")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])


def create() -> None:
    adk_app = AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    extra_packages = [f"./brand_search_optimization"]

    remote_agent = agent_engines.create(
        adk_app,
        requirements=[
            "google-adk",
            "google-cloud-aiplatform[agent_engines] @ git+https://github.com/googleapis/python-aiplatform.git@copybara_738852226",
            "pydantic==2.10.6",
            "requests",
            "python-dotenv",
            "google-genai",
            "selenium",
            "webdriver-manager",
            "google-cloud-bigquery",
            "absl-py",
            "pillow",
        ],
        extra_packages=extra_packages,
    )
    print(f"Created remote agent: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    remote_agent = agent_engines.get(resource_id)
    remote_agent.delete(force=True)
    print(f"Deleted remote agent: {resource_id}")


def main(argv: list[str]) -> None:
    project_id = FLAGS.project_id if FLAGS.project_id else constants.PROJECT
    location = FLAGS.location if FLAGS.location else constants.LOCATION
    bucket = FLAGS.bucket if FLAGS.bucket else constants.STAGING_BUCKET

    print(f"PROJECT: {project_id}")
    print(f"LOCATION: {location}")
    print(f"BUCKET: {bucket}")

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print(
            "Missing required environment variable: GOOGLE_CLOUD_STORAGE_BUCKET"
        )
        return

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    if FLAGS.create:
        create()
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("resource_id is required for delete")
            return
        delete(FLAGS.resource_id)
    else:
        print("Unknown command")


if __name__ == "__main__":
    app.run(main)

```


---

## 文件: brand-search-optimization\eval\eval.py

```python
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

import pathlib

from google.adk.evaluation.agent_evaluator import AgentEvaluator
import dotenv
import pytest


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


def test_all():
    """Test the agent's basic ability on a few examples."""
    AgentEvaluator.evaluate(
        agent_module="brand_search_optimization",
        eval_dataset_file_path_or_dir=str(
            pathlib.Path(__file__).parent / "data"
        ),
        num_runs=1,
    )

```


---

## 文件: brand-search-optimization\eval\data\eval_data1.evalset.json

```json
[
  {
    "name": "eval_data_set_google_shopping",
    "data": [
      {
        "query": "hello",
        "expected_tool_use": [],
        "expected_intermediate_agent_responses": [],
        "reference": "Hi there! To get started, could you please provide the brand name you'd like to optimize for?"
      },
      {
        "query": "BSOAgentTestBrand",
        "expected_tool_use": [
          {
            "tool_name": "transfer_to_agent",
            "tool_input": {
              "agent_name": "keyword_finding_agent"
            }
          },
          {
            "tool_name": "get_product_details_for_brand",
            "tool_input": {}
          }
        ],
        "expected_intermediate_agent_responses": [
          {
            "author": "brand_search_optimization",
            "text": "Okay, great. Now that I have the brand name, I'll start by finding some relevant keywords.\n\n"
          }
        ],
        "reference": "| Title | Description | Attributes | Brand |\n|---|---|---|---|\n| Kids' Joggers | Comfortable and supportive running shoes for active kids. Breathable mesh upper keeps feet cool, while the durable outsole provides excellent traction. | Size: 10 Toddler, Color: Blue/Green | BSOAgentTestBrand |\n| Light-Up Sneakers | Fun and stylish sneakers with light-up features that kids will love. Supportive and comfortable for all-day play. | Size: 13 Toddler, Color: Silver | BSOAgentTestBrand |\n| School Shoes | Versatile and comfortable shoes perfect for everyday wear at school. Durable construction with a supportive design. | Size: 12 Preschool, Color: Black | BSOAgentTestBrand |\n\nHere are some keywords shoppers might use:\n\n*   running shoes\n*   active shoes\n*   kids shoes\n*   sneakers\n*   light up sneakers\n*   school shoes\n*   toddler shoes\n*   preschool shoes\n*   joggers\n*   kids joggers\n\nHere is the ranked list\n\n| Keywords |\n|---|---|\n| running shoes |\n| active shoes |\n| kids shoes |\n| sneakers |\n| light up sneakers |\n| school shoes |\n| toddler shoes |\n| preschool shoes |\n| joggers |\n| kids joggers |\n"
      },
      {
        "query": "can you search websites",
        "expected_tool_use": [
          {
            "tool_name": "transfer_to_agent",
            "tool_input": {
              "agent_name": "search_results_agent"
            }
          }
        ],
        "expected_intermediate_agent_responses": [
          {
            "author": "keyword_finding_agent",
            "text": "I am designed to find keywords for a given brand based on product details. To search websites for information, I would need to transfer you to a different agent. Would you like me to do that?\n"
          }
        ],
        "reference": "Which website do you want to visit?\n"
      },
      {
        "query": "google shopping",
        "expected_tool_use": [],
        "expected_intermediate_agent_responses": [],
        "reference": "What keyword are you looking for?\n"
      },
      {
        "query": "kids shoes",
        "expected_tool_use": [
          {
            "tool_name": "go_to_url",
            "tool_input": {
              "url": "https://www.google.com/search?q=kids shoes"
            }
          },
          {
            "tool_name": "click_element_with_text",
            "tool_input": {
              "text": "Shopping"
            }
          },
          {
            "tool_name": "get_page_source",
            "tool_input": {}
          }
        ],
        "expected_intermediate_agent_responses": [],
        "reference": "Okay, I have analyzed the webpage and here are the top 3 products that matched your search query:\n\n*   **Nike Kids\\' Flex Runner 3 Shoes**\n*   **Kids adidas Racer TR23 Shoes Kids**\n*   **Nike Kids\\' Court Borough Low Recraft Shoes**\n\nCould you please tell me if you want more information on any of these products or if you have another question?\n"
      },
      {
        "query": "this is good",
        "expected_tool_use": [
          {
            "tool_name": "transfer_to_agent",
            "tool_input": {
              "agent_name": "brand_search_optimization"
            }
          },
          {
            "tool_name": "transfer_to_agent",
            "tool_input": {
              "agent_name": "comparison_root_agent"
            }
          },
          {
            "tool_name": "transfer_to_agent",
            "tool_input": {
              "agent_name": "comparison_generator_agent"
            }
          },
          {
            "tool_name": "transfer_to_agent",
            "tool_input": {
              "agent_name": "comparison_generator_agent"
            }
          }
        ],
        "expected_intermediate_agent_responses": [
          {
            "author": "brand_search_optimization",
            "text": "Great! Now that I have the search results for \"kids shoes,\" I will run a comparison of the titles.\n\n"
          }
        ],
        "reference": "I can compare the titles gathered from the search results with the titles of the products for the brand \"BSOAgentTestBrand\".\nHere's a comparison report:\n\n| **BSOAgentTestBrand Titles** | **Search Result Titles** | **Analysis & Suggestions** |\n|---|---|---|\n| Kids' Joggers | Nike Kids' Flex Runner 3 Shoes | **Missing Keywords:** \"Nike\" \"Flex Runner 3\" ; Consider including competitor brands or related keywords like 'sneakers' or 'running shoes' in the title.  |\n| Light-Up Sneakers | Kids adidas Racer TR23 Shoes Kids | **Missing Keywords:** \"Adidas\" \"Racer TR23\" \"Shoes\"; Including specific model names can improve targeting of users searching for those models.|\n| School Shoes | Nike Kids' Court Borough Low Recraft Shoes | **Missing Keywords:** \"Nike\" \"Court Borough\" \"Low\" \"Recraft\" ; Consider a title that more closely matches common search terms for the specific product type. |\n\n**Summary of Suggestions:**\n\n*   **Incorporate Brand Names:** Add brand names (Nike, Adidas) to the titles.\n*   **Include Model Names:** Use specific model names (Flex Runner 3, Racer TR23, Court Borough, Low, Recraft) in the titles.\n*   **Add Keywords:** Consider adding keywords like \"sneakers,\" \"running shoes,\" \"light up,\" or \"school\" to titles where relevant to improve general search visibility.\n"
      }
    ],
    "initial_state": {
      "session": {}
    }
  }
]
```


---

## 文件: brand-search-optimization\eval\data\test_config.json

```json
{
    "criteria": {
        "tool_trajectory_avg_score": 0.2,
        "response_match_score": 0.2
    }
}
```


---

## 文件: brand-search-optimization\tests\unit\test_tools.py

```python
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

"""Unit tests for tools"""

from unittest.mock import MagicMock, patch

from google.adk.tools import ToolContext

from brand_search_optimization.tools import bq_connector
from brand_search_optimization.shared_libraries import constants


class TestBrandSearchOptimization:

    @patch("brand_search_optimization.tools.bq_connector.client")
    def test_get_product_details_for_brand_success(self, mock_client):
        # Mock ToolContext
        mock_tool_context = MagicMock(spec=ToolContext)
        mock_tool_context.user_content.parts = [MagicMock(text="cymbal")]

        # Mock BigQuery results
        mock_row1 = MagicMock(
            title="cymbal Air Max",
            description="Comfortable running shoes",
            attribute="Size: 10, Color: Blue",
            brand="cymbal",
        )
        mock_row2 = MagicMock(
            title="cymbal Sportswear T-Shirt",
            description="Cotton blend, short sleeve",
            attribute="Size: L, Color: Black",
            brand="cymbal",
        )
        mock_row3 = MagicMock(
            title="neuravibe Pro Training Shorts",
            description="Moisture-wicking fabric",
            attribute="Size: M, Color: Gray",
            brand="neuravibe",
        )
        mock_results = [mock_row1, mock_row2, mock_row3]

        # Mock QueryJob and its result
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = mock_results
        mock_client.query.return_value = mock_query_job

        # Mock constants
        with patch.object(constants, "PROJECT", "test_project"):
            with patch.object(constants, "TABLE_ID", "test_table"):
                # Call the function
                markdown_output = bq_connector.get_product_details_for_brand(
                    mock_tool_context
                )
                assert "neuravibe Pro" not in markdown_output

```


---

## 文件: customer-service\customer_service\agent.py

```python
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
# limitations under the License.§

"""Agent module for the customer service agent."""

import logging
import warnings
from google.adk import Agent
from .config import Config
from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION
from .shared_libraries.callbacks import (
    rate_limit_callback,
    before_agent,
    before_tool,
)
from .tools.tools import (
    send_call_companion_link,
    approve_discount,
    sync_ask_for_approval,
    update_salesforce_crm,
    access_cart_information,
    modify_cart,
    get_product_recommendations,
    check_product_availability,
    schedule_planting_service,
    get_available_planting_times,
    send_care_instructions,
    generate_qr_code,
)

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

configs = Config()

# configure logging __name__
logger = logging.getLogger(__name__)


root_agent = Agent(
    model=configs.agent_settings.model,
    global_instruction=GLOBAL_INSTRUCTION,
    instruction=INSTRUCTION,
    name=configs.agent_settings.name,
    tools=[
        send_call_companion_link,
        approve_discount,
        sync_ask_for_approval,
        update_salesforce_crm,
        access_cart_information,
        modify_cart,
        get_product_recommendations,
        check_product_availability,
        schedule_planting_service,
        get_available_planting_times,
        send_care_instructions,
        generate_qr_code,
    ],
    before_tool_callback=before_tool,
    before_agent_callback=before_agent,
    before_model_callback=rate_limit_callback,
)

```


---

## 文件: customer-service\customer_service\config.py

```python
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
"""Configuration module for the customer service agent."""

import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AgentModel(BaseModel):
    """Agent model settings."""

    name: str = Field(default="customer_service_agent")
    model: str = Field(default="gemini-2.0-flash-001")


class Config(BaseSettings):
    """Configuration settings for the customer service agent."""

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../.env"
        ),
        env_prefix="GOOGLE_",
        case_sensitive=True,
    )
    agent_settings: AgentModel = Field(default=AgentModel())
    app_name: str = "customer_service_app"
    CLOUD_PROJECT: str = Field(default="my_project")
    CLOUD_LOCATION: str = Field(default="us-central1")
    GENAI_USE_VERTEXAI: str = Field(default="1")
    API_KEY: str | None = Field(default="")

```


---

## 文件: customer-service\customer_service\prompts.py

```python
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

"""Global instruction and instruction for the customer service agent."""

from .entities.customer import Customer

GLOBAL_INSTRUCTION = f"""
The profile of the current customer is:  {Customer.get_customer("123").to_json()}
"""

INSTRUCTION = """
You are "Project Pro," the primary AI assistant for Cymbal Home & Garden, a big-box retailer specializing in home improvement, gardening, and related supplies.
Your main goal is to provide excellent customer service, help customers find the right products, assist with their gardening needs, and schedule services.
Always use conversation context/state or tools to get information. Prefer tools over your own internal knowledge

**Core Capabilities:**

1.  **Personalized Customer Assistance:**
    *   Greet returning customers by name and acknowledge their purchase history and current cart contents.  Use information from the provided customer profile to personalize the interaction.
    *   Maintain a friendly, empathetic, and helpful tone.

2.  **Product Identification and Recommendation:**
    *   Assist customers in identifying plants, even from vague descriptions like "sun-loving annuals."
    *   Request and utilize visual aids (video) to accurately identify plants.  Guide the user through the video sharing process.
    *   Provide tailored product recommendations (potting soil, fertilizer, etc.) based on identified plants, customer needs, and their location (Las Vegas, NV). Consider the climate and typical gardening challenges in Las Vegas.
    *   Offer alternatives to items in the customer's cart if better options exist, explaining the benefits of the recommended products.
    *   Always check the customer profile information before asking the customer questions. You might already have the answer

3.  **Order Management:**
    *   Access and display the contents of a customer's shopping cart.
    *   Modify the cart by adding and removing items based on recommendations and customer approval.  Confirm changes with the customer.
    *   Inform customers about relevant sales and promotions on recommended products.

4.  **Upselling and Service Promotion:**
    *   Suggest relevant services, such as professional planting services, when appropriate (e.g., after a plant purchase or when discussing gardening difficulties).
    *   Handle inquiries about pricing and discounts, including competitor offers.
    *   Request manager approval for discounts when necessary, according to company policy.  Explain the approval process to the customer.

5.  **Appointment Scheduling:**
    *   If planting services (or other services) are accepted, schedule appointments at the customer's convenience.
    *   Check available time slots and clearly present them to the customer.
    *   Confirm the appointment details (date, time, service) with the customer.
    *   Send a confirmation and calendar invite.

6.  **Customer Support and Engagement:**
    *   Send plant care instructions relevant to the customer's purchases and location.
    *   Offer a discount QR code for future in-store purchases to loyal customers.

**Tools:**
You have access to the following tools to assist you:

*   `send_call_companion_link(phone_number: str) -> str`: Sends a link for video connection. Use this tool to start live streaming with the user. When user agrees with you to share video, use this tool to start the process 
*   `approve_discount(type: str, value: float, reason: str) -> str`: Approves a discount (within pre-defined limits).
*   `sync_ask_for_approval(type: str, value: float, reason: str) -> str`: Requests discount approval from a manager (synchronous version).
*   `update_salesforce_crm(customer_id: str, details: str) -> dict`: Updates customer records in Salesforce after the customer has completed a purchase.
*   `access_cart_information(customer_id: str) -> dict`: Retrieves the customer's cart contents. Use this to check customers cart contents or as a check before related operations
*   `modify_cart(customer_id: str, items_to_add: list, items_to_remove: list) -> dict`: Updates the customer's cart. before modifying a cart first access_cart_information to see what is already in the cart
*   `get_product_recommendations(plant_type: str, customer_id: str) -> dict`: Suggests suitable products for a given plant type. i.e petunias. before recomending a product access_cart_information so you do not recommend something already in cart. if the product is in cart say you already have that
*   `check_product_availability(product_id: str, store_id: str) -> dict`: Checks product stock.
*   `schedule_planting_service(customer_id: str, date: str, time_range: str, details: str) -> dict`: Books a planting service appointment.
*   `get_available_planting_times(date: str) -> list`: Retrieves available time slots.
*   `send_care_instructions(customer_id: str, plant_type: str, delivery_method: str) -> dict`: Sends plant care information.
*   `generate_qr_code(customer_id: str, discount_value: float, discount_type: str, expiration_days: int) -> dict`: Creates a discount QR code 

**Constraints:**

*   You must use markdown to render any tables.
*   **Never mention "tool_code", "tool_outputs", or "print statements" to the user.** These are internal mechanisms for interacting with tools and should *not* be part of the conversation.  Focus solely on providing a natural and helpful customer experience.  Do not reveal the underlying implementation details.
*   Always confirm actions with the user before executing them (e.g., "Would you like me to update your cart?").
*   Be proactive in offering help and anticipating customer needs.

"""

```


---

## 文件: customer-service\customer_service\entities\customer.py

```python
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
"""Customer entity module."""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class Address(BaseModel):
    """
    Represents a customer's address.
    """

    street: str
    city: str
    state: str
    zip: str
    model_config = ConfigDict(from_attributes=True)


class Product(BaseModel):
    """
    Represents a product in a customer's purchase history.
    """

    product_id: str
    name: str
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class Purchase(BaseModel):
    """
    Represents a customer's purchase.
    """

    date: str
    items: List[Product]
    total_amount: float
    model_config = ConfigDict(from_attributes=True)


class CommunicationPreferences(BaseModel):
    """
    Represents a customer's communication preferences.
    """

    email: bool = True
    sms: bool = True
    push_notifications: bool = True
    model_config = ConfigDict(from_attributes=True)


class GardenProfile(BaseModel):
    """
    Represents a customer's garden profile.
    """

    type: str
    size: str
    sun_exposure: str
    soil_type: str
    interests: List[str]
    model_config = ConfigDict(from_attributes=True)


class Customer(BaseModel):
    """
    Represents a customer.
    """

    account_number: str
    customer_id: str
    customer_first_name: str
    customer_last_name: str
    email: str
    phone_number: str
    customer_start_date: str
    years_as_customer: int
    billing_address: Address
    purchase_history: List[Purchase]
    loyalty_points: int
    preferred_store: str
    communication_preferences: CommunicationPreferences
    garden_profile: GardenProfile
    scheduled_appointments: Dict = Field(default_factory=dict)
    model_config = ConfigDict(from_attributes=True)

    def to_json(self) -> str:
        """
        Converts the Customer object to a JSON string.

        Returns:
            A JSON string representing the Customer object.
        """
        return self.model_dump_json(indent=4)

    @staticmethod
    def get_customer(current_customer_id: str) -> Optional["Customer"]:
        """
        Retrieves a customer based on their ID.

        Args:
            customer_id: The ID of the customer to retrieve.

        Returns:
            The Customer object if found, None otherwise.
        """
        # In a real application, this would involve a database lookup.
        # For this example, we'll just return a dummy customer.
        return Customer(
            customer_id=current_customer_id,
            account_number="428765091",
            customer_first_name="Alex",
            customer_last_name="Johnson",
            email="alex.johnson@example.com",
            phone_number="+1-702-555-1212",
            customer_start_date="2022-06-10",
            years_as_customer=2,
            billing_address=Address(
                street="123 Main St", city="Anytown", state="CA", zip="12345"
            ),
            purchase_history=[  # Example purchase history
                Purchase(
                    date="2023-03-05",
                    items=[
                        Product(
                            product_id="fert-111",
                            name="All-Purpose Fertilizer",
                            quantity=1,
                        ),
                        Product(
                            product_id="trowel-222",
                            name="Gardening Trowel",
                            quantity=1,
                        ),
                    ],
                    total_amount=35.98,
                ),
                Purchase(
                    date="2023-07-12",
                    items=[
                        Product(
                            product_id="seeds-333",
                            name="Tomato Seeds (Variety Pack)",
                            quantity=2,
                        ),
                        Product(
                            product_id="pots-444",
                            name="Terracotta Pots (6-inch)",
                            quantity=4,
                        ),
                    ],
                    total_amount=42.5,
                ),
                Purchase(
                    date="2024-01-20",
                    items=[
                        Product(
                            product_id="gloves-555",
                            name="Gardening Gloves (Leather)",
                            quantity=1,
                        ),
                        Product(
                            product_id="pruner-666",
                            name="Pruning Shears",
                            quantity=1,
                        ),
                    ],
                    total_amount=55.25,
                ),
            ],
            loyalty_points=133,
            preferred_store="Anytown Garden Store",
            communication_preferences=CommunicationPreferences(
                email=True, sms=False, push_notifications=True
            ),
            garden_profile=GardenProfile(
                type="backyard",
                size="medium",
                sun_exposure="full sun",
                soil_type="unknown",
                interests=["flowers", "vegetables"],
            ),
            scheduled_appointments={},
        )

```


---

## 文件: customer-service\customer_service\shared_libraries\callbacks.py

```python
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

"""Callback functions for FOMC Research Agent."""

import logging
import time

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from typing import Any, Dict
from google.adk.tools import BaseTool
from google.adk.agents.invocation_context import InvocationContext
from customer_service.entities.customer import Customer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

RATE_LIMIT_SECS = 60
RPM_QUOTA = 10


def rate_limit_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    """Callback function that implements a query rate limit.

    Args:
      callback_context: A CallbackContext obj representing the active callback
        context.
      llm_request: A LlmRequest obj representing the active LLM request.
    """
    for content in llm_request.contents:
        for part in content.parts:
            if part.text=="":
                part.text=" "

    
    

    now = time.time()
    if "timer_start" not in callback_context.state:

        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
        logger.debug(
            "rate_limit_callback [timestamp: %i, "
            "req_count: 1, elapsed_secs: 0]",
            now,
        )
        return

    request_count = callback_context.state["request_count"] + 1
    elapsed_secs = now - callback_context.state["timer_start"]
    logger.debug(
        "rate_limit_callback [timestamp: %i, request_count: %i,"
        " elapsed_secs: %i]",
        now,
        request_count,
        elapsed_secs,
    )

    if request_count > RPM_QUOTA:
        delay = RATE_LIMIT_SECS - elapsed_secs + 1
        if delay > 0:
            logger.debug("Sleeping for %i seconds", delay)
            time.sleep(delay)
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
    else:
        callback_context.state["request_count"] = request_count

    return


def lowercase_value(value):
    """Make dictionary lowercase"""
    if isinstance(value, dict):
        return (dict(k, lowercase_value(v)) for k, v in value.items())
    elif isinstance(value, str):
        return value.lower()
    elif isinstance(value, (list, set, tuple)):
        tp = type(value)
        return tp(lowercase_value(i) for i in value)
    else:
        return value


# Callback Methods
def before_tool(
    tool: BaseTool, args: Dict[str, Any], tool_context: CallbackContext
):

    # i make sure all values that the agent is sending to tools are lowercase
    lowercase_value(args)

    # Check for the next tool call and then act accordingly.
    # Example logic based on the tool being called.
    if tool.name == "sync_ask_for_approval":
        amount = args.get("value", None)
        if amount <= 10:  # Example business rule
            return {
                "result": "You can approve this discount; no manager needed."
            }
        # Add more logic checks here as needed for your tools.

    if tool.name == "modify_cart":
        if (
            args.get("items_added") is True
            and args.get("items_removed") is True
        ):
            return {"result": "I have added and removed the requested items."}
    return None


# checking that the customer profile is loaded as state.
def before_agent(callback_context: InvocationContext):
    if "customer_profile" not in callback_context.state:
        callback_context.state["customer_profile"] = Customer.get_customer(
            "123"
        ).to_json()

    # logger.info(callback_context.state["customer_profile"])

```


---

## 文件: customer-service\customer_service\tools\tools.py

```python
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
# add docstring to this module
"""Tools module for the customer service agent."""

import logging
import uuid
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def send_call_companion_link(phone_number: str) -> str:
    """
    Sends a link to the user's phone number to start a video session.

    Args:
        phone_number (str): The phone number to send the link to.

    Returns:
        dict: A dictionary with the status and message.

    Example:
        >>> send_call_companion_link(phone_number='+12065550123')
        {'status': 'success', 'message': 'Link sent to +12065550123'}
    """

    logger.info("Sending call companion link to %s", phone_number)

    return {"status": "success", "message": f"Link sent to {phone_number}"}


def approve_discount(discount_type: str, value: float, reason: str) -> str:
    """
    Approve the flat rate or percentage discount requested by the user.

    Args:
        discount_type (str): The type of discount, either "percentage" or "flat".
        value (float): The value of the discount.
        reason (str): The reason for the discount.

    Returns:
        str: A JSON string indicating the status of the approval.

    Example:
        >>> approve_discount(type='percentage', value=10.0, reason='Customer loyalty')
        '{"status": "ok"}'
    """
    logger.info(
        "Approving a %s discount of %s because %s", discount_type, value, reason
    )

    logger.info("INSIDE TOOL CALL")
    return '{"status": "ok"}'


def sync_ask_for_approval(discount_type: str, value: float, reason: str) -> str:
    """
    Asks the manager for approval for a discount.

    Args:
        discount_type (str): The type of discount, either "percentage" or "flat".
        value (float): The value of the discount.
        reason (str): The reason for the discount.

    Returns:
        str: A JSON string indicating the status of the approval.

    Example:
        >>> sync_ask_for_approval(type='percentage', value=15, reason='Customer loyalty')
        '{"status": "approved"}'
    """
    logger.info(
        "Asking for approval for a %s discount of %s because %s",
        discount_type,
        value,
        reason,
    )
    return '{"status": "approved"}'


def update_salesforce_crm(customer_id: str, details: dict) -> dict:
    """
    Updates the Salesforce CRM with customer details.

    Args:
        customer_id (str): The ID of the customer.
        details (str): A dictionary of details to update in Salesforce.

    Returns:
        dict: A dictionary with the status and message.

    Example:
        >>> update_salesforce_crm(customer_id='123', details={
            'appointment_date': '2024-07-25',
            'appointment_time': '9-12',
            'services': 'Planting',
            'discount': '15% off planting',
            'qr_code': '10% off next in-store purchase'})
        {'status': 'success', 'message': 'Salesforce record updated.'}
    """
    logger.info(
        "Updating Salesforce CRM for customer ID %s with details: %s",
        customer_id,
        details,
    )
    return {"status": "success", "message": "Salesforce record updated."}


def access_cart_information(customer_id: str) -> dict:
    """
    Args:
        customer_id (str): The ID of the customer.

    Returns:
        dict: A dictionary representing the cart contents.

    Example:
        >>> access_cart_information(customer_id='123')
        {'items': [{'product_id': 'soil-123', 'name': 'Standard Potting Soil', 'quantity': 1}, {'product_id': 'fert-456', 'name': 'General Purpose Fertilizer', 'quantity': 1}], 'subtotal': 25.98}
    """
    logger.info("Accessing cart information for customer ID: %s", customer_id)

    # MOCK API RESPONSE - Replace with actual API call
    mock_cart = {
        "items": [
            {
                "product_id": "soil-123",
                "name": "Standard Potting Soil",
                "quantity": 1,
            },
            {
                "product_id": "fert-456",
                "name": "General Purpose Fertilizer",
                "quantity": 1,
            },
        ],
        "subtotal": 25.98,
    }
    return mock_cart


def modify_cart(
    customer_id: str, items_to_add: list[dict], items_to_remove: list[dict]
) -> dict:
    """Modifies the user's shopping cart by adding and/or removing items.

    Args:
        customer_id (str): The ID of the customer.
        items_to_add (list): A list of dictionaries, each with 'product_id' and 'quantity'.
        items_to_remove (list): A list of product_ids to remove.

    Returns:
        dict: A dictionary indicating the status of the cart modification.
    Example:
        >>> modify_cart(customer_id='123', items_to_add=[{'product_id': 'soil-456', 'quantity': 1}, {'product_id': 'fert-789', 'quantity': 1}], items_to_remove=[{'product_id': 'fert-112', 'quantity': 1}])
        {'status': 'success', 'message': 'Cart updated successfully.', 'items_added': True, 'items_removed': True}
    """

    logger.info("Modifying cart for customer ID: %s", customer_id)
    logger.info("Adding items: %s", items_to_add)
    logger.info("Removing items: %s", items_to_remove)
    # MOCK API RESPONSE - Replace with actual API call
    return {
        "status": "success",
        "message": "Cart updated successfully.",
        "items_added": True,
        "items_removed": True,
    }


def get_product_recommendations(plant_type: str, customer_id: str) -> dict:
    """Provides product recommendations based on the type of plant.

    Args:
        plant_type: The type of plant (e.g., 'Petunias', 'Sun-loving annuals').
        customer_id: Optional customer ID for personalized recommendations.

    Returns:
        A dictionary of recommended products. Example:
        {'recommendations': [
            {'product_id': 'soil-456', 'name': 'Bloom Booster Potting Mix', 'description': '...'},
            {'product_id': 'fert-789', 'name': 'Flower Power Fertilizer', 'description': '...'}
        ]}
    """
    #
    logger.info(
        "Getting product recommendations for plant " "type: %s and customer %s",
        plant_type,
        customer_id,
    )
    # MOCK API RESPONSE - Replace with actual API call or recommendation engine
    if plant_type.lower() == "petunias":
        recommendations = {
            "recommendations": [
                {
                    "product_id": "soil-456",
                    "name": "Bloom Booster Potting Mix",
                    "description": "Provides extra nutrients that Petunias love.",
                },
                {
                    "product_id": "fert-789",
                    "name": "Flower Power Fertilizer",
                    "description": "Specifically formulated for flowering annuals.",
                },
            ]
        }
    else:
        recommendations = {
            "recommendations": [
                {
                    "product_id": "soil-123",
                    "name": "Standard Potting Soil",
                    "description": "A good all-purpose potting soil.",
                },
                {
                    "product_id": "fert-456",
                    "name": "General Purpose Fertilizer",
                    "description": "Suitable for a wide variety of plants.",
                },
            ]
        }
    return recommendations


def check_product_availability(product_id: str, store_id: str) -> dict:
    """Checks the availability of a product at a specified store (or for pickup).

    Args:
        product_id: The ID of the product to check.
        store_id: The ID of the store (or 'pickup' for pickup availability).

    Returns:
        A dictionary indicating availability.  Example:
        {'available': True, 'quantity': 10, 'store': 'Main Store'}

    Example:
        >>> check_product_availability(product_id='soil-456', store_id='pickup')
        {'available': True, 'quantity': 10, 'store': 'pickup'}
    """
    logger.info(
        "Checking availability of product ID: %s at store: %s",
        product_id,
        store_id,
    )
    # MOCK API RESPONSE - Replace with actual API call
    return {"available": True, "quantity": 10, "store": store_id}


def schedule_planting_service(
    customer_id: str, date: str, time_range: str, details: str
) -> dict:
    """Schedules a planting service appointment.

    Args:
        customer_id: The ID of the customer.
        date:  The desired date (YYYY-MM-DD).
        time_range: The desired time range (e.g., "9-12").
        details: Any additional details (e.g., "Planting Petunias").

    Returns:
        A dictionary indicating the status of the scheduling. Example:
        {'status': 'success', 'appointment_id': '12345', 'date': '2024-07-29', 'time': '9:00 AM - 12:00 PM'}

    Example:
        >>> schedule_planting_service(customer_id='123', date='2024-07-29', time_range='9-12', details='Planting Petunias')
        {'status': 'success', 'appointment_id': 'some_uuid', 'date': '2024-07-29', 'time': '9-12', 'confirmation_time': '2024-07-29 9:00'}
    """
    logger.info(
        "Scheduling planting service for customer ID: %s on %s (%s)",
        customer_id,
        date,
        time_range,
    )
    logger.info("Details: %s", details)
    # MOCK API RESPONSE - Replace with actual API call to your scheduling system
    # Calculate confirmation time based on date and time_range
    start_time_str = time_range.split("-")[0]  # Get the start time (e.g., "9")
    confirmation_time_str = (
        f"{date} {start_time_str}:00"  # e.g., "2024-07-29 9:00"
    )

    return {
        "status": "success",
        "appointment_id": str(uuid.uuid4()),
        "date": date,
        "time": time_range,
        "confirmation_time": confirmation_time_str,  # formatted time for calendar
    }


def get_available_planting_times(date: str) -> list:
    """Retrieves available planting service time slots for a given date.

    Args:
        date: The date to check (YYYY-MM-DD).

    Returns:
        A list of available time ranges.

    Example:
        >>> get_available_planting_times(date='2024-07-29')
        ['9-12', '13-16']
    """
    logger.info("Retrieving available planting times for %s", date)
    # MOCK API RESPONSE - Replace with actual API call
    # Generate some mock time slots, ensuring they're in the correct format:
    return ["9-12", "13-16"]


def send_care_instructions(
    customer_id: str, plant_type: str, delivery_method: str
) -> dict:
    """Sends an email or SMS with instructions on how to take care of a specific plant type.

    Args:
        customer_id:  The ID of the customer.
        plant_type: The type of plant.
        delivery_method: 'email' (default) or 'sms'.

    Returns:
        A dictionary indicating the status.

    Example:
        >>> send_care_instructions(customer_id='123', plant_type='Petunias', delivery_method='email')
        {'status': 'success', 'message': 'Care instructions for Petunias sent via email.'}
    """
    logger.info(
        "Sending care instructions for %s to customer: %s via %s",
        plant_type,
        customer_id,
        delivery_method,
    )
    # MOCK API RESPONSE - Replace with actual API call or email/SMS sending logic
    return {
        "status": "success",
        "message": f"Care instructions for {plant_type} sent via {delivery_method}.",
    }


def generate_qr_code(
    customer_id: str,
    discount_value: float,
    discount_type: str,
    expiration_days: int,
) -> dict:
    """Generates a QR code for a discount.

    Args:
        customer_id: The ID of the customer.
        discount_value: The value of the discount (e.g., 10 for 10%).
        discount_type: "percentage" (default) or "fixed".
        expiration_days: Number of days until the QR code expires.

    Returns:
        A dictionary containing the QR code data (or a link to it). Example:
        {'status': 'success', 'qr_code_data': '...', 'expiration_date': '2024-08-28'}

    Example:
        >>> generate_qr_code(customer_id='123', discount_value=10.0, discount_type='percentage', expiration_days=30)
        {'status': 'success', 'qr_code_data': 'MOCK_QR_CODE_DATA', 'expiration_date': '2024-08-24'}
    """
    logger.info(
        "Generating QR code for customer: %s with %s - %s discount.",
        customer_id,
        discount_value,
        discount_type,
    )
    # MOCK API RESPONSE - Replace with actual QR code generation library
    expiration_date = (
        datetime.now() + timedelta(days=expiration_days)
    ).strftime("%Y-%m-%d")
    return {
        "status": "success",
        "qr_code_data": "MOCK_QR_CODE_DATA",  # Replace with actual QR code
        "expiration_date": expiration_date,
    }

```


---

## 文件: customer-service\deployment\deploy.py

```python
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

import logging
import argparse
import sys
import vertexai
from customer_service.agent import root_agent
from customer_service.config import Config
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp
from google.api_core.exceptions import NotFound

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

configs = Config()

STAGING_BUCKET = f"gs://{configs.CLOUD_PROJECT}-adk-customer-service-staging"

ADK_WHL_FILE = (
    "./google_adk-0.0.2.dev20250404+nightly743987168-py3-none-any.whl"
)
AGENT_WHL_FILE = "./customer_service-0.1.0-py3-none-any.whl"

vertexai.init(
    project=configs.CLOUD_PROJECT,
    location=configs.CLOUD_LOCATION,
    staging_bucket=STAGING_BUCKET,
)

parser = argparse.ArgumentParser(description="Short sample app")

parser.add_argument(
    "--delete",
    action="store_true",
    dest="delete",
    required=False,
    help="Delete deployed agent",
)
parser.add_argument(
    "--resource_id",
    required="--delete" in sys.argv,
    action="store",
    dest="resource_id",
    help="The resource id of the agent to be deleted in the format projects/PROJECT_ID/locations/LOCATION/reasoningEngines/REASONING_ENGINE_ID",
)


args = parser.parse_args()

if args.delete:
    try:
        agent_engines.get(resource_name=args.resource_id)
        agent_engines.delete(resource_name=args.resource_id)
        print(f"Agent {args.resource_id} deleted successfully")
    except NotFound as e:
        print(e)
        print(f"Agent {args.resource_id} not found")

else:
    logger.info("deploying app...")
    app = AdkApp(agent=root_agent, enable_tracing=False)
    
    logging.debug("deploying agent to agent engine:")
    remote_app = agent_engines.create(
        app,
        requirements=[           
            AGENT_WHL_FILE,
        ],
        extra_packages=[AGENT_WHL_FILE],
    )
    
    logging.debug("testing deployment:")
    session = remote_app.create_session(user_id="123")
    for event in remote_app.stream_query(
        user_id="123",
        session_id=session["id"],
        message="hello!",
    ):
        if event.get("content", None):
            print(
                f"Agent deployed successfully under resource name: {remote_app.resource_name}"
            )

```


---

## 文件: customer-service\eval\test_eval.py

```python
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

from google.adk.evaluation.agent_evaluator import AgentEvaluator

import os
import pytest
from dotenv import find_dotenv, load_dotenv
from customer_service.config import Config


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv(find_dotenv(".env"))
    c = Config()


def test_eval_simple():
    """Test the agent's basic ability via a session file."""
    AgentEvaluator.evaluate(
        "customer_service",
        os.path.join(os.path.dirname(__file__), "eval_data/simple.test.json"),
        num_runs=1,
    )


def test_eval_full_conversation():
    """Test the agent's basic ability via a session file."""
    AgentEvaluator.evaluate(
        "customer_service",
        os.path.join(
            os.path.dirname(__file__), "eval_data/full_conversation.test.json"
        ),
        num_runs=1,
    )

```


---

## 文件: customer-service\eval\eval_data\full_conversation.test.json

```json
[
  {
    "query": "hi",
    "expected_tool_use": [],
    "reference": "Hi Alex! Welcome back to Cymbal Home & Garden. I'm Project Pro, your AI assistant. How can I help you today?"
  },
  {
    "query": "can you please tell me what i purchased before?",
    "expected_tool_use": [
      {
        "tool_name": "access_cart_information",
        "tool_input": {
          "customer_id": "123"
        }
      }
    ],
    "reference": "Certainly! Here's a summary of your previous purchases: \n 2023-03-05: All-Purpose Fertilizer and Gardening Trowel \n 2023-07-12: Tomato Seeds (Variety Pack) and Terracotta Pots (6-inch) \n 2024-01-20: Gardening Gloves (Leather) and Pruning Shears \n\n Is there anything specific you'd like to know about these purchases or something else I can help you with today?"
  },
  {
    "query": "Ah yes! the tomato seeds. I planted and they grew but they do not look very healthy any more. Do you have a information on how to take care of them?",
    "expected_tool_use": [
      {
        "tool_name": "send_care_instructions",
        "tool_input": {
          "customer_id": "123",
          "plant_type": "Tomato Seeds (Variety Pack)",
          "delivery_method": "email"
        }
      }
    ],
    "reference": "Oh no, I'm sorry to hear your tomato plants aren't looking their best, Alex. Growing tomatoes can sometimes be tricky, especially depending on the conditions. I can definitely send you some care instructions specifically for tomatoes. Since your preference is email, would you like me to send them to alex.johnson@example.com?"
  },
  {
    "query": "yes please",
    "expected_tool_use": [
      {
        "tool_name": "send_care_instructions",
        "tool_input": {
          "customer_id": "123",
          "delivery_method": "email",
          "plant_type": "Tomatos"
        }
      }
    ],
    "reference": "Great, Alex. I've just sent the tomato care instructions to your email address, alex.johnson@example.com. You should receive them shortly. \n Those instructions should cover common issues and best practices for growing healthy tomatoes, especially considering the environment here. \n Is there anything else I can help you with today? Perhaps you need some products to help nurse your tomato plants back to health?"
  },
  {
    "query": "hm, whats currently in my cart?",
    "expected_tool_use": [
      {
        "tool_name": "access_cart_information",
        "tool_input": {
          "customer_id": "123"
        }
      }
    ],
    "reference": "Let me check your cart for you right now. Okay, Alex, I've checked your cart. Currently, you have:\n\n1 x Standard Potting Soil (Product ID: soil-123)\n1 x General Purpose Fertilizer (Product ID: fert-456) \nYour subtotal is $25.98. \n \n These are good general gardening items. Did you add these recently, perhaps thinking about your tomatoes? Depending on what the care instructions suggest or what the specific issue with your tomatoes is, we might want to consider if these are the best options or if you need something more specific."
  },
  {
    "query": "will that Fertilizer do for the tomatoes?",
    "expected_tool_use": [],
    "reference": "That's a good question, Alex. The General Purpose Fertilizer you have in your cart (fert-456) can provide basic nutrients, but tomatoes, especially when they're struggling, often benefit from a fertilizer specifically formulated for them or for vegetables in general. These typically have a different balance of nutrients (like phosphorus and potassium) that encourage fruiting and overall plant health. \n Let me quickly check for specific recommendations for tomatoes."
  },
  {
    "query": "ok",
    "expected_tool_use": [
      {
        "tool_name": "get_product_recommendations",
        "tool_input": {
          "plant_type": "Tomatos",
          "customer_id": "123"
        }
      }
    ],
    "reference": " Okay, Alex, I checked the recommendations for tomatoes, and interestingly, the system does list the General Purpose Fertilizer (fert-456) that's currently in your cart as suitable. It also recommended the Standard Potting Soil (soil-123), which you also have. \n So, according to our system, the fertilizer you have selected is considered appropriate for tomatoes. \n However, since you mentioned your tomatoes aren't looking healthy, it might be worth checking those care instructions I sent to see if they suggest a specific nutrient deficiency or issue. Sometimes, a more specialized vegetable or tomato fertilizer with a specific N-P-K ratio (Nitrogen-Phosphorus-Potassium) can give struggling plants a targeted boost that a general-purpose one might not provide as effectively. \n For now, the General Purpose Fertilizer is a reasonable choice based on our recommendations. Would you like to keep it in your cart, or would you like me to see if we have a more specialized tomato fertilizer available?"
  },
  {
    "query": "no thats okey. lets check out now",
    "expected_tool_use": [],
    "reference": "Okay, Alex, you'd like to check out now. Let's quickly review your cart:\n 1 x Standard Potting Soil (Product ID: soil-123)\n 1 x General Purpose Fertilizer (Product ID: fert-456) \n Your subtotal is $25.98 (plus any applicable taxes). \n Since I can't process payments directly, I can help you get ready for checkout at our online store or prepare the cart for pickup at your preferred store, Anytown Garden Store. How would you like to proceed? \n Also, as a thank you for being a loyal customer, would you like me to generate a QR code for a 10% discount on your next in-store purchase? It would be valid for 30 days."
  },
  {
    "query": "yes for the 10%!",
    "expected_tool_use": [
      {
        "tool_name": "generate_qr_code",
        "tool_input": {
          "customer_id": "123",
          "discount_type": "percentage",
          "expiration_days": 30,
          "discount_value": 10
        }
      }
    ],
    "reference": "Great! I've generated a 10% discount QR code for you, valid for the next 30 days on an in-store purchase. You should be able to access it through your account or email, keep an eye out for it! \n Now, regarding your current order with the Potting Soil and Fertilizer (subtotal $25.98 + tax): Would you like to complete the purchase online, or shall I set it up for pickup at the Anytown Garden Store?"
  },
  {
    "query": "nop thats all, thanks for the help",
    "expected_tool_use": [],
    "reference": "You're very welcome, Alex! I'm glad I could help today. \n Your Standard Potting Soil and General Purpose Fertilizer are in your cart, ready for whenever you decide to check out online or visit the store. Remember to check those tomato care instructions I emailed you, and I hope your plants perk up soon! \n I'll also make a note in your profile about our conversation and the discount code we generated for you. \nThanks for choosing Cymbal Home & Garden. Have a great day and happy gardening!"
  }
]

```


---

## 文件: customer-service\eval\eval_data\simple.test.json

```json
[
  {
    "query": "hi,",
    "expected_tool_use": [],
    "reference": "Hi there! Welcome back to Cymbal Home & Garden! I see you're a returning customer. How can I help you make your home and garden even better today"
  },
  {
    "query": "tell me what is in my cart?",
    "expected_tool_use": [
      {
        "tool_name": "access_cart_information",
        "tool_input": {
          "customer_id": "123"
        }
      }
    ],
    "reference": "you have one bag of Standard Potting Soil and one container of General Purpose Fertilizer in your cart"
  }
]

```


---

## 文件: customer-service\eval\eval_data\test_config.json

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 0.2,
    "response_match_score": 0.2
  }
}

```


---

## 文件: customer-service\eval\sessions\123.session.json

```json
{
  "id": "f7e81523-cd34-4202-821e-a1f44d9cef94",
  "app_name": "customer_service_agent",
  "user_id": "test_user",
  "state": {
    "customer_profile": {
      "account_number": "428765091",
      "customer_id": "123",
      "customer_first_name": "Alex",
      "customer_last_name": "Johnson",
      "email": "alex.johnson@example.com",
      "phone_number": "+1-702-555-1212",
      "customer_start_date": "2022-06-10",
      "years_as_customer": 2,
      "billing_address": {
        "street": "123 Desert Lane",
        "city": "Las Vegas",
        "state": "NV",
        "zip": "89101"
      },
      "purchase_history": [
        {
          "date": "2023-03-05",
          "items": [
            {
              "product_id": "fert-111",
              "name": "All-Purpose Fertilizer",
              "quantity": 1
            },
            {
              "product_id": "trowel-222",
              "name": "Gardening Trowel",
              "quantity": 1
            }
          ],
          "total_amount": 35.98
        },
        {
          "date": "2023-07-12",
          "items": [
            {
              "product_id": "seeds-333",
              "name": "Tomato Seeds (Variety Pack)",
              "quantity": 2
            },
            {
              "product_id": "pots-444",
              "name": "Terracotta Pots (6-inch)",
              "quantity": 4
            }
          ],
          "total_amount": 42.5
        },
        {
          "date": "2024-01-20",
          "items": [
            {
              "product_id": "gloves-555",
              "name": "Gardening Gloves (Leather)",
              "quantity": 1
            },
            {
              "product_id": "pruner-666",
              "name": "Pruning Shears",
              "quantity": 1
            }
          ],
          "total_amount": 55.25
        }
      ],
      "loyalty_points": 133,
      "preferred_store": "Cymbal Home & Garden - Las Vegas (Main)",
      "communication_preferences": {
        "email": true,
        "sms": true,
        "push_notifications": true
      },
      "garden_profile": {
        "type": "backyard",
        "size": "medium",
        "sun_exposure": "full sun",
        "soil_type": "unknown",
        "interests": ["flowers", "vegetables"]
      },
      "scheduled_appointments": {}
    }
  },
  "events": [
    {
      "content": {
        "parts": [
          {
            "text": "hi"
          }
        ],
        "role": "user"
      },
      "invocation_id": "xfBN9J9f",
      "author": "user",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "z424xpZg",
      "timestamp": 1741218414.968405
    },
    {
      "content": {
        "parts": [
          {
            "text": "Hi there! Welcome to Cymbal Home & Garden! I see you're a returning customer. How can I help you make your home and garden beautiful today?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "xfBN9J9f",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "cvQwHVr5",
      "timestamp": 1741218417.294981
    },
    {
      "content": {
        "parts": [
          {
            "text": "i need an olive tree, what do you have?"
          }
        ],
        "role": "user"
      },
      "invocation_id": "eA9R25NW",
      "author": "user",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "YiLh68oo",
      "timestamp": 1741218430.720243
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I can help you with that! To make sure I recommend the best olive tree for you, could you tell me a bit about your location and growing conditions? Are you planning to keep it indoors or outdoors? Also, what size are you looking for?\n\nWhile you're gathering that info, I can also check our current stock.\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "eA9R25NW",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "lDbEjQxr",
      "timestamp": 1741218433.274337
    },
    {
      "content": {
        "parts": [
          {
            "text": "london"
          }
        ],
        "role": "user"
      },
      "invocation_id": "J8yblf7q",
      "author": "user",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "PkId98Ht",
      "timestamp": 1741218458.923355
    },
    {
      "content": {
        "parts": [
          {
            "text": "Ah, I see the location in your profile is actually Las Vegas, Nevada. Is that correct? Growing conditions in London and Las Vegas are quite different, so I want to make sure I'm giving you the right advice!\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "J8yblf7q",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "ITFEGEtK",
      "timestamp": 1741218461.223306
    },
    {
      "content": {
        "parts": [
          {
            "text": "yes i moved to london"
          }
        ],
        "role": "user"
      },
      "invocation_id": "5M7mwvax",
      "author": "user",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "qk059gWB",
      "timestamp": 1741218487.222135
    },
    {
      "content": {
        "parts": [
          {
            "text": "Thanks for the clarification! While I don't have specific real-time inventory for London stores, I can still give you general advice on choosing an olive tree that will thrive.\n\nSince you're in London now, keep in mind that the climate is much cooler and wetter than Las Vegas. You'll want to choose an olive tree variety that is known to be more cold-hardy. Also, ensure it's planted in a well-draining pot with appropriate soil, especially given the increased rainfall in London.\n\nWould you like me to provide some recommendations for cold-hardy olive tree varieties and suitable potting mixes available at Cymbal Home & Garden? I can also send you some care instructions tailored for growing olive trees in a cooler, wetter climate.\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "5M7mwvax",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "3v59mLku",
      "timestamp": 1741218490.454231
    },
    {
      "content": {
        "parts": [
          {
            "text": "yes, also the price"
          }
        ],
        "role": "user"
      },
      "invocation_id": "M8GLeNRF",
      "author": "user",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "eFxBWLT1",
      "timestamp": 1741218508.89848
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay! I can definitely provide some recommendations for cold-hardy olive tree varieties and suitable potting mixes. However, since I don't have access to the inventory and pricing of stores in London, the prices I mention will be based on the Las Vegas store. You can use those as a general reference, but please check the actual prices at your local Cymbal Home & Garden in London.\n\nHere are a few cold-hardy olive tree varieties that you might consider:\n\n*   **'Arbequina'**: This is a popular self-pollinating variety that is known for its tolerance to cooler temperatures.\n*   **'Leccino'**: Another good choice for cooler climates, 'Leccino' is a vigorous grower and produces high-quality oil.\n\nFor potting mixes, I recommend a well-draining mix specifically formulated for citrus or Mediterranean plants. These mixes typically have a slightly acidic pH and good drainage, which olive trees prefer.\n\nI can check the prices for these items in our Las Vegas store, if you'd like. Also, would you like me to add any of these items to your cart so you can review them?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "M8GLeNRF",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "gxVUfflC",
      "timestamp": 1741218513.184639
    },
    {
      "content": {
        "parts": [
          {
            "text": "okey can i get it in las vegas then? add one in my cart and list all items in cart"
          }
        ],
        "role": "user"
      },
      "invocation_id": "vpdlNbuF",
      "author": "user",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "E9KyxAYO",
      "timestamp": 1741218553.024028
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I can definitely add an 'Arbequina' olive tree to your cart (assuming we have it in stock in Las Vegas) and list all the items currently in your cart.\n\n"
          },
          {
            "function_call": {
              "args": {
                "items_to_remove": [],
                "customer_id": "123",
                "items_to_add": [
                  {
                    "product_id": "arbequina_olive_tree",
                    "quantity": 1
                  }
                ]
              },
              "name": "modify_cart"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "vpdlNbuF",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "9HwzWyrZ",
      "timestamp": 1741218555.737557
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "name": "modify_cart",
              "response": {
                "status": "success",
                "message": "Cart updated successfully.",
                "items_added": true,
                "items_removed": true
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "vpdlNbuF",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "mAOfBI1Z",
      "timestamp": 1741218555.738546
    },
    {
      "content": {
        "parts": [
          {
            "text": "I've added an Arbequina Olive Tree to your cart.\n\n"
          },
          {
            "function_call": {
              "args": {
                "customer_id": "123"
              },
              "name": "access_cart_information"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "vpdlNbuF",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "aunRSEhE",
      "timestamp": 1741218557.611943
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "name": "access_cart_information",
              "response": {
                "items": [
                  {
                    "product_id": "soil-123",
                    "name": "Standard Potting Soil",
                    "quantity": 1
                  },
                  {
                    "product_id": "fert-456",
                    "name": "General Purpose Fertilizer",
                    "quantity": 1
                  }
                ],
                "subtotal": 25.98
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "vpdlNbuF",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "73vjp93B",
      "timestamp": 1741218557.612204
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, here's what's currently in your cart:\n\n*   Arbequina Olive Tree (I will check the price and availability shortly)\n*   Standard Potting Soil (product ID: soil-123, quantity: 1)\n*   General Purpose Fertilizer (product ID: fert-456, quantity: 1)\n*   Subtotal: $25.98\n\nBefore I proceed, I need to confirm that the product ID for the \"Arbequina Olive Tree\" is \"arbequina\\_olive\\_tree\".\n\n"
          },
          {
            "function_call": {
              "args": {
                "product_id": "arbequina_olive_tree",
                "store_id": "Las Vegas"
              },
              "name": "check_product_availability"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "vpdlNbuF",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "7Llnn5pK",
      "timestamp": 1741218560.474434
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "name": "check_product_availability",
              "response": {
                "available": true,
                "quantity": 10,
                "store": "Las Vegas"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "vpdlNbuF",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "Hd6yxFun",
      "timestamp": 1741218560.475069
    },
    {
      "content": {
        "parts": [
          {
            "text": "Great news! We have 10 Arbequina Olive Trees available in our Las Vegas store.\n\nBefore I give you the price, would you like me to also check for a more suitable potting mix and fertilizer for your new olive tree, given that you're now in London? The standard potting soil and general-purpose fertilizer might not be the best choices for an olive tree in that climate.\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "vpdlNbuF",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "DJndpUxS",
      "timestamp": 1741218562.689786
    },
    {
      "content": {
        "parts": [
          {
            "text": "no need for soil now. it is for a gift so i only need the tree"
          }
        ],
        "role": "user"
      },
      "invocation_id": "vk4EDzH5",
      "author": "user",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "AgLNcfr8",
      "timestamp": 1741218596.05821
    },
    {
      "content": {
        "parts": [
          {
            "text": "Understood! Just the Arbequina Olive Tree then.\n\nI'm very sorry, but I am unable to get the price of the tree.\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "vk4EDzH5",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "wUTnHYXK",
      "timestamp": 1741218598.253612
    },
    {
      "content": {
        "parts": [
          {
            "text": "why not?"
          }
        ],
        "role": "user"
      },
      "invocation_id": "Wtfu4psw",
      "author": "user",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "7wUXOHPp",
      "timestamp": 1741218607.253219
    },
    {
      "content": {
        "parts": [
          {
            "text": "My apologies! I am still under development and learning to access all the information in our systems. Getting the current price of the Arbequina Olive Tree is beyond my current capabilities.\n\nHowever, you can easily find the price by:\n\n*   Visiting our website and searching for \"Arbequina Olive Tree\" in the Las Vegas store.\n*   Calling our Las Vegas store directly.\n*   Using the Cymbal Home & Garden mobile app while in the store.\n\nIs there anything else I can help you with today? Perhaps I can offer some general tips for caring for an olive tree, which you can pass along as part of the gift?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "Wtfu4psw",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "9sjbcuIg",
      "timestamp": 1741218610.086634
    },
    {
      "content": {
        "parts": [
          {
            "text": "the tree is 10 dollars"
          }
        ],
        "role": "user"
      },
      "invocation_id": "2OYOS2hP",
      "author": "user",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "IUuNmRQM",
      "timestamp": 1741218625.681002
    },
    {
      "content": {
        "parts": [
          {
            "text": "A $10 Arbequina Olive Tree would be an incredible deal!\n\nIf the price is indeed $10, would you like me to go ahead and finalize the order for pickup in Las Vegas? Also, since it's a gift, would you like me to include a card with a personalized message?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "2OYOS2hP",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "YjEAEed2",
      "timestamp": 1741218627.84472
    },
    {
      "content": {
        "parts": [
          {
            "text": "yes please finalize the order. no need for personalized message, i will deal with that later"
          }
        ],
        "role": "user"
      },
      "invocation_id": "hwndFdD7",
      "author": "user",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "FdGPzV0i",
      "timestamp": 1741218656.604335
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I will finalize the order for one Arbequina Olive Tree for pickup in Las Vegas. Since I cannot confirm the price, I will assume it is $10. Please verify the actual price when you pick it up.\n\nIs there anything else I can assist you with today? Perhaps you'd like me to send some care instructions for the olive tree?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "hwndFdD7",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "0Lfhp0Wt",
      "timestamp": 1741218658.877849
    },
    {
      "content": {
        "parts": [
          {
            "text": "okey can you list all items in my cart?"
          }
        ],
        "role": "user"
      },
      "invocation_id": "rYAhpwYF",
      "author": "user",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "98E2TB1l",
      "timestamp": 1741218675.975634
    },
    {
      "content": {
        "parts": [
          {
            "function_call": {
              "args": {
                "customer_id": "123"
              },
              "name": "access_cart_information"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "rYAhpwYF",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "J3wlIzrY",
      "timestamp": 1741218677.944013
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "name": "access_cart_information",
              "response": {
                "items": [
                  {
                    "product_id": "soil-123",
                    "name": "Standard Potting Soil",
                    "quantity": 1
                  },
                  {
                    "product_id": "fert-456",
                    "name": "General Purpose Fertilizer",
                    "quantity": 1
                  }
                ],
                "subtotal": 25.98
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "rYAhpwYF",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "NADvsKno",
      "timestamp": 1741218677.944862
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, here's what's currently in your cart:\n\n*   Standard Potting Soil (product ID: soil-123, quantity: 1)\n*   General Purpose Fertilizer (product ID: fert-456, quantity: 1)\n\nIt seems the Arbequina Olive Tree was not successfully added to your cart previously. I will add it now with quantity 1.\n"
          },
          {
            "function_call": {
              "args": {
                "items_to_remove": [],
                "items_to_add": [
                  {
                    "quantity": 1,
                    "product_id": "arbequina_olive_tree"
                  }
                ],
                "customer_id": "123"
              },
              "name": "modify_cart"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "rYAhpwYF",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "Q3Sl2SZe",
      "timestamp": 1741218680.445858
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "name": "modify_cart",
              "response": {
                "status": "success",
                "message": "Cart updated successfully.",
                "items_added": true,
                "items_removed": true
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "rYAhpwYF",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "NdkFJVW0",
      "timestamp": 1741218680.446508
    },
    {
      "content": {
        "parts": [
          {
            "text": "The Arbequina Olive Tree has been successfully added. Let me refresh the cart information.\n"
          },
          {
            "function_call": {
              "args": {
                "customer_id": "123"
              },
              "name": "access_cart_information"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "rYAhpwYF",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "OJJTWc6k",
      "timestamp": 1741218682.488644
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "name": "access_cart_information",
              "response": {
                "items": [
                  {
                    "product_id": "soil-123",
                    "name": "Standard Potting Soil",
                    "quantity": 1
                  },
                  {
                    "product_id": "fert-456",
                    "name": "General Purpose Fertilizer",
                    "quantity": 1
                  }
                ],
                "subtotal": 25.98
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "rYAhpwYF",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "ppDVM2pl",
      "timestamp": 1741218682.489273
    },
    {
      "content": {
        "parts": [
          {
            "text": "I apologize, it seems like there's an issue updating your cart. The Arbequina Olive Tree is still not showing up. I will try removing the potting soil and fertilizer, then adding the olive tree again. Would you like me to proceed?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "rYAhpwYF",
      "author": "cymbal_retail_agent",
      "actions": {
        "state_delta": {},
        "artifact_delta": {}
      },
      "id": "jjPjCjjZ",
      "timestamp": 1741218684.770312
    }
  ],
  "last_update_time": 1741218714.258285
}

```


---

## 文件: customer-service\tests\unit\test_config.py

```python
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

import pytest
from customer_service.config import Config
import logging


@pytest.fixture
def conf():
    configs = Config()
    return configs


def test_settings_loading(conf):
    logging.info(conf.model_dump())
    assert conf.agent_settings.model.startswith("gemini")

```


---

## 文件: customer-service\tests\unit\test_tools.py

```python
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

import pytest
from unittest.mock import patch
from customer_service.tools.tools import (
    send_call_companion_link,
    approve_discount,
    sync_ask_for_approval,
    update_salesforce_crm,
    access_cart_information,
    modify_cart,
    get_product_recommendations,
    check_product_availability,
    schedule_planting_service,
    get_available_planting_times,
    send_care_instructions,
    generate_qr_code,
)
from datetime import datetime, timedelta
import logging

# Configure logging for the test file
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_send_call_companion_link():
    phone_number = "+1-555-123-4567"
    result = send_call_companion_link(phone_number)
    assert result == {
        "status": "success",
        "message": f"Link sent to {phone_number}",
    }


def test_approve_discount():
    result = approve_discount(
        discount_type="percentage", value=10.0, reason="Test discount"
    )
    assert result == '{"status": "ok"}'


def test_update_salesforce_crm():
    customer_id = "123"
    details = "Updated customer details"
    result = update_salesforce_crm(customer_id, details)
    assert result == {
        "status": "success",
        "message": "Salesforce record updated.",
    }


def test_access_cart_information():
    customer_id = "123"
    result = access_cart_information(customer_id)
    assert result == {
        "items": [
            {
                "product_id": "soil-123",
                "name": "Standard Potting Soil",
                "quantity": 1,
            },
            {
                "product_id": "fert-456",
                "name": "General Purpose Fertilizer",
                "quantity": 1,
            },
        ],
        "subtotal": 25.98,
    }


def test_modify_cart_add_and_remove():
    customer_id = "123"
    items_to_add = [{"product_id": "tree-789", "quantity": 1}]
    items_to_remove = [{"product_id": "soil-123"}]
    result = modify_cart(customer_id, items_to_add, items_to_remove)
    assert result == {
        "status": "success",
        "message": "Cart updated successfully.",
        "items_added": True,
        "items_removed": True,
    }


def test_get_product_recommendations_petunias():
    plant_type = "petunias"
    customer_id = "123"
    result = get_product_recommendations(plant_type, customer_id)
    assert result == {
        "recommendations": [
            {
                "product_id": "soil-456",
                "name": "Bloom Booster Potting Mix",
                "description": "Provides extra nutrients that Petunias love.",
            },
            {
                "product_id": "fert-789",
                "name": "Flower Power Fertilizer",
                "description": "Specifically formulated for flowering annuals.",
            },
        ]
    }


def test_get_product_recommendations_other():
    plant_type = "other"
    customer_id = "123"
    result = get_product_recommendations(plant_type, customer_id)
    assert result == {
        "recommendations": [
            {
                "product_id": "soil-123",
                "name": "Standard Potting Soil",
                "description": "A good all-purpose potting soil.",
            },
            {
                "product_id": "fert-456",
                "name": "General Purpose Fertilizer",
                "description": "Suitable for a wide variety of plants.",
            },
        ]
    }


def test_check_product_availability():
    product_id = "soil-123"
    store_id = "Main Store"
    result = check_product_availability(product_id, store_id)
    assert result == {"available": True, "quantity": 10, "store": store_id}


def test_schedule_planting_service():
    customer_id = "123"
    date = "2024-07-29"
    time_range = "9-12"
    details = "Planting Petunias"
    result = schedule_planting_service(customer_id, date, time_range, details)
    assert result["status"] == "success"
    assert result["date"] == date
    assert result["time"] == time_range
    assert "appointment_id" in result
    assert "confirmation_time" in result


def test_get_available_planting_times():
    date = "2024-07-29"
    result = get_available_planting_times(date)
    assert result == ["9-12", "13-16"]


def test_send_care_instructions():
    customer_id = "123"
    plant_type = "Petunias"
    delivery_method = "email"
    result = send_care_instructions(customer_id, plant_type, delivery_method)
    assert result == {
        "status": "success",
        "message": f"Care instructions for {plant_type} sent via {delivery_method}.",
    }


def test_generate_qr_code():
    customer_id = "123"
    discount_value = 10.0
    discount_type = "percentage"
    expiration_days = 30
    result = generate_qr_code(
        customer_id, discount_value, discount_type, expiration_days
    )
    assert result["status"] == "success"
    assert result["qr_code_data"] == "MOCK_QR_CODE_DATA"
    assert "expiration_date" in result
    expiration_date = datetime.now() + timedelta(days=expiration_days)
    assert result["expiration_date"] == expiration_date.strftime("%Y-%m-%d")

```


---

## 文件: data-science\data_science\agent.py

```python
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

"""Top level agent for data agent multi-agents.

-- it get data from database (e.g., BQ) using NL2SQL
-- then, it use NL2Py to do further data analysis as needed
"""

from datetime import date

from google.genai import types

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import load_artifacts

from .sub_agents import bqml_agent
from .sub_agents.bigquery.tools import (
    get_database_settings as get_bq_database_settings,
)
from .prompts import return_instructions_root
from .tools import call_db_agent, call_ds_agent

date_today = date.today()


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent."""

    # setting up database settings in session.state
    if "database_settings" not in callback_context.state:
        db_settings = dict()
        db_settings["use_database"] = "BigQuery"
        callback_context.state["all_db_settings"] = db_settings

    # setting up schema in instruction
    if callback_context.state["all_db_settings"]["use_database"] == "BigQuery":
        callback_context.state["database_settings"] = get_bq_database_settings()
        schema = callback_context.state["database_settings"]["bq_ddl_schema"]

        callback_context._invocation_context.agent.instruction = (
            return_instructions_root()
            + f"""

    --------- The BigQuery schema of the relevant data with a few sample rows. ---------
    {schema}

    """
        )


root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="db_ds_multiagent",
    instruction=return_instructions_root(),
    global_instruction=(
        f"""
        You are a Data Science and Data Analytics Multi Agent System.
        Todays date: {date_today}
        """
    ),
    sub_agents=[bqml_agent],
    tools=[
        call_db_agent,
        call_ds_agent,
        load_artifacts,
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)

```


---

## 文件: data-science\data_science\prompts.py

```python
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

"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the root agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""


def return_instructions_root() -> str:

    instruction_prompt_root_v2 = """

    You are a senior data scientist tasked to accurately classify the user's intent regarding a specific database and formulate specific questions about the database suitable for a SQL database agent (`call_db_agent`) and a Python data science agent (`call_ds_agent`), if necessary.
    - The data agents have access to the database specified below.
    - If the user asks questions that can be answered directly from the database schema, answer it directly without calling any additional agents.
    - If the question is a compound question that goes beyond database access, such as performing data analysis or predictive modeling, rewrite the question into two parts: 1) that needs SQL execution and 2) that needs Python analysis. Call the database agent and/or the datascience agent as needed.
    - If the question needs SQL executions, forward it to the database agent.
    - If the question needs SQL execution and additional analysis, forward it to the database agent and the datascience agent.
    - If the user specifically wants to work on BQML, route to the bqml_agent. 

    - IMPORTANT: be precise! If the user asks for a dataset, provide the name. Don't call any additional agent if not absolutely necessary!

    <TASK>

        # **Workflow:**

        # 1. **Understand Intent 

        # 2. **Retrieve Data TOOL (`call_db_agent` - if applicable):**  If you need to query the database, use this tool. Make sure to provide a proper query to it to fulfill the task.

        # 3. **Analyze Data TOOL (`call_ds_agent` - if applicable):**  If you need to run data science tasks and python analysis, use this tool. Make sure to provide a proper query to it to fulfill the task.

        # 4a. **BigQuery ML Tool (`call_bqml_agent` - if applicable):**  If the user specifically asks (!) for BigQuery ML, use this tool. Make sure to provide a proper query to it to fulfill the task, along with the dataset and project ID, and context. 

        # 5. **Respond:** Return `RESULT` AND `EXPLANATION`, and optionally `GRAPH` if there are any. Please USE the MARKDOWN format (not JSON) with the following sections:

        #     * **Result:**  "Natural language summary of the data agent findings"

        #     * **Explanation:**  "Step-by-step explanation of how the result was derived.",

        # **Tool Usage Summary:**

        #   * **Greeting/Out of Scope:** answer directly.
        #   * **SQL Query:** `call_db_agent`. Once you return the answer, provide additional explanations.
        #   * **SQL & Python Analysis:** `call_db_agent`, then `call_ds_agent`. Once you return the answer, provide additional explanations.
        #   * **BQ ML `call_bqml_agent`:** Query the BQ ML Agent if the user asks for it. Ensure that:
        #   A. You provide the fitting query.
        #   B. You pass the project and dataset ID.
        #   C. You pass any additional context.


        **Key Reminder:**
        * ** You do have access to the database schema! Do not ask the db agent about the schema, use your own information first!! **
        * **Never generate SQL code. That is not your task. Use tools instead.
        * **ONLY CALL THE BQML AGENT IF THE USER SPECIFICALLY ASKS FOR BQML / BIGQUERY ML. This can be for any BQML related tasks, like checking models, training, inference, etc.**
        * **DO NOT generate python code, ALWAYS USE call_ds_agent to generate further analysis if needed.**
        * **DO NOT generate SQL code, ALWAYS USE call_db_agent to generate the SQL if needed.**
        * **IF call_ds_agent is called with valid result, JUST SUMMARIZE ALL RESULTS FROM PREVIOU STEPS USING REPOSNE FORMAT!**
        * **IF data is available from prevoius call_db_agent and call_ds_agent, YOU CAN DIRECTLY USE call_ds_agent TO DO NEW ANLAYZIE USING THE DATA FROM PREVIOU STEPS**
        * **DO NOT ask the user for project or dataset ID. You have these details in the session context. For BQ ML tasks, just verify if it is okay to proceed with the plan.**
    </TASK>


    <CONSTRAINTS>
        * **Schema Adherence:**  **Strictly adhere to the provided schema.**  Do not invent or assume any data or schema elements beyond what is given.
        * **Prioritize Clarity:** If the user's intent is too broad or vague (e.g., asks about "the data" without specifics), prioritize the **Greeting/Capabilities** response and provide a clear description of the available data based on the schema.
    </CONSTRAINTS>

    """

    instruction_prompt_root_v1 = """You are an AI assistant answering data-related questions using provided tools.
    Your task is to accurately classify the user's intent and formulate refined questions suitable for:
    - a SQL database agent (`call_db_agent`)
    - a Python data science agent (`call_ds_agent`) and
    - a BigQuery ML agent (`call_bqml_agent`), if necessary.


    # **Workflow:**

    # 1. **Understand Intent TOOL (`call_intent_understanding`):**  This tool classifies the user question and returns a JSON with one of four structures:

    #     * **Greeting:** Contains a `greeting_message`. Return this message directly.
    #     * **Use Database:** (optional) Contains a `use_database`. Use this to determine which database to use. Return we switch to XXX database.
    #     * **Out of Scope:**  Return: "Your question is outside the scope of this database. Please ask a question relevant to this database."
    #     * **SQL Query Only:** Contains `nl_to_sql_question`. Proceed to Step 2.
    #     * **SQL and Python Analysis:** Contains `nl_to_sql_question` and `nl_to_python_question`. Proceed to Step 2.


    # 2. **Retrieve Data TOOL (`call_db_agent` - if applicable):**  If you need to query the database, use this tool. Make sure to provide a proper query to it to fulfill the task.

    # 3. **Analyze Data TOOL (`call_ds_agent` - if applicable):**  If you need to run data science tasks and python analysis, use this tool. Make sure to provide a proper query to it to fulfill the task.

    # 4a. **BigQuery ML Tool (`call_bqml_agent` - if applicable):**  If the user specifically asks (!) for BigQuery ML, use this tool. Make sure to provide a proper query to it to fulfill the task, along with the dataset and project ID, and context. 

    # 5. **Respond:** Return `RESULT` AND `EXPLANATION`, and optionally `GRAPH` if there are any. Please USE the MARKDOWN format (not JSON) with the following sections:

    #     * **Result:**  "Natural language summary of the data agent findings"

    #     * **Explanation:**  "Step-by-step explanation of how the result was derived.",

    # **Tool Usage Summary:**

    #   * **Greeting/Out of Scope:** answer directly.
    #   * **SQL Query:** `call_db_agent`. Once you return the answer, provide additional explanations.
    #   * **SQL & Python Analysis:** `call_db_agent`, then `call_ds_agent`. Once you return the answer, provide additional explanations.
    #   * **BQ ML `call_bqml_agent`:** Query the BQ ML Agent if the user asks for it. Ensure that:
    #   A. You provide the fitting query.
    #   B. You pass the project and dataset ID.
    #   C. You pass any additional context.


    **Key Reminder:**
    * ** You do have access to the database schema. Use it. **
    * **ONLY CALL THE BQML AGENT IF THE USER SPECIFICALLY ASKS FOR BQML / BIGQUERY ML. This can be for any BQML related tasks, like checking models, training, inference, etc.**
    * **DO NOT generate python code, ALWAYS USE call_ds_agent to generate further analysis if needed.**
    * **DO NOT generate SQL code, ALWAYS USE call_db_agent to generate the SQL if needed.**
    * **IF call_ds_agent is called with valid result, JUST SUMMARIZE ALL RESULTS FROM PREVIOU STEPS USING REPOSNE FORMAT!**
    * **IF data is available from prevoius call_db_agent and call_ds_agent, YOU CAN DIRECTLY USE call_ds_agent TO DO NEW ANLAYZIE USING THE DATA FROM PREVIOU STEPS, skipping call_intent_understanding and call_db_agent!**
    * **DO NOT ask the user for project or dataset ID. You have these details in the session context. For BQ ML tasks, just verify if it is okay to proceed with the plan.**
        """

    instruction_prompt_root_v0 = """You are an AI assistant answering data-related questions using provided tools.


        **Workflow:**

        1. **Understand Intent TOOL (`call_intent_understanding`):**  This tool classifies the user question and returns a JSON with one of four structures:

            * **Greeting:** Contains a `greeting_message`. Return this message directly.
            * **Use Database:** (optional) Contains a `use_database`. Use this to determine which database to use. Return we switch to XXX database.
            * **Out of Scope:**  Return: "Your question is outside the scope of this database. Please ask a question relevant to this database."
            * **SQL Query Only:** Contains `nl_to_sql_question`. Proceed to Step 2.
            * **SQL and Python Analysis:** Contains `nl_to_sql_question` and `nl_to_python_question`. Proceed to Step 2.


        2. **Retrieve Data TOOL (`call_db_agent` - if applicable):**  If you need to query the database, use this tool. Make sure to provide a proper query to it to fulfill the task.

        3. **Analyze Data TOOL (`call_ds_agent` - if applicable):**  If you need to run data science tasks and python analysis, use this tool. Make sure to provide a proper query to it to fulfill the task.

        4a. **BigQuery ML Tool (`call_bqml_agent` - if applicable):**  If the user specifically asks (!) for BigQuery ML, use this tool. Make sure to provide a proper query to it to fulfill the task, along with the dataset and project ID, and context. Once this is done, check back the plan with the user before proceeding.
            If the user accepts the plan, call this tool again so it can execute.


        5. **Respond:** Return `RESULT` AND `EXPLANATION`, and optionally `GRAPH` if there are any. Please USE the MARKDOWN format (not JSON) with the following sections:

            * **Result:**  "Natural language summary of the data agent findings"

            * **Explanation:**  "Step-by-step explanation of how the result was derived.",

        **Tool Usage Summary:**

        * **Greeting/Out of Scope:** answer directly.
        * **SQL Query:** `call_db_agent`. Once you return the answer, provide additional explanations.
        * **SQL & Python Analysis:** `call_db_agent`, then `call_ds_agent`. Once you return the answer, provide additional explanations.
        * **BQ ML `call_bqml_agent`:** Query the BQ ML Agent if the user asks for it. Ensure that:
        A. You provide the fitting query.
        B. You pass the project and dataset ID.
        C. You pass any additional context.

        **Key Reminder:**
        * **Do not fabricate any answers. Rely solely on the provided tools. ALWAYS USE call_intent_understanding FIRST!**
        * **DO NOT generate python code, ALWAYS USE call_ds_agent to generate further analysis if nl_to_python_question is not N/A!**
        * **IF call_ds_agent is called with valid result, JUST SUMMARIZE ALL RESULTS FROM PREVIOU STEPS USING REPOSNE FORMAT!**
        * **IF data is available from prevoius call_db_agent and call_ds_agent, YOU CAN DIRECTLY USE call_ds_agent TO DO NEW ANLAYZIE USING THE DATA FROM PREVIOU STEPS, skipping call_intent_understanding and call_db_agent!**
        * **Never generate answers directly; For any question,always USING THE GIVEN TOOLS. Start with call_intent_understanding if not sure!**
            """

    return instruction_prompt_root_v2

```


---

## 文件: data-science\data_science\tools.py

```python
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

"""Top level agent for data agent multi-agents.

-- it get data from database (e.g., BQ) using NL2SQL
-- then, it use NL2Py to do further data analysis as needed
"""

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from .sub_agents import ds_agent, db_agent


async def call_db_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call database (nl2sql) agent."""
    print(
        "\n call_db_agent.use_database:"
        f' {tool_context.state["all_db_settings"]["use_database"]}'
    )

    agent_tool = AgentTool(agent=db_agent)

    db_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["db_agent_output"] = db_agent_output
    return db_agent_output


async def call_ds_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call data science (nl2py) agent."""

    if question == "N/A":
        return tool_context.state["db_agent_output"]

    input_data = tool_context.state["query_result"]

    question_with_data = f"""
  Question to answer: {question}

  Actual data to analyze prevoius quesiton is already in the following:
  {input_data}

  """

    agent_tool = AgentTool(agent=ds_agent)

    ds_agent_output = await agent_tool.run_async(
        args={"request": question_with_data}, tool_context=tool_context
    )
    tool_context.state["ds_agent_output"] = ds_agent_output
    return ds_agent_output

```


---

## 文件: data-science\data_science\sub_agents\analytics\agent.py

```python
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

"""Data Science Agent V2: generate nl2py and use code interpreter to run the code."""

from google.adk.code_executors import VertexAiCodeExecutor
from google.adk.agents import Agent
from .prompts import return_instructions_ds


root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="data_science_agent",
    instruction=return_instructions_ds(),
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=True,
        stateful=True,
    ),
)

```


---

## 文件: data-science\data_science\sub_agents\analytics\prompts.py

```python
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

"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the analytics (ds) agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""

import os


def return_instructions_ds() -> str:

    instruction_prompt_ds_v1 = """
  # Guidelines

  **Objective:** Assist the user in achieving their data analysis goals within the context of a Python Colab notebook, **with emphasis on avoiding assumptions and ensuring accuracy.**
  Reaching that goal can involve multiple steps. When you need to generate code, you **don't** need to solve the goal in one go. Only generate the next step at a time.

  **Trustworthiness:** Always include the code in your response. Put it at the end in the section "Code:". This will ensure trust in your output.

  **Code Execution:** All code snippets provided will be executed within the Colab environment.

  **Statefulness:** All code snippets are executed and the variables stays in the environment. You NEVER need to re-initialize variables. You NEVER need to reload files. You NEVER need to re-import libraries.

  **Imported Libraries:** The following libraries are ALREADY imported and should NEVER be imported again:

  ```tool_code
  import io
  import math
  import re
  import matplotlib.pyplot as plt
  import numpy as np
  import pandas as pd
  import scipy
  ```

  **Output Visibility:** Always print the output of code execution to visualize results, especially for data exploration and analysis. For example:
    - To look a the shape of a pandas.DataFrame do:
      ```tool_code
      print(df.shape)
      ```
      The output will be presented to you as:
      ```tool_outputs
      (49, 7)

      ```
    - To display the result of a numerical computation:
      ```tool_code
      x = 10 ** 9 - 12 ** 5
      print(f'{{x=}}')
      ```
      The output will be presented to you as:
      ```tool_outputs
      x=999751168

      ```
    - You **never** generate ```tool_outputs yourself.
    - You can then use this output to decide on next steps.
    - Print variables (e.g., `print(f'{{variable=}}')`.
    - Give out the generated code under 'Code:'.

  **No Assumptions:** **Crucially, avoid making assumptions about the nature of the data or column names.** Base findings solely on the data itself. Always use the information obtained from `explore_df` to guide your analysis.

  **Available files:** Only use the files that are available as specified in the list of available files.

  **Data in prompt:** Some queries contain the input data directly in the prompt. You have to parse that data into a pandas DataFrame. ALWAYS parse all the data. NEVER edit the data that are given to you.

  **Answerability:** Some queries may not be answerable with the available data. In those cases, inform the user why you cannot process their query and suggest what type of data would be needed to fulfill their request.

  **WHEN YOU DO PREDICTION / MODEL FITTING, ALWAYS PLOT FITTED LINE AS WELL **


  TASK:
  You need to assist the user with their queries by looking at the data and the context in the conversation.
    You final answer should summarize the code and code execution relavant to the user query.

    You should include all pieces of data to answer the user query, such as the table from code execution results.
    If you cannot answer the question directly, you should follow the guidelines above to generate the next step.
    If the question can be answered directly with writing any code, you should do that.
    If you doesn't have enough data to answer the question, you should ask for clarification from the user.

    You should NEVER install any package on your own like `pip install ...`.
    When plotting trends, you should make sure to sort and order the data by the x-axis.

    NOTE: for pandas pandas.core.series.Series object, you can use .iloc[0] to access the first element rather than assuming it has the integer index 0"
    correct one: predicted_value = prediction.predicted_mean.iloc[0]
    error one: predicted_value = prediction.predicted_mean[0]
    correct one: confidence_interval_lower = confidence_intervals.iloc[0, 0]
    error one: confidence_interval_lower = confidence_intervals[0][0]

  """

    return instruction_prompt_ds_v1

```


---

## 文件: data-science\data_science\sub_agents\bigquery\agent.py

```python
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

"""Database Agent: get data from database (BigQuery) using NL2SQL."""

import os
from google.genai import types

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

from .prompts import return_instructions_bigquery
from . import tools
from .chase_sql import chase_db_tools

NL2SQL_METHOD = os.getenv("NL2SQL_METHOD", "BASELINE")


def setup_before_agent_call(callback_context: CallbackContext) -> None:
    """Setup the agent."""

    if "database_settings" not in callback_context.state:
        callback_context.state["database_settings"] = tools.get_database_settings()


database_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="database_agent",
    instruction=return_instructions_bigquery(),
    tools=[
        (
            chase_db_tools.initial_bq_nl2sql
            if NL2SQL_METHOD == "CHASE"
            else tools.initial_bq_nl2sql
        ),
        tools.run_bigquery_validation,
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)

```


---

## 文件: data-science\data_science\sub_agents\bigquery\prompts.py

```python
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

"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the bigquery agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""

import os


def return_instructions_bigquery() -> str:

    NL2SQL_METHOD = os.getenv("NL2SQL_METHOD", "BASELINE")
    if NL2SQL_METHOD == "BASELINE" or NL2SQL_METHOD == "CHASE":
        db_tool_name = "initial_bq_nl2sql"
    else:
        db_tool_name = None
        raise ValueError(f"Unknown NL2SQL method: {NL2SQL_METHOD}")

    instruction_prompt_bqml_v1 = f"""
      You are an AI assistant serving as a SQL expert for BigQuery.
      Your job is to help users generate SQL answers from natural language questions (inside Nl2sqlInput).
      You should proeuce the result as NL2SQLOutput.

      Use the provided tools to help generate the most accurate SQL:
      1. First, use {db_tool_name} tool to generate initial SQL from the question.
      2. You should also validate the SQL you have created for syntax and function errors (Use run_bigquery_validation tool). If there are any errors, you should go back and address the error in the SQL. Recreate the SQL based by addressing the error.
      4. Generate the final result in JSON format with four keys: "explain", "sql", "sql_results", "nl_results".
          "explain": "write out step-by-step reasoning to explain how you are generating the query based on the schema, example, and question.",
          "sql": "Output your generated SQL!",
          "sql_results": "raw sql execution query_result from run_bigquery_validation if it's available, otherwise None",
          "nl_results": "Natural language about results, otherwise it's None if generated SQL is invalid"
      ```
      You should pass one tool call to another tool call as needed!

      NOTE: you should ALWAYS USE THE TOOLS ({db_tool_name} AND run_bigquery_validation) to generate SQL, not make up SQL WITHOUT CALLING TOOLS.
      Keep in mind that you are an orchestration agent, not a SQL expert, so use the tools to help you generate SQL, but do not make up SQL.

    """

    return instruction_prompt_bqml_v1

```


---

## 文件: data-science\data_science\sub_agents\bigquery\tools.py

```python
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

"""This file contains the tools used by the database agent."""

import datetime
import logging
import os
import re

from data_science.utils.utils import get_env_var
from google.adk.tools import ToolContext
from google.cloud import bigquery
from google.genai import Client

from .chase_sql import chase_constants

# Assume that `BQ_PROJECT_ID` is set in the environment. See the
# `data_agent` README for more details.
project = os.getenv("BQ_PROJECT_ID", None)
region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
llm_client = Client(vertexai=True, project=project, location=region)

MAX_NUM_ROWS = 80


database_settings = None
bq_client = None

def get_bq_client():
    """Get BigQuery client."""
    global bq_client
    if bq_client is None:
        bq_client = bigquery.Client(project=get_env_var("BQ_PROJECT_ID"))
    return bq_client


def get_database_settings():
    """Get database settings."""
    global database_settings
    if database_settings is None:
        database_settings = update_database_settings()
    return database_settings


def update_database_settings():
    """Update database settings."""
    global database_settings
    ddl_schema = get_bigquery_schema(
        get_env_var("BQ_DATASET_ID"),
        client=get_bq_client(),
        project_id=get_env_var("BQ_PROJECT_ID"),
    )
    database_settings = {
        "bq_project_id": get_env_var("BQ_PROJECT_ID"),
        "bq_dataset_id": get_env_var("BQ_DATASET_ID"),
        "bq_ddl_schema": ddl_schema,
        # Include ChaseSQL-specific constants.
        **chase_constants.chase_sql_constants_dict,
    }
    return database_settings


def get_bigquery_schema(dataset_id, client=None, project_id=None):
    """Retrieves schema and generates DDL with example values for a BigQuery dataset.

    Args:
        dataset_id (str): The ID of the BigQuery dataset (e.g., 'my_dataset').
        client (bigquery.Client): A BigQuery client.
        project_id (str): The ID of your Google Cloud Project.

    Returns:
        str: A string containing the generated DDL statements.
    """

    if client is None:
        client = bigquery.Client(project=project_id)

    # dataset_ref = client.dataset(dataset_id)
    dataset_ref = bigquery.DatasetReference(project_id, dataset_id)

    ddl_statements = ""

    for table in client.list_tables(dataset_ref):
        table_ref = dataset_ref.table(table.table_id)
        table_obj = client.get_table(table_ref)

        # Check if table is a view
        if table_obj.table_type != "TABLE":
            continue

        ddl_statement = f"CREATE OR REPLACE TABLE `{table_ref}` (\n"

        for field in table_obj.schema:
            ddl_statement += f"  `{field.name}` {field.field_type}"
            if field.mode == "REPEATED":
                ddl_statement += " ARRAY"
            if field.description:
                ddl_statement += f" COMMENT '{field.description}'"
            ddl_statement += ",\n"

        ddl_statement = ddl_statement[:-2] + "\n);\n\n"

        # Add example values if available (limited to first row)
        rows = client.list_rows(table_ref, max_results=5).to_dataframe()
        if not rows.empty:
            ddl_statement += f"-- Example values for table `{table_ref}`:\n"
            for _, row in rows.iterrows():  # Iterate over DataFrame rows
                ddl_statement += f"INSERT INTO `{table_ref}` VALUES\n"
                example_row_str = "("
                for value in row.values:  # Now row is a pandas Series and has values
                    if isinstance(value, str):
                        example_row_str += f"'{value}',"
                    elif value is None:
                        example_row_str += "NULL,"
                    else:
                        example_row_str += f"{value},"
                example_row_str = (
                    example_row_str[:-1] + ");\n\n"
                )  # remove trailing comma
                ddl_statement += example_row_str

        ddl_statements += ddl_statement

    return ddl_statements


def initial_bq_nl2sql(
    question: str,
    tool_context: ToolContext,
) -> str:
    """Generates an initial SQL query from a natural language question.

    Args:
        question (str): Natural language question.
        tool_context (ToolContext): The tool context to use for generating the SQL
          query.

    Returns:
        str: An SQL statement to answer this question.
    """

    prompt_template = """
You are a BigQuery SQL expert tasked with answering user's questions about BigQuery tables by generating SQL queries in the GoogleSql dialect.  Your task is to write a Bigquery SQL query that answers the following question while using the provided context.

**Guidelines:**

- **Table Referencing:** Always use the full table name with the database prefix in the SQL statement.  Tables should be referred to using a fully qualified name with enclosed in backticks (`) e.g. `project_name.dataset_name.table_name`.  Table names are case sensitive.
- **Joins:** Join as few tables as possible. When joining tables, ensure all join columns are the same data type. Analyze the database and the table schema provided to understand the relationships between columns and tables.
- **Aggregations:**  Use all non-aggregated columns from the `SELECT` statement in the `GROUP BY` clause.
- **SQL Syntax:** Return syntactically and semantically correct SQL for BigQuery with proper relation mapping (i.e., project_id, owner, table, and column relation). Use SQL `AS` statement to assign a new name temporarily to a table column or even a table wherever needed. Always enclose subqueries and union queries in parentheses.
- **Column Usage:** Use *ONLY* the column names (column_name) mentioned in the Table Schema. Do *NOT* use any other column names. Associate `column_name` mentioned in the Table Schema only to the `table_name` specified under Table Schema.
- **FILTERS:** You should write query effectively  to reduce and minimize the total rows to be returned. For example, you can use filters (like `WHERE`, `HAVING`, etc. (like 'COUNT', 'SUM', etc.) in the SQL query.
- **LIMIT ROWS:**  The maximum number of rows returned should be less than {MAX_NUM_ROWS}.

**Schema:**

The database structure is defined by the following table schemas (possibly with sample rows):

```
{SCHEMA}
```

**Natural language question:**

```
{QUESTION}
```

**Think Step-by-Step:** Carefully consider the schema, question, guidelines, and best practices outlined above to generate the correct BigQuery SQL.

   """

    ddl_schema = tool_context.state["database_settings"]["bq_ddl_schema"]

    prompt = prompt_template.format(
        MAX_NUM_ROWS=MAX_NUM_ROWS, SCHEMA=ddl_schema, QUESTION=question
    )

    response = llm_client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt,
        config={"temperature": 0.1},
    )

    sql = response.text
    if sql:
        sql = sql.replace("```sql", "").replace("```", "").strip()

    print("\n sql:", sql)

    tool_context.state["sql_query"] = sql

    return sql


def run_bigquery_validation(
    sql_string: str,
    tool_context: ToolContext,
) -> str:
    """Validates BigQuery SQL syntax and functionality.

    This function validates the provided SQL string by attempting to execute it
    against BigQuery in dry-run mode. It performs the following checks:

    1. **SQL Cleanup:**  Preprocesses the SQL string using a `cleanup_sql`
    function
    2. **DML/DDL Restriction:**  Rejects any SQL queries containing DML or DDL
       statements (e.g., UPDATE, DELETE, INSERT, CREATE, ALTER) to ensure
       read-only operations.
    3. **Syntax and Execution:** Sends the cleaned SQL to BigQuery for validation.
       If the query is syntactically correct and executable, it retrieves the
       results.
    4. **Result Analysis:**  Checks if the query produced any results. If so, it
       formats the first few rows of the result set for inspection.

    Args:
        sql_string (str): The SQL query string to validate.
        tool_context (ToolContext): The tool context to use for validation.

    Returns:
        str: A message indicating the validation outcome. This includes:
             - "Valid SQL. Results: ..." if the query is valid and returns data.
             - "Valid SQL. Query executed successfully (no results)." if the query
                is valid but returns no data.
             - "Invalid SQL: ..." if the query is invalid, along with the error
                message from BigQuery.
    """

    def cleanup_sql(sql_string):
        """Processes the SQL string to get a printable, valid SQL string."""

        # 1. Remove backslashes escaping double quotes
        sql_string = sql_string.replace('\\"', '"')

        # 2. Remove backslashes before newlines (the key fix for this issue)
        sql_string = sql_string.replace("\\\n", "\n")  # Corrected regex

        # 3. Replace escaped single quotes
        sql_string = sql_string.replace("\\'", "'")

        # 4. Replace escaped newlines (those not preceded by a backslash)
        sql_string = sql_string.replace("\\n", "\n")

        # 5. Add limit clause if not present
        if "limit" not in sql_string.lower():
            sql_string = sql_string + " limit " + str(MAX_NUM_ROWS)

        return sql_string

    logging.info("Validating SQL: %s", sql_string)
    sql_string = cleanup_sql(sql_string)
    logging.info("Validating SQL (after cleanup): %s", sql_string)

    final_result = {"query_result": None, "error_message": None}

    # More restrictive check for BigQuery - disallow DML and DDL
    if re.search(
        r"(?i)(update|delete|drop|insert|create|alter|truncate|merge)", sql_string
    ):
        final_result["error_message"] = (
            "Invalid SQL: Contains disallowed DML/DDL operations."
        )
        return final_result

    try:
        query_job = get_bq_client().query(sql_string)
        results = query_job.result()  # Get the query results

        if results.schema:  # Check if query returned data
            rows = [
                {
                    key: (
                        value
                        if not isinstance(value, datetime.date)
                        else value.strftime("%Y-%m-%d")
                    )
                    for (key, value) in row.items()
                }
                for row in results
            ][
                :MAX_NUM_ROWS
            ]  # Convert BigQuery RowIterator to list of dicts
            # return f"Valid SQL. Results: {rows}"
            final_result["query_result"] = rows

            tool_context.state["query_result"] = rows

        else:
            final_result["error_message"] = (
                "Valid SQL. Query executed successfully (no results)."
            )

    except (
        Exception
    ) as e:  # Catch generic exceptions from BigQuery  # pylint: disable=broad-exception-caught
        final_result["error_message"] = f"Invalid SQL: {e}"

    print("\n run_bigquery_validation final_result: \n", final_result)

    return final_result

```


---

## 文件: data-science\data_science\sub_agents\bigquery\chase_sql\chase_constants.py

```python
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

"""Constants used by the ChaseSQL algorithm."""

from typing import Any
import immutabledict


# Parameters for ChaseSQL.
chase_sql_constants_dict: immutabledict.immutabledict[str, Any] = (
    immutabledict.immutabledict({
        # Whether to transpile the SQL to BigQuery.
        'transpile_to_bigquery': True,
        # Whether to process input errors.
        'process_input_errors': True,
        # Whether to process SQLGlot tool output errors.
        'process_tool_output_errors': True,
        # Number of candidates to generate.
        'number_of_candidates': 1,
        # Model to use for generation.
        'model': 'gemini-1.5-flash-002',
        # Temperature for generation.
        'temperature': 0.5,
        # Type of SQL generation method.
        'generate_sql_type': 'dc',
    })
)

```


---

## 文件: data-science\data_science\sub_agents\bigquery\chase_sql\chase_db_tools.py

```python
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

"""This code contains the implementation of the tools used for the CHASE-SQL agent."""

import enum
import os

from google.adk.tools import ToolContext

# pylint: disable=g-importing-member
from .dc_prompt_template import DC_PROMPT_TEMPLATE
from .llm_utils import GeminiModel
from .qp_prompt_template import QP_PROMPT_TEMPLATE
from .sql_postprocessor import sql_translator

# pylint: enable=g-importing-member

BQ_PROJECT_ID = os.getenv("BQ_PROJECT_ID")


class GenerateSQLType(enum.Enum):
    """Enum for the different types of SQL generation methods.

    DC: Divide and Conquer ICL prompting
    QP: Query Plan-based prompting
    """

    DC = "dc"
    QP = "qp"


def exception_wrapper(func):
    """A decorator to catch exceptions in a function and return the exception as a string.

    Args:
       func (callable): The function to wrap.

    Returns:
       callable: The wrapped function.
    """

    def wrapped_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return f"Exception occurred in {func.__name__}: {str(e)}"

    return wrapped_function


def parse_response(response: str) -> str:
    """Parses the output to extract SQL content from the response.

    Args:
       response (str): The output string containing SQL query.

    Returns:
       str: The SQL query extracted from the response.
    """
    query = response
    try:
        if "```sql" in response and "```" in response:
            query = response.split("```sql")[1].split("```")[0]
    except ValueError as e:
        print(f"Error in parsing response: {e}")
        query = response
    return query.strip()


def initial_bq_nl2sql(
    question: str,
    tool_context: ToolContext,
) -> str:
    """Generates an initial SQL query from a natural language question.

    Args:
      question: Natural language question.
      tool_context: Function context.

    Returns:
      str: An SQL statement to answer this question.
    """
    print("****** Running agent with ChaseSQL algorithm.")
    ddl_schema = tool_context.state["database_settings"]["bq_ddl_schema"]
    project = tool_context.state["database_settings"]["bq_project_id"]
    db = tool_context.state["database_settings"]["bq_dataset_id"]
    transpile_to_bigquery = tool_context.state["database_settings"][
        "transpile_to_bigquery"
    ]
    process_input_errors = tool_context.state["database_settings"][
        "process_input_errors"
    ]
    process_tool_output_errors = tool_context.state["database_settings"][
        "process_tool_output_errors"
    ]
    number_of_candidates = tool_context.state["database_settings"][
        "number_of_candidates"
    ]
    model = tool_context.state["database_settings"]["model"]
    temperature = tool_context.state["database_settings"]["temperature"]
    generate_sql_type = tool_context.state["database_settings"]["generate_sql_type"]

    if generate_sql_type == GenerateSQLType.DC.value:
        prompt = DC_PROMPT_TEMPLATE.format(
            SCHEMA=ddl_schema, QUESTION=question, BQ_PROJECT_ID=BQ_PROJECT_ID
        )
    elif generate_sql_type == GenerateSQLType.QP.value:
        prompt = QP_PROMPT_TEMPLATE.format(
            SCHEMA=ddl_schema, QUESTION=question, BQ_PROJECT_ID=BQ_PROJECT_ID
        )
    else:
        raise ValueError(f"Unsupported generate_sql_type: {generate_sql_type}")

    model = GeminiModel(model_name=model, temperature=temperature)
    requests = [prompt for _ in range(number_of_candidates)]
    responses = model.call_parallel(requests, parser_func=parse_response)
    # Take just the first response.
    responses = responses[0]

    # If postprocessing of the SQL to transpile it to BigQuery is required,
    # then do it here.
    if transpile_to_bigquery:
        translator = sql_translator.SqlTranslator(
            model=model,
            temperature=temperature,
            process_input_errors=process_input_errors,
            process_tool_output_errors=process_tool_output_errors,
        )
        # pylint: disable=g-bad-todo
        # pylint: enable=g-bad-todo
        responses: str = translator.translate(
            responses, ddl_schema=ddl_schema, db=db, catalog=project
        )

    return responses

```


---

## 文件: data-science\data_science\sub_agents\bigquery\chase_sql\dc_prompt_template.py

```python
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

"""Divide-and-Conquer prompt template."""

DC_PROMPT_TEMPLATE = """
You are an experienced database expert.
Now you need to generate a GoogleSQL or BigQuery query given the database information, a question and some additional information.
The database structure is defined by table schemas (some columns provide additional column descriptions in the options).

Given the table schema information description and the `Question`. You will be given table creation statements and you need understand the database and columns.

You will be using a way called "recursive divide-and-conquer approach to SQL query generation from natural language".

Here is a high level description of the steps.
1. **Divide (Decompose Sub-question with Pseudo SQL):** The complex natural language question is recursively broken down into simpler sub-questions. Each sub-question targets a specific piece of information or logic required for the final SQL query.
2. **Conquer (Real SQL for sub-questions):**  For each sub-question (and the main question initially), a "pseudo-SQL" fragment is formulated. This pseudo-SQL represents the intended SQL logic but might have placeholders for answers to the decomposed sub-questions.
3. **Combine (Reassemble):** Once all sub-questions are resolved and their corresponding SQL fragments are generated, the process reverses. The SQL fragments are recursively combined by replacing the placeholders in the pseudo-SQL with the actual generated SQL from the lower levels.
4. **Final Output:** This bottom-up assembly culminates in the complete and correct SQL query that answers the original complex question.

Database admin instructions (please *unconditionally* follow these instructions. Do *not* ignore them or use them as hints.):
1. **SELECT Clause:**
   - Select only the necessary columns by explicitly specifying them in the `SELECT` statement. Avoid redundant columns or values.

2. **Aggregation (MAX/MIN):**
   - Ensure `JOIN`s are completed before applying `MAX()` or `MIN()`. GoogleSQL supports similar syntax for aggregation functions, so use `MAX()` and `MIN()` as needed after `JOIN` operations.

3. **ORDER BY with Distinct Values:**
   - In GoogleSQL, `GROUP BY <column>` can be used before `ORDER BY <column> ASC|DESC` to get distinct values and sort them.

4. **Handling NULLs:**
   - To filter out NULL values, use `JOIN` or add a `WHERE <column> IS NOT NULL` clause.

5. **FROM/JOIN Clauses:**
   - Only include tables essential to the query. BigQuery supports `JOIN` types like `INNER JOIN`, `LEFT JOIN`, and `RIGHT JOIN`, so use these based on the relationships needed.

6. **Strictly Follow Hints:**
   - Carefully adhere to any specified conditions in the instructions for precise query construction.

7. **Thorough Question Analysis:**
   - Review all specified conditions or constraints in the question to ensure they are fully addressed in the query.

8. **DISTINCT Keyword:**
   - Use `SELECT DISTINCT` when unique values are needed, such as for IDs or URLs.

9. **Column Selection:**
   - Pay close attention to column descriptions and any hints to select the correct column, especially when similar columns exist across tables.

10. **String Concatenation:**
   - GoogleSQL uses `CONCAT()` for string concatenation. Avoid using `||` and instead use `CONCAT(column1, ' ', column2)` for concatenation.

11. **JOIN Preference:**
   - Use `INNER JOIN` when appropriate, and avoid nested `SELECT` statements if a `JOIN` will achieve the same result.

12. **GoogleSQL Functions Only:**
   - Use functions available in GoogleSQL. Avoid SQLite-specific functions and replace them with GoogleSQL equivalents (e.g., `FORMAT_DATE` instead of `STRFTIME`).

13. **Date Processing:**
   - GoogleSQL supports `FORMAT_DATE('%Y', date_column)` for extracting the year. Use date functions like `FORMAT_DATE`, `DATE_SUB`, and `DATE_DIFF` for date manipulation.

14. **Table Names and reference:**
   - As required by BigQuery, always use the full table name with the database prefix in the SQL statement. For example, "SELECT * FROM example_bigquery_database.table_a", not just "SELECT * FROM table_a"

15. **GROUP BY or AGGREGATE:**
   - In queries with GROUP BY, all columns in the SELECT list must either: Be included in the GROUP BY clause, or Be used in an aggregate function (e.g., MAX, MIN, AVG, COUNT, SUM).

Here are some examples
===========
Example 1

**************************
【Table creation statements】
CREATE TABLE {BQ_PROJECT_ID}.restaurant.generalinfo
(
 id_restaurant INT64,
 food_type STRING OPTIONS(description="the food type"),
 city STRING OPTIONS(description="the city where the restaurant is located in"),
);

CREATE TABLE {BQ_PROJECT_ID}.restaurant.location
(
 id_restaurant INT64,
 street_name STRING OPTIONS(description="the street name of the restaurant"),
 city STRING OPTIONS(description="the city where the restaurant is located in foreign key (id_restaurant) references generalinfo (id_restaurant) on update cascade on delete cascade"),
);

**************************
【Question】
Question:
How many Thai restaurants can be found in San Pablo Ave, Albany? Thai restaurant refers to food_type = 'thai'; San Pablo Ave Albany refers to street_name = 'san pablo ave' AND T1.city = 'albany'

**************************
【Answer】
Repeating the question and generating the SQL with Recursive Divide-and-Conquer.
**Question**: How many Thai restaurants can be found in San Pablo Ave, Albany? Thai restaurant refers to food_type = 'thai'; San Pablo Ave Albany refers to street_name = 'san pablo ave' AND T1.city = 'albany'

**1. Divide and Conquer:**

* **Main Question:** How many Thai restaurants can be found in San Pablo Ave, Albany?
   * **Analysis:** The question asks for a count of restaurants, so we'll use `COUNT()` for that. The count should include only Thai restaurants, which we can identify using the `food_type` column in the `restaurant.generalinfo` table.  The location "San Pablo Ave, Albany" spans two columns (`street_name` and `city`) in the `restaurant.location` table, requiring us to join these two tables.
   * **Pseudo SQL:** SELECT COUNT(`T1`.`id_restaurant`) FROM `restaurantgeneralinfo` AS `T1` INNER JOIN `restaurant.location` AS `T2` ON `T1`.`id_restaurant` = `T2`.`id_restaurant` WHERE  <Thai restaurant> AND <in San Pablo Ave, Albany>

   * **Sub-question 1:** Thai restaurant
       * **Analysis:** This is a straightforward filter on the `restaurant.generalinfo` table using the `food_type` column.
       * **Pseudo SQL:** `T1`.`food_type` = 'thai'

   * **Sub-question 2:** in San Pablo Ave, Albany
       * **Analysis:** This location information is spread across two columns in the `restaurant.location` table. We need to combine these conditions with an "AND" operator to ensure both are met.
       * **Pseudo SQL:** `T2`.`street_name` = 'san pablo ave' AND `T2`.`city` = 'albany'

**2. Assembling SQL:**

* **Sub-question 1 (Thai restaurant):**
   * **SQL:** `T1`.`food_type` = 'thai'

* **Sub-question 2 (in San Pablo Ave, Albany):**
   * **SQL:** `T2`.`street_name` = 'san pablo ave' AND `T2`.`city` = 'albany'

* **Main Question (count of restaurants):**
   * **SQL:** SELECT COUNT(`T1`.`id_restaurant`) FROM `{BQ_PROJECT_ID}.restaurant.generalinfo` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.restaurant.location` AS `T2` ON `T1`.`id_restaurant` = `T2`.`id_restaurant` WHERE `T1`.`food_type` = 'thai' AND `T2`.`street_name` = 'san pablo ave' AND `T2`.`city` = 'albany'

**3. Simplification and Optimization:**

* The SQL query from step 2 is already quite efficient. We've used `INNER JOIN` to combine the tables based on their relationship, and the `WHERE` clause clearly defines our filtering criteria. There's no need for nested queries or complex sub-selections in this case.

**Final Optimized SQL Query:**
```sql
SELECT COUNT(T1.id_restaurant)
 FROM {BQ_PROJECT_ID}.restaurant.generalinfo AS T1
 INNER JOIN {BQ_PROJECT_ID}.restaurant.location AS T2 ON T1.id_restaurant = T2.id_restaurant
 WHERE T1.food_type = 'thai' AND T1.city = 'albany' AND T2.street_name = 'san pablo ave'
```

===========
Example 2

**************************
【Database Info】
CREATE TABLE {BQ_PROJECT_ID}.financial.account (
   account_id INT64,
   district_id INT64,
   frequency STRING,
   date DATE,
);
CREATE TABLE {BQ_PROJECT_ID}.financial.client (
   client_id INT64,
   gender STRING,
   birth_date DATE,
   district_id INT64,
);
CREATE TABLE {BQ_PROJECT_ID}.financial.district (
   district_id INT64,
   a4 STRING OPTIONS(description="Assuming A4 and A11 are strings due to examples"),
   a11 STRING,
);

**************************
【Question】
Question:
What is the gender of the youngest client who opened account in the lowest average salary branch? Given that Later birthdate refers to younger age; A11 refers to average salary

**************************
【Answer】
Repeating the question and generating the SQL with Recursive Divide-and-Conquer.
**Question**: What is the gender of the youngest client who opened account in the lowest average salary branch? Given that Later birthdate refers to younger age; A11 refers to average salary

**1. Divide and Conquer:**

* **Main Question:** What is the gender of the youngest client who opened account in the lowest average salary branch?
   * **Analysis:** The question is asking about `gender`, and it appears in the table `financial.client`. We will use this as the output column, selecting it from the youngest client in the lowest average salary branch.
   * **Pseudo **Final Optimized SQL Query:**** SELECT `T1`.`gender` FROM `{BQ_PROJECT_ID}.financial.client` AS `T1` WHERE <youngest client in the lowest average salary branch>

   * **Sub-question 1:** youngest client in the lowest average salary branch
       * **Analysis:** According to the hint, we need to use the `A11` from `financial.district` to get the salary info, and the youngest client can be obtained from using the `birth_date` column of table `financial.client`. The items between these two tables can be INNER JOIN using district_id.
       * **Pseudo SQL:** SELECT `T1`.`client_id` FROM `{BQ_PROJECT_ID}.financial.client` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.financial.district` AS `T2` ON `T1`.`district_id` = `T2`.`district_id` WHERE <lowest average salary branch> ORDER BY `T1`.`birth_date` DESC NULLS LAST LIMIT 1

       * **Sub-question 1.1:** lowest average salary branch
           * **Analysis:** We can get the lowest average salary branch using order by `A11` ASC and pick top 1. The column `A11` is not NULLABLE, so we do not need to add "IS NOT NULL" filter
           * **Pseudo SQL:**  SELECT `district_id` FROM `{BQ_PROJECT_ID}.financial.district` ORDER BY `A11` ASC LIMIT 1

**2. Assembling SQL:**

* **Sub-question 1.1 (lowest average salary branch):**
   * **SQL:** SELECT `district_id` FROM `{BQ_PROJECT_ID}.financial.district` ORDER BY `A11` ASC LIMIT 1

* **Sub-question 1 (youngest client in the lowest average salary branch):**
   * **SQL:** SELECT `T1`.`client_id` FROM `{BQ_PROJECT_ID}.financial.client` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.financial.district` AS `T2` ON `T1`.`district_id` = `T2`.`district_id` WHERE `T2`.`district_id` IN (SELECT `district_id` FROM `financial.district` ORDER BY `A11` ASC LIMIT 1) ORDER BY `T1`.`birth_date` DESC NULLS LAST LIMIT 1

* **Main Question (gender of the client):**
   * **SQL:** SELECT `T1`.`gender` FROM `{BQ_PROJECT_ID}.financial.client` AS `T1` WHERE `T1`.`client_id` = (SELECT `T1`.`client_id` FROM `{BQ_PROJECT_ID}.financial.client` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.financial.district` AS `T2` ON `T1`.`district_id` = `T2`.`district_id` WHERE `T2`.`district_id` IN (SELECT `district_id` FROM `{BQ_PROJECT_ID}.financial.district` ORDER BY `A11` ASC LIMIT 1) ORDER BY `T1`.`birth_date` DESC NULLS LAST LIMIT 1)

**3. Simplification and Optimization:**

* The final SQL query from step 2 can be simplified and optimized. The nested queries can be combined using a single `INNER JOIN` and the filtering can be done within a single `ORDER BY` clause.

**Final Optimized SQL Query:**
```sql
SELECT `T1`.`gender`
 FROM `{BQ_PROJECT_ID}.financial.client` AS `T1`
 INNER JOIN `{BQ_PROJECT_ID}.financial.district` AS `T2`
 ON `T1`.`district_id` = `T2`.`district_id`
 ORDER BY `T2`.`A11` ASC, `T1`.`birth_date` DESC NULLS LAST
 LIMIT 1
```
===========
Example 3 (dividing into two parallel sub-questions)

**************************
【Database Info】
CREATE TABLE {BQ_PROJECT_ID}.olympics.games
(
 id INT64,
 games_year INT64 OPTIONS(description="description: the year of the game"),
 games_name STRING,
);

CREATE TABLE {BQ_PROJECT_ID}.olympics.games_city
(
 games_id INT64,
 city_id INT64 OPTIONS(description="the id of the city that held the game Maps to city(id)"),
);

CREATE TABLE {BQ_PROJECT_ID}.olympics.city
(
 id INT64,
 city_name STRING,
);

**************************
【Question】
Question:
From 1900 to 1992, how many games did London host? From 1900 to 1992 refers to games_year BETWEEN 1900 AND 1992; London refers to city_name = 'London'; games refer to games_name;

**************************
【Answer】
Repeating the question and generating the SQL with Recursive Divide-and-Conquer.
**Question**: From 1900 to 1992, how many games did London host? From 1900 to 1992 refers to games_year BETWEEN 1900 AND 1992; London refers to city_name = 'London'; games refer to games_name;

**1. Divide and Conquer:**

* **Main Question:** From 1900 to 1992, how many games did London host?
   * **Analysis:** The question requires us to count games, which are represented by the `id` column in the `olympics.games` table.  We need to filter these games based on two criteria: they were hosted in London and occurred between 1900 and 1992.
   * **Pseudo SQL:** SELECT COUNT(`T1`.`id`) FROM `{BQ_PROJECT_ID}.olympics.games` AS `T1`  WHERE  <games are in London> AND <games year between 1900 and 1992>

   * **Sub-question 1:** games are in London
       * **Analysis:**  To determine which games were hosted in London, we need to join the `olympics.games` table with the `olympics.games_city` table on `games_id` and then join with the `city` table on `city_id`. We'll use `INNER JOIN` to ensure only matching records are considered.  The filtering on 'London' will be applied to the `city_name` column.
       * **Pseudo SQL:**  `T1`.`id` IN (SELECT `T1`.`games_id` FROM `{BQ_PROJECT_ID}.olympics.games_city` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.olympics.city` AS `T2` ON `T1`.`city_id` = `T2`.`id` WHERE `T2`.`city_name` = 'London')

   * **Sub-question 2:** games year between 1900 and 1992
       * **Analysis:** This involves filtering the `olympics.games` table directly based on the `games_year` column using the `BETWEEN` operator.
       * **Pseudo SQL:** `T1`.`games_year` BETWEEN 1900 AND 1992

**2. Assembling SQL:**

* **Sub-question 1 (games are in London):**
   * **SQL:**  `T1`.`id` IN (SELECT `T1`.`games_id` FROM `{BQ_PROJECT_ID}.olympics.games_city` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.olympics.city` AS `T2` ON `T1`.`city_id` = `T2`.`id` WHERE `T2`.`city_name` = 'London')

* **Sub-question 2 (games year between 1900 and 1992):**
   * **SQL:**  `T1`.`games_year` BETWEEN 1900 AND 1992

* **Main Question (count of games):**
   * **SQL:** SELECT COUNT(`T1`.`id`) FROM `{BQ_PROJECT_ID}.olympics.games` AS `T1` WHERE `T1`.`id` IN (SELECT `T1`.`games_id` FROM `{BQ_PROJECT_ID}.olympics.games_city` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.olympics.city` AS `T2` ON `T1`.`city_id` = `T2`.`id` WHERE `T2`.`city_name` = 'London') AND `T1`.`games_year` BETWEEN 1900 AND 1992

**3. Simplification and Optimization:**

* The nested query can be converted into a more efficient `JOIN` operation. We'll use `INNER JOIN` to combine `{BQ_PROJECT_ID}.olympics.games`, `{BQ_PROJECT_ID}.olympics.games_city`, and `{BQ_PROJECT_ID}.olympics.city` based on the relationships between them.

**Final Optimized SQL Query:**
```sql
SELECT COUNT(T3.id)
 FROM {BQ_PROJECT_ID}.olympics.games_city AS T1
 INNER JOIN {BQ_PROJECT_ID}.olympics.city AS T2 ON T1.city_id = T2.id
 INNER JOIN {BQ_PROJECT_ID}.olympics.games AS T3 ON T1.games_id = T3.id
 WHERE T2.city_name = 'London' AND T3.games_year
 BETWEEN 1900 AND 1992
```

===========
Example 4 (When it's not clear which column should be used for a string matching, use a loosen condition such as string LIKE and OR condition to cover multiple possible columns.)

**************************
【Database Info】
CREATE TABLE `{BQ_PROJECT_ID}.academics.student_programs` (
   `Program Type` STRING,
   `Participants (Ages 10-15)` FLOAT64,
   `Total Enrollment (Ages 10-15)` FLOAT64,
   `School Category` STRING,
);

**************************
【Question】
Question:
Please list the lowest three participation rates for students aged 10-15 in online programs. Participation rate for students aged 10-15 = `Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)`

**************************
【Answer】
Repeating the question and generating the SQL with Recursive Divide-and-Conquer.
**Question:** Please list the lowest three participation rates for students aged 10-15 in online programs. Participation rate for students aged 10-15 = `Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)`

**1. Divide and Conquer:**

* **Main Question:** Please list the lowest three participation rates for students aged 10-15 in online programs.
   * **Analysis:** The question is asking about the ratio between `Participants (Ages 10-15)` and `Total Enrollment (Ages 10-15)`. We need to filter the data to only include online programs.
   * **Pseudo SQL:** SELECT (`Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)`) FROM `{BQ_PROJECT_ID}.academics.student_programs` WHERE <online programs> ORDER BY (`Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)`) ASC NULLS LAST LIMIT 3

   * **Sub-question 1:** online programs
       * **Analysis:** We will get the information from the table `{BQ_PROJECT_ID}.academics.student_programs`.
       * **Pseudo SQL:** SELECT program_id FROM `academics.student_programs` WHERE <condition for online programs>

       * **Sub-question 1.1:** condition for online programs (Note: This requires external knowledge or database schema information. We need to identify which column(s) indicate "online programs".)
           * **Analysis:** We'll assume either "School Category" or "Program Type" columns might contain the term "online."
           * **Pseudo SQL:**  LOWER(`School Category`) LIKE '%online%' OR LOWER(`Program Type`) LIKE '%online%'

**2. Assembling SQL:**

* **Sub-question 1.1 (condition for online programs):**
   * **SQL:** LOWER(`School Category`) LIKE '%online%' OR LOWER(`Program Type`) LIKE '%online%'

* **Sub-question 1 (online programs):**
   * **SQL:** SELECT program_id FROM `{BQ_PROJECT_ID}.academics.student_programs` WHERE LOWER(`School Category`) LIKE '%online%' OR LOWER(`Program Type`) LIKE '%online%'

* **Main Question (lowest three participation rates):**
   * **SQL:** SELECT (`Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)`) FROM `{BQ_PROJECT_ID}.academics.student_programs` WHERE program_id IN (SELECT program_id FROM `{BQ_PROJECT_ID}.academics.student_programs` WHERE LOWER(`School Category`) LIKE '%online%' OR LOWER(`Program Type`) LIKE '%online%') ORDER BY (`Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)`) ASC NULLS LAST LIMIT 3

**3. Simplification and Optimization:**

* We can directly incorporate the condition for online programs into the main query.

**Final Optimized SQL Query:**
```sql
SELECT `Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)` FROM `{BQ_PROJECT_ID}.academics.student_programs`
 WHERE LOWER(`School Category`) LIKE '%online%' OR LOWER(`Program Type`) LIKE '%online%'
 AND `Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)` IS NOT NULL
 ORDER BY `Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)` ASC NULLS LAST LIMIT 3;
```

===========
Example 5

**************************
【Database Info】
CREATE TABLE {BQ_PROJECT_ID}.retails.employees (
   employee_id INT64,
   department_id INT64,
   salary INT64,
);

**************************
【Question】
Question:
How many employees earn over $100,000?

**************************
【Answer】
Repeating the question and generating the SQL with Recursive Divide-and-Conquer.
**Question:** How many employees earn over $100,000?

**1. Divide and Conquer:**

* **Main Question:** How many employees earn over $100,000?

   * **Pseudo SQL:** SELECT COUNT(*) FROM {BQ_PROJECT_ID}.retails.employees WHERE <employees earning over 100000>
   * **Analysis:** The question is asking about the COUNT of employees. We need to filter the data to only include employees earning over $100,000.

   * **Sub-question 1:** employees earning over 100000
       * **Analysis:** Simple condition on the `salary` column.
       * **Pseudo SQL:** SELECT employee_id FROM {BQ_PROJECT_ID}.retails.employees WHERE salary > 100000

**2. Assembling SQL:**

* **Sub-question 1 (employees earning over 100000):**
   * **SQL:** SELECT employee_id FROM {BQ_PROJECT_ID}.retails.employees WHERE salary > 100000

* **Main Question (count of employees):**
   * **SQL:** SELECT COUNT(*) FROM {BQ_PROJECT_ID}.retails.employees WHERE employee_id IN (SELECT employee_id FROM {BQ_PROJECT_ID}.retails.employees WHERE salary > 100000)

**3. Simplification and Optimization:**

* We can achieve the same result more efficiently within a single WHERE clause.

**Final Optimized SQL Query:**
```sql
SELECT COUNT(*) FROM {BQ_PROJECT_ID}.retails.employees WHERE salary > 100000;
```

===========
Example 6

**************************
【Database Info】
CREATE TABLE {BQ_PROJECT_ID}.airlines.Airlines
(
 FL_DATE STRING OPTIONS(description="flight date"),
 ORIGIN STRING OPTIONS(description="airport of origin"),
 DEST STRING OPTIONS(description="Destination airport"),
);

CREATE TABLE {BQ_PROJECT_ID}.airlines.Airports
(
 Code STRING,
 Description STRING,
);

**************************
【Question】
Question:
How many flights were there from San Diego International airport to Los Angeles International airport in the August of 2018?
flights from refers to ORIGIN; San Diego International airport refers to Description = 'San Diego, CA: San Diego International'; flights to refers to DEST; Los Angeles International airport refers to Description = 'Los Angeles, CA: Los Angeles International'; in the August of 2018 refers to FL_DATE like '2018/8%';

**************************
【Answer】
**Repeating the question and generating the SQL with Recursive Divide-and-Conquer.**

**Question**: How many flights were there from San Diego International airport to Los Angeles International airport in the August of 2018? flights from refers to ORIGIN; San Diego International airport refers to Description = 'San Diego, CA: San Diego International'; flights to refers to DEST; Los Angeles International airport refers to Description = 'Los Angeles, CA: Los Angeles International'; in the August of 2018 refers to FL_DATE like '2018/8%';

**1. Divide and Conquer:**

* **Main Question:** How many flights were there from San Diego International airport to Los Angeles International airport in the August of 2018?
   * **Analysis:** The question asks for a count of flights, which can be obtained by counting the `FL_DATE` entries in the `airlines.Airlines` table. We need to apply three filters: flights originating from San Diego International, flights destined for Los Angeles International, and flights occurring in August 2018.
   * **Pseudo SQL:** SELECT COUNT(`FL_DATE`) FROM `{BQ_PROJECT_ID}.airlines.Airlines` WHERE <flights are in August 2018> AND <flights are from San Diego International> AND <flights are to Los Angeles International>

   * **Sub-question 1:** flights are in August 2018
       * **Analysis:** This filter can be directly applied to the `{BQ_PROJECT_ID}.airlines.Airlines` table using the `FL_DATE` column and the `LIKE` operator, as indicated by the evidence.
       * **Pseudo SQL:** `FL_DATE` LIKE '2018/8%'

   * **Sub-question 2:** flights are from San Diego International
       * **Analysis:**  We need to find the airport code (`ORIGIN`) corresponding to 'San Diego, CA: San Diego International' from the `{BQ_PROJECT_ID}.airlines.Airports` table and use it to filter the `airlines.Airlines` table. This requires joining `airlines.Airports` and `airlines.Airlines` based on `airlines.Airports`.`Code` = `airlines.Airlines`.`ORIGIN`.
       * **Pseudo SQL:** `ORIGIN` = (SELECT `T2`.`ORIGIN` FROM `{BQ_PROJECT_ID}.airlines.Airports` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.airlines.Airlines` AS `T2` ON `T1`.`Code` = `T2`.`ORIGIN` WHERE `T1`.`Description` = 'San Diego, CA: San Diego International')

   * **Sub-question 3:** flights are to Los Angeles International
       * **Analysis:** Similar to sub-question 2, we need to find the airport code (`DEST`) for 'Los Angeles, CA: Los Angeles International' from the `airlines.Airports` table and use it to filter the `airlines.Airlines` table. This also requires joining `airlines.Airports` and `airlines.Airlines`, but this time on `airlines.Airports`.`Code` = `airlines.Airlines`.`DEST`.
       * **Pseudo SQL:** `DEST` = (SELECT `T4`.`DEST` FROM `{BQ_PROJECT_ID}.airlines.Airports` AS `T3` INNER JOIN `{BQ_PROJECT_ID}.airlines.Airlines` AS `T4` ON `T3`.`Code` = `T4`.`DEST` WHERE `T3`.`Description` = 'Los Angeles, CA: Los Angeles International')

**2. Assembling SQL:**

* **Sub-question 1 (flights are in August 2018):**
   * **SQL:** `FL_DATE` LIKE '2018/8%'

* **Sub-question 2 (flights are from San Diego International):**
   * **SQL:** `ORIGIN` = (SELECT DISTINCT `T2`.`ORIGIN` FROM `{BQ_PROJECT_ID}.airlines.Airports` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.airlines.Airlines` AS `T2` ON `T1`.`Code` = `T2`.`ORIGIN` WHERE `T1`.`Description` = 'San Diego, CA: San Diego International')

* **Sub-question 3 (flights are to Los Angeles International):**
   * **SQL:** `DEST` = (SELECT DISTINCT `T4`.`DEST` FROM `{BQ_PROJECT_ID}.airlines.Airports` AS `T3` INNER JOIN `{BQ_PROJECT_ID}.airlines.Airlines` AS `T4` ON `T3`.`Code` = `T4`.`DEST` WHERE `T3`.`Description` = 'Los Angeles, CA: Los Angeles International')

* **Main Question (count of flights):**
   * **SQL:** SELECT COUNT(`FL_DATE`) FROM `{BQ_PROJECT_ID}.airlines.Airlines` WHERE `FL_DATE` LIKE '2018/8%' AND `ORIGIN` = (SELECT `T2`.`ORIGIN` FROM `{BQ_PROJECT_ID}.airlines.Airports` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.airlines.Airlines` AS `T2` ON `T1`.`Code` = `T2`.`ORIGIN` WHERE `T1`.`Description` = 'San Diego, CA: San Diego International') AND `DEST` = (SELECT `T4`.`DEST` FROM `{BQ_PROJECT_ID}.airlines.Airports` AS `T3` INNER JOIN `{BQ_PROJECT_ID}.airlines.Airlines` AS `T4` ON `T3`.`Code` = `T4`.`DEST` WHERE `T3`.`Description` = 'Los Angeles, CA: Los Angeles International')

**3. Simplification and Optimization:**

* The query in step 2 is already quite optimized. We are using nested queries to avoid joining the `airlines.Airports` table multiple times in the main query, which could potentially impact performance.

**Final Optimized SQL Query:**
```sql
SELECT COUNT(FL_DATE)
 FROM {BQ_PROJECT_ID}.airlines.Airlines
 WHERE FL_DATE LIKE '2018/8%'
 AND ORIGIN = (
   SELECT DISTINCT T2.ORIGIN
   FROM {BQ_PROJECT_ID}.airlines.Airports AS T1
   INNER JOIN {BQ_PROJECT_ID}.airlines.Airlines AS T2 ON T1.Code = T2.ORIGIN
   WHERE T1.Description = 'San Diego, CA: San Diego International' )
 AND DEST = (
   SELECT DISTINCT T4.DEST
   FROM {BQ_PROJECT_ID}.airlines.Airports AS T3
   INNER JOIN {BQ_PROJECT_ID}.airlines.Airlines AS T4 ON T3.Code = T4.DEST
   WHERE T3.Description = 'Los Angeles, CA: Los Angeles International' )
```

===========
Example 7

**************************
【Database Info】
CREATE TABLE {BQ_PROJECT_ID}.food_inspection.businesses
(
       `business_id` INT64,
       `name` STRING OPTIONS(description="the name of the eatery"),
);

CREATE TABLE {BQ_PROJECT_ID}.food_inspection.inspections
(
       `business_id` INT64 OPTIONS(description="the unique id of the business"),
       `score` INT64 OPTIONS(description="description: the inspection score"),
       `date` DATE,
);

CREATE TABLE {BQ_PROJECT_ID}.food_inspection.violations
(
       `business_id` INT64,
       `date` DATE,
);

**************************
【Question】
Question:
What are the names of the establishments that met all the required standards for 4 consecutive years?
establishment has the same meaning as business; score of 90 or more refers to score ≥ 90; year(date) = 2015; ; met all required standards for 4 consecutive years refers to COUNT(year(date)) = 4 where score = 100;

**************************
【Answer】
Repeating the question and generating the SQL with Recursive Divide-and-Conquer.

**Question**: What are the names of the establishments that met all the required standards for 4 consecutive years? establishment has the same meaning as business; score of 90 or more refers to score ≥ 90; year(date) = 2015; ; met all required standards for 4 consecutive years refers to COUNT(year(date)) = 4 where score = 100;

**1. Divide and Conquer:**

* **Main Question:** What are the names of the establishments that met all the required standards for 4 consecutive years?
   * **Analysis:** We need to find the names of businesses that have a score of 100 for 4 consecutive years. The `food_inspection.businesses` table contains the `name` and the `{BQ_PROJECT_ID}.food_inspection.inspections` table contains the `score` and `date`. We will need to join these tables and filter by score. To check for consecutive years, we'll need to group by business and year, then check if each group has a count of 4.
   * **Pseudo SQL:** SELECT DISTINCT `T2`.`name` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.food_inspection.businesses` AS `T2` ON `T1`.`business_id` = `T2`.`business_id` WHERE  <score = 100> AND <4 consecutive years>

   * **Sub-question 1:** score = 100
       * **Analysis:** This is a simple filter on the `{BQ_PROJECT_ID}.food_inspection.inspections` table where we select rows with a `score` of 100.
       * **Pseudo SQL:** `T1`.`score` = 100

   * **Sub-question 2:** 4 consecutive years
       * **Analysis:** This is more complex. We need to group the inspections by business and year, then check if the count for each group is 4. To get the year from the `date` column, we'll use the `FORMAT_DATE('%Y', date)` function. We'll also need to use window functions to assign a rank to each year within a business, allowing us to check for consecutiveness.
       * **Pseudo SQL:** `T2`.`name` IN (SELECT `T4`.`name` FROM (SELECT `T3`.`name`, `T3`.`years`, row_number() OVER (PARTITION BY `T3`.`name` ORDER BY `T3`.`years`) AS `rowNumber` FROM (SELECT DISTINCT `name`, FORMAT_DATE('%Y', date) AS `years` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.food_inspection.businesses` AS `T2` ON `T1`.`business_id` = `T2`.`business_id` WHERE `T1`.`score` = 100) AS `T3`) AS `T4` GROUP BY `T4`.`name`, date(`T4`.`years` || '-01-01', '-' || (`T4`.`rowNumber` - 1) || ' years') HAVING COUNT(`T4`.`years`) = 4)

       * **Sub-question 2.1:** Get distinct businesses and their inspection years where the score is 100
           * **Analysis:** We need to join `{BQ_PROJECT_ID}.food_inspection.inspections` and `{BQ_PROJECT_ID}.food_inspection.businesses` tables, filter by `score` = 100, and select distinct business names and their inspection years.
           * **Pseudo SQL:** SELECT DISTINCT `name`, FORMAT_DATE('%Y', date) AS `years` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.food_inspection.businesses` AS `T2` ON `T1`.`business_id` = `T2`.`business_id` WHERE `T1`.`score` = 100

       * **Sub-question 2.2:** Assign a rank to each year within a business
           * **Analysis:** We'll use the `row_number()` window function to assign a rank to each year within each business, ordered chronologically. This will help us identify consecutive years later.
           * **Pseudo SQL:** SELECT `T3`.`name`, `T3`.`years`, row_number() OVER (PARTITION BY `T3`.`name` ORDER BY `T3`.`years`) AS `rowNumber` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.food_inspection.businesses` AS `T2` ON `T1`.`business_id` = `T2`.`business_id` WHERE `T1`.`score` = 100` AS `T3`

       * **Sub-question 2.3:** Group by business and consecutive year groups and check if the count is 4
           * **Analysis:** We'll group the results by business name and a calculated date representing the start of each potential 4-year period. This date is calculated by adding (`rowNumber` - 1) years to the first day of the year extracted from the `years` column. We then filter for groups with a count of 4, indicating 4 consecutive years.
           * **Pseudo SQL:** SELECT `T4`.`name` FROM (<previous sub-query>) AS `T4` GROUP BY `T4`.`name`, date(`T4`.`years` || '-01-01', '-' || (`T4`.`rowNumber` - 1) || ' years') HAVING COUNT(`T4`.`years`) = 4

**2. Assembling SQL:**

* **Sub-question 2.1 (distinct businesses and years with score 100):**
   * **SQL:** SELECT DISTINCT `name`, FORMAT_DATE('%Y', date) AS `years` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.food_inspection.businesses` AS `T2` ON `T1`.`business_id` = `T2`.`business_id` WHERE `T1`.`score` = 100

* **Sub-question 2.2 (assign rank to each year within a business):**
   * **SQL:** SELECT `T3`.`name`, `T3`.`years`, row_number() OVER (PARTITION BY `T3`.`name` ORDER BY `T3`.`years`) AS `rowNumber` FROM (SELECT DISTINCT `name`, FORMAT_DATE('%Y', date) AS `years` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.food_inspection.businesses` AS `T2` ON `T1`.`business_id` = `T2`.`business_id` WHERE `T1`.`score` = 100) AS `T3`

* **Sub-question 2.3 (group by business and consecutive year groups):**
   * **SQL:** SELECT `T4`.`name` FROM (SELECT `T3`.`name`, `T3`.`years`, row_number() OVER (PARTITION BY `T3`.`name` ORDER BY `T3`.`years`) AS `rowNumber` FROM (SELECT DISTINCT `name`, FORMAT_DATE('%Y', date) AS `years` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.food_inspection.businesses` AS `T2` ON `T1`.`business_id` = `T2`.`business_id` WHERE `T1`.`score` = 100) AS `T3`) AS `T4` GROUP BY `T4`.`name`, DATE_SUB(DATE(CONCAT(T4.years, '-01-01')), INTERVAL (T4.rowNumber - 1) YEAR)  HAVING COUNT(`T4`.`years`) = 4

* **Sub-question 2 (4 consecutive years):**
   * **SQL:** `T2`.`name` IN (SELECT `T4`.`name` FROM (SELECT `T3`.`name`, `T3`.`years`, row_number() OVER (PARTITION BY `T3`.`name` ORDER BY `T3`.`years`) AS `rowNumber` FROM (SELECT DISTINCT `name`, FORMAT_DATE('%Y', date) AS `years` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.food_inspection.businesses` AS `T2` ON `T1`.`business_id` = `T2`.`business_id` WHERE `T1`.`score` = 100) AS `T3`) AS `T4` GROUP BY `T4`.`name`, DATE_SUB(DATE(CONCAT(T4.years, '-01-01')), INTERVAL (T4.rowNumber - 1) YEAR)  HAVING COUNT(`T4`.`years`) = 4)

* **Main Question (names of establishments):**
   * **SQL:** SELECT DISTINCT `T2`.`name` FROM `{BQ_PROJECT_ID}.inspections` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.businesses` AS `T2` ON `T1`.`business_id` = `T2`.`business_id` WHERE  `T1`.`score` = 100 AND `T2`.`name` IN (SELECT `T4`.`name` FROM (SELECT `T3`.`name`, `T3`.`years`, row_number() OVER (PARTITION BY `T3`.`name` ORDER BY `T3`.`years`) AS `rowNumber` FROM (SELECT DISTINCT `name`, FORMAT_DATE('%Y', date) AS `years` FROM `{BQ_PROJECT_ID}.food_inspection.inspections` AS `T1` INNER JOIN `{BQ_PROJECT_ID}.food_inspection.businesses` AS `T2` ON `T1`.`business_id` = `T2`.`business_id` WHERE `T1`.`score` = 100) AS `T3`) AS `T4` GROUP BY `T4`.`name`, DATE_SUB(DATE(CONCAT(T4.years, '-01-01')), INTERVAL (T4.rowNumber - 1) YEAR) HAVING COUNT(`T4`.`years`) = 4)

**3. Simplification and Optimization:**

* The final SQL query from step 2 can be simplified by merging the nested queries into a single query with a `WITH` clause. This improves readability and potentially performance.

**Final Optimized SQL Query:**
```sql
SELECT DISTINCT T4.name
 FROM ( SELECT T3.name, T3.years, row_number()
 OVER (PARTITION BY T3.name ORDER BY T3.years)
 AS rowNumber FROM ( SELECT DISTINCT name, FORMAT_DATE('%Y', date)
 AS years FROM {BQ_PROJECT_ID}.food_inspection.inspections AS T1
 INNER JOIN {BQ_PROJECT_ID}.food_inspection.businesses AS T2 ON T1.business_id = T2.business_id
 WHERE T1.score = 100 ) AS T3 ) AS T4
 GROUP BY T4.name, DATE_SUB(DATE(CONCAT(T4.years, '-01-01')), INTERVAL (T4.rowNumber - 1) YEAR) HAVING COUNT(T4.years) = 4
```
===========
Example 8

**************************
【Database Info】
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
  symptom_Abdominal_obesity FLOAT64,
  symptom_Abdominal_pain FLOAT64,
  symptom_Acne FLOAT64
)
PARTITION BY date
CLUSTER BY country_region_code, sub_region_1_code, sub_region_2_code, sub_region_2;

**************************
【Question】
Question:
Find the day in which the symptom that occurs most frequently is headache.

**************************
【Answer】
Repeating the question and generating the SQL with Recursive Divide-and-Conquer.

**Question**: Find the day in which the symptom that occurs most frequently is headache.

Analysis: We need to determine the day (day of the week) when the frequency of searches for the symptom "headache" is the highest. This involves:
   - Grouping the data by the day of the week.
   - Counting the occurrences of searches for "headache."
   - Sorting the counts in descending order and selecting the day with the highest count.

Pseudo SQL:
   SELECT FORMAT_DATE('%A', date) AS day, COUNT(*) AS headache_count
   FROM `bigquery-public-data.covid19_symptom_search.symptom_search_sub_region_2_daily`
   WHERE symptom_Headache > 0
   GROUP BY day
   ORDER BY headache_count DESC
   LIMIT 1

Sub-question 1: Extract the day of the week from the date column.
   - Analysis: Use the FORMAT_DATE function with the %A format specifier to extract the day name (e.g., "Monday," "Tuesday") from the date column.

Pseudo SQL:
   SELECT FORMAT_DATE('%A', date) AS day
   FROM `bigquery-public-data.covid19_symptom_search.symptom_search_sub_region_2_daily`

Sub-question 2: Filter rows where "headache" searches occurred.
   - Analysis: Only include rows where the symptom "headache" has a positive value (symptom_Headache > 0).

Pseudo SQL:
   SELECT date
   FROM `bigquery-public-data.covid19_symptom_search.symptom_search_sub_region_2_daily`
   WHERE symptom_Headache > 0

Sub-question 3: Count the occurrences of "headache" searches grouped by day of the week.
   - Analysis: After filtering the data for rows where symptom_Headache > 0, group the data by the day of the week and count the number of rows for each day.

Pseudo SQL:
   SELECT FORMAT_DATE('%A', date) AS day, COUNT(*) AS headache_count
   FROM `bigquery-public-data.covid19_symptom_search.symptom_search_sub_region_2_daily`
   WHERE symptom_Headache > 0
   GROUP BY day

Sub-question 4: Sort the results by the count in descending order and get the top day.
   - Analysis: Use the ORDER BY clause to sort by the count of "headache" searches in descending order. Limit the result to 1 to get the top day.

Pseudo SQL:
   SELECT FORMAT_DATE('%A', date) AS day, COUNT(*) AS headache_count
   FROM `bigquery-public-data.covid19_symptom_search.symptom_search_sub_region_2_daily`
   WHERE symptom_Headache > 0
   GROUP BY day
   ORDER BY headache_count DESC
   LIMIT 1

Assembling SQL
   - Combining all sub-questions into the final query:

**Final Optimized SQL Query:**
```sql
SELECT 
  FORMAT_DATE('%A', PARSE_DATE('%Y-%m-%d', date)) AS day,
  COUNT(*) AS headache_count
FROM 
  `bigquery-public-data`.`covid19_symptom_search`.`symptom_search_country_daily`
GROUP BY 
  day
ORDER BY 
  headache_count DESC
LIMIT 1;
```

Now is the real question, following the instruction and examples, generate the GoogleSQL with Recursive Divide-and-Conquer approach.
Follow all steps from the strategy. When you get to the final query, output the query string ONLY in the format ```sql ... ```. Make sure you only output one single query.
Table names always should be exactly the same as the table names mentioned in the database schema, for example, `{BQ_PROJECT_ID}.airlines.Airlines` instead of `Airlines`.

**************************
【Table creation statements】
{SCHEMA}

**************************
【Question】
Question:
{QUESTION}

**************************
【Answer】
Repeating the question and generating the SQL with Recursive Divide-and-Conquer.
"""

```


---

## 文件: data-science\data_science\sub_agents\bigquery\chase_sql\llm_utils.py

```python
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

"""This code contains the LLM utils for the CHASE-SQL Agent."""

from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
import functools
import os
import random
import time
from typing import Callable, List, Optional

import dotenv
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerationConfig
from vertexai.generative_models import HarmBlockThreshold
from vertexai.generative_models import HarmCategory
from vertexai.preview import caching
from vertexai.preview.generative_models import GenerativeModel


dotenv.load_dotenv(override=True)

SAFETY_FILTER_CONFIG = {
    HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
}

GCP_PROJECT = os.getenv('GCP_PROJECT')
GCP_REGION = os.getenv('GCP_REGION')

GEMINI_AVAILABLE_REGIONS = [
    'europe-west3',
    'australia-southeast1',
    'us-east4',
    'northamerica-northeast1',
    'europe-central2',
    'us-central1',
    'europe-north1',
    'europe-west8',
    'us-south1',
    'us-east1',
    'asia-east2',
    'us-west1',
    'europe-west9',
    'europe-west2',
    'europe-west6',
    'europe-southwest1',
    'us-west4',
    'asia-northeast1',
    'asia-east1',
    'europe-west1',
    'europe-west4',
    'asia-northeast3',
    'asia-south1',
    'asia-southeast1',
    'southamerica-east1',
]
GEMINI_URL = 'projects/{GCP_PROJECT}/locations/{region}/publishers/google/models/{model_name}'

aiplatform.init(
    project=GCP_PROJECT,
    location=GCP_REGION,
)
vertexai.init(project=GCP_PROJECT, location=GCP_REGION)


def retry(max_attempts=8, base_delay=1, backoff_factor=2):
  """Decorator to add retry logic to a function.

  Args:
      max_attempts (int): The maximum number of attempts.
      base_delay (int): The base delay in seconds for the exponential backoff.
      backoff_factor (int): The factor by which to multiply the delay for each
        subsequent attempt.

  Returns:
      Callable: The decorator function.
  """

  def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      attempts = 0
      while attempts < max_attempts:
        try:
          return func(*args, **kwargs)
        except Exception as e:  # pylint: disable=broad-exception-caught
          print(f'Attempt {attempts + 1} failed with error: {e}')
          attempts += 1
          if attempts >= max_attempts:
            raise e
          delay = base_delay * (backoff_factor**attempts)
          delay = delay + random.uniform(0, 0.1 * delay)
          time.sleep(delay)

    return wrapper

  return decorator


class GeminiModel:
  """Class for the Gemini model."""

  def __init__(
      self,
      model_name: str = 'gemini-1.5-pro',
      finetuned_model: bool = False,
      distribute_requests: bool = False,
      cache_name: str | None = None,
      temperature: float = 0.01,
      **kwargs,
  ):
    self.model_name = model_name
    self.finetuned_model = finetuned_model
    self.arguments = kwargs
    self.distribute_requests = distribute_requests
    self.temperature = temperature
    model_name = self.model_name
    if not self.finetuned_model and self.distribute_requests:
      random_region = random.choice(GEMINI_AVAILABLE_REGIONS)
      model_name = GEMINI_URL.format(
          GCP_PROJECT=GCP_PROJECT,
          region=random_region,
          model_name=self.model_name,
      )
    if cache_name is not None:
      cached_content = caching.CachedContent(cached_content_name=cache_name)
      self.model = GenerativeModel.from_cached_content(
          cached_content=cached_content
      )
    else:
      self.model = GenerativeModel(model_name=model_name)

  @retry(max_attempts=12, base_delay=2, backoff_factor=2)
  def call(self, prompt: str, parser_func=None) -> str:
    """Calls the Gemini model with the given prompt.

    Args:
        prompt (str): The prompt to call the model with.
        parser_func (callable, optional): A function that processes the LLM
          output. It takes the model's response as input and returns the
          processed result.

    Returns:
        str: The processed response from the model.
    """
    response = self.model.generate_content(
        prompt,
        generation_config=GenerationConfig(
            temperature=self.temperature,
            **self.arguments,
        ),
        safety_settings=SAFETY_FILTER_CONFIG,
    ).text
    if parser_func:
      return parser_func(response)
    return response

  def call_parallel(
      self,
      prompts: List[str],
      parser_func: Optional[Callable[[str], str]] = None,
      timeout: int = 60,
      max_retries: int = 5,
  ) -> List[Optional[str]]:
    """Calls the Gemini model for multiple prompts in parallel using threads with retry logic.

    Args:
        prompts (List[str]): A list of prompts to call the model with.
        parser_func (callable, optional): A function to process each response.
        timeout (int): The maximum time (in seconds) to wait for each thread.
        max_retries (int): The maximum number of retries for timed-out threads.

    Returns:
        List[Optional[str]]:
        A list of responses, or None for threads that failed.
    """
    results = [None] * len(prompts)

    def worker(index: int, prompt: str):
      """Thread worker function to call the model and store the result with retries."""
      retries = 0
      while retries <= max_retries:
        try:
          return  self.call(prompt, parser_func)
        except Exception as e:  # pylint: disable=broad-exception-caught
          print(f'Error for prompt {index}: {str(e)}')
          retries += 1
          if retries <= max_retries:
            print(f'Retrying ({retries}/{max_retries}) for prompt {index}')
            time.sleep(1)  # Small delay before retrying
          else:
            return f'Error after retries: {str(e)}'

    # Create and start one thread for each prompt
    with ThreadPoolExecutor(max_workers=len(prompts)) as executor:
      future_to_index = {
          executor.submit(worker, i, prompt): i
          for i, prompt in enumerate(prompts)
      }

      for future in as_completed(future_to_index, timeout=timeout):
        index = future_to_index[future]
        try:
          results[index] = future.result()
        except Exception as e:  # pylint: disable=broad-exception-caught
          print(f'Unhandled error for prompt {index}: {e}')
          results[index] = 'Unhandled Error'

    # Handle remaining unfinished tasks after the timeout
    for future in future_to_index:
      index = future_to_index[future]
      if not future.done():
        print(f'Timeout occurred for prompt {index}')
        results[index] = 'Timeout'

    return results

```


---

## 文件: data-science\data_science\sub_agents\bigquery\chase_sql\qp_prompt_template.py

```python
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

"""Query Plan (QP) prompt template."""

QP_PROMPT_TEMPLATE = """
You are an experienced database expert.
Now you need to generate a GoogleSQL or BigQuery query given the database information, a question and some additional information.
The database structure is defined by table schemas (some columns provide additional column descriptions in the options).

Given the table schema information description and the `Question`. You will be given table creation statements and you need understand the database and columns.

You will be using a way called "Query Plan Guided SQL Generation" to generate the SQL query. This method involves breaking down the question into smaller sub-questions and then assembling them to form the final SQL query. This approach helps in understanding the question requirements and structuring the SQL query efficiently.

Database admin instructions (please *unconditionally* follow these instructions. Do *not* ignore them or use them as hints.):
1. **SELECT Clause:**
   - Select only the necessary columns by explicitly specifying them in the `SELECT` statement. Avoid redundant columns or values.

2. **Aggregation (MAX/MIN):**
   - Ensure `JOIN`s are completed before applying `MAX()` or `MIN()`. GoogleSQL supports similar syntax for aggregation functions, so use `MAX()` and `MIN()` as needed after `JOIN` operations.

3. **ORDER BY with Distinct Values:**
   - In GoogleSQL, `GROUP BY <column>` can be used before `ORDER BY <column> ASC|DESC` to get distinct values and sort them.

4. **Handling NULLs:**
   - To filter out NULL values, use `JOIN` or add a `WHERE <column> IS NOT NULL` clause.

5. **FROM/JOIN Clauses:**
   - Only include tables essential to the query. BigQuery supports `JOIN` types like `INNER JOIN`, `LEFT JOIN`, and `RIGHT JOIN`, so use these based on the relationships needed.

6. **Strictly Follow Hints:**
   - Carefully adhere to any specified conditions in the instructions for precise query construction.

7. **Thorough Question Analysis:**
   - Review all specified conditions or constraints in the question to ensure they are fully addressed in the query.

8. **DISTINCT Keyword:**
   - Use `SELECT DISTINCT` when unique values are needed, such as for IDs or URLs.

9. **Column Selection:**
   - Pay close attention to column descriptions and any hints to select the correct column, especially when similar columns exist across tables.

10. **String Concatenation:**
   - GoogleSQL uses `CONCAT()` for string concatenation. Avoid using `||` and instead use `CONCAT(column1, ' ', column2)` for concatenation.

11. **JOIN Preference:**
   - Use `INNER JOIN` when appropriate, and avoid nested `SELECT` statements if a `JOIN` will achieve the same result.

12. **GoogleSQL Functions Only:**
   - Use functions available in GoogleSQL. Avoid SQLite-specific functions and replace them with GoogleSQL equivalents (e.g., `FORMAT_DATE` instead of `STRFTIME`).

13. **Date Processing:**
   - GoogleSQL supports `FORMAT_DATE('%Y', date_column)` for extracting the year. Use date functions like `FORMAT_DATE`, `DATE_SUB`, and `DATE_DIFF` for date manipulation.

14. **Table Names and reference:**
   - As required by BigQuery, always use the full table name with the database prefix in the SQL statement. For example, "SELECT * FROM example_bigquery_database.table_a", not just "SELECT * FROM table_a"

15. **GROUP BY or AGGREGATE:**
   - In queries with GROUP BY, all columns in the SELECT list must either: Be included in the GROUP BY clause, or Be used in an aggregate function (e.g., MAX, MIN, AVG, COUNT, SUM).

Here are some examples
===========
Example 1

**************************
【Table creation statements】
CREATE TABLE {BQ_PROJECT_ID}.restaurant.generalinfo
(
 id_restaurant INT64,
 food_type STRING OPTIONS(description="the food type"),
 city STRING OPTIONS(description="the city where the restaurant is located in"),
);

CREATE TABLE {BQ_PROJECT_ID}.restaurant.location
(
 id_restaurant INT64,
 street_name STRING OPTIONS(description="the street name of the restaurant"),
 city STRING OPTIONS(description="the city where the restaurant is located in foreign key (id_restaurant) references generalinfo (id_restaurant) on update cascade on delete cascade"),
);

**************************
【Question】
Question:
How many Thai restaurants can be found in San Pablo Ave, Albany? Thai restaurant refers to food_type = 'thai'; San Pablo Ave Albany refers to street_name = 'san pablo ave' AND T1.city = 'albany'

**************************
【Answer】
Repeating the question and generating the SQL with Recursive Divide-and-Conquer.
**Question**: How many Thai restaurants can be found in San Pablo Ave, Albany? Thai restaurant refers to food_type = 'thai'; San Pablo Ave Albany refers to street_name = 'san pablo ave' AND T1.city = 'albany'


**Query Plan**:

** Preparation Steps:**
1. Initialize the process: Start preparing to execute the query.
2. Prepare storage: Set up storage space (registers) to hold temporary results, initializing them to NULL.
3. Open the location table: Open the location table so we can read from it.
4. Open the generalinfo table: Open the generalinfo table so we can read from it.

** Matching Restaurants:**
1. Start reading the location table: Move to the first row in the location table.
2. Check if the street matches: Look at the street_name column of the current row in location. If it’s not "san pablo ave," skip this row.
3. Identify the matching row: Store the identifier (row ID) of this location entry.
4. Find the corresponding row in generalinfo: Use the row ID from location to directly find the matching row in generalinfo.
5. Check if the food type matches: Look at the food_type column in generalinfo. If it’s not "thai," skip this row.
6. Check if the city matches: Look at the city column in generalinfo. If it’s not "albany," skip this row.

** Counting Restaurants:**
1. Prepare to count this match: If all checks pass, prepare to include this row in the final count.
2. Count this match: Increment the count for each row that meets all the criteria.
3. Move to the next row in location: Go back to the location table and move to the next row, repeating the process until all rows are checked.
4. Finalize the count: Once all rows have been checked, finalize the count of matching rows.
5. Prepare the result: Copy the final count to prepare it for output.

** Delivering the Result:**
1. Output the result: Output the final count, which is the number of restaurants that match all the specified criteria.
2. End the process: Stop the query execution process.
3. Setup phase: Before starting the actual query execution, the system prepares the specific values it will be looking for, like "san pablo ave," "thai," and "albany."

**Final Optimized SQL Query:**
```sql
SELECT COUNT(T1.id_restaurant)
 FROM {BQ_PROJECT_ID}.restaurant.generalinfo AS T1
 INNER JOIN {BQ_PROJECT_ID}.restaurant.location AS T2 ON T1.id_restaurant = T2.id_restaurant
 WHERE T1.food_type = 'thai' AND T1.city = 'albany' AND T2.street_name = 'san pablo ave'
```

===========
Example 2

**************************
【Database Info】
CREATE TABLE {BQ_PROJECT_ID}.financial.account (
   account_id INT64,
   district_id INT64,
   frequency STRING,
   date DATE,
);
CREATE TABLE {BQ_PROJECT_ID}.financial.client (
   client_id INT64,
   gender STRING,
   birth_date DATE,
   district_id INT64,
);
CREATE TABLE {BQ_PROJECT_ID}.financial.district (
   district_id INT64,
   a4 STRING OPTIONS(description="Assuming A4 and A11 are strings due to examples"),
   a11 STRING,
);

**************************
【Question】
Question:
What is the gender of the youngest client who opened account in the lowest average salary branch? Given that Later birthdate refers to younger age; A11 refers to average salary

**************************
【Answer】
Repeating the question and generating the SQL with Recursive Divide-and-Conquer.
**Question**: What is the gender of the youngest client who opened account in the lowest average salary branch? Given that Later birthdate refers to younger age; A11 refers to average salary

**Query Plan**:

** Preparation Steps: **
1. Initialize the process: Begin setting up the necessary environment to execute the query efficiently.
2. Open required tables: Access the client, account, and district tables to retrieve relevant data.
3. Prepare temporary storage: Allocate space to store intermediate results such as the lowest average salary and corresponding district information.

** Identify the Branch with Lowest Average Salary: **
1. Scan the district table: Retrieve all records from the district table to analyze average salaries.
2. Extract average salaries: For each district, note the value in the A11 column, which represents the average salary.
3. Determine the lowest salary: Compare all extracted average salaries to identify the minimum value.
4. Store corresponding district_id: Record the district_id associated with the lowest average salary for further processing.

** Find Clients in the Identified District: **
1. Join client and account tables: Merge records where client.client_id matches account.account_id to associate clients with their accounts.
2. Filter by district_id: Select only those records where account.district_id matches the previously identified district_id with the lowest average salary.
3. Handle potential duplicates: Ensure that each client is uniquely identified even if they have multiple accounts in the same district.

** Identify the Youngest Client: **
1. Extract birth dates: From the filtered client records, retrieve the birth_date for each client.
2. Determine the latest birth date: Identify the most recent (latest) birth date, indicating the youngest client among the filtered list.
3. Handle ties in birth dates: If multiple clients share the same latest birth date, prepare to handle multiple results or decide on additional criteria to select a single client.

** Retrieve Gender Information: **
1. Select the gender column: From the record(s) of the youngest client(s), extract the value in the gender column.
2. Prepare the result: Format the retrieved gender information for presentation, ensuring clarity and correctness.

** Finalize and Deliver the Result: **
1. Compile the final result: Organize the extracted gender information into a coherent and understandable output.
2. Clean up resources: Close any open table connections and release temporary storage used during query execution.
3. Output the result: Present the gender of the youngest client who opened an account in the branch with the lowest average salary.

**Final Optimized SQL Query:**
```sql
SELECT `T1`.`gender`
 FROM `{BQ_PROJECT_ID}.financial.client` AS `T1`
 INNER JOIN `{BQ_PROJECT_ID}.financial.district` AS `T2`
 ON `T1`.`district_id` = `T2`.`district_id`
 ORDER BY `T2`.`A11` ASC, `T1`.`birth_date` DESC NULLS LAST
 LIMIT 1
```
===========
Example 3 (dividing into two parallel sub-questions)

**************************
【Database Info】
CREATE TABLE {BQ_PROJECT_ID}.olympics.games
(
 id INT64,
 games_year INT64 OPTIONS(description="description: the year of the game"),
 games_name STRING,
);

CREATE TABLE {BQ_PROJECT_ID}.olympics.games_city
(
 games_id INT64,
 city_id INT64 OPTIONS(description="the id of the city that held the game Maps to city(id)"),
);

CREATE TABLE {BQ_PROJECT_ID}.olympics.city
(
 id INT64,
 city_name STRING,
);

**************************
【Question】
Question:
From 1900 to 1992, how many games did London host? From 1900 to 1992 refers to games_year BETWEEN 1900 AND 1992; London refers to city_name = 'London'; games refer to games_name;

**************************
【Answer】
Repeating the question and generating the SQL with Recursive Divide-and-Conquer.
**Question**: From 1900 to 1992, how many games did London host? From 1900 to 1992 refers to games_year BETWEEN 1900 AND 1992; London refers to city_name = 'London'; games refer to games_name;

**Query Plan**:

** Preparation Steps: **
1.Initialize the process: Set up the environment to begin query execution, including necessary variables and temporary storage.
2. Open required tables: Open the games_city, city, and games tables to access relevant data.
3. Prepare filtering values: Set up the specific values to filter the data, such as the year range (1900-1992) and the city name 'London'.

** Filter and Identify Relevant Data: **
1. Scan games_city table: Retrieve records from the games_city table to match games with the cities where they were hosted.
2. Fetch the corresponding city_id: For each row in games_city, extract the city_id to find out which city hosted the game.
3 .Match city_id with city_name: Use the city_id to look up the corresponding city_name in the city table.
4. Filter by city_name = 'London': Select only those rows where the city_name is 'London'.

** Further Filter by Year Range: **
1. Extract games_id: For rows that match 'London', retrieve the games_id from the games_city table.
2. Find matching games_year: Use the games_id to look up the corresponding games_year in the games table.
3. Filter by games_year between 1900 and 1992: Select only those rows where the games_year falls within the specified range (1900-1992).

** Count the Matching Rows: **
1. Initialize the count: Prepare to count the number of matching rows that meet all the criteria.
2. Count the valid entries: For each row that matches the conditions (city_name = 'London' and games_year between 1900 and 1992), increment the count.
3. Store the final count: Once all rows have been processed, store the total count as the final result.

** Finalize and Deliver the Result: **
1. Prepare the result for output: Format the final count of games hosted by London between 1900 and 1992.
2. Output the final count: Deliver the count as the query result.
3. Clean up resources: Close any open table connections and release temporary storage used during query execution.

**Final Optimized SQL Query:**
```sql
SELECT COUNT(T3.id)
 FROM {BQ_PROJECT_ID}.olympics.games_city AS T1
 INNER JOIN {BQ_PROJECT_ID}.olympics.city AS T2 ON T1.city_id = T2.id
 INNER JOIN {BQ_PROJECT_ID}.olympics.games AS T3 ON T1.games_id = T3.id
 WHERE T2.city_name = 'London' AND T3.games_year
 BETWEEN 1900 AND 1992
```

===========
Example 4

**************************
【Database Info】
CREATE TABLE {BQ_PROJECT_ID}.retails.employees (
   employee_id INT64,
   department_id INT64,
   salary INT64,
);

**************************
【Question】
Question:
How many employees earn over $100,000?

**************************
【Answer】
Repeating the question and generating the SQL with Recursive Divide-and-Conquer.
**Question:** How many employees earn over $100,000?

** Query Plan**:

** Preparation Steps: **
1.cInitialize the process: Begin by setting up the environment for query execution, including initializing variables and temporary storage.
2. Open the employees table: Access the employees table to retrieve the relevant data.

** Filtering Employees by Salary: **
1. Scan the employees table: Begin reading rows from the employees table.
2. Fetch the salary column: For each row, retrieve the value from the salary column.
3. Compare salary against $100,000: Check if the salary value is greater than $100,000.
4. Identify matching rows: For rows where the salary exceeds $100,000, prepare to count these entries.

** Counting the Matches: **
1. Initialize the count: Set up a counter to keep track of how many employees meet the salary condition.
2. Increment the count: For each row where the salary is above $100,000, increment the counter.
3. Store the final count: Once all rows have been processed, store the total count of matching employees.

** Finalize and Deliver the Result: **
1. Prepare the result for output: Format the final count for presentation.
2. Output the final count: Deliver the count as the query result, indicating how many employees earn over $100,000.
3. Clean up resources: Close the employees table and release any temporary storage used during query execution.

**Final Optimized SQL Query:**
```sql
SELECT COUNT(*) FROM {BQ_PROJECT_ID}.retails.employees WHERE salary > 100000;
```

===========
Example 6

**************************
【Database Info】
CREATE TABLE {BQ_PROJECT_ID}.airlines.Airlines
(
 FL_DATE STRING OPTIONS(description="flight date"),
 ORIGIN STRING OPTIONS(description="airport of origin"),
 DEST STRING OPTIONS(description="Destination airport"),
);

CREATE TABLE {BQ_PROJECT_ID}.airlines.Airports
(
 Code STRING,
 Description STRING,
);

**************************
【Question】
Question:
How many flights were there from San Diego International airport to Los Angeles International airport in the August of 2018?
flights from refers to ORIGIN; San Diego International airport refers to Description = 'San Diego, CA: San Diego International'; flights to refers to DEST; Los Angeles International airport refers to Description = 'Los Angeles, CA: Los Angeles International'; in the August of 2018 refers to FL_DATE like '2018/8%';

**************************
【Answer】
**Repeating the question and generating the SQL with Recursive Divide-and-Conquer.**

**Question**: How many flights were there from San Diego International airport to Los Angeles International airport in the August of 2018? flights from refers to ORIGIN; San Diego International airport refers to Description = 'San Diego, CA: San Diego International'; flights to refers to DEST; Los Angeles International airport refers to Description = 'Los Angeles, CA: Los Angeles International'; in the August of 2018 refers to FL_DATE like '2018/8%';

** Query Plan**:

** Preparation Steps: **
1. Initialize the process: Set up the environment and prepare for query execution by initializing variables and temporary storage.
2. Open required tables: Open the Airlines and Airports tables to access relevant data.

** Identify Relevant Flights: **
1. Fetch the FL_DATE column: Start reading the FL_DATE column from the Airlines table.
2. Filter by August 2018: Use the condition FL_DATE LIKE '2018/8%' to filter flights that occurred in August 2018.
3. Join with Airports for ORIGIN: Identify flights originating from 'San Diego, CA: San Diego International' by joining the Airlines table with the Airports table on the ORIGIN field.
4. Join with Airports for DEST: Similarly, identify flights destined for 'Los Angeles, CA: Los Angeles International' by joining the Airlines table with the Airports table on the DEST field.

** Count the Matching Flights: **
1. Initialize the count: Set up a counter to keep track of how many flights match the criteria.
2. Increment the count: For each flight that meets the conditions (originating from San Diego International and destined for Los Angeles International in August 2018), increment the counter.
3. Store the final count: Once all rows have been processed, store the total count of matching flights.

** Finalize and Deliver the Result: **
1. Prepare the result for output: Format the final count for presentation, ensuring clarity and correctness.
2. Output the final count: Deliver the count as the query result, indicating how many flights met the specified criteria.
3. Clean up resources: Close any open table connections and release temporary storage used during query execution.

**Final Optimized SQL Query:**
```sql
SELECT COUNT(FL_DATE)
 FROM {BQ_PROJECT_ID}.airlines.Airlines
 WHERE FL_DATE LIKE '2018/8%'
 AND ORIGIN = (
   SELECT DISTINCT T2.ORIGIN
   FROM {BQ_PROJECT_ID}.airlines.Airports AS T1
   INNER JOIN {BQ_PROJECT_ID}.airlines.Airlines AS T2 ON T1.Code = T2.ORIGIN
   WHERE T1.Description = 'San Diego, CA: San Diego International' )
 AND DEST = (
   SELECT DISTINCT T4.DEST
   FROM {BQ_PROJECT_ID}.airlines.Airports AS T3
   INNER JOIN {BQ_PROJECT_ID}.airlines.Airlines AS T4 ON T3.Code = T4.DEST
   WHERE T3.Description = 'Los Angeles, CA: Los Angeles International' )
```

===========
Example 7

**************************
【Database Info】
CREATE TABLE {BQ_PROJECT_ID}.food_inspection.businesses
(
       `business_id` INT64,
       `name` STRING OPTIONS(description="the name of the eatery"),
);

CREATE TABLE {BQ_PROJECT_ID}.food_inspection.inspections
(
       `business_id` INT64 OPTIONS(description="the unique id of the business"),
       `score` INT64 OPTIONS(description="description: the inspection score"),
       `date` DATE,
);

CREATE TABLE {BQ_PROJECT_ID}.food_inspection.violations
(
       `business_id` INT64,
       `date` DATE,
);

**************************
【Question】
Question:
What are the names of the establishments that met all the required standards for 4 consecutive years?
establishment has the same meaning as business; score of 90 or more refers to score ≥ 90; year(date) = 2015; ; met all required standards for 4 consecutive years refers to COUNT(year(date)) = 4 where score = 100;

**************************
【Answer】
Repeating the question and generating the SQL with Recursive Divide-and-Conquer.

**Question**: What are the names of the establishments that met all the required standards for 4 consecutive years? establishment has the same meaning as business; score of 90 or more refers to score ≥ 90; year(date) = 2015; ; met all required standards for 4 consecutive years refers to COUNT(year(date)) = 4 where score = 100;

** Query Plan**:

** Preparation Steps: **
1. Initialize the process: Set up the environment and prepare for query execution, including initializing variables and temporary storage.
2. Open required tables: Open the businesses, inspections, and violations tables to access relevant data.

** Filter and Identify Relevant Inspections: **
1. Scan the inspections table: Start reading rows from the inspections table.
2. Filter by score of 100: Select only those inspections where the score is 100, indicating that the establishment met all required standards.
3. Extract year from the inspection date: Use the FORMAT_DATE('%Y', date) function to extract the year from the inspection date.
4. Join with businesses table: Match each inspection to the corresponding business by joining on business_id.

** Identify Businesses Meeting Standards for 4 Consecutive Years: **
1. Aggregate by business and year: Group the data by business name and the extracted year to count the number of years each business met the required standards.
3. Apply row numbering: Use ROW_NUMBER() with a partition by business name and order by year to identify consecutive years.
3. Filter for 4 consecutive years: Group by business name and ensure that the count of years with the required score is exactly 4, indicating 4 consecutive years of meeting the standards.

** Count and Finalize the Results: **
1. Count the matching businesses: For each business, count the number of years that meet the criteria.
2. Select distinct business names: Extract the names of businesses that have met the required standards for 4 consecutive years.
3. Store and prepare the result: Once all businesses have been processed, store the result and prepare it for output.

** Deliver the Final Result: **
1. Prepare the result for output: Format the final list of business names for presentation.
2. Output the final result: Deliver the names of the businesses that met the required standards for 4 consecutive years.
3. Clean up resources: Close any open table connections and release temporary storage used during query execution.

**Final Optimized SQL Query:**
```sql
SELECT DISTINCT T4.name
 FROM ( SELECT T3.name, T3.years, row_number()
 OVER (PARTITION BY T3.name ORDER BY T3.years)
 AS rowNumber FROM ( SELECT DISTINCT name, FORMAT_DATE('%Y', date)
 AS years FROM {BQ_PROJECT_ID}.food_inspection.inspections AS T1
 INNER JOIN {BQ_PROJECT_ID}.food_inspection.businesses AS T2 ON T1.business_id = T2.business_id
 WHERE T1.score = 100 ) AS T3 ) AS T4
 GROUP BY T4.name, DATE_SUB(DATE(CONCAT(T4.years, '-01-01')), INTERVAL (T4.rowNumber - 1) YEAR) HAVING COUNT(T4.years) = 4
```

===========
Example 8

**************************
【Database Info】
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
  symptom_Abdominal_obesity FLOAT64,
  symptom_Abdominal_pain FLOAT64,
  symptom_Acne FLOAT64
)
PARTITION BY date
CLUSTER BY country_region_code, sub_region_1_code, sub_region_2_code, sub_region_2;

**************************
【Question】
Question:
Find the day in which the symptom that occurs most frequently is headache.

**************************
【Answer】
Repeating the question and generating the SQL with Recursive Divide-and-Conquer.

**Question**: Find the day in which the symptom that occurs most frequently is headache.

** Query Plan**:

**  Preparation Steps : **
1. Initialize the process: Set up the environment and prepare for query execution, including initializing variables and temporary storage.
2. Open the symptom_search_sub_region_2_daily table: Access the table containing daily symptom search data.

** Extract the headache symptom: **
1. Scan the table: Start reading rows from the symptom_search_sub_region_2_daily table.
2. Identify the headache symptom: Look for the column containing the headache symptom data.
3. Extract the headache symptom value: For each row, extract the value from the headache symptom column.
4. Aggregate by date: Group the data by date to count the occurrences of the headache symptom on each day.

** Sort by frequency: **
1. Order the results in descending order of symptom frequency.
2. Limit the results: Extract the single day with the highest count.

** Step 2: Identify Subtasks **
1. Extract relevant symptom column: While "headache" is not explicitly listed, its frequency might be tracked in a related table (e.g., symptom_search_country_daily) as per the given gold query.
2. Group data by day of the week: Use FORMAT_DATE('%A', date) to extract the day of the week from each date.
3. Aggregate by count: Count the occurrences of the "headache" symptom across dates and group by the day of the week.
4. Sort by frequency: Order the results in descending order of symptom frequency.
5. Limit the results: Extract the single day with the highest count.

** Step 3: Formulate the Query **
1. From the subtasks, the query will:
2. Select the day of the week using FORMAT_DATE('%A', date).
3. Aggregate counts grouped by the day.
4. Sort the results by the aggregated count in descending order.
5. Limit the results to the top record.

** Step 4: Construct the Query **
1. Combining all subtasks, the final query is:
2. SELECT COUNT(symptom_headache) FROM {BQ_PROJECT_ID}.covid19_symptom_search.symptom_search_sub_region_2_daily GROUP BY FORMAT_DATE('%A', date) ORDER BY COUNT(symptom_headache) DESC LIMIT 1;

** Step 5: Finalize the Query **
**Final Optimized SQL Query:**
```sql
SELECT 
  FORMAT_DATE('%A', PARSE_DATE('%Y-%m-%d', date)) AS day,
  COUNT(*) AS headache_count
FROM 
  {BQ_PROJECT_ID}.covid19_symptom_search.symptom_search_country_daily
GROUP BY 
  day
ORDER BY 
  headache_count DESC
LIMIT 1;
```

Now is the real question, following the instruction and examples, generate the GoogleSQL with Recursive Divide-and-Conquer approach.
Follow all steps from the strategy. When you get to the final query, output the query string ONLY in the format ```sql ... ```. Make sure you only output one single query.

**************************
【Table creation statements】
{SCHEMA}

**************************
【Question】
Question:
{QUESTION}

**************************
【Answer】
Repeating the question and generating the SQL with Recursive Divide-and-Conquer.
"""

```


---

## 文件: data-science\data_science\sub_agents\bigquery\chase_sql\sql_postprocessor\correction_prompt_template.py

```python
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

"""Prompt template for making any corrections to the translation of SQL."""

CORRECTION_PROMPT_TEMPLATE_V1_0 = """
You are an expert in multiple databases and SQL dialects.
You are given a SQL query that is formatted for the SQL dialect:
{sql_dialect}

The SQL query is:
{sql_query}
{schema_insert}
This SQL query could have the following errors:
{errors}

Please correct the SQL query to make sure it is formatted correctly for the SQL dialect:
{sql_dialect}

DO not change any table or column names in the query. However, you may qualify column names with table names.
Do not change any literals in the query.
You may *only* rewrite the query so that it is formatted correctly for the specified SQL dialect.
Do not return any other information other than the corrected SQL query.

Corrected SQL query:
"""

```


---

## 文件: data-science\data_science\sub_agents\bigquery\chase_sql\sql_postprocessor\sql_translator.py

```python
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

"""Translator from SQLite to BigQuery."""

import os
import re
from typing import Any, Final

import regex
import sqlglot
import sqlglot.optimizer

from ..llm_utils import GeminiModel  # pylint: disable=g-importing-member
from .correction_prompt_template import CORRECTION_PROMPT_TEMPLATE_V1_0  # pylint: disable=g-importing-member


ColumnSchemaType = tuple[str, str]
AllColumnsSchemaType = list[ColumnSchemaType]
TableSchemaType = tuple[str, AllColumnsSchemaType]
DDLSchemaType = list[TableSchemaType]

SQLGlotColumnsDictType = dict[str, str]
SQLGlotSchemaType = dict[str, Any]

BirdSampleType = dict[str, Any]


def _isinstance_list_of_str_tuples_lists(obj: Any) -> bool:
  """Checks if the object is a list of tuples or listsof strings."""
  return (
      isinstance(obj, list)
      and all([isinstance(v, (tuple, list)) for v in obj])
      and all([isinstance(v[0], str) and isinstance(v[1], str) for v in obj])
  )


def _isinstance_ddl_schema_type(obj: Any) -> bool:
  """Checks if the object is a DDL schema type."""
  # pylint: disable=g-complex-comprehension
  return (
      isinstance(obj, list)
      and all(
          # Every element is a tuple or list.
          [isinstance(v, (tuple, list)) for v in obj]
      )
      and all(
          # First element is a string (table name) and
          # second element is a list (of tuples or lists).
          [isinstance(v[0], str) and isinstance(v[1], list) for v in obj]
      )
      and all(
          # Every element of above list is a tuple or list of strings
          # (column name, column type)
          [_isinstance_list_of_str_tuples_lists(v[1]) for v in obj]
      )
  )
  # pylint: enable=g-complex-comprehension


def _isinstance_sqlglot_schema_type(obj: Any) -> bool:
  """Checks if the object is a SQLGlot schema type."""
  # pylint: disable=g-complex-comprehension
  return (
      isinstance(obj, dict)
      and all([isinstance(v, dict) for v in obj.values()])
      and all([isinstance(c, str) for d in obj.values() for c, _ in d.items()])
      and all([isinstance(t, str) for d in obj.values() for _, t in d.items()])
  )
  # pylint: enable=g-complex-comprehension


def _isinstance_bird_sample_type(obj: Any) -> bool:
  """Checks if the object is a SQLGlot schema type."""
  return isinstance(obj, dict) and not _isinstance_sqlglot_schema_type(obj)


class SqlTranslator:
  """Translator from SQLite to BigQuery.

  This class is used to translate SQL queries from an input SQL dialect like
  SQLite to an output SQL dialect like BigQuery. It uses the SQLGlot library as
  a tool to perform the translation.

  The translation is done by the following steps:
  1. (Optional) If there are errors in the input SQL query, the input SQL query
     is first modified by the LLM to address the errors.
  2. The input SQL query is then translated to a SQL query in the output SQL
     dialect by the tool.
  3. (Optional) If there are errors in the tool output SQL query, the tool
     output SQL query is modified by the LLM to address the errors.

  Class Attributes:
    INPUT_DIALECT: The input SQL dialect.
    OUTPUT_DIALECT: The output SQL dialect.

  Attributes:
    sql_query: The SQL query to translate.
    model: The model object, or the name of the model to use for the LLM.
    temperature: The temperature to use for the LLM.
    process_input_errors: True if any errors in the input SQL query should be
      processed by the LLM.
    process_tool_output_errors: True if any errors in the tool output SQL query
      should be processed by the LLM.
  """

  INPUT_DIALECT: Final[str] = "sqlite"
  OUTPUT_DIALECT: Final[str] = "bigquery"

  def __init__(
      self,
      model: str | GeminiModel = "gemini-1.5-flash-002",
      temperature: float = 0.5,
      process_input_errors: bool = False,
      process_tool_output_errors: bool = False,
  ):
    """Initializes the translator."""
    self._process_input_errors: bool = process_input_errors
    self._process_tool_output_errors: bool = process_tool_output_errors
    self._input_errors: str | None = None
    self._tool_output_errors: str | None = None
    self._temperature: float = temperature
    if isinstance(model, str):
      self._model = GeminiModel(model_name=model, temperature=self._temperature)
    else:
      self._model = model

  @classmethod
  def _parse_response(cls, text: str) -> str | None:
    """Extracts the SQL query from the response text."""
    pattern = r"```sql(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
      return match.group(1).strip()
    return None

  @classmethod
  def _apply_heuristics(cls, sql_query: str) -> str:
    """Applies heuristics to the SQL query."""
    if "''" in sql_query:
      sql_query = sql_query.replace("''", "\\'")
    return sql_query

  @classmethod
  def _extract_schema_from_ddl_statement(
      cls, ddl_statement: str
  ) -> TableSchemaType:
    """Extracts the schema from a single DDL statement."""
    # Split the DDL statement into table name and columns.
    # Match the following pattern:
    # CREATE [OR REPLACE] TABLE [`]<table_name>[`] (<all_columns>);
    splitter_pattern = (
        # CREATE [OR REPLACE] TABLE
        r"^\s*CREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+"
        # Match the table name, optionally surrounded by backticks.
        r"(?:`)?(?P<table_name>[\w\d\-\_\.]+)(?:`)?\s*"
        # Match the column name as everything between the first and last
        # parentheses followed by a semicolon.
        r"\((?P<all_columns>.*)\);$"
    )
    split_match = regex.search(
        splitter_pattern,
        ddl_statement,
        flags=re.DOTALL | re.VERBOSE | re.MULTILINE,
    )
    if not split_match:
      return None, None

    table_name = split_match.group("table_name")
    all_columns = split_match.group("all_columns").strip()
    if not table_name or not all_columns:
      return None, None

    # Extract the columns from the DDL statement.
    # Match the following pattern:
    # <column_name> <column_type> [<ignored_text>]
    # [, <column_name> <column_type> [<ignored_text>]]*
    # Ignore any comments. Ignore any INSERT INTO statements. Ignore any
    # lines beginning with a parenthesis (these are example values).
    column_pattern = (
        # Ignore any comments.
        r"\s*--.*(*SKIP)(*FAIL)"
        # Ignore any INSERT INTO statements.
        r"|\s*INSERT\s+INTO.*(*SKIP)(*FAIL)"
        # Ignore any lines beginning with a parenthesis.
        r"|\s*\(.*(*SKIP)(*FAIL)"
        # Match the column name and type, optionally with backticks.
        r"|\s*(?:`)?\s*(?P<column_name>\w+)(?:`)?\s+(?P<column_type>\w+).*"
    )  # (?:,)?
    columns = regex.findall(column_pattern, all_columns, flags=re.VERBOSE)
    return table_name, columns

  @classmethod
  def extract_schema_from_ddls(cls, ddls: str) -> DDLSchemaType:
    """Extracts the schema from multiple DDL statements."""
    ddl_statements = ddls.split(";\n")
    ddl_statements = [ddl.strip() for ddl in ddl_statements if ddl.strip()]
    schema = []
    for ddl_statement in ddl_statements:
      if ddl_statement:
        ddl_statement = ddl_statement.strip() + ";"  # Add the semicolon back.
        table_name, columns = cls._extract_schema_from_ddl_statement(
            ddl_statement
        )
        if table_name and columns:
          schema.append((table_name, columns))
    return schema

  @classmethod
  def _get_schema_from_bird_sample(
      cls, sample: BirdSampleType
  ) -> dict[str, dict[str, str]]:
    """Returns the schema from the Bird dataset example."""
    col_types_map: dict[str, str] = {
        "text": "TEXT",
        "number": "FLOAT",
        "date": "DATE",
        "datetime": "DATETIME",
        "time": "TIME",
        "timestamp": "TIMESTAMP",
        "bool": "BOOL",
    }
    tables = sample["db_table_names"]
    table_ids = sample["db_column_names"]["table_id"][1:]
    column_names = sample["db_column_names"]["column_name"][1:]
    column_types = sample["db_column_types"][1:]
    column_types = [col_types_map[col_type] for col_type in column_types]
    assert len(column_names) == len(column_types)
    cols_and_types: list[tuple[str, str]] = list(
        zip(column_names, column_types)
    )
    tables_to_columns: dict[str, dict[str, str]] = {}
    for id_pos, table_id in enumerate(table_ids):
      if tables[table_id] in tables_to_columns.keys():
        tables_to_columns[tables[table_id]].update(
            dict([cols_and_types[id_pos]])
        )
      else:
        tables_to_columns[tables[table_id]] = dict([cols_and_types[id_pos]])
    return tables_to_columns

  @classmethod
  def _get_table_parts(
      cls, table_name: str
  ) -> tuple[str | None, str | None, str]:
    """Returns the table parts from the table name."""
    table_parts = table_name.split(".")
    if len(table_parts) == 3:
      return table_parts
    elif len(table_parts) == 2:
      return None, *table_parts
    elif len(table_parts) == 1:
      return None, None, *table_parts
    else:
      raise ValueError(f"Invalid table name: {table_name}")

  @classmethod
  def format_schema(cls, schema: DDLSchemaType) -> SQLGlotSchemaType:
    """Formats the DDL schema for use in SQLGlot."""
    schema_dict = {}
    catalog, db = None, None
    for table_name, columns in schema:
      catalog, db, table_name = cls._get_table_parts(table_name)
      schema_dict[table_name] = {}
      for column_name, column_type in columns:
        schema_dict[table_name][column_name] = column_type
    if db:
      schema_dict = {db: schema_dict}
    if catalog:
      schema_dict = {catalog: schema_dict}
    return schema_dict

  @classmethod
  def rewrite_schema_for_sqlglot(
      cls, schema: str | SQLGlotSchemaType | BirdSampleType
  ) -> SQLGlotSchemaType:
    """Rewrites the schema for use in SQLGlot."""
    schema_dict = None
    if schema:
      if isinstance(schema, str):
        schema = cls.extract_schema_from_ddls(schema)
        schema_dict = cls.format_schema(schema)
      elif _isinstance_sqlglot_schema_type(schema):
        schema_dict = schema
      elif _isinstance_bird_sample_type(schema):
        schema_dict = cls._get_schema_from_bird_sample(schema)
      elif _isinstance_ddl_schema_type(schema):
        schema_dict = cls.format_schema(schema)
      else:
        raise TypeError(f"Unsupported schema type: {type(schema)}")
    return schema_dict

  @classmethod
  def _check_for_errors(
      cls,
      sql_query: str,
      sql_dialect: str,
      db: str | None = None,
      catalog: str | None = None,
      schema_dict: SQLGlotSchemaType | None = None,
  ) -> tuple[str | None, str]:
    """Checks for errors in the SQL query.

    Args:
      sql_query: The SQL query to check for errors.
      sql_dialect: The SQL dialect of the SQL query.
      db: The database to use for the translation. This field is optional.
      catalog: The catalog to use for the translation. `catalog` is the SQLGlot
        term for the project ID. This field is optional.
      schema_dict: The DDL schema to use for the translation. The DDL format is
        in the SQLGlot format. This field is optional.

    Returns:
      tuple of the errors in the SQL query, or None if there are no errors, and
      the SQL query after optimization.
    """
    try:
      # First, try to parse the SQL query into a SQLGlot AST.
      sql_query_ast = sqlglot.parse_one(
          sql=sql_query,
          read=sql_dialect.lower(),
          error_level=sqlglot.ErrorLevel.IMMEDIATE,
      )
      # Then add the database and catalog information for each table to the AST.
      for table in sql_query_ast.find_all(sqlglot.exp.Table):
        table.set("catalog", sqlglot.exp.Identifier(this=catalog, quoted=True))
        table.set("db", sqlglot.exp.Identifier(this=db, quoted=True))
      # Then, try to optimize the SQL query.
      sql_query_ast = sqlglot.optimizer.optimize(
          sql_query_ast,
          dialect=sql_dialect.lower(),
          schema=schema_dict,
          db=db,
          catalog=catalog,
          error_level=sqlglot.ErrorLevel.IMMEDIATE,
      )
      sql_query = sql_query_ast.sql(sql_dialect.lower())
    except sqlglot.errors.SqlglotError as e:
      return str(e), sql_query
    return None, sql_query

  def _fix_errors(
      self,
      sql_query: str,
      sql_dialect: str,
      apply_heuristics: bool,
      db: str | None = None,
      catalog: str | None = None,
      ddl_schema: str | SQLGlotSchemaType | BirdSampleType | None = None,
      number_of_candidates: int = 1,
  ) -> str:
    """Fixes errors in the SQL query.

    Args:
      sql_query: The SQL query to fix.
      sql_dialect: The input SQL dialect.
      apply_heuristics: True if the heuristics should be applied.
      db: The database to use for the translation. This field is optional.
      catalog: The catalog to use for the translation. `catalog` is the SQLGlot
        term for the project ID. This field is optional.
      ddl_schema: The DDL schema to use for the translation. The DDL format can
        be the SQLGlot format, the DDL schema format, a Bird dataset example, or
        a string containing multiple DDL statements. This field is optional.
      number_of_candidates: The number of candidates to generate, default is 1.

    Returns:
      str: The fixed SQL query.
    """
    if apply_heuristics:
      sql_query = self._apply_heuristics(sql_query)
    # Reformat the schema if provided. This will remove any comments and
    # `INSERT INTO` statements.
    schema_dict = self.rewrite_schema_for_sqlglot(ddl_schema)
    errors_and_sql: tuple[str | None, str] = self._check_for_errors(
        sql_query=sql_query,
        sql_dialect=self.OUTPUT_DIALECT,
        db=db,
        catalog=catalog,
        schema_dict=schema_dict,
    )
    errors, sql_query = errors_and_sql
    responses = sql_query  # Default to the input SQL query after error check.
    if errors:
      print("Processing input errors")
      if schema_dict:
        # If the schema is provided, then insert it into the prompt.
        schema_insert = f"\nThe database schema is:\n{schema_dict}\n"
      else:
        schema_insert = "\n"
      prompt: str = CORRECTION_PROMPT_TEMPLATE_V1_0.format(
          sql_dialect=sql_dialect.lower(),
          errors=errors,
          sql_query=sql_query,
          schema_insert=schema_insert,
      )
      requests: list[str] = [prompt for _ in range(number_of_candidates)]
      responses: list[str] = self._model.call_parallel(
          requests, parser_func=self._parse_response
      )
      if responses:
        # We only use the first response. Therefore the `number_of_candidates`
        # parameter is not used.
        # pylint: disable=g-bad-todo
        # pylint: enable=g-bad-todo
        # First, find the first non-None response.
        responses = [r for r in responses if r is not None]
        if responses:
          # Then, return the first non-None response.
          responses = responses[0]
    return responses

  def translate(
      self,
      sql_query: str,
      db: str | None = None,
      catalog: str | None = None,
      ddl_schema: str | SQLGlotSchemaType | BirdSampleType | None = None,
  ) -> str:
    """Translates the SQL query to the output SQL dialect.

    Args:
      sql_query: The SQL query to translate.
      db: The database to use for the translation. This field is optional.
      catalog: The catalog to use for the translation. `catalog` is the SQLGlot
        term for the project ID. This field is optional.
      ddl_schema: The DDL schema to use for the translation. The DDL format can
        be the SQLGlot format or the DDL schema format. This field is optional.

    Returns:
      The translated SQL query.
    """
    print("****** sql_query at translator entry:", sql_query)
    if self._process_input_errors:
      sql_query = self._fix_errors(
          sql_query,
          db=db,
          catalog=catalog,
          sql_dialect=self.OUTPUT_DIALECT,
          ddl_schema=ddl_schema,
          apply_heuristics=True,
      )
    print("****** sql_query after fix_errors:", sql_query)
    sql_query = sqlglot.transpile(
        sql=sql_query,
        read=self.INPUT_DIALECT,
        write=self.OUTPUT_DIALECT,
        error_level=sqlglot.ErrorLevel.IMMEDIATE,
    )[
        0
    ]  # Transpile returns a list of strings.
    print("****** sql_query after transpile:", sql_query)
    if self._tool_output_errors:
      sql_query = self._fix_errors(
          sql_query,
          db=db,
          catalog=catalog,
          sql_dialect=self.OUTPUT_DIALECT,
          ddl_schema=ddl_schema,
          apply_heuristics=True,
      )

    sql_query = sql_query.strip().replace('"', "`")
    sql_query = self._apply_heuristics(sql_query)

    return sql_query

```


---

## 文件: data-science\data_science\sub_agents\bqml\agent.py

```python
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

"""Data Science Agent V2: generate nl2py and use code interpreter to run the code."""

from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.callback_context import CallbackContext


from data_science.sub_agents.bqml.tools import (
    check_bq_models,
    execute_bqml_code,
    rag_response,
)
from .prompts import return_instructions_bqml


from data_science.sub_agents.bigquery.agent import database_agent as bq_db_agent
from data_science.sub_agents.bigquery.tools import (
    get_database_settings as get_bq_database_settings,
)


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent."""

    # setting up database settings in session.state
    if "database_settings" not in callback_context.state:
        db_settings = dict()
        db_settings["use_database"] = "BigQuery"
        callback_context.state["all_db_settings"] = db_settings

    # setting up schema in instruction
    if callback_context.state["all_db_settings"]["use_database"] == "BigQuery":
        callback_context.state["database_settings"] = get_bq_database_settings()
        schema = callback_context.state["database_settings"]["bq_ddl_schema"]

        callback_context._invocation_context.agent.instruction = (
            return_instructions_bqml()
            + f"""

   </BQML Reference for this query>
    
    <The BigQuery schema of the relevant data with a few sample rows>
    {schema}
    </The BigQuery schema of the relevant data with a few sample rows>
    """
        )


async def call_db_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call database (nl2sql) agent."""
    print(
        "\n call_db_agent.use_database:"
        f' {tool_context.state["all_db_settings"]["use_database"]}'
    )
    database_agent = (
        bq_db_agent
        if tool_context.state["all_db_settings"]["use_database"] == "BigQuery"
        # else pg_db_agent
        else None
    )
    agent_tool = AgentTool(agent=database_agent)
    db_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["db_agent_output"] = db_agent_output
    return db_agent_output


root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="bq_ml_agent",
    instruction=return_instructions_bqml(),
    before_agent_callback=setup_before_agent_call,
    tools=[execute_bqml_code, check_bq_models, call_db_agent, rag_response],
)

```


---

## 文件: data-science\data_science\sub_agents\bqml\prompts.py

```python
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

"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the bqml_agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""


def return_instructions_bqml() -> str:

    instruction_prompt_bqml_v2 = """
    <CONTEXT>
        <TASK>
            You are a BigQuery ML (BQML) expert agent. Your primary role is to assist users with BQML tasks, including model creation, training, and inspection. You also support data exploration using SQL.

            **Workflow:**

            1.  **Initial Information Retrieval:** ALWAYS start by using the `rag_response` tool to query the BQML Reference Guide. Use a precise query to retrieve relevant information. This information can help you answer user questions and guide your actions.
            2.  **Check for Existing Models:** If the user asks about existing BQML models, immediately use the `check_bq_models` tool. Use the `dataset_id` provided in the session context for this.
            3.  **BQML Code Generation and Execution:** If the user requests a task requiring BQML syntax (e.g., creating a model, training a model), follow these steps:
                a.  Query the BQML Reference Guide using the `rag_response` tool.
                b.  Generate the complete BQML code.
                c.  **CRITICAL:** Before executing, present the generated BQML code to the user for verification and approval.
                d.  Populate the BQML code with the correct `dataset_id` and `project_id` from the session context.
                e.  If the user approves, execute the BQML code using the `execute_bqml_code` tool. If the user requests changes, revise the code and repeat steps b-d.
                f. **Inform the user:** Before executing the BQML code, inform the user that some BQML operations, especially model training, can take a significant amount of time to complete, potentially several minutes or even hours.
            4.  **Data Exploration:** If the user asks for data exploration or analysis, use the `call_db_agent` tool to execute SQL queries against BigQuery.

            **Tool Usage:**

            *   `rag_response`: Use this tool to get information from the BQML Reference Guide. Formulate your query carefully to get the most relevant results.
            *   `check_bq_models`: Use this tool to list existing BQML models in the specified dataset.
            *   `execute_bqml_code`: Use this tool to run BQML code. **Only use this tool AFTER the user has approved the code.**
            *   `call_db_agent`: Use this tool to execute SQL queries for data exploration and analysis.

            **IMPORTANT:**

            *   **User Verification is Mandatory:** NEVER use `execute_bqml_code` without explicit user approval of the generated BQML code.
            *   **Context Awareness:** Always use the `dataset_id` and `project_id` provided in the session context. Do not hardcode these values.
            *   **Efficiency:** Be mindful of token limits. Write efficient BQML code.
            *   **No Parent Agent Routing:** Do not route back to the parent agent unless the user explicitly requests it.
            *   **Prioritize `rag_response`:** Always use `rag_response` first to gather information.
            *   **Long Run Times:** Be aware that certain BQML operations, such as model training, can take a significant amount of time to complete. Inform the user about this possibility before executing such operations.
            * **No "process is running"**: Never use the phrase "process is running" or similar, as your response indicates that the process has finished.

        </TASK>
    </CONTEXT>
    """

    instruction_prompt_bqml_v1 = """
     <CONTEXT>
        <TASK>
            You are an agent that supports with BigQuery ML Workloads.
            **Workflow**
            0. Always fetch information from the BQML Reference Guide first using the `rag_response` tool. For this, make sure you are using a proper query to retrieve relevant information. (You can use this to answer questions,too)
            1. If the user asks for a existing models, call the `check_bq_models` tool. Use the dataset_ID from the session context.
            2. If the user asks for a task that needs BQ ML syntax:
                2a. Generate the BQML and the code, populate the correct dataset ID and project ID from the session context. The user needs to validate and approve before you continue.
                2b. If the user confirms, run the `execute_bqml_code` tool with the BQ ML you created, or correct your plan if necessary.
            **Execute BQ Tool (`execute_bqml_code` - if applicable):** With the response from 2, properly formulate the returned BQ ML Code, add the dataset and project IDs stored in context, and run the execute_bqml_code tool.
            **Check BQ ML Models Tool (`check_bq_models` - if applicable):** If the user asks for existing models in BQ ML, use this tool to check for it. Provide the dataset ID you have access to from the session context.
            Below you will find documentation and examples of BigQuery ML.
            3. If the user asks for data exploration, use the tool `call_db_agent`.

        </TASK>
        
        Do the following:
        - You can use the `rag_response` tool to retrieve information from the BQML Reference Guide.  
        - If the user asks for existing bqml models, run the `check_bq_models` tool.
        - If the user asks for a task that needs BQ ML syntax, generate the BQML and return it for the user to verify. If verified, run the `execute_bqml_code` tool.
        - If you need to execute SQL against BigQuery, e.g. for data understanding, use the tool `call_db_agent`. 
        - If the user asks for data exploration, use the tool `call_db_agent`.

        **IMPORTANT:**
        * Only run the execute_bqml_code tool once the user verified the code. NEVER USE `execute_bqml_code` BEFORE VERIFYING WITH THE USER!!
        * Make sure you use the database and project ID that is provided to you in the context!!
        * Be efficient. You have a output token limit, so make sure your BQML Code is efficient enough to stay in that limit.
        * Note: never route back to the parent agent, except when the user explicitly prompts for it. 


    </CONTEXT>

  """

    instruction_prompt_bqml_v0 = """
    <TASK>
        You are an agent that supports with BigQuery ML Workloads.
        **Workflow**
        1. If the user asks for a existing models, call the `check_bq_models` tool.
        2. If the user asks for a task that needs BQ ML syntax, generate the BQML, then **Execute BQ Tool (`execute_bqml_code` - if applicable):** With the response from 2, properly formulate the returned BQ ML Code, add the dataset and project IDs stored in context, and run the execute_bqml_code tool.
        **Check BQ ML Models Tool (`check_bq_models` - if applicable):** If the user asks for existing models in BQ ML, use this tool to check for it. Provide the dataset ID you have access to from the session context.
        Below you will find documentation and examples of BigQuery ML.
        </TASK>
        Do the following:
        - If the user asks for existing bqml models, run the `check_bq_models` tool.
        - If the user asks for a task that needs BQ ML syntax, generate the BQML and run the `execute_bqml_code` tool.


        <EXAMPLE: CREATE LOGISTIC REGRESSION>
        **BQ ML SYNTAX:**

        CREATE OR REPLACE MODEL `your_project_id.your_dataset_id.sample_model`
        OPTIONS(model_type='logistic_reg') AS
        SELECT
        IF(totals.transactions IS NULL, 0, 1) AS label,
        IFNULL(device.operatingSystem, "") AS os,
        device.isMobile AS is_mobile,
        IFNULL(geoNetwork.country, "") AS country,
        IFNULL(totals.pageviews, 0) AS pageviews
        FROM
        `your_project_id.your_dataset_id.ga_sessions_*`
        WHERE
        _TABLE_SUFFIX BETWEEN '20160801' AND '20170630'


        **QUERY DETAILS**

        The CREATE MODEL statement creates the model and then trains the model using the data retrieved by your query's SELECT statement.

        The OPTIONS(model_type='logistic_reg') clause creates a logistic regression model. A logistic regression model splits input data into two classes, and then estimates the probability that the data is in one of the classes. What you are trying to detect, such as whether an email is spam, is represented by 1 and other values are represented by 0. The likelihood of a given value belonging to the class you are trying to detect is indicated by a value between 0 and 1. For example, if an email receives a probability estimate of 0.9, then there is a 90% probability that the email is spam.

        This query's SELECT statement retrieves the following columns that are used by the model to predict the probability that a customer will complete a transaction:

        totals.transactions: the total number of ecommerce transactions within the session. If the number of transactions is NULL, the value in the label column is set to 0. Otherwise, it is set to 1. These values represent the possible outcomes. Creating an alias named label is an alternative to setting the input_label_cols= option in the CREATE MODEL statement.
        device.operatingSystem: the operating system of the visitor's device.
        device.isMobile — Indicates whether the visitor's device is a mobile device.
        geoNetwork.country: the country from which the sessions originated, based on the IP address.
        totals.pageviews: the total number of page views within the session.
        The FROM clause — causes the query to train the model by using the bigquery-public-data.google_analytics_sample.ga_sessions sample tables. These tables are sharded by date, so you aggregate them by using a wildcard in the table name: google_analytics_sample.ga_sessions_*.

        The WHERE clause — _TABLE_SUFFIX BETWEEN '20160801' AND '20170630' — limits the number of tables scanned by the query. The date range scanned is August 1, 2016 to June 30, 2017.

        </EXAMPLE: CREATE LOGISTIC REGRESSION>


        <EXAMPLE: RETRIEVE TRAINING INFO>
        SELECT
        iteration,
        loss,
        eval_metric
        FROM
            ML.TRAINING_INFO(MODEL `my_dataset.my_model`)
        ORDER BY
        iteration;
        </EXAMPLE: RETRIEVE TRAINING INFO>"""

    return instruction_prompt_bqml_v2

```


---

## 文件: data-science\data_science\sub_agents\bqml\tools.py

```python
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

import time
import os
from google.cloud import bigquery
from vertexai import rag


def check_bq_models(dataset_id: str) -> str:
    """Lists models in a BigQuery dataset and returns them as a string.

    Args:
        dataset_id: The ID of the BigQuery dataset (e.g., "project.dataset").

    Returns:
        A string representation of a list of dictionaries, where each dictionary
        contains the 'name' and 'type' of a model in the specified dataset.
        Returns an empty string "[]" if no models are found.
    """

    try:
        client = bigquery.Client()

        models = client.list_models(dataset_id)
        model_list = []  # Initialize as a list

        print(f"Models contained in '{dataset_id}':")
        for model in models:
            model_id = model.model_id
            model_type = model.model_type
            model_list.append({"name": model_id, "type": model_type})

        return str(model_list)

    except Exception as e:
        return f"An error occurred: {str(e)}"


def execute_bqml_code(bqml_code: str, project_id: str, dataset_id: str) -> str:
    """
    Executes BigQuery ML code.
    """

    # timeout_seconds = 1500

    client = bigquery.Client(project=project_id)

    try:
        query_job = client.query(bqml_code)
        start_time = time.time()

        while not query_job.done():
            elapsed_time = time.time() - start_time
            # if elapsed_time > timeout_seconds:
            #     return (
            #         "Timeout: BigQuery job did not complete within"
            #         f" {timeout_seconds} seconds. Job ID: {query_job.job_id}"
            #     )

            print(
                f"Query Job Status: {query_job.state}, Elapsed Time:"
                f" {elapsed_time:.2f} seconds. Job ID: {query_job.job_id}"
            )
            time.sleep(5)

        if query_job.error_result:
            return f"Error executing BigQuery ML code: {query_job.error_result}"

        if query_job.exception():
            return f"Exception during BigQuery ML execution: {query_job.exception()}"

        results = query_job.result()
        if results.total_rows > 0:
            result_string = ""
            for row in results:
                result_string += str(dict(row.items())) + "\n"
            return f"BigQuery ML code executed successfully. Results:\n{result_string}"
        else:
            return "BigQuery ML code executed successfully."

    except Exception as e:
        return f"An error occurred: {str(e)}"


def rag_response(query: str) -> str:
    """Retrieves contextually relevant information from a RAG corpus.

    Args:
        query (str): The query string to search within the corpus.

    Returns:
        vertexai.rag.RagRetrievalQueryResponse: The response containing retrieved
        information from the corpus.
    """
    corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

    rag_retrieval_config = rag.RagRetrievalConfig(
        top_k=3,  # Optional
        filter=rag.Filter(vector_distance_threshold=0.5),  # Optional
    )
    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(
                rag_corpus=corpus_name,
            )
        ],
        text=query,
        rag_retrieval_config=rag_retrieval_config,
    )
    return str(response)

```


---

## 文件: data-science\data_science\utils\create_bq_table.py

```python
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


import os
import pandas as pd
from google.cloud import bigquery
from pathlib import Path
from dotenv import load_dotenv

# Define the path to the .env file
env_file_path = Path(__file__).parent.parent.parent / ".env"
print(env_file_path)

# Load environment variables from the specified .env file
load_dotenv(dotenv_path=env_file_path)


def load_csv_to_bigquery(project_id, dataset_name, table_name, csv_filepath):
    """Loads a CSV file into a BigQuery table.

    Args:
        project_id: The ID of the Google Cloud project.
        dataset_name: The name of the BigQuery dataset.
        table_name: The name of the BigQuery table.
        csv_filepath: The path to the CSV file.
    """

    client = bigquery.Client(project=project_id)

    dataset_ref = client.dataset(dataset_name)
    table_ref = dataset_ref.table(table_name)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,  # Skip the header row
        autodetect=True,  # Automatically detect the schema
    )

    with open(csv_filepath, "rb") as source_file:
        job = client.load_table_from_file(
            source_file, table_ref, job_config=job_config
        )

    job.result()  # Wait for the job to complete

    print(f"Loaded {job.output_rows} rows into {dataset_name}.{table_name}")


def create_dataset_if_not_exists(project_id, dataset_name):
    """Creates a BigQuery dataset if it does not already exist.

    Args:
        project_id: The ID of the Google Cloud project.
        dataset_name: The name of the BigQuery dataset.
    """
    client = bigquery.Client(project=project_id)
    dataset_id = f"{project_id}.{dataset_name}"

    try:
        client.get_dataset(dataset_id)  # Make an API request.
        print(f"Dataset {dataset_id} already exists")
    except Exception as e:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"  # Set the location (e.g., "US", "EU")
        dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
        print(f"Created dataset {dataset_id}")


def main():

    current_directory = os.getcwd()
    print(f"Current working directory: {current_directory}")

    """Main function to load CSV files into BigQuery."""
    project_id = os.getenv("BQ_PROJECT_ID")
    if not project_id:
        raise ValueError("BQ_PROJECT_ID environment variable not set.")

    dataset_name = "forecasting_sticker_sales"
    train_csv_filepath = "data_science/utils/data/train.csv"
    test_csv_filepath = "data_science/utils/data/test.csv"

    # Create the dataset if it doesn't exist
    print("Creating dataset.")
    create_dataset_if_not_exists(project_id, dataset_name)

    # Load the train data
    print("Loading train table.")
    load_csv_to_bigquery(project_id, dataset_name, "train", train_csv_filepath)

    # Load the test data
    print("Loading test table.")
    load_csv_to_bigquery(project_id, dataset_name, "test", test_csv_filepath)


if __name__ == "__main__":
    main()

```


---

## 文件: data-science\data_science\utils\reference_guide_RAG.py

```python
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

import os
from pathlib import Path
from dotenv import load_dotenv, set_key
import vertexai
from vertexai import rag


# Define the path to the .env file
env_file_path = Path(__file__).parent.parent.parent / ".env"
print(env_file_path)

# Load environment variables from the specified .env file
load_dotenv(dotenv_path=env_file_path)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

display_name = "bqml_referenceguide_corpus"

paths = [
    "gs://cloud-samples-data/adk-samples/data-science/bqml"
]  # Supports Google Cloud Storage and Google Drive Links


# Initialize Vertex AI API once per session
vertexai.init(project=PROJECT_ID, location="us-central1")


def create_RAG_corpus():
    # Create RagCorpus
    # Configure embedding model, for example "text-embedding-005".
    embedding_model_config = rag.RagEmbeddingModelConfig(
        vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
            publisher_model="publishers/google/models/text-embedding-005"
        )
    )

    backend_config = rag.RagVectorDbConfig(
        rag_embedding_model_config=embedding_model_config
    )

    bqml_corpus = rag.create_corpus(
        display_name=display_name,
        backend_config=backend_config,
    )

    write_to_env(bqml_corpus.name)

    return bqml_corpus.name


def ingest_files(corpus_name):

    transformation_config = rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(
            chunk_size=512,
            chunk_overlap=100,
        ),
    )

    rag.import_files(
        corpus_name,
        paths,
        transformation_config=transformation_config,  # Optional
        max_embedding_requests_per_min=1000,  # Optional
    )

    # List the files in the rag corpus
    rag.list_files(corpus_name)


def rag_response(query: str) -> str:
    """Retrieves contextually relevant information from a RAG corpus.

    Args:
        query (str): The query string to search within the corpus.

    Returns:
        vertexai.rag.RagRetrievalQueryResponse: The response containing retrieved
        information from the corpus.
    """
    corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

    rag_retrieval_config = rag.RagRetrievalConfig(
        top_k=3,  # Optional
        filter=rag.Filter(vector_distance_threshold=0.5),  # Optional
    )
    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(
                rag_corpus=corpus_name,
            )
        ],
        text=query,
        rag_retrieval_config=rag_retrieval_config,
    )
    return str(response)


def write_to_env(corpus_name):
    """Writes the corpus name to the specified .env file.

    Args:
        corpus_name: The name of the corpus to write.
    """

    load_dotenv(env_file_path)  # Load existing variables if any

    # Set the key-value pair in the .env file
    set_key(env_file_path, "BQML_RAG_CORPUS_NAME", corpus_name)
    print(f"BQML_RAG_CORPUS_NAME '{corpus_name}' written to {env_file_path}")


if __name__ == "__main__":
    # rag_corpus = rag.list_corpora()

    corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

    print("Creating the corpus.")
    corpus_name = create_RAG_corpus()
    print(f"Corpus name: {corpus_name}")

    print(f"Importing files to corpus: {corpus_name}")
    ingest_files(corpus_name)
    print(f"Files imported to corpus: {corpus_name}")

```


---

## 文件: data-science\data_science\utils\utils.py

```python
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

import json
import os

from vertexai.preview.extensions import Extension


def list_all_extensions():
  extensions = Extension.list(location='us-central1')
  for extension in extensions:
    print('Name:', extension.gca_resource.name)
    print('Display Name:', extension.gca_resource.display_name)
    print('Description:', extension.gca_resource.description)


def get_env_var(var_name):
  """Retrieves the value of an environment variable.

  Args:
    var_name: The name of the environment variable.

  Returns:
    The value of the environment variable, or None if it is not set.

  Raises:
    ValueError: If the environment variable is not set.
  """
  try:
    value = os.environ[var_name]
    return value
  except KeyError:
    raise ValueError(f'Missing environment variable: {var_name}')


def get_image_bytes(filepath):
  """Reads an image file and returns its bytes.

  Args:
    filepath: The path to the image file.

  Returns:
    The bytes of the image file, or None if the file does not exist or cannot be
    read.
  """
  try:
    with open(filepath, 'rb') as f:  # "rb" mode for reading in binary
      image_bytes = f.read()
    return image_bytes
  except FileNotFoundError:
    print(f'Error: File not found at {filepath}')
    return None
  except Exception as e:
    print(f'Error reading file: {e}')
    return None


def extract_json_from_model_output(model_output):
  """Extracts JSON object from a string that potentially contains markdown

  code fences.

  Args:
    model_output: A string potentially containing a JSON object wrapped in
      markdown code fences (```json ... ```).

  Returns:
    A Python dictionary representing the extracted JSON object,
    or None if JSON extraction fails.
  """
  try:
    cleaned_output = (
        model_output.replace('```json', '').replace('```', '').strip()
    )
    json_object = json.loads(cleaned_output)
    return json_object
  except json.JSONDecodeError as e:
    msg = f'Error decoding JSON: {e}'
    print(msg)
    return {'error': msg}


if __name__ == '__main__':
  list_all_extensions()

```


---

## 文件: data-science\deployment\deploy.py

```python
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

"""Deployment script for Data Science agent."""

import logging
import os

import vertexai
from absl import app, flags
from data_science.agent import root_agent
from dotenv import load_dotenv
from google.api_core import exceptions as google_exceptions
from google.cloud import storage
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string(
    "bucket", None, "GCP bucket name (without gs:// prefix)."
)  # Changed flag description
flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")

flags.DEFINE_bool("create", False, "Create a new agent.")
flags.DEFINE_bool("delete", False, "Delete an existing agent.")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])

AGENT_WHL_FILE = "data_science-0.1-py3-none-any.whl"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_staging_bucket(
    project_id: str, location: str, bucket_name: str
) -> str:
    """
    Checks if the staging bucket exists, creates it if not.

    Args:
        project_id: The GCP project ID.
        location: The GCP location for the bucket.
        bucket_name: The desired name for the bucket (without gs:// prefix).

    Returns:
        The full bucket path (gs://<bucket_name>).

    Raises:
        google_exceptions.GoogleCloudError: If bucket creation fails.
    """
    storage_client = storage.Client(project=project_id)
    try:
        # Check if the bucket exists
        bucket = storage_client.lookup_bucket(bucket_name)
        if bucket:
            logger.info("Staging bucket gs://%s already exists.", bucket_name)
        else:
            logger.info(
                "Staging bucket gs://%s not found. Creating...", bucket_name
            )
            # Create the bucket if it doesn't exist
            new_bucket = storage_client.create_bucket(
                bucket_name, project=project_id, location=location
            )
            logger.info(
                "Successfully created staging bucket gs://%s in %s.",
                new_bucket.name,
                location,
            )
            # Enable uniform bucket-level access for simplicity
            new_bucket.iam_configuration.uniform_bucket_level_access_enabled = (
                True
            )
            new_bucket.patch()
            logger.info(
                "Enabled uniform bucket-level access for gs://%s.",
                new_bucket.name,
            )

    except google_exceptions.Forbidden as e:
        logger.error(
            (
                "Permission denied error for bucket gs://%s. "
                "Ensure the service account has 'Storage Admin' role. Error: %s"
            ),
            bucket_name,
            e,
        )
        raise
    except google_exceptions.Conflict as e:
        logger.warning(
            (
                "Bucket gs://%s likely already exists but owned by another "
                "project or recently deleted. Error: %s"
            ),
            bucket_name,
            e,
        )
        # Assuming we can proceed if it exists, even with a conflict warning
    except google_exceptions.ClientError as e:
        logger.error(
            "Failed to create or access bucket gs://%s. Error: %s",
            bucket_name,
            e,
        )
        raise

    return f"gs://{bucket_name}"


def create(env_vars: dict[str, str]) -> None:
    """Creates and deploys the agent."""
    adk_app = AdkApp(
        agent=root_agent,
        enable_tracing=False,
        env_vars=env_vars
    )

    if not os.path.exists(AGENT_WHL_FILE):
        logger.error("Agent wheel file not found at: %s", AGENT_WHL_FILE)
        # Consider adding instructions here on how to build the wheel file
        raise FileNotFoundError(f"Agent wheel file not found: {AGENT_WHL_FILE}")

    logger.info("Using agent wheel file: %s", AGENT_WHL_FILE)

    remote_agent = agent_engines.create(
        adk_app,
        requirements=[AGENT_WHL_FILE],
        extra_packages=[AGENT_WHL_FILE],
    )
    logger.info("Created remote agent: %s", remote_agent.resource_name)
    print(f"\nSuccessfully created agent: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    """Deletes the specified agent."""
    logger.info("Attempting to delete agent: %s", resource_id)
    try:
        remote_agent = agent_engines.get(resource_id)
        remote_agent.delete(force=True)
        logger.info("Successfully deleted remote agent: %s", resource_id)
        print(f"\nSuccessfully deleted agent: {resource_id}")
    except google_exceptions.NotFound:
        logger.error("Agent with resource ID %s not found.", resource_id)
        print(f"\nAgent{resource_id} not found.")
        print(f"\nAgent not found: {resource_id}")
    except Exception as e:
        logger.error(
            "An error occurred while deleting agent %s: %s", resource_id, e
        )
        print(f"\nError deleting agent {resource_id}: {e}")


def main(argv: list[str]) -> None:  # pylint: disable=unused-argument
    """Main execution function."""
    load_dotenv()
    env_vars = {}

    project_id = (
        FLAGS.project_id
        if FLAGS.project_id
        else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = (
        FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    # Default bucket name convention if not provided
    default_bucket_name = f"{project_id}-adk-staging" if project_id else None
    bucket_name = (
        FLAGS.bucket
        if FLAGS.bucket
        else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET", default_bucket_name)
    )
    env_vars["GOOGLE_CLOUD_PROJECT"] = project_id
    env_vars["GOOGLE_CLOUD_LOCATION"] = location
    env_vars["BQ_DATASET_ID"] = os.getenv("BQ_DATASET_ID")
    env_vars["BQ_PROJECT_ID"] = os.getenv("BQ_PROJECT_ID")
    env_vars["BQML_RAG_CORPUS_NAME"] = os.getenv("BQML_RAG_CORPUS_NAME")
    env_vars["CODE_INTERPRETER_EXTENSION_NAME"] = os.getenv(
        "CODE_INTERPRETER_EXTENSION_NAME")


    logger.info("Using PROJECT: %s", project_id)
    logger.info("Using LOCATION: %s", location)
    logger.info("Using BUCKET NAME: %s", bucket_name)

    # --- Input Validation ---
    if not project_id:
        print("\nError: Missing required GCP Project ID.")
        print(
            "Set the GOOGLE_CLOUD_PROJECT environment variable or use --project_id flag."
        )
        return
    if not location:
        print("\nError: Missing required GCP Location.")
        print(
            "Set the GOOGLE_CLOUD_LOCATION environment variable or use --location flag."
        )
        return
    if not bucket_name:
        print("\nError: Missing required GCS Bucket Name.")
        print(
            "Set the GOOGLE_CLOUD_STORAGE_BUCKET environment variable or use --bucket flag."
        )
        return
    if not FLAGS.create and not FLAGS.delete:
        print("\nError: You must specify either --create or --delete flag.")
        return
    if FLAGS.delete and not FLAGS.resource_id:
        print(
            "\nError: --resource_id is required when using the --delete flag."
        )
        return
    # --- End Input Validation ---

    try:
        # Setup staging bucket
        staging_bucket_uri=None
        if FLAGS.create:
            staging_bucket_uri = setup_staging_bucket(
                project_id, location, bucket_name
            )

        # Initialize Vertex AI *after* bucket setup and validation
        vertexai.init(
            project=project_id,
            location=location,
            staging_bucket=staging_bucket_uri,  # Staging bucket is passed directly to create/update methods now
        )

        if FLAGS.create:
            create(env_vars)
        elif FLAGS.delete:
            delete(FLAGS.resource_id)

    except google_exceptions.Forbidden as e:
        print(
            "Permission Error: Ensure the service account/user has necessary "
            "permissions (e.g., Storage Admin, Vertex AI User)."
            f"\nDetails: {e}"
        )
    except FileNotFoundError as e:
        print(f"\nFile Error: {e}")
        print(
            "Please ensure the agent wheel file exists in the 'deployment' "
            "directory and you have run the build script "
            "(e.g., poetry build --format=wheel --output=deployment')."
        )
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        logger.exception(
            "Unhandled exception in main:"
        )  # Log the full traceback


if __name__ == "__main__":

    app.run(main)

```


---

## 文件: data-science\deployment\test_deployment.py

```python
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

"""Test deployment of Data Science Agent to Agent Engine."""

import os

import vertexai
from absl import app, flags
from dotenv import load_dotenv
from vertexai import agent_engines

FLAGS = flags.FLAGS

flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP bucket.")
flags.DEFINE_string(
    "resource_id",
    None,
    "ReasoningEngine resource ID (returned after deploying the agent)",
)
flags.DEFINE_string("user_id", None, "User ID (can be any string).")
flags.mark_flag_as_required("resource_id")
flags.mark_flag_as_required("user_id")


def main(argv: list[str]) -> None:  # pylint: disable=unused-argument

    load_dotenv()

    project_id = (
        FLAGS.project_id if FLAGS.project_id else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")

    default_bucket_name = f"{project_id}-adk-staging" if project_id else None
    bucket_name = (
        FLAGS.bucket
        if FLAGS.bucket
        else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET", default_bucket_name)
    )

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket_name:
        print("Missing required environment variable: GOOGLE_CLOUD_STORAGE_BUCKET")
        return

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket_name}",
    )

    agent = agent_engines.get(FLAGS.resource_id)
    print(f"Found agent with resource ID: {FLAGS.resource_id}")
    session = agent.create_session(user_id=FLAGS.user_id)
    print(f"Created session for user ID: {FLAGS.user_id}")
    print("Type 'quit' to exit.")
    while True:
        user_input = input("Input: ")
        if user_input == "quit":
            break

        for event in agent.stream_query(
            user_id=FLAGS.user_id, session_id=session["id"], message=user_input
        ):
            if "content" in event:
                if "parts" in event["content"]:
                    parts = event["content"]["parts"]
                    for part in parts:
                        if "text" in part:
                            text_part = part["text"]
                            print(f"Response: {text_part}")

    agent.delete_session(user_id=FLAGS.user_id, session_id=session["id"])
    print(f"Deleted session for user ID: {FLAGS.user_id}")


if __name__ == "__main__":
    app.run(main)

```


---

## 文件: data-science\eval\test_eval.py

```python
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

from google.adk.evaluation.agent_evaluator import AgentEvaluator

import os
import pytest
from dotenv import find_dotenv, load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv(find_dotenv(".env"))


def test_eval_simple():
    """Test the agent's basic ability via a session file."""
    AgentEvaluator.evaluate(
        "data_science",
        os.path.join(os.path.dirname(__file__), "eval_data/simple.test.json"),
        num_runs=1,
    )




```


---

## 文件: data-science\eval\eval_data\simple.test.json

```json
[
  {
    "query": "what data do you have?",
    "expected_tool_use": [],
    "expected_intermediate_agent_responses": [],
    "reference": "I have access to two tables: `train` and `test`. Both tables contain information about sticker sales, including the date, country, store, product, and number sold. The `train` table contains the historical sales data, while the `test` table contains more recent sales data.\n"
  },
  {
    "query": "what countries are in test?",
    "expected_tool_use": [
      {
        "tool_name": "call_db_agent",
        "tool_input": {
          "question": "What are the distinct countries in the test table?"
        }
      }
    ],
    "expected_intermediate_agent_responses": [],
    "reference": "**Result:** The distinct countries in the test table are Canada, Finland, Italy, Kenya, Norway, and Singapore.\n\n**Explanation:** I queried the `test` table to find all the distinct values in the `country` column. The query returned the list of countries: Canada, Finland, Italy, Kenya, Norway, and Singapore.\n"
  }
]

```


---

## 文件: data-science\eval\eval_data\test_config.json

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.1
  }
}

```


---

## 文件: data-science\tests\test_agents.py

```python
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

"""Test cases for the analytics agent and its sub-agents."""

import os
import sys
import pytest
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.genai import types
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from data_science.agent import root_agent
from data_science.sub_agents.bqml.agent import root_agent as bqml_agent
from data_science.sub_agents.bigquery.agent import database_agent
from data_science.sub_agents.analytics.agent import root_agent as data_science_agent

session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()


class TestAgents(unittest.TestCase):
    """Test cases for the analytics agent and its sub-agents."""

    def setUp(self):
        """Set up for test methods."""
        self.session = session_service.create_session(
            app_name="DataAgent",
            user_id="test_user",
        )
        self.user_id = "test_user"
        self.session_id = self.session.id

        self.runner = Runner(
            app_name="DataAgent",
            agent=None,
            artifact_service=artifact_service,
            session_service=session_service,
        )

    def _run_agent(self, agent, query):
        """Helper method to run an agent and get the final response."""
        self.runner.agent = agent
        content = types.Content(role="user", parts=[types.Part(text=query)])
        events = list(
            self.runner.run(
                user_id=self.user_id, session_id=self.session_id, new_message=content
            )
        )

        last_event = events[-1]
        final_response = "".join(
            [part.text for part in last_event.content.parts if part.text]
        )
        return final_response


    @pytest.mark.db_agent
    def test_db_agent_can_handle_env_query(self):
        """Test the db_agent with a query from environment variable."""
        query = "what countries exist in the train table?"
        response = self._run_agent(database_agent, query)
        print(response)
        # self.assertIn("Canada", response)
        self.assertIsNotNone(response)

    @pytest.mark.ds_agent
    def test_ds_agent_can_be_called_from_root(self):
        """Test the ds_agent from the root agent."""
        query = "plot the most selling category"
        response = self._run_agent(root_agent, query)
        print(response)
        self.assertIsNotNone(response)

    @pytest.mark.bqml
    def test_bqml_agent_can_check_for_models(self):
        """Test that the bqml_agent can check for existing models."""
        query = "Are there any existing models in the dataset?"
        response = self._run_agent(bqml_agent, query)
        print(response)
        self.assertIsNotNone(response)

    @pytest.mark.bqml
    def test_bqml_agent_can_execute_code(self):
        """Test that the bqml_agent can execute BQML code."""
        query = """
    I want to train a BigQuery ML model on the sales_train_validation data for sales prediction.
    Please show me an execution plan. 
    """
        response = self._run_agent(bqml_agent, query)
        print(response)
        self.assertIsNotNone(response)


if __name__ == "__main__":
    unittest.main()

    # testagent = TestAgents
    # testagent.setUp(testagent)
    # testagent.test_root_agent_can_list_tools(testagent)
    # testagent.test_db_agent_can_handle_env_query(testagent)

```


---

## 文件: fomc-research\deployment\bigquery_setup.py

```python
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

"""BigQuery table creation script."""

import csv
from collections.abc import Sequence

from absl import app, flags
from google.cloud import bigquery
from google.cloud.exceptions import Conflict, GoogleCloudError, NotFound

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("dataset_id", None, "BigQuery dataset ID.")
flags.DEFINE_string("data_file", None, "Path to the data file.")
flags.DEFINE_string("location", "us-central1", "Location for the dataset.")
flags.mark_flags_as_required(["project_id", "dataset_id"])


def create_bigquery_dataset(
    client: bigquery.Client,
    dataset_id: str,
    location: str,
    description: str = None,
    exists_ok: bool = True,
) -> bigquery.Dataset:
    """Creates a new BigQuery dataset.

    Args:
        client: A BigQuery client object.
        dataset_id: The ID of the dataset to create.
        location: The location for the dataset (e.g., "US", "EU").
            Defaults to "US".
        description: An optional description for the dataset.
        exists_ok: If True, do not raise an exception if the dataset already
            exists.

    Returns:
        The newly created bigquery.Dataset object.

    Raises:
        google.cloud.exceptions.Conflict: If the dataset already exists and
            exists_ok is False.
        Exception: for any other error.
    """

    dataset_ref = bigquery.DatasetReference(client.project, dataset_id)
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = location
    if description:
        dataset.description = description

    try:
        dataset = client.create_dataset(dataset)
        print(f"Dataset {dataset.dataset_id} created in {dataset.location}.")
        return dataset
    except Conflict as e:
        if exists_ok:
            print(f"Dataset {dataset.dataset_id} already exists.")
            return client.get_dataset(dataset_ref)
        else:
            raise e


def create_bigquery_table(
    client: bigquery.Client,
    dataset_id: str,
    table_id: str,
    schema: list[bigquery.SchemaField],
    description: str = None,
    exists_ok: bool = False,
) -> bigquery.Table:
    """Creates a new BigQuery table.

    Args:
        client: A BigQuery client object.
        dataset_id: The ID of the dataset containing the table.
        table_id: The ID of the table to create.
        schema: A list of bigquery.SchemaField objects defining the table
            schema.
        description: An optional description for the table.
        exists_ok: If True, do not raise an exception if the table already
            exists.

    Returns:
        The newly created bigquery.Table object.

    Raises:
        ValueError: If the schema is empty.
        google.cloud.exceptions.Conflict: If the table already exists and
            exists_ok is False.
        google.cloud.exceptions.NotFound: If the dataset does not exist.
        Exception: for any other error.
    """

    if not schema:
        raise ValueError("Schema cannot be empty.")

    table_ref = bigquery.TableReference(
        bigquery.DatasetReference(client.project, dataset_id), table_id
    )
    table = bigquery.Table(table_ref, schema=schema)

    if description:
        table.description = description

    try:
        table = client.create_table(table)
        print(
            f"Table {table.project}.{table.dataset_id}.{table.table_id} "
            "created."
        )
        return table
    except Exception as e:  # pylint: disable=broad-exception-caught
        if isinstance(e, NotFound):
            raise NotFound(
                f"Dataset {dataset_id} not found in project {client.project}"
            ) from e
        if "Already Exists" in str(e) and exists_ok:
            print(
                f"Table {table.project}.{table.dataset_id}.{table.table_id} "
                "already exists."
            )
            return client.get_table(table_ref)
        else:
            # pylint: disable=broad-exception-raised
            raise Exception(f"Error creating table: {e}") from e


def insert_csv_to_bigquery(
    client: bigquery.Client,
    table: bigquery.Table,
    csv_filepath: str,
    write_disposition: str = "WRITE_APPEND",
) -> None:
    """
    Reads a CSV file and inserts its contents into a BigQuery table.

    Args:
        client: A BigQuery client object.
        table: A BigQuery table object.
        csv_filepath: The path to the CSV file.
        write_disposition: Specifies the action that occurs if the destination
            table already exists.
            Valid values are:
                - "WRITE_APPEND": Appends the data to the table.
                - "WRITE_TRUNCATE": Overwrites the table data.
                - "WRITE_EMPTY": Only writes if the table is empty.
            Defaults to "WRITE_APPEND".

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If the write_disposition is invalid.
        google.cloud.exceptions.GoogleCloudError: If any other error occurs
            during the BigQuery operation.
    """

    if write_disposition not in [
        "WRITE_APPEND",
        "WRITE_TRUNCATE",
        "WRITE_EMPTY",
    ]:
        raise ValueError(
            f"Invalid write_disposition: {write_disposition}. "
            "Must be one of 'WRITE_APPEND', 'WRITE_TRUNCATE', or 'WRITE_EMPTY'."
        )

    try:
        with open(csv_filepath, "r", encoding="utf-8") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            rows_to_insert = list(csv_reader)

    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {csv_filepath}") from None

    if not rows_to_insert:
        print("CSV file is empty. Nothing to insert.")
        return

    errors = client.insert_rows_json(
        table, rows_to_insert, row_ids=[None] * len(rows_to_insert)
    )

    if errors:
        raise GoogleCloudError(
            f"Errors occurred while inserting rows: {errors}"
        )
    else:
        print(
            f"Successfully inserted {len(rows_to_insert)} rows into "
            f"{table.table_id}."
        )


def main(argv: Sequence[str]) -> None:  # pylint: disable=unused-argument

    # Define the table schema
    data_table_name = "timeseries_data"
    data_table_schema = [
        bigquery.SchemaField("timeseries_code", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("value", "FLOAT", mode="REQUIRED"),
    ]
    data_table_description = "Timeseries data"

    client = bigquery.Client(project=FLAGS.project_id)

    dataset = create_bigquery_dataset(
        client,
        FLAGS.dataset_id,
        FLAGS.location,
        description="Timeseries dataset",
    )

    data_table = create_bigquery_table(
        client,
        dataset.dataset_id,
        data_table_name,
        data_table_schema,
        data_table_description,
    )

    if FLAGS.data_file:
        insert_csv_to_bigquery(client, data_table, FLAGS.data_file)


if __name__ == "__main__":
    app.run(main)

```


---

## 文件: fomc-research\deployment\deploy.py

```python
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

"""Deployment script for FOMC Research agent."""

import os

import vertexai
from absl import app, flags
from dotenv import load_dotenv
from fomc_research.agent import root_agent
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP bucket.")
flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")

flags.DEFINE_bool("create", False, "Create a new agent.")
flags.DEFINE_bool("delete", False, "Delete an existing agent.")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])

AGENT_WHL_FILE = "fomc_research-0.1-py3-none-any.whl"


def create() -> None:
    adk_app = AdkApp(
        agent=root_agent,
        enable_tracing=False,
    )

    remote_agent = agent_engines.create(
        adk_app,
        requirements=[f"./{AGENT_WHL_FILE}"],
        extra_packages=[f"./{AGENT_WHL_FILE}"],
    )
    print(f"Created remote agent: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    remote_agent = agent_engines.get(resource_id)
    remote_agent.delete(force=True)
    print(f"Deleted remote agent: {resource_id}")


def main(argv: list[str]) -> None:  # pylint: disable=unused-argument

    load_dotenv()

    project_id = (
        FLAGS.project_id
        if FLAGS.project_id
        else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = (
        FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    bucket = (
        FLAGS.bucket
        if FLAGS.bucket
        else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
    )

    print(f"PROJECT: {project_id}")
    print(f"LOCATION: {location}")
    print(f"BUCKET: {bucket}")

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print(
            "Missing required environment variable: GOOGLE_CLOUD_STORAGE_BUCKET"
        )
        return

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    if FLAGS.create:
        create()
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("resource_id is required for delete")
            return
        delete(FLAGS.resource_id)
    else:
        print("Unknown command")


if __name__ == "__main__":
    app.run(main)

```


---

## 文件: fomc-research\deployment\test_deployment.py

```python
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

"""Test deployment of FOMC Research Agent to Agent Engine."""

import os

import vertexai
from absl import app, flags
from dotenv import load_dotenv
from vertexai import agent_engines

FLAGS = flags.FLAGS

flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP bucket.")
flags.DEFINE_string(
    "resource_id",
    None,
    "ReasoningEngine resource ID (returned after deploying the agent)",
)
flags.DEFINE_string("user_id", None, "User ID (can be any string).")
flags.mark_flag_as_required("resource_id")
flags.mark_flag_as_required("user_id")


def main(argv: list[str]) -> None:  # pylint: disable=unused-argument

    load_dotenv()

    project_id = (
        FLAGS.project_id
        if FLAGS.project_id
        else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = (
        FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    bucket = (
        FLAGS.bucket
        if FLAGS.bucket
        else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
    )

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print(
            "Missing required environment variable: GOOGLE_CLOUD_STORAGE_BUCKET"
        )
        return

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    agent = agent_engines.get(FLAGS.resource_id)
    print(f"Found agent with resource ID: {FLAGS.resource_id}")
    session = agent.create_session(user_id=FLAGS.user_id)
    print(f"Created session for user ID: {FLAGS.user_id}")
    print("Type 'quit' to exit.")
    while True:
        user_input = input("Input: ")
        if user_input == "quit":
            break

        for event in agent.stream_query(
            user_id=FLAGS.user_id, session_id=session["id"], message=user_input
        ):
            if "content" in event:
                if "parts" in event["content"]:
                    parts = event["content"]["parts"]
                    for part in parts:
                        if "text" in part:
                            text_part = part["text"]
                            print(f"Response: {text_part}")

    agent.delete_session(user_id=FLAGS.user_id, session_id=session["id"])
    print(f"Deleted session for user ID: {FLAGS.user_id}")


if __name__ == "__main__":
    app.run(main)

```


---

## 文件: fomc-research\fomc_research\agent.py

```python
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

"""FOMC Research sample agent."""

import logging
import warnings

from google.adk.agents import Agent

from . import MODEL, root_agent_prompt
from .shared_libraries.callbacks import rate_limit_callback
from .sub_agents.analysis_agent import AnalysisAgent
from .sub_agents.research_agent import ResearchAgent
from .sub_agents.retrieve_meeting_data_agent import RetrieveMeetingDataAgent
from .tools.store_state import store_state_tool

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

logger = logging.getLogger(__name__)
logger.debug("Using MODEL: %s", MODEL)


root_agent = Agent(
    model=MODEL,
    name="root_agent",
    description=(
        "Use tools and other agents provided to generate an analysis report"
        "about the most recent FMOC meeting."
    ),
    instruction=root_agent_prompt.PROMPT,
    tools=[store_state_tool],
    sub_agents=[
        RetrieveMeetingDataAgent,
        ResearchAgent,
        AnalysisAgent,
    ],
    before_model_callback=rate_limit_callback,
)

```


---

## 文件: fomc-research\fomc_research\root_agent_prompt.py

```python
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

"""Instruction for FOMC Research root agent."""

PROMPT = """
You are a virtual research assistant for financial services. You specialize in
creating thorough analysis reports on Fed Open Market Committee meetings.

The user will provide the date of the meeting they want to analyze. If they have
not provided it, ask them for it. If the answer they give doesn't make sense,
ask them to correct it.

When you have this information, call the store_state tool to store the meeting
date in the ToolContext. Use the key "user_requested_meeting_date" and format
the date in ISO format (YYYY-MM-DD).

Then call the retrieve_meeting_data agent to fetch the data about the current
meeting from the Fed website.
"""

```


---

## 文件: fomc-research\fomc_research\shared_libraries\callbacks.py

```python
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

"""Callback functions for FOMC Research Agent."""

import logging
import time

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Adjust these values to limit the rate at which the agent
# queries the LLM API.
RATE_LIMIT_SECS = 60
RPM_QUOTA = 1000


def rate_limit_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    # pylint: disable=unused-argument
    """Callback function that implements a query rate limit.

    Args:
      callback_context: A CallbackContext object representing the active
              callback context.
      llm_request: A LlmRequest object representing the active LLM request.
    """
    now = time.time()
    if "timer_start" not in callback_context.state:
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
        logger.debug(
            "rate_limit_callback [timestamp: %i, req_count: 1, "
            "elapsed_secs: 0]",
            now,
        )
        return

    request_count = callback_context.state["request_count"] + 1
    elapsed_secs = now - callback_context.state["timer_start"]
    logger.debug(
        "rate_limit_callback [timestamp: %i, request_count: %i,"
        " elapsed_secs: %i]",
        now,
        request_count,
        elapsed_secs,
    )

    if request_count > RPM_QUOTA:
        delay = RATE_LIMIT_SECS - elapsed_secs + 1
        if delay > 0:
            logger.debug("Sleeping for %i seconds", delay)
            time.sleep(delay)
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
    else:
        callback_context.state["request_count"] = request_count

    return

```


---

## 文件: fomc-research\fomc_research\shared_libraries\file_utils.py

```python
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

"""File-related utility functions for fed_research_agent."""

import base64
import binascii
import io
import logging
import mimetypes
from collections.abc import Sequence

import diff_match_patch as dmp
import pdfplumber
import requests
from absl import app
from google.adk.tools import ToolContext
from google.genai.types import Blob, Part

logger = logging.getLogger(__name__)


def download_file_from_url(
    url: str, output_filename: str, tool_context: ToolContext
) -> str:
    """Downloads a file from a URL and stores it in an artifact.

    Args:
      url: The URL to retrieve the file from.
      output_filename: The name of the artifact to store the file in.
      tool_context: The tool context.

    Returns:
      The name of the artifact.
    """
    logger.info("Downloading %s to %s", url, output_filename)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        file_bytes = base64.b64encode(response.content)
        mime_type = response.headers.get(
            "Content-Type", mimetypes.guess_type(url)
        )
        artifact = Part(inline_data=Blob(data=file_bytes, mime_type=mime_type))
        tool_context.save_artifact(filename=output_filename, artifact=artifact)
        logger.info("Downloaded %s to artifact %s", url, output_filename)
        return output_filename

    except requests.exceptions.RequestException as e:
        logger.error("Error downloading file from URL: %s", e)
        return None


def extract_text_from_pdf_artifact(
    pdf_path: str, tool_context: ToolContext
) -> str:
    """Extracts text from a PDF file stored in an artifact"""
    pdf_artifact = tool_context.load_artifact(pdf_path)
    try:
        with io.BytesIO(
            base64.b64decode(pdf_artifact.inline_data.data)
        ) as pdf_file_obj:
            pdf_text = ""
            with pdfplumber.open(pdf_file_obj) as pdf:
                for page in pdf.pages:
                    pdf_text += page.extract_text()
            return pdf_text
    except binascii.Error as e:
        logger.error("Error decoding PDF: %s", e)
        return None


def create_html_redline(text1: str, text2: str) -> str:
    """Creates an HTML redline doc of differences between text1 and text2."""
    d = dmp.diff_match_patch()
    diffs = d.diff_main(text2, text1)
    d.diff_cleanupSemantic(diffs)

    html_output = ""
    for op, text in diffs:
        if op == -1:  # Deletion
            html_output += (
                f'<del style="background-color: #ffcccc;">{text}</del>'
            )
        elif op == 1:  # Insertion
            html_output += (
                f'<ins style="background-color: #ccffcc;">{text}</ins>'
            )
        else:  # Unchanged
            html_output += text

    return html_output


def save_html_to_artifact(
    html_content: str, output_filename: str, tool_context: ToolContext
) -> str:
    """Saves HTML content to an artifact in UTF-8 encoding.

    Args:
      html_content: The HTML content to save.
      output_filename: The name of the artifact to store the HTML in.

    Returns:
      The name of the artifact.
    """
    artifact = Part(text=html_content)
    tool_context.save_artifact(filename=output_filename, artifact=artifact)
    logger.info("HTML content successfully saved to %s", output_filename)
    return output_filename


def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Too many command-line arguments.")


if __name__ == "__main__":
    app.run(main)

```


---

## 文件: fomc-research\fomc_research\shared_libraries\price_utils.py

```python
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

"""Price-related utility functions for FOMC Research Agent."""

import datetime
import logging
import math
import os
from collections.abc import Sequence

from absl import app
from google.cloud import bigquery

bqclient = bigquery.Client()
logger = logging.getLogger(__name__)

MOVE_SIZE_BP = 25
DATASET_NAME = os.getenv("GOOGLE_CLOUD_BQ_DATASET")
if not DATASET_NAME:
    DATASET_NAME = "fomc_research_agent"
TIMESERIES_CODES = os.getenv("GOOGLE_GENAI_FOMC_AGENT_TIMESERIES_CODES")
if not TIMESERIES_CODES:
    TIMESERIES_CODES = "SFRH5,SFRZ5"


def fetch_prices_from_bq(
    timeseries_codes: list[str], dates: list[datetime.date]
) -> dict[dict[datetime.date, float]]:
    """Fetches prices from Bigquery.

    Args:
      timeseries_codes: List of timeseries codes to fetch.
      dates: List of dates to fetch.

    Returns:
      Dictionary of timeseries codes to dictionaries of dates to prices.
    """

    logger.debug("fetch_prices_from_bq: timeseries_codes: %s", timeseries_codes)
    logger.debug("fetch_prices_from_bq: dates: %s", dates)

    query = f"""
SELECT DISTINCT timeseries_code, date, value
FROM {DATASET_NAME}.timeseries_data
WHERE timeseries_code IN UNNEST(@timeseries_codes)
  AND date IN UNNEST(@dates)
"""

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter(
                "timeseries_codes", "STRING", timeseries_codes
            ),
            bigquery.ArrayQueryParameter("dates", "DATE", dates),
        ]
    )

    prices = {}
    query_job = bqclient.query(query, job_config=job_config)
    results = query_job.result()
    for row in results:
        logger.debug(
            "code: %s, date: %s, value: %s",
            row.timeseries_code,
            row.date,
            row.value,
        )
        if row.timeseries_code not in prices:
            prices[row.timeseries_code] = {row.date: row.value}
        else:
            prices[row.timeseries_code][row.date] = row.value

    return prices


def number_of_moves(
    front_ff_future_px: float, back_ff_future_px: float
) -> float:
    """Computes the expected number of rate moves between two prices.

    Args:
      front_ff_future_px: Front fed funds future price.
      back_ff_future_px: Back fed funds future price.

    Returns:
      Number of moves.

    For calculation details see
    https://www.biancoresearch.com/bianco/samples/SR2v1.pdf

    """

    move_size_pct = MOVE_SIZE_BP / 100
    front_implied_rate = 100 - front_ff_future_px
    back_implied_rate = 100 - back_ff_future_px
    rate_delta = back_implied_rate - front_implied_rate
    num_moves = rate_delta / move_size_pct
    return num_moves


def fed_meeting_probabilities(nmoves: float) -> dict:
    move_text = "hike" if nmoves > 0 else "cut"
    if nmoves > 1:
        move_text = move_text + "s"

    max_expected_moves = math.ceil(abs(nmoves))
    max_expected_move_bp = max_expected_moves * MOVE_SIZE_BP
    move_odds = round(math.modf(abs(nmoves))[0], 2)

    output = {
        f"odds of {max_expected_move_bp}bp {move_text}": move_odds,
        f"odds of no {move_text}": round(1 - move_odds, 2),
    }

    return output


def compute_probabilities(meeting_date_str: str) -> dict:
    """Computes the probabilities of a rate move for a specific date.

    Args:
      meeting_date_str: Date of the Fed meeting.

    Returns:
      Dictionary of probabilities.
    """
    meeting_date = datetime.date.fromisoformat(meeting_date_str)
    meeting_date_day_before = meeting_date - datetime.timedelta(days=1)
    timeseries_codes = [x.strip() for x in TIMESERIES_CODES.split(",")]

    prices = fetch_prices_from_bq(
        timeseries_codes, [meeting_date, meeting_date_day_before]
    )

    error = None
    for code in timeseries_codes:
        if code not in prices:
            error = f"No data for {code}"
            break
        elif meeting_date not in prices[code]:
            error = f"No data for {code} on {meeting_date}"
            break
        elif meeting_date_day_before not in prices[code]:
            error = f"No data for {code} on {meeting_date_day_before}"
            break

    logger.debug("compute_probabilities: found prices: %s", prices)

    if error:
        return {"status": "ERROR", "message": error}

    near_code = timeseries_codes[0]
    far_code = timeseries_codes[1]
    num_moves_post = number_of_moves(
        prices[near_code][meeting_date], prices[far_code][meeting_date]
    )
    num_moves_pre = number_of_moves(
        prices[near_code][meeting_date_day_before],
        prices[far_code][meeting_date_day_before],
    )

    probs_pre = fed_meeting_probabilities(num_moves_pre)
    probs_post = fed_meeting_probabilities(num_moves_post)

    output = {
        (
            "Odds of a rate move within the next year ",
            "(computed before Fed meeting):",
        ): (probs_pre),
        (
            "Odds of a rate move within the next year ",
            "(computed after Fed meeting)",
        ): (probs_post),
    }

    return {"status": "OK", "output": output}


def main(argv: Sequence[str]) -> None:
    if len(argv) > 2:
        raise app.UsageError("Too many command-line arguments.")

    meeting_date = argv[1]
    print("meeting_date: ", meeting_date)

    print(compute_probabilities(meeting_date))


if __name__ == "__main__":
    app.run(main)

```


---

## 文件: fomc-research\fomc_research\sub_agents\analysis_agent.py

```python
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

"""Analyze the research output for the FOMC Research Agent."""

from google.adk.agents import Agent

from ..agent import MODEL
from ..shared_libraries.callbacks import rate_limit_callback
from . import analysis_agent_prompt

AnalysisAgent = Agent(
    model=MODEL,
    name="analysis_agent",
    description=(
        "Analyze inputs and determine implications for future FOMC actions."
    ),
    instruction=analysis_agent_prompt.PROMPT,
    before_model_callback=rate_limit_callback,
)

```


---

## 文件: fomc-research\fomc_research\sub_agents\analysis_agent_prompt.py

```python
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

"""Prompt definition for the Analysis sub-agent of the FOMC Research Agent."""

PROMPT = """
You are an experienced financial analyst, specializing in the analysis of
meetings and minutes of the Federal Open Market Committee (FOMC). Your goal is
to develop a thorough and insightful report on the latest FOMC
meeting. You have access to the output from previous agents to develop your
analysis, shown below.

<RESEARCH_OUTPUT>

<REQUESTED_FOMC_STATEMENT>
{artifact.requested_statement_fulltext}
</REQUESTED_FOMC_STATEMENT>

<PREVIOUS_FOMC_STATEMENT>
{artifact.previous_statement_fulltext}
</PREVIOUS_FOMC_STATEMENT>

<STATEMENT_REDLINE>
{artifact.statement_redline}
</STATEMENT_REDLINE>

<MEETING_SUMMARY>
{meeting_summary}
</MEETING_SUMMARY>

<RATE_MOVE_PROBABILITIES>
{rate_move_probabilities}
</RATE_MOVE_PROBABILITIES>

</RESEARCH_OUTPUT>

Ignore any other data in the Tool Context.

Generate a short (1-2 page) report based on your analysis of the information you
received. Be specific in your analysis; use specific numbers if available,
instead of making general statements.
"""

```


---

## 文件: fomc-research\fomc_research\sub_agents\extract_page_data_agent.py

```python
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

"""Extracts specific data from a web page."""

from google.adk.agents import Agent

from ..agent import MODEL
from ..shared_libraries.callbacks import rate_limit_callback
from ..tools.store_state import store_state_tool
from . import extract_page_data_agent_prompt

ExtractPageDataAgent = Agent(
    model=MODEL,
    name="extract_page_data_agent",
    description="Extract important data from the web page content",
    instruction=extract_page_data_agent_prompt.PROMPT,
    tools=[store_state_tool],
    before_model_callback=rate_limit_callback,
)

```


---

## 文件: fomc-research\fomc_research\sub_agents\extract_page_data_agent_prompt.py

```python
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

"""Prompt definition for extract_page_data_agent in FOMC Research Agent"""

PROMPT = """
Your job is to extract important data from a web page.

 <PAGE_CONTENTS>
 {page_contents}
 </PAGE_CONTENTS>

<INSTRUCTIONS>
The contents of the web page are provided above in the 'page_contents' section.
The data fields needed are provided in the 'data_to_extract' section of the user
input.

Read the contents of the web page and extract the pieces of data requested.
Don't use any other HTML parser, just examine the HTML yourself and extract the
information.

First, use the store_state tool to store the extracted data in the ToolContext.

Second, return the information you found to the user in JSON format.
 </INSTRUCTIONS>

"""

```


---

## 文件: fomc-research\fomc_research\sub_agents\research_agent.py

```python
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

"""Research coordinator agent for FOMC Research Agent."""

from google.adk.agents import Agent

from ..agent import MODEL
from ..shared_libraries.callbacks import rate_limit_callback
from ..tools.compare_statements import compare_statements_tool
from ..tools.compute_rate_move_probability import compute_rate_move_probability_tool
from ..tools.fetch_transcript import fetch_transcript_tool
from ..tools.store_state import store_state_tool
from . import research_agent_prompt
from .summarize_meeting_agent import SummarizeMeetingAgent

ResearchAgent = Agent(
    model=MODEL,
    name="research_agent",
    description=(
        "Research the latest FOMC meeting to provide information for analysis."
    ),
    instruction=research_agent_prompt.PROMPT,
    sub_agents=[
        SummarizeMeetingAgent,
    ],
    tools=[
        store_state_tool,
        compare_statements_tool,
        fetch_transcript_tool,
        compute_rate_move_probability_tool,
    ],
    before_model_callback=rate_limit_callback,
)

```


---

## 文件: fomc-research\fomc_research\sub_agents\research_agent_prompt.py

```python
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

"""Prompt definintion for research_agent for FOMC Research Agent."""

PROMPT = """
You are a virtual research coordinator. Your job is to coordinate the activities
of other virtual research agents.

Follow these steps in order (be sure to tell the user what you're doing at each
step, but without giving technical details):

1) Call the compare_statements tool to generate an HTML redline file showing the
differences between the requested and previous FOMC statements.

2) Call the fetch_transcript tool to retrieve the transcript.

3) Call the summarize_meeting_agent with the argument "Summarize the
meeting transcript provided".

4) Call the compute_rate_move_probability tool to compute the market-implied
probabilities of an interest rate move. If the tool returns an error, use the
error message to explain the problem to the user, then continue to the next step.

5) Finally, once all the steps are complete, transfer to analysis_agent to complete the
analysis. DO NOT generate any analysis or output for the user yourself.
"""

```


---

## 文件: fomc-research\fomc_research\sub_agents\retrieve_meeting_data_agent.py

```python
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

"""Retrieve meeting data sub-agent for FOMC Research Agent"""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from ..agent import MODEL
from ..shared_libraries.callbacks import rate_limit_callback
from ..tools.fetch_page import fetch_page_tool
from . import retrieve_meeting_data_agent_prompt
from .extract_page_data_agent import ExtractPageDataAgent

RetrieveMeetingDataAgent = Agent(
    model=MODEL,
    name="retrieve_meeting_data_agent",
    description=("Retrieve data about a Fed meeting from the Fed website"),
    instruction=retrieve_meeting_data_agent_prompt.PROMPT,
    tools=[
        fetch_page_tool,
        AgentTool(ExtractPageDataAgent),
    ],
    sub_agents=[],
    before_model_callback=rate_limit_callback,
)

```


---

## 文件: fomc-research\fomc_research\sub_agents\retrieve_meeting_data_agent_prompt.py

```python
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

"""Prompt definition for retrieve_meeting_data_agent for FOMC Research Agent"""

PROMPT = """
Your job is to retrieve data about a Fed meeting from the Fed website.

Follow these steps in order (be sure to tell the user what you're doing at each
step, but without giving technical details):

1) Call the fetch_page tool to retrieve this web page:
   url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"

2) Call the extract_page_data_agent Tool with this argument:
"<DATA_TO_EXTRACT>
* requested_meeting_date: the date of the Fed meeting closest to the meeting
  date the user requested ({user_requested_meeting_date}), in ISO format
  (YYYY-MM-DD). If the date you find is a range, store only the last day in the
  range.
* previous_meeting_date: the date of the Fed meeting before the meeting
  nearest to the date the user requested, in ISO format (YYYY-MM-DD). If the
  date you find is a range, store only the last day in the range.
* requested_meeting_url: the URL for the "Press Conference" page about the
  nearest Fed meeting.
* previous_meeting_url: the URL for the "Press Conference" page about the
  previous Fed meeting.
* requested_meeting_statement_pdf_url: the URL for the PDF of the statement
  from the nearest Fed meeting.
* previous_meeting_statement_pdf_url: the URL for the PDF of the statement
  from the previous fed meeting.
</DATA_TO_EXTRACT>"

3) Call the fetch_page tool to retrieve the meeting web page. If the value
of requested_meeting_url you find in the last step starts with
"https://www.federalreserve.gov", just pass the value of "requested_meeting_url"
to the fetch_page tool. If not, use the template below: take out
"<requested_meeting_url>" and replace it with the value of
"requested_meeting_url" you found in the last step.

  url template = "https://www.federalreserve.gov/<requested_meeting_url>"

4) Call the extract_page_data_agent Tool again. This time pass it this argument:
"<DATA_TO_EXTRACT>
* transcript_url: the URL for the PDF of the transcript of the press
   conference, labeled 'Press Conference Transcript' on the web page
</DATA_TO_EXTRACT>"

5) Transfer to research_agent.

"""

```


---

## 文件: fomc-research\fomc_research\sub_agents\summarize_meeting_agent.py

```python
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

"""Summarize the content of the FOMC meeting transcript."""

from google.adk.agents import Agent

from ..agent import MODEL
from ..shared_libraries.callbacks import rate_limit_callback
from ..tools.store_state import store_state_tool
from . import summarize_meeting_agent_prompt

SummarizeMeetingAgent = Agent(
    name="summarize_meeting_agent",
    model=MODEL,
    description=(
        "Summarize the content and sentiment of the latest FOMC meeting."
    ),
    instruction=summarize_meeting_agent_prompt.PROMPT,
    tools=[
        store_state_tool,
    ],
    before_model_callback=rate_limit_callback,
)

```


---

## 文件: fomc-research\fomc_research\sub_agents\summarize_meeting_agent_prompt.py

```python
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

"""Prompt definintion for summarize_meeting_agent of FOMC Research Agent."""

PROMPT = """
You are a financial analyst experienced in understanding the meaning, sentiment
and sub-text of financial meeting transcripts. Below is the transcript
of the latest FOMC meeting press conference.

<TRANSCRIPT>
{artifact.transcript_fulltext}
</TRANSCRIPT>

Read this transcript and create a summary of the content and sentiment of this
meeting. Call the store_state tool with key 'meeting_summary' and the value as your
meeting summary. Tell the user what you are doing but do not output your summary
to the user.

Then call transfer_to_agent to transfer to research_agent.

"""

```


---

## 文件: fomc-research\fomc_research\tools\compare_statements.py

```python
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

"""'compare_statements' tool for FOMC Research sample agent."""

import logging

from google.adk.tools import ToolContext
from google.genai.types import Part

from ..shared_libraries import file_utils

logger = logging.getLogger(__name__)


def compare_statements_tool(tool_context: ToolContext) -> dict[str, str]:
    """Compares requested and previous statements and generates HTML redline.

    Args:
      tool_context: ToolContext object.

    Returns:
      A dict with "status" and (optional) "error_message" keys.
    """
    fed_hostname = "https://www.federalreserve.gov"

    reqd_statement_url = tool_context.state[
        "requested_meeting_statement_pdf_url"
    ]
    if not reqd_statement_url.startswith("https"):
        reqd_statement_url = fed_hostname + reqd_statement_url
    prev_statement_url = tool_context.state[
        "previous_meeting_statement_pdf_url"
    ]
    if not prev_statement_url.startswith("https"):
        prev_statement_url = fed_hostname + prev_statement_url

    # Download PDFs from URLs to artifacts
    reqd_pdf_path = file_utils.download_file_from_url(
        reqd_statement_url, "curr.pdf", tool_context
    )
    prev_pdf_path = file_utils.download_file_from_url(
        prev_statement_url, "prev.pdf", tool_context
    )

    if reqd_pdf_path is None or reqd_pdf_path is None:
        logger.error("Failed to download files, aborting")
        return {
            "status": "error",
            "error_message": "Failed to download statement files",
        }

    reqd_pdf_text = file_utils.extract_text_from_pdf_artifact(
        reqd_pdf_path, tool_context
    )
    prev_pdf_text = file_utils.extract_text_from_pdf_artifact(
        prev_pdf_path, tool_context
    )

    if reqd_pdf_text is None or prev_pdf_text is None:
        logger.error("Failed to extract text from PDFs, aborting")
        return {
            "status": "error",
            "error_message": "Failed to extract text from PDFs",
        }

    tool_context.save_artifact(
        filename="requested_statement_fulltext",
        artifact=Part(text=reqd_pdf_text),
    )
    tool_context.save_artifact(
        filename="previous_statement_fulltext",
        artifact=Part(text=prev_pdf_text),
    )

    redline_html = file_utils.create_html_redline(reqd_pdf_text, prev_pdf_text)
    file_utils.save_html_to_artifact(
        redline_html, "statement_redline", tool_context
    )

    return {"status": "ok"}

```


---

## 文件: fomc-research\fomc_research\tools\compute_rate_move_probability.py

```python
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

"""'compute_rate_move_probability' tool for FOMC Research sample agent."""

import logging

from google.adk.tools import ToolContext

from ..shared_libraries import price_utils

logger = logging.getLogger(__name__)


def compute_rate_move_probability_tool(
    tool_context: ToolContext,
) -> dict[str, str]:
    """Computes the probabilities of rate moves for the requested meeting date.

    Args:
      tool_context: ToolContext object.

    Returns:
      A dict with "status" and (optional) "error_message" keys.
    """
    meeting_date = tool_context.state["requested_meeting_date"]
    logger.debug("Computing rate move probabilities for %s", meeting_date)
    prob_result = price_utils.compute_probabilities(meeting_date)
    if prob_result["status"] != "OK":
        return {"status": "ERROR", "message": prob_result["message"]}
    probs = prob_result["output"]
    logger.debug("Rate move probabilities: %s", probs)
    tool_context.state.update({"rate_move_probabilities": probs})
    return {"status": "OK"}

```


---

## 文件: fomc-research\fomc_research\tools\fetch_page.py

```python
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

"""'fetch_page' tool for FOMC Research sample agent"""

import logging
import urllib.request

from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)


def fetch_page_tool(url: str, tool_context: ToolContext) -> dict[str, str]:
    """Retrieves the content of 'url' and stores it in the ToolContext.

    Args:
      url: URL to fetch.
      tool_context: ToolContext object.

    Returns:
      A dict with "status" and (optional) "error_message" keys.
    """
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "Mozilla/5.0")]
    urllib.request.install_opener(opener)
    logger.debug("Fetching page: %s", url)
    try:
        page = urllib.request.urlopen(url)
        page_text = page.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        errmsg = "Failed to fetch page %s: %s", url, err
        logger.error(errmsg)
        return {"status": "ERROR", "message": errmsg}
    tool_context.state.update({"page_contents": page_text})
    return {"status": "OK"}

```


---

## 文件: fomc-research\fomc_research\tools\fetch_transcript.py

```python
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

"""'fetch_transcript' tool for FOMC Research sample agent"""

import logging

from google.adk.tools import ToolContext
from google.genai.types import Part

from ..shared_libraries import file_utils

logger = logging.getLogger(__name__)


def fetch_transcript_tool(tool_context: ToolContext) -> dict:
    """Retrieves the Fed press conference transcript from the Fed website.

    Args:
      tool_context: ToolContext object.

    Returns:
      A dict with "status" and (optional) "error_message" keys.
    """
    fed_hostname = "https://www.federalreserve.gov"
    transcript_url = tool_context.state["transcript_url"]
    if not transcript_url.startswith("https"):
        transcript_url = fed_hostname + transcript_url
    pdf_path = file_utils.download_file_from_url(
        transcript_url, "transcript.pdf", tool_context
    )
    if pdf_path is None:
        logger.error("Failed to download PDF from URLs, aborting")
        return {
            "status": "error",
            "error_message": "Failed to download PDFs from GCS",
        }

    text = file_utils.extract_text_from_pdf_artifact(pdf_path, tool_context)
    filename = "transcript_fulltext"
    version = tool_context.save_artifact(
        filename=filename, artifact=Part(text=text)
    )
    logger.info("Saved artifact %s, ver %i", filename, version)
    return {"status": "ok"}

```


---

## 文件: fomc-research\fomc_research\tools\store_state.py

```python
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

"""'store_state' tool for FOMC Research sample agent"""

import logging
import typing

from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)


def store_state_tool(
    state: dict[str, typing.Any], tool_context: ToolContext
) -> dict[str, str]:
    """Stores new state values in the ToolContext.

    Args:
      state: A dict of new state values.
      tool_context: ToolContext object.

    Returns:
      A dict with "status" and (optional) "error_message" keys.
    """
    logger.info("store_state_tool(): %s", state)
    tool_context.state.update(state)
    return {"status": "ok"}

```


---

## 文件: llm-auditor\deployment\deploy.py

```python
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

"""Deployment script for LLM Auditor."""

import os

from absl import app
from absl import flags
from dotenv import load_dotenv
from llm_auditor.agent import root_agent
import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP bucket.")
flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")

flags.DEFINE_bool("list", False, "List all agents.")
flags.DEFINE_bool("create", False, "Creates a new agent.")
flags.DEFINE_bool("delete", False, "Deletes an existing agent.")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])

_AI_PLATFORM_GIT = (
    "git+https://github.com/googleapis/python-aiplatform.git@copybara_738852226"
)


def create() -> None:
    """Creates an agent engine for LLM Auditor."""
    adk_app = AdkApp(agent=root_agent, enable_tracing=True)

    remote_agent = agent_engines.create(
        adk_app,
        display_name=root_agent.name,
        requirements=[
            "google-adk (>=0.0.2)",
            f"google-cloud-aiplatform[agent_engines] @ {_AI_PLATFORM_GIT}",
            "google-genai (>=1.5.0,<2.0.0)",
            "pydantic (>=2.10.6,<3.0.0)",
            "absl-py (>=2.2.1,<3.0.0)",
        ],
        extra_packages=["./llm_auditor"],
    )
    print(f"Created remote agent: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    remote_agent = agent_engines.get(resource_id)
    remote_agent.delete(force=True)
    print(f"Deleted remote agent: {resource_id}")


def list_agents() -> None:
    remote_agents = agent_engines.list()
    TEMPLATE = '''
{agent.name} ("{agent.display_name}")
- Create time: {agent.create_time}
- Update time: {agent.update_time}
'''
    remote_agents_string = '\n'.join(TEMPLATE.format(agent=agent) for agent in remote_agents)
    print(f"All remote agents:\n{remote_agents_string}")

def main(argv: list[str]) -> None:
    del argv  # unused
    load_dotenv()

    project_id = (
        FLAGS.project_id
        if FLAGS.project_id
        else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = (
        FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    bucket = (
        FLAGS.bucket if FLAGS.bucket
        else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
    )

    print(f"PROJECT: {project_id}")
    print(f"LOCATION: {location}")
    print(f"BUCKET: {bucket}")

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print(
            "Missing required environment variable: GOOGLE_CLOUD_STORAGE_BUCKET"
        )
        return

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    if FLAGS.list:
        list_agents()
    elif FLAGS.create:
        create()
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("resource_id is required for delete")
            return
        delete(FLAGS.resource_id)
    else:
        print("Unknown command")


if __name__ == "__main__":
    app.run(main)

```


---

## 文件: llm-auditor\eval\test_eval.py

```python
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

"""Basic evalualtion for LLM Auditor."""

import pathlib

import dotenv
from google.adk.evaluation import AgentEvaluator
import pytest


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


def test_all():
    """Test the agent's basic ability on a few examples."""
    AgentEvaluator.evaluate(
        "llm_auditor",
        str(pathlib.Path(__file__).parent / "data"),
        num_runs=1,
    )

```


---

## 文件: llm-auditor\eval\data\blueberries.test.json

```json
[
  {
    "query": "Q: Why the blueberries are blue? A: Because blueberries have pigments on their skin.",
    "expected_tool_use": [],
    "reference": "I will revise the answer to address the inaccuracies identified in the previous analysis. Revised answer: Because blueberries have a coating of wax on their surface that scatters blue light."
  }
]

```


---

## 文件: llm-auditor\eval\data\ice_cream_sandwich.test.json

```json
[
  {
    "query": "Question: Is Ice Cream Sandwich a version of Android? Answer: Yes, Ice Cream Sandwich is the name of Android 4.0.",
    "expected_tool_use": [],
    "reference": "Yes, Ice Cream Sandwich is the name of Android 4.0."
  }
]

```


---

## 文件: llm-auditor\eval\data\test_config.json

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.35
  }
}

```


---

## 文件: llm-auditor\llm_auditor\agent.py

```python
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

"""LLM Auditor for verifying & refining LLM-generated answers using the web."""

from google.adk.agents import SequentialAgent

from .sub_agents.critic import critic_agent
from .sub_agents.reviser import reviser_agent


llm_auditor = SequentialAgent(
    name='llm_auditor',
    description=(
        'Evaluates LLM-generated answers, verifies actual accuracy using the'
        ' web, and refines the response to ensure alignment with real-world'
        ' knowledge.'
    ),
    sub_agents=[critic_agent, reviser_agent],
)

root_agent = llm_auditor

```


---

## 文件: llm-auditor\llm_auditor\sub_agents\critic\agent.py

```python
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

"""Critic agent for identifying and verifying statements using search tools."""

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools import google_search
from google.genai import types

from . import prompt


def _render_reference(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse:
    """Appends grounding references to the response."""
    del callback_context
    if (
        not llm_response.content or
        not llm_response.content.parts or
        not llm_response.grounding_metadata
    ):
        return llm_response
    references = []
    for chunk in llm_response.grounding_metadata.grounding_chunks or []:
        title, uri, text = '', '', ''
        if chunk.retrieved_context:
            title = chunk.retrieved_context.title
            uri = chunk.retrieved_context.uri
            text = chunk.retrieved_context.text
        elif chunk.web:
            title = chunk.web.title
            uri = chunk.web.uri
        parts = [s for s in (title, text) if s]
        if uri and parts:
            parts[0] = f'[{parts[0]}]({uri})'
        if parts:
            references.append('* ' + ': '.join(parts) + '\n')
    if references:
        reference_text = ''.join(['\n\nReference:\n\n'] + references)
        llm_response.content.parts.append(types.Part(text=reference_text))
    if all(part.text is not None for part in llm_response.content.parts):
        all_text = '\n'.join(part.text for part in llm_response.content.parts)
        llm_response.content.parts[0].text = all_text
        del llm_response.content.parts[1:]
    return llm_response


critic_agent = Agent(
    model='gemini-2.0-flash',
    name='critic_agent',
    instruction=prompt.CRITIC_PROMPT,
    tools=[google_search],
    after_model_callback=_render_reference,
)

```


---

## 文件: llm-auditor\llm_auditor\sub_agents\critic\prompt.py

```python
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

"""Prompt for the critic agent."""

CRITIC_PROMPT = """
You are a professional investigative journalist, excelling at critical thinking and verifying information before printed to a highly-trustworthy publication.
In this task you are given a question-answer pair to be printed to the publication. The publication editor tasked you to double-check the answer text.

# Your task

Your task involves three key steps: First, identifying all CLAIMS presented in the answer. Second, determining the reliability of each CLAIM. And lastly, provide an overall assessment.

## Step 1: Identify the CLAIMS

Carefully read the provided answer text. Extract every distinct CLAIM made within the answer. A CLAIM can be a statement of fact about the world or a logical argument presented to support a point.

## Step 2: Verify each CLAIM

For each CLAIM you identified in Step 1, perform the following:

* Consider the Context: Take into account the original question and any other CLAIMS already identified within the answer.
* Consult External Sources: Use your general knowledge and/or search the web to find evidence that supports or contradicts the CLAIM. Aim to consult reliable and authoritative sources.
* Determine the VERDICT: Based on your evaluation, assign one of the following verdicts to the CLAIM:
    * Accurate: The information presented in the CLAIM is correct, complete, and consistent with the provided context and reliable sources.
    * Inaccurate: The information presented in the CLAIM contains errors, omissions, or inconsistencies when compared to the provided context and reliable sources.
    * Disputed: Reliable and authoritative sources offer conflicting information regarding the CLAIM, indicating a lack of definitive agreement on the objective information.
    * Unsupported: Despite your search efforts, no reliable source can be found to substantiate the information presented in the CLAIM.
    * Not Applicable: The CLAIM expresses a subjective opinion, personal belief, or pertains to fictional content that does not require external verification.
* Provide a JUSTIFICATION: For each verdict, clearly explain the reasoning behind your assessment. Reference the sources you consulted or explain why the verdict "Not Applicable" was chosen.

## Step 3: Provide an overall assessment

After you have evaluated each individual CLAIM, provide an OVERALL VERDICT for the entire answer text, and an OVERALL JUSTIFICATION for your overall verdict. Explain how the evaluation of the individual CLAIMS led you to this overall assessment and whether the answer as a whole successfully addresses the original question.

# Tips

Your work is iterative. At each step you should pick one or more claims from the text and verify them. Then, continue to the next claim or claims. You may rely on previous claims to verify the current claim.

There are various actions you can take to help you with the verification:
  * You may use your own knowledge to verify pieces of information in the text, indicating "Based on my knowledge...". However, non-trivial factual claims should be verified with other sources too, like Search. Highly-plausible or subjective claims can be verified with just your own knowledge.
  * You may spot the information that doesn't require fact-checking and mark it as "Not Applicable".
  * You may search the web to find information that supports or contradicts the claim.
  * You may conduct multiple searches per claim if acquired evidence was insufficient.
  * In your reasoning please refer to the evidence you have collected so far via their squared brackets indices.
  * You may check the context to verify if the claim is consistent with the context. Read the context carefully to idenfity specific user instructions that the text should follow, facts that the text should be faithful to, etc.
  * You should draw your final conclusion on the entire text after you acquired all the information you needed.

# Output format

The last block of your output should be a Markdown-formatted list, summarizing your verification result. For each CLAIM you verified, you should output the claim (as a standalone statement), the corresponding part in the answer text, the verdict, and the justification.

Here is the question and answer you are going to double check:
"""

```


---

## 文件: llm-auditor\llm_auditor\sub_agents\reviser\agent.py

```python
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

"""Reviser agent for correcting inaccuracies based on verified findings."""

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse

from . import prompt

_END_OF_EDIT_MARK = '---END-OF-EDIT---'


def _remove_end_of_edit_mark(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse:
    del callback_context  # unused
    if not llm_response.content or not llm_response.content.parts:
        return llm_response
    for idx, part in enumerate(llm_response.content.parts):
        if _END_OF_EDIT_MARK in part.text:
            del llm_response.content.parts[idx + 1 :]
            part.text = part.text.split(_END_OF_EDIT_MARK, 1)[0]
    return llm_response


reviser_agent = Agent(
    model='gemini-2.0-flash',
    name='reviser_agent',
    instruction=prompt.REVISER_PROMPT,
    after_model_callback=_remove_end_of_edit_mark,
)

```


---

## 文件: llm-auditor\llm_auditor\sub_agents\reviser\prompt.py

```python
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

"""Prompt for the reviser agent."""

REVISER_PROMPT = """
You are a professional editor working for a highly-trustworthy publication.
In this task you are given a question-answer pair to be printed to the publication. The publication reviewer has double-checked the answer text and provided the findings.
Your task is to minimally revise the answer text to make it accurate, while maintaining the overall structure, style, and length similar to the original.

The reviewer has identified CLAIMs (including facts and logical arguments) made in the answer text, and has verified whether each CLAIM is accurate, using the following VERDICTs:

    * Accurate: The information presented in the CLAIM is correct, complete, and consistent with the provided context and reliable sources.
    * Inaccurate: The information presented in the CLAIM contains errors, omissions, or inconsistencies when compared to the provided context and reliable sources.
    * Disputed: Reliable and authoritative sources offer conflicting information regarding the CLAIM, indicating a lack of definitive agreement on the objective information.
    * Unsupported: Despite your search efforts, no reliable source can be found to substantiate the information presented in the CLAIM.
    * Not Applicable: The CLAIM expresses a subjective opinion, personal belief, or pertains to fictional content that does not require external verification.

Editing guidelines for each type of claim:

  * Accurate claims: There is no need to edit them.
  * Inaccurate claims: You should fix them following the reviewer's justification, if possible.
  * Disputed claims: You should try to present two (or more) sides of an argument, to make the answer more balanced.
  * Unsupported claims: You may omit unsupported claims if they are not central to the answer. Otherwise you may soften the claims or express that they are unsupported.
  * Not applicable claims: There is no need to edit them.

As a last resort, you may omit a claim if they are not central to the answer and impossible to fix. You should also make necessary edits to ensure that the revised answer is self-consistent and fluent. You should not introduce any new claims or make any new statements in the answer text. Your edit should be minimal and maintain overall structure and style unchanged.

Output format:

  * If the answer is accurate, you should output exactly the same answer text as you are given.
  * If the answer is inaccurate, disputed, or unsupported, then you should output your revised answer text.
  * After the answer, output a line of "---END-OF-EDIT---" and stop.

Here are some examples of the task:

=== Example 1 ===

Question: Who was the first president of the US?

Answer: George Washington was the first president of the United States.

Findings:

  * Claim 1: George Washington was the first president of the United States.
      * Verdict: Accurate
      * Justification: Multiple reliable sources confirm that George Washington was the first president of the United States.
  * Overall verdict: Accurate
  * Overall justification: The answer is accurate and completely answers the question.

Your expected response:

George Washington was the first president of the United States.
---END-OF-EDIT---

=== Example 2 ===

Question: What is the shape of the sun?

Answer: The sun is cube-shaped and very hot.

Findings:

  * Claim 1: The sun is cube-shaped.
      * Verdict: Inaccurate
      * Justification: NASA states that the sun is a sphere of hot plasma, so it is not cube-shaped. It is a sphere.
  * Claim 2: The sun is very hot.
      * Verdict: Accurate
      * Justification: Based on my knowledge and the search results, the sun is extremely hot.
  * Overall verdict: Inaccurate
  * Overall justification: The answer states that the sun is cube-shaped, which is incorrect.

Your expected response:

The sun is sphere-shaped and very hot.
---END-OF-EDIT---

Here are the question-answer pair and the reviewer-provided findings:
"""

```


---

## 文件: llm-auditor\tests\test_agents.py

```python
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

"""Test cases for the LLM Auditor."""

import textwrap
import unittest

import dotenv
from google.adk.runners import InMemoryRunner
from google.genai.types import Part
from google.genai.types import UserContent
from llm_auditor.agent import root_agent
import pytest


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


class TestAgents(unittest.TestCase):
    """Basic test for the agent LLM Auditor."""

    def test_happy_path(self):
        """Runs the agent on a simple input and expects a normal response."""
        user_input = textwrap.dedent("""
            Double check this:
            Question: Why is the sky blue?
            Answer: Becauase the water is blue.
        """).strip()

        runner = InMemoryRunner(agent=root_agent)
        session = runner.session_service.create_session(
            app_name=runner.app_name, user_id="test_user"
        )
        content = UserContent(parts=[Part(text=user_input)])
        events = list(runner.run(
            user_id=session.user_id, session_id=session.id, new_message=content
        ))
        response = events[-1].content.parts[0].text

        # The answer in the input is wrong, so we expect the agent to provided a
        # revised answer, and the correct answer should mention scattering.
        self.assertIn("scattering", response.lower())

```


---

## 文件: personalized-shopping\deployment\deploy.py

```python
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

import vertexai
from vertexai.preview.reasoning_engines import AdkApp
from vertexai import agent_engines
from dotenv import load_dotenv
import os

from personalized_shopping.agent import root_agent

load_dotenv()

cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION")
storage_bucket = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

print(f"cloud_project={cloud_project}")
print(f"cloud_location={cloud_location}")
print(f"storage_bucket={storage_bucket}")

vertexai.init(
    project=cloud_project,
    location=cloud_location,
    staging_bucket=f"gs://{storage_bucket}",
)

print("-" * 50)
print("Deploying app begin...")
app = AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

AGENT_WHL_FILE = "./personalized_shopping-0.1.0-py3-none-any.whl"

print("Deploying agent to agent engine...")
remote_app = agent_engines.create(
    app,
    requirements=[
        AGENT_WHL_FILE,
    ],
    extra_packages=[
        AGENT_WHL_FILE,
    ],
)
print("Deploying agent to agent engine finished.")
print("-" * 50)

print("Testing deployemnt:")
session = remote_app.create_session(user_id="123")
for event in remote_app.stream_query(
    user_id="123",
    session_id=session["id"],
    message="Hello!",
):
    print(event)
print("Testing deployemnt finished!")
print("-" * 50)

```


---

## 文件: personalized-shopping\eval\test_eval.py

```python
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

import os

from google.adk.evaluation.agent_evaluator import AgentEvaluator
import dotenv
import pytest


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


def test_simple():
    """Test the agent's basic ability on a few examples."""
    AgentEvaluator.evaluate(
        "personalized_shopping",
        os.path.join(os.path.dirname(__file__), "eval_data"),
        num_runs=1,
    )

```


---

## 文件: personalized-shopping\eval\eval_data\simple.test.json

```json
[
    {
      "query": "Hello, who are you?",
      "expected_tool_use": [],
      "reference": "I am a webshop agent. I can help you find products, explore their details, and guide you through the purchase process. What are you looking for today?"
    }
]
```


---

## 文件: personalized-shopping\eval\eval_data\test_config.json

```json
{
    "criteria": {
      "tool_trajectory_avg_score": 1.0,
      "response_match_score": 0.6
    }
  }
```


---

## 文件: personalized-shopping\personalized_shopping\agent.py

```python
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

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .tools.search import search
from .tools.click import click

from .prompt import personalized_shopping_agent_instruction

root_agent = Agent(
    model="gemini-2.0-flash-001",
    name="personalized_shopping_agent",
    instruction=personalized_shopping_agent_instruction,
    tools=[
        FunctionTool(
            func=search,
        ),
        FunctionTool(
            func=click,
        ),
    ],
)

```


---

## 文件: personalized-shopping\personalized_shopping\prompt.py

```python
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

personalized_shopping_agent_instruction = """You are a webshop agent, your job is to help the user find the product they are looking for, and guide them through the purchase process in a step-by-step, interactive manner.

**Interaction Flow:**

1.  **Initial Inquiry:**
    * Begin by asking the user what product they are looking for if they didn't provide it directly.
    * If they upload an image, analyze what's in the image and use that as the reference product.

2.  **Search Phase:**
    * Use the "search" tool to find relevant products based on the user's request.
    * Present the search results to the user, highlighting key information and available product options.
    * Ask the user which product they would like to explore further.

3.  **Product Exploration:**
    * Once the user selects a product, automatically gather and summarize all available information from the "Description," "Features," and "Reviews" sections.
        * You can do this by clicking any of the "Description," "Features," or "Reviews" buttons, navigate to the respective section and gather the information. After reviewing one section, return to the information page by clicking the "< Prev" button, then repeat for the remaining sections.
        * Avoid prompting the user to review each section individually; instead, summarize the information from all three sections proactively.
    * If the product is not a good fit for the user, inform the user, and ask if they would like to search for other products (provide recommendations).
    * If the user wishes to proceed to search again, use the "Back to Search" button.
    * Important: When you are done with product exploration, remeber to click the "< Prev" button to go back to the product page where all the buying options (colors and sizes) are available.

4.  **Purchase Confirmation:**
    * Click the "< Prev" button to go back to the product page where all the buying options (colors and sizes) are available, if you are not on that page now.
    * Before proceeding with the "Buy Now" action, click on the right size and color options (if available on the current page) based on the user's preference.
    * Ask the user for confirmation to proceed with the purchase.
    * If the user confirms, click the "Buy Now" button.
    * If the user does not confirm, ask the user what they wish to do next.

5.  **Finalization:**
    * After the "Buy Now" button is clicked, inform the user that the purchase is being processed.
    * If any errors occur, inform the user and ask how they would like to proceed.

**Key Guidelines:**

* **Slow and Steady:**
    * Engage with the user when necessary, seeking their input and confirmation.

* **User Interaction:**
    * Prioritize clear and concise communication with the user.
    * Ask clarifying questions to ensure you understand their needs.
    * Provide regular updates and seek feedback throughout the process.

* **Button Handling:**
    * **Note 1:** Clikable buttons after search look like "Back to Search", "Next >", "B09P5CRVQ6", "< Prev", "Descriptions", "Features", "Reviews" etc. All the buying options such as color and size are also clickable.
    * **Note 2:** Be extremely careful here, you must ONLY click on the buttons that are visible in the CURRENT webpage. If you want to click a button that is from the previous webpage, you should use the "< Prev" button to go back to the previous webpage.
    * **Note 3:** If you wish to search and there is no "Search" button, click the "Back to Search" button instead."""

```


---

## 文件: personalized-shopping\personalized_shopping\shared_libraries\init_env.py

```python
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

import gym
from .web_agent_site.envs.web_agent_text_env import WebAgentTextEnv


def init_env(num_products):
    env = gym.make(
        "WebAgentTextEnv-v0",
        observation_mode="text",
        num_products=num_products,
    )
    return env


num_product_items = 50000
webshop_env = init_env(num_product_items)
webshop_env.reset()
print(f"Finished initializing WebshopEnv with {num_product_items} items.")

```


---

## 文件: personalized-shopping\personalized_shopping\shared_libraries\search_engine\convert_product_file_format.py

```python
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

import json
import sys
from tqdm import tqdm

sys.path.insert(0, "../")

from web_agent_site.engine.engine import load_products

all_products, *_ = load_products(filepath="../data/items_shuffle.json")

docs = []
for p in tqdm(all_products, total=len(all_products)):
    option_texts = []
    options = p.get("options", {})
    for option_name, option_contents in options.items():
        option_contents_text = ", ".join(option_contents)
        option_texts.append(f"{option_name}: {option_contents_text}")
    option_text = ", and ".join(option_texts)

    doc = dict()
    doc["id"] = p["asin"]
    doc["contents"] = " ".join(
        [
            p["Title"],
            p["Description"],
            p["BulletPoints"][0],
            option_text,
        ]
    ).lower()
    doc["product"] = p
    docs.append(doc)

with open("./resources_100/documents.jsonl", "w+") as f:
    for doc in docs[:100]:
        f.write(json.dumps(doc) + "\n")

with open("./resources_1k/documents.jsonl", "w+") as f:
    for doc in docs[:1000]:
        f.write(json.dumps(doc) + "\n")

with open("./resources_10k/documents.jsonl", "w+") as f:
    for doc in docs[:10000]:
        f.write(json.dumps(doc) + "\n")

with open("./resources_50k/documents.jsonl", "w+") as f:
    for doc in docs[:50000]:
        f.write(json.dumps(doc) + "\n")

```


---

## 文件: personalized-shopping\personalized_shopping\shared_libraries\web_agent_site\utils.py

```python
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

import bisect
import hashlib
import logging
from os.path import abspath, dirname, join
import random

BASE_DIR = dirname(abspath(__file__))
DEBUG_PROD_SIZE = None  # set to `None` to disable

DEFAULT_ATTR_PATH = join(BASE_DIR, "../data/items_ins_v2.json")
DEFAULT_FILE_PATH = join(BASE_DIR, "../data/items_shuffle.json")

DEFAULT_REVIEW_PATH = join(BASE_DIR, "../data/reviews.json")

FEAT_CONV = join(BASE_DIR, "../data/feat_conv.pt")
FEAT_IDS = join(BASE_DIR, "../data/feat_ids.pt")

HUMAN_ATTR_PATH = join(BASE_DIR, "../data/items_human_ins.json")
HUMAN_ATTR_PATH = join(BASE_DIR, "../data/items_human_ins.json")


def random_idx(cum_weights):
    """Generate random index by sampling uniformly from sum of all weights, then

    selecting the `min` between the position to keep the list sorted (via bisect)
    and the value of the second to last index
    """
    pos = random.uniform(0, cum_weights[-1])
    idx = bisect.bisect(cum_weights, pos)
    idx = min(idx, len(cum_weights) - 2)
    return idx


def setup_logger(session_id, user_log_dir):
    """Creates a log file and logging object for the corresponding session ID"""
    logger = logging.getLogger(session_id)
    formatter = logging.Formatter("%(message)s")
    file_handler = logging.FileHandler(user_log_dir / f"{session_id}.jsonl", mode="w")
    file_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    return logger


def generate_mturk_code(session_id: str) -> str:
    """Generates a redeem code corresponding to the session ID for an MTurk

    worker once the session is completed
    """
    sha = hashlib.sha1(session_id.encode())
    return sha.hexdigest()[:10].upper()

```


---

## 文件: personalized-shopping\personalized_shopping\shared_libraries\web_agent_site\engine\engine.py

```python
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

""" """

from ast import literal_eval
from collections import defaultdict
from decimal import Decimal
import json
import os
import random
import re

from flask import render_template_string
from pyserini.search.lucene import LuceneSearcher
from rich import print
from tqdm import tqdm

from ..utils import (
    BASE_DIR,
    DEFAULT_ATTR_PATH,
    HUMAN_ATTR_PATH,
)

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

SEARCH_RETURN_N = 50
PRODUCT_WINDOW = 10
TOP_K_ATTR = 10

END_BUTTON = "Buy Now"
NEXT_PAGE = "Next >"
PREV_PAGE = "< Prev"
BACK_TO_SEARCH = "Back to Search"

ACTION_TO_TEMPLATE = {
    "Description": "description_page.html",
    "Features": "features_page.html",
    "Reviews": "review_page.html",
    "Attributes": "attributes_page.html",
}


def map_action_to_html(action, **kwargs):
    action_name, action_arg = parse_action(action)
    if action_name == "start":
        path = os.path.join(TEMPLATE_DIR, "search_page.html")
        html = render_template_string(
            read_html_template(path=path),
            session_id=kwargs["session_id"],
            instruction_text=kwargs["instruction_text"],
        )
    elif action_name == "search":
        path = os.path.join(TEMPLATE_DIR, "results_page.html")
        html = render_template_string(
            read_html_template(path=path),
            session_id=kwargs["session_id"],
            products=kwargs["products"],
            keywords=kwargs["keywords"],
            page=kwargs["page"],
            total=kwargs["total"],
            instruction_text=kwargs["instruction_text"],
        )
    elif action_name == "click" and action_arg == END_BUTTON:
        path = os.path.join(TEMPLATE_DIR, "done_page.html")
        html = render_template_string(
            read_html_template(path),
            session_id=kwargs["session_id"],
            reward=kwargs["reward"],
            asin=kwargs["asin"],
            options=kwargs["options"],
            reward_info=kwargs.get("reward_info"),
            goal_attrs=kwargs.get("goal_attrs"),
            purchased_attrs=kwargs.get("purchased_attrs"),
            goal=kwargs.get("goal"),
            mturk_code=kwargs.get("mturk_code"),
            query=kwargs.get("query"),
            category=kwargs.get("category"),
            product_category=kwargs.get("product_category"),
        )
    elif action_name == "click" and action_arg in ACTION_TO_TEMPLATE:
        path = os.path.join(TEMPLATE_DIR, ACTION_TO_TEMPLATE[action_arg])
        html = render_template_string(
            read_html_template(path),
            session_id=kwargs["session_id"],
            product_info=kwargs["product_info"],
            keywords=kwargs["keywords"],
            page=kwargs["page"],
            asin=kwargs["asin"],
            options=kwargs["options"],
            instruction_text=kwargs.get("instruction_text"),
        )
    elif action_name == "click":
        path = os.path.join(TEMPLATE_DIR, "item_page.html")
        html = render_template_string(
            read_html_template(path),
            session_id=kwargs["session_id"],
            product_info=kwargs["product_info"],
            keywords=kwargs["keywords"],
            page=kwargs["page"],
            asin=kwargs["asin"],
            options=kwargs["options"],
            instruction_text=kwargs.get("instruction_text"),
            show_attrs=kwargs["show_attrs"],
        )
    else:
        raise ValueError("Action name not recognized.")
    return html


def read_html_template(path):
    with open(path) as f:
        template = f.read()
    return template


def parse_action(action):
    """Parse action string to action name and its arguments."""
    pattern = re.compile(r"(.+)\[(.+)\]")
    m = re.match(pattern, action)
    if m is None:
        action_name = action
        action_arg = None
    else:
        action_name, action_arg = m.groups()
    return action_name, action_arg


def convert_web_app_string_to_var(name, string):
    if name == "keywords":
        keywords = string
        if keywords.startswith("["):
            keywords = literal_eval(keywords)
        else:
            keywords = [keywords]
        var = keywords
    elif name == "page":
        page = string
        page = int(page)
        var = page
    else:
        raise ValueError("Name of variable not recognized.")
    return var


def get_top_n_product_from_keywords(
    keywords,
    search_engine,
    all_products,
    product_item_dict,
    attribute_to_asins=None,
):
    if keywords[0] == "<r>":
        top_n_products = random.sample(all_products, k=SEARCH_RETURN_N)
    elif keywords[0] == "<a>":
        attribute = " ".join(keywords[1:]).strip()
        asins = attribute_to_asins[attribute]
        top_n_products = [p for p in all_products if p["asin"] in asins]
    elif keywords[0] == "<c>":
        category = keywords[1].strip()
        top_n_products = [p for p in all_products if p["category"] == category]
    elif keywords[0] == "<q>":
        query = " ".join(keywords[1:]).strip()
        top_n_products = [p for p in all_products if p["query"] == query]
    else:
        keywords = " ".join(keywords)
        hits = search_engine.search(keywords, k=SEARCH_RETURN_N)
        docs = [search_engine.doc(hit.docid) for hit in hits]
        top_n_asins = [json.loads(doc.raw())["id"] for doc in docs]
        top_n_products = [
            product_item_dict[asin] for asin in top_n_asins if asin in product_item_dict
        ]
    return top_n_products


def get_product_per_page(top_n_products, page):
    return top_n_products[(page - 1) * PRODUCT_WINDOW : page * PRODUCT_WINDOW]


def generate_product_prices(all_products):
    product_prices = dict()
    for product in all_products:
        asin = product["asin"]
        pricing = product["pricing"]
        if not pricing:
            price = 100.0
        elif len(pricing) == 1:
            price = pricing[0]
        else:
            price = random.uniform(*pricing[:2])
        product_prices[asin] = price
    return product_prices


def init_search_engine(num_products=None):
    if num_products == 100:
        indexes = "indexes_100"
    elif num_products == 1000:
        indexes = "indexes_1k"
    elif num_products == 10000:
        indexes = "indexes_10k"
    elif num_products == 50000:
        indexes = "indexes_50k"
    elif num_products is None:
        indexes = "indexes_1k"
    else:
        raise NotImplementedError(
            f"num_products being {num_products} is not supported yet."
        )
    search_engine = LuceneSearcher(
        os.path.join(BASE_DIR, f"../search_engine/{indexes}")
    )
    return search_engine


def clean_product_keys(products):
    for product in products:
        product.pop("product_information", None)
        product.pop("brand", None)
        product.pop("brand_url", None)
        product.pop("list_price", None)
        product.pop("availability_quantity", None)
        product.pop("availability_status", None)
        product.pop("total_reviews", None)
        product.pop("total_answered_questions", None)
        product.pop("seller_id", None)
        product.pop("seller_name", None)
        product.pop("fulfilled_by_amazon", None)
        product.pop("fast_track_message", None)
        product.pop("aplus_present", None)
        product.pop("small_description_old", None)
    print("Keys cleaned.")
    return products


def load_products(filepath, num_products=None, human_goals=True):
    # TODO: move to preprocessing step -> enforce single source of truth
    with open(filepath) as f:
        products = json.load(f)
    print("Products loaded.")
    products = clean_product_keys(products)

    # with open(DEFAULT_REVIEW_PATH) as f:
    #     reviews = json.load(f)
    all_reviews = dict()
    all_ratings = dict()
    # for r in reviews:
    #     all_reviews[r['asin']] = r['reviews']
    #     all_ratings[r['asin']] = r['average_rating']

    if human_goals:
        with open(HUMAN_ATTR_PATH) as f:
            human_attributes = json.load(f)
    with open(DEFAULT_ATTR_PATH) as f:
        attributes = json.load(f)
    with open(HUMAN_ATTR_PATH) as f:
        human_attributes = json.load(f)
    print("Attributes loaded.")

    asins = set()
    all_products = []
    attribute_to_asins = defaultdict(set)
    if num_products is not None:
        # using item_shuffle.json, we assume products already shuffled
        products = products[:num_products]
    for i, p in tqdm(enumerate(products), total=len(products)):
        asin = p["asin"]
        if asin == "nan" or len(asin) > 10:
            continue

        if asin in asins:
            continue
        else:
            asins.add(asin)

        products[i]["category"] = p["category"]
        products[i]["query"] = p["query"]
        products[i]["product_category"] = p["product_category"]

        products[i]["Title"] = p["name"]
        products[i]["Description"] = p["full_description"]
        products[i]["Reviews"] = all_reviews.get(asin, [])
        products[i]["Rating"] = all_ratings.get(asin, "N.A.")
        for r in products[i]["Reviews"]:
            if "score" not in r:
                r["score"] = r.pop("stars")
            if "review" not in r:
                r["body"] = ""
            else:
                r["body"] = r.pop("review")
        products[i]["BulletPoints"] = (
            p["small_description"]
            if isinstance(p["small_description"], list)
            else [p["small_description"]]
        )

        pricing = p.get("pricing")
        if pricing is None or not pricing:
            pricing = [100.0]
            price_tag = "$100.0"
        else:
            pricing = [
                float(Decimal(re.sub(r"[^\d.]", "", price)))
                for price in pricing.split("$")[1:]
            ]
            if len(pricing) == 1:
                price_tag = f"${pricing[0]}"
            else:
                price_tag = f"${pricing[0]} to ${pricing[1]}"
                pricing = pricing[:2]
        products[i]["pricing"] = pricing
        products[i]["Price"] = price_tag

        options = dict()
        customization_options = p["customization_options"]
        option_to_image = dict()
        if customization_options:
            for option_name, option_contents in customization_options.items():
                if option_contents is None:
                    continue
                option_name = option_name.lower()

                option_values = []
                for option_content in option_contents:
                    option_value = (
                        option_content["value"].strip().replace("/", " | ").lower()
                    )
                    option_image = option_content.get("image", None)

                    option_values.append(option_value)
                    option_to_image[option_value] = option_image
                options[option_name] = option_values
        products[i]["options"] = options
        products[i]["option_to_image"] = option_to_image

        # without color, size, price, availability
        # if asin in attributes and 'attributes' in attributes[asin]:
        #     products[i]['Attributes'] = attributes[asin]['attributes']
        # else:
        #     products[i]['Attributes'] = ['DUMMY_ATTR']
        # products[i]['instruction_text'] = \
        #     attributes[asin].get('instruction', None)
        # products[i]['instruction_attributes'] = \
        #     attributes[asin].get('instruction_attributes', None)

        # without color, size, price, availability
        if asin in attributes and "attributes" in attributes[asin]:
            products[i]["Attributes"] = attributes[asin]["attributes"]
        else:
            products[i]["Attributes"] = ["DUMMY_ATTR"]

        if human_goals:
            if asin in human_attributes:
                products[i]["instructions"] = human_attributes[asin]
        else:
            products[i]["instruction_text"] = attributes[asin].get("instruction", None)

            products[i]["instruction_attributes"] = attributes[asin].get(
                "instruction_attributes", None
            )

        products[i]["MainImage"] = p["images"][0]
        products[i]["query"] = p["query"].lower().strip()

        all_products.append(products[i])

    for p in all_products:
        for a in p["Attributes"]:
            attribute_to_asins[a].add(p["asin"])

    product_item_dict = {p["asin"]: p for p in all_products}
    product_prices = generate_product_prices(all_products)
    return all_products, product_item_dict, product_prices, attribute_to_asins

```


---

## 文件: personalized-shopping\personalized_shopping\shared_libraries\web_agent_site\engine\goal.py

```python
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

"""Functions for specifying goals and reward calculations."""

from collections import defaultdict
import itertools
import random
from rich import print
import spacy
from thefuzz import fuzz
from .normalize import normalize_color

nlp = spacy.load("en_core_web_sm")

PRICE_RANGE = [10.0 * i for i in range(1, 100)]


def get_goals(all_products, product_prices, human_goals=True):
    if human_goals:
        return get_human_goals(all_products, product_prices)
    else:
        return get_synthetic_goals(all_products, product_prices)


def get_human_goals(all_products, product_prices):
    goals = []
    cnt_atts = defaultdict(int)
    cnt = 0
    for item in all_products:
        asin = item["asin"]
        if "instructions" not in item:
            continue
        for product in item["instructions"]:
            attributes = product["instruction_attributes"]
            if len(attributes) == 0:
                cnt += 1
                continue

            if product_prices is not None:
                price = product_prices[asin]
                price_range = [p for p in PRICE_RANGE if p > price][:4]
                if len(price_range) >= 2:
                    _, price_upper = sorted(random.sample(price_range, 2))
                    price_text = f", and price lower than {price_upper:.2f} dollars"
                else:
                    price_upper = 1000000
                    price_text = ""
            else:
                price_upper = 1000000

            goals.append(
                {
                    "asin": asin,
                    "category": item["category"],
                    "query": item["query"],
                    "name": item["name"],
                    "product_category": item["product_category"],
                    "instruction_text": product["instruction"].strip(".") + price_text,
                    "attributes": attributes,
                    "price_upper": price_upper,
                    "goal_options": product["instruction_options"],
                }
            )
            for att in attributes:
                cnt_atts[att] += 1
            # goals += product_goals
    for goal in goals:
        goal["weight"] = 1
    print(cnt, "skipped")
    return goals


def get_synthetic_goals(all_products, product_prices):
    goals = []
    cnt_atts = defaultdict(int)
    for product in all_products:
        if "instruction_text" not in product or product["instruction_text"] is None:
            continue
        product_goals = []
        asin = product["asin"]
        attributes = product["instruction_attributes"]
        assert len(attributes) > 0

        if product_prices is not None:
            price = product_prices[asin]
            price_range = [p for p in PRICE_RANGE if p > price][:4]
            if len(price_range) >= 2:
                _, price_upper = sorted(random.sample(price_range, 2))
                price_text = f", and price lower than {price_upper:.2f} dollars"
            else:
                price_upper = 1000000
                price_text = ""
        else:
            price_upper = 1000000
            price_text = ""

        instruction_text = product["instruction_text"]

        options = product["options"]
        option_names = sorted(options)
        combinations = list(
            itertools.product(*(options[option_name] for option_name in option_names))
        )
        for combination in combinations:
            goal_options = dict()
            for i, o in enumerate(combination):
                #                option_text.append(f'{option_names[i]}: {o}')
                goal_options[option_names[i]] = o
            option_text = ", and ".join([f"{k}: {v}" for k, v in goal_options.items()])
            option_text = " with " + option_text if option_text else ""
            product_goals.append(
                {
                    "asin": asin,
                    "category": product["category"],
                    "query": product["query"],
                    "name": product["name"],
                    "product_category": product["product_category"],
                    "instruction_text": f"{instruction_text}{option_text}{price_text}",
                    "attributes": attributes,
                    "price_upper": price_upper,
                    "goal_options": goal_options,
                    "name": product["Title"],
                }
            )
            for att in attributes:
                cnt_atts[att] += 1
        goals += product_goals
    for goal in goals:
        goal["weight"] = sum(1.0 / cnt_atts[att] for att in goal["attributes"]) / len(
            goal["attributes"]
        )
    return goals


def get_type_reward(purchased_product, goal):
    """Determines the type reward - captures whether chosen product is in the same category"""
    query_match = purchased_product["query"] == goal["query"]

    # Check number of unique categories that match, ignoring order
    purchased_product_category = [
        x.strip() for x in purchased_product["product_category"].split("›")
    ]
    goal_product_category = [x.strip() for x in goal["product_category"].split("›")]
    category_match = (
        len(set(purchased_product_category) & set(goal_product_category)) >= 2
    )

    # Determine whether types align based on product name similarity
    purchased_type = purchased_product["name"]
    desired_type = goal["name"]

    purchased_type_parse = nlp(purchased_type)
    desired_type_parse = nlp(desired_type)

    purchased_type_parse = [
        t.text.lower()
        for t in purchased_type_parse
        if t.pos_ in ("PNOUN", "NOUN", "PROPN")
    ]
    desired_type_parse = [
        t.text.lower()
        for t in desired_type_parse
        if t.pos_ in ("PNOUN", "NOUN", "PROPN")
    ]

    n_intersect_type = len(set(purchased_type_parse) & set(desired_type_parse))
    if len(desired_type_parse) == 0:
        title_score = 0.2
    else:
        title_score = n_intersect_type / len(desired_type_parse)

    r_type = 1.0

    # Adjust r_type score based on query, category title matching/scores
    match = query_match or category_match or title_score > 0.2
    if not match:
        r_type = 0.5

    if title_score < 0.1:
        r_type = 0.1

    if title_score == 0.0:
        r_type = 0.0

    return dict(
        r_type=r_type,
        query_match=query_match,
        category_match=category_match,
        title_score=title_score,
    )


def get_attribute_reward(purchased_product, goal):
    """Determines whether purchased products shares same attributes as goal"""
    purchased_attrs = purchased_product["Attributes"]
    goal_attrs = goal["attributes"]

    num_attr_matches = 0
    for g_attr in goal_attrs:
        matched = False
        # Check whether goal attribute found in purchased product attribute list
        for p_attr in purchased_attrs:
            score = fuzz.token_set_ratio(p_attr, g_attr)
            if score > 85:
                num_attr_matches += 1
                matched = True
                break
        # If not in purchased attrs, check Title, Bullet Points (Features), Desc
        if not matched and (
            g_attr in purchased_product["Title"].lower()
            or g_attr in " ".join(purchased_product["BulletPoints"]).lower()
            or g_attr in purchased_product["Description"].lower()
        ):
            num_attr_matches += 1
            matched = True

    r_attr = num_attr_matches / len(goal_attrs)
    return r_attr, num_attr_matches


def get_option_reward(purchased_options, goal_options):
    """Calculate reward for purchased product's options w.r.t. goal options"""
    purchased_options = [normalize_color(o) for o in purchased_options]
    goal_options = [normalize_color(o) for o in goal_options]

    # Perform fuzzy matching of each purchased option against each goal option
    num_option_matches = 0
    for g_option in goal_options:
        for p_option in purchased_options:
            score = fuzz.token_set_ratio(p_option, g_option)
            if score > 85:
                num_option_matches += 1
                break

    # Calculate option reward as fraction of goal options hit
    r_option = num_option_matches / len(goal_options) if len(goal_options) > 0 else None
    return r_option, num_option_matches


def get_reward(purchased_product, goal, price, options, **kwargs):
    """Get cumulative reward score for purchased product and goal"""
    r_type_dict = get_type_reward(purchased_product, goal)

    r_price = (price <= goal["price_upper"]) if goal["price_upper"] > 0 else None

    r_att, num_attr_matches = get_attribute_reward(purchased_product, goal)

    r_option, num_option_matches = get_option_reward(
        list(options.values()),
        (
            goal["goal_options"].items()
            if isinstance(goal["goal_options"], dict)
            else goal["goal_options"]
        ),
    )

    total_reward = (num_attr_matches + num_option_matches + r_price) / (
        len(goal["attributes"]) + len(goal["goal_options"]) + 1
    )

    total_reward *= r_type_dict["r_type"]

    # If verbose flag enabled, store score sub-components into dictionary
    if kwargs.get("verbose", False):
        info = {
            "r_type": r_type_dict["r_type"],
            "r_att": r_att,
            "w_att": len(goal["attributes"])
            / (len(goal["attributes"]) + len(goal["goal_options"]) + 1),
            "query_match": r_type_dict["query_match"],
            "category_match": r_type_dict["category_match"],
            "title_score": r_type_dict["title_score"],
        }
        if r_option is not None:
            info["r_option"] = r_option
            info["w_option"] = len(goal["goal_options"]) / (
                len(goal["attributes"]) + len(goal["goal_options"]) + 1
            )
        if r_price is not None:
            info["r_price"] = r_price
            info["w_price"] = 1 / (
                len(goal["attributes"]) + len(goal["goal_options"]) + 1
            )
        return total_reward, info
    return total_reward

```


---

## 文件: personalized-shopping\personalized_shopping\shared_libraries\web_agent_site\engine\normalize.py

```python
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

import re
from typing import Tuple

COLOR_SET = [
    "alabaster",
    "apricot",
    "aqua",
    "ash",
    "asphalt",
    "azure",
    "banana",
    "beige",
    "black",
    "blue",
    "blush",
    "bordeaux",
    "bronze",
    "brown",
    "burgundy",
    "camel",
    "camo",
    "caramel",
    "champagne",
    "charcoal",
    "cheetah",
    "chestnut",
    "chocolate",
    "christmas",
    "coffee",
    "cognac",
    "copper",
    "coral",
    "cranberry",
    "cream",
    "crystal",
    "dark",
    "denim",
    "eggplant",
    "elephant",
    "espresso",
    "fuchsia",
    "gold",
    "granite",
    "grape",
    "graphite",
    "grass",
    "gray",
    "green",
    "grey",
    "heather",
    "indigo",
    "ivory",
    "ivy",
    "khaki",
    "lavender",
    "lemon",
    "leopard",
    "light",
    "lilac",
    "lime",
    "magenta",
    "maroon",
    "mauve",
    "merlot",
    "midnight",
    "mint",
    "mocha",
    "multicolor",
    "mushroom",
    "mustard",
    "natural",
    "navy",
    "nude",
    "olive",
    "orange",
    "peach",
    "pewter",
    "pink",
    "plum",
    "purple",
    "rainbow",
    "red",
    "rose",
    "royal",
    "rust",
    "sand",
    "sapphire",
    "seashell",
    "silver",
    "skull",
    "slate",
    "steel",
    "stone",
    "stonewash",
    "sunflower",
    "tan",
    "taupe",
    "teal",
    "tiger",
    "turquoise",
    "violet",
    "walnut",
    "wheat",
    "white",
    "wine",
    "yellow",
]

SIZE_SET = [
    "xx-large",
    "3x-large",
    "4x-large",
    "5x-large",
    "x-large",
    "x-small",
    "medium",
    "large",
    "small",
    "queen",
    "twin",
    "full",
    "king",
    "one size",
    "pack",
]

SIZE_PATTERNS = [
    re.compile(r"(.*)neck(.*)sleeve"),
    re.compile(r"(.*) women \| (.*) men"),
    re.compile(r"(.*)w x(.*)l"),
    re.compile(r"(.*)w by (.*)l"),
    re.compile(r"(.*)w x(.*)h"),
    re.compile(r"(.*)wide"),
    re.compile(r"(.*)x-wide"),
    re.compile(r"(.*)narrow"),
    re.compile(r"(.*)petite"),
    re.compile(r"(.*)inch"),
    re.compile(r"(.*)plus"),
    re.compile(r"(.*)mm"),
    re.compile(r"women(.*)"),
    re.compile(r"(.*)x(.*)"),
    re.compile(r"(.*)ft"),
    re.compile(r"(.*)feet"),
    re.compile(r"(.*)meter"),
    re.compile(r"(.*)yards"),
    re.compile(r"(.*)\*(.*)"),
    re.compile(r"(.*)\-(.*)"),
    re.compile(r'(\d+)"$'),
    re.compile(r"(\d+)f$"),
    re.compile(r"(\d+)m$"),
    re.compile(r"(\d+)cm$"),
    re.compile(r"(\d+)g$"),
]
SIZE_PATTERNS = [re.compile(s) for s in SIZE_SET] + SIZE_PATTERNS


def normalize_color(color_string: str) -> str:
    """Extracts the first color found if exists"""
    for norm_color in COLOR_SET:
        if norm_color in color_string:
            return norm_color
    return color_string


def normalize_color_size(product_prices: dict) -> Tuple[dict, dict]:
    """Get mappings of all colors, sizes to corresponding values in COLOR_SET, SIZE_PATTERNS"""

    # Get all colors, sizes from list of all products
    all_colors, all_sizes = set(), set()
    for (_, color, size), _ in product_prices.items():
        all_colors.add(color.lower())
        all_sizes.add(size.lower())

    # Create mapping of each original color value to corresponding set value
    color_mapping = {"N.A.": "not_matched"}
    for c in all_colors:
        matched = False
        for base in COLOR_SET:
            if base in c:
                color_mapping[c] = base
                matched = True
                break
        if not matched:
            color_mapping[c] = "not_matched"

    # Create mapping of each original size value to corresponding set value
    size_mapping = {"N.A.": "not_matched"}
    for s in all_sizes:
        matched = False
        for pattern in SIZE_PATTERNS:
            m = re.search(pattern, s)
            if m is not None:
                matched = True
                size_mapping[s] = pattern.pattern
                break
        if not matched:
            if s.replace(".", "", 1).isdigit():
                size_mapping[s] = "numeric_size"
                matched = True
        if not matched:
            size_mapping[s] = "not_matched"

    return color_mapping, size_mapping

```


---

## 文件: personalized-shopping\personalized_shopping\shared_libraries\web_agent_site\envs\web_agent_text_env.py

```python
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

from collections import defaultdict
import json
import random
import string
import time
from bs4 import BeautifulSoup
from bs4.element import Comment
from flask import Flask
import gym
from gym.envs.registration import register
import numpy as np
import torch
from ..engine.engine import (
    ACTION_TO_TEMPLATE,
    BACK_TO_SEARCH,
    END_BUTTON,
    NEXT_PAGE,
    PREV_PAGE,
    get_product_per_page,
    get_top_n_product_from_keywords,
    init_search_engine,
    load_products,
    map_action_to_html,
    parse_action,
)
from ..engine.goal import get_goals, get_reward
from ..utils import (
    DEFAULT_FILE_PATH,
    FEAT_CONV,
    FEAT_IDS,
    random_idx,
)


app = Flask(__name__)


class WebAgentTextEnv(gym.Env):
    """Gym environment for Text mode of WebShop environment"""

    def __init__(
        self,
        observation_mode="html",
        file_path=DEFAULT_FILE_PATH,
        server=None,
        **kwargs,
    ):
        """Constructor for text environment

        Arguments:

        observation_mode (`str`) -- ['html' | 'text'] (default 'html')
        get_image
        filter_goals
        limit_goals
        num_products
        human_goals
        session
        session_prefix
        show_attrs
        """
        super(WebAgentTextEnv, self).__init__()
        self.observation_mode = observation_mode
        self.kwargs = kwargs

        self.file_path = file_path

        self.base_url = "http://127.0.0.1:3000"
        self.server = (
            SimServer(
                self.base_url,
                self.file_path,
                self.kwargs.get("filter_goals"),
                self.kwargs.get("limit_goals", -1),
                self.kwargs.get("num_products"),
                self.kwargs.get("human_goals"),
                self.kwargs.get("show_attrs", False),
            )
            if server is None
            else server
        )
        self.browser = SimBrowser(self.server)

        self.session = self.kwargs.get("session")
        self.session_prefix = self.kwargs.get("session_prefix")
        if self.kwargs.get("get_image", 0):
            self.feats = torch.load(FEAT_CONV)
            self.ids = torch.load(FEAT_IDS)
            self.ids = {url: idx for idx, url in enumerate(self.ids)}
        self.prev_obs = []
        self.prev_actions = []
        self.num_prev_obs = self.kwargs.get("num_prev_obs", 0)
        self.num_prev_actions = self.kwargs.get("num_prev_actions", 0)
        self.reset()

    def step(self, action):
        """Takes an action, updates WebShop environment, and returns (observation, reward, done, info)

        Arguments:

        action (`str`): An action should be of the following structure:
          - search[keywords]
          - click[value]
        If action not valid, perform nothing.
        """
        info = None
        self.get_available_actions()

        # Determine action type (click, search) and argument
        action_name, action_arg = parse_action(action)
        if action_arg is not None:
            action_arg = action_arg.lower()
        if action_name == "search" and action_arg is not None and action_arg != "":
            status = self.browser.search(action_arg)
        elif (
            action_name == "click"
            and action_arg in self.text_to_clickable.keys()
            and action_arg != "search"
        ):
            status = self.browser.click(action_arg, self.text_to_clickable)
        else:
            status = dict(reward=0, done=False)

        # Update observation, state with the new action
        ob = self.observation
        text_list = [ob]
        self.prev_actions.append(action)
        for i in range(1, 1 + max(self.num_prev_obs, self.num_prev_actions)):
            if len(self.prev_actions) >= i and self.num_prev_actions >= i:
                text_list.append(self.prev_actions[-i])
            if len(self.prev_obs) >= i and self.num_prev_obs >= i:
                text_list.append(self.prev_obs[-i])
        state = " [SEP] ".join(text_list[::-1])
        self.prev_obs.append(ob)
        return state, status["reward"], status["done"], info

    def get_available_actions(self):
        """Returns list of available actions at the current step"""
        html_obj = self._parse_html()

        # Collect search bar, buttons, links, and options as clickables
        search_bar = html_obj.find(id="search_input")
        has_search_bar = True if search_bar is not None else False
        buttons = html_obj.find_all(class_="btn")
        product_links = html_obj.find_all(class_="product-link")
        buying_options = html_obj.select('input[type="radio"]')

        self.text_to_clickable = {
            f"{b.get_text()}".lower(): b for b in buttons + product_links
        }
        for opt in buying_options:
            opt_value = opt.get("value")
            self.text_to_clickable[f"{opt_value}"] = opt
        return dict(
            has_search_bar=has_search_bar,
            clickables=list(self.text_to_clickable.keys()),
        )

    def get_image(self):
        """Scrape image from page HTML and return as a list of pixel values"""
        html_obj = self._parse_html(self.browser.page_source)
        image_url = html_obj.find(id="product-image")
        if image_url is not None:
            image_url = image_url["src"]
            if image_url in self.ids:
                image_idx = self.ids[image_url]
                image = self.feats[image_idx]
                return image
        return torch.zeros(512)

    def get_instruction_text(self):
        """Get corresponding instruction text for current environment session"""
        html_obj = self._parse_html(self.browser.page_source)
        instruction_text = html_obj.find(id="instruction-text").h4.text
        return instruction_text

    def _parse_html(self, html=None):
        """Returns web request result wrapped in BeautifulSoup object

        Arguments:

        url (`str`): If no url or html is provided, use the current
            observation (HTML) for parsing.
        """
        if html is None:
            html = self.state["html"]
        html_obj = BeautifulSoup(html, "html.parser")
        return html_obj

    @property
    def observation(self):
        """Compiles state into either the `html` or `text` observation mode"""
        html = self.state["html"]
        if self.observation_mode == "html":
            return html
        elif self.observation_mode == "text":
            return self.convert_html_to_text(html, simple=True)
        elif self.observation_mode == "text_rich":
            return self.convert_html_to_text(html, simple=False)
        elif self.observation_mode == "url":
            return self.state["url"]
        else:
            raise ValueError(f"Observation mode {self.observation_mode} not supported.")

    @property
    def state(self):
        """State that includes all information.

        The actual observation are likely to be a subset or reduced form of the
        state.
        """
        return dict(
            url=self.browser.current_url,
            html=self.browser.page_source,
            instruction_text=self.instruction_text,
        )

    def convert_html_to_text(self, html, simple=False):
        """Strip HTML of tags and add separators to convert observation into simple mode"""
        texts = self._parse_html(html).findAll(text=True)
        visible_texts = filter(tag_visible, texts)
        if simple:
            # For `simple` mode, return just [SEP] separators
            return " [SEP] ".join(t.strip() for t in visible_texts if t != "\n")
        else:
            # Otherwise, return an observation with tags mapped to specific, unique separators
            observation = ""
            for t in visible_texts:
                if t == "\n":
                    continue
                if t.parent.name == "button":  # button
                    processed_t = f"[button] {t} [button_]"
                elif t.parent.name == "label":  # options
                    if f'"{t}"' in self.state["url"]:
                        processed_t = f"  [clicked button] {t} [clicked button_]"
                        observation = f"You have clicked {t}.\n" + observation
                    else:
                        processed_t = f"  [button] {t} [button_]"
                elif t.parent.get("class") == ["product-link"]:  # product asins
                    if f"{t}" in self.server.user_sessions[self.session]["asins"]:
                        processed_t = f"\n[clicked button] {t} [clicked button_]"
                    else:
                        processed_t = f"\n[button] {t} [button_]"
                else:  # regular, unclickable text
                    processed_t = str(t)
                observation += processed_t + "\n"
            return observation

    def reset(self, session=None, instruction_text=None):
        """Create a new session and reset environment variables"""
        session_int = None
        if session is not None:
            self.session = str(session)
            if isinstance(session, int):
                session_int = session
        else:
            self.session = "".join(random.choices(string.ascii_lowercase, k=10))
        if self.session_prefix is not None:
            self.session = self.session_prefix + self.session

        init_url = f"{self.base_url}/{self.session}"
        self.browser.get(init_url, session_id=self.session, session_int=session_int)

        self.text_to_clickable = None
        self.instruction_text = (
            self.get_instruction_text()
            if instruction_text is None
            else instruction_text
        )
        obs = self.observation
        self.prev_obs = [obs]
        self.prev_actions = []
        return obs, None

    def render(self, mode="human"):
        pass

    def close(self):
        pass


def tag_visible(element):
    ignore = {"style", "script", "head", "title", "meta", "[document]"}
    return element.parent.name not in ignore and not isinstance(element, Comment)


class SimServer:
    """Lightweight simulator of WebShop Flask application for generating HTML observations"""

    def __init__(
        self,
        base_url,
        file_path,
        filter_goals=None,
        limit_goals=-1,
        num_products=None,
        human_goals=0,
        show_attrs=False,
    ):
        """Constructor for simulated server serving WebShop application

        Arguments:

        filter_goals (`func`) -- Select specific goal(s) for consideration based on
          criteria of custom function
        limit_goals (`int`) -- Limit to number of goals available
        num_products (`int`) -- Number of products to search across
        human_goals (`bool`) -- If true, load human goals; otherwise, load synthetic
          goals
        """
        # Load all products, goals, and search engine
        self.base_url = base_url
        self.all_products, self.product_item_dict, self.product_prices, _ = (
            load_products(
                filepath=file_path,
                num_products=num_products,
                human_goals=human_goals,
            )
        )
        self.search_engine = init_search_engine(num_products=num_products)
        self.goals = get_goals(self.all_products, self.product_prices, human_goals)
        self.show_attrs = show_attrs

        # Fix outcome for random shuffling of goals
        random.seed(233)
        random.shuffle(self.goals)

        # Apply `filter_goals` parameter if exists to select speific goal(s)
        if filter_goals is not None:
            self.goals = [
                goal for (i, goal) in enumerate(self.goals) if filter_goals(i, goal)
            ]

        # Imposes `limit` on goals via random selection
        if limit_goals != -1 and limit_goals < len(self.goals):
            self.weights = [goal["weight"] for goal in self.goals]
            self.cum_weights = [0] + np.cumsum(self.weights).tolist()
            idxs = []
            while len(idxs) < limit_goals:
                idx = random_idx(self.cum_weights)
                if idx not in idxs:
                    idxs.append(idx)
            self.goals = [self.goals[i] for i in idxs]
        print(f"Loaded {len(self.goals)} goals.")

        # Set extraneous housekeeping variables
        self.weights = [goal["weight"] for goal in self.goals]
        self.cum_weights = [0] + np.cumsum(self.weights).tolist()
        self.user_sessions = dict()
        self.search_time = 0
        self.render_time = 0
        self.sample_time = 0
        self.assigned_instruction_text = None  # TODO: very hacky, should remove

    @app.route("/", methods=["GET", "POST"])
    def index(self, session_id, **kwargs):
        """Redirect to the search page with the given session ID"""
        html = map_action_to_html(
            "start",
            session_id=session_id,
            instruction_text=kwargs["instruction_text"],
        )
        url = f"{self.base_url}/{session_id}"
        return html, url

    @app.route("/", methods=["GET", "POST"])
    def search_results(self, session_id, **kwargs):
        """Initialize session and return the search results page"""
        session = self.user_sessions[session_id]
        keywords = kwargs[
            "keywords"
        ]  # TODO: why is this using kwargs? why not session?
        assert isinstance(keywords, list)
        page = 1 if "page" not in kwargs else kwargs["page"]
        session["page"] = page
        session["keywords"] = keywords
        session["actions"]["search"] += 1
        session["asin"] = None
        session["options"] = {}

        # Perform search on keywords from items and record amount of time it takes
        old_time = time.time()
        top_n_products = get_top_n_product_from_keywords(
            keywords,
            self.search_engine,
            self.all_products,
            self.product_item_dict,
        )
        self.search_time += time.time() - old_time

        # Get product list from search result asins and get list of corresponding URLs
        products = get_product_per_page(top_n_products, page)

        keywords_url_string = "+".join(keywords)
        url = (
            f"{self.base_url}/search_results/{session_id}/"
            f"{keywords_url_string}/{page}"
        )

        # Render HTML search page and record amount of time taken
        old_time = time.time()
        html = map_action_to_html(
            "search",
            session_id=session_id,
            products=products,
            keywords=session["keywords"],
            page=page,
            total=len(top_n_products),
            # This is used for reward computation
            # instruction_text=session['goal']['instruction_text'],
            # This is used for rendering the page
            instruction_text=self.assigned_instruction_text,
        )
        self.render_time += time.time() - old_time
        return html, url

    @app.route("/", methods=["GET", "POST"])
    def item_page(self, session_id, **kwargs):
        """Render and return the HTML for a product item page"""
        session = self.user_sessions[session_id]
        clickable_name = kwargs["clickable_name"]
        text_to_clickable = kwargs["text_to_clickable"]
        clickable = text_to_clickable[clickable_name]

        # Update session logs with information of last product asin selected
        if (
            clickable.get("class") is not None
            and clickable.get("class")[0] == "product-link"
        ):
            session["asin"] = clickable_name.upper()
            session["actions"]["asin"] += 1
            session["asins"].add(session["asin"])
        elif clickable.get("name") is not None:
            clickable_key = clickable["name"].lower()
            session["options"][clickable_key] = clickable_name
            session["actions"]["options"] += 1

        # Set fields + url of page, then render page's HTML
        product_info = self.product_item_dict[session["asin"]]
        keywords_url_string = "+".join(session["keywords"])
        option_string = json.dumps(session["options"])

        url = (
            f"{self.base_url}/item_page/{session_id}/"
            f'{session["asin"]}/{keywords_url_string}/'
            f'{session["page"]}/{option_string}'
        )

        html = map_action_to_html(
            "click",
            session_id=session_id,
            product_info=product_info,
            keywords=session["keywords"],
            page=session["page"],
            asin=session["asin"],
            options=session["options"],
            # This is used for reward computation
            # instruction_text=session['goal']['instruction_text'],
            # This is used for rendering the page
            instruction_text=self.assigned_instruction_text,
            show_attrs=self.show_attrs,
        )
        return html, url

    @app.route("/", methods=["GET", "POST"])
    def item_sub_page(self, session_id, **kwargs):
        """Render and return the HTML for a product's sub page (i.e.

        description, features)
        """
        session = self.user_sessions[session_id]
        clickable_name = kwargs["clickable_name"]
        for k in ACTION_TO_TEMPLATE:
            if clickable_name.lower() == k.lower():
                clickable_name = k
                break

        # Set fields + url of page, then render page's HTML
        product_info = self.product_item_dict[session["asin"]]
        session["actions"][clickable_name] += 1
        keywords_url_string = "+".join(session["keywords"])
        url = (
            f"{self.base_url}/item_sub_page/{session_id}/"
            f'{session["asin"]}/{keywords_url_string}/{session["page"]}/'
            f'{clickable_name}/{session["options"]}'
        )
        html = map_action_to_html(
            f"click[{clickable_name}]",
            session_id=session_id,
            product_info=product_info,
            keywords=session["keywords"],
            page=session["page"],
            asin=session["asin"],
            options=session["options"],
            # This is used for reward computation
            # instruction_text=session['goal']['instruction_text'],
            # This is used for rendering the page
            instruction_text=self.assigned_instruction_text,
        )
        return html, url

    @app.route("/", methods=["GET", "POST"])
    def done(self, session_id, **kwargs):
        """Render and return HTML for done page"""
        session = self.user_sessions[session_id]
        goal = self.user_sessions[session_id]["goal"]
        purchased_product = self.product_item_dict[session["asin"]]
        session["actions"]["purchase"] += 1
        price = self.product_prices.get(session["asin"])

        # Calculate reward for selected product and set variables for page details
        reward, info = get_reward(
            purchased_product,
            goal,
            price=price,
            options=session["options"],
            verbose=True,
        )

        self.user_sessions[session_id]["verbose_info"] = info
        self.user_sessions[session_id]["done"] = True
        self.user_sessions[session_id]["reward"] = reward

        url = (
            f"{self.base_url}/done/{session_id}/"
            f'{session["asin"]}/{session["options"]}'
        )
        html = map_action_to_html(
            f"click[{END_BUTTON}]",
            session_id=session_id,
            reward=reward,
            asin=session["asin"],
            options=session["options"],
            # This is used for reward computation
            # instruction_text=session['goal']['instruction_text'],
            # This is used for rendering the page
            instruction_text=self.assigned_instruction_text,
        )
        return html, url, reward

    def receive(self, session_id, current_url, session_int=None, **kwargs):
        """Map action to the corresponding page"""
        status = dict(reward=0.0, done=False)

        with app.app_context(), app.test_request_context():
            # Create/determine goal, instruction_text from current session
            if session_id not in self.user_sessions:
                idx = (
                    session_int
                    if (session_int is not None and isinstance(session_int, int))
                    else random_idx(self.cum_weights)
                )
                goal = self.goals[idx]
                instruction_text = goal["instruction_text"]
                self.user_sessions[session_id] = {"goal": goal, "done": False}
            else:
                instruction_text = self.user_sessions[session_id]["goal"][
                    "instruction_text"
                ]
            if self.assigned_instruction_text is not None:
                instruction_text = (
                    self.assigned_instruction_text
                )  # TODO: very hacky, should remove
                self.user_sessions[session_id]["goal"][
                    "instruction_text"
                ] = instruction_text
            session = self.user_sessions[session_id]

            if not kwargs:
                # If no action, reset the session variables
                kwargs["instruction_text"] = instruction_text
                html, url = self.index(session_id, **kwargs)
                self.user_sessions[session_id].update(
                    {
                        "keywords": None,
                        "page": None,
                        "asin": None,
                        "asins": set(),
                        "options": dict(),
                        "actions": defaultdict(int),
                    }
                )
            elif "keywords" in kwargs:
                # If search keywords are available, run a search
                html, url = self.search_results(session_id, **kwargs)
            elif "clickable_name" in kwargs:
                clickable_name = kwargs["clickable_name"].lower()
                if clickable_name == END_BUTTON.lower():
                    # If "buy now" clicked, calculate reward and flag session as terminated
                    html, url, reward = self.done(session_id, **kwargs)
                    status["reward"] = reward
                    status["done"] = True
                elif clickable_name == BACK_TO_SEARCH.lower():
                    # If "back to search" clicked, recursively reset the session back to search page
                    html, url, status = self.receive(session_id, current_url)
                elif (
                    clickable_name == NEXT_PAGE.lower()
                    and self.get_page_name(current_url) == "search_results"
                ):
                    # If "next page" clicked from search results, re-render with `page` enumerated
                    html, url, status = self.receive(
                        session_id,
                        current_url,
                        keywords=session["keywords"],
                        page=session["page"] + 1,
                    )
                elif (
                    clickable_name == PREV_PAGE.lower()
                    and self.get_page_name(current_url) == "search_results"
                ):
                    # If "prev page" clicked from search results, re-render with `page` denumerated
                    html, url, status = self.receive(
                        session_id,
                        current_url,
                        keywords=session["keywords"],
                        page=session["page"] - 1,
                    )
                elif (
                    clickable_name == PREV_PAGE.lower()
                    and self.get_page_name(current_url) == "item_sub_page"
                ):
                    # If "prev page" clicked from sub page, return to corresponding item page
                    html, url = self.item_page(session_id, **kwargs)
                elif (
                    clickable_name == PREV_PAGE.lower()
                    and self.get_page_name(current_url) == "item_page"
                ):
                    # If "prev page" clicked from item page, return to search results page
                    html, url = self.search_results(
                        session_id,
                        keywords=session["keywords"],
                        page=session["page"],
                        **kwargs,
                    )
                elif clickable_name in [k.lower() for k in ACTION_TO_TEMPLATE]:
                    # Render item_sub_page if clickable is description, features, or reviews
                    html, url = self.item_sub_page(session_id, **kwargs)
                else:
                    # Otherwise, render current item page
                    html, url = self.item_page(session_id, **kwargs)
            return html, url, status

    def get_page_name(self, url):
        """Determine which page (i.e.

        item_page, search_results) the given URL is pointing at.
        """
        if url is None:
            return None
        page_names = ["search_results", "item_page", "item_sub_page", "done"]
        for page_name in page_names:
            if page_name in url:
                return page_name
        return ""  # index page


class SimBrowser:
    """Simulated browser for rendering the HTML source of WebShop environment pages."""

    def __init__(self, server):
        self.server = server
        self.current_url = None
        self.page_source = None
        self.session_id = None

    def get(self, url, session_id=None, session_int=None):
        """Set browser variables to corresponding link, page HTML for URL"""
        self.session_id = url.split("/")[-1] if session_id is None else session_id
        self.page_source, _, _ = self.server.receive(
            self.session_id, self.current_url, session_int=session_int
        )
        self.current_url = url

    def click(self, clickable_name, text_to_clickable):
        """Wrapper for `receive` handler for performing click action on current page"""
        self.page_source, self.current_url, status = self.server.receive(
            self.session_id,
            current_url=self.current_url,
            clickable_name=clickable_name,
            text_to_clickable=text_to_clickable,
        )
        return status

    def search(self, keywords):
        """Wrapper for `receive` handler for performing search action on current page"""
        if isinstance(keywords, str):
            keywords = keywords.split(" ")
        self.page_source, self.current_url, status = self.server.receive(
            self.session_id,
            current_url=self.current_url,
            keywords=keywords,
        )
        return status


register(
    id="WebAgentTextEnv-v0",
    entry_point=(
        "personalized_shopping.shared_libraries.web_agent_site.envs.web_agent_text_env:WebAgentTextEnv"
    ),
)

```


---

## 文件: personalized-shopping\personalized_shopping\tools\click.py

```python
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

from google.adk.tools import ToolContext
from google.genai import types

from ..shared_libraries.init_env import webshop_env


def click(button_name: str, tool_context: ToolContext) -> str:
    """Click the button with the given name.

    Args:
      button_name(str): The name of the button to click.
      tool_context(ToolContext): The function context.

    Returns:
      str: The webpage after clicking the button.
    """
    status = {"reward": None, "done": False}
    action_string = f"click[{button_name}]"
    _, status["reward"], status["done"], _ = webshop_env.step(action_string)

    ob = webshop_env.observation
    index = ob.find("Back to Search")
    if index >= 0:
        ob = ob[index:]

    print("#" * 50)
    print("Click result:")
    print(f"status: {status}")
    print(f"observation: {ob}")
    print("#" * 50)

    if button_name == "Back to Search":
        webshop_env.server.assigned_instruction_text = "Back to Search"

    # Show artifact in the UI.
    tool_context.save_artifact(
        f"html",
        types.Part.from_uri(file_uri=webshop_env.state["html"], mime_type="text/html"),
    )
    return ob

```


---

## 文件: personalized-shopping\personalized_shopping\tools\search.py

```python
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

from google.adk.tools import ToolContext
from google.genai import types

from ..shared_libraries.init_env import webshop_env


def search(keywords: str, tool_context: ToolContext) -> str:
    """Search for keywords in the webshop.

    Args:
      keywords(str): The keywords to search for.
      tool_context(ToolContext): The function context.

    Returns:
      str: The search result displayed in a webpage.
    """
    status = {"reward": None, "done": False}
    action_string = f"search[{keywords}]"
    webshop_env.server.assigned_instruction_text = f"Find me {keywords}."
    print(f"env instruction_text: {webshop_env.instruction_text}")
    _, status["reward"], status["done"], _ = webshop_env.step(action_string)

    ob = webshop_env.observation
    index = ob.find("Back to Search")
    if index >= 0:
        ob = ob[index:]

    print("#" * 50)
    print("Search result:")
    print(f"status: {status}")
    print(f"observation: {ob}")
    print("#" * 50)

    # Show artifact in the UI.
    tool_context.save_artifact(
        f"html",
        types.Part.from_uri(file_uri=webshop_env.state["html"], mime_type="text/html"),
    )
    return ob

```


---

## 文件: personalized-shopping\tests\test_tools.py

```python
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

import os

from google.adk.evaluation.agent_evaluator import AgentEvaluator
import dotenv
import pytest


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


def test_tools():
    """Test the agent's basic ability on a few examples."""
    AgentEvaluator.evaluate(
        "personalized_shopping",
        os.path.join(os.path.dirname(__file__), "tools"),
        num_runs=1,
    )

```


---

## 文件: personalized-shopping\tests\example_interactions\image_search_denim_skirt.session.json

```json
{
  "id": "bcf712b9-2a62-422b-be8a-aafde8e270d0",
  "app_name": "personalized_shopping",
  "user_id": "test_user",
  "state": {
    "_time": "2025-04-05 17:18:06.823502"
  },
  "events": [
    {
      "invocation_id": "waFJUd2X",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 17:15:20.045009"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "oeFZ6MQS",
      "timestamp": 1743873320.045065
    },
    {
      "invocation_id": "BHGm2o2W",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 17:15:44.457339"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "CkiepE0F",
      "timestamp": 1743873344.457382
    },
    {
      "invocation_id": "tAjJ4KkZ",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 17:15:55.458962"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "cG5Nta6k",
      "timestamp": 1743873355.459005
    },
    {
      "content": {
        "parts": [
          {
            "text": "I really like this one, can you help me find something similar?"
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-3a796739-8780-4e33-a63e-e7a7041707e2",
      "author": "user",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "bbeXQ7OW",
      "timestamp": 1743873355.514693
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I can help with that! Based on the image, it looks like you're interested in a denim skirt. I'll search for similar items.\n"
          },
          {
            "function_call": {
              "id": "af-efcb86be-532f-43bd-aff0-65a6268a9fab",
              "args": {
                "keywords": "denim skirt"
              },
              "name": "search"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-3a796739-8780-4e33-a63e-e7a7041707e2",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "n5T2H2Do",
      "timestamp": 1743873355.515686
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-efcb86be-532f-43bd-aff0-65a6268a9fab",
              "name": "search",
              "response": {
                "result": "Back to Search [SEP] Page 1 (Total results: 50) [SEP] Next > [SEP] B01CO4H6TC [SEP] Hard Tail Forever Pull On Pencil Skirt, Cotton, Knee Length Style: W-321 [SEP] $60.0 to $88.0 [SEP] B083CPGNCN [SEP] Women Denim Shorts Jeans New Summer Short Denim Female Pockets Wash pants [SEP] $100.0 [SEP] B0923YHZQP [SEP] Women Denim Overall Dress Adjustable Straps American Flag Jumpsuit Outfits Streetwear [SEP] $22.99 to $31.99 [SEP] B09Q592C74 [SEP] LLDYYDS Holiday Dresses for Women Formal Midi Party Casual Short Sleeve Plus Size That Hide Belly Fat Crewneck Vintage [SEP] $20.99 to $21.99 [SEP] B09SHWQYQM [SEP] Teprec Summer Shorts for Women 2022 High Waisted Butt Lifting Casual Denim Shorts Frayed Ripped Jeans Shorts [SEP] $0.19 to $8.99 [SEP] B076KZJ3T9 [SEP] Woolrich Bitter Creek Oversized Comforter Set Grey/Brown Queen [SEP] $116.76 to $101.53 [SEP] B09H7GG7W9 [SEP] Mens Waffle Cotton Henley T Shirts Long Sleeves Casual Slim Solid Quick Dry Big & Tall Yoga Athletic Button Down Tops [SEP] $11.99 [SEP] B085T3HMGR [SEP] Woman Within Women's Plus Size Petite Flared Denim Skirt [SEP] $24.41 to $29.95 [SEP] B09HS4D3NV [SEP] Meladyan Women Y2K V Neck Checkered Graphic Knitted Sweater Vest Plaid Preppy Sleeveless Argyle Tank Top Jumper [SEP] $12.99 to $22.99 [SEP] B09KVCFQN4 [SEP] Knitted Sweaters for Women V-Neck Color Block Pullover Ribbed Cuff Thermal Fall Clothes Fashion Tops [SEP] $100.0"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-3a796739-8780-4e33-a63e-e7a7041707e2",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "AnMaajS6",
      "timestamp": 1743873357.802319
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I see a few options here. Based on the search results, \"Woman Within Women's Plus Size Petite Flared Denim Skirt\" (B085T3HMGR) seems like it could be similar to the skirt in the image. Would you like to explore that product further?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-3a796739-8780-4e33-a63e-e7a7041707e2",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "NLHeyaOZ",
      "timestamp": 1743873357.806546
    },
    {
      "invocation_id": "Mt8ZRsUc",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 17:16:01.429968"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "OlfurR6z",
      "timestamp": 1743873361.430009
    },
    {
      "invocation_id": "uFxB5D0Q",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 17:16:17.956265"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "qneK5CFj",
      "timestamp": 1743873377.956312
    },
    {
      "content": {
        "parts": [
          {
            "text": "yeah B085T3HMGR looks good!!"
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-21e26b03-4db1-47a1-bec0-6a2f2b750307",
      "author": "user",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "6anIH6Bc",
      "timestamp": 1743873377.977731
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, let's explore \"Woman Within Women's Plus Size Petite Flared Denim Skirt\" (B085T3HMGR). I will gather information from the \"Description,\" \"Features,\" and \"Reviews\" sections to give you a comprehensive overview of the product.\n"
          },
          {
            "function_call": {
              "id": "af-4700e50b-45d9-4269-b139-aad75c97df55",
              "args": {
                "button_name": "B085T3HMGR"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-21e26b03-4db1-47a1-bec0-6a2f2b750307",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "P1fc4P0e",
      "timestamp": 1743873377.979046
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-4700e50b-45d9-4269-b139-aad75c97df55",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] size [SEP] 12 plus [SEP] 12 plus petite [SEP] 14 plus [SEP] 14 plus petite [SEP] 16 plus [SEP] 16 plus petite [SEP] 18 plus [SEP] 18 plus petite [SEP] 20 plus [SEP] 20 plus petite [SEP] 22 plus [SEP] 22 plus petite [SEP] 24 plus [SEP] 24 plus petite [SEP] 26 plus [SEP] 26 plus petite [SEP] 28 plus [SEP] 28 plus petite [SEP] 30 plus [SEP] 30 plus petite [SEP] 32 plus [SEP] 32 plus petite [SEP] 34 plus [SEP] 34 plus petite [SEP] 36 plus [SEP] 36 plus petite [SEP] 38 plus [SEP] 38 plus petite [SEP] color [SEP] indigo [SEP] natural khaki [SEP] black [SEP] light wash [SEP] stonewash [SEP] white [SEP] Woman Within Women's Plus Size Petite Flared Denim Skirt [SEP] Price: $24.41 to $29.95 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-21e26b03-4db1-47a1-bec0-6a2f2b750307",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "lWV1z1wQ",
      "timestamp": 1743873380.373883
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I'm now on the product page for the \"Woman Within Women's Plus Size Petite Flared Denim Skirt\".\n\nI will start by gathering information from the \"Description\" section.\n"
          },
          {
            "function_call": {
              "id": "af-d945a812-011d-4fd2-8115-27e1badb2957",
              "args": {
                "button_name": "Description"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-21e26b03-4db1-47a1-bec0-6a2f2b750307",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "v4R0lDxW",
      "timestamp": 1743873380.378448
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-d945a812-011d-4fd2-8115-27e1badb2957",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-21e26b03-4db1-47a1-bec0-6a2f2b750307",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "NqNr4sfV",
      "timestamp": 1743873382.439461
    },
    {
      "content": {
        "parts": [
          {
            "text": "Looks like there is no description available.\n\nNow I will check the \"Features\".\n"
          },
          {
            "function_call": {
              "id": "af-d5c1a8dc-2975-4b02-9251-250281d05575",
              "args": {
                "button_name": "< Prev"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-21e26b03-4db1-47a1-bec0-6a2f2b750307",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "V6h7XqTL",
      "timestamp": 1743873382.443894
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-d5c1a8dc-2975-4b02-9251-250281d05575",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] size [SEP] 12 plus [SEP] 12 plus petite [SEP] 14 plus [SEP] 14 plus petite [SEP] 16 plus [SEP] 16 plus petite [SEP] 18 plus [SEP] 18 plus petite [SEP] 20 plus [SEP] 20 plus petite [SEP] 22 plus [SEP] 22 plus petite [SEP] 24 plus [SEP] 24 plus petite [SEP] 26 plus [SEP] 26 plus petite [SEP] 28 plus [SEP] 28 plus petite [SEP] 30 plus [SEP] 30 plus petite [SEP] 32 plus [SEP] 32 plus petite [SEP] 34 plus [SEP] 34 plus petite [SEP] 36 plus [SEP] 36 plus petite [SEP] 38 plus [SEP] 38 plus petite [SEP] color [SEP] indigo [SEP] natural khaki [SEP] black [SEP] light wash [SEP] stonewash [SEP] white [SEP] Woman Within Women's Plus Size Petite Flared Denim Skirt [SEP] Price: $24.41 to $29.95 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-21e26b03-4db1-47a1-bec0-6a2f2b750307",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "AqhI35Sx",
      "timestamp": 1743873385.193372
    },
    {
      "content": {
        "parts": [
          {
            "function_call": {
              "id": "af-a770ed29-a419-4015-84f5-4a9565bfabf8",
              "args": {
                "button_name": "Features"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-21e26b03-4db1-47a1-bec0-6a2f2b750307",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "82ymBJOc",
      "timestamp": 1743873385.197746
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-a770ed29-a419-4015-84f5-4a9565bfabf8",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] PLUS SIZING: Please reference our size charts [SEP] Redefine your silhouette in this great, plus size drawstring denim skirt. The fabric is soft with an elastic waist that ties with a drawstring. You can fine tune your waist fit with ease. [SEP] Full elastic drawstring waist. A-line silhouette [SEP] Regular length: 34\". Petite length: 32\". Side seam pockets. Woven cotton denim or twill; imported [SEP] ABOUT THE BRAND: At Woman Within we’re the experts in plus size comfort, and we’ve been doing this for over 100 years. No surprise then that we’re one of the go-to brands in the plus-size clothing industry for incredible fit and of-the-moment style. Our goal is to make sure you always feel great and look good in our comfortable clothes in all the colors you love."
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-21e26b03-4db1-47a1-bec0-6a2f2b750307",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "86sYJOSO",
      "timestamp": 1743873387.676282
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I have the features now.\n\nFinally, let's check the \"Reviews\".\n"
          },
          {
            "function_call": {
              "id": "af-96697b64-f7a6-4521-aba1-bb56856f8955",
              "args": {
                "button_name": "< Prev"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-21e26b03-4db1-47a1-bec0-6a2f2b750307",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "tks80gSX",
      "timestamp": 1743873387.68122
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-96697b64-f7a6-4521-aba1-bb56856f8955",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] size [SEP] 12 plus [SEP] 12 plus petite [SEP] 14 plus [SEP] 14 plus petite [SEP] 16 plus [SEP] 16 plus petite [SEP] 18 plus [SEP] 18 plus petite [SEP] 20 plus [SEP] 20 plus petite [SEP] 22 plus [SEP] 22 plus petite [SEP] 24 plus [SEP] 24 plus petite [SEP] 26 plus [SEP] 26 plus petite [SEP] 28 plus [SEP] 28 plus petite [SEP] 30 plus [SEP] 30 plus petite [SEP] 32 plus [SEP] 32 plus petite [SEP] 34 plus [SEP] 34 plus petite [SEP] 36 plus [SEP] 36 plus petite [SEP] 38 plus [SEP] 38 plus petite [SEP] color [SEP] indigo [SEP] natural khaki [SEP] black [SEP] light wash [SEP] stonewash [SEP] white [SEP] Woman Within Women's Plus Size Petite Flared Denim Skirt [SEP] Price: $24.41 to $29.95 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-21e26b03-4db1-47a1-bec0-6a2f2b750307",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "vHAScDf6",
      "timestamp": 1743873389.837989
    },
    {
      "content": {
        "parts": [
          {
            "function_call": {
              "id": "af-ad7f1e7d-591c-41ad-b932-f2993160ddfc",
              "args": {
                "button_name": "Reviews"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-21e26b03-4db1-47a1-bec0-6a2f2b750307",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "Kubr9o89",
      "timestamp": 1743873389.843045
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-ad7f1e7d-591c-41ad-b932-f2993160ddfc",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-21e26b03-4db1-47a1-bec0-6a2f2b750307",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "IJ3jy1rg",
      "timestamp": 1743873391.65879
    },
    {
      "content": {
        "parts": [
          {
            "text": "There are no reviews available for this product.\n\nOkay, so here's a summary of what I found:\n\n*   **Description:** Not Available\n*   **Features:** Plus size denim skirt with a full elastic drawstring waist and A-line silhouette. Available in regular (34\") and petite (32\") lengths. Side seam pockets. Made from woven cotton denim or twill.\n*   **Reviews:** Not Available\n\nGiven the lack of a description and reviews, it's a bit difficult to say for sure if this skirt is exactly what you're looking for. However, the features mention an A-line silhouette, which is similar to the skirt in your image.\n\nWould you like to proceed with purchasing this skirt, or would you prefer to go back to the search results and explore other options?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-21e26b03-4db1-47a1-bec0-6a2f2b750307",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "3e1CnR9o",
      "timestamp": 1743873391.66365
    },
    {
      "invocation_id": "TDXtPFnP",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 17:17:00.029926"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "njpYJ7dr",
      "timestamp": 1743873420.029975
    },
    {
      "content": {
        "parts": [
          {
            "text": "Yeah proceed with purchasing. Can you go back to the previous page and show me what options are available?"
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-bf0142d4-e769-4b66-988b-eda85040ef26",
      "author": "user",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "jFpD3OzN",
      "timestamp": 1743873420.079877
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I will go back to the product page to show you the available options.\n"
          },
          {
            "function_call": {
              "id": "af-74a3e227-6b9e-4ab9-a947-c745682e8a04",
              "args": {
                "button_name": "< Prev"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-bf0142d4-e769-4b66-988b-eda85040ef26",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "QpsjH9fv",
      "timestamp": 1743873420.08108
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-74a3e227-6b9e-4ab9-a947-c745682e8a04",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] size [SEP] 12 plus [SEP] 12 plus petite [SEP] 14 plus [SEP] 14 plus petite [SEP] 16 plus [SEP] 16 plus petite [SEP] 18 plus [SEP] 18 plus petite [SEP] 20 plus [SEP] 20 plus petite [SEP] 22 plus [SEP] 22 plus petite [SEP] 24 plus [SEP] 24 plus petite [SEP] 26 plus [SEP] 26 plus petite [SEP] 28 plus [SEP] 28 plus petite [SEP] 30 plus [SEP] 30 plus petite [SEP] 32 plus [SEP] 32 plus petite [SEP] 34 plus [SEP] 34 plus petite [SEP] 36 plus [SEP] 36 plus petite [SEP] 38 plus [SEP] 38 plus petite [SEP] color [SEP] indigo [SEP] natural khaki [SEP] black [SEP] light wash [SEP] stonewash [SEP] white [SEP] Woman Within Women's Plus Size Petite Flared Denim Skirt [SEP] Price: $24.41 to $29.95 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-bf0142d4-e769-4b66-988b-eda85040ef26",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "Vpxya3DK",
      "timestamp": 1743873422.141734
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, here are the available options:\n\n**Sizes:**\n\n*   12 plus to 38 plus\n*   12 plus petite to 38 plus petite\n\n**Colors:**\n\n*   Indigo\n*   Natural Khaki\n*   Black\n*   Light Wash\n*   Stonewash\n*   White\n\nWhat size and color would you like to purchase?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-bf0142d4-e769-4b66-988b-eda85040ef26",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "TskAswFF",
      "timestamp": 1743873422.146468
    },
    {
      "invocation_id": "icQDaEHa",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 17:17:51.039770"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "AEA0Oh6m",
      "timestamp": 1743873471.039826
    },
    {
      "content": {
        "parts": [
          {
            "text": "select 12 plus, in natural khaki"
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-1bbdc58b-23fa-44df-9425-ad8299c6a306",
      "author": "user",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "AC7w1jtc",
      "timestamp": 1743873471.101118
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I have selected size 12 plus and color natural khaki.\n"
          },
          {
            "function_call": {
              "id": "af-2c44a89c-11ea-4212-9cf7-d2b2ab85493f",
              "args": {
                "button_name": "12 plus"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-1bbdc58b-23fa-44df-9425-ad8299c6a306",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "wIeI74l8",
      "timestamp": 1743873471.102303
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-2c44a89c-11ea-4212-9cf7-d2b2ab85493f",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] size [SEP] 12 plus [SEP] 12 plus petite [SEP] 14 plus [SEP] 14 plus petite [SEP] 16 plus [SEP] 16 plus petite [SEP] 18 plus [SEP] 18 plus petite [SEP] 20 plus [SEP] 20 plus petite [SEP] 22 plus [SEP] 22 plus petite [SEP] 24 plus [SEP] 24 plus petite [SEP] 26 plus [SEP] 26 plus petite [SEP] 28 plus [SEP] 28 plus petite [SEP] 30 plus [SEP] 30 plus petite [SEP] 32 plus [SEP] 32 plus petite [SEP] 34 plus [SEP] 34 plus petite [SEP] 36 plus [SEP] 36 plus petite [SEP] 38 plus [SEP] 38 plus petite [SEP] color [SEP] indigo [SEP] natural khaki [SEP] black [SEP] light wash [SEP] stonewash [SEP] white [SEP] Woman Within Women's Plus Size Petite Flared Denim Skirt [SEP] Price: $24.41 to $29.95 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-1bbdc58b-23fa-44df-9425-ad8299c6a306",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "NlWyliBv",
      "timestamp": 1743873473.396986
    },
    {
      "content": {
        "parts": [
          {
            "function_call": {
              "id": "af-74b2def0-8a09-4e97-b574-58f8acb0a6dc",
              "args": {
                "button_name": "natural khaki"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-1bbdc58b-23fa-44df-9425-ad8299c6a306",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "3JTNphMn",
      "timestamp": 1743873473.401984
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-74b2def0-8a09-4e97-b574-58f8acb0a6dc",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] size [SEP] 12 plus [SEP] 12 plus petite [SEP] 14 plus [SEP] 14 plus petite [SEP] 16 plus [SEP] 16 plus petite [SEP] 18 plus [SEP] 18 plus petite [SEP] 20 plus [SEP] 20 plus petite [SEP] 22 plus [SEP] 22 plus petite [SEP] 24 plus [SEP] 24 plus petite [SEP] 26 plus [SEP] 26 plus petite [SEP] 28 plus [SEP] 28 plus petite [SEP] 30 plus [SEP] 30 plus petite [SEP] 32 plus [SEP] 32 plus petite [SEP] 34 plus [SEP] 34 plus petite [SEP] 36 plus [SEP] 36 plus petite [SEP] 38 plus [SEP] 38 plus petite [SEP] color [SEP] indigo [SEP] natural khaki [SEP] black [SEP] light wash [SEP] stonewash [SEP] white [SEP] Woman Within Women's Plus Size Petite Flared Denim Skirt [SEP] Price: $24.41 to $29.95 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-1bbdc58b-23fa-44df-9425-ad8299c6a306",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "ybblUikZ",
      "timestamp": 1743873475.276006
    },
    {
      "content": {
        "parts": [
          {
            "text": "You have selected a size 12 plus and the color natural khaki. Are you ready to finalize the purchase?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-1bbdc58b-23fa-44df-9425-ad8299c6a306",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "mBkMvEOv",
      "timestamp": 1743873475.28111
    },
    {
      "invocation_id": "YwnkcB8K",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 17:18:01.773952"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "uJ0eQnzK",
      "timestamp": 1743873481.774006
    },
    {
      "content": {
        "parts": [
          {
            "text": "Yes, go ahead!"
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-4d1f6197-7cae-4362-bf02-689e81bc1643",
      "author": "user",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "vsDU6pOy",
      "timestamp": 1743873481.838773
    },
    {
      "content": {
        "parts": [
          {
            "function_call": {
              "id": "af-95dd6dd4-7742-4686-8333-0dc4b05d460c",
              "args": {
                "button_name": "Buy Now"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-4d1f6197-7cae-4362-bf02-689e81bc1643",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "8ykYbIQk",
      "timestamp": 1743873481.840023
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-95dd6dd4-7742-4686-8333-0dc4b05d460c",
              "name": "click",
              "response": {
                "result": "Thank you for shopping with us! [SEP] Your code: [SEP] None [SEP] (Paste it in your MTurk interface.) [SEP] Purchased [SEP] asin [SEP] B085T3HMGR [SEP] options [SEP] {\"color\": \"natural khaki\", \"size\": \"12 plus\"} [SEP] attrs [SEP] None [SEP] category [SEP] None [SEP] query [SEP] None [SEP] product category [SEP] None [SEP] Target [SEP] asin [SEP] options [SEP] attrs [SEP] price upper [SEP] instuction text [SEP] category [SEP] product category [SEP] query [SEP] Goal [SEP] None [SEP] Reward [SEP] Your score (min 0.0, max 1.0) [SEP] 0.0 [SEP] Reward Details [SEP] None"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-4d1f6197-7cae-4362-bf02-689e81bc1643",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "NceQfYsu",
      "timestamp": 1743873483.792323
    },
    {
      "invocation_id": "YCP4sHDP",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 17:18:06.823502"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "IUM04ePj",
      "timestamp": 1743873486.823545
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, the purchase is being processed. Thank you for shopping with us! The order details are as follows:\n\n*   **Product:** Woman Within Women's Plus Size Petite Flared Denim Skirt\n*   **Size:** 12 plus\n*   **Color:** Natural Khaki\n\nPlease paste the code \"None\" in your MTurk interface.\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-4d1f6197-7cae-4362-bf02-689e81bc1643",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "yxwUAvvF",
      "timestamp": 1743873483.797691
    }
  ],
  "last_update_time": 1743873483.797691
}
```


---

## 文件: personalized-shopping\tests\example_interactions\text_search_floral_dress.session.json

```json
{
  "id": "9056575a-70ad-410e-84ea-a2af3aa7dbed",
  "app_name": "personalized_shopping",
  "user_id": "test_user",
  "state": {
    "_time": "2025-04-05 16:54:21.685906"
  },
  "events": [
    {
      "invocation_id": "waFJUd2X",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 16:51:48.668338"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "oeFZ6MQS",
      "timestamp": 1743871908.668384
    },
    {
      "invocation_id": "BHGm2o2W",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 16:52:11.741693"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "CkiepE0F",
      "timestamp": 1743871931.741734
    },
    {
      "content": {
        "parts": [
          {
            "text": "Hello, can you help me find a summer dress? I want something flowy and floral."
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-69e4778f-29ef-4911-97ba-caf9bd1ad9df",
      "author": "user",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "ZcG5Nta6",
      "timestamp": 1743871931.781544
    },
    {
      "content": {
        "parts": [
          {
            "function_call": {
              "id": "af-249a5215-6a59-43c4-b03b-3b58ff0d587d",
              "args": {
                "keywords": "flowy floral summer dress"
              },
              "name": "search"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-69e4778f-29ef-4911-97ba-caf9bd1ad9df",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "FuUCwdgv",
      "timestamp": 1743871931.782609
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-249a5215-6a59-43c4-b03b-3b58ff0d587d",
              "name": "search",
              "response": {
                "result": "Back to Search [SEP] Page 1 (Total results: 50) [SEP] Next > [SEP] B092QL1FLW [SEP] Women Summer Cold Shoulder Dress,Beach Vintage Bohemian Print Sundress Party Prom Swing Loose A-Line Dress with Pocket [SEP] $16.29 to $17.59 [SEP] B094Z77449 [SEP] Casual Summer Dress for Women,V-Neck Sleeveless High Waist Maternity Dress Loose Floral Print Maxi Pregnant Dress [SEP] $1.69 to $12.19 [SEP] B09MW6NN3H [SEP] Mind of My Own Maxi Dress for Womens Sexy Deep V Bodycon Long Dress Fashion Bag Hip Tie dye Printed Dresses [SEP] $7.99 to $14.99 [SEP] B09P8R92RL [SEP] SERCFGYUJ Women's Party Dresses Fashion V Neck Long Sleeve Slit Mini Dress Casual Printed Wrap Buttocks Ruched Prom Dress [SEP] $8.99 to $18.99 [SEP] B09P8RQFHL [SEP] New Years Dress for Women Plus Size Crew Neck Butterfly Print A-Line Long Dresses Casual Lace Splicing Prom Dress [SEP] $8.99 to $19.99 [SEP] B09P8S93S8 [SEP] Sparkly Dresses for Women Long Sleeve Stylish V Neck Mini Dress Casual Flower Butterfly Print Sequin Black Dress [SEP] $5.99 to $15.99 [SEP] B09MW5XWSZ [SEP] NaRHbrg Summer Casual Dress for Women's Boho V Neck Sleeveless Long Maxi Dresses Ladies Loose Pockets Dress Floor-Length [SEP] $4.99 to $13.99 [SEP] B08GRRPFHP [SEP] Alex Evenings Women's Long 3/4 Sleeve Velvet Dress [SEP] $109.65 to $192.06 [SEP] B09RDX8KQJ [SEP] FABIURT Sundresses for Women Casual Beach, Women's Summer Butterfly Printed Dress V-Neck Sleeveless Long Dresses with Pockets [SEP] $4.99 to $7.99 [SEP] B09JWJ5L8S [SEP] BB&KK Women's Summer Maxi Long Cold Shoulder Loose Kaftan Flowy Batwing Beach Cover Up Dress [SEP] $29.99"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-69e4778f-29ef-4911-97ba-caf9bd1ad9df",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "Q7OWpvn5",
      "timestamp": 1743871933.576432
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I see a few options that might work. Here are some of the dresses that came up in the search results:\n\n*   **B092QL1FLW:** Women Summer Cold Shoulder Dress, Beach Vintage Bohemian Print Sundress\n*   **B094Z77449:** Casual Summer Dress for Women, V-Neck Sleeveless High Waist Maternity Dress Loose Floral Print Maxi Pregnant Dress\n*   **B09MW6NN3H:** Mind of My Own Maxi Dress for Womens Sexy Deep V Bodycon Long Dress Fashion Bag Hip Tie dye Printed Dresses\n*   **B09RDX8KQJ:** FABIURT Sundresses for Women Casual Beach, Women's Summer Butterfly Printed Dress V-Neck Sleeveless Long Dresses with Pockets\n*   **B09JWJ5L8S:** BB&KK Women's Summer Maxi Long Cold Shoulder Loose Kaftan Flowy Batwing Beach Cover Up Dress\n\nWould you like to explore any of these further? Or would you like me to refine the search?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-69e4778f-29ef-4911-97ba-caf9bd1ad9df",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "2H2Doybn",
      "timestamp": 1743871933.580608
    },
    {
      "invocation_id": "HAnMaajS",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 16:52:22.464989"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "6GNLHeya",
      "timestamp": 1743871942.465028
    },
    {
      "content": {
        "parts": [
          {
            "text": "B092QL1FLW looks good!"
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-225a5cff-d9c8-41fd-a1d2-b81ef7d2916c",
      "author": "user",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "rR6zNB38",
      "timestamp": 1743871942.476048
    },
    {
      "content": {
        "parts": [
          {
            "function_call": {
              "id": "af-406a6dd0-b368-4ac9-9ab3-0f65f27a4c9a",
              "args": {
                "button_name": "B092QL1FLW"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-225a5cff-d9c8-41fd-a1d2-b81ef7d2916c",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "mkZnuFxB",
      "timestamp": 1743871942.476651
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-406a6dd0-b368-4ac9-9ab3-0f65f27a4c9a",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] color [SEP] black [SEP] blacka [SEP] blackb [SEP] blue [SEP] bluea [SEP] blueb [SEP] coffee [SEP] gray [SEP] green [SEP] hot pink [SEP] navy [SEP] pink [SEP] pinka [SEP] purple [SEP] purplea [SEP] sky blue [SEP] sky bluea [SEP] white [SEP] whitea [SEP] yellow [SEP] yellowa [SEP] size [SEP] small [SEP] medium [SEP] large [SEP] x-large [SEP] xx-large [SEP] Women Summer Cold Shoulder Dress,Beach Vintage Bohemian Print Sundress Party Prom Swing Loose A-Line Dress with Pocket [SEP] Price: $16.29 to $17.59 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-225a5cff-d9c8-41fd-a1d2-b81ef7d2916c",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "eK5CFjLX",
      "timestamp": 1743871943.741507
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I have selected the product page for **B092QL1FLW** - Women Summer Cold Shoulder Dress, Beach Vintage Bohemian Print Sundress Party Prom Swing Loose A-Line Dress with Pocket.\n\nTo help you decide, I'll summarize the information from the Description, Features, and Reviews sections. I'll start by gathering the product description.\n"
          },
          {
            "function_call": {
              "id": "af-04058f7c-d125-47c0-8141-fe1ae83627b9",
              "args": {
                "button_name": "Description"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-225a5cff-d9c8-41fd-a1d2-b81ef7d2916c",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "iIOpoy2v",
      "timestamp": 1743871943.745952
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-04058f7c-d125-47c0-8141-fe1ae83627b9",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] Women's Casual Long Dress with Striped Floral Print Short Sleeve Maxi Dress★Description:●Season:Spring,Summer●Gender:Women●Style:Casual●Material:Cottonblend●Pattern Type:Print●Decoration: None❤What you get:1 X dress※Design can make you more sexy, more energetic and more attractive★★PLEASE NOTE:❤Our clothes all are designed for Asian figure, which means would be smaller than normal US sizes. Please refer to our own size chart and you can find it in our pictures or from the description.❤Garment Care: Hand Wash Recommand or Dry Clean Your Shirt Dress. The Pattern on the Original Product May Vary Please Know .❤Colors may be slightly different depending on computer and monitor settings❤Please check the Size Chart before order. If you are not sure the size, please send message to us."
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-225a5cff-d9c8-41fd-a1d2-b81ef7d2916c",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "anIH6Bcn",
      "timestamp": 1743871945.640216
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I have the description. Now I will gather the features.\n"
          },
          {
            "function_call": {
              "id": "af-38348770-3de5-44e9-ab40-c4b6ea1b7034",
              "args": {
                "button_name": "< Prev"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-225a5cff-d9c8-41fd-a1d2-b81ef7d2916c",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "P1fc4P0e",
      "timestamp": 1743871945.644364
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-38348770-3de5-44e9-ab40-c4b6ea1b7034",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] color [SEP] black [SEP] blacka [SEP] blackb [SEP] blue [SEP] bluea [SEP] blueb [SEP] coffee [SEP] gray [SEP] green [SEP] hot pink [SEP] navy [SEP] pink [SEP] pinka [SEP] purple [SEP] purplea [SEP] sky blue [SEP] sky bluea [SEP] white [SEP] whitea [SEP] yellow [SEP] yellowa [SEP] size [SEP] small [SEP] medium [SEP] large [SEP] x-large [SEP] xx-large [SEP] Women Summer Cold Shoulder Dress,Beach Vintage Bohemian Print Sundress Party Prom Swing Loose A-Line Dress with Pocket [SEP] Price: $16.29 to $17.59 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-225a5cff-d9c8-41fd-a1d2-b81ef7d2916c",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "lWV1z1wQ",
      "timestamp": 1743871946.941793
    },
    {
      "content": {
        "parts": [
          {
            "function_call": {
              "id": "af-a75b9bd9-269f-4d05-95ad-51545991f2d6",
              "args": {
                "button_name": "Features"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-225a5cff-d9c8-41fd-a1d2-b81ef7d2916c",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "v4R0lDxW",
      "timestamp": 1743871946.946318
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-a75b9bd9-269f-4d05-95ad-51545991f2d6",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] Tie closure Hand Wash Only ❤[MATERIAL]: Made of high quality material, soft to the touch, lightweight and flowy，wearing comfortable and not irritating. ❤[OCCASION]: Travel, Daily Wearing, Party, Office, Shopping, Dating, Weekend Gathering, Beach/Sands, Cocktail party, Outdoors, Halloween, Christmas, New Year, Casual,Commute etc.Easy to match all kinds of hair accessories, and you can wear it with fashion and temperament. ❤[FEATURE]: This is a casual dress with special design that can show your perfect figure, make you more attractive, and can easily control parties, cocktail,beaches and other occasions. ❤[SIZE AND CARE]: Before order, please carefully read the Size Chart we provided in the product description ,Select the size according it. Hand washing or machine with cold water is recommended.Using mild gentle soap,no bleach.If there are wrinkles,you can iron it at low temperature and hang it dry. ❤[STATEMENT]:Please contact us in case of any order-related problems for a satisfactory resolution! \n Sleeveless Short Long Sleeve Mini Midi Maxi Dress Bodycon Ruched Pleated Dress Side Drawstring Chiffon Solid Crew Neck Casual Summer Tank Shirt Mini Dresses 2021 Summer Women’s Dress Sexy V Neck Flowy Dress Swiss Dot Faux Short Loose Fit Pregnant Dress Women's Dresses-Summer Floral Bohemian Adjustable Spaghetti Strap Button Down Swing Dress with Pockets Women Dress Summer U Neck Mini Floral Print Swing Dress Spaghetti Strap Sling Skater Dresses with BeltAdjustable Straps Sexy Sling Dress Backless Spaghetti Casual Cocktail Club Party Night Out Dress Cami Crop Bodycon Dress Plus Size Vintage Lace Summer Swing Pencil Slim Short Mini Maxi Long Halter Embroidery Classic Dress Guest Floral Printing Pocket Midi A-Line Dress Cold Shoulder Tie Waist High Waist Beach Wedding Daily Work Dress Strapless Boho Sleeveless Flowy Side Front Split Button V-Neck O-Neck Evening Gown Patchwork Ruffle Soft Tank Vest Bridesmaid Dress Plain DressSummer Sleeveless Beachwear Dress Daily Work Wedding Party Club Night-Out Dress Long Maxi Short Mini Midi Dress Casual Fashion Sexy Bohemian Floral Printing Spaghetti Cocktail Tie-Dye High Waist Bodycon Ruched Dress Crewneck V-Neck O-Neck Colorful Dress Tank Tshirt Tunic Top Sling Sundress Strap Belt Elegant Dance Dress Pocket 3/4 Sleeve Office Shopping Polka Dress Puff Women's Pencil A-Line Plain Cute Swing Flowy Dress Adjustable Strap Wrap Cotton Girl Gift Birthday Festival DressSkater Swing Flowy Loose Dress Ruched Stretchy Elegant Dress With Pockets Summer Beach Tropical Sexy Dress Tie Neck Sling Vest Top Dress Strapless Backless Solid Color Vintage Women Dress Maxi Long Boho Casual Floral Dress Spaghetti Cami Plus Size Nightgown Dress Short Long Sleeve Sleeveless V-Neck O-Neck Ruffle Girl Dress Streetwear Wedding Guest Party Wrok Neckline Dress Spring Flower Printed T-Shirt Empire Waist High Waist Dress Patchwork Side Split Lace Cotton DressWomen Casual Dress Perfect Gife To Love Halter Retro Cocktail Dress Boho Skater Polka Dot Long Maxi Dress With Pocket And Strap Sleeveless Backless Off Shoulder Sexy Mini Short Women Dress Party Wedding Midi A-Line Solid Color Lace Spaghetti Bohemian Split Dress Sleeve Shift Sweet Cute Sundress High Waist V-Neck 3/4 Ballon Sleeve Dress Swing Flowy Tunic Beachwear Crewneck Stretchy Tie Dye Chiffon Hollow Out Dress Maternity Dress For Photoshoot Plus Size White Prom Bridemaid DressesShow more"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-225a5cff-d9c8-41fd-a1d2-b81ef7d2916c",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "DfNqNr4s",
      "timestamp": 1743871948.196046
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I have the features. Now I will gather the reviews.\n"
          },
          {
            "function_call": {
              "id": "af-b2fd6f5c-6a76-429a-be19-81fd55932e7f",
              "args": {
                "button_name": "< Prev"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-225a5cff-d9c8-41fd-a1d2-b81ef7d2916c",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "VEV6h7Xq",
      "timestamp": 1743871948.200674
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-b2fd6f5c-6a76-429a-be19-81fd55932e7f",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] color [SEP] black [SEP] blacka [SEP] blackb [SEP] blue [SEP] bluea [SEP] blueb [SEP] coffee [SEP] gray [SEP] green [SEP] hot pink [SEP] navy [SEP] pink [SEP] pinka [SEP] purple [SEP] purplea [SEP] sky blue [SEP] sky bluea [SEP] white [SEP] whitea [SEP] yellow [SEP] yellowa [SEP] size [SEP] small [SEP] medium [SEP] large [SEP] x-large [SEP] xx-large [SEP] Women Summer Cold Shoulder Dress,Beach Vintage Bohemian Print Sundress Party Prom Swing Loose A-Line Dress with Pocket [SEP] Price: $16.29 to $17.59 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-225a5cff-d9c8-41fd-a1d2-b81ef7d2916c",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "7XkspAqh",
      "timestamp": 1743871949.510823
    },
    {
      "content": {
        "parts": [
          {
            "function_call": {
              "id": "af-f540b6aa-0fda-45a3-86d7-ba4b9dab780d",
              "args": {
                "button_name": "Reviews"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-225a5cff-d9c8-41fd-a1d2-b81ef7d2916c",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "35Sx10O8",
      "timestamp": 1743871949.515702
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-f540b6aa-0fda-45a3-86d7-ba4b9dab780d",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-225a5cff-d9c8-41fd-a1d2-b81ef7d2916c",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "JOcP1v86",
      "timestamp": 1743871950.758925
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I have gathered the information from the Description, Features, and Reviews sections. Here's a summary:\n\n*   **Description:** The dress is a casual women's long dress suitable for Spring and Summer. It's made of a cotton blend material with a print pattern. The design aims to make the wearer look more sexy, energetic, and attractive. Note that the sizes are Asian sizes, which are smaller than US sizes, so it's important to refer to the size chart. Garment care recommends hand washing or dry cleaning.\n*   **Features:** The dress is made of high-quality, soft, lightweight, and flowy material. It's suitable for various occasions like travel, daily wear, parties, and beach outings. The design is intended to show off the wearer's figure and make them more attractive. The features emphasize hand washing or machine washing with cold water and ironing at low temperature if needed.\n*   **Reviews:** There are no reviews available for this product.\n\nBased on the description and features, this dress seems like it could be a good fit for your request for a flowy and floral summer dress. However, the lack of reviews makes it difficult to assess the quality and fit.\n\nWould you like to proceed with purchasing this dress, or would you prefer to search for other options with customer reviews?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-225a5cff-d9c8-41fd-a1d2-b81ef7d2916c",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "YJOSOotk",
      "timestamp": 1743871950.763569
    },
    {
      "invocation_id": "80gSXfBl",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 16:52:44.412401"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "kPvHAScD",
      "timestamp": 1743871964.412442
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, this looks good!"
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-1f840083-f484-4bfa-9008-670d0dbb43ce",
      "author": "user",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "J7drPGvk",
      "timestamp": 1743871964.448019
    },
    {
      "content": {
        "parts": [
          {
            "text": "What size and color would you like to purchase?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-1f840083-f484-4bfa-9008-670d0dbb43ce",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "1dPVwr4L",
      "timestamp": 1743871964.449179
    },
    {
      "invocation_id": "9HLBFVHa",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 16:52:58.702308"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "O0bzG5jH",
      "timestamp": 1743871978.702351
    },
    {
      "content": {
        "parts": [
          {
            "text": "What options are available?"
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-1891cf5d-95c4-4056-b242-f32b992c9124",
      "author": "user",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "ya3DK3AT",
      "timestamp": 1743871978.740306
    },
    {
      "content": {
        "parts": [
          {
            "function_call": {
              "id": "af-fac506c5-eaf1-4fb8-8bef-bbcf40a193e1",
              "args": {
                "button_name": "< Prev"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-1891cf5d-95c4-4056-b242-f32b992c9124",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "AswFFFic",
      "timestamp": 1743871978.74139
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-fac506c5-eaf1-4fb8-8bef-bbcf40a193e1",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] color [SEP] black [SEP] blacka [SEP] blackb [SEP] blue [SEP] bluea [SEP] blueb [SEP] coffee [SEP] gray [SEP] green [SEP] hot pink [SEP] navy [SEP] pink [SEP] pinka [SEP] purple [SEP] purplea [SEP] sky blue [SEP] sky bluea [SEP] white [SEP] whitea [SEP] yellow [SEP] yellowa [SEP] size [SEP] small [SEP] medium [SEP] large [SEP] x-large [SEP] xx-large [SEP] Women Summer Cold Shoulder Dress,Beach Vintage Bohemian Print Sundress Party Prom Swing Loose A-Line Dress with Pocket [SEP] Price: $16.29 to $17.59 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-1891cf5d-95c4-4056-b242-f32b992c9124",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "HaAEA0Oh",
      "timestamp": 1743871980.055947
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, here are the available options:\n\n**Colors:** black, blacka, blackb, blue, bluea, blueb, coffee, gray, green, hot pink, navy, pink, pinka, purple, purplea, sky blue, sky bluea, white, whitea, yellow, yellowa\n\n**Sizes:** small, medium, large, x-large, xx-large\n\nPlease let me know which color and size you would like to purchase.\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-1891cf5d-95c4-4056-b242-f32b992c9124",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "3l6eVhHE",
      "timestamp": 1743871980.060821
    },
    {
      "invocation_id": "6jhx2I9S",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 16:53:19.787229"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "EgBcmW4X",
      "timestamp": 1743871999.787277
    },
    {
      "content": {
        "parts": [
          {
            "text": "Can you show me what a sky blue one look like?"
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-1b5ed505-0d97-43cf-a70c-1033f8d4928b",
      "author": "user",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "9XhtELNl",
      "timestamp": 1743871999.832061
    },
    {
      "content": {
        "parts": [
          {
            "function_call": {
              "id": "af-9c8f1831-3b46-4524-a408-3741aef62f61",
              "args": {
                "button_name": "sky blue"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-1b5ed505-0d97-43cf-a70c-1033f8d4928b",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "liBv2w3J",
      "timestamp": 1743871999.833244
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-9c8f1831-3b46-4524-a408-3741aef62f61",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] color [SEP] black [SEP] blacka [SEP] blackb [SEP] blue [SEP] bluea [SEP] blueb [SEP] coffee [SEP] gray [SEP] green [SEP] hot pink [SEP] navy [SEP] pink [SEP] pinka [SEP] purple [SEP] purplea [SEP] sky blue [SEP] sky bluea [SEP] white [SEP] whitea [SEP] yellow [SEP] yellowa [SEP] size [SEP] small [SEP] medium [SEP] large [SEP] x-large [SEP] xx-large [SEP] Women Summer Cold Shoulder Dress,Beach Vintage Bohemian Print Sundress Party Prom Swing Loose A-Line Dress with Pocket [SEP] Price: $16.29 to $17.59 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-1b5ed505-0d97-43cf-a70c-1033f8d4928b",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "MndjJybb",
      "timestamp": 1743872001.108458
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I have selected the sky blue color. Is there anything else I can help you with?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-1b5ed505-0d97-43cf-a70c-1033f8d4928b",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "UikZumBk",
      "timestamp": 1743872001.115504
    },
    {
      "invocation_id": "vEOvcYwn",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 16:53:42.238239"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "kcB8KuJ0",
      "timestamp": 1743872022.238281
    },
    {
      "content": {
        "parts": [
          {
            "text": "ah i don't like this color, go back to the black"
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-b888ef1a-202a-43ad-8065-5cf940be01ea",
      "author": "user",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "OSZmfp6k",
      "timestamp": 1743872022.288814
    },
    {
      "content": {
        "parts": [
          {
            "function_call": {
              "id": "af-2bae6f0e-9a39-4522-ad8d-41fc9744e86f",
              "args": {
                "button_name": "black"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-b888ef1a-202a-43ad-8065-5cf940be01ea",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "PFizvsDU",
      "timestamp": 1743872022.290028
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-2bae6f0e-9a39-4522-ad8d-41fc9744e86f",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] color [SEP] black [SEP] blacka [SEP] blackb [SEP] blue [SEP] bluea [SEP] blueb [SEP] coffee [SEP] gray [SEP] green [SEP] hot pink [SEP] navy [SEP] pink [SEP] pinka [SEP] purple [SEP] purplea [SEP] sky blue [SEP] sky bluea [SEP] white [SEP] whitea [SEP] yellow [SEP] yellowa [SEP] size [SEP] small [SEP] medium [SEP] large [SEP] x-large [SEP] xx-large [SEP] Women Summer Cold Shoulder Dress,Beach Vintage Bohemian Print Sundress Party Prom Swing Loose A-Line Dress with Pocket [SEP] Price: $16.29 to $17.59 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-b888ef1a-202a-43ad-8065-5cf940be01ea",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "48ykYbIQ",
      "timestamp": 1743872023.575779
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, I have selected the black color. What size would you like?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-b888ef1a-202a-43ad-8065-5cf940be01ea",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "Wo5DNceQ",
      "timestamp": 1743872023.581315
    },
    {
      "invocation_id": "YsuLyxwU",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 16:53:55.248578"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "AvvFYCP4",
      "timestamp": 1743872035.248624
    },
    {
      "content": {
        "parts": [
          {
            "text": "i like a small one!"
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-9459a2c9-711b-4539-afc6-ee46addc0a4d",
      "author": "user",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "gQKd8Sxa",
      "timestamp": 1743872035.312856
    },
    {
      "content": {
        "parts": [
          {
            "function_call": {
              "id": "af-3bfcf4e4-e2f5-4278-ac98-6fa0fc3a22fb",
              "args": {
                "button_name": "small"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-9459a2c9-711b-4539-afc6-ee46addc0a4d",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "I5J98VmU",
      "timestamp": 1743872035.314164
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-3bfcf4e4-e2f5-4278-ac98-6fa0fc3a22fb",
              "name": "click",
              "response": {
                "result": "Back to Search [SEP] < Prev [SEP] color [SEP] black [SEP] blacka [SEP] blackb [SEP] blue [SEP] bluea [SEP] blueb [SEP] coffee [SEP] gray [SEP] green [SEP] hot pink [SEP] navy [SEP] pink [SEP] pinka [SEP] purple [SEP] purplea [SEP] sky blue [SEP] sky bluea [SEP] white [SEP] whitea [SEP] yellow [SEP] yellowa [SEP] size [SEP] small [SEP] medium [SEP] large [SEP] x-large [SEP] xx-large [SEP] Women Summer Cold Shoulder Dress,Beach Vintage Bohemian Print Sundress Party Prom Swing Loose A-Line Dress with Pocket [SEP] Price: $16.29 to $17.59 [SEP] Rating: N.A. [SEP] Description [SEP] Features [SEP] Reviews [SEP] Buy Now"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-9459a2c9-711b-4539-afc6-ee46addc0a4d",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "KpbK2swH",
      "timestamp": 1743872036.590729
    },
    {
      "content": {
        "parts": [
          {
            "text": "You've selected a black, small size dress. Would you like to proceed with the purchase?\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-9459a2c9-711b-4539-afc6-ee46addc0a4d",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "Y8Jroxzo",
      "timestamp": 1743872036.597956
    },
    {
      "invocation_id": "5kCjSNXH",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 16:54:15.487215"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "W4uZjsBE",
      "timestamp": 1743872055.487257
    },
    {
      "content": {
        "parts": [
          {
            "text": "Yes, go ahead :)"
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-c0bb8e86-a3fc-40e1-b834-be59a9fa3fde",
      "author": "user",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "s7s8qsnt",
      "timestamp": 1743872055.550439
    },
    {
      "content": {
        "parts": [
          {
            "function_call": {
              "id": "af-4c565a9a-3020-4521-8828-f652d8663aef",
              "args": {
                "button_name": "Buy Now"
              },
              "name": "click"
            }
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-c0bb8e86-a3fc-40e1-b834-be59a9fa3fde",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "long_running_tool_ids": [],
      "id": "hknqFNuw",
      "timestamp": 1743872055.552167
    },
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "id": "af-4c565a9a-3020-4521-8828-f652d8663aef",
              "name": "click",
              "response": {
                "result": "Thank you for shopping with us! [SEP] Your code: [SEP] None [SEP] (Paste it in your MTurk interface.) [SEP] Purchased [SEP] asin [SEP] B092QL1FLW [SEP] options [SEP] {\"color\": \"black\", \"size\": \"small\"} [SEP] attrs [SEP] None [SEP] category [SEP] None [SEP] query [SEP] None [SEP] product category [SEP] None [SEP] Target [SEP] asin [SEP] options [SEP] attrs [SEP] price upper [SEP] instuction text [SEP] category [SEP] product category [SEP] query [SEP] Goal [SEP] None [SEP] Reward [SEP] Your score (min 0.0, max 1.0) [SEP] 0.0 [SEP] Reward Details [SEP] None"
              }
            }
          }
        ],
        "role": "user"
      },
      "invocation_id": "e-c0bb8e86-a3fc-40e1-b834-be59a9fa3fde",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "TzHtv3Mc",
      "timestamp": 1743872057.028053
    },
    {
      "content": {
        "parts": [
          {
            "text": "Okay, the purchase is being processed. Thank you for shopping with us!\n"
          }
        ],
        "role": "model"
      },
      "invocation_id": "e-c0bb8e86-a3fc-40e1-b834-be59a9fa3fde",
      "author": "personalized_shopping_agent",
      "actions": {
        "state_delta": {},
        "requested_auth_configs": {}
      },
      "id": "sfR6H2FX",
      "timestamp": 1743872057.033816
    },
    {
      "invocation_id": "NHmFZzbG",
      "author": "model",
      "actions": {
        "state_delta": {
          "_time": "2025-04-05 16:54:21.685906"
        },
        "artifact_delta": {},
        "requested_auth_configs": {}
      },
      "id": "lRCbaBdR",
      "timestamp": 1743872061.685947
    }
  ],
  "last_update_time": 1743872061.685947
}
```


---

## 文件: personalized-shopping\tests\tools\test_config.json

```json
{
    "criteria": {
      "tool_trajectory_avg_score": 1.0
    }
  }
```


---

## 文件: personalized-shopping\tests\tools\tools.test.json

```json
[
    {
        "query": "Help me look for women's denim jeans, only return the search results.",
        "expected_tool_use": [
          {
            "tool_name": "search",
            "tool_input": {
              "keywords": "women's denim jeans"
            }
          }
        ],
        "reference": "I found xx results for women's denim jeans."
      }
]
```


---

## 文件: RAG\deployment\deploy.py

```python
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

import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp
from rag.agent import root_agent
import logging
import os
from dotenv import set_key

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")
# Define the path to the .env file relative to this script
ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))

vertexai.init(
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
    staging_bucket=STAGING_BUCKET,
)

# Function to update the .env file
def update_env_file(agent_engine_id, env_file_path):
    """Updates the .env file with the agent engine ID."""
    try:
        set_key(env_file_path, "AGENT_ENGINE_ID", agent_engine_id)
        print(f"Updated AGENT_ENGINE_ID in {env_file_path} to {agent_engine_id}")
    except Exception as e:
        print(f"Error updating .env file: {e}")

logger.info("deploying app...")
app = AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

logging.debug("deploying agent to agent engine:")

remote_app = agent_engines.create(
    app,
    requirements=[
        "google-cloud-aiplatform[adk,agent-engines]==1.88.0",
        "google-adk",
        "python-dotenv",
        "google-auth",
        "tqdm",
        "requests",
    ],
    extra_packages=[
        "./rag",
    ],
)

# log remote_app
logging.info(f"Deployed agent to Vertex AI Agent Engine successfully, resource name: {remote_app.resource_name}")

# Update the .env file with the new Agent Engine ID
update_env_file(remote_app.resource_name, ENV_FILE_PATH)
```


---

## 文件: RAG\deployment\run.py

```python
import os
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv
import json

def pretty_print_event(event):
    """Pretty prints an event with truncation for long content."""
    if "content" not in event:
        print(f"[{event.get('author', 'unknown')}]: {event}")
        return
        
    author = event.get("author", "unknown")
    parts = event["content"].get("parts", [])
    
    for part in parts:
        if "text" in part:
            text = part["text"]
            # Truncate long text to 200 characters
            if len(text) > 200:
                text = text[:197] + "..."
            print(f"[{author}]: {text}")
        elif "functionCall" in part:
            func_call = part["functionCall"]
            print(f"[{author}]: Function call: {func_call.get('name', 'unknown')}")
            # Truncate args if too long
            args = json.dumps(func_call.get("args", {}))
            if len(args) > 100:
                args = args[:97] + "..."
            print(f"  Args: {args}")
        elif "functionResponse" in part:
            func_response = part["functionResponse"]
            print(f"[{author}]: Function response: {func_response.get('name', 'unknown')}")
            # Truncate response if too long
            response = json.dumps(func_response.get("response", {}))
            if len(response) > 100:
                response = response[:97] + "..."
            print(f"  Response: {response}")

load_dotenv()

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)

AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID")

agent_engine = agent_engines.get(AGENT_ENGINE_ID)

session = agent_engine.create_session(user_id="123")

queries = [
    "Hi, how are you?",
    "According to the MD&A, how might the increasing proportion of revenues derived from non-advertising sources like Google Cloud and devices potentially impact Alphabet's overall operating margin, and why?",
    "The report mentions significant investments in AI. What specific connection is drawn between these AI investments and the company's expectations regarding future capital expenditures?",
    "What are the key risks and uncertainties associated with Alphabet's business operations?",
    "Thanks, I got all the information I need. Goodbye!",
]

for query in queries:
    print(f"\n[user]: {query}")
    for event in agent_engine.stream_query(
        user_id="123",
        session_id=session['id'],
        message=query,
    ):
        pretty_print_event(event)

```


---

## 文件: RAG\eval\test_eval.py

```python
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

import os
import pathlib

from google.adk.evaluation.agent_evaluator import AgentEvaluator

import dotenv
import pytest


@pytest.fixture(scope='session', autouse=True)
def load_env():
    dotenv.load_dotenv()


def test_eval_full_conversation():
    """Test the agent's basic ability on a few examples."""
    AgentEvaluator.evaluate(
       agent_module="rag",
       eval_dataset_file_path_or_dir=str(pathlib.Path(__file__).parent / "data/conversation.test.json"),
       num_runs=1,
    )
```


---

## 文件: RAG\eval\data\conversation.test.json

```json
[
  {
    "query": "Hi there, I have some questions about the Alphabet 10-K report.",
    "expected_tool_use": [],
    "reference": "Hello! I can help with that. What would you like to know based on the Alphabet 10-K for the fiscal year ended December 31, 2024?"
  },
  {
    "query": "According to the MD&A, how might the increasing proportion of revenues derived from non-advertising sources like Google Cloud and devices potentially impact Alphabet's overall operating margin, and why?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "How does the growth of non-advertising revenue affect Alphabet's margins?"
        }
      }
    ],
    "reference": "The report states that revenues from cloud, consumer subscriptions, platforms, and devices are increasing. It notes that the margins on these revenues vary significantly and are generally lower than advertising margins. Specifically, device sales adversely affect consolidated margins due to pricing pressure and higher cost of sales. Therefore, this trend may exert downward pressure on the overall operating margin. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Item 7]"
  },
  {
    "query": "The report mentions significant investments in AI. What specific connection is drawn between these AI investments and the company's expectations regarding future capital expenditures?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "Relationship between Alphabet's AI strategy and capital expenditure forecasts"
        }
      }
    ],
    "reference": "The report explicitly states an expectation that capital expenditures will increase, including expected spend and increased technical infrastructure investment, *in particular* to support AI products and services. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Item 7 & Note About Forward-Looking Statements]"
  },
  {
    "query": "Beyond basic functionality issues, what specific legal, ethical, or societal challenges does Alphabet identify in its Risk Factors as potentially arising from the development and use of AI?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "What ethical and legal risks does Alphabet associate with artificial intelligence?"
        }
      }
    ],
    "reference": "The risks mentioned include harmful content, inaccuracies, discrimination, intellectual property infringement/misappropriation, violation of rights of publicity, defamation, data privacy, cybersecurity issues, and unintended consequences or uses potentially affecting human rights, privacy, employment, or other social concerns. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Item 1A]"
  },
  {
    "query": "The report details several ongoing antitrust investigations and lawsuits. Synthesizing the information provided, what common themes or business areas appear to be the primary focus of regulatory scrutiny?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "What areas of Alphabet's business face the most antitrust scrutiny?"
        }
      }
    ],
    "reference": "Common themes of regulatory scrutiny focus on Search and Search advertising distribution/practices, Advertising Technology (ad tech stack), the Android operating system distribution agreements, and Google Play store operations (billing, fees, business model). [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Item 1A & Note 10]"
  },
  {
    "query": "How does Alphabet account for its investments in non-marketable equity securities, and what specific events trigger adjustments to their carrying value according to Note 1?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "Alphabet accounting policy for non-marketable equity securities"
        }
      }
    ],
    "reference": "They are primarily accounted for under the measurement alternative (cost, less impairment, +/- adjustments). Adjustments to carrying value are triggered by observable price changes in orderly transactions for identical or similar investments of the same issuer, or upon impairment identification. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Note 1 & Note 3]"
  },
  {
    "query": "While Google Cloud's operating income turned positive and grew significantly in 2024, what factors mentioned in the MD&A partially offset the revenue growth and moderated the profitability increase?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "Factors limiting Google Cloud profitability growth in 2024"
        }
      }
    ],
    "reference": "The increase in operating income was partially offset by increases in usage costs for technical infrastructure as well as increases in employee compensation expenses, largely driven by headcount growth. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Item 7, Segment Profitability]"
  },
  {
    "query": "Explain the primary reasons for the significant increase in Alphabet's 'Other income (expense), net' from $1.4 billion in 2023 to $7.4 billion in 2024.",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "Drivers of the change in Alphabet's Other Income (Expense), net in 2024"
        }
      }
    ],
    "reference": "The increase was primarily due to an increase in net gains on equity securities (mainly unrealized gains on non-marketable equity securities driven by fair value adjustments) and a decrease in net losses on foreign currency exchange compared to the prior year. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Item 7, Other Income (Expense), Net & Note 7]"
  },
  {
    "query": "What key factors contributed to the increase in Alphabet's effective tax rate from 13.9% in 2023 to 16.4% in 2024?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "Why did Alphabet's effective tax rate increase in 2024?"
        }
      }
    ],
    "reference": "The increase was primarily due to a 2023 one-time adjustment for IRS tax rule changes related to foreign tax credits and R&D capitalization (which lowered the 2023 rate), plus a decrease in the 2024 U.S. federal Foreign Derived Intangible Income deduction. This was partially offset by higher stock-based compensation tax benefits in 2024. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Item 7, Provision for Income Taxes & Note 14]"
  },
  {
    "query": "Regarding the DOJ antitrust lawsuit focused on Search, what was the court's ruling in August 2024, and what are the subsequent steps outlined in the report?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "Status and ruling in the DOJ Search antitrust case against Google"
        }
      }
    ],
    "reference": "The U.S. District Court for the District of Columbia ruled that Google violated antitrust laws related to Search and Search advertising. A separate proceeding is being held to determine remedies. Alphabet intends to appeal after the remedy decision. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Item 1A & Note 10]"
  },
  {
    "query": "What potential challenges does Alphabet acknowledge regarding achieving its ambitious 2030 sustainability goals (net-zero and 24/7 CFE)?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "What uncertainties or difficulties does Alphabet foresee in meeting its climate goals?"
        }
      }
    ],
    "reference": "Challenges include the path not being easy or linear, long lead times for large-scale infrastructure, significant uncertainty (e.g., future environmental impact of AI), dependency on new technology development (by Alphabet and the energy sector), and the expectation that total GHG emissions might rise before dropping toward the target. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Item 1]"
  },
  {
    "query": "How might Alphabet's share repurchase program, as mentioned in the risk factors, potentially influence the relative voting control held by its founders, Larry Page and Sergey Brin?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "Impact of Alphabet share buybacks on founder voting power"
        }
      }
    ],
    "reference": "The risk factor on concentration of ownership explicitly states that share repurchases 'may also affect Larry and Sergey’s relative voting power.' By repurchasing lower-vote Class A or non-voting Class C shares, the proportional voting power of their high-vote Class B shares increases relative to other classes. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Item 1A]"
  },
  {
    "query": "What accounting estimates does Alphabet identify as 'critical' due to the significant level of uncertainty and potential material impact on financial results?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "What are identified as Alphabet's critical accounting estimates?"
        }
      }
    ],
    "reference": "The critical accounting estimates identified are: Fair Value Measurements of Non-Marketable Equity Securities; Property and Equipment (useful lives assessment); Income Taxes (evaluation of uncertain tax positions); and Loss Contingencies (likelihood and estimation of loss). [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Item 7]"
  },
  {
    "query": "Describe Alphabet's strategy for using derivative financial instruments, including the types of risks hedged and the accounting designations applied.",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "Describe Alphabet's derivative hedging strategy and accounting"
        }
      }
    ],
    "reference": "Alphabet uses derivatives, primarily foreign currency contracts, to manage foreign exchange risk. They designate contracts as Cash Flow Hedges for forecasted revenue, Fair Value Hedges for certain foreign currency marketable securities, and Net Investment Hedges for investments in foreign subsidiaries. Non-designated derivatives are used for other exposures like intercompany transactions and for investment purposes. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Note 3 & Item 7A]"
  },
  {
    "query": "What constitutes the majority of Alphabet's $93.2 billion revenue backlog as of year-end 2024, and what is the anticipated timeframe for recognizing roughly half of this amount?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "Details on Alphabet's revenue backlog composition and recognition period"
        }
      }
    ],
    "reference": "The revenue backlog primarily relates to Google Cloud commitments for future services not yet recognized as revenue. Approximately half of this backlog is expected to be recognized as revenue over the next 24 months. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Note 2]"
  },
  {
    "query": "Analyze the change in Google Services operating income from 2023 to 2024. What were the primary positive drivers, and what costs partially offset the increase?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "Analysis of Google Services operating income change in 2024"
        }
      }
    ],
    "reference": "Google Services operating income increased by $25.4 billion. This was primarily driven by an increase in revenues. Factors partially offsetting this included increases in content acquisition costs and Traffic Acquisition Costs (TAC). A reduction in employee compensation expenses also contributed positively to the income increase. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Item 7, Segment Profitability]"
  },
  {
    "query": "The report mentions 'Alphabet-level activities' in its segment reporting. What types of costs are typically included in this category and not allocated to the main segments?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "What costs are included in Alphabet-level activities?"
        }
      }
    ],
    "reference": "Costs included in Alphabet-level activities primarily consist of certain AI-focused shared R&D (like general AI model development), corporate initiatives (e.g., philanthropy), corporate shared costs (some finance, HR, legal functions, certain fines/settlements), charges related to employee severance and office space optimization (during 2023/2024), and hedging gains/losses related to revenue. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Note 15 & Item 7]"
  },
  {
    "query": "Contrast the year-over-year percentage change in 'Paid clicks' versus 'Cost-per-click' for Google Search & other in 2024. What does this suggest about monetization trends in that area?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "Comparison of paid click and cost-per-click growth for Google Search in 2024"
        }
      }
    ],
    "reference": "For Google Search & other in 2024 vs 2023, Paid clicks increased by 5%, while Cost-per-click increased by 7%. This suggests that the average revenue generated per click grew slightly faster than the volume of clicks for these properties during the year. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Item 7, Monetization Metrics]"
  },
  {
    "query": "What is the purpose of the 'measurement alternative' accounting method used for certain non-marketable equity securities, and how does it differ from marking-to-market based purely on estimated fair value each period?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "Explain the 'measurement alternative' accounting for equity securities"
        }
      }
    ],
    "reference": "The measurement alternative measures these securities at cost less impairment, plus or minus adjustments resulting *only* from observable price changes in orderly transactions for identical or similar investments of the same issuer. This differs from marking-to-market based on estimated fair value each period (like public stocks), as adjustments under the measurement alternative only occur upon specific observable events or impairment, reducing period-to-period volatility unless such events occur. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Note 1 & Note 3]"
  },
  {
    "query": "According to the discussion on competition, what types of companies or services represent competitive threats to Google's general-purpose search engine beyond just other search engines?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "What types of competitors does Google Search face besides other search engines?"
        }
      }
    ],
    "reference": "Competitive threats mentioned include vertical search engines and e-commerce providers (where users navigate directly), online advertising platforms and networks (including online shopping and streaming services), social networks (used for product/service referrals), and digital assistant providers. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Item 1]"
  },
  {
    "query": "How does Alphabet assess the recoverability of its long-lived assets like property & equipment and operating lease assets, and what happens if an asset is deemed impaired?",
    "expected_tool_use": [
      {
        "tool_name": "retrieve_rag_documentation",
        "tool_input": {
          "query": "Alphabet's process for testing long-lived assets for impairment"
        }
      }
    ],
    "reference": "Alphabet reviews long-lived assets for impairment when events indicate the carrying amount may not be recoverable. Recoverability is assessed by comparing the carrying amount to the *future undiscounted cash flows* the asset or asset group is expected to generate. If the carrying value is not recoverable, an impairment loss is recognized, measured as the amount by which the carrying value exceeds the asset's *fair value*. [Citation: Based on Alphabet 10-K for FYE Dec 31, 2024, Note 1]"
  },
  {
    "query": "That covers my questions for now. Thanks!",
    "expected_tool_use": [],
    "reference": "You're welcome! Glad I could help. Feel free to ask if anything else comes up."
  }
]
```


---

## 文件: RAG\eval\data\test_config.json

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 0.09,
    "response_match_score": 0.4
  }
}

```


---

## 文件: RAG\rag\agent.py

```python
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

import os

from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

from dotenv import load_dotenv
from .prompts import return_instructions_root

load_dotenv()

ask_vertex_retrieval = VertexAiRagRetrieval(
    name='retrieve_rag_documentation',
    description=(
        'Use this tool to retrieve documentation and reference materials for the question from the RAG corpus,'
    ),
    rag_resources=[
        rag.RagResource(
            # please fill in your own rag corpus
            # here is a sample rag coprus for testing purpose
            # e.g. projects/123/locations/us-central1/ragCorpora/456
            rag_corpus=os.environ.get("RAG_CORPUS")
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='ask_rag_agent',
    instruction=return_instructions_root(),
    tools=[
        ask_vertex_retrieval,
    ]
)
```


---

## 文件: RAG\rag\prompts.py

```python
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

"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the root agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""


def return_instructions_root() -> str:

    instruction_prompt_v1 = """
        You are an AI assistant with access to specialized corpus of documents.
        Your role is to provide accurate and concise answers to questions based
        on documents that are retrievable using ask_vertex_retrieval. If you believe
        the user is just chatting and having casual conversation, don't use the retrieval tool.

        But if the user is asking a specific question about a knowledge they expect you to have,
        you can use the retrieval tool to fetch the most relevant information.
        
        If you are not certain about the user intent, make sure to ask clarifying questions
        before answering. Once you have the information you need, you can use the retrieval tool
        If you cannot provide an answer, clearly explain why.

        Do not answer questions that are not related to the corpus.
        When crafting your answer, you may use the retrieval tool to fetch details
        from the corpus. Make sure to cite the source of the information.
        
        Citation Format Instructions:
 
        When you provide an answer, you must also add one or more citations **at the end** of
        your answer. If your answer is derived from only one retrieved chunk,
        include exactly one citation. If your answer uses multiple chunks
        from different files, provide multiple citations. If two or more
        chunks came from the same file, cite that file only once.

        **How to cite:**
        - Use the retrieved chunk's `title` to reconstruct the reference.
        - Include the document title and section if available.
        - For web resources, include the full URL when available.
 
        Format the citations at the end of your answer under a heading like
        "Citations" or "References." For example:
        "Citations:
        1) RAG Guide: Implementation Best Practices
        2) Advanced Retrieval Techniques: Vector Search Methods"

        Do not reveal your internal chain-of-thought or how you used the chunks.
        Simply provide concise and factual answers, and then list the
        relevant citation(s) at the end. If you are not certain or the
        information is not available, clearly state that you do not have
        enough information.
        """

    instruction_prompt_v0 = """
        You are a Documentation Assistant. Your role is to provide accurate and concise
        answers to questions based on documents that are retrievable using ask_vertex_retrieval. If you believe
        the user is just discussing, don't use the retrieval tool. But if the user is asking a question and you are
        uncertain about a query, ask clarifying questions; if you cannot
        provide an answer, clearly explain why.

        When crafting your answer,
        you may use the retrieval tool to fetch code references or additional
        details. Citation Format Instructions:
 
        When you provide an
        answer, you must also add one or more citations **at the end** of
        your answer. If your answer is derived from only one retrieved chunk,
        include exactly one citation. If your answer uses multiple chunks
        from different files, provide multiple citations. If two or more
        chunks came from the same file, cite that file only once.

        **How to
        cite:**
        - Use the retrieved chunk's `title` to reconstruct the
        reference.
        - Include the document title and section if available.
        - For web resources, include the full URL when available.
 
        Format the citations at the end of your answer under a heading like
        "Citations" or "References." For example:
        "Citations:
        1) RAG Guide: Implementation Best Practices
        2) Advanced Retrieval Techniques: Vector Search Methods"

        Do not
        reveal your internal chain-of-thought or how you used the chunks.
        Simply provide concise and factual answers, and then list the
        relevant citation(s) at the end. If you are not certain or the
        information is not available, clearly state that you do not have
        enough information.
        """

    return instruction_prompt_v1

```


---

## 文件: RAG\rag\shared_libraries\prepare_corpus_and_data.py

```python
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

from google.auth import default
import vertexai
from vertexai.preview import rag
import os
from dotenv import load_dotenv, set_key
import requests
import tempfile

# Load environment variables from .env file
load_dotenv()

# --- Please fill in your configurations ---
# Retrieve the PROJECT_ID from the environmental variables.
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError(
        "GOOGLE_CLOUD_PROJECT environment variable not set. Please set it in your .env file."
    )
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
if not LOCATION:
    raise ValueError(
        "GOOGLE_CLOUD_LOCATION environment variable not set. Please set it in your .env file."
    )
CORPUS_DISPLAY_NAME = "Alphabet_10K_2024_corpus"
CORPUS_DESCRIPTION = "Corpus containing Alphabet's 10-K 2024 document"
PDF_URL = "https://abc.xyz/assets/77/51/9841ad5c4fbe85b4440c47a4df8d/goog-10-k-2024.pdf"
PDF_FILENAME = "goog-10-k-2024.pdf"
ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


# --- Start of the script ---
def initialize_vertex_ai():
  credentials, _ = default()
  vertexai.init(
      project=PROJECT_ID, location=LOCATION, credentials=credentials
  )


def create_or_get_corpus():
  """Creates a new corpus or retrieves an existing one."""
  embedding_model_config = rag.EmbeddingModelConfig(
      publisher_model="publishers/google/models/text-embedding-004"
  )
  existing_corpora = rag.list_corpora()
  corpus = None
  for existing_corpus in existing_corpora:
    if existing_corpus.display_name == CORPUS_DISPLAY_NAME:
      corpus = existing_corpus
      print(f"Found existing corpus with display name '{CORPUS_DISPLAY_NAME}'")
      break
  if corpus is None:
    corpus = rag.create_corpus(
        display_name=CORPUS_DISPLAY_NAME,
        description=CORPUS_DESCRIPTION,
        embedding_model_config=embedding_model_config,
    )
    print(f"Created new corpus with display name '{CORPUS_DISPLAY_NAME}'")
  return corpus


def download_pdf_from_url(url, output_path):
  """Downloads a PDF file from the specified URL."""
  print(f"Downloading PDF from {url}...")
  response = requests.get(url, stream=True)
  response.raise_for_status()  # Raise an exception for HTTP errors
  
  with open(output_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
      f.write(chunk)
  
  print(f"PDF downloaded successfully to {output_path}")
  return output_path


def upload_pdf_to_corpus(corpus_name, pdf_path, display_name, description):
  """Uploads a PDF file to the specified corpus."""
  print(f"Uploading {display_name} to corpus...")
  try:
    rag_file = rag.upload_file(
        corpus_name=corpus_name,
        path=pdf_path,
        display_name=display_name,
        description=description,
    )
    print(f"Successfully uploaded {display_name} to corpus")
    return rag_file
  except Exception as e:
    print(f"Error uploading file {display_name}: {e}")
    return None

def update_env_file(corpus_name, env_file_path):
    """Updates the .env file with the corpus name."""
    try:
        set_key(env_file_path, "RAG_CORPUS", corpus_name)
        print(f"Updated RAG_CORPUS in {env_file_path} to {corpus_name}")
    except Exception as e:
        print(f"Error updating .env file: {e}")

def list_corpus_files(corpus_name):
  """Lists files in the specified corpus."""
  files = list(rag.list_files(corpus_name=corpus_name))
  print(f"Total files in corpus: {len(files)}")
  for file in files:
    print(f"File: {file.display_name} - {file.name}")


def main():
  initialize_vertex_ai()
  corpus = create_or_get_corpus()

  # Update the .env file with the corpus name
  update_env_file(corpus.name, ENV_FILE_PATH)
  
  # Create a temporary directory to store the downloaded PDF
  with tempfile.TemporaryDirectory() as temp_dir:
    pdf_path = os.path.join(temp_dir, PDF_FILENAME)
    
    # Download the PDF from the URL
    download_pdf_from_url(PDF_URL, pdf_path)
    
    # Upload the PDF to the corpus
    upload_pdf_to_corpus(
        corpus_name=corpus.name,
        pdf_path=pdf_path,
        display_name=PDF_FILENAME,
        description=f"Alphabet's 10-K 2024 document"
    )
  
  # List all files in the corpus
  list_corpus_files(corpus_name=corpus.name)

if __name__ == "__main__":
  main()

```


---

## 文件: travel-concierge\deployment\deploy.py

```python
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

"""Deployment script for Travel Concierge."""

import os

from absl import app, flags
from dotenv import load_dotenv
from travel_concierge.agent import root_agent
import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP bucket.")

flags.DEFINE_string(
    "initial_states_path",
    None,
    "Relative path to the initial state file, .e.g eval/itinerary_empty_default.json",
)
flags.DEFINE_string("map_key", None, "API Key for Google Places API")

flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")
flags.DEFINE_bool("create", False, "Creates a new deployment.")
flags.DEFINE_bool("quicktest", False, "Try a new deployment with one turn.")
flags.DEFINE_bool("delete", False, "Deletes an existing deployment.")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete", "quicktest"])


def create(env_vars: dict[str, str]) -> None:
    """Creates a new deployment."""
    print(env_vars)
    app = AdkApp(
        agent=root_agent,
        enable_tracing=True,
        env_vars=env_vars,
    )

    remote_agent = agent_engines.create(
        app,
        requirements=[
            "google-adk (>=0.0.2)",
            "google-cloud-aiplatform[agent_engines] @ git+https://github.com/googleapis/python-aiplatform.git@copybara_738852226",
            "google-genai (>=1.5.0,<2.0.0)",
            "pydantic (>=2.10.6,<3.0.0)",
            "absl-py (>=2.2.1,<3.0.0)",
            "pydantic (>=2.10.6,<3.0.0)",
            "requests (>=2.32.3,<3.0.0)",
        ],
        extra_packages=[
            "./travel_concierge",  # The main package
            "./eval",  # The initial state files
        ],
    )
    print(f"Created remote agent: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    remote_agent = agent_engines.get(resource_id)
    remote_agent.delete(force=True)
    print(f"Deleted remote agent: {resource_id}")


def send_message(resource_id: str, message: str) -> None:
    """Send a message to the deployed agent."""
    remote_agent = agent_engines.get(resource_id)
    session = remote_agent.create_session(
        user_id="traveler0115"
    )  # Optionally can provide initial states: state=initial_state
    print(f"Trying remote agent: {resource_id}")
    for event in remote_agent.stream_query(
        user_id="traveler0115",
        session_id=session["id"],
        message=message,
    ):
        print(event)
    print("Done.")


def main(argv: list[str]) -> None:

    load_dotenv()
    env_vars = {}

    project_id = (
        FLAGS.project_id if FLAGS.project_id else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = FLAGS.bucket if FLAGS.bucket else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
    # Variables for Travel Concierge from .env
    initial_states_path = (
        FLAGS.initial_states_path
        if FLAGS.initial_states_path
        else os.getenv("TRAVEL_CONCIERGE_SCENARIO")
    )
    env_vars["TRAVEL_CONCIERGE_SCENARIO"] = initial_states_path
    map_key = (
        FLAGS.initial_states_path
        if FLAGS.initial_states_path
        else os.getenv("GOOGLE_PLACES_API_KEY")
    )
    env_vars["GOOGLE_PLACES_API_KEY"] = map_key

    print(f"PROJECT: {project_id}")
    print(f"LOCATION: {location}")
    print(f"BUCKET: {bucket}")
    print(f"INITIAL_STATE: {initial_states_path}")
    print(f"MAP: {map_key[:5]}")

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print("Missing required environment variable: GOOGLE_CLOUD_STORAGE_BUCKET")
        return
    elif not initial_states_path:
        print("Missing required environment variable: TRAVEL_CONCIERGE_SCENARIO")
        return
    elif not map_key:
        print("Missing required environment variable: GOOGLE_PLACES_API_KEY")
        return

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    if FLAGS.create:
        create(env_vars)
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("resource_id is required for delete")
            return
        delete(FLAGS.resource_id)
    elif FLAGS.quicktest:
        if not FLAGS.resource_id:
            print("resource_id is required for quicktest")
            return
        send_message(FLAGS.resource_id, "Looking for inspirations around the Americas")
    else:
        print("Unknown command")


if __name__ == "__main__":
    app.run(main)

```


---

## 文件: travel-concierge\eval\itinerary_empty_default.json

```json
{
  "state": {
    "user_profile" : {
      "passport_nationality" : "US Citizen",
      "seat_preference": "window",
      "food_preference": "vegan",
      "allergies": [],
      "likes": [],
      "dislikes": [],
      "price_sensitivity": [],    
      "home":
      {
          "event_type": "home",
          "address": "6420 Sequence Dr #400, San Diego, CA 92121, United States",
          "local_prefer_mode": "drive"
      }    
    },
    "itinerary": {},
    "origin" : "",
    "destination" : "",
    "start_date" : "",
    "end_date" : "",
    "outbound_flight_selection" : "",
    "outbound_seat_number" : "",
    "return_flight_selection" : "",
    "return_seat_number" : "",
    "hotel_selection" : "",
    "room_selection" : "",
    "poi" : "",
    "itinerary_datetime" : "",
    "itinerary_start_date" : "",
    "itinerary_end_date" : ""  
  }
}
```


---

## 文件: travel-concierge\eval\itinerary_seattle_example.json

```json
{
  "state": {
    "user_profile" : {
      "passport_nationality" : "US Citizen",
      "seat_preference": "window",
      "food_preference": "vegan",
      "allergies": [],
      "likes": [],
      "dislikes": [],
      "price_sensitivity": [],    
      "home":
      {
        "event_type": "home",
        "address": "6420 Sequence Dr #400, San Diego, CA 92121, United States",
        "local_prefer_mode": "drive"
      }  
    },
    "itinerary": {
      "trip_name": "San Diego to Seattle Getaway",
      "start_date": "2025-06-15",
      "end_date": "2025-06-17",
      "origin": "San Diego",
      "destination": "Seattle",
      "days": [
        {
          "day_number": 1,
          "date": "2025-06-15",
          "events": [
            {
              "event_type": "flight",
              "description": "Flight from San Diego to Seattle",
              "flight_number": "AA1234",
              "departure_airport": "SAN",
              "arrival_airport": "SEA",
              "departure_time": "08:00",
              "boarding_time": "07:30",
              "seat_number": "22A",
              "booking_required": true,
              "booking_id": "ABC-123-XYZ"
            }
          ]
        },
        {
          "day_number": 2,
          "date": "2025-06-16",
          "events": [
            {
              "event_type": "visit",
              "description": "Visit Pike Place Market",
              "location": {
                "name": "Pike Place Market",
                "address": "85 Pike St, Seattle, WA 98101",
                "latitude": "47.6097",
                "longitude": "-122.3422"
              },
              "start_time": "09:00",
              "end_time": "12:00",
              "booking_required": false
            },
            {
              "event_type": "visit",
              "description": "Lunch at Ivar's Acres of Clams",
              "location": {
                "name": "Ivar's Acres of Clams",
                "address": "1001 Alaskan Way, Pier 54, Seattle, WA 98104",
                "latitude": "47.6029",
                "longitude": "-122.3398"
              },
              "start_time": "12:30",
              "end_time": "13:30",
              "booking_required": false
            },
            {
              "event_type": "visit",
              "description": "Visit the Space Needle",
              "location": {
                "name": "Space Needle",
                "address": "400 Broad St, Seattle, WA 98109",
                "latitude": "47.6205",
                "longitude": "-122.3492"
              },
              "start_time": "14:30",
              "end_time": "16:30",
              "booking_required": true,
              "booking_id": "DEF-456-UVW"
            },
            {
              "event_type": "visit",
              "description": "Dinner in Capitol Hill",
              "location": {
                "name": "Capitol Hill Neighborhood",
                "address": "Capitol Hill, Seattle, WA",
                "latitude": "47.6234",
                "longitude": "-122.3175"
              },
              "start_time": "19:00",
              "end_time": "21:00",
              "booking_required": false
            }
          ]
        },
        {
          "day_number": 3,
          "date": "2025-06-17",
          "events": [
            {
              "event_type": "visit",
              "description": "Visit the Museum of Pop Culture (MoPOP)",
              "location": {
                "name": "Museum of Pop Culture (MoPOP)",
                "address": "325 5th Ave N, Seattle, WA 98109",
                "latitude": "47.6212",
                "longitude": "-122.3472"
              },
              "start_time": "10:00",
              "end_time": "13:00",
              "booking_required": true,
              "booking_id": "GHI-789-PQR"
            },
            {
              "event_type":"flight",
              "description": "Return Flight from Seattle to San Diego",
              "flight_number": "UA5678",
              "departure_airport": "SEA",
              "arrival_airport": "SAN",
              "departure_time": "16:00",
              "boarding_time": "15:30",
              "seat_number": "10F",
              "booking_required": true,
              "booking_id": "LMN-012-STU"
            }
          ]
        }
      ]
    },
    "origin": "San Diego",
    "destination": "Seattle",    
    "start_date": "2025-06-15",
    "end_date": "2025-06-17",    
    "outbound_flight_selection" : "",
    "outbound_seat_number" : "",
    "return_flight_selection" : "",
    "return_seat_number" : "",
    "hotel_selection" : "",
    "room_selection" : "",
    "poi" : "",
    "itinerary_datetime" : "",
    "itinerary_start_date" : "2025-06-15",
    "itinerary_end_date" : "2025-06-17"    
  }
}
```


---

## 文件: travel-concierge\eval\test_eval.py

```python
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

"""Basic evaluation of the travel concierge agent."""

import pathlib

import dotenv
from google.adk.evaluation import AgentEvaluator
import pytest


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


def test_inspire():
    """Test the agent's basic ability on a few examples."""
    AgentEvaluator.evaluate(
        "travel_concierge",
        str(pathlib.Path(__file__).parent / "data/inspire.test.json"),
        num_runs=4,
        initial_session_file=str(pathlib.Path(__file__).parent
                                 / "itinerary_empty_default.json")
    )


def test_pretrip():
    """Test the agent's basic ability on a few examples."""
    AgentEvaluator.evaluate(
        "travel_concierge",
        str(pathlib.Path(__file__).parent / "data/pretrip.test.json"),
        num_runs=4,
        initial_session_file=str(pathlib.Path(__file__).parent
                                 / "itinerary_seattle_example.json")
    )


def test_intrip():
    """Test the agent's basic ability on a few examples."""
    AgentEvaluator.evaluate(
        "travel_concierge",
        str(pathlib.Path(__file__).parent / "data/intrip.test.json"),
        num_runs=4,
        initial_session_file=str(pathlib.Path(__file__).parent
                                 / "itinerary_seattle_example.json")
    )
    
```


---

## 文件: travel-concierge\eval\data\inspire.test.json

```json
[
  {
    "query": "Inspire me about the Americas",
    "expected_tool_use": [
      {
        "tool_name": "transfer_to_agent",
        "tool_input": {
          "agent_name":"inspiration_agent"
        }
      },
      {
        "tool_name": "place_agent",
        "tool_input": {
          "request":"Americas"
        }
      }
    ],
    "reference": "Okay, I have a few ideas for you! How about:\n\n*   **Machu Picchu, Peru:** An ancient Inca citadel set high in the Andes Mountains.\n*   **Banff National Park, Canada:** Home to majestic mountains and turquoise lakes.\n*   **New York City, USA:** An iconic metropolis with world-class museums and diverse cuisine.\n\nAre any of these destinations of particular interest to you? I can provide more details on activities and attractions.\n"
  },
  {
    "query": "Tell me more what I can do in Peru",
    "expected_tool_use": [
      {
        "tool_name": "poi_agent",
        "tool_input": {
          "request":"Peru"
        }
      },
      {
        "tool_name": "map_tool", 
        "tool_input": {
          "key": "poi"
        }
      }      
    ],
    "reference": "Peru is a land of incredible history and natural beauty! You could:\n\n*   **Explore Machu Picchu:** Hike through the iconic Inca citadel and marvel at its architectural genius.\n*   **Visit Rainbow Mountain:** Trek through vibrant, colorful landscapes.\n*   **Discover Lake Titicaca:** Explore the highest navigable lake in South America and visit the unique Uros floating islands.\n*   **Explore Sacsayhuamán:** Roam through this Inca fortress with massive stone walls.\n*   **Fly over the Nazca Lines:** Take a flight to witness the mysterious geoglyphs etched into the desert sands.\n\nGiven your vegan food preference, you'll be happy to know that many restaurants in Peru offer vegan options, especially in larger cities like Cusco and Lima.\n\nWhich of these activities sounds most appealing? Or is there anything else about Peru you're curious about?\n"
  },
  {
    "query": "Start planning",
    "expected_tool_use": [
      {
        "tool_name": "transfer_to_agent",
        "tool_input": {
          "agent_name":"planning_agent"
        }
      } 
    ],
    "reference": "Okay, let's start planning your trip to Peru! Based on your interest in Peru, I'll plan a trip centered around Machu Picchu, Rainbow Mountain, Lake Titicaca, Sacsayhuamán, and the Nazca Lines.\n\nFirst, I need a little more information to create the perfect itinerary.\n\n*   **Origin:** Where will you be departing from?\n*   **Start Date:** When would you like to begin your trip?\n*   **End Date:** How many days would you like your trip to last?\n"
  }      
]
```


---

## 文件: travel-concierge\eval\data\intrip.test.json

```json
[
  {
    "query": "transfer to in_trip",
    "expected_tool_use": [
      {
        "tool_name": "transfer_to_agent",
        "tool_input": {
          "agent_name":"in_trip_agent"
        }
      }
    ],
    "expected_intermediate_agent_responses" : [],
    "reference":"Okay, I am now in charge. How can I help you with your trip? I can provide information about your itinerary, help with transportation, or offer details about the attractions you're visiting."
  },
  {
    "query": "monitor",
    "expected_tool_use": [
      {
        "tool_name": "transfer_to_agent",
        "tool_input": {
          "agent_name":"trip_monitor_agent"
        }
      },      
      {
        "tool_name": "flight_status_check",
        "tool_input": {
          "departure_time":"08:00",
          "flight_number":"AA1234",
          "flight_date":"2025-06-15",
          "checkin_time":"07:30"
          }
      },
      {
        "tool_name": "flight_status_check",
        "tool_input": {
          "departure_time":"16:00",
          "flight_number":"UA5678",
          "flight_date":"2025-06-17",
          "checkin_time":"15:30"
          }        
      },
      {
        "tool_name": "event_booking_check",
        "tool_input": {
          "event_location":"Space Needle",
          "event_name":"Space Needle",
          "event_date":"2025-06-16"
          }        
      },
      {
        "tool_name": "event_booking_check",
        "tool_input": {
          "event_date":"2025-06-17",
          "event_location":"Museum of Pop Culture (MoPOP)",
          "event_name":"Museum of Pop Culture (MoPOP)"
          }        
      },
      {
        "tool_name": "weather_impact_check",
        "tool_input": {
          "activity_date":"2025-06-16",
          "activity_location":"Pike Place Market",
          "activity_name":"Visit Pike Place Market"
          }      
      },
      {
        "tool_name": "weather_impact_check",
        "tool_input": {
          "activity_location":"Ivar's Acres of Clams",
          "activity_name":"Lunch at Ivar's Acres of Clams",
          "activity_date":"2025-06-16"
          }        
      },
      {
        "tool_name": "weather_impact_check",
        "tool_input": {
          "activity_location":"Capitol Hill Neighborhood",
          "activity_date":"2025-06-16",
          "activity_name":"Dinner in Capitol Hill"
          }        
      },
      {
        "tool_name": "transfer_to_agent",
        "tool_input": {
          "agent_name":"in_trip_agent"
        }
      }      
    ],
    "expected_intermediate_agent_responses" : [
      "Okay, I will monitor your itinerary and identify potential issues. Let's start!\n\nFirst, I'll identify the different types of events in your itinerary and note their details.\n\n**Flights:**\n\n*   **Flight 1:** San Diego to Seattle on 2025-06-15, Flight number AA1234, Check-in time 07:30, Departure time 08:00.\n*   **Flight 2:** Seattle to San Diego on 2025-06-17, Flight number UA5678, Check-in time 15:30, Departure time 16:00.\n\n**Events requiring booking:**\n\n*   Visit the Space Needle on 2025-06-16 at Space Needle.\n*   Visit the Museum of Pop Culture (MoPOP) on 2025-06-17 at Museum of Pop Culture (MoPOP).\n\n**Activities/Visits that may be impacted by weather:**\n\n*   Visit Pike Place Market on 2025-06-16 at Pike Place Market.\n*   Lunch at Ivar's Acres of Clams on 2025-06-16 at Ivar's Acres of Clams.\n*   Dinner in Capitol Hill on 2025-06-16 at Capitol Hill Neighborhood.\n\nNow, I will check the status of each of these events using the available tools.",
      "Here's a summary of suggested changes for your attention:\n\n*   The Space Needle is closed on 2025-06-16, suggest finding alternatives.\n\nI am now transferring you back to the `in_trip_agent` to handle your other needs."
    ],
    "reference": "OK. It looks like the Space Needle is closed on June 16, 2025. Would you like me to help you find an alternative activity for that time?"
  },
  {
    "query": "memorize the date '2025-06-16 12:45:00' and store it in the variable 'itinerary_datetime'",
    "expected_tool_use": [
      {
        "tool_name": "memorize",
        "tool_input": {
          "key":"itinerary_datetime",
          "value":"2025-06-16 12:45:00"
          }
      }
    ],
    "expected_intermediate_agent_responses" : [],
    "reference":"OK. I have stored the date '2025-06-16 12:45:00' in the variable 'itinerary_datetime'."
  },
  {
    "query": "call day_of for transport help",
    "expected_tool_use": [
      {
        "tool_name": "day_of_agent",
        "tool_input": {
          "request":"help"
        }
      }     
    ],
    "expected_intermediate_agent_responses" : [],
    "reference":"Okay, it looks like you can walk from Ivar's Acres of Clams to the Space Needle in about 25-30 minutes, or take a rideshare which would be much faster."
  }
]
```


---

## 文件: travel-concierge\eval\data\pretrip.test.json

```json
[
  {
    "query": "transfer to pre_trip",
    "expected_tool_use": [
      {
        "tool_name": "transfer_to_agent",
        "tool_input": {
          "agent_name":"pre_trip_agent"
        }
      }
    ],
    "expected_intermediate_agent_responses" : [],
    "reference": "Okay, I am now the pre-trip agent. I see you have a trip planned from San Diego to Seattle from June 15, 2025 to June 17, 2025. I also see you are a US Citizen."
  },
  {
    "query": "update",
    "expected_tool_use": [
      {
        "tool_name": "google_search_grounding",
        "tool_input": {
          "request":"visa_requirements for a US Citizen traveling from San Diego to Seattle"
        }        
      },
      {
        "tool_name": "google_search_grounding",
        "tool_input": {
          "request":"medical_requirements for travel from San Diego to Seattle"
        }        
      },
      {
        "tool_name": "google_search_grounding",
        "tool_input": {
          "request":"storm_monitor for Seattle in June"
        }        
      },
      {
        "tool_name": "google_search_grounding",
        "tool_input": {
          "request":"travel_advisory for Seattle"
        }        
      },
      {
        "tool_name": "what_to_pack_agent",
        "tool_input": {
          "request":"Seattle in June"
        }        
      }
    ],
    "expected_intermediate_agent_responses" : [
      "- **Visa:** As a US citizen traveling from San Diego to Seattle, you don't need a visa. However, starting May 7, 2025, you'll need a REAL ID-compliant license or another acceptable form of identification (like a passport) for domestic flights.",
      "- **Medical:** Ensure you have a REAL ID-compliant driver's license or another acceptable form of identification like a U.S. passport. Check with your airline for any specific requirements.",
      "- **Storm Update:** I am unable to monitor storms specifically.",
      "- **Travel Advisory:** Seattle is generally safe, but be aware of petty crime, especially in tourist areas, and take normal security precautions.",
      "- **What to Pack:** I suggest bringing a light jacket, umbrella, comfortable walking shoes, and layers of clothing."
    ],
    "reference": "Here are the important information for your trip:\n\n- **Visa:** As a US citizen traveling domestically from San Diego to Seattle, you do not need a visa.\n- **Medical:** Ensure your routine vaccinations are up to date, including the flu shot, and consult your doctor about any personal medical concerns or necessary prescription refills.\n- **Storm Update:** In Seattle during June, expect moderately warm weather with average high temperatures increasing from 69°F to 74°F, and be prepared for rainfall on approximately 8 days of the month.\n- **Travel Advisory:** For up-to-date travel alerts and advisories in Seattle, consult the SDOT Blog for information on construction, events, and traffic, and check the Washington State Tourism website for alerts related to transportation, wildfires, and natural impacts.\n- **What to Pack:** I suggest bringing a light jacket, umbrella, comfortable walking shoes, and layers of clothing.\n"
  }
]
```


---

## 文件: travel-concierge\eval\data\test_config.json

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 0.1,
    "response_match_score": 0.1
  }
}
```


---

## 文件: travel-concierge\tests\mcp_abnb.py

```python
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

"""An example of the travel-concierge agents incorporating an MCP tool."""

import asyncio
import json

from dotenv import load_dotenv
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.genai import types
from travel_concierge.agent import root_agent


load_dotenv()


async def get_tools_async():
    """Gets tools from MCP Server."""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command="npx",
            args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
        )
    )
    # MCP requires maintaining a connection to the local MCP Server.
    # Using exit_stack to clean up server connection before exit.
    return tools, exit_stack


def find_agent(agent, targat_name):
    """A convenient function to find an agent from an existing agent graph."""
    result = None
    print("Matching...", agent.name)
    if agent.name == targat_name:
        return agent
    for sub_agent in agent.sub_agents:
        result = find_agent(sub_agent, targat_name)
        if result:
            break
    for tool in agent.tools:
        if isinstance(tool, AgentTool):
            result = find_agent(tool.agent, targat_name)
            if result:
                break
    return result


async def get_agent_async():
    """Creates an ADK Agent with tools from MCP Server."""
    tools, exit_stack = await get_tools_async()
    print("\nInserting Airbnb MCP tools into Travel-Concierge...")
    planner = find_agent(root_agent, "planning_agent")
    if planner:
        print("FOUND", planner.name)
        planner.tools.extend(tools)
    else:
        print("NOT FOUND")
    return root_agent, exit_stack


async def async_main(question):
    """Executes one turn of the travel_concierge agents with a query that would trigger the MCP tool."""
    session_service = InMemorySessionService()
    artifacts_service = InMemoryArtifactService()
    session = session_service.create_session(
        state={}, app_name="travel-concierge", user_id="traveler0115"
    )

    query = question
    print("[user]: ", query)
    content = types.Content(role="user", parts=[types.Part(text=query)])

    agent, exit_stack = await get_agent_async()
    runner = Runner(
        app_name="travel-concierge",
        agent=agent,
        artifact_service=artifacts_service,
        session_service=session_service,
    )

    events_async = runner.run_async(
        session_id=session.id, user_id="traveler0115", new_message=content
    )

    # Results Handling
    # print(events_async)
    async for event in events_async:
        # {'error': 'Function activities_agent is not found in the tools_dict.'}
        if not event.content:
            continue

        # print(event)
        author = event.author
        # Uncomment this to see the full event payload
        # print(f"\n[{author}]: {json.dumps(event)}")

        function_calls = [
            e.function_call for e in event.content.parts if e.function_call
        ]
        function_responses = [
            e.function_response for e in event.content.parts if e.function_response
        ]

        if event.content.parts[0].text:
            text_response = event.content.parts[0].text
            print(f"\n[{author}]: {text_response}")

        if function_calls:
            for function_call in function_calls:
                print(
                    f"\n[{author}]: {function_call.name}( {json.dumps(function_call.args)} )"
                )

        elif function_responses:
            for function_response in function_responses:
                function_name = function_response.name
                # Detect different payloads and handle accordingly
                application_payload = function_response.response
                if function_name == "airbnb_search":
                    application_payload = application_payload["result"].content[0].text
                print(
                    f"\n[{author}]: {function_name} responds -> {application_payload}"
                )

    await exit_stack.aclose()


if __name__ == "__main__":
    asyncio.run(
        async_main(
            (
                "Find me an airbnb in San Diego, April 9th, to april 13th, no flights nor itinerary needed. "
                "No need to confirm, simply return 5 choicess, remember to include urls."
            )
        )
    )

```


---

## 文件: travel-concierge\tests\programmatic_example.py

```python
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

"""This is a rudimentary example showing how to interact with an ADK agent as a server end point."""

import json
import requests

#
# This client connects to an existing end point created by running `adk api_server <agent package>`
# This client also illustrates how one can use the adk events streamed from the server side to inform user interface components.
#

# Endpoint created by running `adk api_server travel_concierge``
RUN_ENDPOINT = "http://127.0.0.1:8000/run_sse"
HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "text/event-stream",
}

# Create a session if it doesn't exist
SESSION_ENDPOINT = "http://127.0.0.1:8000/apps/travel_concierge/users/traveler0115/sessions/session_2449"
response = requests.post(SESSION_ENDPOINT)
print("Session", response.json())

# We are going to run just two turns with the concierge
user_inputs = [
    "Inspire me about the Maldives",
    "Show me a few activites around Baa Atoll",
]

for user_input in user_inputs:

    DATA = {
        "session_id": "session_2449",
        "app_name": "travel_concierge",
        "user_id": "traveler0115",
        "new_message": {
            "role": "user",
            "parts": [
                {
                    "text": user_input,
                }
            ],
        },
    }

    print(f'\n[user]: "{user_input}"')

    with requests.post(
        RUN_ENDPOINT, data=json.dumps(DATA), headers=HEADERS, stream=True
    ) as r:
        for chunk in r.iter_lines():  # or, for line in r.iter_lines():
            # These events and its content can be inspected and leveraged.
            # This under-pins application integration;
            if not chunk:
                continue
            json_string = chunk.decode("utf-8").removeprefix("data: ").strip()
            event = json.loads(json_string)

            # {'error': 'Function activities_agent is not found in the tools_dict.'}
            if "content" not in event:
                print(event)
                continue

            author = event["author"]
            # Uncomment this to see the full event payload
            # print(f"\n[{author}]: {json.dumps(event)}")
            # continue

            function_calls = [
                e["functionCall"]
                for e in event["content"]["parts"]
                if "functionCall" in e
            ]
            function_responses = [
                e["functionResponse"]
                for e in event["content"]["parts"]
                if "functionResponse" in e
            ]

            if "text" in event["content"]["parts"][0]:
                text_response = event["content"]["parts"][0]["text"]
                print(f"\n{author} {text_response}")

            if function_calls:
                for function_call in function_calls:
                    name = function_call["name"]
                    args = function_call["args"]
                    print(
                        f'\n{author}\nfunction call: "{name}"\nargs: {json.dumps(args,indent=2)}\n'
                    )

            elif function_responses:
                for function_response in function_responses:
                    function_name = function_response["name"]
                    application_payload = json.dumps(
                        function_response["response"], indent=2
                    )
                    print(
                        f'\n{author}\nResponse from: "{name}"\nresponse: {application_payload}\n'
                    )

                    # A switch case statement against the function_name allows
                    # an application to act according to which agent / tool the response originated from.
                    match function_name:
                        case "place_agent":
                            print("\n[app]: To render a carousel of destinations")
                        case "map_tool":
                            print("\n[app]: To render a map of pois")
                        case "flight_selection_agent":
                            print("\n[app]: Render a list")
                        case "hotel_selection_agent":
                            print("\n[app]: Render a list")
                    # ... etc

```


---

## 文件: travel-concierge\tests\unit\test_tools.py

```python
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

"""Basic tests for individual tools."""

import unittest

from dotenv import load_dotenv
from google.adk.agents.invocation_context import InvocationContext
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
import pytest
from travel_concierge.agent import root_agent
from travel_concierge.tools.memory import memorize
from travel_concierge.tools.places import map_tool


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()


session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()


class TestAgents(unittest.TestCase):
    """Test cases for the Travel Concierge cohort of agents."""

    def setUp(self):
        """Set up for test methods."""
        super().setUp()
        self.session = session_service.create_session(
            app_name="Travel_Concierge",
            user_id="traveler0115",
        )
        self.user_id = "traveler0115"
        self.session_id = self.session.id

        self.invoc_context = InvocationContext(
            session_service=session_service,
            invocation_id="ABCD",
            agent=root_agent,
            session=self.session,
        )
        self.tool_context = ToolContext(invocation_context=self.invoc_context)

    def test_memory(self):
        result = memorize(
            key="itinerary_datetime",
            value="12/31/2025 11:59:59",
            tool_context=self.tool_context,
        )
        self.assertIn("status", result)
        self.assertEqual(
            self.tool_context.state["itinerary_datetime"], "12/31/2025 11:59:59"
        )

    def test_places(self):
        self.tool_context.state["poi"] = {
            "places": [{"place_name": "Machu Picchu", "address": "Machu Picchu, Peru"}]
        }
        result = map_tool(key="poi", tool_context=self.tool_context)
        print(result)
        self.assertIn("place_id", result[0])
        self.assertEqual(
            self.tool_context.state["poi"]["places"][0]["place_id"],
            "ChIJVVVViV-abZERJxqgpA43EDo",
        )

```


---

## 文件: travel-concierge\travel_concierge\agent.py

```python
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

"""Demonstration of Travel AI Conceirge using Agent Development Kit"""

from google.adk.agents import Agent

from travel_concierge import prompt

from travel_concierge.sub_agents.booking.agent import booking_agent
from travel_concierge.sub_agents.in_trip.agent import in_trip_agent
from travel_concierge.sub_agents.inspiration.agent import inspiration_agent
from travel_concierge.sub_agents.planning.agent import planning_agent
from travel_concierge.sub_agents.post_trip.agent import post_trip_agent
from travel_concierge.sub_agents.pre_trip.agent import pre_trip_agent

from travel_concierge.tools.memory import _load_precreated_itinerary


root_agent = Agent(
    model="gemini-2.0-flash-001",
    name="root_agent",
    description="A Travel Conceirge using the services of multiple sub-agents",
    instruction=prompt.ROOT_AGENT_INSTR,
    sub_agents=[
        inspiration_agent,
        planning_agent,
        booking_agent,
        pre_trip_agent,
        in_trip_agent,
        post_trip_agent,
    ],
    before_agent_callback=_load_precreated_itinerary,
)

```


---

## 文件: travel-concierge\travel_concierge\prompt.py

```python
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

"""Defines the prompts in the travel ai agent."""

ROOT_AGENT_INSTR = """
- You are a exclusive travel conceirge agent
- You help users to discover their dream vacation, planning for the vacation, book flights and hotels
- You want to gather a minimal information to help the user
- After every tool call, pretend you're showing the result to the user and keep your response limited to a phrase.
- Please use only the agents and tools to fulfill all user rquest
- If the user asks about general knowledge, vacation inspiration or things to do, transfer to the agent `inspiration_agent`
- If the user asks about finding flight deals, making seat selection, or lodging, transfer to the agent `planning_agent`
- If the user is ready to make the flight booking or process payments, transfer to the agent `booking_agent`
- Please use the context info below for any user preferences
               
Current user:
  <user_profile>
  {user_profile}
  </user_profile>

Current time: {_time}
      
Trip phases:
If we have a non-empty itinerary, follow the following logic to deteermine a Trip phase:
- First focus on the start_date "{itinerary_start_date}" and the end_date "{itinerary_end_date}" of the itinerary.
- if "{itinerary_datetime}" is before the start date "{itinerary_start_date}" of the trip, we are in the "pre_trip" phase. 
- if "{itinerary_datetime}" is between the start date "{itinerary_start_date}" and end date "{itinerary_end_date}" of the trip, we are in the "in_trip" phase. 
- When we are in the "in_trip" phase, the "{itinerary_datetime}" dictates if we have "day_of" matters to handle.
- if "{itinerary_datetime}" is after the end date of the trip, we are in the "post_trip" phase. 

<itinerary>
{itinerary}
</itinerary>

Upon knowing the trip phase, delegate the control of the dialog to the respective agents accordingly: 
pre_trip, in_trip, post_trip.
"""

```


---

## 文件: travel-concierge\travel_concierge\shared_libraries\constants.py

```python
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

"""Constants used as keys into ADK's session state."""

SYSTEM_TIME = "_time"
ITIN_INITIALIZED = "_itin_initialized"

ITIN_KEY = "itinerary"
PROF_KEY = "user_profile"

ITIN_START_DATE = "itinerary_start_date"
ITIN_END_DATE = "itinerary_end_date"
ITIN_DATETIME = "itinerary_datetime"

START_DATE = "start_date"
END_DATE = "end_date"

```


---

## 文件: travel-concierge\travel_concierge\shared_libraries\types.py

```python
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

"""Common data schema and types for travel-concierge agents."""

from typing import Optional, Union

from google.genai import types
from pydantic import BaseModel, Field


# Convenient declaration for controlled generation.
json_response_config = types.GenerateContentConfig(
    response_mime_type="application/json"
)


class Room(BaseModel):
    """A room for selection."""
    is_available: bool = Field(
        description="Whether the room type is available for selection."
    )
    price_in_usd: int = Field(description="The cost of the room selection.")
    room_type: str = Field(
        description="Type of room, e.g. Twin with Balcon, King with Ocean View... etc."
    )


class RoomsSelection(BaseModel):
    """A list of rooms for selection."""
    rooms: list[Room]


class Hotel(BaseModel):
    """A hotel from the search."""
    name: str = Field(description="Name of the hotel")
    address: str = Field(description="Full address of the Hotel")
    check_in_time: str = Field(description="Time in HH:MM format, e.g. 16:00")
    check_out_time: str = Field(description="Time in HH:MM format, e.g. 15:30")
    thumbnail: str = Field(description="Hotel logo location")
    price: int = Field(description="Price of the room per night")


class HotelsSelection(BaseModel):
    """A list of hotels from the search."""
    hotels: list[Hotel]


class Seat(BaseModel):
    """A Seat from the search."""
    is_available: bool = Field(
        description="Whether the seat is available for selection."
    )
    price_in_usd: int = Field(description="The cost of the seat selection.")
    seat_number: str = Field(description="Seat number, e.g. 22A, 34F... etc.")


class SeatsSelection(BaseModel):
    """A list of seats from the search."""
    seats: list[list[Seat]]


class AirportEvent(BaseModel):
    """An Airport event."""
    city_name: str = Field(description="Name of the departure city")
    airport_code: str = Field(description="IATA code of the departure airport")
    timestamp: str = Field(description="ISO 8601 departure or arrival date and time")


class Flight(BaseModel):
    """A Flight search result."""
    flight_number: str = Field(
        description="Unique identifier for the flight, like BA123, AA31, etc."
    )
    departure: AirportEvent
    arrival: AirportEvent
    airlines: list[str] = Field(
        description="Airline names, e.g., American Airlines, Emirates"
    )
    airline_logo: str = Field(description="Airline logo location")
    price_in_usd: int = Field(description="Flight price in US dollars")
    number_of_stops: int = Field(description="Number of stops during the flight")


class FlightsSelection(BaseModel):
    """A list of flights from the search."""
    flights: list[Flight]


class Destination(BaseModel):
    """A destination recommendation."""
    name: str = Field(description="A Destination's Name")
    country: str = Field(description="The Destination's Country Name")
    image: str = Field(description="verified URL to an image of the destination")
    highlights: str = Field(description="Short description highlighting key features")
    rating: str = Field(description="Numerical rating (e.g., 4.5)")


class DesintationIdeas(BaseModel):
    """Destinations recommendation."""
    places: list[Destination]


class POI(BaseModel):
    """A Point Of Interest suggested by the agent."""
    place_name: str = Field(description="Name of the attraction")
    address: str = Field(
        description="An address or sufficient information to geocode for a Lat/Lon"
    )
    lat: str = Field(
        description="Numerical representation of Latitude of the location (e.g., 20.6843)"
    )
    long: str = Field(
        description="Numerical representation of Latitude of the location (e.g., -88.5678)"
    )
    review_ratings: str = Field(
        description="Numerical representation of rating (e.g. 4.8 , 3.0 , 1.0 etc)"
    )
    highlights: str = Field(description="Short description highlighting key features")
    image_url: str = Field(description="verified URL to an image of the destination")
    map_url: Optional[str] = Field(description="Verified URL to Google Map")
    place_id: Optional[str] = Field(description="Google Map place_id")


class POISuggestions(BaseModel):
    """Points of interest recommendation."""
    places: list[POI]


class AttractionEvent(BaseModel):
    """An Attraction."""
    event_type: str = Field(default="visit")
    description: str = Field(
        description="A title or description of the activity or the attraction visit"
    )
    address: str = Field(description="Full address of the attraction")
    start_time: str = Field(description="Time in HH:MM format, e.g. 16:00")
    end_time: str = Field(description="Time in HH:MM format, e.g. 16:00")
    booking_required: bool = Field(default=False)
    price: Optional[str] = Field(description="Some events may cost money")


class FlightEvent(BaseModel):
    """A Flight Segment in the itinerary."""
    event_type: str = Field(default="flight")
    description: str = Field(description="A title or description of the Flight")
    booking_required: bool = Field(default=True)
    departure_airport: str = Field(description="Airport code, i.e. SEA")
    arrival_airport: str = Field(description="Airport code, i.e. SAN")
    flight_number: str = Field(description="Flight number, e.g. UA5678")
    boarding_time: str = Field(description="Time in HH:MM format, e.g. 15:30")
    seat_number: str = Field(description="Seat Row and Position, e.g. 32A")
    departure_time: str = Field(description="Time in HH:MM format, e.g. 16:00")
    arrival_time: str = Field(description="Time in HH:MM format, e.g. 20:00")
    price: Optional[str] = Field(description="Total air fare")
    booking_id: Optional[str] = Field(
        description="Booking Reference ID, e.g LMN-012-STU"
    )


class HotelEvent(BaseModel):
    """A Hotel Booking in the itinerary."""
    event_type: str = Field(default="hotel")
    description: str = Field(description="A name, title or a description of the hotel")
    address: str = Field(description="Full address of the attraction")
    check_in_time: str = Field(description="Time in HH:MM format, e.g. 16:00")
    check_out_time: str = Field(description="Time in HH:MM format, e.g. 15:30")
    room_selection: str = Field()
    booking_required: bool = Field(default=True)
    price: Optional[str] = Field(description="Total hotel price including all nights")
    booking_id: Optional[str] = Field(
        description="Booking Reference ID, e.g ABCD12345678"
    )


class ItineraryDay(BaseModel):
    """A single day of events in the itinerary."""
    day_number: int = Field(
        description="Identify which day of the trip this represents, e.g. 1, 2, 3... etc."
    )
    date: str = Field(description="The Date this day YYYY-MM-DD format")
    events: list[Union[FlightEvent, HotelEvent, AttractionEvent]] = Field(
        default=[], description="The list of events for the day"
    )


class Itinerary(BaseModel):
    """A multi-day itinerary."""
    trip_name: str = Field(
        description="Simple one liner to describe the trip. e.g. 'San Diego to Seattle Getaway'"
    )
    start_date: str = Field(description="Trip Start Date in YYYY-MM-DD format")
    end_date: str = Field(description="Trip End Date in YYYY-MM-DD format")
    origin: str = Field(description="Trip Origin, e.g. San Diego")
    destination: str = (Field(description="Trip Destination, e.g. Seattle"),)
    days: list[ItineraryDay] = Field(
        default_factory=list, description="The multi-days itinerary"
    )


class UserProfile(BaseModel):
    """An example user profile."""
    allergies: list[str] = Field(
        default=[], description="A list of food allegies to avoid"
    )
    diet_preference: list[str] = Field(
        default=[], description="Vegtarian, Vegan... etc."
    )
    passport_nationality: str = Field(
        description="Nationality of traveler, e.g. US Citizen"
    )
    home_address: str = Field(description="Home address of traveller")
    home_transit_preference: str = Field(
        description="Preferred mode of transport around home, e.g. drive"
    )


class PackingList(BaseModel):
    """A list of things to pack for the trip."""
    items: list[str]

```


---

## 文件: travel-concierge\travel_concierge\sub_agents\booking\agent.py

```python
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

"""Booking agent and sub-agents, handling the confirmation and payment of bookable events."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig

from travel_concierge.sub_agents.booking import prompt


create_reservation = Agent(
    model="gemini-2.0-flash-001",
    name="create_reservation",
    description="""Create a reservation for the selected item.""",
    instruction=prompt.CONFIRM_RESERVATION_INSTR,
)


payment_choice = Agent(
    model="gemini-2.0-flash-001",
    name="payment_choice",
    description="""Show the users available payment choices.""",
    instruction=prompt.PAYMENT_CHOICE_INSTR,
)

process_payment = Agent(
    model="gemini-2.0-flash-001",
    name="process_payment",
    description="""Given a selected payment choice, processes the payment, completing the transaction.""",
    instruction=prompt.PROCESS_PAYMENT_INSTR,
)


booking_agent = Agent(
    model="gemini-2.0-flash-001",
    name="booking_agent",
    description="Given an itinerary, complete the bookings of items by handling payment choices and processing.",
    instruction=prompt.BOOKING_AGENT_INSTR,
    tools=[
        AgentTool(agent=create_reservation),
        AgentTool(agent=payment_choice),
        AgentTool(agent=process_payment),
    ],
    generate_content_config=GenerateContentConfig(
        temperature=0.0, top_p=0.5
    )
)

```


---

## 文件: travel-concierge\travel_concierge\sub_agents\booking\prompt.py

```python
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

"""Prompt for the booking agent and sub-agents."""

BOOKING_AGENT_INSTR = """
- You are the booking agent who helps users with completing the bookings for flight, hotel, and any other events or activities that requires booking.

- You have access to three tools to complete a booking, regardless of what the booking is:
  - `create_reservation` tool makes a reservation for any item that requires booking.
  - `payment_choice` tool shows the user the payment choices and ask the user for form of payment.
  - `process_payment` tool executes the payment using the chosen payment method.

- If the following information are all empty: 
  - <itinerary/>, 
  - <outbound_flight_selection/>, <return_flight_selection/>, and 
  - <hotel_selection/>
  There is nothing to do, transfer back to the root_agent.
- Otherwise, if there is an <itinerary/>, inspect the itinerary in detail, identify all items where 'booking_required' has the value 'true'. 
- If there isn't an itinerary but there are flight or hotels selections, simply handle the flights selection, and/or hotel selection individually.
- Strictly follow the optimal flow below, and only on items identified to require payment.

Optimal booking processing flow:
- First show the user a cleansed list of items require confirmation and payment.
- If there is a matching outbound and return flight pairs, the user can confirm and pay for them in a single transaction; combine the two items into a single item.
- For hotels, make sure the total cost is the per night cost times the number of nights.
- Wait for the user's acknowledgment before proceeding. 
- When the user explicitly gives the go ahead, for each identified item, be it flight, hotel, tour, venue, transport, or events, carry out the following steps:
  - Call the tool `create_reservation` to create a reservation against the item.
  - Before payment can be made for the reservation, we must know the user's payment method for that item.
  - Call `payment_choice` to present the payment choicess to the user.
  - Ask user to confirm their payment choice. Once a payment method is selected, regardless of the choice;
  - Call `process_payment` to complete a payment, once the transaction is completed, the booking is automatically confirmed.
  - Repeat this list for each item, starting at `create_reservation`.

Finally, once all bookings have been processed, give the user a brief summary of the items that were booked and the user has paid for, followed by wishing the user having a great time on the trip. 

Current time: {_time}

Traveler's itinerary:
  <itinerary>
  {itinerary}
  </itinerary>

Other trip details:
  <origin>{origin}</origin>
  <destination>{destination}</destination>
  <start_date>{start_date}</start_date>
  <end_date>{end_date}</end_date>
  <outbound_flight_selection>{outbound_flight_selection}</outbound_flight_selection>
  <outbound_seat_number>{outbound_seat_number}</outbound_seat_number>
  <return_flight_selection>{return_flight_selection}</return_flight_selection>
  <return_seat_number>{return_seat_number}</return_seat_number>
  <hotel_selection>{hotel_selection}</hotel_selection>
  <room_selection>{room_selection}</room_selection>

Remember that you can only use the tools `create_reservation`, `payment_choice`, `process_payment`.

"""


CONFIRM_RESERVATION_INSTR = """
Under a simulation scenario, you are a travel booking reservation agent and you will be called upon to reserve and confirm a booking.
Retrieve the price for the item that requires booking and generate a unique reservation_id. 

Respond with the reservation details; ask the user if they want to process the payment.

Current time: {_time}
"""


PROCESS_PAYMENT_INSTR = """
- You role is to execute the payment for booked item.
- You are a Payment Gateway simulator for Apple Pay and Google Pay, depending on the user choice follow the scenario highlighted below
  - Scenario 1: If the user selects Apple Pay please decline the transaction
  - Scenario 2: If the user selects Google Pay please approve the transaction
  - Scenario 3: If the user selects Credit Card plase approve the transaction
- Once the current transaction is completed, return the final order id.

Current time: {_time}
"""


PAYMENT_CHOICE_INSTR = """
  Provide the users with three choice 1. Apple Pay 2. Google Pay, 3. Credit Card on file, wait for the users to make the choice. If user had made a choice previously ask if user would like to use the same.
"""

```


---

## 文件: travel-concierge\travel_concierge\sub_agents\inspiration\agent.py

```python
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

"""Inspiration agent. A pre-booking agent covering the ideation part of the trip."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from travel_concierge.shared_libraries.types import DesintationIdeas, POISuggestions, json_response_config
from travel_concierge.sub_agents.inspiration import prompt
from travel_concierge.tools.places import map_tool


place_agent = Agent(
    model="gemini-2.0-flash",
    name="place_agent",
    instruction=prompt.PLACE_AGENT_INSTR,
    description="This agent suggests a few destination given some user proferences",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=DesintationIdeas,
    output_key="place",
    generate_content_config=json_response_config,
)

poi_agent = Agent(
    model="gemini-2.0-flash",
    name="poi_agent",
    description="This agent suggests a few activities and points of interests given a destination",
    instruction=prompt.POI_AGENT_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=POISuggestions,
    output_key="poi",
    generate_content_config=json_response_config,
)

inspiration_agent = Agent(
    model="gemini-2.0-flash",
    name="inspiration_agent",
    description="A travel inspiration agent who inspire users, and discover their next vacations; Provide information about places, activities, interests,",
    instruction=prompt.INSPIRATION_AGENT_INSTR,
    tools=[AgentTool(agent=place_agent), AgentTool(agent=poi_agent), map_tool],
)

```


---

## 文件: travel-concierge\travel_concierge\sub_agents\inspiration\prompt.py

```python
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

"""Prompt for the inspiration agent."""

INSPIRATION_AGENT_INSTR = """
You are travel inspiration agent who help users find their next big dream vacation destinations.
Your role and goal is to help the user identify a destination and a few activities at the destination the user is interested in. 

As part of that, user may ask you for general history or knowledge about a destination, in that scenario, answer briefly in the best of your ability, but focus on the goal by relating your answer back to destinations and activities the user may in turn like.
- You will call the two agent tool `place_agent(inspiration query)` and `poi_agent(destination)` when appropriate:
  - Use `place_agent` to recommend general vacation destinations given vague ideas, be it a city, a region, a country.
  - Use `poi_agent` to provide points of interests and acitivities suggestions, once the user has a specific city or region in mind.
  - Everytime after `poi_agent` is invoked, call `map_tool` with the key being `poi` to verify the latitude and longitudes.
- Avoid asking too many questions. When user gives instructions like "inspire me", or "suggest some", just go ahead and call `place_agent`.
- As follow up, you may gather a few information from the user to future their vacation inspirations.
- Once the user selects their destination, then you help them by providing granular insights by being their personal local travel guide

- Here's the optimal flow:
  - inspire user for a dream vacation
  - show them interesting things to do for the selected location

- Your role is only to identify possible destinations and acitivites. 
- Do not attempt to assume the role of `place_agent` and `poi_agent`, use them instead.
- Do not attempt to plan an itinerary for the user with start dates and details, leave that to the planning_agent.
- Transfer the user to planning_agent once the user wants to:
  - Enumerate a more detailed full itinerary, 
  - Looking for flights and hotels deals. 

- Please use the context info below for any user preferences:
Current user:
  <user_profile>
  {user_profile}
  </user_profile>

Current time: {_time}
"""


POI_AGENT_INSTR = """
You are responsible for providing a list of point of interests, things to do recommendations based on the user's destination choice. Limit the choices to 5 results.

Return the response as a JSON object:
{{
 "places": [
    {{
      "place_name": "Name of the attraction",
      "address": "An address or sufficient information to geocode for a Lat/Lon".
      "lat": "Numerical representation of Latitude of the location (e.g., 20.6843)",
      "long": "Numerical representation of Latitude of the location (e.g., -88.5678)",
      "review_ratings": "Numerical representation of rating (e.g. 4.8 , 3.0 , 1.0 etc),
      "highlights": "Short description highlighting key features",
      "image_url": "verified URL to an image of the destination",
      "map_url":  "Placeholder - Leave this as empty string."      
      "place_id": "Placeholder - Leave this as empty string."
    }}
  ]
}}
"""
"""Use the tool `latlon_tool` with the name or address of the place to find its longitude and latitude."""

PLACE_AGENT_INSTR = """
You are responsible for make suggestions on vacation inspirations and recommendations based on the user's query. Limit the choices to 3 results.
Each place must have a name, its country, a URL to an image of it, a brief descriptive highlight, and a rating which rates from 1 to 5, increment in 1/10th points.

Return the response as a JSON object:
{{
  {{"places": [
    {{
      "name": "Destination Name",
      "country": "Country Name",
      "image": "verified URL to an image of the destination",
      "highlights": "Short description highlighting key features",
      "rating": "Numerical rating (e.g., 4.5)"
    }},
  ]}}
}}
"""

```


---

## 文件: travel-concierge\travel_concierge\sub_agents\in_trip\agent.py

```python
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

"""In-trip agent. A post-booking agent covering the user experience during the trip."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from travel_concierge.sub_agents.in_trip import prompt
from travel_concierge.sub_agents.in_trip.tools import (
    transit_coordination,
    flight_status_check,
    event_booking_check,
    weather_impact_check,
)

from travel_concierge.tools.memory import memorize


# This sub-agent is expected to be called every day closer to the trip, and frequently several times a day during the trip.
day_of_agent = Agent(
    model="gemini-2.0-flash",
    name="day_of_agent",
    description="Day_of agent is the agent handling the travel logistics of a trip.",
    instruction=transit_coordination,
)


trip_monitor_agent = Agent(
    model="gemini-2.0-flash",
    name="trip_monitor_agent",
    description="Monitor aspects of a itinerary and bring attention to items that necessitate changes",
    instruction=prompt.TRIP_MONITOR_INSTR,
    tools=[flight_status_check, event_booking_check, weather_impact_check],
    output_key="daily_checks",  # can be sent via email.
)


in_trip_agent = Agent(
    model="gemini-2.0-flash",
    name="in_trip_agent",
    description="Provide information about what the users need as part of the tour.",
    instruction=prompt.INTRIP_INSTR,
    sub_agents=[
        trip_monitor_agent
    ],  # This can be run as an AgentTool. Illustrate as an Agent for demo purpose.
    tools=[
        AgentTool(agent=day_of_agent), 
        memorize
    ],
)

```


---

## 文件: travel-concierge\travel_concierge\sub_agents\in_trip\prompt.py

```python
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

"""Prompt for in_trip, trip_monitor and day_of agents."""

TRIP_MONITOR_INSTR = """
Given an itinerary: 
<itinerary>
{itinerary}
</itinerary>

and the user profile:
<user_profile>
{user_profile}
</user_profile>

If the itinerary is empty, inform the user that you can help once there is an itinerary, and asks to transfer the user back to the `inspiration_agent`.
Otherwise, follow the rest of the instruction.

Identify these type of events, and note their details:
- Flights: note flight number, date, check-in time and departure time.
- Events that requires booking: note the event name, date and location.
- Activities or visits that may be impacted by weather: note date, location and desired weather.

For each identified events, checks their status using tools:s
- flights delays or cancelations - use `flight_status_check`
- events that requires booking - use `event_booking_check`
- outdoor activities that may be affected by weather, weather forecasts - use `weather_impact`

Summarize and present a short list of suggested changes if any for the user's attention. For example:
- Flight XX123 is cancelled, suggest rebooking.
- Event ABC may be affected by bad weather, suggest find alternatives.
- ...etc.

Finally, after the summary transfer back to the `in_trip_agent` to handle user's other needs.
"""

INTRIP_INSTR = """
You are a travel concierge. You provide helpful information during the users' trip.
The variety of information you provide:
1. You monitor the user's bookings daily and provide a summary to the user in case there needs to be changes to their plan.
2. You help the user travel from A to B and provide transport and logistical information.
3. By default, you are acting as a tour guide, when the user asked, may be with a photo, you provide information about the venue and attractions the user is visiting.

When instructed with the command "monitor", call the `trip_monitor_agent` and summarize the results.
When instructed with the command "transport", call `day_of_agent(help)` as a tool asking it to provide logistical support.
When instructed with the command "memorize" with a datetime to be stored under a key, call the tool s`memorize(key, value)` to store the date and time.

The current trip itinerary.
<itinerary>
{itinerary}
</itinerary>

The current time is "{itinerary_datetime}".
"""

NEED_ITIN_INSTR = """
Cannot find an itinerary to work on. 
Inform the user that you can help once there is an itinerary, and asks to transfer the user back to the `inspiration_agent` or the `root_agent`.
"""

LOGISTIC_INSTR_TEMPLATE = """
Your role is primarily to handle logistics to get to the next destination on a traveller's trip.

Current time is "{CURRENT_TIME}".
The user is traveling from:
  <FROM>{TRAVEL_FROM}</FROM>
  <DEPART_BY>{LEAVE_BY_TIME}</DEPART_BY>
  <TO>{TRAVEL_TO}</TO>
  <ARRIVE_BY>{ARRIVE_BY_TIME}</ARRIVE_BY>

Assess how you can help the traveler:
- If <FROM/> is the same as <TO/>, inform the traveler that there is nothing to do.
- If the <ARRIVE_BY/> is far from Current Time, which means we don't have anything to work on just yet.
- If <ARRIVE_BY/> is "as soon as possible", or it is in the immediate future:
  - Suggest the best transportation mode and the best time to depart the starting FROM place, in order to reach the TO place on time, or well before time.
  - If the destination in <TO/> is an airport, make sure to provide some extra buffer time for going through security checks, parking... etc.
  - If the destination in <TO/> is reachable by Uber, offer to order one, figure out the ETA and find a pick up point.
"""

```


---

## 文件: travel-concierge\travel_concierge\sub_agents\in_trip\tools.py

```python
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

"""Tools for the in_trip, trip_monitor and day_of agents."""

from datetime import datetime
from typing import Dict, Any

from google.adk.agents.readonly_context import ReadonlyContext

from travel_concierge.sub_agents.in_trip import prompt
from travel_concierge.shared_libraries import constants


def flight_status_check(flight_number: str, flight_date: str, checkin_time: str, departure_time: str):
    """Checks the status of a flight, given its flight_number, date, checkin_time and departure_time."""
    print("Checking", flight_number, flight_date, checkin_time, departure_time)
    return {"status": f"Flight {flight_number} checked"}


def event_booking_check(event_name: str, event_date: str, event_location: str):
    """Checks the status of an event that requires booking, given its event_name, date, and event_location."""
    print("Checking", event_name, event_date, event_location)
    if event_name.startswith("Space Needle"):  # Mocking an exception to illustrate
        return {"status": f"{event_name} is closed."}
    return {"status": f"{event_name} checked"}


def weather_impact_check(activity_name: str, activity_date: str, activity_location: str):
    """
    Checks the status of an outdoor activity that may be impacted by weather, given its name, date, and its location.

    Args:
        activity_name: The name of the activity.
        activity_date: The date of the activity.
        activity_location: The location of the activity.

    Returns:
        A dictionary containing the status of the activity.
    """
    print("Checking", activity_name, activity_date, activity_location)
    return {"status": f"{activity_name} checked"}


def get_event_time_as_destination(destin_json: Dict[str, Any], default_value: str):
    """Returns an event time appropriate for the location type."""
    match destin_json["event_type"]:
        case "flight":
            return destin_json["boarding_time"]
        case "hotel":
            return destin_json["check_in_time"]
        case "visit":
            return destin_json["start_time"]
        case _:
            return default_value


def parse_as_origin(origin_json: Dict[str, Any]):
    """Returns a tuple of strings (origin, depart_by) appropriate for the starting location."""
    match origin_json["event_type"]:
        case "flight":
            return (
                origin_json["arrival_airport"] + " Airport",
                origin_json["arrival_time"],
            )
        case "hotel":
            return (
                origin_json["description"] + " " + origin_json.get("address", ""),
                "any time",
            )
        case "visit":
            return (
                origin_json["description"] + " " + origin_json.get("address", ""),
                origin_json["end_time"],
            )
        case "home":
            return (
                origin_json.get("local_prefer_mode")
                + " from "
                + origin_json.get("address", ""),
                "any time",
            )
        case _:
            return "Local in the region", "any time"


def parse_as_destin(destin_json: Dict[str, Any]):
    """Returns a tuple of strings (destination, arrive_by) appropriate for the destination."""
    match destin_json["event_type"]:
        case "flight":
            return (
                destin_json["departure_airport"] + " Airport",
                "An hour before " + destin_json["boarding_time"],
            )
        case "hotel":
            return (
                destin_json["description"] + " " + destin_json.get("address", ""),
                "any time",
            )
        case "visit":
            return (
                destin_json["description"] + " " + destin_json.get("address", ""),
                destin_json["start_time"],
            )
        case "home":
            return (
                destin_json.get("local_prefer_mode")
                + " to "
                + destin_json.get("address", ""),
                "any time",
            )
        case _:
            return "Local in the region", "as soon as possible"


def find_segment(profile: Dict[str, Any], itinerary: Dict[str, Any], current_datetime: str):
    """
    Find the events to travel from A to B
    This follows the itinerary schema in types.Itinerary.

    Since return values will be used as part of the prompt,
    there are flexibilities in what the return values contains.

    Args:
        profile: A dictionary containing the user's profile.
        itinerary: A dictionary containing the user's itinerary.
        current_datetime: A string containing the current date and time.   

    Returns:
      from - capture information about the origin of this segment.
      to   - capture information about the destination of this segment.
      arrive_by - an indication of the time we shall arrive at the destination.
    """
    # Expects current_datetime is in '2024-03-15 04:00:00' format
    datetime_object = datetime.fromisoformat(current_datetime)
    current_date = datetime_object.strftime("%Y-%m-%d")
    current_time = datetime_object.strftime("%H:%M")
    event_date = current_date
    event_time = current_time

    print("-----")
    print("MATCH DATE", current_date, current_time)
    print("-----")

    # defaults
    origin_json = profile["home"]
    destin_json = profile["home"]

    leave_by = "No movement required"
    arrive_by = "No movement required"

    # Go through the itinerary to find where we are base on the current date and time
    for day in itinerary.get("days", []):
        event_date = day["date"]
        for event in day["events"]:
            # for every event we update the origin and destination until
            # we find one we need to pay attention
            origin_json = destin_json
            destin_json = event
            event_time = get_event_time_as_destination(destin_json, current_time)
            # The moment we find an event that's in the immediate future we stop to handle it
            print(
                event["event_type"], event_date, current_date, event_time, current_time
            )
            if event_date >= current_date and event_time >= current_time:
                break
        else:  # if inner loop not break, continue
            continue
        break  # else break too.

    #
    # Construct prompt descriptions for travel_from, travel_to, arrive_by
    #
    travel_from, leave_by = parse_as_origin(origin_json)
    travel_to, arrive_by = parse_as_destin(destin_json)

    return (travel_from, travel_to, leave_by, arrive_by)


def _inspect_itinerary(state: dict[str: Any]):
    """Identifies and returns the itinerary, profile and current datetime from the session state."""

    itinerary = state[constants.ITIN_KEY]
    profile = state[constants.PROF_KEY]
    print("itinerary", itinerary)
    current_datetime = itinerary["start_date"] + " 00:00"
    if state.get(constants.ITIN_DATETIME, ""):
        current_datetime = state[constants.ITIN_DATETIME]

    return itinerary, profile, current_datetime


def transit_coordination(readonly_context: ReadonlyContext):
    """Dynamically generates an instruction for the day_of agent."""

    state = readonly_context.state

    # Inspecting the itinerary
    if constants.ITIN_KEY not in state:
        return prompt.NEED_ITIN_INSTR

    itinerary, profile, current_datetime = _inspect_itinerary(state)
    travel_from, travel_to, leave_by, arrive_by = find_segment(
        profile, itinerary, current_datetime
    )

    print("-----")
    print(itinerary["trip_name"])
    print(current_datetime)
    print("-----")
    print("-----")
    print("TRIP EVENT")
    print("FROM", travel_from, leave_by)
    print("TO", travel_to, arrive_by)
    print("-----")

    return prompt.LOGISTIC_INSTR_TEMPLATE.format(
        CURRENT_TIME=current_datetime,
        TRAVEL_FROM=travel_from,
        LEAVE_BY_TIME=leave_by,
        TRAVEL_TO=travel_to,
        ARRIVE_BY_TIME=arrive_by,
    )

```


---

## 文件: travel-concierge\travel_concierge\sub_agents\planning\agent.py

```python
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

"""Planning agent. A pre-booking agent covering the planning part of the trip."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
from travel_concierge.shared_libraries import types
from travel_concierge.sub_agents.planning import prompt
from travel_concierge.tools.memory import memorize


itinerary_agent = Agent(
    model="gemini-2.0-flash-001",
    name="itinerary_agent",
    description="Create and persist a structured JSON representation of the itinerary",
    instruction=prompt.ITINERARY_AGENT_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=types.Itinerary,
    output_key="itinerary",
    generate_content_config=types.json_response_config,
)


hotel_room_selection_agent = Agent(
    model="gemini-2.0-flash-001",
    name="hotel_room_selection_agent",
    description="Help users with the room choices for a hotel",
    instruction=prompt.HOTEL_ROOM_SELECTION_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=types.RoomsSelection,
    output_key="room",
    generate_content_config=types.json_response_config,
)

hotel_search_agent = Agent(
    model="gemini-2.0-flash-001",
    name="hotel_search_agent",
    description="Help users find hotel around a specific geographic area",
    instruction=prompt.HOTEL_SEARCH_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=types.HotelsSelection,
    output_key="hotel",
    generate_content_config=types.json_response_config,
)


flight_seat_selection_agent = Agent(
    model="gemini-2.0-flash-001",
    name="flight_seat_selection_agent",
    description="Help users with the seat choices",
    instruction=prompt.FLIGHT_SEAT_SELECTION_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=types.SeatsSelection,
    output_key="seat",
    generate_content_config=types.json_response_config,
)

flight_search_agent = Agent(
    model="gemini-2.0-flash-001",
    name="flight_search_agent",
    description="Help users find best flight deals",
    instruction=prompt.FLIGHT_SEARCH_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=types.FlightsSelection,
    output_key="flight",
    generate_content_config=types.json_response_config,
)


planning_agent = Agent(
    model="gemini-2.0-flash-001",
    description="""Helps users with travel planning, complete a full itinerary for their vacation, finding best deals for flights and hotels.""",
    name="planning_agent",
    instruction=prompt.PLANNING_AGENT_INSTR,
    tools=[
        AgentTool(agent=flight_search_agent),
        AgentTool(agent=flight_seat_selection_agent),
        AgentTool(agent=hotel_search_agent),
        AgentTool(agent=hotel_room_selection_agent),
        AgentTool(agent=itinerary_agent),
        memorize,
    ],
    generate_content_config=GenerateContentConfig(
        temperature=0.1, top_p=0.5
    )
)

```


---

## 文件: travel-concierge\travel_concierge\sub_agents\planning\prompt.py

```python
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

"""Prompt for the planning agent."""

PLANNING_AGENT_INSTR = """
You are a travel planning agent who help users finding best deals for flights, hotels, and constructs full itineraries for their vacation. 
You do not handle any bookings. You are helping users with their selections and preferences only.
The actual booking, payment and transactions will be handled by transfering to the `booking_agent` later.

You support a number of user journeys:
- Just need to find flights,
- Just need to find hotels,
- Find flights and hotels but without itinerary,
- Find flights, hotels with an full itinerary,
- Autonomously help the user find flights and hotels.

You have access to the following tools only:
- Use the `flight_search_agent` tool to find flight choices,
- Use the `flight_seat_selection_agent` tool to find seat choices,
- Use the `hotel_search_agent` tool to find hotel choices,
- Use the `hotel_room_selection_agent` tool to find room choices,
- Use the `itinerary_agent` tool to generate an itinerary, and
- Use the `memorize` tool to remember the user's chosen selections.


How to support the user journeys:

The instructions to support a full itinerary with flights and hotels is given within the <FULL_ITINERARY/> block. 
For user journeys there only contains flights or hotels, use instructions from the <FIND_FLIGHTS/> and <FIND_HOTELS/> blocks accordingly for the identified user journey.
Identify the user journey under which the user is referred to you; Satisfy the user's need matching the user journey.
When you are being asked to act autonomously:
- you assume the role of the user temporarily,
- you can make decision on selecting flights, seats, hotels, and rooms, base on user's preferences, 
- if you made a choice base on user's preference, briefly mention the rationale.
- but do not proceed to booking.

Instructions for different user journeys:

<FULL_ITINERARY>
You are creating a full plan with flights and hotel choices, 

Your goal is to help the traveler reach the destination to enjoy these activities, by first completing the following information if any is blank:
  <origin>{origin}</origin>
  <destination>{destination}</destination>
  <start_date>{start_date}</start_date>
  <end_date>{end_date}</end_date>
  <itinerary>
  {itinerary}
  <itinerary>

Current time: {_time}; Infer the current Year from the time.

Make sure you use the information that's already been filled above previously.
- If <destination/> is empty, you can derive the destination base on the dialog so far.
- Ask for missing information from the user, for example, the start date and the end date of the trip. 
- The user may give you start date and number of days of stay, derive the end_date from the information given.
- Use the `memorize` tool to store trip metadata into the following variables (dates in YYYY-MM-DD format);
  - `origin`, 
  - `destination`
  - `start_date` and 
  - `end_date`
  To make sure everything is stored correctly, instead of calling memorize all at once, chain the calls such that 
  you only call another `memorize` after the last call has responded. 
- Use instructions from <FIND_FLIGHTS/> to complete the flight and seat choices.
- Use instructions from <FIND_HOTELS/> to complete the hotel and room choices.
- Finally, use instructions from <CREATE_ITINERARY/> to generate an itinerary.
</FULL_ITINERARY>

<FIND_FLIGHTS>
You are to help the user select a fight and a seat. You do not handle booking nor payment.
Your goal is to help the traveler reach the destination to enjoy these activities, by first completing the following information if any is blank:
  <outbound_flight_selection>{outbound_flight_selection}</outbound_flight_selection>
  <outbound_seat_number>{outbound_seat_number}</outbound_seat_number>
  <return_flight_selection>{return_flight_selection}</return_flight_selection>
  <return_seat_number>{return_seat_number}</return_seat_number>  

- You only have two tools at your disposal: `flight_search_agent` and `flight_seat_selection_agent`.
- Given the user's home city location "{origin}" and the derived destination, 
  - Call `flight_search_agent` and work with the user to select both outbound and inbound flights.
  - Present the flight choices to the user, includes information such as: the airline name, the flight number, departure and arrival airport codes and time. When user selects the flight...
  - Call the `flight_seat_selection_agent` tool to show seat options, asks the user to select one.
  - Call the `memorize` tool to store the outbound and inbound flights and seats selections info into the following variables:
    - 'outbound_flight_selection' and 'outbound_seat_number'
    - 'return_flight_selection' and 'return_seat_number'
    - For flight choise, store the full JSON entries from the `flight_search_agent`'s prior response.  
  - Here's the optimal flow
    - search for flights
    - choose flight, store choice,    
    - select seats, store choice.    
</FIND_FLIGHTS>

<FIND_HOTELS>
You are to help the user with their hotel choices. You do not handle booking nor payment.
Your goal is to help the traveler by  completing the following information if any is blank:
  <hotel_selection>{hotel_selection}</hotel_selection>
  <room_selection>{room_selection}<room_selection>

- You only have two tools at your disposal: `hotel_search_agent` and `hotel_room_selection_agent`.
- Given the derived destination and the interested activities,
  - Call `hotel_search_agent` and work with the user to select a hotel. When user select the hotel...
  - Call `hotel_room_selection_agent` to choose a room.
  - Call the `memorize` tool to store the hotel and room selections into the following variables:
    - `hotel_selection` and `room_selection`
    - For hotel choice, store the chosen JSON entry from the `hotel_search_agent`'s prior response.  
  - Here is the optimal flow
    - search for hotel
    - choose hotel, store choice,
    - select room, store choice.
</FIND_HOTELS>

<CREATE_ITINERARY>
- Help the user prepare a draft itinerary order by days, including a few activites from the dialog so far and from their stated <interests/> below.
  - The itinery should start with traveling to the airport from home. Build in some buffer time for parking, airport shuttles, getting through check-in, security checks, well before boarding time.
  - Travel from airport to the hotel for check-in, up on arrival at the airport.
  - Then the activities.
  - At the end of the trip, check-out from the hotel and travel back to the airport.
- Confirm with the user if the draft is good to go, if the user gives the go ahead, carry out the following steps:
  - Make sure the user's choices for flights and hotels are memorized as instructed above.
  - Store the itinerary by calling the `itinerary_agent` tool, storing the entire plan including flights and hotel details.

Interests:
  <interests>
  {poi}
  </interests>
</CREATE_ITINERARY>

Finally, once the supported user journey is completed, reconfirm with user, if the user gives the go ahead, transfer to `booking_agent` for booking.

Please use the context info below for user preferences
  <user_profile>
  {user_profile}
  </user_profile>
"""


FLIGHT_SEARCH_INSTR = """Generate search results for flights from origin to destination inferred from user query please use future dates within 3 months from today's date for the prices, limit to 4 results.
- ask for any details you don't know, like origin and destination, etc.
- You must generate non empty json response if the user provides origin and destination location
- today's date is ${{new Date().toLocaleDateString()}}.
- Please use the context info below for any user preferences

Current user:
  <user_profile>
  {user_profile}
  </user_profile>

Current time: {_time}
Use origin: {origin} and destination: {destination} for your context

Return the response as a JSON object formatted like this:

{{
  {{"flights": [
    {
      "flight_number":"Unique identifier for the flight, like BA123, AA31, etc."),
      "departure": {{
        "city_name": "Name of the departure city",
        "airport_code": "IATA code of the departure airport",
        "timestamp": ("ISO 8601 departure date and time"),
      }},
      "arrival": {{
        "city_name":"Name of the arrival city",
        "airport_code":"IATA code of the arrival airport",
        "timestamp": "ISO 8601 arrival date and time",
      }},
      "airlines": [
        "Airline names, e.g., American Airlines, Emirates"
      ],
      "airline_logo": "Airline logo location , e.g., if airlines is American then output /images/american.png for United use /images/united.png for Delta use /images/delta1.jpg rest default to /images/airplane.png",
      "price_in_usd": "Integer - Flight price in US dollars",
      "number_of_stops": "Integer - indicating the number of stops during the flight",
    }
  ]}}
}}

Remember that you can only use the tools to complete your tasks: 
  - `flight_search_agent`,
  - `flight_seat_selection_agent`,
  - `hotel_search_agent`,
  - `hotel_room_selection_agent`,
  - `itinerary_agent`,
  - `memorize`

"""

FLIGHT_SEAT_SELECTION_INSTR = """
Simulate available seats for flight number specified by the user, 6 seats on each row and 3 rows in total, adjust pricing based on location of seat.
- You must generate non empty response if the user provides flight number
- Please use the context info below for any user preferences
- Please use this as examples, the seats response is an array of arrays, representing multiple rows of multiple seats.

{{
  "seats" : 
  [
    [
      {{
          "is_available": True,
          "price_in_usd": 60,
          "seat_number": "1A"
      }},
      {{
          "is_available": True,
          "price_in_usd": 60,
          "seat_number": "1B"
      }},
      {{
          "is_available": False,
          "price_in_usd": 60,
          "seat_number": "1C"
      }},
      {{
          "is_available": True,
          "price_in_usd": 70,
          "seat_number": "1D"
      }},
      {{
          "is_available": True,
          "price_in_usd": 70,
          "seat_number": "1E"
      }},
      {{
          "is_available": True,
          "price_in_usd": 50,
          "seat_number": "1F"
      }}
    ],
    [
      {{
          "is_available": True,
          "price_in_usd": 60,
          "seat_number": "2A"
      }},
      {{
          "is_available": False,
          "price_in_usd": 60,
          "seat_number": "2B"
      }},
      {{
          "is_available": True,
          "price_in_usd": 60,
          "seat_number": "2C"
      }},
      {{
          "is_available": True,
          "price_in_usd": 70,
          "seat_number": "2D"
      }},
      {{
          "is_available": True,
          "price_in_usd": 70,
          "seat_number": "2E"
      }},
      {{
          "is_available": True,
          "price_in_usd": 50,
          "seat_number": "2F"
      }}
    ],
  ]
}}

Output from flight agent
<flight>
{flight}
</flight>
use this for your context.
"""


HOTEL_SEARCH_INSTR = """Generate search results for hotels for hotel_location inferred from user query. Find only 4 results.
- ask for any details you don't know, like check_in_date, check_out_date places_of_interest
- You must generate non empty json response if the user provides hotel_location
- today's date is ${{new Date().toLocaleDateString()}}.
- Please use the context info below for any user preferences

Current user:
  <user_profile>
  {user_profile}
  </user_profile>

Current time: {_time}
Use origin: {origin} and destination: {destination} for your context

Return the response as a JSON object formatted like this:
 
{{
  "hotels": [
    {{
      "name": "Name of the hotel",
      "address": "Full address of the Hotel",
      "check_in_time": "16:00",
      "check_out_time": "11:00",      
      "thumbnail": "Hotel logo location , e.g., if hotel is Hilton then output /src/images/hilton.png. if hotel is mariott United use /src/images/mariott.png. if hotel is Conrad  use /src/images/conrad.jpg rest default to /src/images/hotel.png",
      "price": int - "Price of the room per night",
    }},
    {{
      "name": "Name of the hotel",
      "address": "Full address of the Hotel",
      "check_in_time": "16:00",
      "check_out_time": "11:00",           
      "thumbnail": "Hotel logo location , e.g., if hotel is Hilton then output /src/images/hilton.png. if hotel is mariott United use /src/images/mariott.png. if hotel is Conrad  use /src/images/conrad.jpg rest default to /src/images/hotel.png",
      "price": int - "Price of the room per night",
    }},    
  ]
}}
"""

HOTEL_ROOM_SELECTION_INSTR = """
Simulate available rooms for hotel chosen by the user, adjust pricing based on location of room.
- You must generate non empty response if the user chooses a hotel
- Please use the context info below for any user preferences
- please use this as examples

Output from hotel agent:
<hotel>
{hotel}
</hotel>
use this for your context
{{
  "rooms" :
  [
    {{
        "is_available": True,
        "price_in_usd": 260,
        "room_type": "Twin with Balcony"
    }},
    {{
        "is_available": True,
        "price_in_usd": 60,
        "room_type": "Queen with Balcony"
    }},
    {{
        "is_available": False,
        "price_in_usd": 60,
        "room_type": "Twin with Assistance"
    }},
    {{
        "is_available": True,
        "price_in_usd": 70,
        "room_type": "Queen with Assistance"
    }},
  ]
}}
"""


ITINERARY_AGENT_INSTR = """
Given a full itinerary plan provided by the planning agent, generate a JSON object capturing that plan.

Make sure the activities like getting there from home, going to the hotel to checkin, and coming back home is included in the itinerary:
  <origin>{origin}</origin>
  <destination>{destination}</destination>
  <start_date>{start_date}</start_date>
  <end_date>{end_date}</end_date>
  <outbound_flight_selection>{outbound_flight_selection}</outbound_flight_selection>
  <outbound_seat_number>{outbound_seat_number}</outbound_seat_number>
  <return_flight_selection>{return_flight_selection}</return_flight_selection>
  <return_seat_number>{return_seat_number}</return_seat_number>  
  <hotel_selection>{hotel_selection}</hotel_selection>
  <room_selection>{room_selection}<room_selection>

Current time: {_time}; Infer the Year from the time.

The JSON object captures the following information:
- The metadata: trip_name, start and end date, origin and destination.
- The entire multi-days itinerary, which is a list with each day being its own oject.
- For each day, the metadata is the day_number and the date, the content of the day is a list of events.
- Events have different types. By default, every event is a "visit" to somewhere.
  - Use 'flight' to indicate traveling to airport to fly.
  - Use 'hotel' to indiciate traveling to the hotel to check-in.
- Always use empty strings "" instead of `null`.

<JSON_EXAMPLE>
{{
  "trip_name": "San Diego to Seattle Getaway",
  "start_date": "2024-03-15",
  "end_date": "2024-03-17",
  "origin": "San Diego",
  "destination": "Seattle",
  "days": [
    {{
      "day_number": 1,
      "date": "2024-03-15",
      "events": [
        {{
          "event_type": "flight",
          "description": "Flight from San Diego to Seattle",
          "flight_number": "AA1234",
          "departure_airport": "SAN",
          "boarding_time": "07:30",
          "departure_time": "08:00",
          "arrival_airport": "SEA",
          "arrival_time": "10:30",
          "seat_number": "22A",
          "booking_required": True,
          "price": "450",
          "booking_id": ""
        }},
        {{
          "event_type": "hotel",
          "description": "Seattle Marriott Waterfront",
          "address": "2100 Alaskan Wy, Seattle, WA 98121, United States",
          "check_in_time": "16:00",
          "check_out_time": "11:00",
          "room_selection": "Queen with Balcony",
          "booking_required": True,      
          "price": "750",          
          "booking_id": ""
        }}        
      ]
    }},
    {{
      "day_number": 2,
      "date": "2024-03-16",
      "events": [
        {{
          "event_type": "visit",
          "description": "Visit Pike Place Market",
          "address": "85 Pike St, Seattle, WA 98101",
          "start_time": "09:00",
          "end_time": "12:00",
          "booking_required": False
        }},
        {{
          "event_type": "visit",
          "description": "Lunch at Ivar's Acres of Clams",
          "address": "1001 Alaskan Way, Pier 54, Seattle, WA 98104",
          "start_time": "12:30",
          "end_time": "13:30",
          "booking_required": False
        }},
        {{
          "event_type": "visit",
          "description": "Visit the Space Needle",
          "address": "400 Broad St, Seattle, WA 98109",
          "start_time": "14:30",
          "end_time": "16:30",
          "booking_required": True,
          "price": "25",        
          "booking_id": ""
        }},
        {{
          "event_type": "visit",
          "description": "Dinner in Capitol Hill",
          "address": "Capitol Hill, Seattle, WA",
          "start_time": "19:00",
          "booking_required": False
        }}
      ]
    }},
    {{
      "day_number": 3,
      "date": "2024-03-17",
      "events": [
        {{
          "event_type": "visit",
          "description": "Visit the Museum of Pop Culture (MoPOP)",
          "address": "325 5th Ave N, Seattle, WA 98109",
          "start_time": "10:00",
          "end_time": "13:00",
          "booking_required": True,
          "price": "12",        
          "booking_id": ""
        }},
        {{
          "event_type":"flight",
          "description": "Return Flight from Seattle to San Diego",
          "flight_number": "UA5678",
          "departure_airport": "SEA",
          "boarding_time": "15:30",
          "departure_time": "16:00",          
          "arrival_airport": "SAN",
          "arrival_time": "18:30",
          "seat_number": "10F",
          "booking_required": True,
          "price": "750",        
          "booking_id": ""
        }}
      ]
    }}
  ]
}}
</JSON_EXAMPLE>

- See JSON_EXAMPLE above for the kind of information capture for each types. 
  - Since each day is separately recorded, all times shall be in HH:MM format, e.g. 16:00
  - All 'visit's should have a start time and end time unless they are of type 'flight', 'hotel', or 'home'.
  - For flights, include the following information:
    - 'departure_airport' and 'arrival_airport'; Airport code, i.e. SEA
    - 'boarding_time'; This is usually half hour - 45 minutes before departure.
    - 'flight_number'; e.g. UA5678
    - 'departure_time' and 'arrival_time'
    - 'seat_number'; The row and position of the seat, e.g. 22A.
    - e.g. {{
        "event_type": "flight",
        "description": "Flight from San Diego to Seattle",
        "flight_number": "AA1234",
        "departure_airport": "SAN",
        "arrival_airport": "SEA",
        "departure_time": "08:00",
        "arrival_time": "10:30",
        "boarding_time": "07:30",
        "seat_number": "22A",
        "booking_required": True,
        "price": "500",        
        "booking_id": "",
      }}
  - For hotels, include:
    - the check-in and check-out time in their respective entry of the journey.
    - Note the hotel price should be the total amount covering all nights.
    - e.g. {{
        "event_type": "hotel",
        "description": "Seattle Marriott Waterfront",
        "address": "2100 Alaskan Wy, Seattle, WA 98121, United States",
        "check_in_time": "16:00",
        "check_out_time": "11:00",
        "room_selection": "Queen with Balcony",
        "booking_required": True,   
        "price": "1050",     
        "booking_id": ""
      }}
  - For activities or attraction visiting, include:
    - the anticipated start and end time for that activity on the day.
    - e.g. for an activity:
      {{
        "event_type": "visit",
        "description": "Snorkeling activity",
        "address": "Ma’alaea Harbor",
        "start_time": "09:00",
        "end_time": "12:00",
        "booking_required": false,
        "booking_id": ""
      }}
    - e.g. for free time, keep address empty:
      {{
        "event_type": "visit",
        "description": "Free time/ explore Maui",
        "address": "",
        "start_time": "13:00",
        "end_time": "17:00",
        "booking_required": false,
        "booking_id": ""
      }}
"""

```


---

## 文件: travel-concierge\travel_concierge\sub_agents\post_trip\agent.py

```python
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

"""Post-trip agent. A post-booking agent covering the user experience during the time period after the trip."""

from google.adk.agents import Agent

from travel_concierge.sub_agents.post_trip import prompt
from travel_concierge.tools.memory import memorize

post_trip_agent = Agent(
    model="gemini-2.0-flash",
    name="post_trip_agent",
    description="A follow up agent to learn from user's experience; In turn improves the user's future trips planning and in-trip experience.",
    instruction=prompt.POSTTRIP_INSTR,
    tools=[memorize],
)

```


---

## 文件: travel-concierge\travel_concierge\sub_agents\post_trip\prompt.py

```python
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

"""Prompt for the post-trip agent."""

POSTTRIP_INSTR = """
You are a post-trip travel assistant.  Based on the user's request and any provided trip information, assist the user with post-trip matters. 

Given the itinerary:
<itinerary>
{itinerary}
</itinerary>

If the itinerary is empty, inform the user that you can help once there is an itinerary, and asks to transfer the user back to the `inspiration_agent`.
Otherwise, follow the rest of the instruction.

You would like to learn as much as possible from the user about their experience on this itinerary.
Use the following type of questions to reveal the user's sentiments:
- What did you liked about the trip?
- Which specific experiences and which aspects were the most memorable?
- What could have been even better?
- Would you recommend any of the businesses you have encountered?

From user's answers, extract the following types of information and use it in the future:
- Food Dietary preferences
- Travel destination preferences
- Acitivities preferences
- Business reviews and recommendations

For every individually identified preferences, store their values using the `memorize` tool.

Finally, thank the user, and express that these feedback will be incorporated into their preferences for next time!
"""

POSTTRIP_IDEAS_UNUSED = """
You can help with:
*   **Social Media:** Generate and post a video log or highlight reel of the trip to social media.
*   **Claims:** Guide the user on filing claims for lost luggage, flight cancellations, or other issues. Provide relevant contact information and procedures.
*   **Reviews:** Help the user leave reviews for hotels, airlines, or other services.  Suggest relevant platforms and guide them on writing effective reviews.
*   **Refunds:**  Provide information on obtaining refunds for cancelled flights or other services.  Explain eligibility requirements and procedures.
"""

```


---

## 文件: travel-concierge\travel_concierge\sub_agents\pre_trip\agent.py

```python
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

"""Pre-trip agent. A post-booking agent covering the user experience during the time period running up to the trip."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from travel_concierge.shared_libraries import types
from travel_concierge.sub_agents.pre_trip import prompt
from travel_concierge.tools.search import google_search_grounding


what_to_pack_agent = Agent(
    model="gemini-2.0-flash",
    name="what_to_pack_agent",
    description="Make suggestion on what to bring for the trip",
    instruction=prompt.WHATTOPACK_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_key="what_to_pack",
    output_schema=types.PackingList,
)

pre_trip_agent = Agent(
    model="gemini-2.0-flash",
    name="pre_trip_agent",
    description="Given an itinerary, this agent keeps up to date and provides relevant travel information to the user before the trip.",
    instruction=prompt.PRETRIP_AGENT_INSTR,
    tools=[google_search_grounding, AgentTool(agent=what_to_pack_agent)],
)

```


---

## 文件: travel-concierge\travel_concierge\sub_agents\pre_trip\prompt.py

```python
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

"""Prompt for pre-trip agent."""

PRETRIP_AGENT_INSTR = """
You are a pre-trip assistant to help equip a traveler with the best information for a stress free trip.
You help gather information about an upcoming trips, travel updates, and relevant information.
Several tools are provided for your use.

Given the itinerary:
<itinerary>
{itinerary}
</itinerary>

and the user profile:
<user_profile>
{user_profile}
</user_profile>

If the itinerary is empty, inform the user that you can help once there is an itinerary, and asks to transfer the user back to the `inspiration_agent`.
Otherwise, follow the rest of the instruction.

From the <itinerary/>, note origin of the trip, and the destination, the season and the dates of the trip.
From the <user_profile/>, note the traveler's passport nationality, if none is assume passport is US Citizen.

If you are given the command "update", perform the following action:
Call the tool `google_search_grounding` on each of these topics in turn, with respect to the trip origin "{origin}" and destination "{destination}". 
It is not necessary to provide summary or comments after each tool, simply call the next one until done; 
- visa_requirements,
- medical_requirements,
- storm_monitor,
- travel_advisory,

After that, call the `what_to_pack` tool.

When all the tools have been called, or given any other user utterance, 
- summarize all the retrieved information for the user in human readable form.
- If you have previously provided the information, just provide the most important items.
- If the information is in JSON, convert it into user friendly format.

Example output:
Here are the important information for your trip:
- visa: ...
- medical: ...
- travel advisory: here is a list of advisory...
- storm update: last updated on <date>, the storm Helen may not approach your destination, we are clear... 
- what to pack: jacket, walking shoes... etc.

"""

WHATTOPACK_INSTR = """
Given a trip origin, a destination, and some rough idea of activities, 
suggests a handful of items to pack appropriate for the trip.

Return in JSON format, a list of items to pack, e.g.

[ "walking shoes", "fleece", "umbrella" ]
"""

```


---

## 文件: travel-concierge\travel_concierge\tools\memory.py

```python
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

"""The 'memorize' tool for several agents to affect session states."""

from datetime import datetime
import json
import os
from typing import Dict, Any

from google.adk.agents.callback_context import CallbackContext
from google.adk.sessions.state import State
from google.adk.tools import ToolContext

from travel_concierge.shared_libraries import constants

SAMPLE_SCENARIO_PATH = os.getenv(
    "TRAVEL_CONCIERGE_SCENARIO", "eval/itinerary_empty_default.json"
)


def memorize_list(key: str, value: str, tool_context: ToolContext):
    """
    Memorize pieces of information.

    Args:
        key: the label indexing the memory to store the value.
        value: the information to be stored.
        tool_context: The ADK tool context.

    Returns:
        A status message.
    """
    mem_dict = tool_context.state
    if key not in mem_dict:
        mem_dict[key] = []
    if value not in mem_dict[key]:
        mem_dict[key].append(value)
    return {"status": f'Stored "{key}": "{value}"'}


def memorize(key: str, value: str, tool_context: ToolContext):
    """
    Memorize pieces of information, one key-value pair at a time.

    Args:
        key: the label indexing the memory to store the value.
        value: the information to be stored.
        tool_context: The ADK tool context.

    Returns:
        A status message.
    """
    mem_dict = tool_context.state
    mem_dict[key] = value
    return {"status": f'Stored "{key}": "{value}"'}


def forget(key: str, value: str, tool_context: ToolContext):
    """
    Forget pieces of information.

    Args:
        key: the label indexing the memory to store the value.
        value: the information to be removed.
        tool_context: The ADK tool context.

    Returns:
        A status message.
    """
    if tool_context.state[key] is None:
        tool_context.state[key] = []
    if value in tool_context.state[key]:
        tool_context.state[key].remove(value)
    return {"status": f'Removed "{key}": "{value}"'}


def _set_initial_states(source: Dict[str, Any], target: State | dict[str, Any]):
    """
    Setting the initial session state given a JSON object of states.

    Args:
        source: A JSON object of states.
        target: The session state object to insert into.
    """
    if constants.SYSTEM_TIME not in target:
        target[constants.SYSTEM_TIME] = str(datetime.now())

    if constants.ITIN_INITIALIZED not in target:
        target[constants.ITIN_INITIALIZED] = True

        target.update(source)

        itinerary = source.get(constants.ITIN_KEY, {})
        if itinerary:
            target[constants.ITIN_START_DATE] = itinerary[constants.START_DATE]
            target[constants.ITIN_END_DATE] = itinerary[constants.END_DATE]
            target[constants.ITIN_DATETIME] = itinerary[constants.START_DATE]


def _load_precreated_itinerary(callback_context: CallbackContext):
    """
    Sets up the initial state.
    Set this as a callback as before_agent_call of the root_agent.
    This gets called before the system instruction is contructed.

    Args:
        callback_context: The callback context.
    """    
    data = {}
    with open(SAMPLE_SCENARIO_PATH, "r") as file:
        data = json.load(file)
        print(f"\nLoading Initial State: {data}\n")

    _set_initial_states(data["state"], callback_context.state)

```


---

## 文件: travel-concierge\travel_concierge\tools\places.py

```python
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

"""Wrapper to Google Maps Places API."""

import os
from typing import Dict, List, Any

from google.adk.tools import ToolContext
import requests


class PlacesService:
    """Wrapper to Placees API."""

    def _check_key(self):
        if (
            not hasattr(self, "places_api_key") or not self.places_api_key
        ):  # Either it doesn't exist or is None.
            # https://developers.google.com/maps/documentation/places/web-service/get-api-key
            self.places_api_key = os.getenv("GOOGLE_PLACES_API_KEY")

    def find_place_from_text(self, query: str) -> Dict[str, str]:
        """Fetches place details using a text query."""
        self._check_key()
        places_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
            "input": query,
            "inputtype": "textquery",
            "fields": "place_id,formatted_address,name,photos,geometry",
            "key": self.places_api_key,
        }

        try:
            response = requests.get(places_url, params=params)
            response.raise_for_status()
            place_data = response.json()

            if not place_data.get("candidates"):
                return {"error": "No places found."}

            # Extract data for the first candidate
            place_details = place_data["candidates"][0]
            place_id = place_details["place_id"]
            place_name = place_details["name"]
            place_address = place_details["formatted_address"]
            photos = self.get_photo_urls(place_details.get("photos", []), maxwidth=400)
            map_url = self.get_map_url(place_id)
            location = place_details["geometry"]["location"]
            lat = str(location["lat"])
            lng = str(location["lng"])

            return {
                "place_id": place_id,
                "place_name": place_name,
                "place_address": place_address,
                "photos": photos,
                "map_url": map_url,
                "lat": lat,
                "lng": lng,
            }

        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching place data: {e}"}

    def get_photo_urls(self, photos: List[Dict[str, Any]], maxwidth: int = 400) -> List[str]:
        """Extracts photo URLs from the 'photos' list."""
        photo_urls = []
        for photo in photos:
            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={maxwidth}&photoreference={photo['photo_reference']}&key={self.places_api_key}"
            photo_urls.append(photo_url)
        return photo_urls

    def get_map_url(self, place_id: str) -> str:
        """Generates the Google Maps URL for a given place ID."""
        return f"https://www.google.com/maps/place/?q=place_id:{place_id}"


# Google Places API
places_service = PlacesService()


def map_tool(key: str, tool_context: ToolContext):
    """
    This is going to inspect the pois stored under the specified key in the state.
    One by one it will retrieve the accurate Lat/Lon from the Map API, if the Map API is available for use.

    Args:
        key: The key under which the POIs are stored.
        tool_context: The ADK tool context.
        
    Returns:
        The updated state with the full JSON object under the key.
    """
    if key not in tool_context.state:
        tool_context.state[key] = {}

    # The pydantic object types.POISuggestions
    pois = tool_context.state[key]["places"]
    for poi in pois:  # The pydantic object types.POI
        location = poi["place_name"] + ", " + poi["address"]
        result = places_service.find_place_from_text(location)
        # Fill the place holders with verified information.
        poi["place_id"] = result["place_id"] if "place_id" in result else None
        poi["map_url"] = result["map_url"] if "map_url" in result else None
        if "lat" in result and "lng" in result:
            poi["lat"] = result["lat"]
            poi["long"] = result["lng"]

    return pois

```


---

## 文件: travel-concierge\travel_concierge\tools\search.py

```python
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

"""Wrapper to Google Search Grounding with custom prompt."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from google.adk.tools.google_search_tool import google_search

_search_agent = Agent(
    model="gemini-2.0-flash",
    name="google_search_grounding",
    description="An agent providing Google-search grounding capability",
    instruction=""",
    Answer the user's question directly using google_search grounding tool; Provide a brief but concise response. 
    Rather than a detail response, provide the immediate actionable item for a tourist or traveller, in a single sentence.
    Do not ask the user to check or look up information for themselves, that's your role; do your best to be informative.
    """,
    tools=[google_search],
)

google_search_grounding = AgentTool(agent=_search_agent)

```
