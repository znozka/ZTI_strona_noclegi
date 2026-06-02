
import streamlit as st
from src.ui import render_page_header, render_page_footer
st.set_page_config(
    page_title="InnSight",
    page_icon="assets/images/icon.svg",
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

st.title("Panel Administratora - Przegląd bazy Azure SQL")
st.subheader("Dane z bazy")

# =========================================================================
# 1. TABELA: NOCLEGI
# =========================================================================
st.subheader("Lista noclegów w bazie danych")

query_noclegi = """
SELECT 
    id_noclegu, 
    nazwa,
    opis,
    typ_obiektu,
    lokalizacja_miasto,
    cena_za_noc,
    maks_liczba_osob,
    srednia_ocena,
    liczba_opinii
FROM noclegi
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
                "cena_za_noc": st.column_config.NumberColumn("Cena za noc", format="%.2f PLN"),
                "maks_liczba_osob": "Maks. osób",
                "srednia_ocena": "Ocena",
                "liczba_opinii": "Liczba opinii"
            }
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'noclegi'. Błąd: {e}")

st.markdown("---")

# =========================================================================
# 2. TABELA: ZDJĘCIA NOCLEGU
# =========================================================================
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

st.markdown("---")

# =========================================================================
# 3. TABELA: UŻYTKOWNICY
# =========================================================================
st.subheader("Lista użytkowników w bazie danych")

query_users = """
SELECT 
    id_uzytkownika,
    email,
    imie,
    nazwisko,
    telefon,
    rola,
    data_rejestracji
FROM uzytkownicy
"""

try:
    df_users = conn.query(query_users, ttl=600)

    if df_users.empty:
        st.info("Tabela 'uzytkownicy' jest pusta.")
    else:
        st.dataframe(
            df_users,
            width='stretch',
            hide_index=True,
            column_config={
                "id_uzytkownika": "ID",
                "email": "Email",
                "imie": "Imię",
                "nazwisko": "Nazwisko",
                "telefon": "Telefon",
                "rola": st.column_config.TextColumn("Rola"),
                "data_rejestracji": st.column_config.DatetimeColumn("Data rejestracji")
            }
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'uzytkownicy'. Błąd: {e}")

st.markdown("---")

# =========================================================================
# 3b. TABELA: WŁAŚCICIELE NOCLEGÓW (NOWA SEKCJA)
# =========================================================================
st.subheader("Lista właścicieli obiektów (Gospodarzy)")

query_wlasciciele = """
SELECT 
    id_uzytkownika AS id_wlasciciela,
    email,
    imie,
    nazwisko,
    telefon,
    data_rejestracji,
    (SELECT COUNT(*) FROM noclegi WHERE id_wlasciciela = u.id_uzytkownika) AS liczba_obiektow
FROM uzytkownicy u
WHERE rola = 'właściciel'
"""

try:
    df_wlasciciele = conn.query(query_wlasciciele, ttl=600)

    if df_wlasciciele.empty:
        st.info("Brak zarejestrowanych użytkowników z rolą 'właściciel'.")
    else:
        st.dataframe(
            df_wlasciciele,
            width='stretch',
            hide_index=True,
            column_config={
                "id_wlasciciela": "ID Właściciela",
                "email": "Email",
                "imie": "Imię",
                "nazwisko": "Nazwisko",
                "telefon": "Telefon",
                "data_rejestracji": st.column_config.DatetimeColumn("Data rejestracji"),
                "liczba_obiektow": st.column_config.NumberColumn("Posiadane obiekty", format="%d")
            }
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych o właścicielach. Błąd: {e}")

st.markdown("---")

# =========================================================================
# 4. TABELA: REZERWACJE
# =========================================================================
st.subheader("Lista rezerwacji (w tym wygenerowane automatycznie)")

query_rezerwacje = """
SELECT 
    r.id_rezerwacji,
    r.id_noclegu,
    n.nazwa AS nazwa_noclegu,
    CONCAT(u.imie, ' ', u.nazwisko) AS turysta,
    r.data_zameldowania,
    r.data_wymeldowania,
    r.liczba_gosci,
    r.calkowita_cena,
    r.status
FROM rezerwacje r
INNER JOIN noclegi n ON r.id_noclegu = n.id_noclegu
INNER JOIN uzytkownicy u ON r.id_turysty = u.id_uzytkownika
"""

try:
    df_rezerwacje = conn.query(query_rezerwacje, ttl=600)

    if df_rezerwacje.empty:
        st.info("Tabela 'rezerwacje' jest pusta.")
    else:
        st.dataframe(
            df_rezerwacje,
            width='stretch',
            hide_index=True,
            column_config={
                "id_rezerwacji": "ID Rezerwacji",
                "id_noclegu": "ID Noclegu",
                "nazwa_noclegu": "Obiekt noclegowy",
                "turysta": "Klient (Turysta)",
                "data_zameldowania": st.column_config.DateColumn("Zameldowanie"),
                "data_wymeldowania": st.column_config.DateColumn("Wymeldowanie"),
                "liczba_gosci": "Goście",
                "calkowita_cena": st.column_config.NumberColumn("Koszt całkowity", format="%.2f PLN"),
                "status": "Status"
            }
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'rezerwacje'. Błąd: {e}")

st.markdown("---")

# =========================================================================
# 5. TABELA: PŁATNOŚCI
# =========================================================================
st.subheader("Rejestr transakcji i płatności")

query_platnosci = """
SELECT 
    p.id_platnosci,
    p.id_rezerwacji,
    p.id_transakcji_zewnetrznej,
    p.metoda_platnosci,
    p.kwota,
    p.status,
    p.data_platnosci
FROM platnosci p
"""

try:
    df_platnosci = conn.query(query_platnosci, ttl=600)

    if df_platnosci.empty:
        st.info("Tabela 'platnosci' jest pusta.")
    else:
        st.dataframe(
            df_platnosci,
            width='stretch',
            hide_index=True,
            column_config={
                "id_platnosci": "ID Płatności",
                "id_rezerwacji": "ID Rezerwacji",
                "id_transakcji_zewnetrznej": "ID Bramki (External)",
                "metoda_platnosci": "Metoda",
                "kwota": st.column_config.NumberColumn("Kwota", format="%.2f PLN"),
                "status": "Status",
                "data_platnosci": st.column_config.DatetimeColumn("Data księgowania")
            }
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'platnosci'. Błąd: {e}")

st.markdown("---")

# =========================================================================
# 6. TABELA: OPINIE
# =========================================================================
st.subheader("Opinie i oceny wystawione przez użytkowników")

query_opinie = """
SELECT 
    o.id_opinii,
    n.nazwa AS nazwa_noclegu,
    CONCAT(u.imie, ' ', u.nazwisko) AS autor,
    o.ocena,
    o.komentarz,
    o.data_dodania
FROM opinie o
INNER JOIN noclegi n ON o.id_noclegu = n.id_noclegu
INNER JOIN uzytkownicy u ON o.id_turysty = u.id_uzytkownika
"""

try:
    df_opinie = conn.query(query_opinie, ttl=600)

    if df_opinie.empty:
        st.info("Tabela 'opinie' jest pusta.")
    else:
        st.dataframe(
            df_opinie,
            width='stretch',
            hide_index=True,
            column_config={
                "id_opinii": "ID Opinii",
                "nazwa_noclegu": "Obiekt noclegowy",
                "autor": "Wystawiający",
                "ocena": st.column_config.NumberColumn("Ocena punktowa", format="%d ⭐"),
                "komentarz": st.column_config.TextColumn("Treść komentarza (Może być NULL)", width="large"),
                "data_dodania": st.column_config.DatetimeColumn("Data dodania")
            }
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'opinie'. Błąd: {e}")

st.markdown("---")

# =========================================================================
# 7. TABELA: NOCLEGI_UDOGODNIENIA (Tabela łącząca M:N)
# =========================================================================
st.subheader("Udogodnienia przypisane do obiektów")

query_udogodnienia = """
SELECT 
    nu.id_noclegu,
    n.nazwa AS nazwa_noclegu,
    nu.id_udogodnienia
FROM noclegi_udogodnienia nu
INNER JOIN noclegi n ON nu.id_noclegu = n.id_noclegu
"""

try:
    df_udogodnienia = conn.query(query_udogodnienia, ttl=600)

    if df_udogodnienia.empty:
        st.info("Tabela łącząca 'noclegi_udogodnienia' jest pusta.")
    else:
        st.dataframe(
            df_udogodnienia,
            width='stretch',
            hide_index=True,
            column_config={
                "id_noclegu": "ID Noclegu",
                "nazwa_noclegu": "Obiekt noclegowy",
                "id_udogodnienia": "ID Udogodnienia"
            }
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'noclegi_udogodnienia'. Błąd: {e}")

st.markdown("---")

# =========================================================================
# 8. TABELA: KALENDARZ DOSTĘPNOŚCI
# =========================================================================
st.subheader("Terminarz i kalendarz dostępności pokoi")

query_kalendarz = """
SELECT 
    k.id_terminu,
    k.id_noclegu,
    n.nazwa AS nazwa_noclegu,
    k.data,
    k.czy_dostepny,
    k.cena_modyfikowana
FROM kalendarz_dostepnosci k
INNER JOIN noclegi n ON k.id_noclegu = n.id_noclegu
"""

try:
    df_kalendarz = conn.query(query_kalendarz, ttl=600)

    if df_kalendarz.empty:
        st.info("Tabela 'kalendarz_dostepnosci' jest pusta.")
    else:
        st.dataframe(
            df_kalendarz,
            width='stretch',
            hide_index=True,
            column_config={
                "id_terminu": "ID Rekordu",
                "id_noclegu": "ID Noclegu",
                "nazwa_noclegu": "Obiekt noclegowy",
                "data": st.column_config.DateColumn("Dzień kalendarzowy"),
                "czy_dostepny": "Dostępność (0/1)",
                "cena_modyfikowana": st.column_config.NumberColumn("Cena dedykowana", format="%.2f PLN")
            }
        )
except Exception as e:
    st.error(f"Nie udało się pobrać danych z tabeli 'kalendarz_dostepnosci'. Błąd: {e}")

render_page_footer()
