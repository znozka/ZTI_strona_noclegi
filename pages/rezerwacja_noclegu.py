import streamlit as st
import datetime
from datetime import date, datetime, timedelta
import streamlit.components.v1 as components
import json
import os
import logging
import warnings
from sqlalchemy import text
from src.ui import render_page_header, render_page_footer
from src.utils import send_booking_created_email

# ukrycie ostrzeżeń w konsoli
warnings.filterwarnings("ignore", category=DeprecationWarning)

# filtr usuwający komunikat Streamlita o st.components
class WyciszKomponentyFilter(logging.Filter):
    def filter(self, record):
        # jeśli log zawiera wzmiankę o st.components.v1.html, wyrzuć go
        return "st.components.v1.html" not in record.getMessage()

# nakładamy filtr na absolutnie wszystkie loggery powiązane ze Streamlitem
for logger_name in list(logging.Logger.manager.loggerDict.keys()):
    if "streamlit" in logger_name:
        logger = logging.getLogger(logger_name)
        logger.addFilter(WyciszKomponentyFilter())
        logger.setLevel(logging.ERROR)

# 1. Odzyskanie i walidacja ID noclegu
if "id" in st.query_params:
    st.session_state.selected_nocleg_id = int(st.query_params["id"])

# Pobranie do lokalnej zmiennej
selected_id = st.session_state.get("selected_nocleg_id")

# Jeśli nie ma ID w URL ani w sesji, blokujemy wejście
if not selected_id:
    st.warning("Nie wybrano noclegu. Wracam do wyników...")
    st.switch_page("pages/wyniki_wyszukiwania.py")

