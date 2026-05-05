import streamlit as st

from src.ui import render_page_header

st.set_page_config(
    page_title="Strona noclegu",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header()

st.header("Strona noclegu")
