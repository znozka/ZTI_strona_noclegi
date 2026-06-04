# # import streamlit as st
# # import datetime
# # import folium
# # from streamlit_folium import folium_static
# # from urllib.parse import urlencode
# # from src.ui import render_page_header, render_page_footer
# # from src.utils import wyswietl_zdjecie

# # # Ustawienia strony
# # st.set_page_config(
# #     page_title="Wyniki wyszukiwania",
# #     page_icon="assets/images/icon.svg",
# #     layout="wide",
# #     initial_sidebar_state="collapsed"
# # )

# # render_page_header()

# # st.markdown("### Przeglądaj dostępne oferty noclegów")

# # conn = st.connection("azure_sql", type="sql")

# # # pobieranie najwyższej ceny dla bieżących kryteriów wyszukiwania
# # def pobierz_najwyzsza_cene(miejsce, osoby):
# #     try:
# #         where_clauses = ["maks_liczba_osob >= :osoby"]
# #         sql_params = {"osoby": osoby}
        
# #         if miejsce and miejsce.strip():
# #             where_clauses.append("lokalizacja_miasto LIKE :miasto")
# #             sql_params["miasto"] = f"%{miejsce.strip()}%"
            
# #         query = f"SELECT MAX(cena_za_noc) as max_cena FROM noclegi WHERE {' AND '.join(where_clauses)}"
# #         df = conn.query(query, params=sql_params, ttl=0)
        
# #         if not df.empty and df.iloc[0]["max_cena"] is not None:
# #             return int(df.iloc[0]["max_cena"])
# #     except Exception:
# #         pass
# #     return 2000  # fallback

# # # Funkcja callback obsługująca kliknięcie w dowolny element noclegu
# # def przejdz_do_szczegolow(id_noclegu):
# #     st.session_state.selected_nocleg_id = id_noclegu
# #     # Czyścimy zbędne parametry z URL przed przejściem, aby wstecz działało idealnie
# #     st.query_params.clear()
# #     st.switch_page("pages/strona_noclegu.py")

# # # Dynamiczne pobieranie unikalnych miast z bazy danych z cache na 1 godzinę
# # @st.cache_data(ttl=3600)
# # def pobierz_unikalne_miasta():
# #     try:
# #         df_miasta = conn.query("SELECT DISTINCT lokalizacja_miasto FROM noclegi WHERE lokalizacja_miasto IS NOT NULL ORDER BY lokalizacja_miasto", ttl=0)
# #         return df_miasta["lokalizacja_miasto"].tolist()
# #     except Exception:
# #         return ["Gdańsk", "Kraków", "Katowice", "Poznań", "Warszawa", "Wrocław", "Łódź"]

# # lista_miast = pobierz_unikalne_miasta()

# # def build_search_map(df_hotels):
# #     df_coords = df_hotels.dropna(subset=["szerokosc_geo", "dlugosc_geo"])
# #     if df_coords.empty:
# #         return None

# #     center_lat = float(df_coords["szerokosc_geo"].astype(float).mean())
# #     center_lon = float(df_coords["dlugosc_geo"].astype(float).mean())
    
# #     m = folium.Map(
# #         location=[center_lat, center_lon], 
# #         zoom_start=11, 
# #         control_scale=False,
# #         tiles="cartodbpositron"
# #     )

# #     primary_color = st.config.get_option("theme.primaryColor")
# #     text_color = st.config.get_option("theme.textColor")
# #     bg_color = st.config.get_option("theme.backgroundColor")

# #     bounds = []
# #     for _, row in df_coords.iterrows():
# #         lat = float(row["szerokosc_geo"])
# #         lon = float(row["dlugosc_geo"])
# #         bounds.append([lat, lon])

# #         query = urlencode({
# #             "page": "pages/strona_noclegu.py",
# #             "id": row["id_noclegu"],
# #             "miejsce": st.session_state.search_miejsce,
# #             "data_od": str(st.session_state.search_data_od),
# #             "data_do": str(st.session_state.search_data_do),
# #             "osoby": str(st.session_state.search_osoby),
# #             "clicked": "True",
# #         })
        
# #         # kliknięcie pinezki przekierowuje na stronę noclegu
# #         js = f"window.open(window.top.location.origin + '/strona_noclegu?{query}', '_blank'); return false;"
        
# #         popup_html = f"""
# #         <div style="
# #             font-family: 'Source Sans Pro', sans-serif; 
# #             font-size: 13px; 
# #             color: {text_color};
# #             line-height: 1.4;
# #             max-width: 200px;
# #         ">
# #             <strong style="font-size: 14px; color: {primary_color};">{row['nazwa']}</strong><br>
# #             <span style="color: #767676;">{row['lokalizacja_adres']}</span><br>
# #             <a href="#" onclick="{js}" style="
# #                 color: {primary_color}; 
# #                 text-decoration: none; 
# #                 font-weight: bold;
# #             ">Zobacz szczegóły →</a>
# #         </div>
# #         """

# #         w, h = (22, 36)
# #         anchor_x = w // 2
# #         anchor_y = h
        
# #         icon_html = f"""
# #         <div style="cursor: pointer;">
# #             <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 32" width="{w}" height="{h}" style="filter: drop-shadow(0px 2px 3px rgba(0,0,0,0.3));">
# #                 <path d="M12 0C5.38 0 0 5.38 0 12c0 9 12 20 12 20s12-11 12-20C24 5.38 18.62 0 12 0z" fill="{primary_color}"/>
# #                 <circle cx="12" cy="12" r="4.5" fill="white"/>
# #                 <circle cx="12" cy="12" r="3.5" fill="{bg_color}"/>
# #             </svg>
# #         </div>
# #         """
        
# #         icon = folium.DivIcon(
# #             html=icon_html,
# #             icon_size=(w, h),
# #             icon_anchor=(anchor_x, anchor_y)
# #         )

# #         folium.Marker(
# #             location=[lat, lon],
# #             tooltip=row["nazwa"],
# #             popup=folium.Popup(popup_html, max_width=250),
# #             icon=icon,
# #         ).add_to(m)

# #     if len(bounds) > 1:
# #         m.fit_bounds(bounds, padding=(40, 40))

# #     return m

# # # formularz wyszukiwania
# # if "miejsce" in st.query_params:
# #     st.session_state.search_miejsce = st.query_params["miejsce"]
# # elif "search_miejsce" not in st.session_state:
# #     st.session_state.search_miejsce = ""

# # if "data_od" in st.query_params:
# #     try: st.session_state.search_data_od = datetime.date.fromisoformat(st.query_params["data_od"])
# #     except ValueError: st.session_state.search_data_od = datetime.date.today()
# # elif "search_data_od" not in st.session_state:
# #     st.session_state.search_data_od = datetime.date.today()

# # if "data_do" in st.query_params:
# #     try: st.session_state.search_data_do = datetime.date.fromisoformat(st.query_params["data_do"])
# #     except ValueError: st.session_state.search_data_do = datetime.date.today() + datetime.timedelta(days=2)
# # elif "search_data_do" not in st.session_state:
# #     st.session_state.search_data_do = datetime.date.today() + datetime.timedelta(days=2)

