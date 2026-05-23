import streamlit as st

from src.ui import render_page_header

st.set_page_config(
    page_title="InnSight",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_page_header()

st.header("Tymczasowe przyciski")

nav_cols = st.columns([1, 1, 1, 4])
if nav_cols[0].button("Wyniki wyszukiwania"):
    st.switch_page("pages/wyniki_wyszukiwania.py")
if nav_cols[1].button("Strona noclegu"):
    st.switch_page("pages/strona_noclegu.py")
if nav_cols[2].button("Testy API pogodowego"):
    st.switch_page("pages/testy_api.py")

conn = st.connection("azure_sql", type="sql")

st.title("Próbna tabelka z Azure")

st.subheader("Dane z bazy")

# TABELA NOCLEGÓW

st.subheader("Lista noclegów w bazie danych")

query_noclegi = """
SELECT 
    id_noclegu, 
    nazwa, 
    typ_obiektu, 
    lokalizacja_miasto, 
    lokalizacja_adres, 
    cena_za_noc, 
    maks_liczba_osob,
    srednia_ocena,
    liczba_opinii
FROM noclegi
ORDER BY data_dodania DESC
"""

try:
    df_noclegi = conn.query(query_noclegi, ttl=600)
    
    if df_noclegi.empty:
        st.info("Tabela 'noclegi' jest pusta.")
    else:
        st.dataframe(
            df_noclegi, 
            width='stretch', 
            hide_index=True,
            column_config={
                "id_noclegu": "ID Noclegu",
                "nazwa": "Nazwa obiektu",
                "typ_obiektu": "Typ",
                "lokalizacja_miasto": "Miasto",
                "lokalizacja_adres": "Adres",
                "cena_za_noc": st.column_config.NumberColumn("Cena za noc", format="%.2f PLN"),
                "maks_liczba_osob": "Maks. osób",
                "srednia_ocena": "Ocena",
                "liczba_opinii": "Liczba opinii"
            }
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'noclegi'. Błąd: {e}")

st.markdown("---")

st.subheader("Galeria zdjęć przypisanych do obiektów")

query_zdjecia = """
SELECT 
    z.id_zdjecia,
    z.id_noclegu,
    n.nazwa AS nazwa_noclegu,
    z.url_zdjecia,
    z.czy_glowne
FROM zdjecia_noclegu z
INNER JOIN noclegi n ON z.id_noclegu = n.id_noclegu
"""

try:
    df_zdjecia = conn.query(query_zdjecia, ttl=600)
    
    if df_zdjecia.empty:
        st.info("Tabela 'zdjecia_noclegu' jest pusta. Dodaj linki URL do zdjęć w bazie, aby je zobaczyć.")
    else:
        st.dataframe(
            df_zdjecia,
            width='stretch',
            hide_index=True,
            column_config={
                "id_zdjecia": "ID Zdjęcia",
                "id_noclegu": "ID Noclegu",
                "nazwa_noclegu": "Obiekt noclegowy",
                "url_zdjecia": st.column_config.ImageColumn("Podgląd zdjęcia"),
                "czy_glowne": "Czy główne (0/1)"
            }
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'zdjecia_noclegu'. Błąd: {e}")