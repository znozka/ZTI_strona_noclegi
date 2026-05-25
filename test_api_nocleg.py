# import streamlit as st
from src.database import fetch_and_sync_hotels_from_serpapi

print("[TEST] Uruchamiam skrypt testowy API...")

try:
    conn = st.connection("azure_sql", type="sql")
    print("[TEST] Połączenie z Azure SQL nawiązane prawidłowo.")
except Exception as e:
    print(f"[TEST] BŁĄD: Nie można połączyć się z bazą danych: {e}")
    exit(1)

API_KEY = "e774a85944636029ae51a815780a6058c0726e47040c8d68a61c665089c128c9" 

MIASTO = "Wroclaw"
DATA_IN = "2026-06-15"   
DATA_OUT = "2026-09-02"

try:
    wynik = fetch_and_sync_hotels_from_serpapi(
        conn=conn, 
        api_key=API_KEY, 
        q=MIASTO, 
        check_in_date=DATA_IN, 
        check_out_date=DATA_OUT
    )
    print(f"[TEST] SUKCES! Zapisano {wynik} hoteli w bazie danych.")
except Exception as e:
    print(f"[TEST] Wystąpił błąd podczas wykonywania funkcji: {e}")