# # if "osoby" in st.query_params:
# #     try: st.session_state.search_osoby = int(st.query_params["osoby"])
# #     except ValueError: st.session_state.search_osoby = 2
# # elif "search_osoby" not in st.session_state:
# #     st.session_state.search_osoby = 2

# # try:
# #     st.session_state.search_osoby = int(st.session_state.search_osoby)
# # except (ValueError, TypeError):
# #     st.session_state.search_osoby = 2

# # if "clicked" in st.query_params:
# #     st.session_state.search_clicked = st.query_params["clicked"] == "True"
# # elif "search_clicked" not in st.session_state:
# #     st.session_state.search_clicked = bool(st.session_state.search_miejsce)

# # # dynamiczne wyliczenie najwyższej ceny dla aktualnego wyszukiwania
# # max_cena_baza = pobierz_najwyzsza_cene(st.session_state.get("search_miejsce", ""), st.session_state.search_osoby)

# # # filtry boczne i sortowanie
# # if "saved_filters" not in st.session_state:
# #     st.session_state.saved_filters = {}

# # def pobierz_filtr(param_name, domyslna_wartosc, transformacja=lambda x: x):
# #     if param_name in st.query_params:
# #         wartosc = transformacja(st.query_params[param_name])
# #         st.session_state.saved_filters[param_name] = wartosc
# #         return wartosc
# #     return st.session_state.saved_filters.get(param_name, domyslna_wartosc)

# # # Podmieniamy domyślne 2000 na zmienną max_cena_baza
# # url_filters = {
# #     "sort": pobierz_filtr("sort", "od najtańszych"),
# #     "cena_min": pobierz_filtr("cena_min", 0, lambda x: int(x) if str(x).isdigit() else 0),
# #     "cena_max": pobierz_filtr("cena_max", max_cena_baza, lambda x: int(x) if str(x).isdigit() else max_cena_baza),
# #     "f_hotel": pobierz_filtr("f_hotel", False, lambda x: x == "True" or x is True),
# #     "f_apartament": pobierz_filtr("f_apartament", False, lambda x: x == "True" or x is True),
# #     "f_b_and_b": pobierz_filtr("f_b_and_b", False, lambda x: x == "True" or x is True),
# #     "f_schronisko": pobierz_filtr("f_schronisko", False, lambda x: x == "True" or x is True),
# #     "f_wynajem": pobierz_filtr("f_wynajem", False, lambda x: x == "True" or x is True),
# #     "f_p_darmowy": pobierz_filtr("f_p_darmowy", False, lambda x: x == "True" or x is True),
# #     "f_p_platny": pobierz_filtr("f_p_platny", False, lambda x: x == "True" or x is True),
# #     "f_p_brak": pobierz_filtr("f_p_brak", False, lambda x: x == "True" or x is True),
# #     "u_jacuzzi": pobierz_filtr("u_jacuzzi", False, lambda x: x == "True" or x is True),
# #     "u_basen": pobierz_filtr("u_basen", False, lambda x: x == "True" or x is True),
# #     "u_spa": pobierz_filtr("u_spa", False, lambda x: x == "True" or x is True),
# #     "u_kuchnia": pobierz_filtr("u_kuchnia", False, lambda x: x == "True" or x is True),
# # }

# # # Określenie indeksu dla selectboxa na podstawie odzyskanego stanu z sesji
# # domyslny_indeks = None
# # if st.session_state.get("search_miejsce") in lista_miast:
# #     domyslny_indeks = lista_miast.index(st.session_state.search_miejsce)
# # else:
# #     domyslny_indeks = None

# # # Inicjalizacja wersji filtrów bocznych
# # if "filters_version" not in st.session_state:
# #     st.session_state.filters_version = 0
# # version = st.session_state.filters_version

# # # Blokada przed nieautoryzowanym wejściem
# # if not st.session_state.search_clicked:
# #     st.warning("Aby wyświetlić wyniki, najpierw uruchom wyszukiwanie na stronie głównej.")
# #     if st.button("Wróć do strony głównej"):
# #         st.session_state.search_clicked = False
# #         for key in ["search_miejsce", "search_data_od", "search_data_do", "search_osoby", "selected_nocleg_id", "saved_filters"]:
# #             if key in st.session_state: del st.session_state[key]
# #         st.query_params.clear()
# #         st.switch_page("app.py")
# #     render_page_footer()
# #     st.stop()

# # # formularz wyszukiwania
# # search_container = st.container(border=True)
# # with search_container:
# #     c1, c2, c3, c4, c5 = st.columns([2.5, 1.2, 1.2, 1.2, 1])
    
# #     with c1:
# #         miejsce_input = st.selectbox(
# #             "Miejsce", 
# #             options=lista_miast,
# #             index=domyslny_indeks,
# #             placeholder="Wpisz miasto...", 
# #             label_visibility="visible"
# #         )
# #     with c2:
# #         data_od_input = st.date_input("Data od", value=st.session_state.search_data_od)
# #     with c3:
# #         data_do_input = st.date_input("Data do", value=st.session_state.search_data_do)
# #     with c4:
# #         osoby_input = st.number_input("Liczba osób", min_value=1, max_value=20, value=st.session_state.search_osoby)
# #     with c5:
# #         st.markdown("<br>", unsafe_allow_html=True)
        
# #         czyste_miejsce = miejsce_input if miejsce_input is not None else ""
        
# #         # ZAWSZE dbamy o to, aby te parametry były w URL (przy każdym rerun, np. z filtrów bocznych)
# #         st.query_params["miejsce"] = czyste_miejsce
# #         st.query_params["data_od"] = str(data_od_input)
# #         st.query_params["data_do"] = str(data_do_input)
# #         st.query_params["osoby"] = str(osoby_input)
# #         st.query_params["clicked"] = "True"
        
# #         if st.button("Szukaj", width='stretch', type="primary"):
# #             # Czyszczenie filtrów cenowych z adresu URL
# #             for klucz in ["cena_min", "cena_max"]:
# #                 if klucz in st.query_params:
# #                     del st.query_params[klucz]
            
# #             # Czyszczenie filtrów cenowych z zapamiętanego słownika
# #             if "saved_filters" in st.session_state:
# #                 st.session_state.saved_filters.pop("cena_min", None)
# #                 st.session_state.saved_filters.pop("cena_max", None)
            
# #             # Zwiększenie wersji, aby zmusić st.number_input w panelu bocznym do odświeżenia klucza
# #             if "filters_version" in st.session_state:
# #                 st.session_state.filters_version += 1
# #             else:
# #                 st.session_state.filters_version = 1
            
# #             # Zapisanie nowych kryteriów głównych
# #             st.session_state.search_clicked = True
# #             st.session_state.search_miejsce = czyste_miejsce
# #             st.session_state.search_osoby = osoby_input
# #             st.session_state.search_data_od = data_od_input
# #             st.session_state.search_data_do = data_do_input
            
# #             st.rerun()

# # # Layout dolny (mapa + filtry + wyniki)
# # panel_filtrow, panel_wynikow = st.columns([1, 3])

# # with panel_filtrow:
# #     # kontener na mapkę
# #     sidebar_map_container = st.container()
    
# #     st.subheader("Sortuj")
# #     sort_options_list = ["od najtańszych", "od najdroższych", "najwyższa ocena"]
# #     try: sort_index = sort_options_list.index(url_filters["sort"])
# #     except ValueError: sort_index = 0

