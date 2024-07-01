# st_app/business_details.py

import streamlit as st


def business_details():
    st.title("Tell me about your business 🚀")

    business_name = st.text_input("Business Name")
    website = st.text_input("Website")
    industry = st.multiselect(
        "Industry", ["Retail", "Fitness", "Tech", "Healthcare", "Finance"])
    description = st.text_area(
        "What does your business do? (Be as specific as possible 👀)")

    pain_points = st.multiselect(
        "What is your biggest pain?",
        ["Unorganized data", "Useless dashboard", "No data",
            "Don't know what to ask", "No budget", "No time"]
    )

    report_format = st.selectbox("How do you like your reports?", [
                                 "PDF", "Excel", "Dashboard"])
    kpis = st.multiselect("What are your most important KPIs", [
                          "CAC", "LTV", "Churn Rate", "Conversion Rate", "Revenue"])

    if st.button("Save changes"):
        st.success("Business details saved!")
