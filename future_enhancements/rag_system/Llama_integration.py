from llama_index import LlamaIndex
from future_enhancements.loaders import DataLoader
from flask import current_app


class LlamaIndexIntegration:
    def __init__(self):
        self.index = LlamaIndex()

    def add_data(self, data):
        # Assuming data is a list of dictionaries
        self.index.add_documents(data)

    def query(self, query_text, client_id):
        # Check if SQL connection information exists for the client
        sql_connection_string = current_app.config['SQL_CONNECTIONS'].get(
            client_id)
        if sql_connection_string:
            # Perform an SQL query if relevant to the query text (this is a simplified example)
            # Implement a method to create SQL queries based on the input text
            sql_query = self.construct_sql_query(query_text)
            sql_data = DataLoader.load_sql(sql_connection_string, sql_query)
            # Incorporate SQL data into the response
            response = self.index.query(query_text)
            response['sql_data'] = sql_data
        else:
            # If no SQL connection, proceed with the normal query
            response = self.index.query(query_text)
        return response

    def construct_sql_query(self, query_text):
        # Implement a method to construct SQL queries based on the input text
        # This is a placeholder implementation
        return "SELECT * FROM some_table WHERE some_column LIKE '%{}%'".format(query_text)