# #     sort_option = st.selectbox(
# #         "Sortuj według", 
# #         sort_options_list,
# #         index=sort_index,
# #         label_visibility="collapsed",
# #         key=f"sort_{version}"
# #     )
# #     st.query_params["sort"] = sort_option
    
# #     st.markdown("---")
# #     st.subheader("Filtruj") 
    
# #     st.write("**Cena za noc**")
# #     c_min, c_max = st.columns(2)
    
# #     with c_min:
# #         cena_min = st.number_input("Od", min_value=0, value=url_filters["cena_min"], step=100, key=f"cena_min_{version}")
# #         st.query_params["cena_min"] = str(cena_min)
# #     with c_max:
# #         cena_max = st.number_input("Do", min_value=0, value=url_filters["cena_max"], step=100, key=f"cena_max_{version}")
# #         st.query_params["cena_max"] = str(cena_max)
        
# #     st.markdown("---")
# #     st.write("**Rodzaj noclegu**")
# #     f_hotel = st.checkbox("Hotel", value=url_filters["f_hotel"], key=f"f_hotel_{version}")
# #     f_apartament = st.checkbox("Apartament", value=url_filters["f_apartament"], key=f"f_apartament_{version}")
# #     f_b_and_b = st.checkbox("B&B", value=url_filters["f_b_and_b"], key=f"f_b_and_b_{version}")
# #     f_schronisko = st.checkbox("Schronisko", value=url_filters["f_schronisko"], key=f"f_schronisko_{version}")
# #     f_wynajem = st.checkbox("Wynajem wakacyjny", value=url_filters["f_wynajem"], key=f"f_wynajem_{version}")
    
# #     st.query_params["f_hotel"] = str(f_hotel)
# #     st.query_params["f_apartament"] = str(f_apartament)
# #     st.query_params["f_b_and_b"] = str(f_b_and_b)
# #     st.query_params["f_schronisko"] = str(f_schronisko)
# #     st.query_params["f_wynajem"] = str(f_wynajem)
    
# #     st.markdown("---")
# #     st.write("**Parking**")
# #     f_p_darmowy = st.checkbox("Darmowy", value=url_filters["f_p_darmowy"], key=f"f_p_darmowy_{version}")
# #     f_p_platny = st.checkbox("Za dodatkową opłatą", value=url_filters["f_p_platny"], key=f"f_p_platny_{version}")
# #     f_p_brak = st.checkbox("Brak", value=url_filters["f_p_brak"], key=f"f_p_brak_{version}")
    
# #     st.query_params["f_p_darmowy"] = str(f_p_darmowy)
# #     st.query_params["f_p_platny"] = str(f_p_platny)
# #     st.query_params["f_p_brak"] = str(f_p_brak)
    
# #     st.markdown("---")
# #     st.write("**Udogodnienia**")
# #     u_jacuzzi = st.checkbox("Jacuzzi", value=url_filters["u_jacuzzi"], key=f"u_jacuzzi_{version}")
# #     u_basen = st.checkbox("Basen", value=url_filters["u_basen"], key=f"u_basen_{version}")
# #     u_spa = st.checkbox("Spa", value=url_filters["u_spa"], key=f"u_spa_{version}")
# #     u_kuchnia = st.checkbox("Aneks kuchenny/kuchnia", value=url_filters["u_kuchnia"], key=f"u_kuchnia_{version}")
    
# #     st.query_params["u_jacuzzi"] = str(u_jacuzzi)
# #     st.query_params["u_basen"] = str(u_basen)
# #     st.query_params["u_spa"] = str(u_spa)
# #     st.query_params["u_kuchnia"] = str(u_kuchnia)
    
# #     st.markdown("<br>", unsafe_allow_html=True)
# #     if st.button("Wyczyść filtry", width='stretch'):
# #         klucze_filtrow = [
# #             "sort", "cena_min", "cena_max", "f_hotel", "f_apartament", "f_b_and_b", 
# #             "f_schronisko", "f_wynajem", "f_p_darmowy", "f_p_platny", "f_p_brak",
# #             "u_jacuzzi", "u_basen", "u_spa", "u_kuchnia"
# #         ]
# #         for klucz in klucze_filtrow:
# #             if klucz in st.query_params: del st.query_params[klucz]
# #         st.session_state.filters_version += 1
# #         st.session_state.saved_filters = {}
# #         st.rerun()

# # # Zapisanie stanu filtrów bocznych na potrzeby powrotów
# # st.session_state.saved_filters = {
# #     "sort": sort_option,
# #     "cena_min": cena_min,
# #     "cena_max": cena_max,
# #     "f_hotel": f_hotel,
# #     "f_apartament": f_apartament,
# #     "f_b_and_b": f_b_and_b,
# #     "f_schronisko": f_schronisko,
# #     "f_wynajem": f_wynajem,
# #     "f_p_darmowy": f_p_darmowy,
# #     "f_p_platny": f_p_platny,
# #     "f_p_brak": f_p_brak,
# #     "u_jacuzzi": u_jacuzzi,
# #     "u_basen": u_basen,
# #     "u_spa": u_spa,
# #     "u_kuchnia": u_kuchnia,
# # }

# # with panel_wynikow:
# #     st.markdown("""
# #     <style>
# #     div[class*="st-key-title_btn_"] button {
# #         background: transparent !important;
# #         border: none !important;
# #         box-shadow: none !important;
# #         color: inherit !important;
# #         font-size: 1.75rem !important;
# #         font-weight: 700 !important;
# #         padding: 0 !important;
# #         margin: 0 !important;
# #         text-align: left !important;
# #         justify-content: flex-start !important;
# #         line-height: 1.2 !important;
# #     }
# #     div[class*="st-key-title_btn_"] button:hover {
# #         color: #ff4b4b !important;
# #         text-decoration: underline !important;
# #         background: transparent !important;
# #     }
# #     </style>
# #     """, unsafe_allow_html=True)

# #     # Budowanie zapytania SQL
# #     where_clauses = ["n.maks_liczba_osob >= :osoby"]
# #     sql_params = {"osoby": st.session_state.search_osoby}
    
# #     if st.session_state.search_miejsce.strip():
# #         where_clauses.append("n.lokalizacja_miasto LIKE :miasto")
# #         sql_params["miasto"] = f"%{st.session_state.search_miejsce.strip()}%"
        
# #     where_clauses.append("n.cena_za_noc BETWEEN :cena_min AND :cena_max")
# #     sql_params["cena_min"] = cena_min
# #     sql_params["cena_max"] = cena_max
    
# #     wybrane_typy = []
# #     if f_hotel: wybrane_typy.append('Hotel')
# #     if f_apartament: wybrane_typy.append('Apartament')
# #     if f_b_and_b: wybrane_typy.append('B&B')
# #     if f_schronisko: wybrane_typy.append('Schronisko')
# #     if f_wynajem: wybrane_typy.append('Wynajem wakacyjny')

# #     if wybrane_typy:
# #         type_clauses = []
# #         for idx, t in enumerate(wybrane_typy):
# #             param_key = f"type_{idx}"
# #             type_clauses.append(f":{param_key}")
# #             sql_params[param_key] = t
# #         where_clauses.append(f"n.typ_obiektu IN ({', '.join(type_clauses)})")

