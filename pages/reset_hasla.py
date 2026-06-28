import streamlit as st
from src.ui import render_page_header, render_page_footer
from src.database import get_user_by_email
from src.utils import send_reset_email

st.set_page_config(
    page_title="Odzyskiwanie hasła",
    page_icon="assets/images/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header(is_auth_page=True)
conn = st.connection("azure_sql", type="sql")

left_co, cent_co, right_co = st.columns([1, 1.5, 1])

with cent_co:
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("Odzyskiwanie hasła")
    st.markdown("Wpisz swój adres e-mail. Jeśli znajduje się w naszej bazie, wyślemy na niego instrukcje resetowania hasła.")
    
    with st.form("reset_form", border=False):
        reset_email = st.text_input("Adres e-mail", placeholder="np. jan.kowalski@email.com")
        submit_reset = st.form_submit_button("Wyślij link do resetowania", width='stretch')
        
    if submit_reset:
        if not reset_email:
            st.error("Proszę podać adres e-mail.")
        else:
            user = get_user_by_email(conn, reset_email)
            
            if user is not None and not user.empty:
                try:
                    user_id = user["id_uzytkownika"].iloc[0]
                    user_email = user["email"].iloc[0] if "email" in user.columns else reset_email
                    
                    with st.spinner("Wysyłanie wiadomości e-mail..."):
                        email_sent = send_reset_email(user_email, user_id)
                    
                    if not email_sent:
                        st.error("Wystąpił problem techniczny podczas wysyłania maila. Spróbuj ponownie później.")
                        st.stop()
                        
                except AttributeError:
                    user_id = user["id_uzytkownika"]
                    with st.spinner("Wysyłanie wiadomości e-mail..."):
                        send_reset_email(reset_email, user_id)

            st.success("Jeżeli adres istnieje w naszej bazie, wiadomość z linkiem została wysłana.")
            st.info("Sprawdź skrzynkę odbiorczą (oraz folder SPAM). Możesz wrócić do logowania.")

    if st.button("Wróć do logowania", type="secondary", width='stretch'):
        st.switch_page("pages/login.py")

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