import streamlit as st

from src.ui import render_page_header

st.set_page_config(
    page_title="Wyniki wyszukiwania",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header()
# # from src.ui import render_page_header, render_page_footer

# # st.set_page_config(
# #     page_title="Wyniki wyszukiwania - InnSight",
# #     layout="wide",
# #     initial_sidebar_state="collapsed"
# # )

# # render_page_header()

# # conn = st.connection("azure_sql", type="sql")

# # st.markdown("## Znajdź idealny nocleg")

# # # =========================
# # # FILTRY WYSZUKIWANIA
# # # =========================

# # # filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 1, 1, 1])
# # filter_col1, filter_col2, filter_col3, filter_col4, filter_col5, filter_col6 = st.columns([2,1,1,1,1,1])

# # with filter_col1:
# #     miasto = st.text_input(
# #         "Dokąd jedziesz?",
# #         placeholder="np. Kraków"
# #     )

# # with filter_col2:
# #     liczba_osob = st.number_input(
# #         "Liczba gości",
# #         min_value=1,
# #         max_value=20,
# #         value=2
# #     )
# # with filter_col3:
# #     data_od = st.date_input(
# #         "Data od"
# #     )

# # with filter_col4:
# #     data_do = st.date_input(
# #         "Data do"
# #     )

# # with filter_col5:
# #     cena_min = st.number_input(
# #         "Cena od",
# #         min_value=0,
# #         value=100,
# #         step=50
# #     )

# # with filter_col6:
# #     cena_max = st.number_input(
# #         "Cena do",
# #         min_value=0,
# #         value=1000,
# #         step=50
# #     )

# # st.markdown("<br>", unsafe_allow_html=True)


# # search_col1, search_col2, search_col3 = st.columns([5, 1, 5])

# # with search_col2:
# #     search_button = st.button(
# #         "Szukaj",
# #         width="stretch"
# #     )
# # # =========================
# # # ZAPYTANIE SQL
# # # =========================
# # query = """
# # SELECT DISTINCT TOP 30
# #     n.id_noclegu,
# #     n.nazwa,
# #     n.typ_obiektu,
# #     n.lokalizacja_miasto,
# #     n.lokalizacja_adres,
# #     n.cena_za_noc,
# #     n.maks_liczba_osob,
# #     n.srednia_ocena,
# #     n.liczba_opinii,
# #     z.url_zdjecia
# # FROM noclegi n

# # LEFT JOIN zdjecia_noclegu z
# #     ON n.id_noclegu = z.id_noclegu
# #     AND z.czy_glowne = 1

# # WHERE
# #     (:miasto = '' OR n.lokalizacja_miasto LIKE :miasto_like)

# #     AND n.maks_liczba_osob >= :liczba_osob

# #     AND n.cena_za_noc BETWEEN :cena_min AND :cena_max

# #     AND NOT EXISTS (
# #         SELECT 1
# #         FROM kalendarz_dostepnosci k
# #         WHERE k.id_noclegu = n.id_noclegu
# #         AND k.data >= :data_od
# #         AND k.data < :data_do
# #         AND k.czy_dostepny = 0
# #     )

# # ORDER BY
# #     n.srednia_ocena DESC,
# #     n.liczba_opinii DESC
# # """

# # params = {
# #     "miasto": miasto,
# #     "miasto_like": f"%{miasto}%",
# #     "liczba_osob": liczba_osob,
# #     "cena_min": cena_min,
# #     "cena_max": cena_max,
# #     "data_od": data_od,
# #     "data_do": data_do
# # }
# # if search_button:

# #     try:
# #         df = conn.query(query, params=params, ttl=0)

# #         st.markdown(f"### Znaleziono {len(df)} obiektów")

# #         if df.empty:
# #             st.warning("Nie znaleziono noclegów dla podanych filtrów.")

# #         else:
# #             for _, row in df.iterrows():

# #                 with st.container(border=True):
# #                     col_img, col_info, col_price = st.columns([1.2, 2, 1])

# #                     with col_img:
# #                         if row["url_zdjecia"]:
# #                             st.image(row["url_zdjecia"], width="stretch")
# #                         else:
# #                             st.image(
# #                                 "https://placehold.co/600x400?text=Brak+zdjecia",
# #                                 width="stretch"
# #                             )

# #                     with col_info:
# #                         st.markdown(f"## {row['nazwa']}")

# #                         st.markdown(
# #                             f"📍 {row['lokalizacja_miasto']} • {row['lokalizacja_adres']}"
# #                         )

# #                         st.markdown(
# #                             f"🏨 {row['typ_obiektu']} • 👥 Maks. {row['maks_liczba_osob']} osób"
# #                         )

# #                         st.markdown(
# #                             f"⭐ {row['srednia_ocena']} ({row['liczba_opinii']} opinii)"
# #                         )

# #                     with col_price:
# #                         st.markdown(
# #                             f'''
# #                             <div style=\"text-align:right;\">
# #                                 <h2>{row['cena_za_noc']:.0f} PLN</h2>
# #                                 <p>za noc</p>
# #                             </div>
# #                             ''',
# #                             unsafe_allow_html=True
# #                         )

# #                         if st.button(
# #                             "Zobacz ofertę",
# #                             key=f"offer_{row['id_noclegu']}",
# #                             width="stretch"
# #                         ):
# #                             st.session_state.selected_hotel_id = row["id_noclegu"]
# #                             st.switch_page("pages/strona_noclegu.py")

# #     except Exception as e:
# #         st.error(f"Wystąpił błąd podczas pobierania danych: {e}")

# # render_page_footer()
# import streamlit as st
# from sqlalchemy import text
# from src.ui import render_page_header, render_page_footer

# st.set_page_config(
#     page_title="Wyniki wyszukiwania - InnSight",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# render_page_header()

# conn = st.connection("azure_sql", type="sql")

# st.markdown("## Znajdź idealny nocleg")

# # =========================
# # FILTRY WYSZUKIWANIA
# # =========================
# filter_col1, filter_col2, filter_col3, filter_col4, filter_col5, filter_col6 = st.columns([2, 1, 1, 1, 1, 1])

# with filter_col1:
#     miasto = st.text_input(
#         "Dokąd jedziesz?",
#         placeholder="np. Kraków"
#     )

# with filter_col2:
#     liczba_osob = st.number_input(
#         "Liczba gości",
#         min_value=1,
#         max_value=20,
#         value=2
#     )

# with filter_col3:
#     data_od = st.date_input(
#         "Data od"
#     )

# with filter_col4:
#     data_do = st.date_input(
#         "Data do"
#     )

# with filter_col5:
#     cena_min = st.number_input(
#         "Cena od",
#         min_value=0,
#         value=100,
#         step=50
#     )

# with filter_col6:
#     cena_max = st.number_input(
#         "Cena do",
#         min_value=0,
#         value=1000,
#         step=50
#     )

# st.markdown("<br>", unsafe_allow_html=True)

# search_col1, search_col2, search_col3 = st.columns([5, 2, 5])
# with search_col2:
#     search_button = st.button(
#         "Szukaj",
#         width='content'
#     )

# # =========================
# # ZAPYTANIE SQL
# # =========================
# query = ("""
# SELECT DISTINCT TOP 30
#     n.id_noclegu,
#     n.nazwa,
#     n.typ_obiektu,
#     n.lokalizacja_miasto,
#     n.lokalizacja_adres,
#     n.cena_za_noc,
#     n.maks_liczba_osob,
#     n.srednia_ocena,
#     n.liczba_opinii,
#     z.url_zdjecia
# FROM noclegi n
# LEFT JOIN zdjecia_noclegu z
#     ON n.id_noclegu = z.id_noclegu
#     AND z.czy_glowne = 1
# WHERE
#     (:miasto = '' OR n.lokalizacja_miasto LIKE :miasto_like)
#     AND n.maks_liczba_osob >= :liczba_osob
#     AND n.cena_za_noc BETWEEN :cena_min AND :cena_max
#     AND NOT EXISTS (
#         SELECT 1
#         FROM kalendarz_dostepnosci k
#         WHERE k.id_noclegu = n.id_noclegu
#         AND k.data >= :data_od
#         AND k.data < :data_do
#         AND k.czy_dostepny = 0
#     )
# ORDER BY
#     n.srednia_ocena DESC,
#     n.liczba_opinii DESC
# """)

# params = {
#     "miasto": miasto,
#     "miasto_like": f"%{miasto}%",
#     "liczba_osob": liczba_osob,
#     "cena_min": cena_min,
#     "cena_max": cena_max,
#     "data_od": data_od,
#     "data_do": data_do
# }

# # Wykonaj zapytanie zawsze (aby wyniki nie znikały), przycisk wymusi odświeżenie formularza
# try:
#     df = conn.query(query, params=params, ttl=0)

#     st.markdown(f"### Znaleziono {len(df)} obiektów")

#     if df.empty:
#         st.warning("Nie znaleziono noclegów dla podanych filtrów.")
#     else:
#         for _, row in df.iterrows():
#             with st.container(border=True):
#                 col_img, col_info, col_price = st.columns([1.5, 2.5, 1])

#                 with col_img:
#                     if row["url_zdjecia"]:
#                         st.image(row["url_zdjecia"], width='content')
#                     else:
#                         st.image(
#                             "https://placehold.co/600x400?text=Brak+zdjecia",
#                             width='content'
#                         )

#                 with col_info:
#                     st.markdown(f"### {row['nazwa']}")
#                     st.markdown(f"{row['lokalizacja_miasto']} • {row['lokalizacja_adres']}")
#                     st.markdown(f"{row['typ_obiektu']} • 👥 Maks. {row['maks_liczba_osob']} osób")
#                     st.markdown(f"{row['srednia_ocena']} ({row['liczba_opinii']} opinii)")

#                 with col_price:
#                     st.markdown(
#                         f'''
#                         <div style="text-align: right; margin-bottom: 10px;">
#                             <h2 style="margin: 0;">{row['cena_za_noc']:.0f} PLN</h2>
#                             <p style="margin: 0; color: gray;">za noc</p>
#                         </div>
#                         ''',
#                         unsafe_allow_html=True
#                     )

#                     if st.button(
#                         "Zobacz ofertę",
#                         key=f"offer_{row['id_noclegu']}",
#                         width='content'
#                     ):
#                         st.session_state.selected_hotel_id = row["id_noclegu"]
#                         st.switch_page("pages/strona_noclegu.py")

# except Exception as e:
#     st.error(f"Wystąpił błąd podczas pobierania danych: {e}")

# render_page_footer()