# #     wybrane_udogodnienia = []
# #     if u_jacuzzi: wybrane_udogodnienia.append('Jacuzzi')
# #     if u_basen: wybrane_udogodnienia.append('Basen')
# #     if u_spa: wybrane_udogodnienia.append('Spa')
# #     if u_kuchnia: wybrane_udogodnienia.append('Aneks kuchenny/kuchnia')

# #     if wybrane_udogodnienia:
# #         for idx, u in enumerate(wybrane_udogodnienia):
# #             u_param = f"u_param_{idx}"
# #             sql_params[u_param] = u
# #             where_clauses.append(f"""
# #                 EXISTS (
# #                     SELECT 1 FROM noclegi_udogodnienia nu
# #                     JOIN udogodnienia ud ON nu.id_udogodnienia = ud.id_udogodnienia
# #                     WHERE nu.id_noclegu = n.id_noclegu AND ud.nazwa = :{u_param}
# #                 )
# #             """)

# #     if sort_option == "od najtańszych": order_by = "n.cena_za_noc ASC"
# #     elif sort_option == "od najdroższych": order_by = "n.cena_za_noc DESC"
# #     else: order_by = "n.srednia_ocena DESC"

# #     query_szukaj = f"""
# #     SELECT 
# #         n.id_noclegu, n.nazwa, n.lokalizacja_miasto, n.lokalizacja_adres, n.opis, n.cena_za_noc, n.srednia_ocena,
# #         n.szerokosc_geo, n.dlugosc_geo,
# #         (SELECT TOP 1 url_zdjecia FROM zdjecia_noclegu WHERE id_noclegu = n.id_noclegu ORDER BY czy_glowne DESC) AS url_zdjecia
# #     FROM noclegi n
# #     WHERE {" AND ".join(where_clauses)}
# #     ORDER BY {order_by}
# #     """
    
# #     try:
# #         df_wyniki = conn.query(query_szukaj, params=sql_params, ttl=0)
        
# #         if df_wyniki.empty:
# #             st.info("Brak dostępnych ofert dla wybranych kryteriów.")
# #         else:
# #             search_map = build_search_map(df_wyniki)
            
# #             # mapa do panelu bocznego
# #             if search_map is not None:
# #                 with sidebar_map_container:
# #                     st.markdown("#### Lokalizacja ofert")
# #                     folium_static(search_map, width=320, height=280)
# #                     st.markdown("---")
            
# #             for _, row in df_wyniki.iterrows():
# #                 card = st.container(border=True)
# #                 with card:
# #                     col_img, col_detale = st.columns([1.2, 2.5])
                    
# #                     with col_img:
# #                         if row['url_zdjecia']:
# #                             foto_ready = wyswietl_zdjecie(row['url_zdjecia'], szerokosc=400, wysokosc=330)
# #                             if foto_ready:
# #                                 st.image(foto_ready, width='stretch')
# #                             else:
# #                                 st.markdown("<div class='surface-block' style='height: 160px;'></div>", unsafe_allow_html=True)
# #                         else:
# #                             st.markdown("<div class='surface-block' style='height: 160px;'></div>", unsafe_allow_html=True)
                            
# #                     with col_detale:
# #                         c_title, c_rating = st.columns([3, 1])
# #                         with c_title:
# #                             kliknieto_tytul = st.button(row['nazwa'], key=f"title_btn_{row['id_noclegu']}")
# #                             st.caption(f"{row['lokalizacja_adres']}")
# #                         with c_rating:
# #                             st.markdown(f"<div class='rating-chip'>{row['srednia_ocena']}/5</div>", unsafe_allow_html=True)
                        
# #                         opis_skrócony = row['opis'] if row['opis'] else "Brak opisu obiektu."
# #                         if len(opis_skrócony) > 160:
# #                             opis_skrócony = opis_skrócony[:160] + "..."
# #                         st.write(opis_skrócony)
                        
# #                         st.markdown("<br>", unsafe_allow_html=True)
# #                         c_space, c_price_btn = st.columns([2, 1])

# #                         with c_price_btn:
# #                             st.markdown(f"<div style='text-align: right; font-size: 1.4rem;'>{int(row['cena_za_noc'])} zł</div>", unsafe_allow_html=True)
# #                             kliknieto_przycisk = st.button("Szczegóły", key=f"btn_{row['id_noclegu']}", width='stretch')
                    
# #                     # Wewnątrz bloku sprawdzającego kliknięcie:
# #                     if kliknieto_tytul or kliknieto_przycisk:
# #                         st.session_state.selected_nocleg_id = row['id_noclegu']
# #                         st.query_params["id"] = str(row['id_noclegu']) 
# #                         st.switch_page("pages/strona_noclegu.py")
                                
# #     except Exception as e:
# #         st.error(f"Nie udało się załadować ofert. Błąd: {e}")

# # render_page_footer()
# import streamlit as st
# import datetime
# import pandas as pd
# import folium
# from streamlit_folium import folium_static
# from urllib.parse import urlencode
# from src.ui import render_page_header, render_page_footer
# from src.utils import wyswietl_zdjecie

# # Ustawienia strony
# st.set_page_config(
#     page_title="Wyniki wyszukiwania",
#     page_icon="assets/images/icon.svg",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# render_page_header()

# st.markdown("### Przeglądaj dostępne oferty noclegów")

# conn = st.connection("azure_sql", type="sql")

# # pobieranie najwyższej ceny dla bieżących kryteriów wyszukiwania
# def pobierz_najwyzsza_cene(miejsce, osoby):
#     try:
#         where_clauses = ["maks_liczba_osob >= :osoby"]
#         sql_params = {"osoby": osoby}
        
#         if miejsce and miejsce.strip():
#             where_clauses.append("lokalizacja_miasto LIKE :miasto")
#             sql_params["miasto"] = f"%{miejsce.strip()}%"
            
#         query = f"SELECT MAX(cena_za_noc) as max_cena FROM noclegi WHERE {' AND '.join(where_clauses)}"
#         df = conn.query(query, params=sql_params, ttl=0)
        
#         if not df.empty and df.iloc[0]["max_cena"] is not None:
#             return int(df.iloc[0]["max_cena"])
#     except Exception:
#         pass
#     return 2000  # fallback

# # Funkcja callback obsługująca kliknięcie w dowolny element noclegu
# def przejdz_do_szczegolow(id_noclegu):
#     st.session_state.selected_nocleg_id = id_noclegu
#     # Czyścimy zbędne parametry z URL przed przejściem, aby wstecz działało idealnie
#     st.query_params.clear()
#     st.switch_page("pages/strona_noclegu.py")

# # Dynamiczne pobieranie unikalnych miast z bazy danych z cache na 1 godzinę
# @st.cache_data(ttl=3600)
# def pobierz_unikalne_miasta():
#     try:
#         df_miasta = conn.query("SELECT DISTINCT lokalizacja_miasto FROM noclegi WHERE lokalizacja_miasto IS NOT NULL ORDER BY lokalizacja_miasto", ttl=0)
#         return df_miasta["lokalizacja_miasto"].tolist()
#     except Exception:
#         return ["Gdańsk", "Kraków", "Katowice", "Poznań", "Warszawa", "Wrocław", "Łódź"]

