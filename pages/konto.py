import streamlit as st
import extra_streamlit_components as stx
from src.ui import render_page_header, render_page_footer

st.set_page_config(
    page_title="Moje konto",
    page_icon="assets/images/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header()

st.header("Moje konto")

if st.session_state.get("user_name"):
    st.write(f"Zalogowany jako: **{st.session_state.user_name}**")

#Nie zmieniać!
if st.button("Wyloguj"):
    cookie_manager = stx.CookieManager(key="root_cookie_saver")

    cookie_manager.set("user_id", "", key="logout_uid")
    cookie_manager.set("user_name", "", key="logout_name")
    cookie_manager.set("user_role", "", key="logout_role")

    for key in ["user_id", "user_name", "user_role"]:
        st.session_state.pop(key, None)

    st.success("Wylogowano pomyślnie!")
    st.switch_page("app.py")

render_page_footer()
