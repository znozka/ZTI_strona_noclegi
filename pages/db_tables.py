import streamlit as st
from src.ui import render_page_header, render_page_footer
from src.utils import wyswietl_zdjecie

st.set_page_config(
    page_title="Baza danych",
    page_icon="assets/images/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_page_header()

st.title("Tabele w bazie danych")

try:
    conn = st.connection("azure_sql", type="sql")
except Exception as e:
    st.error(f"Nie udało się nawiązać połączenia z bazą danych Azure SQL. Błąd: {e}")
    st.stop()

st.subheader("noclegi")
query_noclegi = """SELECT * FROM noclegi"""

try:
    df_noclegi = conn.query(query_noclegi, ttl=600)
    
    if df_noclegi.empty:
        st.info("Tabela 'noclegi' jest pusta.")
    else:
        st.dataframe(
            df_noclegi, 
            width='stretch', 
            hide_index=True
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'noclegi'. Błąd: {e}")

st.markdown("---")

st.subheader("zdjecia_noclegu (ostatnie 100)")
query_zdjecia = """SELECT * FROM zdjecia_noclegu"""

try:
    df_zdjecia = conn.query(query_zdjecia, ttl=0) # ttl=0 aby zawsze widzieć świeże dane
    
    if df_zdjecia.empty:
        st.info("Tabela 'zdjecia_noclegu' jest pusta.")
    else:
        df_display = df_zdjecia.tail(100).copy()
        
        with st.spinner("Generuję miniatury"):
            df_display["url_zdjecia"] = df_display["url_zdjecia"].apply(wyswietl_zdjecie)
        
        st.dataframe(
            df_display,
            width='stretch',
            hide_index=True,
            column_config={
                "id_zdjecia": "id_zdjecia",
                "id_noclegu": "id_noclegu",
                "url_zdjecia": st.column_config.ImageColumn("podgląd"),
                "czy_glowne": "czy_glowne"
            }
        )
            
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'zdjecia_noclegu'. Błąd: {e}")

st.markdown("---")

st.subheader("uzytkownicy")
query_users = """SELECT * FROM uzytkownicy"""

try:
    df_users = conn.query(query_users, ttl=600)

    if df_users.empty:
        st.info("Tabela 'uzytkownicy' jest pusta.")
    else:
        st.dataframe(
            df_users,
            width='stretch',
            hide_index=True
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'uzytkownicy'. Błąd: {e}")

st.markdown("---")

st.subheader("historia_opinii")
query_historia = """SELECT * FROM historia_opinii"""

try:
    df_historia = conn.query(query_historia, ttl=600)

    if df_historia.empty:
        st.info("Tabela 'historia_opinii' jest pusta.")
    else:
        st.dataframe(
            df_historia,
            width='stretch',
            hide_index=True
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'historia_opinii'. Błąd: {e}")

st.markdown("---")

st.subheader("historia_wyszukiwan")
query_historia_wyszukiwan = """SELECT * FROM historia_wyszukiwan"""

try:
    df_historia_wyszukiwan = conn.query(query_historia_wyszukiwan, ttl=600)

    if df_historia_wyszukiwan.empty:
        st.info("Tabela 'historia_wyszukiwan' jest pusta.")
    else:
        st.dataframe(
            df_historia_wyszukiwan,
            width='stretch',
            hide_index=True
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'historia_wyszukiwan'. Błąd: {e}")

st.markdown("---")

st.subheader("kalendarz_dostepnosci")
query_kalendarz = """SELECT * FROM kalendarz_dostepnosci"""

try:
    df_kalendarz = conn.query(query_kalendarz, ttl=600)

    if df_kalendarz.empty:
        st.info("Tabela 'kalendarz_dostepnosci' jest pusta.")
    else:
        st.dataframe(
            df_kalendarz,
            width='stretch',
            hide_index=True
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'kalendarz_dostepnosci'. Błąd: {e}")

st.markdown("---")

st.subheader("noclegi_udogodnienia")
query_noclegi_udogodnienia = """SELECT * FROM noclegi_udogodnienia"""

try:
    df_noclegi_udogodnienia = conn.query(query_noclegi_udogodnienia, ttl=600)

    if df_noclegi_udogodnienia.empty:
        st.info("Tabela 'noclegi_udogodnienia' jest pusta.")
    else:
        st.dataframe(
            df_noclegi_udogodnienia,
            width='stretch',
            hide_index=True
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'noclegi_udogodnienia'. Błąd: {e}")

st.markdown("---")

st.subheader("opinie")
query_opinie = """SELECT * FROM opinie"""

try:
    df_opinie = conn.query(query_opinie, ttl=600)

    if df_opinie.empty:
        st.info("Tabela 'opinie' jest pusta.")
    else:
        st.dataframe(
            df_opinie,
            width='stretch',
            hide_index=True
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'opinie'. Błąd: {e}")

st.markdown("---")

st.subheader("platnosci")
query_platnosci = """SELECT * FROM platnosci"""

try:
    df_platnosci = conn.query(query_platnosci, ttl=600)

    if df_platnosci.empty:
        st.info("Tabela 'platnosci' jest pusta.")
    else:
        st.dataframe(
            df_platnosci,
            width='stretch',
            hide_index=True
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'platnosci'. Błąd: {e}")

st.markdown("---")

st.subheader("powiadomienia")
query_powiadomienia = """SELECT * FROM powiadomienia"""

try:
    df_powiadomienia = conn.query(query_powiadomienia, ttl=600)

    if df_powiadomienia.empty:
        st.info("Tabela 'powiadomienia' jest pusta.")
    else:
        st.dataframe(
            df_powiadomienia,
            width='stretch',
            hide_index=True
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'powiadomienia'. Błąd: {e}")

st.markdown("---")

st.subheader("rezerwacje")
query_rezerwacje = """SELECT * FROM rezerwacje"""

try:
    df_rezerwacje = conn.query(query_rezerwacje, ttl=600)

    if df_rezerwacje.empty:
        st.info("Tabela 'rezerwacje' jest pusta.")
    else:
        st.dataframe(
            df_rezerwacje,
            width='stretch',
            hide_index=True
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'rezerwacje'. Błąd: {e}")

st.markdown("---")

st.subheader("udogodnienia")
query_udogodnienia = """SELECT * FROM udogodnienia"""

try:
    df_udogodnienia = conn.query(query_udogodnienia, ttl=600)

    if df_udogodnienia.empty:
        st.info("Tabela 'udogodnienia' jest pusta.")
    else:
        st.dataframe(
            df_udogodnienia,
            width='stretch',
            hide_index=True
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'udogodnienia'. Błąd: {e}")

st.markdown("---")

st.subheader("ulubione_noclegi")
query_ulubione_noclegi = """SELECT * FROM ulubione_noclegi"""

try:
    df_ulubione_noclegi = conn.query(query_ulubione_noclegi, ttl=600)

    if df_ulubione_noclegi.empty:
        st.info("Tabela 'ulubione_noclegi' jest pusta.")
    else:
        st.dataframe(
            df_ulubione_noclegi,
            width='stretch',
            hide_index=True
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'ulubione_noclegi'. Błąd: {e}")

st.markdown("---")

render_page_footer()
