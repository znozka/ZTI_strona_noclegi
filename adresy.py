import streamlit as st
import time
from geopy.geocoders import Nominatim
from sqlalchemy import text

# Inicjalizacja połączenia
conn = st.connection("azure_sql", type="sql")
geolocator = Nominatim(user_agent="geokodowanie_noclegow_app")

def sformatuj_adres_ujednolicony(raw_address):
    """
    Formatuje adres w sposób spójny: ul. Ulica Numer, Miasto
    Dzielnice są pomijane w celu zachowania czytelności.
    """
    ulica = raw_address.get('road', 'Nieznana ulica')
    nr = raw_address.get('house_number', '')
    miasto = raw_address.get('city', raw_address.get('town', raw_address.get('village', 'Kraków')))
    
    # Składamy w format: ul. Nazwa Nr, Miasto
    return f"ul. {ulica} {nr}, {miasto}".strip()

def geokoduj_i_zapisz():
    # Pobieramy rekordy wymagające uzupełnienia
    query = """
    SELECT id_noclegu, szerokosc_geo, dlugosc_geo 
    FROM noclegi 
    WHERE (lokalizacja_adres = 'Brak adresu w API' OR lokalizacja_adres IS NULL)
    AND szerokosc_geo IS NOT NULL AND dlugosc_geo IS NOT NULL
    """
    df_do_poprawy = conn.query(query)
    
    if df_do_poprawy.empty:
        st.info("Wszystkie adresy są już uzupełnione!")
        return

    progress_bar = st.progress(0)
    total = len(df_do_poprawy)

    for i, (index, row) in enumerate(df_do_poprawy.iterrows()):
        coords = f"{row['szerokosc_geo']}, {row['dlugosc_geo']}"
        
        # Konwersja ID na integer, aby uniknąć 21.0
        nocleg_id = int(row['id_noclegu'])
        
        try:
            location = geolocator.reverse(coords, timeout=10)
            if location and location.raw.get('address'):
                nowy_adres = sformatuj_adres_ujednolicony(location.raw['address'])
                
                with conn.session as s:
                    s.execute(
                        text("UPDATE noclegi SET lokalizacja_adres = :adres WHERE id_noclegu = :id"),
                        {"adres": nowy_adres, "id": nocleg_id}
                    )
                    s.commit()
                st.write(f"Zaktualizowano ID {nocleg_id}")
            
            # ZWIĘKSZ CZAS OPOŹNIENIA do 1.5 sekundy, żeby być bezpiecznym
            time.sleep(1.5) 
            
        except Exception as e:
            st.error(f"Błąd przy ID {nocleg_id}: {e}")

    st.success("Zakończono aktualizację adresów!")

# Wywołanie w interfejsie Streamlit
if st.button("Ujednolic i uzupełnij adresy"):
    geokoduj_i_zapisz()
