import streamlit as st
import datetime
import requests
import pandas as pd
import folium
import logging
import warnings
from streamlit_folium import folium_static
from urllib.parse import urlencode
from src.ui import render_page_header, render_page_footer
from src.utils import wyswietl_zdjecie

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

# Ustawienia strony
st.set_page_config(
    page_title="Wyniki wyszukiwania",
    page_icon="assets/images/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header()

st.markdown("### Przeglądaj dostępne oferty noclegów")

conn = st.connection("azure_sql", type="sql")

# pogoda
WSPOLRZEDNE_MIAST = {
    "Gdańsk": (54.3520, 18.6466),
    "Kraków": (50.0614, 19.9366),
    "Katowice": (50.2649, 19.0238),
    "Poznań": (52.4064, 16.9252),
    "Warszawa": (52.2297, 21.0122),
    "Wrocław": (51.1079, 17.0385),
    "Łódź": (51.7592, 19.4560),
}

# definicje kategorii pogodowych - każda to funkcja oceniająca listę dziennych podsumowań (df_summary)
# zwraca True/False, czy dany zestaw dni spełnia warunek.
# każde "podsumowanie dnia" to słownik zgodny ze strukturą odpowiedzi /onecall/day_summary.
WEATHER_CATEGORIES = {
    "upalne_wakacje": {
        "label": "☀️ Upalne wakacje",
        "opis": "każdego dnia ponad 25°C w ciągu dnia",
        "check": lambda dni: all(d["temperature"]["afternoon"] > 25 for d in dni),
    },
    "przyjemnie_cieplo": {
        "label": "🌤️ Przyjemnie ciepło",
        "opis": "każdego dnia ponad 20°C w ciągu dnia",
        "check": lambda dni: all(d["temperature"]["afternoon"] > 20 for d in dni),
    },
    "bez_deszczu": {
        "label": "🌂 Bez deszczu",
        "opis": "minimalne ryzyko opadów przez cały pobyt",
        "check": lambda dni: (sum(d["precipitation"]["total"] for d in dni) / max(1, len(dni))) < 1,
    },
    "ciepłe_wieczory": {
        "label": "🌇 Ciepłe wieczory",
        "opis": "każdego wieczoru ponad 20°C - idealnie na kolację na zewnątrz",
        "check": lambda dni: all(d["temperature"]["evening"] > 20 for d in dni),
    },
    "slonecznie": {
        "label": "🌞 Słonecznie",
        "opis": "niskie zachmurzenie - duża szansa na słońce",
        "check": lambda dni: (sum(d["cloud_cover"]["afternoon"] for d in dni) / max(1, len(dni))) < 40,
    },
    "bez_wiatru": {
        "label": "🍃 Bezwietrznie",
        "opis": "wiatr nie przekracza 5 m/s przez cały pobyt",
        "check": lambda dni: all(d["wind"]["max"]["speed"] <= 5 for d in dni),
    },
    "chlodniej": {
        "label": "❄️ Chłodniej",
        "opis": "w dzień nie więcej niż 20°C - dla lubiących chłodniejszą pogodę",
        "check": lambda dni: all(d["temperature"]["afternoon"] <= 20 for d in dni),
    },
}

MAX_DNI_SPRAWDZANYCH = 5  # ograniczenie liczby zapytań API na pobyt

def wygeneruj_daty_do_sprawdzenia(data_od, data_do, maks_dni=MAX_DNI_SPRAWDZANYCH):
    """Zwraca listę dat (max maks_dni) równomiernie rozłożonych w okresie pobytu."""
    liczba_nocy = max(1, (data_do - data_od).days)
    wszystkie_daty = [data_od + datetime.timedelta(days=i) for i in range(liczba_nocy)]

    if len(wszystkie_daty) <= maks_dni:
        return wszystkie_daty

    # równomierne próbkowanie maks_dni dat z całego zakresu pobytu
    krok = (len(wszystkie_daty) - 1) / (maks_dni - 1)
    indeksy = sorted(set(round(i * krok) for i in range(maks_dni)))
    return [wszystkie_daty[i] for i in indeksy]

@st.cache_data(ttl=3600, show_spinner=False)
def pobierz_pogode_dnia(lat, lon, data_iso):
    """Pojedyncze zapytanie do OpenWeatherMap day_summary."""
    try:
        api_key = st.secrets.api_keys["API_KEY_OPENWEATHER"]
    except Exception:
        return None

    url = "https://api.openweathermap.org/data/3.0/onecall/day_summary"
    params = {
        "lat": lat,
        "lon": lon,
        "date": data_iso,
        "appid": api_key,
        "units": "metric",
        "lang": "pl",
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def pobierz_prognoze_dla_miasta(miasto, data_od_iso, data_do_iso):
    """
    Pobiera podsumowania pogodowe (max MAX_DNI_SPRAWDZANYCH dni) dla danego miasta
    i zwraca listę słowników day_summary (tylko udane odpowiedzi).
    """
    if miasto not in WSPOLRZEDNE_MIAST:
        return []

    lat, lon = WSPOLRZEDNE_MIAST[miasto]
    data_od = datetime.date.fromisoformat(data_od_iso)
    data_do = datetime.date.fromisoformat(data_do_iso)

    daty = wygeneruj_daty_do_sprawdzenia(data_od, data_do)

    wyniki = []
    for d in daty:
        dane = pobierz_pogode_dnia(lat, lon, d.isoformat())
        if dane:
            wyniki.append(dane)
    return wyniki

def miasto_spelnia_kategorie(miasto, data_od_iso, data_do_iso, wybrane_kategorie):
    """Sprawdza czy dla danego miasta i zakresu dat spełnione są WSZYSTKIE wybrane kategorie pogodowe (AND)."""
    if not wybrane_kategorie:
        return True

    dni = pobierz_prognoze_dla_miasta(miasto, data_od_iso, data_do_iso)
    if not dni:
        return False

    for klucz_kat in wybrane_kategorie:
        funkcja_check = WEATHER_CATEGORIES[klucz_kat]["check"]
        try:
            if not funkcja_check(dni):
                return False
        except Exception:
            return False

    return True

@st.fragment
def renderuj_panel_pogody(version):
    # sprawdzamy, czy użytkownik szuka "Gdziekolwiek" lub nie wpisał nic
    aktywne_miejsce = st.session_state.get("search_miejsce", "")
    if aktywne_miejsce is None:
        aktywne_miejsce = ""

    pokaz_filtr_pogodowy = aktywne_miejsce.strip() == "" or aktywne_miejsce.strip().lower() == "gdziekolwiek"

    if pokaz_filtr_pogodowy:
        if "aktywna_pogoda" not in st.session_state:
            zapisane_kategorie_str_init = url_filters["pogoda"]
            st.session_state.aktywna_pogoda = (
                [k for k in zapisane_kategorie_str_init.split(",") if k]
                if zapisane_kategorie_str_init else []
            )

        weather_card = st.container(border=True)
        with weather_card:
            st.markdown("#### Dopasuj podróż do pogody!")

            klucze_kategorii = list(WEATHER_CATEGORIES.keys())
            etykieta_do_klucza = {f"{v['label']} - {v['opis']}": k for k, v in WEATHER_CATEGORIES.items()}
            klucz_do_etykiety = {k: f"{v['label']} - {v['opis']}" for k, v in WEATHER_CATEGORIES.items()}

            wybrane_etykiety_robocze = st.multiselect(
                "Warunki pogodowe",
                options=[klucz_do_etykiety[k] for k in klucze_kategorii],
                default=[klucz_do_etykiety[k] for k in st.session_state.aktywna_pogoda if k in WEATHER_CATEGORIES],
                placeholder="Wybierz opcje",
                key=f"pogoda_multi_{version}",
                label_visibility="collapsed",
            )

            col_left, col_center, col_right = st.columns([3, 1, 3])
            with col_center:
                zastosuj_pogode = st.button("Zastosuj filtr pogodowy", type="primary", use_container_width=True)

            if zastosuj_pogode:
                st.session_state.aktywna_pogoda = [etykieta_do_klucza[e] for e in wybrane_etykiety_robocze]
                st.query_params["pogoda"] = ",".join(st.session_state.aktywna_pogoda)
                # Wywołanie st.rerun() WEWNĄTRZ fragmentu spowoduje przeładowanie JUŻ CAŁEJ strony
                st.rerun()

            # dynamiczne wyświetlanie miast (działa płynnie bez dotykania mapy!)
            wybrane_kategorie_pogody = wybrane_etykiety_robocze
            if wybrane_kategorie_pogody and "search_data_od" in st.session_state and "search_data_do" in st.session_state:
                klucze_robocze = [etykieta_do_klucza[e] for e in wybrane_kategorie_pogody]
                data_od_iso = str(st.session_state.search_data_od)
                data_do_iso = str(st.session_state.search_data_do)
                
                pasujace_miasta = [
                    miasto for miasto in WSPOLRZEDNE_MIAST.keys()
                    if miasto_spelnia_kategorie(miasto, data_od_iso, data_do_iso, klucze_robocze)
                ]
                
                if pasujace_miasta:
                    st.info(f"**Dostępne miasta dla tej pogody:** {', '.join(pasujace_miasta)}")
                else:
                    st.error("**Brak miast** spełniających wybrane warunki pogodowe w tych datach.")
    else:
        st.session_state.aktywna_pogoda = []

# pobieranie najwyższej ceny dla bieżących kryteriów wyszukiwania
def pobierz_najwyzsza_cene(miejsce, osoby):
    try:
        where_clauses = ["maks_liczba_osob >= :osoby"]
        sql_params = {"osoby": osoby}
        
        if miejsce and miejsce.strip():
            where_clauses.append("lokalizacja_miasto LIKE :miasto")
            sql_params["miasto"] = f"%{miejsce.strip()}%"
            
        query = f"SELECT MAX(cena_za_noc) as max_cena FROM noclegi WHERE {' AND '.join(where_clauses)}"
        df = conn.query(query, params=sql_params, ttl=0)
        
        if not df.empty and df.iloc[0]["max_cena"] is not None:
            return int(df.iloc[0]["max_cena"])
    except Exception:
        pass
    return 2000  # fallback

# Funkcja callback obsługująca kliknięcie w dowolny element noclegu
def przejdz_do_szczegolow(id_noclegu):
    st.session_state.selected_nocleg_id = id_noclegu
    st.query_params.clear()
    st.switch_page("pages/strona_noclegu.py")

# Dynamiczne pobieranie unikalnych miast z bazy danych z cache na 1 godzinę
@st.cache_data(ttl=3600)
def pobierz_unikalne_miasta():
    try:
        df_miasta = conn.query("SELECT DISTINCT lokalizacja_miasto FROM noclegi WHERE lokalizacja_miasto IS NOT NULL ORDER BY lokalizacja_miasto", ttl=0)
        return df_miasta["lokalizacja_miasto"].tolist()
    except Exception:
        return ["Gdańsk", "Kraków", "Katowice", "Poznań", "Warszawa", "Wrocław", "Łódź"]

lista_miast = pobierz_unikalne_miasta()

def build_search_map(df_hotels):
    df_coords = df_hotels.dropna(subset=["szerokosc_geo", "dlugosc_geo"])
    if df_coords.empty:
        return None

    center_lat = float(df_coords["szerokosc_geo"].astype(float).mean())
    center_lon = float(df_coords["dlugosc_geo"].astype(float).mean())
    
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=11, 
        control_scale=False,
        tiles="cartodbpositron"
    )

    primary_color = st.config.get_option("theme.primaryColor")
    text_color = st.config.get_option("theme.textColor")
    bg_color = st.config.get_option("theme.backgroundColor")

    bounds = []
    for _, row in df_coords.iterrows():
        lat = float(row["szerokosc_geo"])
        lon = float(row["dlugosc_geo"])
        bounds.append([lat, lon])

        query = urlencode({
            "page": "pages/strona_noclegu.py",
            "id": row["id_noclegu"],
            "miejsce": st.session_state.search_miejsce,
            "data_od": str(st.session_state.search_data_od),
            "data_do": str(st.session_state.search_data_do),
            "osoby": str(st.session_state.search_osoby),
            "clicked": "True",
        })
        
        js = f"window.open(window.top.location.origin + '/strona_noclegu?{query}', '_blank'); return false;"
        
        popup_html = f"""
        <div style="
            font-family: 'Source Sans Pro', sans-serif; 
            font-size: 13px; 
            color: {text_color};
            line-height: 1.4;
            max-width: 200px;
        ">
            <strong style="font-size: 14px; color: {primary_color};">{row['nazwa']}</strong><br>
            <span style="color: #767676;">{row['lokalizacja_adres']}</span><br>
            <a href="#" onclick="{js}" style="
                color: {primary_color}; 
                text-decoration: none; 
                font-weight: bold;
            ">Zobacz szczegóły →</a>
        </div>
        """

        w, h = (22, 36)
        anchor_x = w // 2
        anchor_y = h
        
        icon_html = f"""
        <div style="cursor: pointer;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 32" width="{w}" height="{h}" style="filter: drop-shadow(0px 2px 3px rgba(0,0,0,0.3));">
                <path d="M12 0C5.38 0 0 5.38 0 12c0 9 12 20 12 20s12-11 12-20C24 5.38 18.62 0 12 0z" fill="{primary_color}"/>
                <circle cx="12" cy="12" r="4.5" fill="white"/>
                <circle cx="12" cy="12" r="3.5" fill="{bg_color}"/>
            </svg>
        </div>
        """
        
        icon = folium.DivIcon(
            html=icon_html,
            icon_size=(w, h),
            icon_anchor=(anchor_x, anchor_y)
        )

        folium.Marker(
            location=[lat, lon],
            tooltip=row["nazwa"],
            popup=folium.Popup(popup_html, max_width=250),
            icon=icon,
        ).add_to(m)

    if len(bounds) > 1:
        m.fit_bounds(bounds, padding=(40, 40))

    return m

# formularz wyszukiwania
if "miejsce" in st.query_params:
    st.session_state.search_miejsce = st.query_params["miejsce"]
elif "search_miejsce" not in st.session_state:
    st.session_state.search_miejsce = ""

if "data_od" in st.query_params:
    try: st.session_state.search_data_od = datetime.date.fromisoformat(st.query_params["data_od"])
    except ValueError: st.session_state.search_data_od = datetime.date.today()
elif "search_data_od" not in st.session_state:
    st.session_state.search_data_od = datetime.date.today()

if "data_do" in st.query_params:
    try: st.session_state.search_data_do = datetime.date.fromisoformat(st.query_params["data_do"])
    except ValueError: st.session_state.search_data_do = datetime.date.today() + datetime.timedelta(days=2)
elif "search_data_do" not in st.session_state:
    st.session_state.search_data_do = datetime.date.today() + datetime.timedelta(days=2)

if "osoby" in st.query_params:
    try: st.session_state.search_osoby = int(st.query_params["osoby"])
    except ValueError: st.session_state.search_osoby = 2
elif "search_osoby" not in st.session_state:
    st.session_state.search_osoby = 2

try:
    st.session_state.search_osoby = int(st.session_state.search_osoby)
except (ValueError, TypeError):
    st.session_state.search_osoby = 2

if "clicked" in st.query_params:
    st.session_state.search_clicked = st.query_params["clicked"] == "True"
elif "search_clicked" not in st.session_state:
    st.session_state.search_clicked = bool(st.session_state.search_miejsce)

max_cena_baza = pobierz_najwyzsza_cene(st.session_state.get("search_miejsce", ""), st.session_state.search_osoby)

if "saved_filters" not in st.session_state:
    st.session_state.saved_filters = {}

def pobierz_filtr(param_name, domyslna_wartosc, transformacja=lambda x: x):
    if param_name in st.query_params:
        wartosc = transformacja(st.query_params[param_name])
        st.session_state.saved_filters[param_name] = wartosc
        return wartosc
    return st.session_state.saved_filters.get(param_name, domyslna_wartosc)

url_filters = {
    "sort": pobierz_filtr("sort", "najwyższa ocena"),  # ZMIANA: domyślnie po najwyższej ocenie
    "cena_min": pobierz_filtr("cena_min", 0, lambda x: int(x) if str(x).isdigit() else 0),
    "cena_max": pobierz_filtr("cena_max", max_cena_baza, lambda x: int(x) if str(x).isdigit() else max_cena_baza),
    "f_hotel": pobierz_filtr("f_hotel", False, lambda x: x == "True" or x is True),
    "f_apartament": pobierz_filtr("f_apartament", False, lambda x: x == "True" or x is True),
    "f_b_and_b": pobierz_filtr("f_b_and_b", False, lambda x: x == "True" or x is True),
    "f_schronisko": pobierz_filtr("f_schronisko", False, lambda x: x == "True" or x is True),
    "f_wynajem": pobierz_filtr("f_wynajem", False, lambda x: x == "True" or x is True),
    "f_p_darmowy": pobierz_filtr("f_p_darmowy", False, lambda x: x == "True" or x is True),
    "f_p_platny": pobierz_filtr("f_p_platny", False, lambda x: x == "True" or x is True),
    "f_p_brak": pobierz_filtr("f_p_brak", False, lambda x: x == "True" or x is True),
    "u_klimatyzacja": pobierz_filtr("u_klimatyzacja", False, lambda x: x == "True" or x is True),
    "u_przyjazny_dzieciom": pobierz_filtr("u_przyjazny_dzieciom", False, lambda x: x == "True" or x is True),
    "u_kuchnia": pobierz_filtr("u_kuchnia", False, lambda x: x == "True" or x is True),
    "u_wifi": pobierz_filtr("u_wifi", False, lambda x: x == "True" or x is True),
    "u_sniadanie": pobierz_filtr("u_sniadanie", False, lambda x: x == "True" or x is True),
    "u_zwierzeta": pobierz_filtr("u_zwierzeta", False, lambda x: x == "True" or x is True),
    "u_fitness": pobierz_filtr("u_fitness", False, lambda x: x == "True" or x is True),
    "u_bar": pobierz_filtr("u_bar", False, lambda x: x == "True" or x is True),
    "u_restauracja": pobierz_filtr("u_restauracja", False, lambda x: x == "True" or x is True),
    "u_transfer": pobierz_filtr("u_transfer", False, lambda x: x == "True" or x is True),
    "u_wozki": pobierz_filtr("u_wozki", False, lambda x: x == "True" or x is True),
    "u_niepalacy": pobierz_filtr("u_niepalacy", False, lambda x: x == "True" or x is True),
    "u_pralnia": pobierz_filtr("u_pralnia", False, lambda x: x == "True" or x is True),
    "u_balkon": pobierz_filtr("u_balkon", False, lambda x: x == "True" or x is True),
    "u_lozeczko": pobierz_filtr("u_lozeczko", False, lambda x: x == "True" or x is True),
    "u_winda": pobierz_filtr("u_winda", False, lambda x: x == "True" or x is True),
    "u_basen": pobierz_filtr("u_basen", False, lambda x: x == "True" or x is True),
    "pogoda": pobierz_filtr("pogoda", "", lambda x: x),
}

domyslny_indeks = None
if st.session_state.get("search_miejsce") in lista_miast:
    domyslny_indeks = lista_miast.index(st.session_state.search_miejsce)

if "filters_version" not in st.session_state:
    st.session_state.filters_version = 0
version = st.session_state.filters_version

if not st.session_state.search_clicked:
    st.warning("Aby wyświetlić wyniki, najpierw uruchom wyszukiwanie na stronie głównej.")
    if st.button("Wróć do strony głównej"):
        st.session_state.search_clicked = False
        for key in ["search_miejsce", "search_data_od", "search_data_do", "search_osoby", "selected_nocleg_id", "saved_filters"]:
            if key in st.session_state: del st.session_state[key]
        st.query_params.clear()
        st.switch_page("app.py")
    render_page_footer()
    st.stop()

# formularz wyszukiwania
search_container = st.container(border=True)
with search_container:
    c1, c2, c3, c4, c5 = st.columns([2.5, 1.2, 1.2, 1.2, 1])

    dzis = datetime.date.today()
    
    with c1:
        # pobieramy aktualne miasto z pamięci sesji
        zapisane_miejsce = st.session_state.get("search_miejsce", "")
        
        # tworzymy nową listę opcji: na samym początku doklejamy pusty ciąg znaków ""
        opcje_miast = [""] + [m for m in lista_miast if m != ""]
        
        # wyliczamy indeks startowy. Jeśli w pamięci jest miasto, wskazujemy na nie.
        if zapisane_miejsce in opcje_miast:
            domyslny_indeks = opcje_miast.index(zapisane_miejsce)
        else:
            domyslny_indeks = 0

        # renderujemy selectbox, używamy format_func, aby pusty ciąg "" wyświetlał się użytkownikowi jako opcja resetu
        miejsce_input = st.selectbox(
            "Miejsce", 
            options=opcje_miast,
            index=domyslny_indeks,
            format_func=lambda x: "Gdziekolwiek" if x == "" else x,
            label_visibility="visible"
        )
        
        # reakcja na kliknięcie - jeśli użytkownik rozwinął listę i kliknął opcję "Gdziekolwiek" (czyli miejsce_input stało się ""), a w tle wciąż wiszą wyniki dla starego miasta:
        if miejsce_input == "" and zapisane_miejsce != "":
            st.session_state.search_miejsce = ""  # czyścimy pamięć aktywną
            st.query_params["miejsce"] = ""       # czyścimy parametr z paska URL
            st.rerun()                            # odświeżamy stronę, by od razu pokazać noclegi ze wszystkich miast
    with c2:
        start_val = st.session_state.search_data_od
        if start_val < dzis:
            start_val = dzis

        data_od_input = st.date_input("Data od", value=start_val, min_value=dzis)
    with c3:
        min_data_do = data_od_input + datetime.timedelta(days=1)
        end_val = st.session_state.search_data_do
        if end_val < min_data_do:
            end_val = min_data_do

        data_do_input = st.date_input("Data do", value=end_val, min_value=min_data_do)
    with c4:
        osoby_input = st.number_input("Liczba osób", min_value=1, max_value=20, value=st.session_state.search_osoby)
    with c5:
        st.markdown("<br>", unsafe_allow_html=True)
        czyste_miejsce = miejsce_input if miejsce_input is not None else ""
        
        st.query_params["miejsce"] = czyste_miejsce
        st.query_params["data_od"] = str(data_od_input)
        st.query_params["data_do"] = str(data_do_input)
        st.query_params["osoby"] = str(osoby_input)
        st.query_params["clicked"] = "True"
        
        if st.button("Szukaj", width='stretch', type="primary"):
            if data_od_input >= data_do_input:
                st.toast("Data wyjazdu musi być późniejsza niż data przyjazdu!", icon="⚠️")
            else:            
                for klucz in ["cena_min", "cena_max"]:
                    if klucz in st.query_params: del st.query_params[klucz]
                
                if "saved_filters" in st.session_state:
                    st.session_state.saved_filters.pop("cena_min", None)
                    st.session_state.saved_filters.pop("cena_max", None)

                # nowe wyszukiwanie (inne miasto/daty) unieważnia poprzednią prognozę pogody, więc czyścimy aktywny filtr pogodowy - użytkownik musi go zatwierdzić ponownie
                st.session_state.aktywna_pogoda = []
                if "pogoda" in st.query_params: del st.query_params["pogoda"]

                st.session_state.filters_version += 1
                st.session_state.search_clicked = True
                st.session_state.search_miejsce = czyste_miejsce
                st.session_state.search_osoby = osoby_input
                st.session_state.search_data_od = data_od_input
                st.session_state.search_data_do = data_do_input
                st.rerun()

# karta filtra pogodowego
renderuj_panel_pogody(version)

# pobierasz wynik do dalszego filtrowania bazy danych / DataFrame poniżej
wybrane_kategorie_pogody = st.session_state.get("aktywna_pogoda", [])

# Layout dolny
panel_filtrow, panel_wynikow = st.columns([1, 3])

with panel_filtrow:
    sidebar_map_container = st.container()
    
    st.subheader("Sortuj")
    # ZMIANA: "najwyższa ocena" na pierwszym miejscu listy
    sort_options_list = ["najwyższa ocena", "od najtańszych", "od najdroższych"]
    try: sort_index = sort_options_list.index(url_filters["sort"])
    except ValueError: sort_index = 0

    sort_option = st.selectbox(
        "Sortuj według", 
        sort_options_list,
        index=sort_index,
        label_visibility="collapsed",
        key=f"sort_{version}"
    )
    st.query_params["sort"] = sort_option
    
    st.markdown("---")
    st.subheader("Filtruj") 
    
    st.write("**Cena za noc**")
    c_min, c_max = st.columns(2)
    
    with c_min:
        cena_min = st.number_input("Od", min_value=0, value=url_filters["cena_min"], step=100, key=f"cena_min_{version}")
        st.query_params["cena_min"] = str(cena_min)
    with c_max:
        cena_max = st.number_input("Do", min_value=0, value=url_filters["cena_max"], step=100, key=f"cena_max_{version}")
        st.query_params["cena_max"] = str(cena_max)
        
    st.markdown("---")
    st.write("**Rodzaj noclegu**")
    f_hotel = st.checkbox("Hotel", value=url_filters["f_hotel"], key=f"f_hotel_{version}")
    f_apartament = st.checkbox("Apartament", value=url_filters["f_apartament"], key=f"f_apartament_{version}")
    f_b_and_b = st.checkbox("B&B", value=url_filters["f_b_and_b"], key=f"f_b_and_b_{version}")
    f_schronisko = st.checkbox("Schronisko", value=url_filters["f_schronisko"], key=f"f_schronisko_{version}")
    f_wynajem = st.checkbox("Wynajem wakacyjny", value=url_filters["f_wynajem"], key=f"f_wynajem_{version}")
    
    st.query_params["f_hotel"] = str(f_hotel)
    st.query_params["f_apartament"] = str(f_apartament)
    st.query_params["f_b_and_b"] = str(f_b_and_b)
    st.query_params["f_schronisko"] = str(f_schronisko)
    st.query_params["f_wynajem"] = str(f_wynajem)
    
    st.markdown("---")
    st.write("**Parking**")
    f_p_darmowy = st.checkbox("Darmowy", value=url_filters["f_p_darmowy"], key=f"f_p_darmowy_{version}")
    f_p_platny = st.checkbox("Za dodatkową opłatą", value=url_filters["f_p_platny"], key=f"f_p_platny_{version}")
    f_p_brak = st.checkbox("Brak", value=url_filters["f_p_brak"], key=f"f_p_brak_{version}")
    
    st.query_params["f_p_darmowy"] = str(f_p_darmowy)
    st.query_params["f_p_platny"] = str(f_p_platny)
    st.query_params["f_p_brak"] = str(f_p_brak)
    
    st.markdown("---")
    st.write("**Udogodnienia**")
    u_klimatyzacja = st.checkbox("Klimatyzacja", value=url_filters["u_klimatyzacja"], key=f"u_klimatyzacja_{version}")
    u_przyjazny_dzieciom = st.checkbox("Przyjazny dzieciom", value=url_filters["u_przyjazny_dzieciom"], key=f"u_przyjazny_dzieciom_{version}")
    u_kuchnia = st.checkbox("Kuchnia", value=url_filters["u_kuchnia"], key=f"u_kuchnia_{version}")
    u_wifi = st.checkbox("Bezpłatne Wi-Fi", value=url_filters["u_wifi"], key=f"u_wifi_{version}")
    u_sniadanie = st.checkbox("Bezpłatne śniadanie", value=url_filters["u_sniadanie"], key=f"u_sniadanie_{version}")
    u_zwierzeta = st.checkbox("Przyjazny zwierzętom", value=url_filters["u_zwierzeta"], key=f"u_zwierzeta_{version}")
    u_fitness = st.checkbox("Centrum fitness", value=url_filters["u_fitness"], key=f"u_fitness_{version}")
    u_bar = st.checkbox("Bar", value=url_filters["u_bar"], key=f"u_bar_{version}")
    u_restauracja = st.checkbox("Restauracja", value=url_filters["u_restauracja"], key=f"u_restauracja_{version}")
    u_transfer = st.checkbox("Transfer lotniskowy", value=url_filters["u_transfer"], key=f"u_transfer_{version}")
    u_wozki = st.checkbox("Dostępne dla osób na wózkach", value=url_filters["u_wozki"], key=f"u_wozki_{version}")
    u_niepalacy = st.checkbox("Dla niepalących", value=url_filters["u_niepalacy"], key=f"u_niepalacy_{version}")
    u_pralnia = st.checkbox("Usługi pralnicze", value=url_filters["u_pralnia"], key=f"u_pralnia_{version}")
    u_balkon = st.checkbox("Balkon", value=url_filters["u_balkon"], key=f"u_balkon_{version}")
    u_lozeczko = st.checkbox("Łóżeczko dziecięce", value=url_filters["u_lozeczko"], key=f"u_lozeczko_{version}")
    u_winda = st.checkbox("Winda", value=url_filters["u_winda"], key=f"u_winda_{version}")
    u_basen = st.checkbox("Basen", value=url_filters["u_basen"], key=f"u_basen_{version}")
    
    st.query_params["u_klimatyzacja"] = str(u_klimatyzacja)
    st.query_params["u_przyjazny_dzieciom"] = str(u_przyjazny_dzieciom)
    st.query_params["u_kuchnia"] = str(u_kuchnia)
    st.query_params["u_wifi"] = str(u_wifi)
    st.query_params["u_sniadanie"] = str(u_sniadanie)
    st.query_params["u_zwierzeta"] = str(u_zwierzeta)
    st.query_params["u_fitness"] = str(u_fitness)
    st.query_params["u_bar"] = str(u_bar)
    st.query_params["u_restauracja"] = str(u_restauracja)
    st.query_params["u_transfer"] = str(u_transfer)
    st.query_params["u_wozki"] = str(u_wozki)
    st.query_params["u_niepalacy"] = str(u_niepalacy)
    st.query_params["u_pralnia"] = str(u_pralnia)
    st.query_params["u_balkon"] = str(u_balkon)
    st.query_params["u_lozeczko"] = str(u_lozeczko)
    st.query_params["u_winda"] = str(u_winda)
    st.query_params["u_basen"] = str(u_basen)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Wyczyść filtry", width='stretch'):
        klucze_filtrow = [
            "sort", "cena_min", "cena_max", "f_hotel", "f_apartament", "f_b_and_b", 
            "f_schronisko", "f_wynajem", "f_p_darmowy", "f_p_platny", "f_p_brak",
            "u_klimatyzacja", "u_przyjazny_dzieciom", "u_kuchnia", "u_wifi", "u_sniadanie",
            "u_zwierzeta", "u_fitness", "u_bar", "u_restauracja", "u_transfer", "u_wozki",
            "u_niepalacy", "u_pralnia", "u_balkon", "u_lozeczko", "u_winda", "u_basen",
            "pogoda",
        ]
        for klucz in klucze_filtrow:
            if klucz in st.query_params: del st.query_params[klucz]
        st.session_state.filters_version += 1
        st.session_state.saved_filters = {}
        st.session_state.aktywna_pogoda = []  # czyścimy też zatwierdzony filtr pogodowy
        st.rerun()

st.session_state.saved_filters = {
    "sort": sort_option, "cena_min": cena_min, "cena_max": cena_max,
    "f_hotel": f_hotel, "f_apartament": f_apartament, "f_b_and_b": f_b_and_b,
    "f_schronisko": f_schronisko, "f_wynajem": f_wynajem, "f_p_darmowy": f_p_darmowy,
    "f_p_platny": f_p_platny, "f_p_brak": f_p_brak, "u_klimatyzacja": u_klimatyzacja,
    "u_przyjazny_dzieciom": u_przyjazny_dzieciom, "u_kuchnia": u_kuchnia, "u_wifi": u_wifi,
    "u_sniadanie": u_sniadanie, "u_zwierzeta": u_zwierzeta, "u_fitness": u_fitness,
    "u_bar": u_bar, "u_restauracja": u_restauracja, "u_transfer": u_transfer,
    "u_wozki": u_wozki, "u_niepalacy": u_niepalacy, "u_pralnia": u_pralnia,
    "u_balkon": u_balkon, "u_lozeczko": u_lozeczko, "u_winda": u_winda, "u_basen": u_basen,
    "pogoda": ",".join(wybrane_kategorie_pogody),
}

with panel_wynikow:
    st.markdown("""
    <style>
    div[class*="st-key-title_btn_"] button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: inherit !important;
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        padding: 0 !important;
        margin: 0 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        line-height: 1.2 !important;
    }
    div[class*="st-key-title_btn_"] button:hover {
        color: #ff4b4b !important;
        text-decoration: underline !important;
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Budowanie zapytania SQL
    where_clauses = ["n.maks_liczba_osob >= :osoby"]
    sql_params = {"osoby": st.session_state.search_osoby}
    
    if st.session_state.search_miejsce.strip():
        where_clauses.append("n.lokalizacja_miasto LIKE :miasto")
        sql_params["miasto"] = f"%{st.session_state.search_miejsce.strip()}%"
        
    where_clauses.append("n.cena_za_noc BETWEEN :cena_min AND :cena_max")
    sql_params["cena_min"] = cena_min
    sql_params["cena_max"] = cena_max
    
    wybrane_typy = []
    if f_hotel: wybrane_typy.append('Hotel')
    if f_apartament: wybrane_typy.append('Apartament')
    if f_b_and_b: wybrane_typy.append('B&B')
    if f_schronisko: wybrane_typy.append('Schronisko')
    if f_wynajem: wybrane_typy.append('Wynajem wakacyjny')

    if wybrane_typy:
        type_clauses = []
        for idx, t in enumerate(wybrane_typy):
            param_key = f"type_{idx}"
            type_clauses.append(f":{param_key}")
            sql_params[param_key] = t
        where_clauses.append(f"n.typ_obiektu IN ({', '.join(type_clauses)})")

    # --- ZMIANA: NOWA LOGIKA MAPOWANIA ID UDOGODNIEŃ ---
    if u_klimatyzacja:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia IN (1, 12))")
    if u_przyjazny_dzieciom:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia IN (2, 19))")
    if u_kuchnia:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia IN (4, 23, 44, 5, 6))")
    if u_wifi:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia IN (8, 10, 22, 49))")
    if u_sniadanie:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia IN (9, 21, 40))")
    if u_zwierzeta:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia IN (13, 25))")
    if u_fitness:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia = 14)")
    if u_bar:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia = 15)")
    if u_restauracja:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia = 16)")
    if u_transfer:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia IN (17, 43))")
    if u_wozki:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia IN (18, 47))")
    if u_niepalacy:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia IN (20, 26))")
    if u_pralnia:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia IN (27, 37))")
    if u_balkon:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia = 29)")
    if u_lozeczko:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia = 30)")
    if u_winda:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia = 31)")
    if u_basen:
        where_clauses.append("EXISTS (SELECT 1 FROM noclegi_udogodnienia nu WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia IN (32, 36, 46, 50))")

    # --- LOGIKA FILTROWANIA PARKINGU ---
    parking_conditions = []

    if f_p_darmowy:
        # Sprawdzamy czy przypisane jest id_udogodnienia = 24
        parking_conditions.append("""
            EXISTS (
                SELECT 1 FROM noclegi_udogodnienia nu 
                WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia = 24
            )
        """)

    if f_p_platny:
        # Sprawdzamy czy przypisane jest id_udogodnienia = 28
        parking_conditions.append("""
            EXISTS (
                SELECT 1 FROM noclegi_udogodnienia nu 
                WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia = 28
            )
        """)

    if f_p_brak:
        # Sprawdzamy czy obiekt NIE POSIADA ani darmowego (24), ani płatnego (28)
        parking_conditions.append("""
            NOT EXISTS (
                SELECT 1 FROM noclegi_udogodnienia nu 
                WHERE nu.id_noclegu = n.id_noclegu AND nu.id_udogodnienia IN (24, 28)
            )
        """)

    # Jeśli użytkownik zaznaczył jakiekolwiek opcje parkingu, łączymy je warunkiem OR
    # (np. jeśli zaznaczył darmowy LUB płatny, to chcemy pokazać oba typy)
    if parking_conditions:
        where_clauses.append(f"({ ' OR '.join(parking_conditions) })")
    # -------------------------------------
    

    if sort_option == "od najtańszych": order_by = "n.cena_za_noc ASC"
    elif sort_option == "od najdroższych": order_by = "n.cena_za_noc DESC"
    else: order_by = "n.srednia_ocena DESC"

    query_szukaj = f"""
    SELECT 
        n.id_noclegu, n.nazwa, n.lokalizacja_miasto, n.lokalizacja_adres, n.opis, n.cena_za_noc, n.srednia_ocena,
        n.szerokosc_geo, n.dlugosc_geo,
        (SELECT TOP 1 url_zdjecia FROM zdjecia_noclegu WHERE id_noclegu = n.id_noclegu ORDER BY czy_glowne DESC) AS url_zdjecia
    FROM noclegi n
    WHERE {" AND ".join(where_clauses)}
    ORDER BY {order_by}
    """
    
    try:
        df_wyniki = conn.query(query_szukaj, params=sql_params, ttl=0)

        # filtrowanie wyników po pogodzie
        if not df_wyniki.empty and wybrane_kategorie_pogody:
            data_od_iso = str(st.session_state.search_data_od)
            data_do_iso = str(st.session_state.search_data_do)

            # cache wyników per-miasto w obrębie tego przebiegu strony, żeby nie sprawdzać tego samego miasta wielokrotnie
            wynik_pogody_per_miasto = {}

            def sprawdz_wiersz(miasto):
                if miasto not in wynik_pogody_per_miasto:
                    wynik_pogody_per_miasto[miasto] = miasto_spelnia_kategorie(
                        miasto, data_od_iso, data_do_iso, wybrane_kategorie_pogody
                    )
                return wynik_pogody_per_miasto[miasto]

            with st.spinner("Sprawdzam prognozę pogody dla wyników..."):
                maska_pogody = df_wyniki["lokalizacja_miasto"].apply(sprawdz_wiersz)
            df_wyniki = df_wyniki[maska_pogody]

        if df_wyniki.empty:
            st.info("Brak dostępnych ofert dla wybranych kryteriów.")
        else:
            search_map = build_search_map(df_wyniki)
            
            if search_map:
                with sidebar_map_container:
                    st.markdown("#### Lokalizacja ofert")
                    folium_static(search_map, width='Stretch', height=280)
                    st.markdown("---")
            
            for _, row in df_wyniki.iterrows():
                card = st.container(border=True)
                with card:
                    col_img, col_detale = st.columns([1.2, 2.5])
                    
                    with col_img:
                        if row['url_zdjecia']:
                            foto_ready = wyswietl_zdjecie(row['url_zdjecia'], szerokosc=400, wysokosc=300)
                            if foto_ready:
                                st.image(foto_ready, width='stretch')
                            else:
                                st.markdown("<div class='surface-block' style='height: 160px;'></div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div class='surface-block' style='height: 160px;'></div>", unsafe_allow_html=True)
                            
                    with col_detale:
                        # Górna część: tytuł + ocena
                        c_title, c_rating = st.columns([2.8, 1.2])
                        with c_title:
                            kliknieto_tytul = st.button(row['nazwa'], key=f"title_btn_{row['id_noclegu']}")
                            st.markdown(f"""
                            <div style='color: #767676; font-size: 0.85rem; margin-top:-16px; margin-bottom: 10px;'>
                                {row['lokalizacja_adres']}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with c_rating:
                            ocena_val = row['srednia_ocena']
                            if pd.isna(ocena_val) or ocena_val is None:
                                ocena_html = "<span style='color: #767676; font-size: 15px;'>Brak ocen</span>"
                            else:
                                f_ocena = float(ocena_val)
                                str_ocena = f"{f_ocena:.1f}" if f_ocena % 1 != 0 else f"{int(f_ocena)}"
                                ocena_html = f"⭐ {str_ocena}/5"
                            
                            st.markdown(f"""
                                <div style="display: flex; justify-content: flex-end; align-items: center; margin-top: 4px;">
                                    <div class='rating-chip' style='margin: 0; font-size: 20px; font-weight: bold; line-height: 1;'>
                                        {ocena_html}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # Opis + cena/przycisk w jednym bloku HTML – daje pełną kontrolę nad layoutem
                        opis_skrocony = row['opis'] if row['opis'] else "Brak opisu obiektu."
                        if len(opis_skrocony) > 180:
                            wycinek = opis_skrocony[:200]
                            ostatnia_spacja = wycinek.rfind(' ')
                            if ostatnia_spacja != -1:
                                wycinek = wycinek[:ostatnia_spacja]
                            opis_skrocony = wycinek.rstrip('.,; ') + "..."

                        cena_za_noc = row['cena_za_noc']
                        liczba_nocy = (st.session_state.search_data_do - st.session_state.search_data_od).days
                        liczba_nocy = max(1, liczba_nocy)
                        cena_calkowita = int(cena_za_noc) * liczba_nocy

                        st.markdown(f"""
                        <div style='overflow-wrap:break-word; word-break:break-word; font-size:0.92rem; line-height:1.5;'>
                            {opis_skrocony}
                        </div>
                        """, unsafe_allow_html=True)

                        # Wypełniacz - rozpycha przestrzeń w górę
                        st.markdown("<div style='min-height: 5rem;'></div>", unsafe_allow_html=True)

                        _, c_btn = st.columns([3, 1])
                        with c_btn:
                            st.markdown(f"""
                            <div style='text-align:right; line-height:1.1; margin-bottom:8px;'>
                                <span style='font-size:2rem; font-weight:bold;'>{cena_calkowita} zł</span><br>
                                <span style='font-size:0.9rem; color:#767676;'>{int(cena_za_noc)} zł za noc</span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            kliknieto_przycisk = st.button(
                                "Szczegóły",
                                key=f"btn_{row['id_noclegu']}",
                                use_container_width=True,
                                type="primary"
                            )
                    
                    if kliknieto_tytul or kliknieto_przycisk:
                        st.session_state.selected_nocleg_id = row['id_noclegu']
                        st.query_params["id"] = str(row['id_noclegu']) 
                        st.switch_page("pages/strona_noclegu.py")
                                        
    except Exception as e:
        st.error(f"Nie udało się załadować ofert. Błąd: {e}")

render_page_footer()
