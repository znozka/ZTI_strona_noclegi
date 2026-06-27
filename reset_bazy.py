import streamlit as st
from sqlalchemy import text

st.title("Wdrażanie Triggerów InnSight")

try:
    conn = st.connection("azure_sql", type="sql")
    st.write("Połączono z Azure SQL. Instaluję automatyzację w bazie danych...")
except Exception as e:
    st.error(f"Błąd połączenia: {e}")
    st.stop()

# Każdy trigger zdefiniowany jako osobny, czysty ciąg tekstowy bez zbędnych komentarzy na początku
trigger_rezerwacje = """
CREATE OR ALTER TRIGGER TR_Rezerwacje_BlokadaTerminu
ON rezerwacje
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    IF EXISTS (SELECT 1 FROM inserted WHERE status = 'potwierdzona')
    BEGIN
        WITH DatyRezerwacji AS (
            SELECT i.id_noclegu, i.data_zameldowania as DataRez, i.data_wymeldowania
            FROM inserted i WHERE i.status = 'potwierdzona'
            UNION ALL
            SELECT id_noclegu, DATEADD(day, 1, DataRez), data_wymeldowania
            FROM DatyRezerwacji
            WHERE DATEADD(day, 1, DataRez) < data_wymeldowania
        )
        MERGE kalendarz_dostepnosci AS target
        USING DatyRezerwacji AS source
        ON (target.id_noclegu = source.id_noclegu AND target.data = source.DataRez)
        WHEN MATCHED THEN
            UPDATE SET czy_dostepny = 0
        WHEN NOT MATCHED THEN
            INSERT (id_noclegu, data, czy_dostepny)
            VALUES (source.id_noclegu, source.DataRez, 0);
    END
END
"""

trigger_opinie = """
CREATE OR ALTER TRIGGER TR_Opinie_PrzeliczAgregaty
ON opinie
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @NoclegiDoAktualizacji TABLE (id_noclegu INT);

    INSERT INTO @NoclegiDoAktualizacji
    SELECT id_noclegu FROM inserted
    UNION
    SELECT id_noclegu FROM deleted;

    UPDATE n
    SET 
        n.srednia_ocena = ISNULL(o.Srednia, 0.00),
        n.liczba_opinii = ISNULL(o.Ilosc, 0)
    FROM noclegi n
    LEFT JOIN (
        SELECT id_noclegu, AVG(CAST(ocena AS DECIMAL(3,2))) as Srednia, COUNT(id_opinii) as Ilosc
        FROM opinie
        GROUP BY id_noclegu
    ) o ON n.id_noclegu = o.id_noclegu
    WHERE n.id_noclegu IN (SELECT id_noclegu FROM @NoclegiDoAktualizacji);
END
"""

trigger_historia = """
CREATE OR ALTER TRIGGER TR_Opinie_HistoriaEdycji
ON opinie
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    IF UPDATE(ocena) OR UPDATE(komentarz)
    BEGIN
        INSERT INTO historia_opinii (id_opinii, stara_ocena, stary_komentarz)
        SELECT d.id_opinii, d.ocena, d.komentarz
        FROM deleted d
        JOIN inserted i ON d.id_opinii = i.id_opinii;

        UPDATE o
        SET o.czy_edytowana = 1, o.data_modyfikacji = GETDATE()
        FROM opinie o
        JOIN inserted i ON o.id_opinii = i.id_opinii;
    END
END
"""

with conn.session as session:
    try:
        # Wykonujemy każdy trigger w osobnym wywołaniu sesji, eliminując konflikty składniowe
        session.execute(text(trigger_rezerwacje.strip()))
        session.execute(text(trigger_opinie.strip()))
        session.execute(text(trigger_historia.strip()))
        
        session.commit()
        st.success("Sukces! Wszystkie triggery zostały pomyślnie utworzone bezpośrednio w Azure SQL!")
        st.balloons()
    except Exception as e:
        session.rollback()
        st.error(f"Blad podczas tworzenia triggerów: {e}")


