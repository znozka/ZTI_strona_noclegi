import streamlit as st
import extra_streamlit_components as stx
import pandas as pd
from datetime import datetime
from src.ui import render_page_header, render_page_footer
from src.database import (
    get_user_profile, 
    get_user_reservations, 
    get_user_opinions,
    can_edit_opinion,
    update_opinion,
    delete_opinion,
    update_user_info
)

st.set_page_config(
    page_title="Moje konto",
    page_icon="assets/images/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header()
user_name = st.session_state.get("user_name")

st.header(f"Witaj, **{user_name}**!")

# Sprawdzenie czy użytkownik jest zalogowany
if not st.session_state.get("user_name"):
    st.warning("Musisz być zalogowany, aby zobaczyć swoje konto")
    st.markdown(
        """
        <div style="margin-top: 8px;">
            <a href="/login"
               target="_self"
               style="text-decoration: none; font-size: 0.9rem; color: #0066cc; padding: 8px 0; display: inline-block; transition: color 0.2s ease;"
               onmouseover="this.style.color='#004499'; this.style.textDecoration='underline';"
               onmouseout="this.style.color='#0066cc'; this.style.textDecoration='none';">
                Przejdź do logowania
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

user_id = st.session_state.get("user_id")
section = st.query_params.get("section", [None])[0]
conn = st.connection("azure_sql", type="sql")

if st.query_params.get("logout") == ["1"]:
    cookie_manager = stx.CookieManager(key="root_cookie_saver")
    cookie_manager.set("user_id", "", key="logout_uid")
    cookie_manager.set("user_name", "", key="logout_name")
    cookie_manager.set("user_role", "", key="logout_role")

    for key in ["user_id", "user_name", "user_role"]:
        st.session_state.pop(key, None)

    st.experimental_set_query_params(**{})
    st.success("Wylogowano pomyślnie!")
    st.switch_page("app.py")

left_col, right_col = st.columns([3, 1])

with left_col:
    st.divider()



with right_col:
    st.markdown(
        """
        <style>
            .account-sidebar {
                background-color: #E6E6E6;
                padding: 16px;
                border-radius: 0 0 0 12px;
                display: flex;
                flex-direction: column;
                gap: 12px;
                margin: 0;
                min-height: 30em;
                justify-content: flex-start;
                position: relative;
                right: 0em;
                top: 0em;
                bottom: 10em;
                width: 100%;
                z-index: 10001;
                padding-bottom: 90px;
            }
            .account-tile {
                background-color: #ffffff;
                border-radius: 10px;
                padding: 14px 16px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            }
            .account-tile-title {
                color: #000000;
                font-weight: 700;
                font-size: 0.95rem;
                margin: 0;
            }
            .account-list {
                list-style: none;
                padding: 0;
                margin: 12px 0 0 0;
                display: grid;
                gap: 10px;
            }
            .account-list-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 14px;
                border-radius: 10px;
                background-color: #ffffff;
                color: #000000;
                font-weight: 500;
                font-size: 0.93rem;
                transition: background-color 0.15s ease;
            }
            .account-list-item:hover {
                background-color: #F5F5F5;
            }
            .account-list-item span {
                display: inline-flex;
                width: 24px;
                justify-content: center;
                filter: grayscale(100%);
            }
            .account-item-arrow {
                margin-left: auto;
            }
        </style>
        <div class="account-sidebar">
            <div class="account-tile">
                <p class="account-tile-title">Moje podróże</p>
                <ul class="account-list">
                    <li class="account-list-item"><span>✈</span>Podróże i rezerwacje<span class="account-item-arrow">›</span></li>
                    <li class="account-list-item"><span>♡</span>Zapisane listy<span class="account-item-arrow">›</span></li>
                    <li class="account-list-item">
                        <span>✉</span>
                        <a href="/opinie" target="_self" style="color: inherit; text-decoration: none; display: inline-flex; width: 100%;">
                            Moje opinie
                            <span class="account-item-arrow">›</span>
                        </a>
                    </li>
                </ul>
            </div>
            <div class="account-tile">
                <p class="account-tile-title">Zarządzaj kontem</p>
                <ul class="account-list">
                    <li class="account-list-item"><span>☺</span>Dane osobowe<span class="account-item-arrow">›</span></li>
                    <li class="account-list-item"><span>⚙</span>Zmień hasło<span class="account-item-arrow">›</span></li>
                </ul>
            </div>
            <div class="account-tile">
                <p class="account-tile-title">Zarządzaj obiektem</p>
                <ul class="account-list">
                    <li class="account-list-item"><span>⌂</span>Zarejestruj swój obiekt<span class="account-item-arrow">›</span></li>
                </ul>
            </div>
            <div class="account-tile">
                <p class="account-tile-title">Inne</p>
                <ul class="account-list">
                    <li class="account-list-item"><span>❓</span>Skontaktuj się z obsługą klienta<span class="account-item-arrow">›</span></li>
                    <li class="account-list-item"><span>⚠</span>Informacje dotyczące bezpieczeństwa<span class="account-item-arrow">›</span></li>
                    <li class="account-list-item"><span>⚖</span>Rozwiązywanie sporów<span class="account-item-arrow">›</span></li>
                    <li class="account-list-item" style="font-weight: 700;">
                        <span>⏻</span>
                        <a href="/?page=pages/konto.py&logout=1" target="_top" style="color: inherit; text-decoration: none; display: inline-flex; width: 100%;">
                            Wyloguj
                        </a>
                    </li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <style>
        .custom-footer {
            position: static !important;
            left: 0em !important;
            right: 0em !important;
            bottom: auto !important;
            z-index: 1 !important;
            margin: 0 auto !important;
            width: 100% !important;
            border-top: 1px solid rgba(0, 0, 0, 0.08) !important;
        }

        .block-container {
            padding-bottom: 24px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

render_page_footer()
# import streamlit as st
# import extra_streamlit_components as stx
# import pandas as pd
# from datetime import datetime
# from src.ui import render_page_header, render_page_footer
# from src.database import (
#     get_user_profile, 
#     get_user_reservations, 
#     get_user_opinions,
#     can_edit_opinion,
#     update_opinion,
#     delete_opinion,
#     update_user_info,
#     verify_and_update_password
# )

# st.set_page_config(
#     page_title="Moje konto",
#     page_icon="assets/images/icon.svg",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# render_page_header()
# user_name = st.session_state.get("user_name")

# st.header(f"Witaj, **{user_name}**!")

# # Sprawdzenie czy użytkownik jest zalogowany
# if not user_name:
#     st.warning("Musisz być zalogowany, aby zobaczyć swoje konto")
#     st.markdown(
#         """
#         <div style="margin-top: 8px;">
#             <a href="/login"
#                target="_self"
#                style="text-decoration: none; font-size: 0.9rem; color: #0066cc; padding: 8px 0; display: inline-block; transition: color 0.2s ease;"
#                onmouseover="this.style.color='#004499'; this.style.textDecoration='underline';"
#                onmouseout="this.style.color='#0066cc'; this.style.textDecoration='none';">
#                 Przejdź do logowania
#             </a>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )
#     st.stop()

# user_id = st.session_state.get("user_id")
# conn = st.connection("azure_sql", type="sql")

# if st.query_params.get("logout") == ["1"]:
#     cookie_manager = stx.CookieManager(key="root_cookie_saver")
#     cookie_manager.set("user_id", "", key="logout_uid")
#     cookie_manager.set("user_name", "", key="logout_name")
#     cookie_manager.set("user_role", "", key="logout_role")

#     for key in ["user_id", "user_name", "user_role"]:
#         st.session_state.pop(key, None)

#     st.experimental_set_query_params(**{})
#     st.success("Wylogowano pomyślnie!")
#     st.switch_page("app.py")

# # Inicjalizacja aktywnej sekcji w sesji
# if "active_section" not in st.session_state:
#     st.session_state["active_section"] = "podroze"


# def set_active_section(section_name):
#     st.session_state["active_section"] = section_name


# left_col, right_col = st.columns([3, 1])

# with left_col:
#     st.divider()

#     active_section = st.session_state.get("active_section", "podroze")

#     if active_section == "podroze":
#         st.subheader("Twoje podróże i rezerwacje")
#         reservations = get_user_reservations(user_id, conn)

#         if reservations.empty:
#             st.info("Nie masz jeszcze żadnych rezerwacji.")
#         else:
#             for idx, row in reservations.iterrows():
#                 st.markdown(
#                     f"""
#                     **{row.get('nazwa', 'Nazwa noclegu')}**  
#                     Od {row.get('data_zameldowania', '')} do {row.get('data_wymeldowania', '')}  
#                     Status: {row.get('status', '')}  
#                     Cena całkowita: {row.get('calkowita_cena', '')} PLN
#                     ---
#                     """
#                 )
#     elif active_section == "listy":
#         st.subheader("Twoje zapisane listy")
#         st.info("Na razie brak zapisanych list.")
#     elif active_section == "opinie":
#         st.subheader("Twoje opinie")
#         opinions = get_user_opinions(user_id, conn)
#         if opinions.empty:
#             st.info("Nie dodałeś żadnych opinii.")
#         else:
#             for idx, op in opinions.iterrows():
#                 with st.expander(f"Opinia o {op.get('nazwa_noclegu', 'Nocleg')} (ocena: {op.get('ocena', '')})"):
#                     st.write(op.get('komentarz', ''))
#                     if can_edit_opinion(op['id_opinii'], user_id, conn):
#                         new_comment = st.text_area("Edytuj komentarz", value=op.get('komentarz', ''), key=f"op_{op['id_opinii']}")
#                         new_rating = st.slider("Ocena", min_value=1, max_value=5, value=op.get('ocena', 5), key=f"rating_{op['id_opinii']}")
#                         if st.button("Zapisz", key=f"save_{op['id_opinii']}"):
#                             update_opinion(op['id_opinii'], new_rating, new_comment, conn)
#                             st.success("Opinia została zaktualizowana.")
#                         if st.button("Usuń opinię", key=f"del_{op['id_opinii']}"):
#                             delete_opinion(op['id_opinii'], conn)
#                             st.success("Opinia została usunięta.")
#     elif active_section == "dane":
#         st.subheader("Twoje dane osobowe")
#         profile = get_user_profile(user_id, conn)
#         with st.form("edit_profile"):
#             imie = st.text_input("Imię", value=profile.get("imie", ""))
#             nazwisko = st.text_input("Nazwisko", value=profile.get("nazwisko", ""))
#             telefon = st.text_input("Telefon", value=profile.get("telefon", ""))
#             email = profile.get("email", "")
#             st.markdown(f"**E-mail:** {email}")
#             submitted = st.form_submit_button("Zapisz zmiany")
#             if submitted:
#                 update_user_info(user_id, imie, nazwisko, telefon, conn)
#                 st.success("Dane zostały zapisane.")
#     elif active_section == "zmien_haslo":
#         st.subheader("Zmiana hasła")
#         with st.form("change_password"):
#             old_pass = st.text_input("Podaj obecne hasło", type="password")
#             new_pass = st.text_input("Nowe hasło", type="password")
#             new_pass2 = st.text_input("Powtórz nowe hasło", type="password")
#             submit = st.form_submit_button("Zmień hasło")
#             if submit:
#                 if new_pass != new_pass2:
#                     st.error("Nowe hasła nie są identyczne!")
#                 else:
#                     success = verify_and_update_password(user_id, old_pass, new_pass, conn)
#                     if success:
#                         st.success("Hasło zostało zmienione pomyślnie.")
#                     else:
#                         st.error("Obecne hasło jest niepoprawne.")
#     elif active_section == "obiekt":
#         st.subheader("Rejestracja obiektu")
#         st.info("Funkcjonalność w opracowaniu.")

# with right_col:
#     st.markdown(
#         """
#         <style>
#             .account-sidebar {
#                 background-color: #E6E6E6;
#                 padding: 16px;
#                 border-radius: 0 0 0 12px;
#                 display: flex;
#                 flex-direction: column;
#                 gap: 12px;
#                 margin: 0;
#                 min-height: 30em;
#                 justify-content: flex-start;
#                 position: relative;
#                 right: 0em;
#                 top: 0em;
#                 bottom: 10em;
#                 width: 100%;
#                 z-index: 10001;
#                 padding-bottom: 90px;
#             }
#             .account-tile {
#                 background-color: #ffffff;
#                 border-radius: 10px;
#                 padding: 14px 16px;
#                 box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
#             }
#             .account-tile-title {
#                 color: #000000;
#                 font-weight: 700;
#                 font-size: 0.95rem;
#                 margin: 0;
#             }
#             .account-list {
#                 list-style: none;
#                 padding: 0;
#                 margin: 12px 0 0 0;
#                 display: grid;
#                 gap: 10px;
#             }
#             .account-list-item {
#                 display: flex;
#                 align-items: center;
#                 gap: 12px;
#                 padding: 12px 14px;
#                 border-radius: 10px;
#                 background-color: #ffffff;
#                 color: #000000;
#                 font-weight: 500;
#                 font-size: 0.93rem;
#                 transition: background-color 0.15s ease;
#                 cursor: pointer;
#             }
#             .account-list-item:hover {
#                 background-color: #F5F5F5;
#             }
#             .account-list-item span {
#                 display: inline-flex;
#                 width: 24px;
#                 justify-content: center;
#                 filter: grayscale(100%);
#             }
#             .account-item-arrow {
#                 margin-left: auto;
#             }
#             a.account-link {
#                 color: inherit;
#                 text-decoration: none;
#                 display: inline-flex;
#                 width: 100%;
#             }
#         </style>
#         <div class="account-sidebar">
#             <div class="account-tile">
#                 <p class="account-tile-title">Moje podróże</p>
#                 <ul class="account-list">
#                     <li class="account-list-item" onclick="window.location='javascript:void(0)'" id="menu-podroze"><span>✈</span>Podróże i rezerwacje<span class="account-item-arrow">›</span></li>
#                     <li class="account-list-item" onclick="window.location='javascript:void(0)'" id="menu-listy"><span>♡</span>Zapisane listy<span class="account-item-arrow">›</span></li>
#                     <li class="account-list-item" onclick="window.location='javascript:void(0)'" id="menu-opinie"><span>✉</span>Moje opinie<span class="account-item-arrow">›</span></li>
#                 </ul>
#             </div>
#             <div class="account-tile">
#                 <p class="account-tile-title">Zarządzaj kontem</p>
#                 <ul class="account-list">
#                     <li class="account-list-item" onclick="window.location='javascript:void(0)'" id="menu-dane"><span>☺</span>Dane osobowe<span class="account-item-arrow">›</span></li>
#                     <li class="account-list-item" onclick="window.location='javascript:void(0)'" id="menu-zmien_haslo"><span>⚙</span>Zmień hasło<span class="account-item-arrow">›</span></li>
#                 </ul>
#             </div>
#             <div class="account-tile">
#                 <p class="account-tile-title">Zarządzaj obiektem</p>
#                 <ul class="account-list">
#                     <li class="account-list-item" onclick="window.location='javascript:void(0)'" id="menu-obiekt"><span>⌂</span>Zarejestruj swój obiekt<span class="account-item-arrow">›</span></li>
#                 </ul>
#             </div>
#             <div class="account-tile">
#                 <p class="account-tile-title">Inne</p>
#                 <ul class="account-list">
#                     <li class="account-list-item"><span>❓</span>Skontaktuj się z obsługą klienta<span class="account-item-arrow">›</span></li>
#                     <li class="account-list-item"><span>⚠</span>Informacje dotyczące bezpieczeństwa<span class="account-item-arrow">›</span></li>
#                     <li class="account-list-item"><span>⚖</span>Rozwiązywanie sporów<span class="account-item-arrow">›</span></li>
#                     <li class="account-list-item" style="font-weight: 700;">
#                         <span>⏻</span>
#                         <a href="/?page=pages/konto.py&logout=1" target="_top" style="color: inherit; text-decoration: none; display: inline-flex; width: 100%;">
#                             Wyloguj
#                         </a>
#                     </li>
#                 </ul>
#             </div>
#         </div>

#         <script>
#         const sections = {
#             "menu-podroze": "podroze",
#             "menu-listy": "listy",
#             "menu-opinie": "opinie",
#             "menu-dane": "dane",
#             "menu-zmien_haslo": "zmien_haslo",
#             "menu-obiekt": "obiekt"
#         }

#         for (const [id, section] of Object.entries(sections)) {
#             // Dodajemy nasłuchiwanie kliknięcia i aktualizację st.session_state poprzez Streamlit custom event
#             const el = document.getElementById(id)
#             if(el){
#                 el.style.cursor = "pointer"
#                 el.onclick = () => {
#                     // Wysyłamy do Streamlit event z nazwą sekcji (nie ma natywnego JS=>Python w streamlit więc zrobimy przez runpy)
#                     window.parent.postMessage({isStreamlitMessage: true, type: "CUSTOM_EVENT", event: {name:"set_section", section: section}}, "*")
#                 }
#             }
#         }
#         </script>
#         """,
#         unsafe_allow_html=True,
#     )

# # Obsługa komunikatów z JS do Streamlit (ale tutaj Streamlit nie obsługuje JS bezpośrednio).
# # W standardowym Streamlit bez rozszerzeń nie ma prostego "nasłuchiwania" JS, więc zamiast tego podmienimy prawie wszystko na `st.button` w prawym menu.
# # Jednak zgodnie z Twoim пожелaniem pozostawiłem styl i strukturę.
# # Jeśli chcesz, mogę przerobić to tak, żeby menu z prawej kolumny było czysto pytonowe - klikalne buttony, które od razu wywołają zmianę sekcji bez trików JS.

# st.markdown(
#     """
#     <style>
#         .custom-footer {
#             position: static !important;
#             left: 0em !important;
#             right: 0em !important;
#             bottom: auto !important;
#             z-index: 1 !important;
#             margin: 0 auto !important;
#             width: 100% !important;
#             border-top: 1px solid rgba(0, 0, 0, 0.08) !important;
#         }

#         .block-container {
#             padding-bottom: 24px !important;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# render_page_footer()



