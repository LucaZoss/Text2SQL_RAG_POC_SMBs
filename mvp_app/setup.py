import streamlit as st
import os
from utils import chat_space, get_logger


def setup_agent():
    st.title("Setup Agent")

    csv_files = st.file_uploader("Upload CSV File", type=[
                                 "csv"], accept_multiple_files=True)

    if st.button("Finish Setup"):
        if csv_files:
            os.makedirs("./tmp", exist_ok=True)
            csv_paths = []
            for csv_file in csv_files:
                csv_path = f"./tmp/{csv_file.name}"
                with open(csv_path, "wb") as f:
                    f.write(csv_file.getbuffer())
                csv_paths.append(csv_path)

            st.session_state['csv_paths'] = csv_paths

            st.success("File saved successfully!")
            get_logger().info("File saved successfully!")
        else:
            st.warning("Please upload at least one CSV file.")
            get_logger().warning("CSV file not uploaded.")

    # with st.sidebar:
    #     chat_space()
