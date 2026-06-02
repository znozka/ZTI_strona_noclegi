import streamlit as st
from src.ui import render_page_header, render_page_footer
from src.database import get_user_by_email, check_password

st.set_page_config(
    page_title="Logowanie",
    page_icon="assets/images/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header()

conn = st.connection("azure_sql", type="sql")

left_co, cent_co, right_co = st.columns([1, 1.5, 1])

with cent_co:
    st.markdown("<br>", unsafe_allow_html=True) 
    st.header("Zaloguj się")
    
    email = st.text_input("Wpisz swój adres email", placeholder="np. jan.kowalski@email.com")
    st.markdown(
        """
        <div style='text-align: right; margin-top: 10px; margin-bottom: -20px;'>
            <a href='#' style='color: #0F172A; font-size: 0.85rem;'>Zapomniałeś hasła?</a>
        </div>
        """,
        unsafe_allow_html=True
    )
    haslo = st.text_input("Wpisz hasło", type="password", placeholder="••••••••")
    
    if st.button("Zaloguj się", use_container_width=True):
        if not email or not haslo:
            st.error("Proszę uzupełnić wszystkie pola.")
        else:
            user = get_user_by_email(conn, email)
            if user is not None and check_password(haslo, user.haslo_hash):
                st.session_state.user_id = user.id_uzytkownika
                st.session_state.user_name = user.imie
                st.session_state.user_role = user.rola
                
                st.success(f"Pomyślnie zalogowano! Witaj {user.imie}.")
                st.switch_page("app.py")
            else:
                st.error("Niepoprawny adres e-mail lub hasło.")
        
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("<div style='text-align: center; color: #0F172A;'>Nie masz jeszcze konta?</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Załóż konto", use_container_width=True, type="secondary"):
        st.switch_page("pages/rejestracja.py") 

    st.markdown("<hr>", unsafe_allow_html=True)

render_page_footer()
