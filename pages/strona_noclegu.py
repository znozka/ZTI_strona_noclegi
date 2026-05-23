# # # import streamlit as st

# # # from src.ui import render_page_header

# # # st.set_page_config(
# # #     page_title="Strona noclegu",
# # #     layout="wide",
# # #     initial_sidebar_state="collapsed"
# # # )

# # # render_page_header()

# # # st.header("Strona noclegu")
# # import streamlit as st
# # from sqlalchemy import text

# # from src.ui import render_page_header, render_page_footer

# # st.set_page_config(
# #     page_title="Strona noclegu - InnSight",
# #     layout="wide",
# #     initial_sidebar_state="collapsed"
# # )

# # render_page_header()

# # conn = st.connection("azure_sql", type="sql")

# # id_noclegu = st.session_state.get("selected_hotel_id")

# # if not id_noclegu:
# #     st.warning("Nie wybrano żadnego noclegu.")
# #     st.stop()

# # # =========================
# # # DANE NOCLEGU
# # # =========================

# # query_nocleg = text("""
# # SELECT *
# # FROM noclegi
# # WHERE id_noclegu = :id_noclegu
# # """)

# # query_zdjecia = text("""
# # SELECT url_zdjecia
# # FROM zdjecia_noclegu
# # WHERE id_noclegu = :id_noclegu
# # ORDER BY czy_glowne DESC
# # """)

# # query_udogodnienia = text("""
# # SELECT u.nazwa
# # FROM noclegi_udogodnienia nu
# # INNER JOIN udogodnienia u
# #     ON nu.id_udogodnienia = u.id_udogodnienia
# # WHERE nu.id_noclegu = :id_noclegu
# # """)
# # query_opinie = text("""
# # SELECT TOP 5
# #     o.ocena,
# #     o.komentarz,
# #     o.data_dodania,
# #     u.imie,
# #     u.nazwisko
# # FROM opinie o
# # INNER JOIN uzytkownicy u
# #     ON o.id_turysty = u.id_uzytkownika
# # WHERE o.id_noclegu = :id_noclegu
# # ORDER BY o.data_dodania DESC
# # """)

# # try:
# #     hotel_df = conn.query(query_nocleg, params={"id_noclegu": id_noclegu}, ttl=0)

# #     if hotel_df.empty:
# #         st.error("Nie znaleziono noclegu.")
# #         st.stop()

# #     hotel = hotel_df.iloc[0]
# #     images_df = conn.query(query_zdjecia, params={"id_noclegu": id_noclegu}, ttl=0)
# #     amenities_df = conn.query(query_udogodnienia, params={"id_noclegu": id_noclegu}, ttl=0)
# #     reviews_df = conn.query(query_opinie, params={"id_noclegu": id_noclegu}, ttl=0)

# #     # =========================
# #     # NAGŁÓWEK
# #     # =========================

# #     st.markdown(f"# {hotel['nazwa']}")

# #     info_col1, info_col2 = st.columns([3, 1])

# #     with info_col1:
# #         st.markdown(
# #             f"📍 {hotel['lokalizacja_miasto']} • {hotel['lokalizacja_adres']}"
# #         )

# #         st.markdown(
# #             f"⭐ {hotel['srednia_ocena']} ({hotel['liczba_opinii']} opinii)"
# #         )

# #     with info_col2:
# #         st.metric("Cena za noc", f"{hotel['cena_za_noc']:.0f} PLN")

# #     st.markdown("---")


# #     # =========================
# #     # GALERIA
# #     # =========================

# #     st.subheader("Galeria zdjęć")

# #     if not images_df.empty:
# #         image_urls = images_df["url_zdjecia"].tolist()
# #         st.image(image_urls, use_container_width=True)
# #     else:
# #         st.info("Brak zdjęć dla tego obiektu.")

# #     st.markdown("---")

# #     # =========================
# #     # OPIS + REZERWACJA
# #     # =========================

# #     left_col, right_col = st.columns([2, 1])

# #     with left_col:
# #         st.subheader("Opis")

# #         if hotel["opis"]:
# #             st.write(hotel["opis"])
# #         else:
# #             st.write("Brak opisu obiektu.")

# #         st.subheader("Udogodnienia")

# #         if not amenities_df.empty:
# #             amenity_cols = st.columns(3)

# #             for idx, (_, amenity) in enumerate(amenities_df.iterrows()):
# #                 with amenity_cols[idx % 3]:
# #                     st.markdown(f"✅ {amenity['nazwa']}")
# #         else:
# #             st.info("Brak dodanych udogodnień.")

