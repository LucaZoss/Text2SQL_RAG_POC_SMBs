import os
import sys
import dotenv

# Loading the data
import pandas as pd
from pathlib import Path

# Metadata Extraction
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.bridge.pydantic import BaseModel, Field
from llama_index.llms.openai import OpenAI
import json

# Put data in a SQLight DB
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
)
import re

# Object Index & Retriever
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llama_index.core import SQLDatabase, VectorStoreIndex

# SQLRetriever + Table Parser
from llama_index.core.retrievers import SQLRetriever
from typing import List
from llama_index.core.query_pipeline import FnComponent

# Text2SQL prompt and output parser
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT
from llama_index.core import PromptTemplate
from llama_index.core.query_pipeline import FnComponent
from llama_index.core.llms import ChatResponse

# Define Query Pipeline
from llama_index.core.query_pipeline import (
    QueryPipeline as QP,
    Link,
    InputComponent,
    CustomQueryComponent,
)

# Visualize the pipeline
from pyvis.network import Network
from IPython.display import display, HTML


# loading the environment variables
dotenv.load_dotenv('.env')

print(os.getenv('OPENAI_API_KEY'))

cur_dir = Path(os.path.dirname(os.path.abspath(__file__)))
print(cur_dir)

# data_dir = cur_dir / 'data'
data_dir = Path(os.path.join(cur_dir, 'ds'))

# reading the files and storing them in a list
csv_files = sorted([f for f in data_dir.glob("*.csv")])
dfs = []
for csv_file in csv_files:
    print(f"processing file: {csv_file}")
    try:
        df = pd.read_csv(csv_file)
        dfs.append(df)
    except Exception as e:
        print(f"Error parsing {csv_file}: {str(e)}")

# Extracting table names and table summary
# Making a dictionary of table names and table summary

tableinfo_dir = cur_dir / 'tableinfo_dir'
os.makedirs(tableinfo_dir, exist_ok=True)


class TableInfo(BaseModel):
    """Information regarding a structured table."""

    table_name: str = Field(
        ..., description="table name (must be underscores and NO spaces)"
    )
    table_summary: str = Field(
        ..., description="short, concise summary/caption of the table"
    )


prompt_str = """\
Give me a summary of the table with the following JSON format.

- The table name must be unique to the table and describe it while being concise. 
- Do NOT output a generic table name (e.g. table, my_table).

Do NOT make the table name one of the following: {exclude_table_name_list}

Table:
{table_str}

Summary: """

program = LLMTextCompletionProgram.from_defaults(
    output_cls=TableInfo,
    llm=OpenAI(model="gpt-3.5-turbo"),
    prompt_template_str=prompt_str,
)


def _get_tableinfo_with_index(idx: int) -> str:
    results_gen = Path(tableinfo_dir).glob(f"{idx}_*")
    results_list = list(results_gen)
    if len(results_list) == 0:
        return None
    elif len(results_list) == 1:
        path = results_list[0]
        return TableInfo.parse_file(path)
    else:
        raise ValueError(
            f"More than one file matching index: {list(results_gen)}"
        )


table_names = set()
table_infos = []
for idx, df in enumerate(dfs):
    table_info = _get_tableinfo_with_index(idx)
    if table_info:
        table_infos.append(table_info)
    else:
        while True:
            df_str = df.head(10).to_csv()
            table_info = program(
                table_str=df_str,
                exclude_table_name_list=str(list(table_names)),
            )
            table_name = table_info.table_name
            print(f"Processed table: {table_name}")
            if table_name not in table_names:
                table_names.add(table_name)
                break
            else:
                # try again
                print(f"Table name {table_name} already exists, trying again.")
                pass

        out_file = f"{tableinfo_dir}/{idx}_{table_name}.json"
        json.dump(table_info.dict(), open(out_file, "w"))
    table_infos.append(table_info)

# Put data in a SQL database

# Function to create a sanitized column name


def sanitize_column_name(col_name):
    # Remove special characters and replace spaces with underscores
    return re.sub(r"\W+", "_", col_name)

# Function to create a table from a DataFrame using SQLAlchemy


def create_table_from_dataframe(
    df: pd.DataFrame, table_name: str, engine, metadata_obj
):
    # Sanitize column names
    sanitized_columns = {col: sanitize_column_name(col) for col in df.columns}
    df = df.rename(columns=sanitized_columns)

    # Dynamically create columns based on DataFrame columns and data types
    columns = [
        Column(col, String if dtype == "object" else Integer)
        for col, dtype in zip(df.columns, df.dtypes)
    ]

    # Create a table with the defined columns
    table = Table(table_name, metadata_obj, *columns)

    # Create the table in the database
    metadata_obj.create_all(engine)

    # Insert data from DataFrame into the table
    with engine.connect() as conn:
        for _, row in df.iterrows():
            insert_stmt = table.insert().values(**row.to_dict())
            conn.execute(insert_stmt)
        conn.commit()


