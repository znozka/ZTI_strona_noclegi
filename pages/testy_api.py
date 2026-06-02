import streamlit as st

from src.ui import render_page_header, render_page_footer

st.set_page_config(
    page_title="Testy API pogodowego",
    page_icon="assets/images/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header()

st.header("Z: tu będą się działy testy api pogodowego")

render_page_footer()