# #     with right_col:
# #         st.subheader("Zarezerwuj")

# #         data_od = st.date_input("Data zameldowania")
# #         data_do = st.date_input("Data wymeldowania")

# #         liczba_gosci = st.number_input(
# #             "Liczba gości",
# #             min_value=1,
# #             max_value=int(hotel["maks_liczba_osob"]),
# #             value=1
# #         )

# #         liczba_nocy = max((data_do - data_od).days, 1)
# #         cena_koncowa = liczba_nocy * float(hotel["cena_za_noc"])

# #         st.metric("Łączna cena", f"{cena_koncowa:.0f} PLN")

# #         if st.button("Zarezerwuj teraz", use_container_width=True):
# #             st.success("Rezerwacja testowa została utworzona.")

# #     st.markdown("---")

# #     # =========================
# #     # OPINIE
# #     # =========================

# #     st.subheader("Opinie gości")

# #     if reviews_df.empty:
# #         st.info("Ten obiekt nie ma jeszcze opinii.")
# #     else:
# #         for _, review in reviews_df.iterrows():
# #             with st.container(border=True):
# #                 st.markdown(
# #                     f"### ⭐ {review['ocena']} • {review['imie']} {review['nazwisko']}"
# #                 )

# #                 st.caption(str(review['data_dodania']))

# #                 st.write(review['komentarz'])

# # except Exception as e:
# #     st.error(f"Wystąpił błąd podczas ładowania strony: {e}")

# # render_page_footer()

# import streamlit as st
# from sqlalchemy import text
# import datetime
# from src.ui import render_page_header, render_page_footer

# st.set_page_config(
#     page_title="Strona noclegu - InnSight",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# render_page_header()

# conn = st.connection("azure_sql", type="sql")
# id_noclegu = st.session_state.get("selected_hotel_id")

# if not id_noclegu:
#     st.warning("Nie wybrano żadnego noclegu. Wróć do wyszukiwarki.")
#     if st.button("Powrót do wyszukiwania"):
#         st.switch_page("pages/wyniki_wyszukiwania.py")
#     st.stop()

# # =========================
# # PRZYGOTOWANIE ZAPYTAŃ SQL
# # =========================
# query_nocleg = ("SELECT * FROM noclegi WHERE id_noclegu = :id_noclegu")
# query_zdjecia = ("SELECT url_zdjecia FROM zdjecia_noclegu WHERE id_noclegu = :id_noclegu ORDER BY czy_glowne DESC")
# query_udogodnienia = ("""
#     SELECT u.nazwa FROM noclegi_udogodnienia nu
#     INNER JOIN udogodnienia u ON nu.id_udogodnienia = u.id_udogodnienia
#     WHERE nu.id_noclegu = :id_noclegu
# """)
# query_opinie = ("""
#     SELECT TOP 5 o.ocena, o.komentarz, o.data_dodania, u.imie, u.nazwisko
#     FROM opinie o
#     INNER JOIN uzytkownicy u ON o.id_turysty = u.id_uzytkownika
#     WHERE o.id_noclegu = :id_noclegu
#     ORDER BY o.data_dodania DESC
# """)

# try:
#     hotel_df = conn.query(query_nocleg, params={"id_noclegu": id_noclegu}, ttl=0)
    
#     if hotel_df.empty:
#         st.error("Nie znaleziono wybranego obiektu noclegowego.")
#         st.stop()

#     hotel = hotel_df.iloc[0]
#     images_df = conn.query(query_zdjecia, params={"id_noclegu": id_noclegu}, ttl=0)
#     amenities_df = conn.query(query_udogodnienia, params={"id_noclegu": id_noclegu}, ttl=0)
#     reviews_df = conn.query(query_opinie, params={"id_noclegu": id_noclegu}, ttl=0)

# except Exception as e:
#     st.error(f"Wystąpił błąd podczas ładowania danych z bazy: {e}")
#     st.stop()

# # =========================
# # NAGŁÓWEK STRONY
# # =========================
# st.markdown(f"# {hotel['nazwa']}")

# info_col1, info_col2 = st.columns([3, 1])
# with info_col1:
#     st.markdown(f"📍 {hotel['lokalizacja_miasto']} • {hotel['lokalizacja_adres']}")
#     st.markdown(f"⭐ {hotel['srednia_ocena']} ({hotel['liczba_opinii']} opinii)")

# with info_col2:
#     st.metric("Cena podstawowa", f"{hotel['cena_za_noc']:.0f} PLN / noc")

