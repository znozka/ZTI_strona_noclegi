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
#     verify_and_update_user_credentials,
#     hash_password, 
#     check_password,
#     add_new_property,
#     get_user_properties,
#     delete_property,
#     get_property_reviews,
#     upsert_owner_reply
# )


# def switch_section(section_name):
#     """Czyści stan edycji i przełącza sekcję."""
#     # Usuwamy wszystkie klucze zaczynające się od 'editing_' lub 'form_'
#     for key in list(st.session_state.keys()):
#         if key.startswith("editing_") or key.startswith("form_"):
#             del st.session_state[key]
    
#     st.session_state.active_section = section_name
#     st.rerun()

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
# if not st.session_state.get("user_name"):
#     st.warning("Musisz być zalogowany, aby zobaczyć swoje konto")
#     st.markdown(
#         """
#         <div style="margin-top: 8px;">
#             <a href="/login"
#                target="_self"
#                style="text-decoration: none; font-size: 0.9rem; color: #0066cc; padding: 8px 0; display: inline-block; transition: color 0.2s ease;"
#                onmouseover="this.style.color='#004499'; this.style.textDecoration='underline';"
#                onmouseout="this.style.color='#0066cc'; this.style.textDecoration='none';">
#                  Przejdź do logowania
#             </a>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )
#     st.stop()

# user_id = st.session_state.get("user_id")
# conn = st.connection("azure_sql", type="sql")


# st.markdown(
#     """
#     <style>
#         .custom-page{
#             position: static !important;
#             left: 0em !important;
#             right: 0em !important;
#             bottom: auto !important;
#             z-index: 1 !important;
#             margin: 0 auto !important;
#             border-top: 1px solid rgba(0, 0, 0, 0.08) !important;
#         }

#         .block-container {
#             padding-bottom: 0em !important;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )


# # Inicjalizacja stanu aktywnej sekcji w session_state
# if "active_section" not in st.session_state:
#     st.session_state.active_section = "rezerwacje"

# left_col, right_col= st.columns([8, 1])

# with left_col:
    
#     if st.session_state.active_section == "opinie":
#         st.subheader("Oto Twoje opinie z ostaniego roku podróży!")
#         st.markdown("Zmieniłeś zdanie odnośnie któregoś noclegu? Zaktualizuj swoją opinię!") 
#         st.divider()
#         opinie_df = get_user_opinions(user_id, conn)
        
#         if not opinie_df.empty:
#             for _, row in opinie_df.iterrows():
#                 with st.container():
#                     st.markdown(f"**Obiekt:** {row['nazwa_obiektu']}")
#                     st.markdown(f"**Ocena:** {'⭐' * int(row['ocena'])}")
#                     st.markdown(f"**Komentarz:** {row['komentarz'] or '*(brak)*'}")
                    
#                     # Tworzymy kolumny dla przycisków, aby ładnie wyglądały obok siebie
#                     col_edit, col_del, col_empty = st.columns([1,1,6])

#                     with col_edit:
#                         if st.button("Edytuj opinię", key=f"edit_{row['id_opinii']}", use_container_width=True):
#                             st.session_state[f"editing_{row['id_opinii']}"] = True
                            
#                     with col_del:
#                         if st.button("Usuń opinię", key=f"del_{row['id_opinii']}", use_container_width=True):
#                             success, msg = delete_opinion(row['id_opinii'], conn)
#                             if success:
#                                 st.success(msg)
#                                 st.rerun()

#                     # Formularz edycji (pozostaje bez zmian)
#                     if st.session_state.get(f"editing_{row['id_opinii']}", False):
#                         with st.form(key=f"form_{row['id_opinii']}"):
#                             new_rating = st.slider("Nowa ocena", 1, 5, int(row['ocena']))
#                             new_comment = st.text_area("Nowy komentarz", row['komentarz'])
#                             if st.form_submit_button("Zapisz zmiany"):
#                                 update_opinion(row['id_opinii'], new_rating, new_comment, conn)
#                                 st.session_state[f"editing_{row['id_opinii']}"] = False
#                                 st.rerun()
#                     target_url = (
#                         f"/strona_noclegu?id={row['id_noclegu']}"
#                         "&miejsce=Kraków"  # Jeśli miejsce jest w bazie, użyj row['miasto']
#                         "&data_od=2026-06-27"
#                         "&data_do=2026-06-29"
#                         "&osoby=2"
#                         "&clicked=True"
#                     )

#                     st.markdown(f"[Zobacz obiekt]({target_url})")
#                     st.divider()
#         else:
#             st.info("Nie dodałeś jeszcze żadnych opinii.")

#     if st.session_state.active_section == "dane_osobowe":
#             st.subheader("Twoje dane osobowe")
#             user_data = get_user_profile(user_id, conn)
            
#             if user_data:
#                 with st.form(key="profile_form"):
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         new_imie = st.text_input("Imię", value=user_data['imie'])
#                         new_telefon = st.text_input("Telefon", value=user_data['telefon'] or "")
#                     with col2:
#                         new_nazwisko = st.text_input("Nazwisko", value=user_data['nazwisko'])
#                         # Pole email z informacją o braku edycji
#                         st.text_input("Email", value=user_data['email'], disabled=True, help="Adres email jest powiązany z kontem i nie może być zmieniony w tym miejscu.")
                    
