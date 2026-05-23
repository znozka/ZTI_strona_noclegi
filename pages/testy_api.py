import streamlit as st

from src.ui import render_page_header

st.set_page_config(
    page_title="Testy API pogodowego",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header()

st.header("Z: tu będą się działy testy api pogodowego")
