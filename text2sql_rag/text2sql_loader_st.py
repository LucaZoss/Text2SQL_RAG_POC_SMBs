import os
import dotenv
import pandas as pd
from pathlib import Path
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.bridge.pydantic import BaseModel, Field
from llama_index.llms.openai import OpenAI
import json
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer
import re
from llama_index.core.objects import SQLTableNodeMapping, ObjectIndex, SQLTableSchema
from llama_index.core import SQLDatabase, VectorStoreIndex
from llama_index.core.retrievers import SQLRetriever
from typing import List
from llama_index.core.query_pipeline import FnComponent
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT
from llama_index.core import PromptTemplate
from llama_index.core.llms import ChatResponse
from llama_index.core.query_pipeline import QueryPipeline as QP, InputComponent
from pyvis.network import Network
from IPython.display import display, HTML

import streamlit as st

dotenv.load_dotenv('.env')
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")
# os.getenv("OPENAI_API_KEY"))


class TableInfo(BaseModel):
    """Information regarding a structured table."""
    table_name: str = Field(
        ..., description="table name (must be underscores and NO spaces)"
    )
    table_summary: str = Field(
        ..., description="short, concise summary/caption of the table"
    )


class text2SQL:
    """
    Add Comments
    """

    def __init__(self):
        self.dfs = []
        self.table_infos = []
        self.engine = create_engine("sqlite:///:memory:")
        self.metadata_obj = MetaData()

    def load_data(self, csv_files: List[Path]):
        for csv_file in csv_files:
            print(f"Processing file: {csv_file}")
            try:
                df = pd.read_csv(csv_file)
                self.dfs.append(df)
            except Exception as e:
                print(f"Error parsing {csv_file}: {str(e)}")

    def process_tables(self):
        tableinfo_dir = Path("tableinfo_dir")
        os.makedirs(tableinfo_dir, exist_ok=True)

        program = LLMTextCompletionProgram.from_defaults(
            output_cls=TableInfo,
            llm=OpenAI(model="gpt-4", openai_api_key=OPENAI_API_KEY),
            prompt_template_str=self.prompt_str()
        )

        table_names = set()
        for idx, df in enumerate(self.dfs):
            table_info = self._get_tableinfo_with_index(idx, tableinfo_dir)
            if table_info:
                self.table_infos.append(table_info)
            else:
                while True:
                    df_str = df.head(10).to_csv()  # .sample?
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
                        print(
                            f"Table name {table_name} already exists, trying again.")

                out_file = f"{tableinfo_dir}/{idx}_{table_name}.json"
                json.dump(table_info.dict(), open(out_file, "w"))
                self.table_infos.append(table_info)

    def _get_tableinfo_with_index(self, idx: int, tableinfo_dir: Path) -> str:
        results_gen = tableinfo_dir.glob(f"{idx}_*")
        results_list = list(results_gen)
        if len(results_list) == 0:
            return None
        elif len(results_list) == 1:
            path = results_list[0]
            return TableInfo.parse_file(path)
        else:
            raise ValueError(
                f"More than one file matching index: {list(results_gen)}")

    def prompt_str(self):
        return """\
Give me a summary of the table with the following JSON format.

- The table name must be unique to the table and describe it while being concise. 
- Do NOT output a generic table name (e.g. table, my_table).

Do NOT make the table name one of the following: {exclude_table_name_list}

Table:
{table_str}

Summary: """

    def create_sql_database(self):
        for idx, df in enumerate(self.dfs):
            tableinfo = self._get_tableinfo_with_index(
                idx, Path("tableinfo_dir"))
            print(f"Creating table: {tableinfo.table_name}")
            self.create_table_from_dataframe(df, tableinfo.table_name)

    def sanitize_column_name(self, col_name: str) -> str:
        return re.sub(r"\W+", "_", col_name)

    def create_table_from_dataframe(self, df: pd.DataFrame, table_name: str):
        sanitized_columns = {
            col: self.sanitize_column_name(col) for col in df.columns}
        df = df.rename(columns=sanitized_columns)

        columns = [
            Column(col, String if dtype == "object" else Integer)
            for col, dtype in zip(df.columns, df.dtypes)
        ]

        table = Table(table_name, self.metadata_obj, *columns)
        self.metadata_obj.create_all(self.engine)

        with self.engine.connect() as conn:
            for _, row in df.iterrows():
                insert_stmt = table.insert().values(**row.to_dict())
                conn.execute(insert_stmt)
            conn.commit()

    def setup_query_pipeline(self):
        # Initialize a connection to the SQL database using the provided engine
        self.sql_database = SQLDatabase(self.engine)
        # Create a mapping between SQL tables and their corresponding nodes
        table_node_mapping = SQLTableNodeMapping(self.sql_database)
        # Generate schema objects for each table, including the table name and a summary context
        table_schema_objs = [
            SQLTableSchema(table_name=t.table_name,
                           context_str=t.table_summary)
            for t in self.table_infos
        ]
        # Create an index from the table schema objects using the SQLTableNodeMapping and a vector store for indexing
        obj_index = ObjectIndex.from_objects(
            table_schema_objs,
            table_node_mapping,
            VectorStoreIndex,  # by default uses embeddinds-ada-002 from OpenAI
        )
        # Set up a retriever that uses the object index to find similar objects based on top k similarity
        self.obj_retriever = obj_index.as_retriever(similarity_top_k=5)
        # Initialize a SQL retriever that can execute queries against the SQL database
        self.sql_retriever = SQLRetriever(self.sql_database)

        # Define a function component to get the context string for a table
        table_parser_component = FnComponent(fn=self.get_table_context_str)
        # Define a function component to parse responses into SQL queries
        sql_parser_component = FnComponent(fn=self.parse_response_to_sql)

        # Prompt template for converting text to SQL based on the database dialect
        text2sql_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(
            dialect=self.engine.dialect.name
        )

        # Define a prompt template for synthesizing a response from SQL query results
        response_synthesis_prompt_str = (
            "Given an input question, synthesize a response from the query results.\n"
            "Query: {query_str}\n"
            "SQL: {sql_query}\n"
            "SQL Response: {context_str}\n"
            "Response: "
        )
        response_synthesis_prompt = PromptTemplate(
            response_synthesis_prompt_str)

        # Setting up the Query Pipeline
        llm = OpenAI(model="gpt-4", openai_api_key=OPENAI_API_KEY)

        self.qp = QP(
            modules={
                "input": InputComponent(),
                "table_retriever": self.obj_retriever,
                "table_output_parser": table_parser_component,
                "text2sql_prompt": text2sql_prompt,
                "text2sql_llm": llm,
                "sql_output_parser": sql_parser_component,
                "sql_retriever": self.sql_retriever,
                "response_synthesis_prompt": response_synthesis_prompt,
                "response_synthesis_llm": llm,
            },
            verbose=True,
        )

        self.qp.add_chain(["input", "table_retriever", "table_output_parser"])
        self.qp.add_link("input", "text2sql_prompt", dest_key="query_str")
        self.qp.add_link("table_output_parser",
                         "text2sql_prompt", dest_key="schema")
        self.qp.add_chain(
            ["text2sql_prompt", "text2sql_llm",
                "sql_output_parser", "sql_retriever"]
        )
        self.qp.add_link(
            "sql_output_parser", "response_synthesis_prompt", dest_key="sql_query"
        )
        self.qp.add_link(
            "sql_retriever", "response_synthesis_prompt", dest_key="context_str"
        )
        self.qp.add_link("input", "response_synthesis_prompt",
                         dest_key="query_str")
        self.qp.add_link("response_synthesis_prompt", "response_synthesis_llm")

    def get_table_context_str(self, table_schema_objs: List[SQLTableSchema]) -> str:
        context_strs = []
        for table_schema_obj in table_schema_objs:
            table_info = self.sql_database.get_single_table_info(
                table_schema_obj.table_name)
            if table_schema_obj.context_str:
                table_opt_context = " The table description is: "
                table_opt_context += table_schema_obj.context_str
                table_info += table_opt_context

            context_strs.append(table_info)
        return "\n\n".join(context_strs)

    def parse_response_to_sql(self, response: ChatResponse) -> str:
        response = response.message.content
        sql_query_start = response.find("SQLQuery:")
        if sql_query_start != -1:
            response = response[sql_query_start:]
            if response.startswith("SQLQuery:"):
                response = response[len("SQLQuery:"):]
        sql_result_start = response.find("SQLResult:")
        if sql_result_start != -1:
            response = response[:sql_result_start]
        return response.strip().strip("```").strip()

    def run_query(self, query: str) -> str:
        response = self.qp.run(query=query)
        print(str(response))
        return str(response)

    def visualize_pipeline(self):
        html_viz_dir = Path("html_viz")
        html_viz_dir.mkdir(exist_ok=True)

        net = Network(notebook=True, cdn_resources="in_line", directed=True)
        net.from_nx(self.qp.dag)

        html_path = html_viz_dir / "text2sql_dag.html"
        net.write_html(str(html_path))

        with open(html_path, "r") as file:
            html_content = file.read()
            display(HTML(html_content))


# Example usage
if __name__ == "__main__":
    csv_file_paths = [Path("/Users/lucazosso/Desktop/IE_Course/weclomeback/welcomeback_dev/text2sql_rag/ds/hourly_agg_weather_flavoured_features.csv"),
                      Path("/Users/lucazosso/Desktop/IE_Course/weclomeback/welcomeback_dev/text2sql_rag/ds/rfm_data.csv")]
    text2sql_instance = text2SQL()
    text2sql_instance.load_data(csv_file_paths)
    text2sql_instance.process_tables()
    text2sql_instance.create_sql_database()
    text2sql_instance.setup_query_pipeline()
    text2sql_instance.visualize_pipeline()
    query_result = text2sql_instance.run_query(
        "What was the total number of orders in january?")
    print(query_result)