# lista_miast = pobierz_unikalne_miasta()

# def build_search_map(df_hotels):
#     df_coords = df_hotels.dropna(subset=["szerokosc_geo", "dlugosc_geo"])
#     if df_coords.empty:
#         return None

#     center_lat = float(df_coords["szerokosc_geo"].astype(float).mean())
#     center_lon = float(df_coords["dlugosc_geo"].astype(float).mean())
    
#     m = folium.Map(
#         location=[center_lat, center_lon], 
#         zoom_start=11, 
#         control_scale=False,
#         tiles="cartodbpositron"
#     )

#     primary_color = st.config.get_option("theme.primaryColor")
#     text_color = st.config.get_option("theme.textColor")
#     bg_color = st.config.get_option("theme.backgroundColor")

#     bounds = []
#     for _, row in df_coords.iterrows():
#         lat = float(row["szerokosc_geo"])
#         lon = float(row["dlugosc_geo"])
#         bounds.append([lat, lon])

#         query = urlencode({
#             "page": "pages/strona_noclegu.py",
#             "id": row["id_noclegu"],
#             "miejsce": st.session_state.search_miejsce,
#             "data_od": str(st.session_state.search_data_od),
#             "data_do": str(st.session_state.search_data_do),
#             "osoby": str(st.session_state.search_osoby),
#             "clicked": "True",
#         })
        
#         # kliknięcie pinezki przekierowuje na stronę noclegu
#         js = f"window.open(window.top.location.origin + '/strona_noclegu?{query}', '_blank'); return false;"
        
#         popup_html = f"""
#         <div style="
#             font-family: 'Source Sans Pro', sans-serif; 
#             font-size: 13px; 
#             color: {text_color};
#             line-height: 1.4;
#             max-width: 200px;
#         ">
#             <strong style="font-size: 14px; color: {primary_color};">{row['nazwa']}</strong><br>
#             <span style="color: #767676;">{row['lokalizacja_adres']}</span><br>
#             <a href="#" onclick="{js}" style="
#                 color: {primary_color}; 
#                 text-decoration: none; 
#                 font-weight: bold;
#             ">Zobacz szczegóły →</a>
#         </div>
#         """

#         w, h = (22, 36)
#         anchor_x = w // 2
#         anchor_y = h
        
#         icon_html = f"""
#         <div style="cursor: pointer;">
#             <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 32" width="{w}" height="{h}" style="filter: drop-shadow(0px 2px 3px rgba(0,0,0,0.3));">
#                 <path d="M12 0C5.38 0 0 5.38 0 12c0 9 12 20 12 20s12-11 12-20C24 5.38 18.62 0 12 0z" fill="{primary_color}"/>
#                 <circle cx="12" cy="12" r="4.5" fill="white"/>
#                 <circle cx="12" cy="12" r="3.5" fill="{bg_color}"/>
#             </svg>
#         </div>
#         """
        
#         icon = folium.DivIcon(
#             html=icon_html,
#             icon_size=(w, h),
#             icon_anchor=(anchor_x, anchor_y)
#         )

#         folium.Marker(
#             location=[lat, lon],
#             tooltip=row["nazwa"],
#             popup=folium.Popup(popup_html, max_width=250),
#             icon=icon,
#         ).add_to(m)

#     if len(bounds) > 1:
#         m.fit_bounds(bounds, padding=(40, 40))

#     return m

# # formularz wyszukiwania
# if "miejsce" in st.query_params:
#     st.session_state.search_miejsce = st.query_params["miejsce"]
# elif "search_miejsce" not in st.session_state:
#     st.session_state.search_miejsce = ""

# if "data_od" in st.query_params:
#     try: st.session_state.search_data_od = datetime.date.fromisoformat(st.query_params["data_od"])
#     except ValueError: st.session_state.search_data_od = datetime.date.today()
# elif "search_data_od" not in st.session_state:
#     st.session_state.search_data_od = datetime.date.today()

# if "data_do" in st.query_params:
#     try: st.session_state.search_data_do = datetime.date.fromisoformat(st.query_params["data_do"])
#     except ValueError: st.session_state.search_data_do = datetime.date.today() + datetime.timedelta(days=2)
# elif "search_data_do" not in st.session_state:
#     st.session_state.search_data_do = datetime.date.today() + datetime.timedelta(days=2)

# if "osoby" in st.query_params:
#     try: st.session_state.search_osoby = int(st.query_params["osoby"])
#     except ValueError: st.session_state.search_osoby = 2
# elif "search_osoby" not in st.session_state:
#     st.session_state.search_osoby = 2

# try:
#     st.session_state.search_osoby = int(st.session_state.search_osoby)
# except (ValueError, TypeError):
#     st.session_state.search_osoby = 2

# if "clicked" in st.query_params:
#     st.session_state.search_clicked = st.query_params["clicked"] == "True"
# elif "search_clicked" not in st.session_state:
#     st.session_state.search_clicked = bool(st.session_state.search_miejsce)

# # dynamiczne wyliczenie najwyższej ceny dla aktualnego wyszukiwania
# max_cena_baza = pobierz_najwyzsza_cene(st.session_state.get("search_miejsce", ""), st.session_state.search_osoby)

# # filtry boczne i sortowanie
# if "saved_filters" not in st.session_state:
#     st.session_state.saved_filters = {}

# def pobierz_filtr(param_name, domyslna_wartosc, transformacja=lambda x: x):
#     if param_name in st.query_params:
#         wartosc = transformacja(st.query_params[param_name])
#         st.session_state.saved_filters[param_name] = wartosc
#         return wartosc
#     return st.session_state.saved_filters.get(param_name, domyslna_wartosc)

# url_filters = {
#     "sort": pobierz_filtr("sort", "od najtańszych"),
#     "cena_min": pobierz_filtr("cena_min", 0, lambda x: int(x) if str(x).isdigit() else 0),
#     "cena_max": pobierz_filtr("cena_max", max_cena_baza, lambda x: int(x) if str(x).isdigit() else max_cena_baza),
#     "f_hotel": pobierz_filtr("f_hotel", False, lambda x: x == "True" or x is True),
#     "f_apartament": pobierz_filtr("f_apartament", False, lambda x: x == "True" or x is True),
#     "f_b_and_b": pobierz_filtr("f_b_and_b", False, lambda x: x == "True" or x is True),
#     "f_schronisko": pobierz_filtr("f_schronisko", False, lambda x: x == "True" or x is True),
#     "f_wynajem": pobierz_filtr("f_wynajem", False, lambda x: x == "True" or x is True),
#     "f_p_darmowy": pobierz_filtr("f_p_darmowy", False, lambda x: x == "True" or x is True),
#     "f_p_platny": pobierz_filtr("f_p_platny", False, lambda x: x == "True" or x is True),
#     "f_p_brak": pobierz_filtr("f_p_brak", False, lambda x: x == "True" or x is True),
#     "u_jacuzzi": pobierz_filtr("u_jacuzzi", False, lambda x: x == "True" or x is True),
#     "u_basen": pobierz_filtr("u_basen", False, lambda x: x == "True" or x is True),
#     "u_spa": pobierz_filtr("u_spa", False, lambda x: x == "True" or x is True),
#     "u_kuchnia": pobierz_filtr("u_kuchnia", False, lambda x: x == "True" or x is True),
# }

