import streamlit as st
from text2sql_rag.t2s_classtest import load_and_process_files


def main():
    st.title("CSV File Loader")
    # The type parameter restricts uploads to .csv files
    uploaded_files = st.file_uploader(
        "Upload CSV files", type='csv', accept_multiple_files=True)

    if uploaded_files is not None and len(uploaded_files) > 0:
        # Process files when the user uploads them
        dataframes = load_and_process_files(uploaded_files)
        for df in dataframes:
            st.write(df)  # Display each dataframe in the Streamlit app


if __name__ == "__main__":
    main()
