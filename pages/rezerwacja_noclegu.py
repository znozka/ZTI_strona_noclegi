import streamlit as st
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import json
import os

def st_custom_date_picker(label, zajete_daty):

    import json
    import streamlit.components.v1 as components

    zajete = [
        d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)
        for d in zajete_daty
    ]

    html = f"""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
    <script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
    <script src="https://unpkg.com/streamlit-component-lib/dist/streamlit-component-lib.js"></script>

    <input id="picker" style="width:100%;padding:10px;" placeholder="{label}" />

    <script>
        const disabled = {json.dumps(zajete)};

        flatpickr("#picker", {{
            mode: "range",
            minDate: "today",
            dateFormat: "Y-m-d",
            disable: disabled,

            onChange: function(sel) {{
                if(sel.length === 2) {{
                    Streamlit.setComponentValue({{
                        start: sel[0].toISOString().slice(0,10),
                        end: sel[1].toISOString().slice(0,10)
                    }});
                }}
            }}
        }});
    </script>
    """

    return components.html(html, height=420)

# Tymczasowe dane #
# Obiekt
OBIEKT = {
    "id": 101,
    "nazwa": "Apartament Widokowy Giewont",
    "cena_za_noc": 250,
    "max_osob": 4
}

# Symulacja zajętych terminów w bazie danych
dzis = datetime.today().date()
ZAJETE_DATY = [
    dzis + timedelta(days=2),
    dzis + timedelta(days=3),
    dzis + timedelta(days=4),
    dzis + timedelta(days=10),
    dzis + timedelta(days=11),
]

if "search_check_in" not in st.session_state:
    st.session_state.search_check_in = dzis
if "search_check_out" not in st.session_state:
    st.session_state.search_check_out = dzis + timedelta(days=1)
if "search_guests" not in st.session_state:
    st.session_state.search_guests = 2

# Interfejs użytkownika
st.title("Bezpieczna Rezerwacja Noclegu")
st.subheader(f"Rezerwujesz: {OBIEKT['nazwa']}")
st.caption(f"Cena bazowa: {OBIEKT['cena_za_noc']} PLN / doba | Maksymalna liczba gości: {OBIEKT['max_osob']}")

st.markdown("---")

# Formularz rezerwacji
with st.form("formularz_rezerwacji"):
    st.write("### Szczegóły twojego pobytu")

    col_daty, col_osoby = st.columns([2, 1])

    with col_daty:
        wybrane_daty = st_custom_date_picker(
            label="Wybierz termin pobytu (zameldowanie i wymeldowanie)",
            zajete_daty=ZAJETE_DATY
        )

    with col_osoby:
        liczba_gosci = st.number_input(
            "Liczba osób",
            min_value=1,
            max_value=OBIEKT["max_osob"],
            value=st.session_state.search_guests
        )

    # Dodatkowa sekcja 
    st.write("### Dodatki do pobytu")
    col_snadanie, col_parking, col_zwierze = st.columns(3)

    with col_snadanie:
        # Zmieniono nazwę na 'sniadanie' dla spójności z kalkulatorem kosztów
        sniadanie = st.checkbox("Śniadanie kontynentalne (+50 PLN / doba)")
    with col_parking:
        parking = st.checkbox("Miejsce parkingowe (+30 PLN / doba)")
    with col_zwierze:
        zwierze = st.checkbox("Pobyt ze zwierzęciem (+100 PLN jednorazowo)")

    st.markdown("<br>", unsafe_allow_html=True)

    przycisk_zarezerwuj = st.form_submit_button("Zarezerwuj", use_container_width=True)

