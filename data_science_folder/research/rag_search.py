import pandas as pd
import logging
import sqlite3
import openai
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core import Document
from llama_index.core import Document, SummaryIndex, ListIndex, SQLDatabase, ServiceContext
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from sqlalchemy import create_engine
from typing import List
import ast
from IPython.display import display, HTML

# Initialize logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Initialize logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SQLRAGSystem:
    def __init__(self, db_path: str, openai_api_key: str, temperature: float = 0.0, model: str = "gpt-3.5-turbo"):
        self.db_path = db_path
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key  # Set the OpenAI API key here
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.llm = OpenAI(temperature=temperature, model=model)
        self.service_context = ServiceContext.from_defaults(llm=self.llm)
        self.table_mapping = {
            'weather': 'hourly_agg_weather_ecommerce_KPIs',
            'orders': 'hourly_orders_customer_main_table',
            'rfm': 'rfm_data'
        }
        self.load_data()

    def load_data(self):
        logging.debug("Loading CSV files into Pandas DataFrames")
        self.df1 = pd.read_csv(
            '/Users/lucazosso/Desktop/IE_Course/weclomeback/welcomeback_dev/data_science_folder/cleaned/hourly_agg_weather_flavoured_features.csv')
        self.df2 = pd.read_csv(
            '/Users/lucazosso/Desktop/IE_Course/weclomeback/welcomeback_dev/data_science_folder/cleaned/hourly_orders_weather_flavoured.csv')
        self.df3 = pd.read_csv(
            '/Users/lucazosso/Desktop/IE_Course/weclomeback/welcomeback_dev/data_science_folder/cleaned/rfm_data.csv')
        logging.debug("CSV files loaded successfully")

        logging.debug(
            "Creating SQLite database and writing dataframes to tables")
        with sqlite3.connect(self.db_path) as conn:
            self.df1.to_sql('hourly_agg_weather_ecommerce_KPIs',
                            conn, if_exists='replace', index=False)
            self.df2.to_sql('hourly_orders_customer_main_table',
                            conn, if_exists='replace', index=False)
            self.df3.to_sql('rfm_data', conn, if_exists='replace', index=False)
        logging.debug(
            "SQLite database created and CSV data imported successfully")

    def generate_questions(self, user_query: str) -> List[str]:
        system_message = f'''
        You are given SQLite tables with the following name and columns.
        
          1. hourly_agg_weather_ecommerce_KPIs: {', '.join(self.df1.columns)}
          2. hourly_orders_customer_main_table: {', '.join(self.df2.columns)}
          3. rfm_data: {', '.join(self.df3.columns)}
        
        Your task is to decompose the given question into the following two questions.
        
        1. Question in natural language that needs to be asked to retrieve results from the table.
        2. Question that needs to be asked on top of the result from the first question to provide the final answer.
        
        Example:
        
        Input:
        What was my top best month in 2023 in terms of revenue?
        
        Output:
        1. Get the month with the highest revenue in 2023
        2. Provide the monthly revenue for the month of January 2023
        '''

        messages = [
            ChatMessage(role="system", content=system_message),
            ChatMessage(role="user", content=user_query),
        ]
        generated_questions = self.llm.chat(
            messages).message.content.split('\n')

        logging.debug(f"Generated questions: {generated_questions}")
        return generated_questions

    def determine_tables(self, user_query: str) -> List[str]:
        selected_tables = []
        for keyword, table in self.table_mapping.items():
            if keyword in user_query.lower():
                selected_tables.append(table)

        logging.debug(
            f"Determined tables for query '{user_query}': {selected_tables}")
        return selected_tables

    def sql_rag(self, user_query: str) -> str:
        text_to_sql_query, rag_query = self.generate_questions(user_query)

        selected_tables = self.determine_tables(user_query)

        if not selected_tables:
            return "No relevant tables found for the query."

        # Create SQLDatabase instance without passing tables parameter
        sql_database = SQLDatabase(engine=self.engine)

        sql_query_engine = NLSQLTableQueryEngine(
            sql_database=sql_database,
            # synthesize_response is set to False to return the raw SQL query
            synthesize_response=False,
            service_context=self.service_context
        )

        # Execute the SQL query
        sql_response = sql_query_engine.query(text_to_sql_query)

        logging.debug(f"SQL Response: {sql_response}")

        # Processing the SQL response
        sql_response_list = ast.literal_eval(sql_response.response)
        text = [' '.join(t) for t in sql_response_list]
        text = ' '.join(text)

        # Refining and Interpreting the reviews with ListIndex
        listindex = ListIndex([Document(text=text)])
        list_query_engine = listindex.as_query_engine()

        response = list_query_engine.query(rag_query)

        return response.response


# Example usage
if __name__ == "__main__":
    db_path = '/Users/lucazosso/Desktop/IE_Course/weclomeback/welcomeback_dev/data_science_folder/cleaned/rag_demo_database.db'
    openai_api_key = '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'

    sql_rag_system = SQLRAGSystem(
        db_path=db_path, openai_api_key=openai_api_key)

    user_query = "Get the customer segments based on the RFM analysis."
    result = sql_rag_system.sql_rag(user_query)
    print(result)
