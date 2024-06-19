from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    select,
    column,
    insert,
)
import pandas as pd
from llama_index.core import SQLDatabase
from llama_index.core.indices import SQLStructStoreIndex
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.vector_stores import MetadataInfo
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.tools import QueryEngineTool

from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
import openai
import os

from llama_index.core.tools import FunctionTool


class SQLAgent:
    def __init__(self, csv_paths: list, table_names: list = None, db_path: str = "sqlite:///:memory:", api_key: str = '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'):
        self.csv_paths = csv_paths
        self.table_names = [os.path.splitext(os.path.basename(path))[
            0] for path in csv_paths] if table_names is None else table_names
        self.db_path = db_path
        self.api_key = api_key
        self.sql_database = self.create_db()

        # set the openai api key
        openai.api_key = self.api_key
        self.agent = self.create_agent()

    ######### Create SQLite Database #########
    def create_db(self):
        assert len(self.csv_paths) == len(
            self.table_names), "csv_paths and table_names must have the same length"

        engine = create_engine(self.db_path, future=True)
        metadata_obj = MetaData()

        for csv_path, table_name in zip(self.csv_paths, self.table_names):
            df = pd.read_csv(csv_path)
            df.to_sql(table_name, engine, if_exists="replace", index=False)

            # Reflect the table
            Table(table_name, metadata_obj, autoload_with=engine)

            with engine.connect() as connection:
                cursor = connection.exec_driver_sql(
                    f"SELECT * FROM {table_name} LIMIT 5")
                # print(cursor.fetchall())
                print("Data inserted successfully in table: ", table_name)

        sql_database = SQLDatabase(engine, include_tables=self.table_names)

        return sql_database

    ######### Instantiate the Query Engine#########
    def create_agent(self):
        # Instantiate the Query Engine
        query_engine = NLSQLTableQueryEngine(
            sql_database=self.sql_database,
            tables=self.table_names,
        )

        # Define the query engines / tool
        sql_tool = QueryEngineTool.from_defaults(
            query_engine=query_engine,
            name="sql_tool",
            description=(
                """Useful for translating a natural language query into a SQL query over
            3 tables containing: hourly aggregated weather data, hourly orders data, and RFM data for customers, 
            the data is from an e-commerce company in Switzerland from January 2023 to December 2023.
            """
            ),
        )

        # Initialize the agent
        agent = OpenAIAgent.from_tools(
            [sql_tool],
            llm=OpenAI(temperature=0, model="gpt-4-0613"),
            verbose=True,
        )
        return agent

    def chat(self):
        print("Welcome to the SQL Agent! Type 'exit' to quit.")
        while True:
            query = input("Enter a query:")
            if query.lower() == 'exit':
                break
            response = self.agent.chat(query)
            print(str(response))


if __name__ == "__main__":
    ######### Testing#########
    weather_features_path = '/Users/lucazosso/Desktop/IE_Course/weclomeback/welcomeback_dev/data_science_folder/cleaned/hourly_agg_weather_flavoured_features.csv'
    orders_weather_path = '/Users/lucazosso/Desktop/IE_Course/weclomeback/welcomeback_dev/data_science_folder/cleaned/hourly_orders_weather_flavoured.csv'
    rfm_data_path = '/Users/lucazosso/Desktop/IE_Course/weclomeback/welcomeback_dev/data_science_folder/cleaned/rfm_data.csv'
    csv_paths = [weather_features_path, orders_weather_path, rfm_data_path]
    sql_agent = SQLAgent(csv_paths)

    # Start the chat process
    sql_agent.chat()
