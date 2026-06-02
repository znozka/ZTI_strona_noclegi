import streamlit as st
import datetime
from src.ui import render_page_header, render_page_footer

# Ustawienia strony
st.set_page_config(
    page_title="Wyniki wyszukiwania",
    page_icon="assets/images/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header()

conn = st.connection("azure_sql", type="sql")

# Dynamiczne pobieranie unikalnych miast z bazy danych z cache na 1 godzinę
@st.cache_data(ttl=3600)
def pobierz_unikalne_miasta():
    try:
        df_miasta = conn.query("SELECT DISTINCT lokalizacja_miasto FROM noclegi WHERE lokalizacja_miasto IS NOT NULL ORDER BY lokalizacja_miasto", ttl=0)
        return df_miasta["lokalizacja_miasto"].tolist()
    except Exception:
        # Lista ratunkowa, jeśli baza nie odpowie
        return ["Gdańsk", "Kraków", "Katowice", "Poznań", "Warszawa", "Wrocław", "Łódź"]

lista_miast = pobierz_unikalne_miasta()

# Określenie domyślnego indeksu dla selectboxa na bazie adresu URL / session_state
domyslny_indeks = None
if st.session_state.get("search_miejsce") in lista_miast:
    domyslny_indeks = lista_miast.index(st.session_state.search_miejsce)

# Odczyt i parsowanie danych z url
url_miejsce = st.query_params.get("miejsce", st.session_state.get("search_miejsce", ""))
url_data_od = st.query_params.get("data_od", None)
url_data_do = st.query_params.get("data_do", None)
url_osoby = st.query_params.get("osoby", None)
url_clicked = st.query_params.get("clicked", None)

# Parsowanie daty "od"
if url_data_od:
    try: st.session_state.search_data_od = datetime.date.fromisoformat(url_data_od)
    except ValueError: st.session_state.search_data_od = datetime.date.today()
else:
    st.session_state.search_data_od = st.session_state.get("search_data_od", datetime.date.today())

# Parsowanie daty "do"
if url_data_do:
    try: st.session_state.search_data_do = datetime.date.fromisoformat(url_data_do)
    except ValueError: st.session_state.search_data_do = datetime.date.today() + datetime.timedelta(days=2)
else:
    st.session_state.search_data_do = st.session_state.get("search_data_do", datetime.date.today() + datetime.timedelta(days=2))

# Liczba osób
if url_osoby is not None:
    try: url_osoby = int(url_osoby)
    except ValueError: url_osoby = 2
else:
    url_osoby = st.session_state.get("search_osoby", 2)

# Czy kliknięto szukaj
if url_clicked is not None:
    url_clicked = url_clicked == "True"
else:
    url_clicked = st.session_state.get("search_clicked", False)

st.session_state.search_miejsce = url_miejsce
st.session_state.search_osoby = url_osoby
st.session_state.search_clicked = url_clicked

# Inicjalizacja wersji filtrów bocznych (zapobiega zacinaniu się widgetów)
if "filters_version" not in st.session_state:
    st.session_state.filters_version = 0
version = st.session_state.filters_version

# Słownik domyślnych wartości dla filtrów bocznych (pobierany z URL)
url_filters = {
    "sort": st.query_params.get("sort", "od najtańszych"),
    "cena_min": int(st.query_params.get("cena_min", "0")) if st.query_params.get("cena_min", "").isdigit() else 0,
    "cena_max": int(st.query_params.get("cena_max", "2000")) if st.query_params.get("cena_max", "").isdigit() else 2000,
    "f_hotel": st.query_params.get("f_hotel", "False") == "True",
    "f_apartament": st.query_params.get("f_apartament", "False") == "True",
    "f_b_and_b": st.query_params.get("f_b_and_b", "False") == "True",
    "f_schronisko": st.query_params.get("f_schronisko", "False") == "True",
    "f_wynajem": st.query_params.get("f_wynajem", "False") == "True",
    "f_p_darmowy": st.query_params.get("f_p_darmowy", "False") == "True",
    "f_p_platny": st.query_params.get("f_p_platny", "False") == "True",
    "f_p_brak": st.query_params.get("f_p_brak", "False") == "True",
    "u_jacuzzi": st.query_params.get("u_jacuzzi", "False") == "True",
    "u_basen": st.query_params.get("u_basen", "False") == "True",
    "u_spa": st.query_params.get("u_spa", "False") == "True",
    "u_kuchnia": st.query_params.get("u_kuchnia", "False") == "True",
}

if not st.session_state.search_clicked:
    st.markdown(f"### Witaj! Dokąd się tym razem wybierasz?")

# Kontener na formularz wyszukiwania
search_container = st.container(border=True)
with search_container:
    c1, c2, c3, c4, c5 = st.columns([2.5, 1.2, 1.2, 1.2, 1])
    
    with c1:
        # Selectbox działający jako wyszukiwarka z autouzupełnianiem
        miejsce_input = st.selectbox(
            "Miejsce", 
            options=lista_miast,
            index=domyslny_indeks,
            placeholder="Wpisz miasto...", 
            label_visibility="visible"
        )
    with c2:
        data_od_input = st.date_input("Data od", value=st.session_state.search_data_od)
    with c3:
        data_do_input = st.date_input("Data do", value=st.session_state.search_data_do)
    with c4:
        osoby_input = st.number_input("Liczba osób", min_value=1, max_value=20, value=st.session_state.search_osoby)
    with c5:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Szukaj", width='stretch', type="primary"):
            # Ponieważ selectbox bez wyboru zwraca None, musimy to bezpiecznie zamienić na pusty string
            czyste_miejsce = miejsce_input if miejsce_input is not None else ""
            
            st.session_state.search_clicked = True
            st.session_state.search_miejsce = czyste_miejsce
            st.session_state.search_osoby = osoby_input
            st.session_state.search_data_od = data_od_input
            st.session_state.search_data_do = data_do_input

            # Zapis głównych filtrów do URL
            st.query_params["miejsce"] = czyste_miejsce
            st.query_params["data_od"] = str(data_od_input)
            st.query_params["data_do"] = str(data_do_input)
            st.query_params["osoby"] = str(osoby_input)
            st.query_params["clicked"] = "True"
            if "id" in st.query_params:
                del st.query_params["id"]

            st.rerun()

if not st.session_state.search_clicked:
    st.markdown("---")
    
    # Sekcja: Polecane w tym tygodniu (4 miejsca)
    st.subheader("Polecane w tym tygodniu")
    cols_recommended = st.columns(4)
    
    recommended_cities = [
        {"name": "Gdańsk", "file": "assets/images/Gdańsk.jpg"},
        {"name": "Kraków", "file": "assets/images/Kraków.jpeg"},
        {"name": "Warszawa", "file": "assets/images/Warszawa.jpeg"},
        {"name": "Wrocław", "file": "assets/images/Wrocław.jpg"}
    ]
    
    for i, col in enumerate(cols_recommended):
        city = recommended_cities[i]
        with col:
            with st.container(border=True):
                st.image(city["file"], width='stretch')
                st.markdown(f"<div style='text-align: center; font-weight: bold; padding: 5px;'>{city['name']}</div>", unsafe_allow_html=True)
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sekcja: Odkryj nowe kierunki (2 miejsca)
    st.subheader("Odkryj nowe kierunki")
    cols_new_dest = st.columns(2)
    
    new_cities = [
        {"name": "Poznań", "file": "assets/images/Poznań.jpg"},
        {"name": "Łódź", "file": "assets/images/Łódź.png"}
    ]
    
    with cols_new_dest[0]:
        with st.container(border=True):
            st.image(new_cities[0]["file"], width='stretch')
            st.markdown(f"<div style='text-align: center; font-weight: bold; padding: 5px;'>{new_cities[0]['name']}</div>", unsafe_allow_html=True)
            
    with cols_new_dest[1]:
        with st.container(border=True):
            st.image(new_cities[1]["file"], width='stretch')
            st.markdown(f"<div style='text-align: center; font-weight: bold; padding: 5px;'>{new_cities[1]['name']}</div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)

    # Sekcja: Twój ostatni wyjazd
    st.subheader("Twój ostatni wyjazd z nami:")
    last_trip_box = st.container(border=True)
    with last_trip_box:
        col_last_img, col_last_txt = st.columns([1, 3])
        with col_last_img:
            st.image("assets/images/Katowice.jpg", width='stretch')
        with col_last_txt:
            st.markdown("<div style='padding-top: 10px;'><b>Katowice</b><br>Wyjazd udany? Podziel się svoimi wrażeniami z pobytu w województwie śląskim!</div>", unsafe_allow_html=True)
            
    st.markdown("**Podziel się swoimi wrażeniami, napisz opinię!**")

else:
    panel_filtrow, panel_wynikow = st.columns([1, 3])
    
    with panel_filtrow:
        st.subheader("Sortuj")
        sort_options_list = ["od najtańszych", "od najdroższych", "najwyższa ocena"]
        try:
            sort_index = sort_options_list.index(url_filters["sort"])
        except ValueError:
            sort_index = 0

        sort_option = st.selectbox(
            "Sortuj według", 
            sort_options_list,
            index=sort_index,
            label_visibility="collapsed",
            key=f"sort_{version}"  # <-- DODANY KEY
        )
        st.query_params["sort"] = sort_option
        
        st.markdown("---")
        st.subheader("Filtruj") 
        
        st.write("**Cena za noc**")
        c_min, c_max = st.columns(2)
        with c_min:
            cena_min = st.number_input("Od", min_value=0, value=url_filters["cena_min"], step=50, key=f"cena_min_{version}") # <-- DODANY KEY
            st.query_params["cena_min"] = str(cena_min)
        with c_max:
            cena_max = st.number_input("Do", min_value=0, value=url_filters["cena_max"], step=50, key=f"cena_max_{version}") # <-- DODANY KEY
            st.query_params["cena_max"] = str(cena_max)
            
        st.markdown("---")
        st.write("**Rodzaj noclegu**")
        f_hotel = st.checkbox("Hotel", value=url_filters["f_hotel"], key=f"f_hotel_{version}") # <-- DODANY KEY
        f_apartament = st.checkbox("Apartament", value=url_filters["f_apartament"], key=f"f_apartament_{version}") # <-- DODANY KEY
        f_b_and_b = st.checkbox("B&B", value=url_filters["f_b_and_b"], key=f"f_b_and_b_{version}") # <-- DODANY KEY
        f_schronisko = st.checkbox("Schronisko", value=url_filters["f_schronisko"], key=f"f_schronisko_{version}") # <-- DODANY KEY
        f_wynajem = st.checkbox("Wynajem wakacyjny", value=url_filters["f_wynajem"], key=f"f_wynajem_{version}") # <-- DODANY KEY
        
        st.query_params["f_hotel"] = str(f_hotel)
        st.query_params["f_apartament"] = str(f_apartament)
        st.query_params["f_b_and_b"] = str(f_b_and_b)
        st.query_params["f_schronisko"] = str(f_schronisko)
        st.query_params["f_wynajem"] = str(f_wynajem)
        
        st.markdown("---")
        st.write("**Parking**")
        f_p_darmowy = st.checkbox("Darmowy", value=url_filters["f_p_darmowy"], key=f"f_p_darmowy_{version}") # <-- DODANY KEY
        f_p_platny = st.checkbox("Za dodatkową opłatą", value=url_filters["f_p_platny"], key=f"f_p_platny_{version}") # <-- DODANY KEY
        f_p_brak = st.checkbox("Brak", value=url_filters["f_p_brak"], key=f"f_p_brak_{version}") # <-- DODANY KEY
        
        st.query_params["f_p_darmowy"] = str(f_p_darmowy)
        st.query_params["f_p_platny"] = str(f_p_platny)
        st.query_params["f_p_brak"] = str(f_p_brak)
        
        st.markdown("---")
        st.write("**Udogodnienia**")
        u_jacuzzi = st.checkbox("Jacuzzi", value=url_filters["u_jacuzzi"], key=f"u_jacuzzi_{version}") # <-- DODANY KEY
        u_basen = st.checkbox("Basen", value=url_filters["u_basen"], key=f"u_basen_{version}") # <-- DODANY KEY
        u_spa = st.checkbox("Spa", value=url_filters["u_spa"], key=f"u_spa_{version}") # <-- DODANY KEY
        u_kuchnia = st.checkbox("Aneks kuchenny/kuchnia", value=url_filters["u_kuchnia"], key=f"u_kuchnia_{version}") # <-- DODANY KEY
        
        st.query_params["u_jacuzzi"] = str(u_jacuzzi)
        st.query_params["u_basen"] = str(u_basen)
        st.query_params["u_spa"] = str(u_spa)
        st.query_params["u_kuchnia"] = str(u_kuchnia)
        
        # Przycisk czyszczenia filtrów bocznych
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Wyczyść filtry", width='stretch'):
            klucze_filtrow = [
                "sort", "cena_min", "cena_max", 
                "f_hotel", "f_apartament", "f_b_and_b", "f_schronisko", "f_wynajem",
                "f_p_darmowy", "f_p_platny", "f_p_brak",
                "u_jacuzzi", "u_basen", "u_spa", "u_kuchnia"
            ]
            for klucz in klucze_filtrow:
                if klucz in st.query_params:
                    del st.query_params[klucz]
            
            # Zmiana wersji wymusi na Streamlit całkowite zresetowanie pamięci widgetów bocznym
            st.session_state.filters_version += 1
            st.rerun()

    with panel_wynikow:
        # Budowanie zapytania SQL na podstawie filtrów
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

        wybrane_udogodnienia = []
        if u_jacuzzi: wybrane_udogodnienia.append('Jacuzzi')
        if u_basen: wybrane_udogodnienia.append('Basen')
        if u_spa: wybrane_udogodnienia.append('Spa')
        if u_kuchnia: wybrane_udogodnienia.append('Aneks kuchenny/kuchnia')

        if wybrane_udogodnienia:
            for idx, u in enumerate(wybrane_udogodnienia):
                u_param = f"u_param_{idx}"
                sql_params[u_param] = u
                where_clauses.append(f"""
                    EXISTS (
                        SELECT 1 FROM noclegi_udogodnienia nu
                        JOIN udogodnienia ud ON nu.id_udogodnienia = ud.id_udogodnienia
                        WHERE nu.id_noclegu = n.id_noclegu AND ud.nazwa = :{u_param}
                    )
                """)

        if sort_option == "od najtańszych":
            order_by = "n.cena_za_noc ASC"
        elif sort_option == "od najdroższych":
            order_by = "n.cena_za_noc DESC"
        else:
            order_by = "n.srednia_ocena DESC"

        query_szukaj = f"""
        SELECT 
            n.id_noclegu,
            n.nazwa,
            n.lokalizacja_miasto,
            n.opis,
            n.cena_za_noc,
            n.srednia_ocena,
            (SELECT TOP 1 url_zdjecia FROM zdjecia_noclegu WHERE id_noclegu = n.id_noclegu ORDER BY czy_glowne DESC) AS url_zdjecia
        FROM noclegi n
        WHERE {" AND ".join(where_clauses)}
        ORDER BY {order_by}
        """
        
        try:
            df_wyniki = conn.query(query_szukaj, params=sql_params, ttl=0)
            
            if df_wyniki.empty:
                st.info("Brak dostępnych ofert dla wybranych kryteriów.")
            else:
                for _, row in df_wyniki.iterrows():
                    card = st.container(border=True)
                    with card:
                        col_img, col_detale = st.columns([1.2, 2.5])
                        
                        with col_img:
                            if row['url_zdjecia']:
                                st.image(row['url_zdjecia'], width='stretch')
                            else:
                                st.markdown(
                                    "<div class='surface-block' style='height: 160px;'></div>", 
                                    unsafe_allow_html=True
                                )
                                
                        with col_detale:
                            c_title, c_rating = st.columns([3, 1])
                            with c_title:
                                st.markdown(f"### {row['nazwa']}")
                                st.caption(f"{row['lokalizacja_miasto']}")
                            with c_rating:
                                st.markdown(
                                    f"<div class='rating-chip'>{row['srednia_ocena']}/5</div>", 
                                    unsafe_allow_html=True
                                )
                            
                            opis_skrócony = row['opis'] if row['opis'] else "Brak opisu obiektu."
                            if len(opis_skrócony) > 160:
                                opis_skrócony = opis_skrócony[:160] + "..."
                            st.write(opis_skrócony)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            c_space, c_price_btn = st.columns([2, 1])

                            with c_price_btn:
                                st.markdown(f"<div style='text-align: right; font-size: 1.4rem; ...'>{int(row['cena_za_noc'])} zł</div>", unsafe_allow_html=True)
                                
                                if st.button("Szczegóły", key=f"btn_{row['id_noclegu']}", width='stretch'):
                                    # 1. Zapisujemy w sesji
                                    st.session_state.selected_nocleg_id = row['id_noclegu']
                                    
                                    # 2. DOPISZ TO: Wstrzykujemy ID do parametrów URL przed skokiem na nową stronę
                                    st.query_params["id"] = str(row['id_noclegu'])
                                    
                                    # 3. Przełączamy stronę
                                    st.switch_page("pages/strona_noclegu.py")
                                    
        except Exception as e:
            st.error(f"Nie udało się załadować ofert. Błąd: {e}")

render_page_footer()