# st.divider()

# # KAFELKI - PROSTY DESIGN (3 kafelki obok siebie)

# col1, col2, col3 = st.columns(3, gap="medium")

# with col1:
#     with st.container(border=True):
#         st.markdown("### Moje podróże") # Nagłówek wewnątrz kafelka
        
#         if st.button("📅 Podróże i rezerwacje >", key="btn_rez"):
#             st.session_state.show_section = "rezerwacje"
#             st.rerun()
        
#         if st.button("❤️ Zapisane listy >", key="btn_ulub"):
#             st.session_state.show_section = "ulubione"
#             st.rerun()
            
#         if st.button("💬 Moje opinie >", key="btn_op"):
#             st.session_state.show_section = "opinie"
#             st.rerun()

# # KAFELEK 2: ZARZĄDZAJ KONTEM
# with col2:
#     with st.container(border=True):
#         st.markdown("**Zarządzaj kontem**")
                
#         if st.button("👤 Dane osobowe >", key="btn_prof", use_container_width=True):
#             st.session_state.show_section = "profil"


# # KAFELEK 3: ZARZĄDZAJ OBIEKTEM
# with col3:
#     with st.container(border=True):
#         st.markdown("**Zarządzaj obiektem**")
    
#         if st.button("🏠 Zarejestruj swój obiekt >", key="btn_obj", use_container_width=True):
#             st.session_state.show_section = "obiekt"

# st.divider()

# # ============================================================================
# # SEKCJE SZCZEGÓŁOWE
# # ============================================================================

# # SEKCJA: PROFIL
# if st.session_state.get("show_section") == "profil":
#     st.markdown("---")
#     st.subheader("👤 Edycja danych osobowych")
    
#     try:
#         user_profile = get_user_profile(conn, user_id)
        
#         if user_profile is not None:
#             st.write("**Aktualne dane:**")
            
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 st.write(f"Email: **{user_profile['email']}** (nie można zmienić)")
            
#             st.divider()
#             st.write("**Zmień dane:**")
            
#             imie = st.text_input("Imię:", value=str(user_profile['imie'].item() if hasattr(user_profile['imie'], 'item') else user_profile['imie']))
#             nazwisko = st.text_input("Nazwisko:", value=str(user_profile['nazwisko'].item() if hasattr(user_profile['nazwisko'], 'item') else user_profile['nazwisko']))
            
#             telefon_val = user_profile['telefon']
#             current_phone = str(telefon_val.item() if hasattr(telefon_val, 'item') else telefon_val) if telefon_val else ""
#             telefon = st.text_input("Telefon:", value=current_phone)
            
#             col_save, col_cancel = st.columns(2)
            
#             with col_save:
#                 if st.button("💾 Zapisz zmiany", key="save_profile_btn"):
#                     success, message = update_user_info(conn, user_id, imie, nazwisko, telefon)
#                     if success:
#                         st.success(message)
#                         st.session_state.show_section = None
#                         st.rerun()
#                     else:
#                         st.error(message)
            
#             with col_cancel:
#                 if st.button("❌ Anuluj", key="cancel_profile_btn"):
#                     st.session_state.show_section = None
#                     st.rerun()
#         else:
#             st.error("Nie udało się pobrać danych profilu")
    
#     except Exception as e:
#         st.error(f"❌ Błąd: {str(e)}")


# # SEKCJA: REZERWACJE
# elif st.session_state.get("show_section") == "rezerwacje":
#     st.markdown("---")
#     st.subheader("📅 Historia moich rezerwacji")
    
#     try:
#         reservations = get_user_reservations(conn, user_id)
        
#         if not reservations.empty:
#             display_cols = ["nazwa_noclegu", "lokalizacja_miasto", "data_zameldowania", 
#                           "data_wymeldowania", "liczba_gosci", "calkowita_cena", "status"]
            
