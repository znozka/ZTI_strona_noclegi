import streamlit as st
import datetime
import pandas as pd
from src.ui import render_page_header, render_page_footer
from src.utils import wyswietl_zdjecie

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
    page_title="Szczegóły noclegu",
    page_icon="assets/images/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Renderowanie nagłówka strony (wspólny element)
render_page_header()

# Połączenie z bazą danych
conn = st.connection("azure_sql", type="sql")

# cache unikalnych miast
@st.cache_data(ttl=3600)
def pobierz_unikalne_miasta():
    try:
        df_miasta = conn.query("SELECT DISTINCT lokalizacja_miasto FROM noclegi WHERE lokalizacja_miasto IS NOT NULL ORDER BY lokalizacja_miasto", ttl=0)
        return df_miasta["lokalizacja_miasto"].tolist()
    except Exception:
        return ["Gdańsk", "Kraków", "Katowice", "Poznań", "Warszawa", "Wrocław", "Łódź"]

lista_miast = pobierz_unikalne_miasta()

# Pobieranie parametrów z URL / Sesji
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

st.query_params["id"] = str(selected_id)
st.query_params["miejsce"] = str(st.session_state.search_miejsce)
st.query_params["data_od"] = str(st.session_state.search_data_od)
st.query_params["data_do"] = str(st.session_state.search_data_do)
st.query_params["osoby"] = str(st.session_state.search_osoby)
st.query_params["clicked"] = str(st.session_state.search_clicked)

# Określenie domyślnego indeksu dla selectboxa
domyslny_indeks = None
if st.session_state.get("search_miejsce") in lista_miast:
    domyslny_indeks = lista_miast.index(st.session_state.search_miejsce)
else:
    domyslny_indeks = None

# wyszukiwarka
search_container = st.container(border=True)
with search_container:
    c1, c2, c3, c4, c5 = st.columns([2.5, 1.2, 1.2, 1.2, 1])
    
    with c1:
        miejsce_input = st.selectbox(
            "Miejsce", 
            options=lista_miast,
            index=domyslny_indeks,
            placeholder="Wpisz miasto...", 
            key="details_search_miejsce"
        )
    with c2:
        data_od_input = st.date_input("Data od", value=st.session_state.search_data_od, key="details_date_od")
    with c3:
        data_do_input = st.date_input("Data do", value=st.session_state.search_data_do, key="details_date_do")
    with c4:
        osoby_input = st.number_input("Liczba osób", min_value=1, max_value=20, value=st.session_state.search_osoby, key="details_osoby")
    with c5:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Szukaj", width='stretch', type="primary", key="details_search_btn"):
            czyste_miejsce = miejsce_input if miejsce_input is not None else ""
            
            st.session_state.search_clicked = True
            st.session_state.search_miejsce = czyste_miejsce
            st.session_state.search_osoby = osoby_input
            st.session_state.search_data_od = data_od_input
            st.session_state.search_data_do = data_do_input

            # Zapisujemy komplet filtrów do URL
            st.query_params["miejsce"] = czyste_miejsce
            st.query_params["data_od"] = str(data_od_input)
            st.query_params["data_do"] = str(data_do_input)
            st.query_params["osoby"] = str(osoby_input)
            st.query_params["clicked"] = "True"
            
            # # Usuwamy id oglądanego noclegu, bo wracamy do listy wyników
            # if "id" in st.query_params:
            #     del st.query_params["id"]
                
            st.switch_page("pages/wyniki_wyszukiwania.py")

st.markdown("<br>", unsafe_allow_html=True)

# pobieranie i renderowanie danych noclegu
if selected_id is None:
    st.warning("Nie wybrano żadnego noclegu. Powróć do wyników wyszukiwania.")
    if st.button("Powrót do wyszukiwarki", width='stretch'):
        st.switch_page("pages/wyniki_wyszukiwania.py")
