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

cookie_manager = stx.CookieManager(key="cookie_handler")

if "user_id" not in st.session_state:
    cookie_uid = st.context.cookies.get("user_id")
    if cookie_uid:
        st.session_state.user_id = cookie_uid
        st.session_state.user_name = st.context.cookies.get("user_name")
        st.session_state.user_role = st.context.cookies.get("user_role")

# Jeśli sesja jest już aktywna i nie jesteśmy w trakcie logowania -> na stronę główną
if "user_id" in st.session_state and not st.session_state.get("just_logged_in"):
    st.switch_page("app.py")

render_page_header()
conn = st.connection("azure_sql", type="sql")

left_co, cent_co, right_co = st.columns([1, 1.5, 1])

with cent_co:
    st.markdown("<br>", unsafe_allow_html=True) 
    st.header("Zaloguj się")
    
    # Jeśli użytkownik wpisał poprawne hasło, pokazujemy mu ekran sukcesu
    if st.session_state.get("just_logged_in"):
        st.markdown(f"Pomyślnie zalogowano! Witaj, {st.session_state.user_name}.")
        
        if st.button("Przejdź do wyszukiwania", use_container_width=True, type="primary"):
            del st.session_state["just_logged_in"]  # Czyścimy flagę pomocniczą
            st.switch_page("app.py")                # Bezpieczne przekierowanie
            
    else:
        # Standardowy formularz logowania
        email = st.text_input("Wpisz swój adres email", placeholder="np. jan.kowalski@email.com")
        st.markdown(
            """
            <div style='text-align: right; margin-top: 10px; margin-bottom: -20px;'>
                <a href='#' class='small-link'>Zapomniałeś hasła?</a>
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
                    
                    # 1. Zapisujemy dane do session_state (działa natychmiastowo)
                    st.session_state.user_id = user.id_uzytkownika
                    st.session_state.user_name = user.imie
                    st.session_state.user_role = user.rola
                    
                    # 2. KLUCZOWE: Ustawiamy flagę informującą app.py, że musi zapisać ciasteczka u siebie (jako ROOT)
                    st.session_state.needs_cookie_save = True
                    
                    st.success(f"Pomyślnie zalogowano! Witaj, {user.imie}.")
                    
                    # 3. Przekierowujemy bezpiecznie na stronę główną
                    st.switch_page("app.py")
                else:
                    st.error("Niepoprawny adres e-mail lub hasło.")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='text-muted' style='text-align: center;'>Nie masz jeszcze konta?</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Załóż konto", use_container_width=True, type="secondary"):
            st.switch_page("pages/rejestracja.py") 

    st.markdown("<hr>", unsafe_allow_html=True)

render_page_footer()