#                     if st.form_submit_button("Zapisz zmiany"):
#                         update_user_info(user_id, new_imie, new_nazwisko, new_telefon, conn)
#                         st.success("Dane zostały zaktualizowane!")
#                         st.rerun()

#                 # DODANA SEKCJA INFORMACYJNA
#                 st.info("""
#                 **Dlaczego nie mogę edytować adresu email i hasła?**
#                 * Ze względu na bezpieczeństwo danych użytkowników zmiana adresu email oraz hasła wymaga dodatkowej weryfikacji tożsamości, aby chronić konto przed nieautoryzowanym dostępem.
#                 * Edycję tych danych znajdziesz w dedykowanej sekcji **"Zmień hasło"** oraz w ustawieniach zabezpieczeń konta. 
#                 """)
#             else:
#                 st.error("Nie udało się pobrać danych użytkownika.")

#     if st.session_state.active_section == "zmiana_hasla":
#         st.subheader("Zmień hasło i email")
        
#         # Pobieramy aktualny email z profilu, aby wyświetlić go w polu edycji
#         user_data = get_user_profile(user_id, conn)
        
#         with st.form(key="credentials_form"):
#             st.write("Wprowadź aktualne hasło, aby potwierdzić zmiany.")
            
#             old_password = st.text_input("Obecne hasło", type="password")
#             new_email = st.text_input("Nowy adres email", value=user_data['email'])
#             new_password = st.text_input("Nowe hasło (pozostaw puste, jeśli nie zmieniasz)", type="password")
#             confirm_password = st.text_input("Potwierdź nowe hasło", type="password")
            
#             if st.form_submit_button("Zaktualizuj dane"):
#                 if not old_password:
#                     st.error("Musisz podać obecne hasło.")
#                 elif new_password and new_password != confirm_password:
#                     st.error("Nowe hasła nie są identyczne.")
#                 elif new_password and len(new_password) < 8:
#                     st.error("Nowe hasło musi mieć min. 8 znaków.")
#                 else:
#                     # Jeśli hasło nie jest zmieniane, używamy starego hasha
#                     final_pass_hash = hash_password(new_password) if new_password else user_data['haslo_hash']
                    
#                     success, msg = verify_and_update_user_credentials(user_id, old_password, final_pass_hash, new_email, conn)
                    
#                     if success:
#                         st.success(msg)
#                     else:
#                         st.error(msg)

#     if st.session_state.active_section == "rezerwacje":
#         st.subheader("Twoje rezerwacje")
#         st.markdown("Lista Twoich podróży, posortowana od najnowszej.")
#         st.divider()
        
#         # Pobranie rezerwacji (pamiętaj o metodzie w database.py)
#         rezerwacje_df = get_user_reservations(user_id, conn)
        
#         if not rezerwacje_df.empty:
#             # Sortowanie po dacie (zakładam kolumnę 'data_rezerwacji')
#             rezerwacje_df['data_utworzenia'] = pd.to_datetime(rezerwacje_df['data_utworzenia'])
#             rezerwacje_df = rezerwacje_df.sort_values(by='data_utworzenia', ascending=False)
            
#             for _, row in rezerwacje_df.iterrows():
#                 with st.container():
#                     st.markdown(f"### {row['nazwa']}")
#                     st.write(f"{row['data_zameldowania'].strftime('%Y-%m-%d')} - {row['data_wymeldowania'].strftime('%Y-%m-%d')}")
#                     st.write(f"**Status:** {row.get('status', 'Potwierdzona')}")

#                     st.markdown(f"[Zobacz obiekt](/strona_noclegu?id={row['id_noclegu']})")
#                     st.divider()
#         else:
#             st.info("Nie masz jeszcze żadnych rezerwacji.")

#     if st.session_state.active_section == "rejestracja_obiektu":
#             st.subheader("Zarejestruj swój obiekt")
            
#             with st.form(key="add_property_form"):
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     nazwa = st.text_input("Nazwa obiektu")
#                     typ = st.selectbox("Typ obiektu", ["Apartament", "Dom", "Pokój", "Pensjonat", "Willa"])
#                     cena = st.number_input("Cena za noc (PLN)", min_value=0.0, step=10.0)
#                 with col2:
#                     miasto = st.text_input("Miasto")
#                     adres = st.text_input("Adres")
#                     osoby = st.number_input("Maksymalna liczba osób", min_value=1, step=1)
                
#                 opis = st.text_area("Opis obiektu")
                
#                 if st.form_submit_button("Zarejestruj obiekt"):
#                     if not nazwa or not miasto:
#                         st.error("Nazwa i miasto są wymagane!")
#                     else:
#                         success, msg = add_new_property(user_id, nazwa, opis, typ, miasto, adres, cena, osoby, conn)
#                         if success:
#                             st.success(msg)
#                         else:
#                             st.error(msg)

#     if st.session_state.active_section == "zarzadzanie_obiektami":
#             st.subheader("Zarządzaj swoimi obiektami")
#             moje_obiekty = get_user_properties(int(user_id), conn)
            
#             if not moje_obiekty.empty:
#                 # 1. POBIERAMY OPINIE RAZ DLA CAŁEGO WŁAŚCICIELA PRZED PĘTLĄ
#                 opinie_all = get_property_reviews(user_id, conn)
                
