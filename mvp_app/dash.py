# st_app/dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import chat_space


def dummy_dashboard():
    st.title("Dashboard 📊")
    st.write("This is a dummy dashboard.")

    if not st.session_state.csv_paths:
        st.warning("Please setup the agent and upload CSV files first.")
        return

    selected_file = st.selectbox(
        "Select a CSV file", st.session_state.csv_paths)
    df = pd.read_csv(selected_file)

    st.write("Display a chart")
    dimension = st.selectbox("Select a dimension", df.select_dtypes(
        include=['object', 'category']).columns)
    metric = st.selectbox("Select a metric", df.select_dtypes(
        include=(['int64', 'float64'])).columns)
    chart_type = st.selectbox("Select a chart type", [
                              "Bar", "Line", "Area", "Pie"])

    if chart_type == "Bar":
        fig = px.bar(df, x=dimension, y=metric)
    elif chart_type == "Line":
        fig = px.line(df, x=dimension, y=metric)
    elif chart_type == "Area":
        fig = px.area(df, x=dimension, y=metric)
    elif chart_type == "Pie":
        fig = px.pie(df, names=dimension, values=metric)

    st.plotly_chart(fig)
    st.write(df.head())

    with st.sidebar:
        st.write("This is a sidebar.")
        chat_space()