# domyslny_indeks = None
# if st.session_state.get("search_miejsce") in lista_miast:
#     domyslny_indeks = lista_miast.index(st.session_state.search_miejsce)

# if "filters_version" not in st.session_state:
#     st.session_state.filters_version = 0
# version = st.session_state.filters_version

# if not st.session_state.search_clicked:
#     st.warning("Aby wyświetlić wyniki, najpierw uruchom wyszukiwanie na stronie głównej.")
#     if st.button("Wróć do strony głównej"):
#         st.session_state.search_clicked = False
#         for key in ["search_miejsce", "search_data_od", "search_data_do", "search_osoby", "selected_nocleg_id", "saved_filters"]:
#             if key in st.session_state: del st.session_state[key]
#         st.query_params.clear()
#         st.switch_page("app.py")
#     render_page_footer()
#     st.stop()

# # formularz wyszukiwania
# search_container = st.container(border=True)
# with search_container:
#     c1, c2, c3, c4, c5 = st.columns([2.5, 1.2, 1.2, 1.2, 1])
    
#     with c1:
#         miejsce_input = st.selectbox(
#             "Miejsce", 
#             options=lista_miast,
#             index=domyslny_indeks,
#             placeholder="Wpisz miasto...", 
#             label_visibility="visible"
#         )
#     with c2:
#         data_od_input = st.date_input("Data od", value=st.session_state.search_data_od)
#     with c3:
#         data_do_input = st.date_input("Data do", value=st.session_state.search_data_do)
#     with c4:
#         osoby_input = st.number_input("Liczba osób", min_value=1, max_value=20, value=st.session_state.search_osoby)
#     with c5:
#         st.markdown("<br>", unsafe_allow_html=True)
#         czyste_miejsce = miejsce_input if miejsce_input is not None else ""
        
#         st.query_params["miejsce"] = czyste_miejsce
#         st.query_params["data_od"] = str(data_od_input)
#         st.query_params["data_do"] = str(data_do_input)
#         st.query_params["osoby"] = str(osoby_input)
#         st.query_params["clicked"] = "True"
        
#         if st.button("Szukaj", width='stretch', type="primary"):
#             for klucz in ["cena_min", "cena_max"]:
#                 if klucz in st.query_params: del st.query_params[klucz]
            
#             if "saved_filters" in st.session_state:
#                 st.session_state.saved_filters.pop("cena_min", None)
#                 st.session_state.saved_filters.pop("cena_max", None)
            
#             st.session_state.filters_version += 1
#             st.session_state.search_clicked = True
#             st.session_state.search_miejsce = czyste_miejsce
#             st.session_state.search_osoby = osoby_input
#             st.session_state.search_data_od = data_od_input
#             st.session_state.search_data_do = data_do_input
#             st.rerun()

# # Layout dolny
# panel_filtrow, panel_wynikow = st.columns([1, 3])

# with panel_filtrow:
#     sidebar_map_container = st.container()
    
#     st.subheader("Sortuj")
#     sort_options_list = ["od najtańszych", "od najdroższych", "najwyższa ocena"]
#     try: sort_index = sort_options_list.index(url_filters["sort"])
#     except ValueError: sort_index = 0

#     sort_option = st.selectbox(
#         "Sortuj według", 
#         sort_options_list,
#         index=sort_index,
#         label_visibility="collapsed",
#         key=f"sort_{version}"
#     )
#     st.query_params["sort"] = sort_option
    
#     st.markdown("---")
#     st.subheader("Filtruj") 
    
#     st.write("**Cena za noc**")
#     c_min, c_max = st.columns(2)
    
#     with c_min:
#         cena_min = st.number_input("Od", min_value=0, value=url_filters["cena_min"], step=100, key=f"cena_min_{version}")
#         st.query_params["cena_min"] = str(cena_min)
#     with c_max:
#         cena_max = st.number_input("Do", min_value=0, value=url_filters["cena_max"], step=100, key=f"cena_max_{version}")
#         st.query_params["cena_max"] = str(cena_max)
        
#     st.markdown("---")
#     st.write("**Rodzaj noclegu**")
#     f_hotel = st.checkbox("Hotel", value=url_filters["f_hotel"], key=f"f_hotel_{version}")
#     f_apartament = st.checkbox("Apartament", value=url_filters["f_apartament"], key=f"f_apartament_{version}")
#     f_b_and_b = st.checkbox("B&B", value=url_filters["f_b_and_b"], key=f"f_b_and_b_{version}")
#     f_schronisko = st.checkbox("Schronisko", value=url_filters["f_schronisko"], key=f"f_schronisko_{version}")
#     f_wynajem = st.checkbox("Wynajem wakacyjny", value=url_filters["f_wynajem"], key=f"f_wynajem_{version}")
    
#     st.query_params["f_hotel"] = str(f_hotel)
#     st.query_params["f_apartament"] = str(f_apartament)
#     st.query_params["f_b_and_b"] = str(f_b_and_b)
#     st.query_params["f_schronisko"] = str(f_schronisko)
#     st.query_params["f_wynajem"] = str(f_wynajem)
    
#     st.markdown("---")
#     st.write("**Parking**")
#     f_p_darmowy = st.checkbox("Darmowy", value=url_filters["f_p_darmowy"], key=f"f_p_darmowy_{version}")
#     f_p_platny = st.checkbox("Za dodatkową opłatą", value=url_filters["f_p_platny"], key=f"f_p_platny_{version}")
#     f_p_brak = st.checkbox("Brak", value=url_filters["f_p_brak"], key=f"f_p_brak_{version}")
    
#     st.query_params["f_p_darmowy"] = str(f_p_darmowy)
#     st.query_params["f_p_platny"] = str(f_p_platny)
#     st.query_params["f_p_brak"] = str(f_p_brak)
    
#     st.markdown("---")
#     st.write("**Udogodnienia**")
#     u_jacuzzi = st.checkbox("Jacuzzi", value=url_filters["u_jacuzzi"], key=f"u_jacuzzi_{version}")
#     u_basen = st.checkbox("Basen", value=url_filters["u_basen"], key=f"u_basen_{version}")
#     u_spa = st.checkbox("Spa", value=url_filters["u_spa"], key=f"u_spa_{version}")
#     u_kuchnia = st.checkbox("Aneks kuchenny/kuchnia", value=url_filters["u_kuchnia"], key=f"u_kuchnia_{version}")
    
#     st.query_params["u_jacuzzi"] = str(u_jacuzzi)
#     st.query_params["u_basen"] = str(u_basen)
#     st.query_params["u_spa"] = str(u_spa)
#     st.query_params["u_kuchnia"] = str(u_kuchnia)
    
#     st.markdown("<br>", unsafe_allow_html=True)
#     if st.button("Wyczyść filtry", width='stretch'):
#         klucze_filtrow = [
#             "sort", "cena_min", "cena_max", "f_hotel", "f_apartament", "f_b_and_b", 
#             "f_schronisko", "f_wynajem", "f_p_darmowy", "f_p_platny", "f_p_brak",
#             "u_jacuzzi", "u_basen", "u_spa", "u_kuchnia"
#         ]
#         for klucz in klucze_filtrow:
#             if klucz in st.query_params: del st.query_params[klucz]
#         st.session_state.filters_version += 1
#         st.session_state.saved_filters = {}
#         st.rerun()