#             reservations_display = reservations[display_cols].copy()
#             reservations_display["data_zameldowania"] = pd.to_datetime(
#                 reservations_display["data_zameldowania"]
#             ).dt.strftime("%d.%m.%Y")
#             reservations_display["data_wymeldowania"] = pd.to_datetime(
#                 reservations_display["data_wymeldowania"]
#             ).dt.strftime("%d.%m.%Y")
#             reservations_display["calkowita_cena"] = reservations_display["calkowita_cena"].apply(
#                 lambda x: f"{x:.2f} PLN"
#             )
            
#             reservations_display.columns = [
#                 "🏨 Noclég", "📍 Miasto", "📥 Zamelowanie", 
#                 "📤 Wymelowanie", "👥 Gości", "💰 Cena", "📊 Status"
#             ]
            
#             st.dataframe(reservations_display, use_container_width=True)
#         else:
#             st.info("📭 Nie masz żadnych rezerwacji")
    
#     except Exception as e:
#         st.error(f"❌ Błąd: {str(e)}")
    
#     if st.button("Wróć do menu", key="back_rezerwacje"):
#         st.session_state.show_section = None
#         st.rerun()


# # SEKCJA: OPINIE
# elif st.session_state.get("show_section") == "opinie":
#     st.markdown("---")
#     st.subheader("⭐ Moje recenzje noclegów")
    
#     try:
#         opinions = get_user_opinions(conn, user_id)
        
#         if not opinions.empty:
#             st.info("⚠️ **Możesz edytować swoje opinie do 1 roku po ich wystawieniu** (lub je usunąć)")
            
#             for idx, opinion in opinions.iterrows():
#                 with st.container(border=True):
#                     col1, col2, col3 = st.columns([2, 1, 1])
                    
#                     nazwa_noclegu = str(opinion['nazwa_noclegu'].item() if hasattr(opinion['nazwa_noclegu'], 'item') else opinion['nazwa_noclegu'])
#                     lokalizacja = str(opinion['lokalizacja_miasto'].item() if hasattr(opinion['lokalizacja_miasto'], 'item') else opinion['lokalizacja_miasto'])
#                     data_zam = str(opinion['data_zameldowania'].item() if hasattr(opinion['data_zameldowania'], 'item') else opinion['data_zameldowania'])
#                     data_wym = str(opinion['data_wymeldowania'].item() if hasattr(opinion['data_wymeldowania'], 'item') else opinion['data_wymeldowania'])
#                     komentarz = str(opinion['komentarz'].item() if hasattr(opinion['komentarz'], 'item') else opinion['komentarz'])
#                     data_dod = str(opinion['data_dodania'].item() if hasattr(opinion['data_dodania'], 'item') else opinion['data_dodania'])
#                     data_mod = str(opinion['data_modyfikacji'].item() if hasattr(opinion['data_modyfikacji'], 'item') else opinion['data_modyfikacji']) if opinion['data_modyfikacji'] else None
#                     id_opinii = int(opinion['id_opinii'].item() if hasattr(opinion['id_opinii'], 'item') else opinion['id_opinii'])
                    
#                     with col1:
#                         st.write(f"**🏨 {nazwa_noclegu}** • {lokalizacja}")
#                         st.write(f"_Pobyt: {pd.to_datetime(data_zam).strftime('%d.%m.%Y')} - {pd.to_datetime(data_wym).strftime('%d.%m.%Y')}_")
                    
#                     with col2:
#                         ocena_val = int(opinion['ocena'].item() if hasattr(opinion['ocena'], 'item') else opinion['ocena'])
#                         ocena_str = "⭐" * ocena_val + "☆" * (5 - ocena_val)
#                         st.write(f"**Ocena:** {ocena_str}")
                    
#                     with col3:
#                         czy_edytowana_val = bool(opinion['czy_edytowana'].item() if hasattr(opinion['czy_edytowana'], 'item') else opinion['czy_edytowana'])
#                         if czy_edytowana_val:
#                             st.caption("✏️ Edytowana")
                    
