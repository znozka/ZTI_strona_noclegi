import streamlit as st
import datetime
from src.ui import render_page_header, render_page_footer

# Ustawienia strony
st.set_page_config(
    page_title="Wyniki wyszukiwania - InnSight",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_page_header()

conn = st.connection("azure_sql", type="sql")

# Inicjalizacja stanów wyszukiwania w session_state
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False
if "search_miejsce" not in st.session_state:
    st.session_state.search_miejsce = ""
if "search_osoby" not in st.session_state:
    st.session_state.search_osoby = 2

if not st.session_state.search_clicked:
    user_name = st.session_state.get("user_name", "Ania")
    st.markdown(f"### Witaj, {user_name}. Dokąd się tym razem wybierasz?")

# Kontener na formularz wyszukiwania (ramka wokół wyszukiwarki)
search_container = st.container(border=True)
with search_container:
    c1, c2, c3, c4, c5 = st.columns([2.5, 1.2, 1.2, 1.2, 1])
    
    with c1:
        miejsce_input = st.text_input(
            "Miejsce", 
            placeholder="Wpisz miasto...", 
            value=st.session_state.search_miejsce,
            label_visibility="visible"
        )
    with c2:
        data_od_input = st.date_input("Data od", value=datetime.date.today())
    with c3:
        data_do_input = st.date_input("Data do", value=datetime.date.today() + datetime.timedelta(days=2))
    with c4:
        osoby_input = st.number_input("Liczba osób", min_value=1, max_value=20, value=st.session_state.search_osoby)
    with c5:
        # Wyrównanie przycisku do linii z inputami
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Szukaj", use_container_width=True, type="primary"):
            st.session_state.search_clicked = True
            st.session_state.search_miejsce = miejsce_input
            st.session_state.search_osoby = osoby_input
            st.rerun()

if not st.session_state.search_clicked:
    st.markdown("---")
    
    # Sekcja: Polecane w tym tygodniu (4 miejsca)
    st.subheader("Polecane w tym tygodniu")
    cols_recommended = st.columns(4)
    
    # Lista miast do sekcji "Polecane" (Zmień nazwy lub kolejność według uznania)
    recommended_cities = [
        {"name": "Gdańsk", "file": "zdj/Gdańsk.jpg"},
        {"name": "Kraków", "file": "zdj/Kraków.jpg"},
        {"name": "Warszawa", "file": "zdj/Warszawa.jpg"},
        {"name": "Wrocław", "file": "zdj/Wrocław.jpg"}
    ]
    
    for i, col in enumerate(cols_recommended):
        city = recommended_cities[i]
        with col:
            with st.container(border=True):
                # Wyświetlamy zdjęcie dopasowane do szerokości kontenera
                st.image(city["file"], width='stretch')
                st.markdown(f"<div style='text-align: center; font-weight: bold; padding: 5px;'>{city['name']}</div>", unsafe_allow_html=True)
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sekcja: Odkryj nowe kierunki (2 miejsca)
    st.subheader("Odkryj nowe kierunki")
    cols_new_dest = st.columns(2)
    
    # Lista miast do sekcji "Nowe kierunki"
    new_cities = [
        {"name": "Poznań", "file": "zdj/Poznań.jpg"},
        {"name": "Łódź", "file": "zdj/Łódź.png"}
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
        # Tutaj jako 7. miasto możesz opcjonalnie wstawić Katowice
        col_last_img, col_last_txt = st.columns([1, 3])
        with col_last_img:
            st.image("zdj/Katowice.jpg", width='stretch')
        with col_last_txt:
            st.markdown("<div style='padding-top: 10px;'><b>Katowice</b><br>Wyjazd udany? Podziel się swoimi wrażeniami z pobytu w województwie śląskim!</div>", unsafe_allow_html=True)
            
    st.markdown("**Podziel się swoimi wrażeniami, napisz opinię!**")

else:
    panel_filtrow, panel_wynikow = st.columns([1, 3])
    
    with panel_filtrow:
        st.subheader("Sortuj")
        sort_option = st.selectbox(
            "Sortuj według", 
            ["od najtańszych", "od najdroższych", "najwyższa ocena"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.subheader("Filtruj") 
        
        st.write("**Cena za noc**")
        c_min, c_max = st.columns(2)
        with c_min:
            cena_min = st.number_input("Od", min_value=0, value=0, step=50)
        with c_max:
            cena_max = st.number_input("Do", min_value=0, value=2000, step=50)
            
        st.markdown("---")
        st.write("**Rodzaj noclegu**")
        f_hotel = st.checkbox("Hotel")
        f_apartament = st.checkbox("Apartament")
        f_domek = st.checkbox("Domek")
        f_namiot = st.checkbox("Namiot")
        
        st.markdown("---")
        st.write("**Parking**")
        f_p_darmowy = st.checkbox("Darmowy")
        f_p_platny = st.checkbox("Za dodatkową opłatą")
        f_p_brak = st.checkbox("Brak")
        
        st.markdown("---")
        st.write("**Udogodnienia**")
        u_jacuzzi = st.checkbox("Jacuzzi")
        u_basen = st.checkbox("Basen")
        u_spa = st.checkbox("Spa")
        u_kuchnia = st.checkbox("Aneks kuchenny/kuchnia")
        
        # Przycisk powrotu do ekranu głównego
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Wyczyść wyniki wyszukiwania", use_container_width=True):
            st.session_state.search_clicked = False
            st.session_state.search_miejsce = ""
            st.rerun()

    with panel_wynikow:
        # Budowanie zapytania SQL na podstawie filtrów
        where_clauses = ["n.maks_liczba_osob >= :osoby"]
        sql_params = {"osoby": st.session_state.search_osoby}
        
        # Filtr miasta
        if st.session_state.search_miejsce.strip():
            where_clauses.append("n.lokalizacja_miasto LIKE :miasto")
            sql_params["miasto"] = f"%{st.session_state.search_miejsce.strip()}%"
            
        # Filtr ceny
        where_clauses.append("n.cena_za_noc BETWEEN :cena_min AND :cena_max")
        sql_params["cena_min"] = cena_min
        sql_params["cena_max"] = cena_max
        
        # Filtr typu obiektu
        wybrane_typy = []
        if f_hotel: wybrane_typy.append('Hotel')
        if f_apartament: wybrane_typy.append('Apartament')
        if f_domek: wybrane_typy.append('B&B')
        if f_namiot: wybrane_typy.append('Wynajem wakacyjny')
        
        if wybrane_typy:
            type_clauses = []
            for idx, t in enumerate(wybrane_typy):
                param_key = f"type_{idx}"
                type_clauses.append(f":{param_key}")
                sql_params[param_key] = t
            where_clauses.append(f"n.typ_obiektu IN ({', '.join(type_clauses)})")

        # Filtr udogodnień
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

        # Sortowanie wyników
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
                                    "<div style='background-color: #E2E8F0; height: 160px; border-radius: 5px;'></div>", 
                                    unsafe_allow_html=True
                                )
                                
                        with col_detale:
                            c_title, c_rating = st.columns([3, 1])
                            with c_title:
                                st.markdown(f"### {row['nazwa']}")
                                st.caption(f"{row['lokalizacja_miasto']}")
                            with c_rating:
                                st.markdown(
                                    f"<div style='text-align: right; background-color: #E2E8F0; padding: 5px 10px; border-radius: 5px; font-weight: bold;'>{row['srednia_ocena']}/5</div>", 
                                    unsafe_allow_html=True
                                )
                            
                            opis_skrócony = row['opis'] if row['opis'] else "Brak opisu obiektu."
                            if len(opis_skrócony) > 160:
                                opis_skrócony = opis_skrócony[:160] + "..."
                            st.write(opis_skrócony)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            c_space, c_price_btn = st.columns([2, 1])
                            with c_price_btn:
                                st.markdown(
                                    f"<div style='text-align: right; font-size: 1.4rem; font-weight: bold; margin-bottom: 5px;'>{int(row['cena_za_noc'])} zł</div>", 
                                    unsafe_allow_html=True
                                )
                                if st.button("Szczegóły", key=f"btn_{row['id_noclegu']}", width='stretch'):
                                    st.session_state.selected_nocleg_id = row['id_noclegu']
                                    st.switch_page("pages/strona_noclegu.py")
                                    
        except Exception as e:
            st.error(f"Nie udało się załadować ofert. Błąd: {e}")

render_page_footer()