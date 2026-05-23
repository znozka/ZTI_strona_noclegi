import streamlit as st
from src.ui import render_page_header

st.set_page_config(
    page_title="Moje konto",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header()

st.header("Moje konto")

# Wyświetlanie danych zalogowanego użytkownika
if st.session_state.get("user_name"):
    st.write(f"Zalogowany jako: **{st.session_state.user_name}**")

if st.button("Wyloguj się"):
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.user_role = None
    st.success("Zostałeś wylogowany.")
    st.rerun()