# Ustawienia strony
st.set_page_config(
    page_title="Rezerwacja noclegu",
    page_icon="assets/images/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Renderowanie nagłówka strony (wspólny element)
render_page_header()

# Połączenie z bazą danych
conn = st.connection("azure_sql", type="sql")

@st.cache_data(ttl=300)
def pobierz_dane_noclegu(nocleg_id):
    try:
        query = """
            SELECT id_noclegu, nazwa, typ_obiektu, lokalizacja_miasto, lokalizacja_adres, cena_za_noc, maks_liczba_osob
            FROM noclegi
            WHERE id_noclegu = :id
        """
        df = conn.query(query, params={"id": nocleg_id})

        if not df.empty:
            return df.iloc[0].to_dict()
    except Exception as e:
        st.error("Błąd pobierania danych z bazy: {e}")
    return None

try:
    query_udogodnienia = """
        SELECT u.nazwa
        FROM udogodnienia u
        JOIN noclegi_udogodnienia nu ON u.id_udogodnienia = nu.id_udogodnienia
        WHERE nu.id_noclegu = :id_noclegu
    """
    with conn.session as session:
        rows = session.execute(text(query_udogodnienia), {"id_noclegu": int(selected_id)}).fetchall()
        lista_udogodnien = [row[0] for row in rows]
except Exception as e:
    lista_udogodnien = []

OBIEKT = pobierz_dane_noclegu(selected_id)

if not OBIEKT:
    st.error("Nie znaleziono obiektu o podanym ID w bazie")
    st.stop()

# Pobieranie parametrów z URL / Sesji
url_miejsce = st.query_params.get("miejsce", st.session_state.get("search_miejsce", ""))
url_data_od = st.query_params.get("data_od", None)
url_data_do = st.query_params.get("data_do", None)
url_osoby = st.query_params.get("osoby", None)
url_clicked = st.query_params.get("clicked", None)

# Parsowanie daty "od"
if url_data_od:
    try: st.session_state.search_data_od = date.fromisoformat(url_data_od)
    except ValueError: st.session_state.search_data_od = date.today()
else:
    st.session_state.search_data_od = st.session_state.get("search_data_od", date.today())

# Parsowanie daty "do"
if url_data_do:
    try: st.session_state.search_data_do = date.fromisoformat(url_data_do)
    except ValueError: st.session_state.search_data_do = date.today() + timedelta(days=2)
else:
    st.session_state.search_data_do = st.session_state.get("search_data_do", date.today() + timedelta(days=2))

# Liczba osób
if url_osoby is not None:
    try: url_osoby = int(url_osoby)
    except ValueError: url_osoby = 2
else:
    url_osoby = st.session_state.get("search_osoby", 2)


dzis = datetime.today().date()

if "search_check_in" not in st.session_state:
    st.session_state.search_check_in = dzis
if "search_check_out" not in st.session_state:
    st.session_state.search_check_out = dzis + timedelta(days=1)
if "search_guests" not in st.session_state:
    st.session_state.search_guests = 2

# Interfejs użytkownika
st.title("Rezerwacja Noclegu")
st.subheader(f"Rezerwujesz: {OBIEKT['nazwa']}")
st.caption(f"Lokalizacja: {OBIEKT['lokalizacja_adres']} | Cena bazowa: {OBIEKT['cena_za_noc']} PLN / doba | Maksymalna liczba gości: {OBIEKT['maks_liczba_osob']}")

st.markdown("---")

# Formularz rezerwacji
with st.form("formularz_rezerwacji"):
    st.write("### Szczegóły twojego pobytu")

    col_data_od, col_data_do, col_osoby = st.columns([1.2, 1.2, 0.6])

    with col_data_od:
        wybrana_data_od = st.date_input(
            label="Początek pobytu",
            value=st.session_state.get("search_data_od", date.today())
        )

    with col_data_do:
        wybrana_data_do = st.date_input(
            label="Koniec pobytu",
            value=st.session_state.get("search_data_do", date.today() + timedelta(days=2))
        )

    with col_osoby:
        liczba_gosci = st.number_input(
            "Liczba osób",
            min_value=1,
            max_value=OBIEKT["maks_liczba_osob"],
            value=int(url_osoby)
        )

    # Dodatkowa sekcja 
    st.write("#### Dodatki")
    col_snadanie, col_parking, col_zwierze = st.columns(3)

    ma_sniadanie = "Breakfast ($)" in lista_udogodnien
    ma_parking = "Parking ($)" in lista_udogodnien
    ma_zwierzeta = "Pet-friendly" in lista_udogodnien

    with col_snadanie:
        sniadanie = st.checkbox(
            "Śniadanie kontynentalne (+50 PLN / doba)",
            value=False,
            disabled=not ma_sniadanie,
            help=None if ma_sniadanie else "Brak dostępnej usługi w tym obiekcie",
            key="chk_sniadanie"
            )
    with col_parking:
        parking = st.checkbox(
            "Miejsce parkingowe (+30 PLN / doba)",
            value=False,
            disabled=not ma_parking,
            help=None if ma_parking else "Brak dostępnej usługi w tym obiekcie",
            key="chk_parking"
            )
    with col_zwierze:
        zwierze = st.checkbox(
            "Pobyt ze zwierzęciem (+100 PLN jednorazowo)",
            value=False,
            disabled=not ma_zwierzeta,
            help=None if ma_zwierzeta else "Brak dostępnej usługi w tym obiekcie",
            key="chk_zwierzeta"
            )

    st.markdown("<br>", unsafe_allow_html=True)

    przycisk_podsumuj = st.form_submit_button("Przejdź do podsumowania", use_container_width=True)

if "rezerwacja_kliknieta" not in st.session_state:
    st.session_state.rezerwacja_kliknieta = False

st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@800&display=swap" rel="stylesheet">
    <style>
        /* Aplikowanie czcionki Inter do całego bloku podsumowania */
        .custom-font-container * {
            font-family: 'Inter', sans-serif !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

if przycisk_podsumuj or st.session_state.get("pokaz_podsumowanie", False):
    st.session_state.pokaz_podsumowanie = True

    data_od = wybrana_data_od
    data_do = wybrana_data_do

    if data_od and data_do:
        if data_od < data_do:
            liczba_nocy = (data_do - data_od).days
            koszt_pobytu = round(liczba_nocy * OBIEKT["cena_za_noc"], 2)

            lista_dodatkow = []
            koszt_dodatkow = 0

            if sniadanie:
                cena_sn = 50 * liczba_nocy * liczba_gosci
                lista_dodatkow.append(f"Śniadanie kontynentalne: **{cena_sn} PLN**")
                koszt_dodatkow += cena_sn
            if parking:
                cena_pk = 30 * liczba_nocy
                lista_dodatkow.append(f"Miejsce parkingowe: **{cena_pk} PLN**")
                koszt_dodatkow += cena_pk
            if zwierze:
                lista_dodatkow.append("Pobyt ze zwierzęciem: **100 PLN**")
                koszt_dodatkow += 100

            sum_total = round(koszt_pobytu + koszt_dodatkow,2)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("## Podsumowanie rezerwacji")

            st.markdown('<div class="custom-font-container">', unsafe_allow_html=True)

            col_lewa_dane, col_prawa_koszty = st.columns(2)

            with col_lewa_dane:
                with st.container(border=True):
                    st.markdown("### Szczegóły pobytu")
                    st.markdown(f"**Obiekt:** {OBIEKT['nazwa']}")
                    st.markdown(f"**Typ:** {OBIEKT.get('typ_obiektu', 'Apartament')}")
                    st.markdown(f"**Adres:** {OBIEKT['lokalizacja_adres']}")
                    st.markdown("---")
                    st.markdown(f"**Od:** {data_od}")
                    st.markdown(f"**Do:** {data_do}")
                    st.markdown(f"**Długość pobytu:** {liczba_nocy} {'noc' if liczba_nocy == 1 else 'noce' if 1 < liczba_nocy < 5 else 'nocy'}")
                    st.markdown(f"**Liczba gości:** {liczba_gosci} os.")

            with col_prawa_koszty:
                with st.container(border=True):
                    st.markdown("### Opłaty")
                    st.markdown(f"Wynajem: **{koszt_pobytu:.2f} PLN**")
                    
                    if lista_dodatkow:
                        st.markdown("**Wybrane usługi dodatkowe:**")
                        for dodatek in lista_dodatkow:
                            st.markdown(f"{dodatek}")
                    else:
                        st.markdown("Usługi dodatkowe: _Brak_")
                        
                    st.markdown("---")
                    
                    st.markdown(
                        f"""
                        <div style="padding: 12px 18px; border-radius: 8px; margin-top: 10px;">
                            <span style="font-size: 13px; font-weight: 600; color: #555; display: block; margin-bottom: 2px; letter-spacing: 0.5px;">RAZEM DO ZAPŁATY</span>
                            <span style="font-size: 34px; font-weight: 800; color: #EAB308; letter-spacing: -0.5px;">{sum_total:.2f} PLN</span>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    
            st.markdown('</div>', unsafe_allow_html=True)


            st.markdown("<br>", unsafe_allow_html=True)

            if "rezerwacja_kliknieta" not in st.session_state:
                st.session_state.rezerwacja_kliknieta = False

            if not st.session_state.rezerwacja_kliknieta:
                if st.button("Zatwierdzam i rezerwuję", use_container_width=True, type="primary"):
                    id_turysty = st.session_state.get("user_id")

                    if not id_turysty:
                        st.error("Musisz być zalogowany, aby dokonać rezerwacji!")
                    else:
                        try:
                            query_insert = """
                                INSERT INTO rezerwacje (
                                id_turysty, id_noclegu, data_zameldowania, data_wymeldowania, liczba_gosci, calkowita_cena, status
                                ) 
                                VALUES (
                                    :id_turysty, :id_noclegu, :data_od, :data_do, :liczba_gosci, :cena, 'oczekuje_na_platnosc'
                                )
                            """
                            query_select_id = """
                                SELECT TOP 1 id_rezerwacji 
                                FROM rezerwacje 
                                WHERE id_turysty = :id_turysty AND id_noclegu = :id_noclegu
                                ORDER BY id_rezerwacji DESC
                            """

                            with conn.session as session:
                                session.execute(
                                    text(query_insert),
                                    {
                                        "id_turysty": int(id_turysty),
                                        "id_noclegu": int(selected_id),
                                        "data_od": data_od,
                                        "data_do": data_do,
                                        "liczba_gosci": int(liczba_gosci),
                                        "cena": float(sum_total)
                                    }
                                )
                                session.commit()

                                result = session.execute(
                                    text(query_select_id),
                                    {"id_turysty": int(id_turysty), "id_noclegu": int(selected_id)}
                                )
                                id_rezerwacji = int(result.fetchone()[0])
                                
                            
                            send_booking_created_email(
                                to_email=st.session_state.user_email, 
                                id_rezerwacji=id_rezerwacji, 
                                nazwa_obiektu=OBIEKT['nazwa'], 
                                kwota=sum_total
                            )

                            st.session_state.rezerwacja_kliknieta = True
                            st.rerun()

                        except Exception as e:
                            st.error(f"Błąd zapisu rezerwacji do bazy danych {e}")
            else:
                st.success("Sukces! Przejdź do płatności aby opłacić swoją rezerwację.")
               

                if st.button("Przejdź do płatności", use_container_width=True, type="primary"):
                    st.info("Przekierowywanie do bramki płatniczej...")
                    st.switch_page("pages/platnosci.py")

        else:
            st.error("Data wyjazdu musi być późniejsza niż data przyjazdu.")

    st.markdown("<br>", unsafe_allow_html=True)

    kliknieto_powrot = st.markdown(
        """
        <style>
            div[data-testid="stButton"] button[key="btn_powrot_szary"] {
                background-color: #f0f2f6 !important;
                color: #31333f !important;
                border: 1px solid #d3d3d3 !important;
            }
            div[data-testid="stButton"] button[key="btn_powrot_szary"]:hover {
                background-color: #e0e4ec !important;
                border-color: #bcbcbc !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    if st.button("Wróć do noclegu", use_container_width=True, type="secondary"):
        st.session_state.pokaz_podsumowanie = False
        st.session_state.rezerwacja_kliknieta = False

        if selected_id:
            st.query_params["id"] = selected_id
        st.switch_page("pages/strona_noclegu.py")


render_page_footer()