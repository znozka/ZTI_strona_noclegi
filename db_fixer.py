import pyodbc
import traceback
import sys

# Konfiguracja połączenia
CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=database-zti.database.windows.net,1433;"
    "DATABASE=NoclegiDB_2026-05-26T20-19Z;"
    "UID=Zuza;"
    "PWD=haslo.Admin;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

def inicjalizuj_tabele_odpowiedzi():
    query = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='odpowiedzi_wlasciciela' AND xtype='U')
    BEGIN
        CREATE TABLE odpowiedzi_wlasciciela (
            id_odpowiedzi INT IDENTITY(1,1) PRIMARY KEY,
            id_opinii INT NOT NULL UNIQUE,
            tresc NVARCHAR(MAX) NOT NULL,
            data_dodania DATETIME DEFAULT GETDATE(),
            CONSTRAINT FK_odp_opinia FOREIGN KEY (id_opinii) REFERENCES opinie(id_opinii) ON DELETE CASCADE
        )
        SELECT 1 AS Stan; -- Tabela została utworzona
    END
    ELSE
    BEGIN
        SELECT 0 AS Stan; -- Tabela już istniała
    END
    """
    
    conn = None
    try:
        print("[1/4] Próba nawiązania połączenia z bazą Azure SQL...")
        # Ustalamy krótki timeout (np. 10 sekund), żeby skrypt nie wisiał w nieskończoność przy braku IP w firewallu
        conn = pyodbc.connect(CONNECTION_STRING, timeout=10)
        print("[2/4] Połączenie ustanowione pomyślnie.")
        
        print("[3/4] Wykonywanie zapytania SQL (sprawdzanie/tworzenie tabeli)...")
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Pobieramy wynik z SELECT, który dodaliśmy do query
        wynik = cursor.fetchone()
        conn.commit()
        print("[4/4] Zmiany zostały zatwierdzone w bazie danych.")
        
        print("\n--- STATUS OPERACJI ---")
        if wynik and wynik[0] == 1:
            print("Sukces: Tabela 'odpowiedzi_wlasciciela' nie istniała i została UTWORZONA.")
        else:
            print("Informacja: Tabela 'odpowiedzi_wlasciciela' JUŻ ISTNIEJE w bazie danych. Nic nie zmieniono.")
        print("-----------------------")

    except pyodbc.OperationalError as e:
        print("\n[BŁĄD POŁĄCZENIA] Nie udało się połączyć z bazą danych!")
        print("Sprawdź: 1) Czy Twój adres IP jest dodany w Firewallu Azure? 2) Czy masz internet? 3) Czy login/hasło są poprawne?")
        print("\nSzczegóły błędu:")
        traceback.print_exc()
        
    except Exception as e:
        print(f"\n[BŁĄD KRYTYCZNY] Wystąpił nieoczekiwany błąd podczas działania skryptu:")
        print("\nSzczegóły błędu:")
        traceback.print_exc()
        
    finally:
        if conn:
            print("\nZamykanie połączenia z bazą danych...")
            conn.close()
            print("Połączenie zamknięte.")

if __name__ == "__main__":
    print("Rozpoczęcie działania skryptu db_fixer.py\n")
    inicjalizuj_tabele_odpowiedzi()
    print("\nZakończono działanie skryptu.")