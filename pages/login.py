import streamlit as st

from src.ui import render_page_header

st.set_page_config(
    page_title="Logowanie",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header()

st.header("Zaloguj się")
if st.button("Zaloguj się"):
    st.session_state.user_name = "Użytkownik"
    st.success("Jesteś teraz zalogowany.")
    st.rerun()