#                 for _, row in moje_obiekty.iterrows():
#                     with st.expander(f"{row['nazwa']} ({row['lokalizacja_miasto']})"):
#                         st.write(f"**Typ:** {row['typ_obiektu']} | **Cena:** {row['cena_za_noc']} PLN")
#                         st.write(f"**Opis:** {row['opis']}")
                        
#                         # Przyciski akcji
#                         col1, col2 = st.columns(2)
#                         with col1:
#                             if st.button("Edytuj dane", key=f"edit_prop_{row['id_noclegu']}"):
#                                 st.info("Logika edycji w budowie")

#                         with col2:
#                             with st.popover("❌ Usuń obiekt", use_container_width=True):
#                                 st.warning("Czy na pewno chcesz bezpowrotnie usunąć ten obiekt?")
#                                 if st.button("Tak, usuń", key=f"confirm_del_{row['id_noclegu']}", type="primary"):
#                                     success, msg = delete_property(row['id_noclegu'], conn)
#                                     if success:
#                                         st.success(msg)
#                                         st.rerun()
#                                     else:
#                                         st.error(msg)
                                            
#                         st.divider()
#                         st.subheader("Opinie gości")
                        
#                         # 2. BEZPIECZNE FILTROWANIE OPINII DLA KONKRETNEGO OBIEKTU
#                         if opinie_all is not None and not opinie_all.empty and 'id_noclegu' in opinie_all.columns:
#                             opinie_obiektu = opinie_all[opinie_all['id_noclegu'] == row['id_noclegu']].head(5)
                            
#                             if not opinie_obiektu.empty:
#                                 for _, rev in opinie_obiektu.iterrows():
#                                     st.markdown(f"**{rev['autor']}** - ⭐ {rev['ocena']}")
#                                     st.caption(rev['komentarz'] if rev['komentarz'] else "*(brak komentarza)*")
                                    
#                                     # Pobieramy istniejącą odpowiedź (jeśli jest w DataFrame, w przeciwnym razie pusty string)
#                                     istniejaca_odp = rev.get('odpowiedz_wlasciciela') if pd.notna(rev.get('odpowiedz_wlasciciela')) else ""
                                    
#                                     # Formularz dedykowany dla konkretnej odpowiedzi
#                                     with st.form(key=f"reply_form_{rev['id_opinii']}"):
#                                         user_reply = st.text_area(
#                                             "Twoja odpowiedź jako właściciel:", 
#                                             value=istniejaca_odp,
#                                             key=f"input_{rev['id_opinii']}"
#                                         )
                                        
#                                         # Przycisk wysyłający / akceptujący formularz
#                                         submit_reply = st.form_submit_button("Zatwierdź odpowiedź")
                                        
#                                         if submit_reply:
#                                             if user_reply.strip() != istniejaca_odp: # Wyślij tylko jeśli treść się zmieniła
#                                                 success, msg = upsert_owner_reply(rev['id_opinii'], user_reply, conn)
#                                                 if success:
#                                                     st.success(msg)
#                                                     st.rerun()
#                                                 else:
#                                                     st.error(msg)
#                                             else:
#                                                 st.info("Treść odpowiedzi nie uległa zmianie.")
#                             else:
#                                 st.info("Ten obiekt nie otrzymał jeszcze żadnych opinii.")
#                         else:
#                             st.info("Nie masz jeszcze żadnych opinii od gości.")
#             else:
#                 st.info("Nie zarejestrowałeś jeszcze żadnego obiektu.")
                            

# with right_col:

#     def menu_item(label, key, section):
#         if st.button(label, key=key):
#             switch_section(section)

#     menu_item("Historia rezerwacji ›", "btn_travels", "rezerwacje")
#     menu_item("Moje opinie          ›", "btn_opinions", "opinie")
#     menu_item("Dane osobowe         ›", "btn_profile", "dane_osobowe")
#     menu_item("Zmień hasło          ›", "btn_password", "zmiana_hasla")
#     menu_item("Zarejestruj obiekt   ›", "btn_register_prop", "rejestracja_obiektu")
#     menu_item("Moje obiekty         ›", "btn_manage_props", "zarzadzanie_obiektami")
#     menu_item("Pomoc                ›", "btn_support", "support")
#     menu_item("Bezpieczeństwo      ›", "btn_security", "security")
    

#     if st.button("⏻  Wyloguj", key="btn_logout"):
#         cookie_manager = stx.CookieManager(key="root_cookie_saver")
#         cookie_manager.set("user_id", "", key="logout_uid")
#         cookie_manager.set("user_name", "", key="logout_name")
#         cookie_manager.set("user_role", "", key="logout_role")

#         for key in ["user_id", "user_name", "user_role", "active_section"]:
#             st.session_state.pop(key, None)

#         st.success("Wylogowano pomyślnie!")
#         st.switch_page("app.py")
        

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
#             padding-bottom: 0em !important;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# render_page_footer()

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
#     verify_and_update_user_credentials,
#     hash_password, 
#     check_password,
#     add_new_property,
#     get_user_properties,
#     delete_property,
#     get_property_reviews,
#     upsert_owner_reply
# )


# def switch_section(section_name):
#     """Czyści stan edycji i przełącza sekcję."""
#     # Usuwamy wszystkie klucze zaczynające się od 'editing_' lub 'form_'
#     for key in list(st.session_state.keys()):
#         if key.startswith("editing_") or key.startswith("form_"):
#             del st.session_state[key]
    
