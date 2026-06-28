import datetime
import urllib.parse
import base64
import mimetypes
import streamlit as st
import extra_streamlit_components as stx  
from src.ui import render_page_header, render_page_footer
from src.utils import generuj_plan_wycieczki_ai


MAPA_ZDJEC = {
    "Gdańsk": "assets/images/Gdańsk.jpg",
    "Kraków": "assets/images/Kraków.jpeg",
    "Warszawa": "assets/images/Warszawa.jpeg",
    "Wrocław": "assets/images/Wrocław.jpg",
    "Poznań": "assets/images/Poznań.jpg",
    "Łódź": "assets/images/Łódź.png",
    "Katowice": "assets/images/Katowice.jpg"
}

st.set_page_config(
    page_title="InnSight",
    page_icon="assets/images/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# KROK A: Jeśli użytkownik przyszedł ze strony logowania, "upiecz" ciasteczka na poziomie głównej ścieżki (/)
if st.session_state.get("needs_cookie_save"):
    cookie_manager = stx.CookieManager(key="root_cookie_saver")
    cookie_manager.set("user_id", str(st.session_state.user_id), max_age=86400, key="rc_uid")
    cookie_manager.set("user_name", st.session_state.user_name, max_age=86400, key="rc_uname")
    cookie_manager.set("user_role", st.session_state.user_role, max_age=86400, key="rc_urole")
    st.session_state["needs_cookie_save"] = False  # Oznacz jako wykonane, aby nie zapętlać

# KROK B: Automatyczne odbudowanie sesji z ciasteczek (Nie zmieniać!)
if "user_id" not in st.session_state and not st.session_state.get("going_to_login"):
    cookie_uid = st.context.cookies.get("user_id")
    cookie_name = st.context.cookies.get("user_name")
    cookie_role = st.context.cookies.get("user_role")

    if (
        cookie_uid
        and cookie_uid not in ["None", ""]
        and cookie_name
        and cookie_name not in ["None", ""]
    ):
        st.session_state.user_id = cookie_uid
        st.session_state.user_name = cookie_name
        st.session_state.user_role = cookie_role
        st.rerun()

render_page_header()

conn = st.connection("azure_sql", type="sql")

@st.cache_data(ttl=3600)
def pobierz_unikalne_miasta():
    try:
        df_miasta = conn.query(
            "SELECT DISTINCT lokalizacja_miasto FROM noclegi WHERE lokalizacja_miasto IS NOT NULL ORDER BY lokalizacja_miasto",
            ttl=0,
        )
        return df_miasta["lokalizacja_miasto"].tolist()
    except Exception:
        return ["Gdańsk", "Kraków", "Katowice", "Poznań", "Warszawa", "Wrocław", "Łódź"]

lista_miast = pobierz_unikalne_miasta()


def _make_clickable_image(path, href):
    """Return HTML for an image wrapped in a link, embedding the image as base64."""
    try:
        mime, _ = mimetypes.guess_type(path)
        with open(path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        src = f"data:{mime};base64,{b64}" if mime else f"data:image/png;base64,{b64}"
        return f"<a href='{href}'><img src='{src}' style='width:100%; height:auto; display:block;'/></a>"
    except Exception:
        # fallback to simple img tag if reading fails
        return f"<a href='{href}'><img src='{path}' style='width:100%; height:auto; display:block;'/></a>"

miejsce_sesja = st.session_state.get("search_miejsce", "")

if miejsce_sesja in lista_miast and miejsce_sesja != "":
    domyslny_indeks = lista_miast.index(miejsce_sesja)
else:
    domyslny_indeks = None 

# Jeśli kliknięto link z parametrem (np. kliknięcie obrazu), ustaw parametry i przekieruj
params = st.query_params if hasattr(st, "query_params") else {}

def _first(v):
    if isinstance(v, list):
        return v[0] if v else ""
    return v

clicked = _first(params.get("clicked"))
miejsce_param = _first(params.get("miejsce"))
if clicked == "True" and miejsce_param:
    st.session_state.search_clicked = True
    st.session_state.search_miejsce = miejsce_param
    try:
        osoby_val = _first(params.get("osoby"))
        st.session_state.search_osoby = int(osoby_val) if osoby_val else st.session_state.get("search_osoby", 2)
    except Exception:
        st.session_state.search_osoby = st.session_state.get("search_osoby", 2)

    try:
        dod = _first(params.get("data_od")) or str(datetime.date.today())
        ddo = _first(params.get("data_do")) or str(datetime.date.today() + datetime.timedelta(days=2))
        st.session_state.search_data_od = datetime.date.fromisoformat(dod)
        st.session_state.search_data_do = datetime.date.fromisoformat(ddo)
    except Exception:
        pass

    st.switch_page("pages/wyniki_wyszukiwania.py")

st.title("Witaj w InnSight")
if st.session_state.get("user_name"):
    st.markdown(f"### Witaj, {st.session_state.user_name}! Dokąd wybierasz się tym razem?")
else:
    st.markdown("### Witaj! Dokąd wybierasz się tym razem?")

search_container = st.container(border=True)
with search_container:
    c1, c2, c3, c4, c5 = st.columns([2.5, 1.2, 1.2, 1.2, 1])

    dzis = datetime.date.today()

    with c1:
        miejsce_input = st.selectbox(
            "Miejsce",
            options=lista_miast,
            index=domyslny_indeks,
            placeholder="Wpisz miasto...",
            label_visibility="visible",
        )
    with c2:
        start_val = st.session_state.get("search_data_od", dzis)
        if start_val < dzis:
            start_val = dzis
        data_od_input = st.date_input(
            "Data od",
            value=start_val,
            min_value=dzis
        )
    with c3:
        min_data_do = data_od_input + datetime.timedelta(days=1)

        end_val = st.session_state.get("search_data_do", dzis + datetime.timedelta(days=2))
        if end_val < min_data_do:
            end_val = min_data_do

        data_do_input = st.date_input(
            "Data do",
            value=end_val,
            min_value=min_data_do
        )
    with c4:
        osoby_input = st.number_input(
            "Liczba osób",
            min_value=1,
            max_value=20,
            value=st.session_state.get("search_osoby", 2),
        )
    with c5:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Szukaj", width='stretch', type="primary"):
            if data_od_input >= data_do_input:
                st.toast("Data wyjazdu musi być późniejsza niż data przyjazdu!", icon="⚠️")
            else:
                czyste_miejsce = miejsce_input if miejsce_input is not None else ""
                st.session_state.search_clicked = True
                st.session_state.search_miejsce = czyste_miejsce
                st.session_state.search_osoby = osoby_input
                st.session_state.search_data_od = data_od_input
                st.session_state.search_data_do = data_do_input
                st.query_params["miejsce"] = czyste_miejsce
                st.query_params["data_od"] = str(data_od_input)
                st.query_params["data_do"] = str(data_do_input)
                st.query_params["osoby"] = str(osoby_input)
                st.query_params["clicked"] = "True"
                if "id" in st.query_params:
                    del st.query_params["id"]
                st.switch_page("pages/wyniki_wyszukiwania.py")

st.markdown("---")

st.subheader("Polecane w tym miesiącu")
cols_recommended = st.columns(4)

recommended_cities = [
    {"name": "Gdańsk", "file": "assets/images/Gdańsk.jpg"},
    {"name": "Kraków", "file": "assets/images/Kraków.jpeg"},
    {"name": "Warszawa", "file": "assets/images/Warszawa.jpeg"},
    {"name": "Wrocław", "file": "assets/images/Wrocław.jpg"},
]

for i, col in enumerate(cols_recommended):
    city = recommended_cities[i]
    with col:
        with st.container(border=True):
            img_href = (
                f"?miejsce={urllib.parse.quote(city['name'])}"
                f"&data_od={str(st.session_state.get('search_data_od', datetime.date.today()))}"
                f"&data_do={str(st.session_state.get('search_data_do', datetime.date.today() + datetime.timedelta(days=2)))}"
                f"&osoby={st.session_state.get('search_osoby', 2)}&clicked=True"
            )
            st.markdown(_make_clickable_image(city['file'], img_href), unsafe_allow_html=True)
            st.markdown(
                f"<div style='text-align: center; font-weight: bold; padding: 5px;'>{city['name']}</div>",
                unsafe_allow_html=True,
            )

st.markdown("---")

st.subheader("Odkryj nowe kierunki")
cols_new_dest = st.columns(2)

new_cities = [
    {"name": "Poznań", "file": "assets/images/Poznań.jpg"},
    {"name": "Łódź", "file": "assets/images/Łódź.png"},
]

with cols_new_dest[0]:
    with st.container(border=True):
        img_href = (
            f"?miejsce={urllib.parse.quote(new_cities[0]['name'])}"
            f"&data_od={str(st.session_state.get('search_data_od', datetime.date.today()))}"
            f"&data_do={str(st.session_state.get('search_data_do', datetime.date.today() + datetime.timedelta(days=2)))}"
            f"&osoby={st.session_state.get('search_osoby', 2)}&clicked=True"
        )
        st.markdown(_make_clickable_image(new_cities[0]['file'], img_href), unsafe_allow_html=True)
        st.markdown(
            f"<div style='text-align: center; font-weight: bold; padding: 5px; font-size: 1.3rem'>{new_cities[0]['name']}</div>",
            unsafe_allow_html=True,
        )

with cols_new_dest[1]:
    with st.container(border=True):
        img_href = (
            f"?miejsce={urllib.parse.quote(new_cities[1]['name'])}"
            f"&data_od={str(st.session_state.get('search_data_od', datetime.date.today()))}"
            f"&data_do={str(st.session_state.get('search_data_do', datetime.date.today() + datetime.timedelta(days=2)))}"
            f"&osoby={st.session_state.get('search_osoby', 2)}&clicked=True"
        )
        st.markdown(_make_clickable_image(new_cities[1]['file'], img_href), unsafe_allow_html=True)
        st.markdown(
            f"<div style='text-align: center; font-weight: bold; padding: 5px; font-size: 1.3rem'>{new_cities[1]['name']}</div>",
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

def pobierz_ostatni_wyjazd(user_name):
    try:
        query = """
            SELECT TOP 1 n.lokalizacja_miasto 
            FROM rezerwacje r
            INNER JOIN noclegi n ON r.id_noclegu = n.id_noclegu
            INNER JOIN uzytkownicy u ON r.id_turysty = u.id_uzytkownika
            WHERE u.imie = :user_name 
            ORDER BY r.data_wymeldowania DESC
        """
        df_ostatni = conn.query(query, params={"user_name": user_name}, ttl=0)
        
        if not df_ostatni.empty:
            return df_ostatni.iloc[0]["lokalizacja_miasto"]
        return None
    except Exception as e:
        st.error(f"Błąd SQL: {e}")
        return None

if st.session_state.get("user_name"):
    ostatnie_miasto = pobierz_ostatni_wyjazd(st.session_state.user_name)
    
    if ostatnie_miasto:
        st.markdown("---")
        st.subheader("Twój ostatni wyjazd z nami")
        
        sciezka_zdjecia = MAPA_ZDJEC.get(ostatnie_miasto)
        
        last_trip_box = st.container(border=True)
        with last_trip_box:
            col_last_img, col_last_txt = st.columns([1, 3])
            with col_last_img:
                st.image(sciezka_zdjecia, width='stretch')
            with col_last_txt:
                st.markdown(
                    f"<div style='padding-top: 10px; font-size: 1.5rem;'><b>{ostatnie_miasto}</b><br>"
                    f"<div style='padding-top: 10px; font-size: 1rem;'>Wyjazd udany? Podziel się swoimi wrażeniami z pobytu!</div>",
                    unsafe_allow_html=True,
                )

def generuj_plan_wycieczki(destination, origin, start_date, end_date, trip_type):
    days = (end_date - start_date).days + 1
    trip_type = trip_type or "City Break"

    city_acts = {
        "Gdańsk": {
            "city break": [
                ("Spacer po Starym Mieście", "2 godz., zwiedzanie Długiego Targu, Fontanna Neptuna i Bazylika Mariacka"),
                ("Wizyta w Europejskim Centrum Solidarności", "1.5 godz., wystawy i historia"),
                ("Rejs po Motławie", "1 godz., trasa wzdłuż nabrzeża")
            ],
            "przyroda": [
                ("Plaża Brzeźno", "3 godz., spacer i odpoczynek nad morzem"),
                ("Oliwski Park", "2 godz., ogród zoologiczny i katedra"),
                ("Wyspa Sobieszewska", "cały dzień, rezerwat przyrody i ptaki")
            ]
        },
        "Kraków": {
            "city break": [
                ("Rynek Główny", "2 godz., Sukiennice, Wieża Ratuszowa i Kościół Mariacki"),
                ("Zamek Królewski na Wawelu", "2.5 godz., komnaty i katedra"),
                ("Kazimierz", "2 godz., żydowskie zabytki i kawiarnie")
            ],
            "przyroda": [
                ("Ojcowski Park Narodowy", "4 godz., zamek, Maczuga Herkulesa i Jaskinia Łokietka"),
                ("Kopiec Kościuszki", "1.5 godz., panorama Krakowa"),
                ("Las Wolski", "2 godz., spacer i zwiedzanie Zoo")
            ]
        },
    }

    fallback_city = {
        "city break": [
            ("Spacer po centrum", "2 godz., główne atrakcje i lokalne kawiarnie"),
            ("Muzeum lub galeria", "2 godz., wystawa regionalna"),
            ("Kolacja w lokalnej restauracji", "1.5 godz.")
        ],
        "przyroda": [
            ("Park lub rezerwat", "3 godz., trasa przyrodnicza"),
            ("Piknik na łonie natury", "2 godz."),
            ("Punkt widokowy", "1 godz.")
        ]
    }

    typ = trip_type.lower()
    typ_key = "przyroda" if "przyroda" in typ else "city break"
    destination_info = city_acts.get(destination, city_acts.get("Gdańsk", {}))
    activities = destination_info.get(typ_key, fallback_city[typ_key])

    route = f"Dojazd ze {origin} do {destination}."
    if origin and origin.lower() != destination.lower():
        route += " Najszybsza opcja to pociąg lub samochód, w zależności od dostępności połączeń."
        route += " Przykładowo: dworzec główny do centrum miasta w 20-40 minut." if typ_key == "city break" else " Przykładowo: trasa do parku narodowego lub rezerwatu zajmuje około 30-60 minut." 
    else:
        route += " Zakładamy wyjazd z Twojej lokalnej okolicy do centrum miasta."

    plan = [f"# Plan wycieczki AI: {destination}",
            f"**Typ wycieczki:** {trip_type}",
            f"**Termin:** {start_date} – {end_date} ({days} dni)",
            f"**Trasa:** {route}",
            "---",
            "## Co możesz robić"]

    for i in range(min(days, len(activities))):
        activity = activities[i]
        plan.append(f"### Dzień {i+1}: {activity[0]}")
        plan.append(f"- Szacowany czas: {activity[1]}")
        plan.append(f"- Polecane godziny: {10 + i*2}:00 – {12 + i*2}:00")

    if days > len(activities):
        plan.append("### Dodatkowy dzień")
        plan.append("- Zarezerwuj czas na relaks, kawę w lokalnej kawiarni i krótki spacer.")

    plan.append("---")
    plan.append("## Dodatkowe wskazówki")
    plan.append("- Sprawdź lokalne rozkłady jazdy lub bilety online przed wyjazdem.")
    plan.append("- Weź pod uwagę czas na transfery oraz odpoczynek między atrakcjami.")
    plan.append("- Jeśli jedziesz autem, zostaw miejsce w samochodzie na pamiątki.")

    return "\n".join(plan)


st.markdown("---")
st.subheader("Zaplanuj swoją wycieczkę z pomocą AI")
with st.container(border=True):
    st.markdown(
        "Skorzystaj z naszego pomocnika AI do planowania wycieczek! Wybierz miejsce, daty oraz rodzaj wycieczki, a nasz asystent AI przygotuje przykładowy plan: co robić, jak dojechać i ile będzie trwać każda atrakcja. Generowanie planu zajmie dłuższą chwilę",
    )

    c1, c2, c3, c4 = st.columns([1.8, 1.3, 1.3, 1.6])
    with c1:
        ai_origin = st.text_input("Skąd jedziesz?", value="Warszawa", placeholder="np. Warszawa", key="ai_origin")
    with c2:
        ai_destination = st.selectbox(
            "Cel podróży",
            options=lista_miast,
            index=domyslny_indeks if domyslny_indeks is not None else 0,
            label_visibility="visible",
            key="ai_destination"
        )
    with c3:
        ai_start_date = st.date_input("Data od", value=dzis, min_value=dzis, key="ai_start_date")
    with c4:
        min_end = ai_start_date + datetime.timedelta(days=1)
        ai_end_date = st.date_input("Data do", value=ai_start_date + datetime.timedelta(days=2), min_value=min_end, key="ai_end_date")

    ai_type = st.selectbox(
        "Rodzaj wycieczki",
        options=["City Break", "Wycieczka na łono przyrody", "Relaks i wellness", "Kulturalna", "Aktywna"],
        index=0,
        key="ai_trip_type"
    )

    if st.button("Zaproponuj plan wycieczki", type="primary"):
        if ai_start_date >= ai_end_date:
            st.toast("Data końcowa musi być późniejsza niż data początkowa.", icon="⚠️")
        else:
            plan = generuj_plan_wycieczki_ai(ai_destination, ai_origin, ai_start_date, ai_end_date, ai_type)
            if not plan:
                if st.session_state.get("openai_api_source"):
                    st.error(
                        f"AI jest niedostępne. Pobierono klucz z {st.session_state['openai_api_source']}, ale wystąpił błąd: {st.session_state.get('openai_error')}"
                    )
                else:
                    st.warning(
                        "AI jest niedostępne. Dodaj prawidłowy klucz OpenAI lub Hugging Face do pliku `.streamlit/secrets.toml` lub ustaw odpowiednią zmienną środowiskową."
                    )
                    st.info(
                        "Przykład formatu pliku `.streamlit/secrets.toml`:\n```\n[openai]\napi_key = \"TWÓJ_OPENAI_API_KEY\"\n```"
                    )
                plan = generuj_plan_wycieczki(ai_destination, ai_origin, ai_start_date, ai_end_date, ai_type)
            else:
                st.success("Plan wygenerowany przez AI.")

            with st.expander("Pokaż plan wycieczki"):
                st.markdown(
                    "<style>"
                    ".stExpander div[data-testid='stMarkdownContainer'] { font-size: 0.88rem !important; line-height: 1.45 !important; }"
                    "</style>",
                    unsafe_allow_html=True,
                )
                st.markdown(plan)

render_page_footer()
