import streamlit as st
from src.ui import render_page_header, render_page_footer
from src.database import update_user_password, hash_password 

st.set_page_config(
    page_title="Ustaw nowe hasło",
    page_icon="assets/images/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header(is_auth_page=True)
conn = st.connection("azure_sql", type="sql")

left_co, cent_co, right_co = st.columns([1, 1.5, 1])

with cent_co:
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("Zmień swoje hasło")
    
    user_id = st.query_params.get("user_id")
    
    if not user_id:
        st.error("Nieprawidłowy lub wygasły link do resetowania hasła.")
        if st.button("Wróć do logowania", width='stretch'):
            st.switch_page("pages/login.py")
        st.stop()
        
    with st.form("new_password_form", border=False):
        st.markdown("Wprowadź i potwierdź nowe hasło dla swojego konta.")
        
        nowe_haslo = st.text_input("Nowe hasło", type="password", placeholder="••••••••")
        powtórz_haslo = st.text_input("Powtórz nowe hasło", type="password", placeholder="••••••••")
        
        submit_change = st.form_submit_button("Zapisz nowe hasło", width='stretch')
        
    if submit_change:
        if not nowe_haslo or not powtórz_haslo:
            st.error("Proszę wypełnić oba pola.")
        elif nowe_haslo != powtórz_haslo:
            st.error("Podane hasła nie są identyczne.")
        elif len(nowe_haslo) < 8:  
            st.error("Hasło musi mieć co najmniej 8 znaków.")
        else:
            try:
                nowe_haslo_hash = hash_password(nowe_haslo)
                
                success = update_user_password(conn, user_id, nowe_haslo_hash)
                
                if success:
                    st.success("Hasło zostało pomyślnie zmienione!")
                    st.info("Za chwilę nastąpi przekierowanie do strony logowania...")
                    
                    st.query_params.clear()
                    
                    import time
                    time.sleep(2)
                    st.switch_page("pages/login.py")
                else:
                    st.error("Wystąpił błąd podczas aktualizacji hasła w bazie danych.")
                    
            except Exception as e:
                st.error(f"Wystąpił nieoczekiwany błąd: {e}")

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