#     st.session_state.active_section = section_name
#     st.rerun()

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
# if not st.session_state.get("user_name"):
#     st.warning("Musisz być zalogowany, aby zobaczyć swoje konto")
#     st.markdown(
#         """
#         <div style="margin-top: 8px;">
#             <a href="/login"
#                target="_self"
#                style="text-decoration: none; font-size: 0.9rem; color: #0066cc; padding: 8px 0; display: inline-block; transition: color 0.2s ease;"
#                onmouseover="this.style.color='#004499'; this.style.textDecoration='underline';"
#                onmouseout="this.style.color='#0066cc'; this.style.textDecoration='none';">
#                  Przejdź do logowania
#             </a>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )
#     st.stop()

# user_id = st.session_state.get("user_id")
# conn = st.connection("azure_sql", type="sql")


# st.markdown(
#     """
#     <style>
#         .custom-page{
#             position: static !important;
#             left: 0em !important;
#             right: 0em !important;
#             bottom: auto !important;
#             z-index: 1 !important;
#             margin: 0 auto !important;
#             border-top: 1px solid rgba(0, 0, 0, 0.08) !important;
#         }

#         .block-container {
#             padding-bottom: 0em !important;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )


# # Inicjalizacja stanu aktywnej sekcji w session_state
# if "active_section" not in st.session_state:
#     st.session_state.active_section = "rezerwacje"


# # Tworzenie zakładek głównych
# tab_travels, tab_profile, tab_owner = st.tabs(["Moje podróże", "Mój profil", "Panel Właściciela"])

# # ==========================================
# # ZAKŁADKA: MOJE PODRÓŻE
# # ==========================================
# with tab_travels:
    
#     # Kategoria: Historia rezerwacji
#     st.subheader("Twoje rezerwacje")
#     st.markdown("Lista Twoich podróży, posortowana od najnowszej.")
#     st.divider()
    
#     rezerwacje_df = get_user_reservations(user_id, conn)
    
#     if not rezerwacje_df.empty:
#         rezerwacje_df['data_utworzenia'] = pd.to_datetime(rezerwacje_df['data_utworzenia'])
#         rezerwacje_df = rezerwacje_df.sort_values(by='data_utworzenia', ascending=False)
        
#         for _, row in rezerwacje_df.iterrows():
#             with st.container():
#                 st.markdown(f"### {row['nazwa']}")
#                 st.write(f"{row['data_zameldowania'].strftime('%Y-%m-%d')} - {row['data_wymeldowania'].strftime('%Y-%m-%d')}")
#                 st.write(f"**Status:** {row.get('status', 'Potwierdzona')}")

#                 st.markdown(f"[Zobacz obiekt](/strona_noclegu?id={row['id_noclegu']})")
#                 st.divider()
#     else:
#         st.info("Nie masz jeszcze żadnych rezerwacji.")

#     # Kategoria: Moje opinie
#     st.subheader("Oto Twoje opinie z ostaniego roku podróży!")
#     st.markdown("Zmieniłeś zdanie odnośnie któregoś noclegu? Zaktualizuj swoją opinię!") 
#     st.divider()
#     opinie_df = get_user_opinions(user_id, conn)
    
#     if not opinie_df.empty:
#         for _, row in opinie_df.iterrows():
#             with st.container():
#                 st.markdown(f"**Obiekt:** {row['nazwa_obiektu']}")
#                 st.markdown(f"**Ocena:** {'⭐' * int(row['ocena'])}")
#                 st.markdown(f"**Komentarz:** {row['komentarz'] or '*(brak)*'}")
                
#                 col_edit, col_del, col_empty = st.columns([1,1,6])

#                 with col_edit:
#                     if st.button("Edytuj opinię", key=f"edit_{row['id_opinii']}", use_container_width=True):
#                         st.session_state[f"editing_{row['id_opinii']}"] = True
                        
#                 with col_del:
#                     if st.button("Usuń opinię", key=f"del_{row['id_opinii']}", use_container_width=True):
#                         success, msg = delete_opinion(row['id_opinii'], conn)
#                         if success:
#                             st.success(msg)
#                             st.rerun()

#                 if st.session_state.get(f"editing_{row['id_opinii']}", False):
#                     with st.form(key=f"form_{row['id_opinii']}"):
#                         new_rating = st.slider("Nowa ocena", 1, 5, int(row['ocena']))
#                         new_comment = st.text_area("Nowy komentarz", row['komentarz'])
#                         if st.form_submit_button("Zapisz zmiany"):
#                             update_opinion(row['id_opinii'], new_rating, new_comment, conn)
#                             st.session_state[f"editing_{row['id_opinii']}"] = False
#                             st.rerun()
#                 target_url = (
#                     f"/strona_noclegu?id={row['id_noclegu']}"
#                     "&miejsce=Kraków"
#                     "&data_od=2026-06-27"
#                     "&data_do=2026-06-29"
#                     "&osoby=2"
#                     "&clicked=True"
#                 )

#                 st.markdown(f"[Zobacz obiekt]({target_url})")
#                 st.divider()
#     else:
#         st.info("Nie dodałeś jeszcze żadnych opinii.")


# # ==========================================
# # ZAKŁADKA: MÓJ PROFIL
# # ==========================================
# with tab_profile:
    
#     # Kategoria: Dane osobowe
#     st.subheader("Twoje dane osobowe")
#     user_data = get_user_profile(user_id, conn)
    
