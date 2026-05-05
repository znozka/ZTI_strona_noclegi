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

# Zawartość strony głównej
conn = st.connection("azure_sql", type="sql")

st.title("Próbna tabelka z Azure")

# odczyt danych
st.subheader("Dane z bazy")
query = "SELECT * FROM SalesLT.Address"
df = conn.query(query, ttl=600)
st.dataframe(df)