else:
    try:
        # Pobranie danych głównych noclegu
        query_nocleg = """
            SELECT id_noclegu, nazwa, opis, lokalizacja_miasto, lokalizacja_adres, cena_za_noc, srednia_ocena, liczba_opinii
            FROM noclegi
            WHERE id_noclegu = :id
        """
        df_nocleg = conn.query(query_nocleg, params={"id": selected_id}, ttl=0)
        
        if df_nocleg.empty:
            st.error("Nie znaleziono podanego noclegu w bazie danych.")
        else:
            nocleg = df_nocleg.iloc[0]
            
            # Pobranie wszystkich zdjęć dla danego noclegu
            query_zdjecia = """
                SELECT url_zdjecia, czy_glowne 
                FROM zdjecia_noclegu 
                WHERE id_noclegu = :id
                ORDER BY czy_glowne DESC, id_zdjecia ASC
            """
            df_zdjecia = conn.query(query_zdjecia, params={"id": selected_id}, ttl=0)
            lista_zdjec = df_zdjecia['url_zdjecia'].tolist() if not df_zdjecia.empty else []
            
            # Pobranie opinii o noclegu
            query_opinie = """
                SELECT o.ocena, o.komentarz, u.imie
                FROM opinie o
                JOIN uzytkownicy u ON o.id_turysty = u.id_uzytkownika
                WHERE o.id_noclegu = :id
                ORDER BY o.data_dodania DESC
            """
            df_opinie = conn.query(query_opinie, params={"id": selected_id}, ttl=0)
            
            # Nazwa i lokalizacja obiektu
            st.markdown(f"<h1 style='margin-bottom: 0px;'>{nocleg['nazwa']}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p class='text-muted' style='font-size: 1.1rem; margin-top: 5px;'>{nocleg['lokalizacja_miasto']}, {nocleg['lokalizacja_adres']}</p>", unsafe_allow_html=True)
            
            # Podział ekranu na sekcję główną (zdjęcia) i panel boczny (opinie + mapa)
            col_main, col_side = st.columns([2.8, 1.2])
            
            with col_main:
                # Przygotowanie placeholderów na zdjęcia (wymagane 6 zdjęć do makiety)
                while len(lista_zdjec) < 6:
                    lista_zdjec.append(None)
                
                # Funkcja pomocnicza do renderowania małych zdjęć (dolny wiersz i boczny panel)
                def render_photo(url):
                    # Wymuszamy stały wymiar 400x250 dla małych zdjęć
                    foto_ready = wyswietl_zdjecie(url, szerokosc=400, wysokosc=250)
                    if foto_ready:
                        st.image(foto_ready, width='stretch')
                    else:
                        st.markdown(
                            "<div class='surface-block surface-block-small'></div>", 
                            unsafe_allow_html=True
                        )
                        
                # WIERSZ 1: Duże zdjęcie + 2 małe obok
                img_row_1 = st.columns([2, 1])
                
                with img_row_1[0]:
                    # Duże zdjęcie po lewej stronie (wymiar dopasowany geometrycznie: 800x510)
                    foto_duze = wyswietl_zdjecie(lista_zdjec[0], szerokosc=800, wysokosc=510)
                    if foto_duze:
                        st.image(foto_duze, width='stretch')
                    else:
                        st.markdown(
                            "<div class='surface-block surface-block-large'></div>", 
                            unsafe_allow_html=True
                        )
                
                with img_row_1[1]:
                    # Dwa mniejsze zdjęcia po prawej stronie dużego zdjęcia
                    render_photo(lista_zdjec[1])
                    render_photo(lista_zdjec[2])
                
                # WIERSZ 2: Dolny wiersz zdjęć: 3 równe kolumny
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True) # Delikatna przerwa pionowa
                img_row_2 = st.columns([1, 1, 1])
                
                with img_row_2[0]:
                    render_photo(lista_zdjec[3])
                with img_row_2[1]:
                    render_photo(lista_zdjec[4])
                with img_row_2[2]:
                    render_photo(lista_zdjec[5])

            with col_side:
                # Panel Opinie
                opinie_box = st.container(border=True)
                with opinie_box:
                    head_l, head_r = st.columns([2, 1])
                    with head_l:
                        st.markdown("### Opinie")
                    with head_r:
                        st.markdown(
                            f"<div class='rating-chip'>⭐ {nocleg['srednia_ocena']}/5</div>", 
                            unsafe_allow_html=True
                        )
                    st.markdown("---")
                    
                    if not df_opinie.empty:
                        for _, opinia in df_opinie.head(2).iterrows():
                            st.markdown(f"**{opinia['ocena']}/5** ({opinia['imie']})")
                            st.caption(opinia['komentarz'])
                            st.markdown("<br>", unsafe_allow_html=True)
                    else:
                        st.markdown("**5/5**")
                        st.caption("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse suscipit ligula nec arcu elementum vehicula. Sed et aliquam urna, ut tincidunt diam.")
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("**3/5**")
                        st.caption("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse suscipit ligula.")
            
                # Pusty blok zarezerwowany na mapę zgodnie z wytycznymi makiety
                map_box = st.container(border=True)
                with map_box:
                    st.markdown("<div class='text-muted' style='text-align: center; padding: 40px 0;'>[ Miejsce na mapę ]</div>", unsafe_allow_html=True)

            # Opis obiektu pod zdjęciami na pełną szerokość
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Opis obiektu")
            if nocleg['opis'] and nocleg['opis'].strip():
                st.write(nocleg['opis'])
            else:
                st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse suscipit ligula nec arcu elementum vehicula. Sed et aliquam urna, ut tincidunt diam. Cras rutrum dui turpis, sed placerat velit accumsan et. Cras mattis convallis ipsum. Aliquam erat volutpat. Donec laoreet, libero non egestas malesuada, nisi lorem blandit est, eu blandit nunc diam sit amet libero. Sed eu arcu sagittis, ultrices est eu, ultrices lectus. Proin congue, elit nec efficitur ultrices, nulla lorem interdum nibh, et iaculis nulla ante a nulla. Aenean pharetra congue erat non gravida.")

    except Exception as e:
        st.error(f"Nie udało się załadować danych noclegu. Błąd: {e}")

# Renderowanie stopki strony (wspólny element)
render_page_footer()