# st.session_state.saved_filters = {
#     "sort": sort_option, "cena_min": cena_min, "cena_max": cena_max,
#     "f_hotel": f_hotel, "f_apartament": f_apartament, "f_b_and_b": f_b_and_b,
#     "f_schronisko": f_schronisko, "f_wynajem": f_wynajem, "f_p_darmowy": f_p_darmowy,
#     "f_p_platny": f_p_platny, "f_p_brak": f_p_brak, "u_jacuzzi": u_jacuzzi,
#     "u_basen": u_basen, "u_spa": u_spa, "u_kuchnia": u_kuchnia,
# }

# with panel_wynikow:
#     st.markdown("""
#     <style>
#     div[class*="st-key-title_btn_"] button {
#         background: transparent !important;
#         border: none !important;
#         box-shadow: none !important;
#         color: inherit !important;
#         font-size: 1.75rem !important;
#         font-weight: 700 !important;
#         padding: 0 !important;
#         margin: 0 !important;
#         text-align: left !important;
#         justify-content: flex-start !important;
#         line-height: 1.2 !important;
#     }
#     div[class*="st-key-title_btn_"] button:hover {
#         color: #ff4b4b !important;
#         text-decoration: underline !important;
#         background: transparent !important;
#     }
#     </style>
#     """, unsafe_allow_html=True)

#     # Budowanie zapytania SQL
#     where_clauses = ["n.maks_liczba_osob >= :osoby"]
#     sql_params = {"osoby": st.session_state.search_osoby}
    
#     if st.session_state.search_miejsce.strip():
#         where_clauses.append("n.lokalizacja_miasto LIKE :miasto")
#         sql_params["miasto"] = f"%{st.session_state.search_miejsce.strip()}%"
        
#     where_clauses.append("n.cena_za_noc BETWEEN :cena_min AND :cena_max")
#     sql_params["cena_min"] = cena_min
#     sql_params["cena_max"] = cena_max
    
#     wybrane_typy = []
#     if f_hotel: wybrane_typy.append('Hotel')
#     if f_apartament: wybrane_typy.append('Apartament')
#     if f_b_and_b: wybrane_typy.append('B&B')
#     if f_schronisko: wybrane_typy.append('Schronisko')
#     if f_wynajem: wybrane_typy.append('Wynajem wakacyjny')

#     if wybrane_typy:
#         type_clauses = []
#         for idx, t in enumerate(wybrane_typy):
#             param_key = f"type_{idx}"
#             type_clauses.append(f":{param_key}")
#             sql_params[param_key] = t
#         where_clauses.append(f"n.typ_obiektu IN ({', '.join(type_clauses)})")

#     wybrane_udogodnienia = []
#     if u_jacuzzi: wybrane_udogodnienia.append('Jacuzzi')
#     if u_basen: wybrane_udogodnienia.append('Basen')
#     if u_spa: wybrane_udogodnienia.append('Spa')
#     if u_kuchnia: wybrane_udogodnienia.append('Aneks kuchenny/kuchnia')

#     if wybrane_udogodnienia:
#         for idx, u in enumerate(wybrane_udogodnienia):
#             u_param = f"u_param_{idx}"
#             sql_params[u_param] = u
#             where_clauses.append(f"""
#                 EXISTS (
#                     SELECT 1 FROM noclegi_udogodnienia nu
#                     JOIN udogodnienia ud ON nu.id_udogodnienia = ud.id_udogodnienia
#                     WHERE nu.id_noclegu = n.id_noclegu AND ud.nazwa = :{u_param}
#                 )
#             """)

#     if sort_option == "od najtańszych": order_by = "n.cena_za_noc ASC"
#     elif sort_option == "od najdroższych": order_by = "n.cena_za_noc DESC"
#     else: order_by = "n.srednia_ocena DESC"

#     query_szukaj = f"""
#     SELECT 
#         n.id_noclegu, n.nazwa, n.lokalizacja_miasto, n.lokalizacja_adres, n.opis, n.cena_za_noc, n.srednia_ocena,
#         n.szerokosc_geo, n.dlugosc_geo,
#         (SELECT TOP 1 url_zdjecia FROM zdjecia_noclegu WHERE id_noclegu = n.id_noclegu ORDER BY czy_glowne DESC) AS url_zdjecia
#     FROM noclegi n
#     WHERE {" AND ".join(where_clauses)}
#     ORDER BY {order_by}
#     """
    
#     try:
#         df_wyniki = conn.query(query_szukaj, params=sql_params, ttl=0)
        
#         if df_wyniki.empty:
#             st.info("Brak dostępnych ofert dla wybranych kryteriów.")
#         else:
#             search_map = build_search_map(df_wyniki)
            
#             if search_map is not None:
#                 with sidebar_map_container:
#                     st.markdown("#### Lokalizacja ofert")
#                     folium_static(search_map, width=320, height=280)
#                     st.markdown("---")
            
#             for _, row in df_wyniki.iterrows():
#                 card = st.container(border=True)
#                 with card:
#                     col_img, col_detale = st.columns([1.2, 2.5])
                    
#                     with col_img:
#                         if row['url_zdjecia']:
#                             foto_ready = wyswietl_zdjecie(row['url_zdjecia'], szerokosc=400, wysokosc=330)
#                             if foto_ready:
#                                 st.image(foto_ready, width='stretch')
#                             else:
#                                 st.markdown("<div class='surface-block' style='height: 160px;'></div>", unsafe_allow_html=True)
#                         else:
#                             st.markdown("<div class='surface-block' style='height: 160px;'></div>", unsafe_allow_html=True)
                            
#                     with col_detale:
#                         c_title, c_rating = st.columns([2.8, 1.2])
#                         with c_title:
#                             kliknieto_tytul = st.button(row['nazwa'], key=f"title_btn_{row['id_noclegu']}")
#                             st.caption(f"{row['lokalizacja_adres']}")
                        
#                         # --- SEKCOJA OCENY (ZBUDOWANA IDENTYCZNIE JAK W SZCZEGÓŁACH) ---
#                         with c_rating:
#                             ocena_val = row['srednia_ocena']
#                             if pd.isna(ocena_val) or ocena_val is None:
#                                 ocena_html = "<span style='color: #767676; font-size: 14px;'>Brak ocen</span>"
#                             else:
#                                 # Normalizacja wyświetlania (np. 4.5 lub 5 zamiast 5.0)
#                                 f_ocena = float(ocena_val)
#                                 str_ocena = f"{f_ocena:.1f}" if f_ocena % 1 != 0 else f"{int(f_ocena)}"
#                                 ocena_html = f"⭐ {str_ocena}/5"
                            
#                             st.markdown(f"""
#                                 <div style="display: flex; justify-content: flex-end; align-items: center; margin-top: 4px;">
#                                     <div class='rating-chip' style='margin: 0; font-size: 20px; font-weight: bold; line-height: 1;'>
#                                         {ocena_html}
#                                     </div>
#                                 </div>
#                             """, unsafe_allow_html=True)
#                         # -----------------------------------------------------------------
                        
