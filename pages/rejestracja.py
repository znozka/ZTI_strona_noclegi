import streamlit as st
from src.ui import render_page_header, render_page_footer
from src.database import register_user, get_user_by_email

st.set_page_config(
    page_title="Zarejestruj się - InnSight",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header()

conn = st.connection("azure_sql", type="sql")

left_co, cent_co, right_co = st.columns([1, 1.75, 1])

with cent_co:
    st.header("Zarejestruj się")

    col_name, col_surname = st.columns(2)
    with col_name:
        imie = st.text_input("Imię", placeholder="np. Jan")
    with col_surname:
        nazwisko = st.text_input("Nazwisko", placeholder="np. Kowalski")
    nowy_email = st.text_input("Wpisz swój adres email", placeholder="np. jan.kowalski@email.com")
    nowe_haslo = st.text_input("Wpisz hasło", type="password", placeholder="Minimum 8 znaków")
    powtórz_haslo = st.text_input("Powtórz hasło", type="password", placeholder="••••••••")
    
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Zarejestruj się i zaloguj", use_container_width=True):
        if not imie or not nazwisko or not nowy_email or not nowe_haslo or not powtórz_haslo:
            st.error("Wszystkie pola są wymagane!")
        elif len(nowe_haslo) < 8:
            st.error("Hasło musi mieć minimum 8 znaków.")
        elif nowe_haslo != powtórz_haslo:
            st.error("Podane hasła nie są identyczne.")
        else:
            try:
                success = register_user(conn, nowy_email, nowe_haslo, imie, nazwisko)
                
                if success:
                    from src.database import get_user_by_email
                    user = get_user_by_email(conn, nowy_email)
                    
                    st.session_state.user_id = user.id_uzytkownika
                    st.session_state.user_name = user.imie
                    st.session_state.user_role = user.rola
                    
                    st.success("Konto zostało utworzone pomyślnie!")
                    st.switch_page("app.py") 
                else:
                    st.error("Użytkownik o podanym adresie e-mail już istnieje.")
            except Exception as e:
                st.error(f"Wystąpił błąd podczas rejestracji: {e}")
        
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #0F172A;'>Masz już konto?</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Wróć do logowania", use_container_width=True):
        st.switch_page("pages/login.py")
    st.markdown("<hr>", unsafe_allow_html=True)

render_page_footer()