# st.markdown("---")

# # =========================
# # GALERIA ZDJĘĆ
# # =========================
# st.subheader("📸 Galeria zdjęć")
# if not images_df.empty:
#     image_urls = images_df["url_zdjecia"].tolist()
#     # Wyświetlamy zdjęcia w zgrabnej siatce (grid) zamiast jednego pod drugim
#     img_cols = st.columns(min(len(image_urls), 3))
#     for idx, url in enumerate(image_urls):
#         with img_cols[idx % 3]:
#             st.image(url, use_container_width=True)
# else:
#     st.info("Brak zdjęć dla tego obiektu.")

# st.markdown("---")

# # =========================
# # OPIS + SEKCOJA REZERWACJI
# # =========================
# left_col, right_col = st.columns([2, 1])

# with left_col:
#     st.subheader("📝 Opis obiektu")
#     if hotel["opis"]:
#         st.write(hotel["opis"])
#     else:
#         st.write("Brak opisu obiektu.")

#     st.markdown("<br>", unsafe_allow_html=True)
#     st.subheader("✨ Udogodnienia")
#     if not amenities_df.empty:
#         amenity_cols = st.columns(3)
#         for idx, (_, amenity) in enumerate(amenities_df.iterrows()):
#             with amenity_cols[idx % 3]:
#                 st.markdown(f"✅ {amenity['nazwa']}")
#     else:
#         st.info("Brak dodatkowych udogodnień dla tego obiektu.")

# with right_col:
#     with st.container(border=True):
#         st.subheader("📅 Zarezerwuj pobyt")
        
#         # Poprawne domyślne daty (zameldowanie dziś, wymeldowanie jutro)
#         today = datetime.date.today()
#         data_od = st.date_input("Data zameldowania", value=today, min_value=today)
#         data_do = st.date_input("Data wymeldowania", value=today + datetime.timedelta(days=1), min_value=today)

#         liczba_gosci = st.number_input(
#             "Liczba gości",
#             min_value=1,
#             max_value=int(hotel["maks_liczba_osob"]),
#             value=1
#         )

#         # Walidacja poprawności wybranych dat
#         if data_do <= data_od:
#             st.error("Błąd: Data wymeldowania musi nastąpić po dacie zameldowania.")
#             btn_disabled = True
#             cena_koncowa = 0
#         else:
#             liczba_nocy = (data_do - data_od).days
#             cena_koncowa = liczba_nocy * float(hotel["cena_za_noc"])
#             st.metric(f"Łączna cena ({liczba_nocy} noc/y)", f"{cena_koncowa:.0f} PLN")
#             btn_disabled = False

#         if st.button("Zarezerwuj teraz", use_container_width=True, disabled=btn_disabled):
#             st.success(f"Sukces! Rezerwacja na {liczba_nocy} nocy dla {liczba_gosci} os. została pomyślnie utworzona.")

# st.markdown("---")

# # =========================
# # OPINIE GOŚCI
# # =========================
# st.subheader("💬 Opinie gości")
# if reviews_df.empty:
#     st.info("Ten obiekt nie posiada jeszcze żadnych opinii.")
# else:
#     for _, review in reviews_df.iterrows():
#         with st.container(border=True):
#             st.markdown(f"**⭐ {review['ocena']}/5** • {review['imie']} {review['nazwisko']}")
#             st.caption(f"Dodano: {review['data_dodania']}")
#             st.write(review['komentarz'])

# render_page_footer()

import streamlit as st
from sqlalchemy import text
import datetime
from src.ui import render_page_header, render_page_footer