#                     st.write(f"**Opinią:** {komentarz}")
#                     st.caption(f"Wystawiona: {pd.to_datetime(data_dod).strftime('%d.%m.%Y o %H:%M')}")
                    
#                     if data_mod:
#                         st.caption(f"Ostatnia edycja: {pd.to_datetime(data_mod).strftime('%d.%m.%Y o %H:%M')}")
                    
#                     can_edit, dni_pozostale = can_edit_opinion(conn, id_opinii)
                    
#                     col_edit, col_del = st.columns(2)
                    
#                     with col_edit:
#                         if can_edit:
#                             if st.button(f"✏️ Edytuj", key=f"edit_{id_opinii}"):
#                                 st.session_state[f"editing_{id_opinii}"] = True
#                         else:
#                             st.button("❌ Nie można edytować (limit 1 roku)", disabled=True)
                    
#                     with col_del:
#                         if st.button(f"🗑️ Usuń", key=f"delete_{id_opinii}"):
#                             success, message = delete_opinion(conn, id_opinii)
#                             if success:
#                                 st.success(message)
#                                 st.rerun()
#                             else:
#                                 st.error(message)
                    
#                     if st.session_state.get(f"editing_{id_opinii}"):
#                         st.divider()
#                         st.write("**Edytuj opinię:**")
                        
#                         new_rating = st.slider(
#                             "Ocena (1-5):",
#                             min_value=1,
#                             max_value=5,
#                             value=int(opinion['ocena'].item() if hasattr(opinion['ocena'], 'item') else opinion['ocena']),
#                             key=f"rating_{id_opinii}"
#                         )
                        
#                         new_comment = st.text_area(
#                             "Komentarz:",
#                             value=komentarz,
#                             height=100,
#                             key=f"comment_{id_opinii}"
#                         )
                        
#                         col_save, col_cancel = st.columns(2)
                        
#                         with col_save:
#                             if st.button("💾 Zapisz zmiany", key=f"save_{id_opinii}"):
#                                 success, message = update_opinion(conn, id_opinii, new_rating, new_comment)
#                                 if success:
#                                     st.success(message)
#                                     st.session_state[f"editing_{id_opinii}"] = False
#                                     st.rerun()
#                                 else:
#                                     st.error(message)
                        
#                         with col_cancel:
#                             if st.button("❌ Anuluj", key=f"cancel_{id_opinii}"):
#                                 st.session_state[f"editing_{id_opinii}"] = False
#                                 st.rerun()
#         else:
#             st.info("📭 Nie wystawiłeś jeszcze żadnych opinii. Zarezerwuj noclég i napisz opinię!")
    
#     except Exception as e:
#         st.error(f"❌ Błąd: {str(e)}")
    
#     if st.button("Wróć do menu", key="back_opinie"):
#         st.session_state.show_section = None
#         st.rerun()


# # SEKCJA: ULUBIONE (placeholder)
# elif st.session_state.get("show_section") == "ulubione":
#     st.markdown("---")
#     st.subheader("❤️ Moje ulubione noclegi")
#     st.info("Funkcjonalność ulubionych noclegów - wkrótce!")
    
#     if st.button("Wróć do menu", key="back_ulubione"):
#         st.session_state.show_section = None
#         st.rerun()


# # SEKCJA: OBIEKT (placeholder)
# elif st.session_state.get("show_section") == "obiekt":
#     st.markdown("---")
#     st.subheader("🏨 Zarejestruj swój obiekt")
#     st.info("Panel rejestracji obiektu - wkrótce!")
    
#     if st.button("Wróć do menu", key="back_obiekt"):
#         st.session_state.show_section = None
#         st.rerun()

# # Przycisk wylogowania (zawsze widoczny)
# st.divider()
# st.subheader("🔒 Bezpieczeństwo")