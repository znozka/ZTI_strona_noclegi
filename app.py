import datetime
import streamlit as st
import extra_streamlit_components as stx  
from src.ui import render_page_header, render_page_footer


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

miejsce_sesja = st.session_state.get("search_miejsce", "")

if miejsce_sesja in lista_miast and miejsce_sesja != "":
    domyslny_indeks = lista_miast.index(miejsce_sesja)
else:
    domyslny_indeks = None 

st.title("Witaj w InnSight")
if st.session_state.get("user_name"):
    st.markdown(f"### Witaj, {st.session_state.user_name}! Dokąd wybierasz się tym razem?")
else:
    st.markdown("### Witaj! Dokąd wybierasz się tym razem?")

search_container = st.container(border=True)
with search_container:
    c1, c2, c3, c4, c5 = st.columns([2.5, 1.2, 1.2, 1.2, 1])

    with c1:
        miejsce_input = st.selectbox(
            "Miejsce",
            options=lista_miast,
            index=domyslny_indeks,
            placeholder="Wpisz miasto...",
            label_visibility="visible",
        )
    with c2:
        data_od_input = st.date_input(
            "Data od",
            value=st.session_state.get("search_data_od", datetime.date.today()),
        )
    with c3:
        data_do_input = st.date_input(
            "Data do",
            value=st.session_state.get("search_data_do", datetime.date.today() + datetime.timedelta(days=2)),
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
            st.image(city["file"], width='stretch')
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
        st.image(new_cities[0]["file"], width='stretch')
        st.markdown(
            f"<div style='text-align: center; font-weight: bold; padding: 5px;'>{new_cities[0]['name']}</div>",
            unsafe_allow_html=True,
        )

with cols_new_dest[1]:
    with st.container(border=True):
        st.image(new_cities[1]["file"], width='stretch')
        st.markdown(
            f"<div style='text-align: center; font-weight: bold; padding: 5px;'>{new_cities[1]['name']}</div>",
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

render_page_footer()