#     if user_data:
#         with st.form(key="profile_form"):
#             col1, col2 = st.columns(2)
#             with col1:
#                 new_imie = st.text_input("Imię", value=user_data['imie'])
#                 new_telefon = st.text_input("Telefon", value=user_data['telefon'] or "")
#             with col2:
#                 new_nazwisko = st.text_input("Nazwisko", value=user_data['nazwisko'])
#                 st.text_input("Email", value=user_data['email'], disabled=True, help="Adres email jest powiązany z kontem i nie może być zmieniony w tym miejscu.")
            
#             if st.form_submit_button("Zapisz zmiany"):
#                 update_user_info(user_id, new_imie, new_nazwisko, new_telefon, conn)
#                 st.success("Dane zostały zaktualizowane!")
#                 st.rerun()
#     else:
#         st.error("Nie udało się pobrać danych użytkownika.")

#     st.divider()

#     # Kategoria: Zmień hasło
#     st.subheader("Zmień hasło i email")
    
#     if user_data:
#         with st.form(key="credentials_form"):
#             st.write("Wprowadź aktualne hasło, aby potwierdzić zmiany.")
            
#             old_password = st.text_input("Obecne hasło", type="password")
#             new_email = st.text_input("Nowy adres email", value=user_data['email'])
#             new_password = st.text_input("Nowe hasło (pozostaw puste, jeśli nie zmieniasz)", type="password")
#             confirm_password = st.text_input("Potwierdź nowe hasło", type="password")
            
#             if st.form_submit_button("Zaktualizuj dane"):
#                 if not old_password:
#                     st.error("Musisz podać obecne hasło.")
#                 elif new_password and new_password != confirm_password:
#                     st.error("Nowe hasła nie są identyczne.")
#                 elif new_password and len(new_password) < 8:
#                     st.error("Nowe hasło musi mieć min. 8 znaków.")
#                 else:
#                     final_pass_hash = hash_password(new_password) if new_password else user_data['haslo_hash']
                    
#                     success, msg = verify_and_update_user_credentials(user_id, old_password, final_pass_hash, new_email, conn)
                    
#                     if success:
#                         st.success(msg)
#                     else:
#                         st.error(msg)
                        
#     st.divider()
    
#     # Przycisk wylogowania umieszczony w zakładce "Mój profil"
#     if st.button("⏻  Wyloguj", key="btn_logout"):
#         cookie_manager = stx.CookieManager(key="root_cookie_saver")
#         cookie_manager.set("user_id", "", key="logout_uid")
#         cookie_manager.set("user_name", "", key="logout_name")
#         cookie_manager.set("user_role", "", key="logout_role")

#         for key in ["user_id", "user_name", "user_role", "active_section"]:
#             st.session_state.pop(key, None)

#         st.success("Wylogowano pomyślnie!")
#         st.switch_page("app.py")


# # ==========================================
# # ZAKŁADKA: PANEL WŁAŚCICIELA
# # ==========================================
# with tab_owner:
    
#     # Kategoria: Zarejestruj obiekt
#     st.subheader("Zarejestruj swój obiekt")
    
#     with st.form(key="add_property_form"):
#         col1, col2 = st.columns(2)
#         with col1:
#             nazwa = st.text_input("Nazwa obiektu")
#             typ = st.selectbox("Typ obiektu", ["Apartament", "Dom", "Pokój", "Pensjonat", "Willa"])
#             cena = st.number_input("Cena za noc (PLN)", min_value=0.0, step=10.0)
#         with col2:
#             miasto = st.text_input("Miasto")
#             adres = st.text_input("Adres")
#             osoby = st.number_input("Maksymalna liczba osób", min_value=1, step=1)
        
#         opis = st.text_area("Opis obiektu")
        
#         if st.form_submit_button("Zarejestruj obiekt"):
#             if not nazwa or not miasto:
#                 st.error("Nazwa i miasto są wymagane!")
#             else:
#                 success, msg = add_new_property(user_id, nazwa, opis, typ, miasto, adres, cena, osoby, conn)
#                 if success:
#                     st.success(msg)
#                 else:
#                     st.error(msg)

#     st.divider()

#     # Kategoria: Moje obiekty
#     st.subheader("Zarządzaj swoimi obiektami")
#     moje_obiekty = get_user_properties(int(user_id), conn)
    
#     if not moje_obiekty.empty:
#         opinie_all = get_property_reviews(user_id, conn)
        
#         for _, row in moje_obiekty.iterrows():
#             with st.expander(f"{row['nazwa']} ({row['lokalizacja_miasto']})"):
#                 st.write(f"**Typ:** {row['typ_obiektu']} | **Cena:** {row['cena_za_noc']} PLN")
#                 st.write(f"**Opis:** {row['opis']}")
                
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     if st.button("Edytuj dane", key=f"edit_prop_{row['id_noclegu']}"):
#                         st.info("Logika edycji w budowie")

#                 with col2:
#                     with st.popover("❌ Usuń obiekt", use_container_width=True):
#                         st.warning("Czy na pewno chcesz bezpowrotnie usunąć ten obiekt?")
#                         if st.button("Tak, usuń", key=f"confirm_del_{row['id_noclegu']}", type="primary"):
#                             success, msg = delete_property(row['id_noclegu'], conn)
#                             if success:
#                                 st.success(msg)
#                                 st.rerun()
#                             else:
#                                 st.error(msg)
                                    