#                         opis_skrócony = row['opis'] if row['opis'] else "Brak opisu obiektu."
#                         if len(opis_skrócony) > 160:
#                             opis_skrócony = opis_skrócony[:160] + "..."
#                         st.write(opis_skrócony)
                        
#                         st.markdown("<br>", unsafe_allow_html=True)
#                         c_space, c_price_btn = st.columns([2, 1])

#                         with c_price_btn:
#                             st.markdown(f"<div style='text-align: right; font-size: 1.4rem;'>{int(row['cena_za_noc'])} zł</div>", unsafe_allow_html=True)
#                             kliknieto_przycisk = st.button("Szczegóły", key=f"btn_{row['id_noclegu']}", width='stretch')
                    
#                     if kliknieto_tytul or kliknieto_przycisk:
#                         st.session_state.selected_nocleg_id = row['id_noclegu']
#                         st.query_params["id"] = str(row['id_noclegu']) 
#                         st.switch_page("pages/strona_noclegu.py")
                                        
#     except Exception as e:
#         st.error(f"Nie udało się załadować ofert. Błąd: {e}")

# render_page_footer()
import streamlit as st
import datetime
import pandas as pd
import folium
from streamlit_folium import folium_static
from urllib.parse import urlencode
from src.ui import render_page_header, render_page_footer
from src.utils import wyswietl_zdjecie

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
    "u_jacuzzi": pobierz_filtr("u_jacuzzi", False, lambda x: x == "True" or x is True),
    "u_basen": pobierz_filtr("u_basen", False, lambda x: x == "True" or x is True),
    "u_spa": pobierz_filtr("u_spa", False, lambda x: x == "True" or x is True),
    "u_kuchnia": pobierz_filtr("u_kuchnia", False, lambda x: x == "True" or x is True),
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
    
    with c1:
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
        czyste_miejsce = miejsce_input if miejsce_input is not None else ""
        
        st.query_params["miejsce"] = czyste_miejsce
        st.query_params["data_od"] = str(data_od_input)
        st.query_params["data_do"] = str(data_do_input)
        st.query_params["osoby"] = str(osoby_input)
        st.query_params["clicked"] = "True"
        
        if st.button("Szukaj", width='stretch', type="primary"):
            for klucz in ["cena_min", "cena_max"]:
                if klucz in st.query_params: del st.query_params[klucz]
            
            if "saved_filters" in st.session_state:
                st.session_state.saved_filters.pop("cena_min", None)
                st.session_state.saved_filters.pop("cena_max", None)
            
            st.session_state.filters_version += 1
            st.session_state.search_clicked = True
            st.session_state.search_miejsce = czyste_miejsce
            st.session_state.search_osoby = osoby_input
            st.session_state.search_data_od = data_od_input
            st.session_state.search_data_do = data_do_input
            st.rerun()

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
    u_jacuzzi = st.checkbox("Jacuzzi", value=url_filters["u_jacuzzi"], key=f"u_jacuzzi_{version}")
    u_basen = st.checkbox("Basen", value=url_filters["u_basen"], key=f"u_basen_{version}")
    u_spa = st.checkbox("Spa", value=url_filters["u_spa"], key=f"u_spa_{version}")
    u_kuchnia = st.checkbox("Aneks kuchenny/kuchnia", value=url_filters["u_kuchnia"], key=f"u_kuchnia_{version}")
    
    st.query_params["u_jacuzzi"] = str(u_jacuzzi)
    st.query_params["u_basen"] = str(u_basen)
    st.query_params["u_spa"] = str(u_spa)
    st.query_params["u_kuchnia"] = str(u_kuchnia)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Wyczyść filtry", width='stretch'):
        klucze_filtrow = [
            "sort", "cena_min", "cena_max", "f_hotel", "f_apartament", "f_b_and_b", 
            "f_schronisko", "f_wynajem", "f_p_darmowy", "f_p_platny", "f_p_brak",
            "u_jacuzzi", "u_basen", "u_spa", "u_kuchnia"
        ]
        for klucz in klucze_filtrow:
            if klucz in st.query_params: del st.query_params[klucz]
        st.session_state.filters_version += 1
        st.session_state.saved_filters = {}
        st.rerun()

st.session_state.saved_filters = {
    "sort": sort_option, "cena_min": cena_min, "cena_max": cena_max,
    "f_hotel": f_hotel, "f_apartament": f_apartament, "f_b_and_b": f_b_and_b,
    "f_schronisko": f_schronisko, "f_wynajem": f_wynajem, "f_p_darmowy": f_p_darmowy,
    "f_p_platny": f_p_platny, "f_p_brak": f_p_brak, "u_jacuzzi": u_jacuzzi,
    "u_basen": u_basen, "u_spa": u_spa, "u_kuchnia": u_kuchnia,
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
        
        if df_wyniki.empty:
            st.info("Brak dostępnych ofert dla wybranych kryteriów.")
        else:
            search_map = build_search_map(df_wyniki)
            
            if search_map is not None:
                with sidebar_map_container:
                    st.markdown("#### Lokalizacja ofert")
                    folium_static(search_map, width=320, height=280)
                    st.markdown("---")
            
            for _, row in df_wyniki.iterrows():
                card = st.container(border=True)
                with card:
                    col_img, col_detale = st.columns([1.2, 2.5])
                    
                    with col_img:
                        if row['url_zdjecia']:
                            foto_ready = wyswietl_zdjecie(row['url_zdjecia'], szerokosc=400, wysokosc=330)
                            if foto_ready:
                                st.image(foto_ready, width='stretch')
                            else:
                                st.markdown("<div class='surface-block' style='height: 160px;'></div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div class='surface-block' style='height: 160px;'></div>", unsafe_allow_html=True)
                            
                    with col_detale:
                        c_title, c_rating = st.columns([2.8, 1.2])
                        with c_title:
                            kliknieto_tytul = st.button(row['nazwa'], key=f"title_btn_{row['id_noclegu']}")
                            st.caption(f"{row['lokalizacja_adres']}")
                        
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
                                    <div class='rating-chip' style='margin: 0; font-size: 25px; font-weight: bold; line-height: 1;'>
                                        {ocena_html}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        opis_skrocony = row['opis'] if row['opis'] else "Brak opisu obiektu."
                        if len(opis_skrocony) > 160:
                            opis_skrocony = opis_skrocony[:200] + "..."

                        st.markdown(
                            f"""
                            <div style="
                                width: 40rem;
                                overflow-wrap: break-word;
                                word-wrap: break-word;
                            ">
                                {opis_skrocony}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        c_space, c_price_btn = st.columns([2, 1])

                        with c_price_btn:
                            st.markdown(f"<div style='text-align: right; font-size: 3rem;'>{int(row['cena_za_noc'])} zł</div>", unsafe_allow_html=True)
                            kliknieto_przycisk = st.button("Szczegóły", key=f"btn_{row['id_noclegu']}", width='stretch')
                    
                    if kliknieto_tytul or kliknieto_przycisk:
                        st.session_state.selected_nocleg_id = row['id_noclegu']
                        st.query_params["id"] = str(row['id_noclegu']) 
                        st.switch_page("pages/strona_noclegu.py")
                                        
    except Exception as e:
        st.error(f"Nie udało się załadować ofert. Błąd: {e}")

render_page_footer()