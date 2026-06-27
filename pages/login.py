import streamlit as st
import extra_streamlit_components as stx
from src.ui import render_page_header, render_page_footer
from src.database import get_user_by_email, check_password

st.set_page_config(
    page_title="Logowanie",
    page_icon="assets/images/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "going_to_login" in st.session_state:
    del st.session_state["going_to_login"]

cookie_manager = stx.CookieManager(key="cookie_handler")

if "user_id" in st.session_state and not st.session_state.get("needs_cookie_save"):
    st.switch_page("app.py")

render_page_header()
conn = st.connection("azure_sql", type="sql")

left_co, cent_co, right_co = st.columns([1, 1.5, 1])

with cent_co:
    st.markdown("<br>", unsafe_allow_html=True) 
    st.header("Zaloguj się")
    
    if st.session_state.get("just_logged_in"):
        st.markdown(f"Pomyślnie zalogowano! Witaj, {st.session_state.user_name}.")
        
        if st.button("Przejdź do wyszukiwania", use_container_width=True, type="primary"):
            del st.session_state["just_logged_in"]  
            st.switch_page("app.py")               
            
    else:

        with st.form("login_form", clear_on_submit=False, border=False):
            email = st.text_input("Wpisz swój adres email", placeholder="np. jan.kowalski@email.com", key="login_email")

            st.markdown(
                """
                <style>
                    .forgot-password-link {
                        text-decoration: none; 
                        font-size: 0.9rem; 
                        color: #0066cc; 
                        padding: 10px 5px; /* Dodaje niewidzialną przestrzeń wokół tekstu, zwiększając obszar kliknięcia */
                        display: inline-block;
                        transition: color 0.2s ease;
                    }
                    .forgot-password-link:hover {
                        color: #004499; /* Ciemniejszy kolor po najechaniu, dający sygnał użytkownikowi */
                        text-decoration: underline;
                    }
                </style>
                <div style='text-align: right; margin-top: 5px; margin-bottom: -15px;'>
                    <a href='/reset_hasla' target='_self' class='forgot-password-link'>Zapomniałeś hasła?</a>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            haslo = st.text_input("Wpisz hasło", type="password", placeholder="••••••••", key="login_password")
            
            submit_button = st.form_submit_button("Zaloguj się", use_container_width=True)
            
        if submit_button:
            if not email or not haslo:
                st.error("Proszę uzupełnić wszystkie pola.")
            else:
                user = get_user_by_email(conn, email)
                if user is not None and check_password(haslo, user.haslo_hash):
                    
                    st.session_state.user_id = user.id_uzytkownika
                    st.session_state.user_name = user.imie
                    st.session_state.user_role = user.rola

                    st.session_state.pop("needs_cookie_save", None)
                    
                    st.success(f"Pomyślnie zalogowano! Witaj, {user.imie}.")
                    
                    st.switch_page("app.py")
                else:
                    st.error("Niepoprawny adres e-mail lub hasło.")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='text-muted' style='text-align: center;'>Nie masz jeszcze konta?</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Załóż konto", use_container_width=True, type="secondary"):
            st.switch_page("pages/rejestracja.py") 

    st.markdown("<hr>", unsafe_allow_html=True)

st.markdown(
    """
    <style>
        .custom-footer {
            position: fixed !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            z-index: 9999 !important;
            margin: 0 !important;
            width: 100vw !important;
            border-top: 1px solid rgba(0, 0, 0, 0.08) !important;
        }

        .block-container {
            padding-bottom: 110px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

render_page_footer()