#                 st.divider()
#                 st.subheader("Opinie gości")
                
#                 if opinie_all is not None and not opinie_all.empty and 'id_noclegu' in opinie_all.columns:
#                     opinie_obiektu = opinie_all[opinie_all['id_noclegu'] == row['id_noclegu']].head(5)
                    
#                     if not opinie_obiektu.empty:
#                         for _, rev in opinie_obiektu.iterrows():
#                             st.markdown(f"**{rev['autor']}** - ⭐ {rev['ocena']}")
#                             st.caption(rev['komentarz'] if rev['komentarz'] else "*(brak komentarza)*")
                            
#                             istniejaca_odp = rev.get('odpowiedz_wlasciciela') if pd.notna(rev.get('odpowiedz_wlasciciela')) else ""
                            
#                             with st.form(key=f"reply_form_{rev['id_opinii']}"):
#                                 user_reply = st.text_area(
#                                     "Twoja odpowiedź jako właściciel:", 
#                                     value=istniejaca_odp,
#                                     key=f"input_{rev['id_opinii']}"
#                                 )
                                
#                                 submit_reply = st.form_submit_button("Zatwierdź odpowiedź")
                                
#                                 if submit_reply:
#                                     if user_reply.strip() != istniejaca_odp:
#                                         success, msg = upsert_owner_reply(rev['id_opinii'], user_reply, conn)
#                                         if success:
#                                             st.success(msg)
#                                             st.rerun()
#                                         else:
#                                             st.error(msg)
#                                     else:
#                                         st.info("Treść odpowiedzi nie uległa zmianie.")
#                     else:
#                         st.info("Ten obiekt nie otrzymał jeszcze żadnych opinii.")
#                 else:
#                     st.info("Nie masz jeszcze żadnych opinii od gości.")
#     else:
#         st.info("Nie zarejestrowałeś jeszcze żadnego obiektu.")


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
#             padding-bottom: 0em !important;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# render_page_footer()
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
    update_user_info,
    verify_and_update_user_credentials,
    hash_password, 
    check_password,
    add_new_property,
    get_user_properties,
    delete_property,
    get_property_reviews,
    upsert_owner_reply,
    add_opinion  # <--- UPEWNIJ SIĘ, ŻE MASZ TAKĄ LUB PODOBNĄ FUNKCJĘ W DATABASE
)

def switch_section(section_name):
    """Czyści stan edycji i przełącza sekcję."""
    for key in list(st.session_state.keys()):
        if key.startswith("editing_") or key.startswith("form_") or key.startswith("adding_"):
            del st.session_state[key]
    
    st.session_state.active_section = section_name
    st.rerun()

