# st_app/utils.py

# from text2sql_rag.text2sql_loader import text2SQL
from text2sql_rag.text2sql_loader_st import text2SQL
import streamlit as st
import logging

import sys


# from SQLAgent_V2 import SQLAgent_V2


def configure_logging():
    logging.basicConfig(level=logging.INFO)
    global logger
    logger = logging.getLogger(__name__)


def get_logger():
    return logging.getLogger(__name__)


def chat_space():
    st.title("Assistant 🤖")
    # st.warning("Please setup the agent first.")
    csv_file_paths = st.session_state['csv_paths']

    # Display example queries or actions
    example_queries = [
        "Show me the total sales for last month",
        "List top 5 products by sales",
        "What are my top rfm segments?"
    ]

    if not csv_file_paths:
        st.warning("Please upload CSV files and setup the agent first.")
        return

    text2sql_instance = text2SQL()
    text2sql_instance.load_data(csv_file_paths)
    text2sql_instance.process_tables()
    text2sql_instance.create_sql_database()
    text2sql_instance.setup_query_pipeline()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("How can I help you today?"):
        try:
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append(
                {"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                with st.spinner("Querying agent..."):
                    response = text2sql_instance.run_query(prompt)
                st.markdown(response)
            st.session_state.messages.append(
                {"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"An error occurred: {e}")
            get_logger().error(f"Error during query: {e}")
