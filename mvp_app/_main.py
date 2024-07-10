# st_app/home.py
from PIL import Image
import streamlit as st
import os
# Local
from mvp_app.dash import dummy_dashboard
from utils import configure_logging, chat_space
from mvp_app.business_details import business_details
from mvp_app.setup import setup_agent
from mvp_app.dash import dummy_dashboard


def home():
    # st.write(os.getcwd())
    script_dir = os.path.dirname(__file__)
    image_path = os.path.join(script_dir, "messy_logo.jpeg")
    image = Image.open(image_path)
    # image = Image.open("./st_app/messy_logo.jpeg")

    # Adjust image size (optional)
    image = image.resize((2000, 1600))  # Adjust width and height as needed

    left_co, mid, right_1 = st.columns(3)
    with mid:
        st.image(image)

    # Add logo and slogan
    st.markdown("""
        <style>
            .header {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 30px;
                text-align: center;
            }

            .header .slogan {
                font-size: 24px;
                font-weight: bold;
                margin: 0;
            }
        </style>
        <div class="header">
            <p class="slogan"><strong>Transforming your messy</strong> data into <strong>actionable</strong> decisions</p>
        </div>
    """, unsafe_allow_html=True)

    # Add Button to start
    left_co, mid, right_1 = st.columns(3)


def main():
    st.set_page_config(
        page_title="MessyAI MVP",
        page_icon="⚡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    # Add custom CSS
    st.markdown("""
        <style>
            .stApp {
                background-color: #6A6FFD;
                color: white;
            }
            .header {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                text-align: center;
            }
            .header img {
                width: 50%;
                max-width: 400px;
                margin-bottom: 20px;
            }
            .header .slogan {
                font-size: 24px;
                font-weight: bold;
                margin: 0;
            }
            .stSidebar > div {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    configure_logging()
    st.sidebar.image("messy_logo.jpeg")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to", ["Home", "Business Details", "Setup Data Source", "Dashboard"])

    if "agent" not in st.session_state:
        st.session_state['agent'] = None
    if "csv_paths" not in st.session_state:
        st.session_state['csv_paths'] = []
    if "table_names" not in st.session_state:
        st.session_state['table_names'] = []
    if "context_prompt" not in st.session_state:
        st.session_state['context_prompt'] = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if page == "Home":
        home()
    elif page == "Business Details":
        business_details()
    elif page == "Setup Data Source":
        setup_agent()
    elif page == "Dashboard":
        dummy_dashboard()


if __name__ == "__main__":
    main()
