import logging
import warnings
import streamlit as st
import time
from sqlalchemy import text

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
    page_title="Płatności",
    page_icon="assets/images/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
        div[data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
        
        header[data-testid="stHeader"] button {
            display: none !important;
        }
        
        section[data-testid="stSidebar"] {
            display: none !important;
            width: 0px !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

conn = st.connection("azure_sql", type="sql")

st.title("Bramka Płatnicza")
st.write("Dokończ rezerwację korzystając z szybkiej płatności BLIK")

st.markdown("""
    <style>
        .blik-container {
            background-color: #ffffff;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
        }
        .blik-logo {
            font-size: 32px;
            font-weight: bold;
            color: #484848;
            margin-bottom: 10px;
        }
        .blik-dot {
            color: #E30613; /* Charakterystyczny czerwony kolor BLIK */
        }
    </style>
""", unsafe_allow_html=True)

id_turysty = st.session_state.get("user_id")
# if not id_turysty:
#     st.error("Błąd autoryzacji. Musisz być zalogowany.")
#     st.stop()

try:
    with conn.session as session:
        query_rez = """
            SELECT TOP 1 id_rezerwacji, calkowita_cena 
            FROM rezerwacje 
            WHERE id_turysty = :id_turysty AND status = 'oczekuje_na_platnosc'
            ORDER BY data_utworzenia DESC
        """
        result = session.execute(text(query_rez), {"id_turysty": int(id_turysty)}).fetchone()

    if result:
        id_rezerwacji = int(result[0])
        kwota = float(result[1])

        query_platnosc_check = """
            SELECT id_platnosci FROM platnosci WHERE id_rezerwacji = :id_rez
        """
        platnosc_exists = session.execute(text(query_platnosc_check), {"id_rez": id_rezerwacji}).fetchone()

        query_insert_platnosc = """
            INSERT INTO platnosci (id_rezerwacji, metoda_platnosci, kwota, status)
            VALUES (:id_rez, 'BLIK', :kwota, 'rozpoczeta')
        """
        if not platnosc_exists:
            session.execute(text(query_insert_platnosc), {"id_rez": id_rezerwacji, "kwota": kwota})
            session.commit()

    else:
        st.warning("Nie znaleziono żadnych rezerwacji oczekujących na płatność.")
        if st.button("Wróć do aplikacji"):
            st.switch_page("app.py")
        st.stop()

except Exception as e:
    st.error(f"Błąd bazy danych: {e}")
    st.stop()




st.markdown(f"""
    <div class="blik-container">
        <div class="blik-logo">b<span class="blik-dot">l</span>ik</div>
        <p style="font-size: 18px; color: #555;">Kwota do zapłaty: <b>{kwota:.2f} PLN</b></p>
        <p style="font-size: 14px; color: #888;">Rezerwacja numer: #{id_rezerwacji}</p>
    </div>
""", unsafe_allow_html=True)

# Formularz wprowadzania kodu BLIK
with st.form("formularz_blik"):
    kod_blik = st.text_input(
        "Wprowadź 6-cyfrowy kod BLIK:", 
        max_chars=6, 
        placeholder="X X X   X X X",
        help="Wpisz kod wygenerowany w aplikacji bankowej."
    )
    
    submit_button = st.form_submit_button("Zapłać teraz", use_container_width=True, type="primary")

if submit_button:
    if len(kod_blik) == 6 and kod_blik.isdigit():
        
        with st.status("🔄 Łączenie z bankiem... Oczekuję na akceptację w Twojej aplikacji...", expanded=True) as status:
            time.sleep(2)
            status.update(label="✅ Płatność autoryzowana!", state="complete", expanded=False)
        
        try:
            atrapa_transakcji_id = f"T-BLIK-{int(time.time())}"

            query_update_platnosc = """
                UPDATE platnosci
                SET status = 'sukces',
                    id_transakcji_zewnetrznej = :id_transakcji,
                    data_platnosci = GETDATE()
                WHERE id_rezerwacji = :id_rez
            """
            query_update_rezerwacja = """
                UPDATE rezerwacje 
                SET status = 'potwierdzona' 
                WHERE id_rezerwacji = :id_rez
            """
            with conn.session as session:
                session.execute(text(query_update_platnosc), {
                    "id_rez": id_rezerwacji,
                    "id_transakcji": atrapa_transakcji_id
                })
                session.execute(text(query_update_rezerwacja), {
                    "id_rez": id_rezerwacji
                })
                session.commit()
            
            st.success("Płatność zakończona sukcesem! Twoja rezerwacja została potwierdzona.")
            
            st.session_state.rezerwacja_kliknieta = False
            st.session_state.pokaz_podsumowanie = False
            
            time.sleep(7)
            st.switch_page("app.py")
            
        except Exception as e:
            st.error(f"Błąd podczas aktualizacji statusu rezerwacji: {e}")
            
    else:
        st.error("Niepoprawny kod BLIK. Kod musi składać się z dokładnie 6 cyfr.")


st.markdown("<br>", unsafe_allow_html=True)
if st.button("Anuluj i wróć", use_container_width=True, type="secondary"):
    st.switch_page("app.py")