st.set_page_config(
    page_title="Moje konto",
    page_icon="assets/images/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header(is_konto_page=True)
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
conn = st.connection("azure_sql", type="sql")

st.markdown(
    """
    <style>
        .custom-page{
            position: static !important;
            left: 0em !important;
            right: 0em !important;
            bottom: auto !important;
            z-index: 1 !important;
            margin: 0 auto !important;
            border-top: 1px solid rgba(0, 0, 0, 0.08) !important;
        }

        .block-container {
            padding-bottom: 0em !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if "active_section" not in st.session_state:
    st.session_state.active_section = "rezerwacje"

# Tworzenie zakładek głównych
tab_travels, tab_profile, tab_owner = st.tabs(["Moje podróże", "Mój profil", "Panel Właściciela"])

# ==========================================
# ZAKŁADKA: MOJE PODRÓŻE
# ==========================================
with tab_travels:
    st.subheader("Twoje rezerwacje i opinie")
    st.markdown("Lista Twoich podróży wraz z wystawionymi opiniami, posortowana od najnowszej.")
    st.divider()
    
    # Pobieramy rezerwacje oraz opinie użytkownika
    rezerwacje_df = get_user_reservations(user_id, conn)
    opinie_df = get_user_opinions(user_id, conn)
    
    if not rezerwacje_df.empty:
        rezerwacje_df['data_utworzenia'] = pd.to_datetime(rezerwacje_df['data_utworzenia'])
        rezerwacje_df = rezerwacje_df.sort_values(by='data_utworzenia', ascending=False)
        
        for _, row in rezerwacje_df.iterrows():
            with st.container():
                # Szczegóły noclegu
                st.markdown(f"### {row['nazwa']}")
                st.write(f"{row['data_zameldowania'].strftime('%Y-%m-%d')} - {row['data_wymeldowania'].strftime('%Y-%m-%d')}")
                st.write(f"**Status:** {row.get('status', 'Potwierdzona')}")

                target_url = (
                    f"/strona_noclegu?id={row['id_noclegu']}"
                    "&miejsce=Kraków"
                    "&data_od=2026-06-27"
                    "&data_do=2026-06-29"
                    "&osoby=2"
                    "&clicked=True"
                )
                st.markdown(f"[Zobacz obiekt]({target_url})")
                
                # Sekcja opinii przypisana bezpośrednio do tego obiektu
                st.markdown("#### Twoja opinia o tym miejscu:")
                
                # Flaga sprawdzająca, czy opinia istnieje
                ma_opinie = False
                opinia_row = None
                
                # !!! ZMIANA: Szukamy po id_rezerwacji, a nie id_noclegu !!!
                if not opinie_df.empty and 'id_rezerwacji' in opinie_df.columns:
                    opinia_obiektu = opinie_df[opinie_df['id_rezerwacji'] == row['id_rezerwacji']].head(1)
                    if not opinia_obiektu.empty:
                        ma_opinie = True
                        opinia_row = opinia_obiektu.iloc[0]

                # --- PRZYPADEK 1: OPINIA JUŻ ISTNIEJE ---
                if ma_opinie:
                    st.markdown(f"**Ocena:** {'⭐' * int(opinia_row['ocena'])}")
                    st.markdown(f"**Komentarz:** {opinia_row['komentarz'] or '*(brak)*'}")
                    
                    col_edit, col_del, col_empty = st.columns([1,1,6])

                    with col_edit:
                        if st.button("Edytuj opinię", key=f"edit_{opinia_row['id_opinii']}", use_container_width=True):
                            st.session_state[f"editing_{opinia_row['id_opinii']}"] = True
                            
                    with col_del:
                        if st.button("Usuń opinię", key=f"del_{opinia_row['id_opinii']}", use_container_width=True):
                            success, msg = delete_opinion(opinia_row['id_opinii'], conn)
                            if success:
                                st.success(msg)
                                st.rerun()

                    if st.session_state.get(f"editing_{opinia_row['id_opinii']}", False):
                        with st.form(key=f"form_{opinia_row['id_opinii']}"):
                            new_rating = st.slider("Nowa ocena", 1, 5, int(opinia_row['ocena']))
                            new_comment = st.text_area("Nowy komentarz", opinia_row['komentarz'])
                            if st.form_submit_button("Zapisz zmiany"):
                                update_opinion(opinia_row['id_opinii'], new_rating, new_comment, conn)
                                st.session_state[f"editing_{opinia_row['id_opinii']}"] = False
                                st.rerun()
                                
                # --- PRZYPADEK 2: BRAK OPINII (DODAWANIE NOWEJ) ---
                else:
                    st.info("Nie dodałeś jeszcze opinii dla tego pobytu.")
                    
                    # Unikalny klucz oparty o id_rezerwacji
                    add_key = f"adding_new_{row['id_rezerwacji']}"
                    
                    if not st.session_state.get(add_key, False):
                        if st.button("Dodaj opinię", key=f"btn_add_{row['id_rezerwacji']}", type="primary"):
                            st.session_state[add_key] = True
                            st.rerun()
                    else:
                        with st.form(key=f"form_add_{row['id_rezerwacji']}"):
                            st.markdown("### Nowa opinia")
                            rating = st.slider("Ocena", 1, 5, 5, key=f"rate_{row['id_rezerwacji']}")
                            comment = st.text_area("Komentarz", placeholder="Napisz co myślisz o tym obiekcie...", key=f"comm_{row['id_rezerwacji']}")
                            
                            col_submit, col_cancel = st.columns([1, 1])
                            with col_submit:
                                submit_btn = st.form_submit_button("Wyślij opinię", use_container_width=True)
                            with col_cancel:
                                cancel_btn = st.form_submit_button("Anuluj", use_container_width=True)
                                
                            if submit_btn:
                                # Wywołanie poprawnej funkcji przekazującej row['id_rezerwacji']
                                success, msg = add_opinion(row['id_rezerwacji'], user_id, row['id_noclegu'], rating, comment, conn)
                                if success:
                                    st.success("Opinia została pomyślnie dodana!")
                                    st.session_state[add_key] = False
                                    st.rerun()
                                else:
                                    st.error(f"Błąd podczas dodawania opinii: {msg}")
                                    
                            if cancel_btn:
                                st.session_state[add_key] = False
                                st.rerun()
                
                st.divider()
    else:
        st.info("Nie masz jeszcze żadnych rezerwacji.")

# ==========================================
# ZAKŁADKA: MÓJ PROFIL
# ==========================================
with tab_profile:
    st.subheader("Twoje dane osobowe")
    user_data = get_user_profile(user_id, conn)
    
    if user_data:
        with st.form(key="profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_imie = st.text_input("Imię", value=user_data['imie'])
                new_telefon = st.text_input("Telefon", value=user_data['telefon'] or "")
            with col2:
                new_nazwisko = st.text_input("Nazwisko", value=user_data['nazwisko'])
                st.text_input("Email", value=user_data['email'], disabled=True, help="Adres email jest powiązany z kontem i nie może być zmieniony w tym miejscu.")
            
            if st.form_submit_button("Zapisz zmiany"):
                update_user_info(user_id, new_imie, new_nazwisko, new_telefon, conn)
                st.success("Dane zostały zaktualizowane!")
                st.rerun()

    else:
        st.error("Nie udało się pobrać danych użytkownika.")

    st.divider()

    st.subheader("Zmień hasło i email")
    
    if user_data:
        with st.form(key="credentials_form"):
            st.write("Wprowadź aktualne hasło, aby potwierdzić zmiany.")
            
            old_password = st.text_input("Obecne hasło", type="password")
            new_email = st.text_input("Nowy adres email", value=user_data['email'])
            new_password = st.text_input("Nowe hasło (pozostaw puste, jeśli nie zmieniasz)", type="password")
            confirm_password = st.text_input("Potwierdź nowe hasło", type="password")
            
            if st.form_submit_button("Zaktualizuj dane"):
                if not old_password:
                    st.error("Musisz podać obecne hasło.")
                elif new_password and new_password != confirm_password:
                    st.error("Nowe hasła nie są identyczne.")
                elif new_password and len(new_password) < 8:
                    st.error("Nowe hasło musi mieć min. 8 znaków.")
                else:
                    final_pass_hash = hash_password(new_password) if new_password else user_data['haslo_hash']
                    
                    success, msg = verify_and_update_user_credentials(user_id, old_password, final_pass_hash, new_email, conn)
                    
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                        
    st.divider()
    
    # if st.button("⏻  Wyloguj", key="btn_logout"):
    #     cookie_manager = stx.CookieManager(key="root_cookie_saver")
    #     cookie_manager.set("user_id", "", key="logout_uid")
    #     cookie_manager.set("user_name", "", key="logout_name")
    #     cookie_manager.set("user_role", "", key="logout_role")

    #     for key in ["user_id", "user_name", "user_role", "active_section"]:
    #         st.session_state.pop(key, None)

    #     st.success("Wylogowano pomyślnie!")
    #     st.switch_page("app.py")

# ==========================================
# ZAKŁADKA: PANEL WŁAŚCICIELA
# ==========================================
with tab_owner:
    st.subheader("Zarejestruj swój obiekt")
    
    with st.form(key="add_property_form"):
        col1, col2 = st.columns(2)
        with col1:
            nazwa = st.text_input("Nazwa obiektu")
            typ = st.selectbox("Typ obiektu", ["Apartament", "Dom", "Pokój", "Pensjonat", "Willa"])
            cena = st.number_input("Cena za noc (PLN)", min_value=0.0, step=10.0)
        with col2:
            miasto = st.text_input("Miasto")
            adres = st.text_input("Adres")
            osoby = st.number_input("Maksymalna liczba osób", min_value=1, step=1)
        
        opis = st.text_area("Opis obiektu")
        
        if st.form_submit_button("Zarejestruj obiekt"):
            if not nazwa or not miasto:
                st.error("Nazwa i miasto są wymagane!")
            else:
                success, msg = add_new_property(user_id, nazwa, opis, typ, miasto, adres, cena, osoby, conn)
                if success:
                    st.success(msg)
                    st.rerun()  # Warto dodać rerun, aby sekcja zarządzania pojawiła się od razu po rejestracji
                else:
                    st.error(msg)

    # Pobieramy obiekty użytkownika przed renderowaniem kolejnej sekcji
    moje_obiekty = get_user_properties(int(user_id), conn)
    
    # Warunek: Pokazuj sekcję zarządzania TYLKO jeśli użytkownik ma przypisane obiekty
    if not moje_obiekty.empty:
        st.divider()
        st.subheader("Zarządzaj swoimi obiektami")
        
        opinie_all = get_property_reviews(user_id, conn)
        
        for _, row in moje_obiekty.iterrows():
            with st.expander(f"{row['nazwa']} ({row['lokalizacja_miasto']})"):
                st.write(f"**Typ:** {row['typ_obiektu']} | **Cena:** {row['cena_za_noc']} PLN")
                st.write(f"**Opis:** {row['opis']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Edytuj dane", key=f"edit_prop_{row['id_noclegu']}"):
                        st.info("Logika edycji w budowie")

                with col2:
                    with st.popover("❌ Usuń obiekt", use_container_width=True):
                        st.warning("Czy na pewno chcesz bezpowrotnie usunąć ten obiekt?")
                        if st.button("Tak, usuń", key=f"confirm_del_{row['id_noclegu']}", type="primary"):
                            success, msg = delete_property(row['id_noclegu'], conn)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                                    
                st.divider()
                st.subheader("Opinie gości")
                
                if opinie_all is not None and not opinie_all.empty and 'id_noclegu' in opinie_all.columns:
                    opinie_obiektu = opinie_all[opinie_all['id_noclegu'] == row['id_noclegu']].head(5)
                    
                    if not opinie_obiektu.empty:
                        for _, rev in opinie_obiektu.iterrows():
                            st.markdown(f"**{rev['autor']}** - ⭐ {rev['ocena']}")
                            st.caption(rev['komentarz'] if rev['komentarz'] else "*(brak komentarza)*")
                            
                            istniejaca_odp = rev.get('odpowiedz_wlasciciela') if pd.notna(rev.get('odpowiedz_wlasciciela')) else ""
                            
                            with st.form(key=f"reply_form_{rev['id_opinii']}"):
                                user_reply = st.text_area(
                                    "Twoja odpowiedź jako właściciel:", 
                                    value=istniejaca_odp,
                                    key=f"input_{rev['id_opinii']}"
                                )
                                
                                submit_reply = st.form_submit_button("Zatwierdź odpowiedź")
                                
                                if submit_reply:
                                    if user_reply.strip() != istniejaca_odp:
                                        success, msg = upsert_owner_reply(rev['id_opinii'], user_reply, conn)
                                        if success:
                                            st.success(msg)
                                            st.rerun()
                                        else:
                                            st.error(msg)
                                    else:
                                        st.info("Treść odpowiedzi nie uległa zmianie.")
                    else:
                        st.info("Ten obiekt nie otrzymał jeszcze żadnych opinii.")
                else:
                    st.info("Nie masz jeszcze żadnych opinii od gości.")


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