if przycisk_zarezerwuj:
    poprawny_zakres = False
    data_od = None
    data_do = None
    liczba_nocy = 0
    st.write(datetime.strptime(wybrane_daty["start"], "%Y-%m-%d").date())
    # 1. SPRAWDZENIE I WALIDACJA DAT
    if wybrane_daty and isinstance(wybrane_daty, dict):
        # Wyciągamy teksty i zamieniamy je z powrotem na obiekty datetime.date
        data_od = datetime.strptime(wybrane_daty["start"], "%Y-%m-%d").date()
        data_do = datetime.strptime(wybrane_daty["end"], "%Y-%m-%d").date()
    
        if data_od < data_do:
            poprawny_zakres = True
            liczba_nocy = (data_do - data_od).days
        else:
            st.error("❌ Data wyjazdu musi być późniejsza niż data przyjazdu.")
    else:
        st.error("❌ Proszę wybrać pełny zakres dat na kalendarzu.")

    # 2. SEKCJA KALKULACJI (Uruchamia się TYLKO, gdy zakres jest poprawny)
    if poprawny_zakres:
        koszt_pobytu = liczba_nocy * OBIEKT["cena_za_noc"]
        
        # Uwzględnienie kosztu dodatków
        koszt_dodatkow = (
            (50 * liczba_nocy * liczba_gosci if sniadanie else 0) + 
            (30 * liczba_nocy if parking else 0) +
            (100 if zwierze else 0)
        )
        
        status_rezerwacji = "Oczekuje na płatność"
        sum_total = koszt_pobytu + koszt_dodatkow

        st.success("🎉 Wirtualna rezerwacja utworzona pomyślnie!")

        st.markdown(f"""
        ### Podsumowanie rezerwacji (MOCK)
        * **Obiekt:** {OBIEKT['nazwa']}
        * **Termin:** {data_od} do {data_do} ({liczba_nocy} nocy)
        * **Liczba gości:** {liczba_gosci} os.
        * **Status rezerwacji:** `{status_rezerwacji}` ⏳

        ### Kosztorys:
        * Wynajem obiektu: **{koszt_pobytu} PLN**
        * Usługi dodatkowe: **{koszt_dodatkow} PLN**
        * **Razem do zapłaty: {sum_total} PLN**
        """)

# Przycisk powrotu całkowicie poza blokiem formularza rezerwacji
st.markdown("<br>", unsafe_allow_html=True)
if st.button("Wróć do panelu głównego", use_container_width=True):
    st.switch_page("app.py")


# import streamlit as st
# from datetime import datetime, timedelta

# OBIEKT = {
#     "nazwa": "Apartament Widokowy Giewont",
#     "cena_za_noc": 250,
#     "max_osob": 4
# }

# dzis = datetime.today().date()

# ZAJETE_DATY = {
#     dzis + timedelta(days=2),
#     dzis + timedelta(days=3),
#     dzis + timedelta(days=4),
#     dzis + timedelta(days=10),
# }

# st.title("Rezerwacja noclegu")
# st.subheader(OBIEKT["nazwa"])

# col1, col2 = st.columns(2)

# with col1:
#     zakres = st.date_input(
#         "Wybierz termin pobytu",
#         value=(dzis, dzis + timedelta(days=1)),
#         min_value=dzis
#     )

# if isinstance(zakres, tuple) and len(zakres) == 2:
#     data_od, data_do = zakres

#     if data_od >= data_do:
#         st.error("Zły zakres dat")
#         st.stop()

#     dni = (data_do - data_od).days
# else:
#     st.error("Wybierz pełny zakres dat")
#     st.stop()

# def czy_kolizja(start, end, zajete):
#     d = start
#     while d < end:
#         if d in zajete:
#             return True
#         d += timedelta(days=1)
#     return False

# if czy_kolizja(data_od, data_do, ZAJETE_DATY):
#         st.error("Ten termin jest zajęty")
#         st.stop()

# with st.form("form"):

#     osoby = st.number_input("Liczba osób", 1, 10, 2)

#     sniadanie = st.checkbox("Śniadanie")
#     parking = st.checkbox("Parking")
#     zwierze = st.checkbox("Zwierzę")

#     submit = st.form_submit_button("Rezerwuj")

# if submit:

#     koszt_noclegu = dni * 250

#     koszt_dodatkow = (
#         (50 * dni * osoby if sniadanie else 0) +
#         (30 * dni if parking else 0) +
#         (100 if zwierze else 0)
#     )

#     st.success("Rezerwacja OK!")

#     st.write("Od:", data_od)
#     st.write("Do:", data_do)
#     st.write("Noce:", dni)
#     st.write("Razem:", koszt_noclegu + koszt_dodatkow)