st.set_page_config(
    page_title="Strona noclegu - InnSight",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header()

conn = st.connection("azure_sql", type="sql")
id_noclegu = st.session_state.get("selected_hotel_id")

if not id_noclegu:
    st.warning("Nie wybrano żadnego noclegu. Wróć do wyszukiwarki.")
    if st.button("Powrót do wyszukiwania"):
        st.switch_page("pages/wyniki_wyszukiwania.py")
    st.stop()


query_nocleg = ("SELECT * FROM noclegi WHERE id_noclegu = :id_noclegu")
query_zdjecia = ("SELECT url_zdjecia FROM zdjecia_noclegu WHERE id_noclegu = :id_noclegu ORDER BY czy_glowne DESC")
query_udogodnienia = ("""
    SELECT u.nazwa FROM noclegi_udogodnienia nu
    INNER JOIN udogodnienia u ON nu.id_udogodnienia = u.id_udogodnienia
    WHERE nu.id_noclegu = :id_noclegu
""")
query_opinie = ("""
    SELECT TOP 5 o.ocena, o.komentarz, o.data_dodania, u.imie, u.nazwisko
    FROM opinie o
    INNER JOIN uzytkownicy u ON o.id_turysty = u.id_uzytkownika
    WHERE o.id_noclegu = :id_noclegu
    ORDER BY o.data_dodania DESC
""")

try:
    hotel_df = conn.query(query_nocleg, params={"id_noclegu": id_noclegu}, ttl=0)
    
    if hotel_df.empty:
        st.error("Nie znaleziono wybranego obiektu noclegowego.")
        st.stop()

    hotel = hotel_df.iloc[0]
    images_df = conn.query(query_zdjecia, params={"id_noclegu": id_noclegu}, ttl=0)
    amenities_df = conn.query(query_udogodnienia, params={"id_noclegu": id_noclegu}, ttl=0)
    reviews_df = conn.query(query_opinie, params={"id_noclegu": id_noclegu}, ttl=0)

except Exception as e:
    st.error(f"Wystąpił błąd podczas ładowania danych z bazy: {e}")
    st.stop()


st.markdown(f"# {hotel['nazwa']}")

info_col1, info_col2 = st.columns([3, 1])
with info_col1:
    st.markdown(f"📍 {hotel['lokalizacja_miasto']} • {hotel['lokalizacja_adres']}")
    st.markdown(f"⭐ {hotel['srednia_ocena']} ({hotel['liczba_opinii']} opinii)")

with info_col2:
    st.metric("Cena podstawowa", f"{hotel['cena_za_noc']:.0f} PLN / noc")

st.markdown("---")


st.subheader("📸 Galeria zdjęć")
if not images_df.empty:
    image_urls = images_df["url_zdjecia"].tolist()
    # Wyświetlamy zdjęcia w zgrabnej siatce (grid) zamiast jednego pod drugim
    img_cols = st.columns(min(len(image_urls), 3))
    for idx, url in enumerate(image_urls):
        with img_cols[idx % 3]:
            st.image(url, width='content')
else:
    st.info("Brak zdjęć dla tego obiektu.")

st.markdown("---")

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Opis obiektu")
    if hotel["opis"]:
        st.write(hotel["opis"])
    else:
        st.write("Brak opisu obiektu.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("✨ Udogodnienia")
    if not amenities_df.empty:
        amenity_cols = st.columns(3)
        for idx, (_, amenity) in enumerate(amenities_df.iterrows()):
            with amenity_cols[idx % 3]:
                st.markdown(f"{amenity['nazwa']}")
    else:
        st.info("Brak dodatkowych udogodnień dla tego obiektu.")

with right_col:
    with st.container(border=True):
        st.subheader("Zarezerwuj pobyt")
        
        # Poprawne domyślne daty (zameldowanie dziś, wymeldowanie jutro)
        today = datetime.date.today()
        data_od = st.date_input("Data zameldowania", value=today, min_value=today)
        data_do = st.date_input("Data wymeldowania", value=today + datetime.timedelta(days=1), min_value=today)

        liczba_gosci = st.number_input(
            "Liczba gości",
            min_value=1,
            max_value=int(hotel["maks_liczba_osob"]),
            value=1
        )

        # Walidacja poprawności wybranych dat
        if data_do <= data_od:
            st.error("Błąd: Data wymeldowania musi nastąpić po dacie zameldowania.")
            btn_disabled = True
            cena_koncowa = 0
        else:
            liczba_nocy = (data_do - data_od).days
            cena_koncowa = liczba_nocy * float(hotel["cena_za_noc"])
            st.metric(f"Łączna cena ({liczba_nocy} noc/y)", f"{cena_koncowa:.0f} PLN")
            btn_disabled = False

        if st.button("Zarezerwuj teraz", width='content', disabled=btn_disabled):
            st.success(f"Sukces! Rezerwacja na {liczba_nocy} nocy dla {liczba_gosci} os. została pomyślnie utworzona.")

st.markdown("---")

st.subheader("Opinie gości")
if reviews_df.empty:
    st.info("Ten obiekt nie posiada jeszcze żadnych opinii.")
else:
    for _, review in reviews_df.iterrows():
        with st.container(border=True):
            st.markdown(f"**{review['ocena']}/5** • {review['imie']} {review['nazwisko']}")
            st.caption(f"Dodano: {review['data_dodania']}")
            st.write(review['komentarz'])

render_page_footer()