# here we load everything in memory (the best way would be to load in an existing db)
engine = create_engine("sqlite:///:memory:")
metadata_obj = MetaData()
for idx, df in enumerate(dfs):
    tableinfo = _get_tableinfo_with_index(idx)
    print(f"Creating table: {tableinfo.table_name}")
    create_table_from_dataframe(df, tableinfo.table_name, engine, metadata_obj)

# Object Index & Retriever
sql_database = SQLDatabase(engine)

table_node_mapping = SQLTableNodeMapping(sql_database)
table_schema_objs = [
    SQLTableSchema(table_name=t.table_name, context_str=t.table_summary)
    for t in table_infos
]  # add a SQLTableSchema for each table

obj_index = ObjectIndex.from_objects(
    table_schema_objs,
    table_node_mapping,
    VectorStoreIndex,
)
obj_retriever = obj_index.as_retriever(similarity_top_k=3)

# SQLRetriever + Table Parser

sql_retriever = SQLRetriever(sql_database)


def get_table_context_str(table_schema_objs: List[SQLTableSchema]):
    """Get table context string."""
    context_strs = []
    for table_schema_obj in table_schema_objs:
        table_info = sql_database.get_single_table_info(
            table_schema_obj.table_name
        )
        if table_schema_obj.context_str:
            table_opt_context = " The table description is: "
            table_opt_context += table_schema_obj.context_str
            table_info += table_opt_context

        context_strs.append(table_info)
    return "\n\n".join(context_strs)


table_parser_component = FnComponent(fn=get_table_context_str)


def parse_response_to_sql(response: ChatResponse) -> str:
    """Parse response to SQL."""
    response = response.message.content
    sql_query_start = response.find("SQLQuery:")
    if sql_query_start != -1:
        response = response[sql_query_start:]
        # TODO: move to removeprefix after Python 3.9+
        if response.startswith("SQLQuery:"):
            response = response[len("SQLQuery:"):]
    sql_result_start = response.find("SQLResult:")
    if sql_result_start != -1:
        response = response[:sql_result_start]
    return response.strip().strip("```").strip()


sql_parser_component = FnComponent(fn=parse_response_to_sql)

text2sql_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(
    dialect=engine.dialect.name
)
print(text2sql_prompt.template)

# Response synthesis prompt
response_synthesis_prompt_str = (
    "Given an input question, synthesize a response from the query results.\n"
    "Query: {query_str}\n"
    "SQL: {sql_query}\n"
    "SQL Response: {context_str}\n"
    "Response: "
)
response_synthesis_prompt = PromptTemplate(
    response_synthesis_prompt_str,
)

llm = OpenAI(model="gpt-3.5-turbo")

# Define Query Pipeline
qp = QP(
    modules={
        "input": InputComponent(),
        "table_retriever": obj_retriever,
        "table_output_parser": table_parser_component,
        "text2sql_prompt": text2sql_prompt,
        "text2sql_llm": llm,
        "sql_output_parser": sql_parser_component,
        "sql_retriever": sql_retriever,
        "response_synthesis_prompt": response_synthesis_prompt,
        "response_synthesis_llm": llm,
    },
    verbose=True,
)

qp.add_chain(["input", "table_retriever", "table_output_parser"])
qp.add_link("input", "text2sql_prompt", dest_key="query_str")
qp.add_link("table_output_parser", "text2sql_prompt", dest_key="schema")
qp.add_chain(
    ["text2sql_prompt", "text2sql_llm", "sql_output_parser", "sql_retriever"]
)
qp.add_link(
    "sql_output_parser", "response_synthesis_prompt", dest_key="sql_query"
)
qp.add_link(
    "sql_retriever", "response_synthesis_prompt", dest_key="context_str"
)
qp.add_link("input", "response_synthesis_prompt", dest_key="query_str")
qp.add_link("response_synthesis_prompt", "response_synthesis_llm")

# Visualize the pipeline
net = Network(notebook=True, cdn_resources="in_line", directed=True)
net.from_nx(qp.dag)

# Save the network as "text2sql_dag.html"
net.write_html("text2sql_dag.html")

# Read the contents of the HTML file
with open("text2sql_dag.html", "r") as file:
    html_content = file.read()

# Display the HTML content
# display(HTML(html_content))

response = qp.run(
    query="What was the total number of orders in january?"
)

print(str(response))
