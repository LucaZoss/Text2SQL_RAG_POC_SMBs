
import openai
import os
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
#
from sqlalchemy import create_engine
from llama_index.core import SQLDatabase
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.agent.openai import OpenAIAgent

from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT


class SQLAgent_V2:
    def __init__(self, csv_paths: list, table_names: list, context_prompt: str):
        super().__init__()
        '''
        Initialize the SQLAgent_V2 class
        '''
        load_dotenv(".env")
        self.csv_paths = csv_paths
        self.table_names = table_names
        self.context_prompt = context_prompt
        self.agent = None
        openai.api_key = os.getenv('OPENAI_API_KEY')
        # os.getenv("OPENAI_API_KEY")
        self.engine = create_engine('sqlite://', echo=False)

        Settings.llm = OpenAI(model="gpt-4o")
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
        Settings.node_parser = SentenceSplitter(
            chunk_size=512, chunk_overlap=20)
        Settings.num_output = 512
        Settings.context_window = 3900

    def create_db(self, csv_paths, table_names):
        '''
        Create a SQLite database
        '''
        for csv_path, table_name in zip(csv_paths, table_names):
            df = pd.read_csv(csv_path)
            df.to_sql(table_name, con=self.engine)
        self.rag_text2sql_db = SQLDatabase(
            self.engine, include_tables=self.table_names)

    def instantiate_agent(self):
        '''
        Instantiate the OpenAIAgent
        '''
        text2sql_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(
            dialect=self.engine.dialect.name)
        sql_query_engine = NLSQLTableQueryEngine(
            sql_database=self.rag_text2sql_db,
            tables=self.table_names,
            text_to_sql_prompt=text2sql_prompt,
            service_context=Settings,
            verbose=True
        )

        description = f"Useful for translating a natural language query into a SQL query. \
        Use {self.context_prompt} for additional guidelines on the data. "

        sql_tool = QueryEngineTool.from_defaults(
            query_engine=sql_query_engine,
            name="sql_tool",
            description=description,
        )

        self.agent = OpenAIAgent.from_tools(
            tools=[sql_tool],
            llm=OpenAI(model="gpt-4o"),  # gpt-3.5-turbo gpt-4-0613
            system_prompt=None,
            verbose=True)

        print("Agent instantiated successfully.")

    def query_agent(self, query: str):
        """
        Query the OpenAIAgent
        """
        if self.agent is None:
            raise ValueError(
                "Agent is not instantiated. Please call instantiate_agent first.")
        # response = self.agent.chat(query)
        response = self.agent.query(query)
        return response


def setup_and_query_sql_agent(csv_paths: list, table_names: list, context_prompt: str, query: str):
    '''
    Function to set up and query the SQLAgent_V2
    '''
    agent = SQLAgent_V2(csv_paths, table_names, context_prompt)
    agent.create_db(csv_paths, table_names)
    agent.instantiate_agent()
    response = agent.query_agent(query)
    return response


if __name__ == "__main__":
    csv_paths = [
        Path("/Users/lucazosso/Desktop/IE_Course/weclomeback/welcomeback_dev/text2sql_rag/ds/hourly_agg_weather_flavoured_features.csv"),
        Path("/Users/lucazosso/Desktop/IE_Course/weclomeback/welcomeback_dev/text2sql_rag/ds/rfm_data.csv")]
    table_names = ["hourly_agg_weather_flavoured_features", "rfm_data"]
    context_prompt = "The data is from an e-commerce company in Switzerland from January 2023 to December 2023."

    sql_agent = SQLAgent_V2(csv_paths, table_names, context_prompt)
    sql_agent.create_db(csv_paths, table_names)
    sql_agent.instantiate_agent()
    response = sql_agent.query_agent(
        "Get my number 1 customer in RFM terms")
    print(response)
