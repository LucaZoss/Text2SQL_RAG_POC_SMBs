from llama_index import SimpleCSVReader, SimpleJSONReader, SimpleSQLReader, SimplePDFReader, SimpleWordReader, SimpleImageReader
import requests
import sqlite3
import pandas as pd

class DataLoader:

    @staticmethod
    def load_csv(file_path):
        reader = SimpleCSVReader(file_path)
        return reader.load_data()

    @staticmethod
    def load_json(file_path):
        reader = SimpleJSONReader(file_path)
        return reader.load_data()

    @staticmethod
    def load_sql(connection_string, query):
        reader = SimpleSQLReader(connection_string)
        return reader.load_data(query)
    
    #TODO: Test sql methods
    
    @staticmethod
    def load_sql(connection_string, query):
        conn = sqlite3.connect(connection_string)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_dict(orient='records')

    @staticmethod
    def load_pdf(file_path):
        reader = SimplePDFReader(file_path)
        return reader.load_data()

    @staticmethod
    def load_word(file_path):
        reader = SimpleWordReader(file_path)
        return reader.load_data()

    @staticmethod
    def load_image(file_path):
        reader = SimpleImageReader(file_path)
        return reader.load_data()

    @staticmethod
    def load_api(url, params=None):
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
