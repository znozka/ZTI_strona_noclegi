import requests
import pandas as pd
import streamlit as st
import bcrypt
from sqlalchemy import text

def get_user_by_email(conn, email):
    """
    Pobiera dane użytkownika z bazy Azure SQL na podstawie adresu e-mail.
    Zwraca obiekt wiersza (np. z polami id_uzytkownika, imie, haslo_hash, rola)
    lub None, jeśli użytkownik nie istnieje.
    """
    # USUNIĘTO text(...) - przekazujemy czysty string
    query = """
        SELECT id_uzytkownika, email, haslo_hash, imie, nazwisko, rola 
        FROM uzytkownicy 
        WHERE email = :email
    """

    df = conn.query(query, params={"email": email}, ttl=0)
    
    if df.empty:
        return None

    return df.iloc[0]


def check_password(password, hashed_password):
    """
    Weryfikuje, czy podane hasło w czystym tekście pasuje do hasha z bazy danych.
    """
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


def register_user(conn, email, password, imie, nazwisko):
    """
    Rejestruje nowego użytkownika w bazie danych.
    Najpierw sprawdza, czy e-mail jest już zajęty.
    Hasło przed zapisem jest bezpiecznie haszowane za pomocą bcrypt.
    Zwraca True w przypadku sukcesu, False jeśli e-mail już istnieje.
    """
    # 1. Sprawdzenie duplikatu
    existing_user = get_user_by_email(conn, email)
    if existing_user is not None:
        return False
        
    # 2. Haszowanie hasła
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    # 3. Zapis do bazy w bezpiecznej transakcji 
    insert_query = text("""
        INSERT INTO uzytkownicy (email, haslo_hash, imie, nazwisko, rola)
        VALUES (:email, :haslo_hash, :imie, :nazwisko, 'turysta')
    """)
    
    with conn.session as session:
        session.execute(
            insert_query, 
            {
                "email": email, 
                "haslo_hash": hashed_password, 
                "imie": imie, 
                "nazwisko": nazwisko
            }
        )
        session.commit()
        
    return True

def fetch_and_sync_hotels_from_serpapi(conn, api_key, q, check_in_date, check_out_date):
    """
    Pobiera dane o hotelach z SerpAPI (Google Hotels) i zapisuje pełne informacje
    wraz ze zdjęciami oraz udogodnieniami do bazy danych Azure SQL.
    """
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_hotels",
        "q": q,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "api_key": api_key,
        "currency": "PLN",
        "hl": "pl"  
    }

    print(f"[DEBUG] Wysyłam zapytanie do SerpAPI dla miasta: {q}...")
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Błąd SerpAPI: {response.status_code} - {response.text}")
        
    data = response.json()
    properties = data.get("properties", [])
    
    if not properties:
        print("[DEBUG] SerpAPI nie zwróciło żadnych hoteli dla podanych kryteriów.")
        return 0

    saved_count = 0

    with conn.session as session:
        user_check = session.execute(text("SELECT TOP 1 id_uzytkownika FROM uzytkownicy")).fetchone()
        if user_check:
            id_wlasciciela = user_check[0]
        else:
            session.execute(text("""
                INSERT INTO uzytkownicy (email, haslo_hash, imie, nazwisko, rola) 
                VALUES ('system@innsight.pl', 'hash', 'System', 'Admin', 'admin')
            """))
            id_wlasciciela = session.execute(text("SELECT @@IDENTITY")).fetchone()[0]

        for hotel in properties:
            nazwa = hotel.get("name")
            typ_obiektu = hotel.get("type", "Hotel")
            lokalizacja_miasto = q
            lokalizacja_adres = hotel.get("address", "Brak adresu w API")

            gps = hotel.get("gps_coordinates", {})
            szerokosc_geo = gps.get("latitude")
            dlugosc_geo = gps.get("longitude")

            rate_info = hotel.get("rate_per_night", {})
            cena_za_noc = rate_info.get("extracted_lowest") or rate_info.get("lowest") or 150.00

            srednia_ocena = hotel.get("overall_rating", 0.00)
            liczba_opinii = hotel.get("reviews", 0)
            
            maks_liczba_osob = 2 

            check_hotel = session.execute(
                text("SELECT id_noclegu FROM noclegi WHERE nazwa = :nazwa AND lokalizacja_miasto = :miasto"),
                {"nazwa": nazwa, "miasto": lokalizacja_miasto}
            ).fetchone()

            if check_hotel:
                id_noclegu = check_hotel[0]
            else:
                insert_nocleg = text("""
                    INSERT INTO noclegi (id_wlasciciela, nazwa, opis, typ_obiektu, lokalizacja_miasto, lokalizacja_adres, szerokosc_geo, dlugosc_geo, cena_za_noc, maks_liczba_osob, srednia_ocena, liczba_opinii)
                    VALUES (:id_wlasciciela, :nazwa, :opis, :typ_obiektu, :lokalizacja_miasto, :lokalizacja_adres, :szerokosc_geo, :dlugosc_geo, :cena_za_noc, :maks_liczba_osob, :srednia_ocena, :liczba_opinii)
                """)
                session.execute(insert_nocleg, {
                    "id_wlasciciela": id_wlasciciela, "nazwa": nazwa, "opis": hotel.get("description", ""),
                    "typ_obiektu": typ_obiektu, "lokalizacja_miasto": lokalizacja_miasto, "lokalizacja_adres": lokalizacja_adres,
                    "szerokosc_geo": szerokosc_geo, "dlugosc_geo": dlugosc_geo, "cena_za_noc": cena_za_noc,
                    "maks_liczba_osob": maks_liczba_osob, "srednia_ocena": srednia_ocena, "liczba_opinii": liczba_opinii
                })

                id_noclegu = session.execute(text("SELECT @@IDENTITY")).fetchone()[0]
                saved_count += 1

            images = hotel.get("images", [])
            for idx, img in enumerate(images):
                url_img = img.get("thumbnail")
                if url_img:
                    check_img = session.execute(
                        text("SELECT id_zdjecia FROM zdjecia_noclegu WHERE id_noclegu = :id AND url_zdjecia = :url"),
                        {"id": id_noclegu, "url": url_img}
                    ).fetchone()
                    
                    if not check_img:
                        czy_glowne = 1 if idx == 0 else 0
                        session.execute(text("""
                            INSERT INTO zdjecia_noclegu (id_noclegu, url_zdjecia, czy_glowne)
                            VALUES (:id_noclegu, :url_zdjecia, :czy_glowne)
                        """), {"id_noclegu": id_noclegu, "url_zdjecia": url_img, "czy_glowne": czy_glowne})

            amenities = hotel.get("amenities", [])
            for amenity_name in amenities:
                if amenity_name:
                    check_amenity = session.execute(
                        text("SELECT id_udogodnienia FROM udogodnienia WHERE nazwa = :nazwa"),
                        {"nazwa": amenity_name}
                    ).fetchone()
                    
                    if check_amenity:
                        id_udogodnienia = check_amenity[0]
                    else:
                        session.execute(text("INSERT INTO udogodnienia (nazwa) VALUES (:nazwa)"), {"nazwa": amenity_name})
                        id_udogodnienia = session.execute(text("SELECT @@IDENTITY")).fetchone()[0]

                    check_link = session.execute(text("""
                        SELECT id_noclegu FROM noclegi_udogodnienia 
                        WHERE id_noclegu = :id_noclegu AND id_udogodnienia = :id_udogodnienia
                    """), {"id_noclegu": id_noclegu, "id_udogodnienia": id_udogodnienia}).fetchone()
                    
                    if not check_link:
                        session.execute(text("""
                            INSERT INTO noclegi_udogodnienia (id_noclegu, id_udogodnienia)
                            VALUES (:id_noclegu, :id_udogodnienia)
                        """), {"id_noclegu": id_noclegu, "id_udogodnienia": id_udogodnienia})

        session.commit()
    return saved_count

def get_available_rooms(conn, date_start, date_end):
    query = "SELECT * FROM Pokoje WHERE id NOT IN (...)"
    return conn.query(query)

import os
def get_and_save_serpapi_cities_to_file(api_key, filename="miasta.txt", limit=20):
    url_loc = "https://serpapi.com/locations.json"
    params = {
        "q": "Poland",
        "limit": 100
    }
    
    existing_cities = set()
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing_cities = {line.strip() for line in f if line.strip()}

    print(f"[API] Pobieram nowe propozycje miast z SerpAPI...")
    try:
        response = requests.get(url_loc, params=params)
        if response.status_code != 200:
            print(f"[BŁĄD] Nie udało się pobrać danych z API (Status: {response.status_code})")
            return list(existing_cities)
            
        locations = response.json()

        new_cities_added = 0
        
        with open(filename, "a", encoding="utf-8") as f:
            for loc in locations:
                
                country_code = loc.get("country_code")
                
                if country_code == "PL":
                    full_name = loc.get("name", "")
                    if not full_name:
                        continue

                    city_name = full_name.split(",")[0].strip()

                    if city_name.lower() == "poland":
                        continue
                    
                    if city_name and city_name not in existing_cities:
                        f.write(f"{city_name}\n")
                        existing_cities.add(city_name)
                        new_cities_added += 1
                        
                    if new_cities_added >= limit:
                        break
                        
        print(f"[TXT] Synchronizacja pliku zakończona. Dopisałem {new_cities_added} nowych miast do '{filename}'.")
        
    except Exception as e:
        print(f"[BŁĄD] Problem podczas zapisu do pliku: {e}")
        
    return sorted(list(existing_cities))

def update_user_password(conn, user_id, new_password_hash):
    try:
        with conn.session as session:

            query = text("""
                UPDATE uzytkownicy 
                SET haslo_hash = :password_hash 
                WHERE id_uzytkownika = :user_id
            """)
            session.execute(query, {"password_hash": new_password_hash, "user_id": user_id})
            session.commit()
        return True
    except Exception as e:
        st.error(f"Szczegóły błędu bazy danych: {e}")
        return False
    
def hash_password(password: str) -> str:
    """
    Haszuje hasło za pomocą biblioteki bcrypt w dokładnie taki sam sposób,
    w jaki odbywa się to podczas rejestracji użytkownika.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


# =========================================================================
# FUNKCJE DLA STRONY "MOJE KONTO"
# =========================================================================

def get_user_profile(conn, user_id):
    """
    Pobiera profil użytkownika na podstawie jego ID.
    Zwraca Series z danymi: id_uzytkownika, email, imie, nazwisko, telefon, rola, data_rejestracji
    """
    user_id = int(user_id)
    query = """
        SELECT id_uzytkownika, email, imie, nazwisko, telefon, rola, data_rejestracji
        FROM uzytkownicy
        WHERE id_uzytkownika = :user_id
    """
    df = conn.query(query, params={"user_id": user_id}, ttl=0)
    return df.iloc[0] if not df.empty else None


def get_user_reservations(conn, user_id):
    """
    Pobiera wszystkie rezerwacje użytkownika wraz z informacjami o noclegu.
    Zwraca DataFrame: id_rezerwacji, nazwa noclegu, miasto, data zamelowania, 
    data wyjazdowania, liczba gości, cena całkowita, status
    """
    user_id = int(user_id)
    query = """
        SELECT 
            r.id_rezerwacji,
            n.id_noclegu,
            n.nazwa AS nazwa_noclegu,
            n.lokalizacja_miasto,
            n.lokalizacja_adres,
            n.cena_za_noc,
            r.data_zameldowania,
            r.data_wymeldowania,
            r.liczba_gosci,
            r.calkowita_cena,
            r.status,
            r.data_utworzenia
        FROM rezerwacje r
        JOIN noclegi n ON r.id_noclegu = n.id_noclegu
        WHERE r.id_turysty = :user_id
        ORDER BY r.data_wymeldowania DESC
    """
    df = conn.query(query, params={"user_id": user_id}, ttl=0)
    return df if not df.empty else pd.DataFrame()


def get_reservation_details(conn, reservation_id):
    """
    Pobiera szczegóły konkretnej rezerwacji.
    """
    query = """
        SELECT 
            r.id_rezerwacji,
            r.id_turysty,
            r.id_noclegu,
            n.nazwa AS nazwa_noclegu,
            n.lokalizacja_miasto,
            n.lokalizacja_adres,
            n.opis,
            n.typ_obiektu,
            r.data_zameldowania,
            r.data_wymeldowania,
            r.liczba_gosci,
            r.calkowita_cena,
            r.status,
            r.data_utworzenia
        FROM rezerwacje r
        JOIN noclegi n ON r.id_noclegu = n.id_noclegu
        WHERE r.id_rezerwacji = :reservation_id
    """
    df = conn.query(query, params={"reservation_id": reservation_id}, ttl=0)
    return df.iloc[0] if not df.empty else None


def get_user_opinions(conn, user_id):
    """
    Pobiera wszystkie opinie wystawione przez użytkownika.
    Zwraca DataFrame: id_opinii, nazwa noclegu, miasta, ocena, komentarz, 
    data_dodania, czy_edytowana, data_modyfikacji, id_rezerwacji
    """
    user_id = int(user_id)
    query = """
        SELECT 
            o.id_opinii,
            o.id_rezerwacji,
            o.ocena,
            o.komentarz,
            o.data_dodania,
            o.data_modyfikacji,
            o.czy_edytowana,
            n.id_noclegu,
            n.nazwa AS nazwa_noclegu,
            n.lokalizacja_miasto,
            r.data_zameldowania,
            r.data_wymeldowania
        FROM opinie o
        JOIN rezerwacje r ON o.id_rezerwacji = r.id_rezerwacji
        JOIN noclegi n ON o.id_noclegu = n.id_noclegu
        WHERE o.id_turysty = :user_id
        ORDER BY o.data_dodania DESC
    """
    df = conn.query(query, params={"user_id": user_id}, ttl=0)
    return df if not df.empty else pd.DataFrame()


def can_edit_opinion(conn, opinion_id):
    """
    Sprawdza czy opinię można jeszcze edytować.
    ⚠️ OGRANICZENIE: Opinię można edytować maksymalnie do 1 ROKU po jej wystawieniu
    
    Zwraca: (True/False, liczba_dni_do_wygaśnięcia)
    """
    opinion_id = int(opinion_id)
    query = """
        SELECT data_dodania
        FROM opinie
        WHERE id_opinii = :opinion_id
    """
    df = conn.query(query, params={"opinion_id": opinion_id}, ttl=0)
    
    if df.empty:
        return False, 0
    
    data_dodania = pd.to_datetime(df.iloc[0]["data_dodania"])
    data_dzisiaj = pd.Timestamp.now()
    
    # ⚠️ TUTAJ JEST OGRANICZENIE: można edytować przez 365 dni od wystawienia opinii
    data_graniczna = data_dodania + pd.Timedelta(days=365)
    
    if data_dzisiaj <= data_graniczna:
        dni_pozostale = (data_graniczna - data_dzisiaj).days
        return True, dni_pozostale
    else:
        return False, 0


def update_opinion(conn, opinion_id, new_rating, new_comment):
    """
    Aktualizuje opinię użytkownika (ocena i komentarz).
    Zapisuje historię poprzedniej wersji w tabeli historia_opinii.
    Aktualizuje flagi: czy_edytowana=1, data_modyfikacji=GETDATE()
    
    ⚠️ OGRANICZENIE: Najpierw sprawdza czy można edytować (do 1 roku)
    Zwraca: (True/False, komunikat)
    """
    opinion_id = int(opinion_id)
    # Najpierw sprawdzamy czy można edytować
    can_edit, dni_pozostale = can_edit_opinion(conn, opinion_id)
    if not can_edit:
        return False, "❌ Okres do edycji opinii upłynął (maksymalnie do 1 roku po wystawieniu)"
    
    try:
        with conn.session as session:
            # Pobierz stare dane opinii
            old_opinion = session.execute(
                text("""
                    SELECT ocena, komentarz 
                    FROM opinie 
                    WHERE id_opinii = :opinion_id
                """),
                {"opinion_id": opinion_id}
            ).fetchone()
            
            if not old_opinion:
                return False, "❌ Opinia nie znaleziona"
            
            stara_ocena, stary_komentarz = old_opinion
            
            # Zapisz historię
            session.execute(
                text("""
                    INSERT INTO historia_opinii (id_opinii, stara_ocena, stary_komentarz)
                    VALUES (:opinion_id, :stara_ocena, :stary_komentarz)
                """),
                {"opinion_id": opinion_id, "stara_ocena": stara_ocena, "stary_komentarz": stary_komentarz}
            )
            
            # Aktualizuj opinię
            session.execute(
                text("""
                    UPDATE opinie 
                    SET ocena = :ocena, 
                        komentarz = :komentarz,
                        data_modyfikacji = GETDATE(),
                        czy_edytowana = 1
                    WHERE id_opinii = :opinion_id
                """),
                {"ocena": new_rating, "komentarz": new_comment, "opinion_id": opinion_id}
            )
            
            session.commit()
            return True, f"✅ Opinia zaktualizowana. Możesz ją edytować jeszcze przez {dni_pozostale} dni"
    
    except Exception as e:
        return False, f"❌ Błąd bazy danych: {str(e)}"


def delete_opinion(conn, opinion_id):
    """
    Usuwa opinię użytkownika wraz z historią.
    Zwraca: (True/False, komunikat)
    """
    opinion_id = int(opinion_id)
    try:
        with conn.session as session:
            # Najpierw usuń historię
            session.execute(
                text("DELETE FROM historia_opinii WHERE id_opinii = :opinion_id"),
                {"opinion_id": opinion_id}
            )
            
            # Potem usuń samą opinię
            session.execute(
                text("DELETE FROM opinie WHERE id_opinii = :opinion_id"),
                {"opinion_id": opinion_id}
            )
            
            session.commit()
            return True, "✅ Opinia usunięta"
    
    except Exception as e:
        return False, f"❌ Błąd bazy danych: {str(e)}"


def update_user_profile(conn, user_id, telefon):
    """
    Aktualizuje profil użytkownika (telefon).
    Zwraca: (True/False, komunikat)
    """
    user_id = int(user_id)
    try:
        with conn.session as session:
            session.execute(
                text("""
                    UPDATE uzytkownicy 
                    SET telefon = :telefon
                    WHERE id_uzytkownika = :user_id
                """),
                {"telefon": telefon, "user_id": user_id}
            )
            session.commit()
            return True, "✅ Profil zaktualizowany"
    
    except Exception as e:
        return False, f"❌ Błąd bazy danych: {str(e)}"


def update_user_info(conn, user_id, imie, nazwisko, telefon):
    """
    Aktualizuje pełne dane profilu użytkownika (imię, nazwisko, telefon).
    Zwraca: (True/False, komunikat)
    """
    user_id = int(user_id)
    try:
        with conn.session as session:
            session.execute(
                text("""
                    UPDATE uzytkownicy 
                    SET imie = :imie, 
                        nazwisko = :nazwisko,
                        telefon = :telefon
                    WHERE id_uzytkownika = :user_id
                """),
                {"imie": imie, "nazwisko": nazwisko, "telefon": telefon, "user_id": user_id}
            )
            session.commit()
            return True, "✅ Dane zaktualizowane"
    
    except Exception as e:
        return False, f"❌ Błąd bazy danych: {str(e)}"
    
from sqlalchemy import text
import pandas as pd
import numpy as np # Upewnij się, że masz to zaimportowane



def get_user_opinions(user_id, conn):
    uid = int(user_id) 
    query = text("""
        SELECT 
            o.id_opinii, 
            o.id_rezerwacji,  -- <-- DODANE: niezbędne do mapowania w Streamlit
            o.ocena, 
            o.komentarz, 
            o.data_dodania, 
            o.id_noclegu, 
            n.nazwa AS nazwa_obiektu
        FROM opinie o
        JOIN noclegi n ON o.id_noclegu = n.id_noclegu
        WHERE o.id_turysty = :uid
        ORDER BY 
            CASE WHEN o.komentarz IS NOT NULL AND o.komentarz <> '' THEN 0 ELSE 1 END,
            o.data_dodania DESC
    """)
    
    with conn.session as s:
        result = s.execute(query, {"uid": uid})
        return pd.DataFrame(result.fetchall(), columns=result.keys())

from sqlalchemy import text

def get_user_reservations(user_id, conn):
    # Używamy konstrukcji z ROW_NUMBER(), aby dla każdego obiektu (id_noclegu)
    # wybrać tylko jeden (najnowszy) wiersz rezerwacji
    query = """
        WITH RankedReservations AS (
            SELECT 
                r.id_rezerwacji, 
                n.nazwa, 
                r.data_utworzenia, 
                r.data_zameldowania, 
                r.data_wymeldowania, 
                r.status, 
                r.id_noclegu,
                ROW_NUMBER() OVER (PARTITION BY r.id_noclegu ORDER BY r.data_utworzenia DESC) as rn
            FROM rezerwacje r
            JOIN noclegi n ON r.id_noclegu = n.id_noclegu
            WHERE r.id_turysty = :uid
        )
        SELECT TOP 5 
            id_rezerwacji, nazwa, data_utworzenia, data_zameldowania, 
            data_wymeldowania, status, id_noclegu,
            (SELECT COUNT(*) FROM opinie o WHERE o.id_rezerwacji = RankedReservations.id_rezerwacji) as ma_opinie
        FROM RankedReservations
        WHERE rn = 1
        ORDER BY data_wymeldowania DESC
    """
    return conn.query(query, params={"uid": int(user_id)})

def can_edit_opinion(opinion_id, user_id, conn):
    query = "SELECT id_opinii FROM opinie WHERE id_opinii = ? AND id_turysty = ?"
    result = conn.query(query, params=[opinion_id, user_id])
    return not result.empty

from sqlalchemy import text # Upewnij się, że masz ten import

def update_opinion(opinion_id, new_rating, new_comment, conn):
    # Rzutowanie na typy bazowe Pythona (int)
    oid = int(opinion_id)
    rating = int(new_rating)
    
    with conn.session as s:
        # Owijamy zapytanie w text() i używamy nazwanego parametru (:oid)
        s.execute(
            text("""
                UPDATE opinie 
                SET ocena = :r, komentarz = :c, data_modyfikacji = GETDATE(), czy_edytowana = 1 
                WHERE id_opinii = :oid
            """),
            {"r": rating, "c": new_comment, "oid": oid}
        )
        s.commit()

def delete_opinion(opinion_id, conn):
    with conn.session as s:
        s.execute("DELETE FROM opinie WHERE id_opinii = ?", (opinion_id,))
        s.commit()

def get_user_profile(user_id, conn):
    # Rzutowanie na int jest nadal ważne (aby uniknąć błędu numpy.int64)
    clean_user_id = int(user_id)
    
    # 1. Używamy nazwanego parametru (:id) zamiast ?
    query = "SELECT imie, nazwisko, telefon, email FROM uzytkownicy WHERE id_uzytkownika = :id"
    
    # 2. Przekazujemy parametry jako słownik (klucz: wartość)
    result = conn.query(query, params={"id": clean_user_id})
    
    if not result.empty:
        return result.iloc[0].to_dict()
    return None

def update_user_info(user_id, imie, nazwisko, telefon, conn):
    # Również tutaj rzutujemy ID na int
    clean_user_id = int(user_id)
    
    with conn.session as s:
        s.execute(
            text("UPDATE uzytkownicy SET imie = :imie, nazwisko = :nazwisko, telefon = :telefon WHERE id_uzytkownika = :id"),
            {"imie": imie, "nazwisko": nazwisko, "telefon": telefon, "id": clean_user_id}
        )
        s.commit()

import bcrypt # Upewnij się, że masz tę bibliotekę



def hash_password(password: str) -> str:
    """Konwertuje tekst hasła na bezpieczny hash."""
    # Salt jest generowany automatycznie przez gensalt
    salt = bcrypt.gensalt()
    # Hashujemy hasło (musi być w bajtach .encode('utf-8'))
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Zwracamy hash jako string, aby można go było zapisać w bazie
    return hashed.decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    """Weryfikuje, czy hasło pasuje do hasha."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def verify_and_update_user_credentials(user_id, old_pass, new_pass, new_email, conn):
    # 1. Pobierz dane użytkownika
    # PRZEKAŻ STRINGA zamiast obiektu text()
    query = "SELECT haslo_hash FROM uzytkownicy WHERE id_uzytkownika = :id"
    result = conn.query(query, params={"id": int(user_id)})
    
    if result.empty:
        return False, "Użytkownik nie istnieje."

    stored_hash = result.iloc[0]['haslo_hash']
    
    # Weryfikacja hasła
    if not check_password(old_pass, stored_hash):
        return False, "Podano błędne obecne hasło."

    # 2. Aktualizacja danych
    with conn.session as s:
        # Tutaj text() JEST wymagane, ponieważ korzystasz z s.execute (sesja SQLAlchemy)
        s.execute(
            text("UPDATE uzytkownicy SET haslo_hash = :new_pass, email = :new_email WHERE id_uzytkownika = :id"),
            {"new_pass": new_pass, "new_email": new_email, "id": int(user_id)}
        )
        s.commit()
    
    return True, "Dane zostały zaktualizowane pomyślnie!"

def add_new_property(user_id, nazwa, opis, typ, miasto, adres, cena, max_osoby, conn):
    """
    Dodaje nowy obiekt do tabeli 'noclegi' z wymuszoną konwersją typów numpy.
    """
    try:
        # Konwersja typów numpy na natywne typy Pythona
        clean_user_id = int(user_id) if isinstance(user_id, (np.integer, int)) else user_id
        clean_cena = float(cena) if isinstance(cena, (np.floating, float)) else cena
        clean_osoby = int(max_osoby) if isinstance(max_osoby, (np.integer, int)) else max_osoby

        query = text("""
            INSERT INTO noclegi 
            (id_wlasciciela, nazwa, opis, typ_obiektu, lokalizacja_miasto, lokalizacja_adres, cena_za_noc, maks_liczba_osob)
            VALUES (:uid, :nazwa, :opis, :typ, :miasto, :adres, :cena, :osoby)
        """)
        
        with conn.session as s:
            s.execute(query, {
                "uid": clean_user_id, 
                "nazwa": nazwa, 
                "opis": opis, 
                "typ": typ, 
                "miasto": miasto, 
                "adres": adres, 
                "cena": clean_cena, 
                "osoby": clean_osoby
            })
            s.commit()
            
        return True, "Obiekt został pomyślnie dodany!"
    except Exception as e:
        return False, f"Błąd podczas dodawania obiektu: {str(e)}"
    

def delete_opinion(id_opinii, conn):
    """
    Usuwa opinię z bazy danych na podstawie jej ID.
    """
    try:
        query = text("DELETE FROM opinie WHERE id_opinii = :id")
        with conn.session as s:
            s.execute(query, {"id": id_opinii})
            s.commit()
        return True, "Opinia została usunięta."
    except Exception as e:
        return False, f"Błąd podczas usuwania opinii: {str(e)}"
    
def get_user_properties(user_id, conn):
    """Pobiera listę 5 ostatnio dodanych obiektów należących do użytkownika."""
    clean_id = int(user_id)  # Wymuszenie czystego typu int
    
    # Używamy TOP 5 oraz sortowania po data_dodania DESC
    query = """
        SELECT TOP 5 * FROM noclegi 
        WHERE id_wlasciciela = :id 
        ORDER BY data_dodania DESC
    """
    return conn.query(query, params=[{"id": clean_id}])

def get_property_reviews(user_id, conn):
    """Pobiera wszystkie opinie gości dla obiektów danego właściciela, 
    sortując w pierwszej kolejności te, które posiadają komentarz tekstowy."""
    clean_id = int(user_id)  # Wymuszenie czystego typu int
    
    # Warunek CASE sprawdza czy komentarz nie jest NULLem i czy nie jest pustym stringem
    query = """
        SELECT 
            o.id_opinii AS id_opinii,
            o.id_noclegu AS id_noclegu,
            o.ocena AS ocena,
            o.komentarz AS komentarz,
            o.data_dodania AS data_dodania,
            n.nazwa AS nazwa_obiektu, 
            u.imie + ' ' + u.nazwisko AS autor,
            ow.tresc AS odpowiedz_wlasciciela
        FROM opinie o
        INNER JOIN noclegi n ON o.id_noclegu = n.id_noclegu
        INNER JOIN uzytkownicy u ON o.id_turysty = u.id_uzytkownika
        LEFT JOIN odpowiedzi_wlasciciela ow ON o.id_opinii = ow.id_opinii
        WHERE n.id_wlasciciela = :id
        ORDER BY 
            CASE 
                WHEN o.komentarz IS NOT NULL AND LEN(TRIM(o.komentarz)) > 0 THEN 0 
                ELSE 1 
            END ASC,
            o.data_dodania DESC
    """
    return conn.query(query, params=[{"id": clean_id}], ttl=0)


def delete_property(property_id, conn):
    try:
        clean_property_id = int(property_id)
        with conn.session as session:
            # Rezerwacje i opinie mogą blokować usunięcie, jeśli nie ma CASCADE w DB.
            # Dla bezpieczeństwa można najpierw usunąć powiązane elementy:
            session.execute(text("DELETE FROM zdjecia_noclegu WHERE id_noclegu = :id"), {"id": clean_property_id})
            session.execute(text("DELETE FROM kalendarz_dostepnosci WHERE id_noclegu = :id"), {"id": clean_property_id})
            
            # Właściwe usunięcie obiektu
            query = text("DELETE FROM noclegi WHERE id_noclegu = :id")
            result = session.execute(query, {"id": clean_property_id})
            
            session.commit() # <--- TO JEST KLUCZOWE DLA AZURE SQL
            return True, "Obiekt został usunięty."
    except Exception as e:
        return False, f"Błąd bazy danych: {str(e)}"
    
from sqlalchemy import text

def upsert_owner_reply(opinion_id, reply_text, conn):
    """Dodaje nową odpowiedź właściciela lub aktualizuje istniejącą."""
    try:
        clean_opinion_id = int(opinion_id)
        stripped_text = reply_text.strip()
        
        if not stripped_text:
            return False, "Treść odpowiedzi nie może być pusta."
            
        query = text("""
            MERGE odpowiedzi_wlasciciela AS target
            USING (SELECT :id_opinii AS id_opinii) AS source
            ON (target.id_opinii = source.id_opinii)
            WHEN MATCHED THEN
                UPDATE SET tresc = :tresc, data_dodania = GETDATE()
            WHEN NOT MATCHED THEN
                INSERT (id_opinii, tresc) VALUES (:id_opinii, :tresc);
        """)
        
        with conn.session as session:
            session.execute(query, {"id_opinii": clean_opinion_id, "tresc": stripped_text})
            session.commit()
            return True, "Odpowiedź została zapisana."
    except Exception as e:
        return False, f"Błąd bazy danych przy zapisywaniu odpowiedzi: {str(e)}"
    


def add_opinion(reservation_id, user_id, property_id, rating, comment, conn):
    """
    Dodaje nową opinię do tabeli 'opinie' na podstawie struktury bazy danych.
    """
    rid = int(reservation_id)
    uid = int(user_id)
    pid = int(property_id)
    rate = int(rating)
    
    try:
        with conn.session as s:
            s.execute(
                text("""
                    INSERT INTO opinie (
                        id_rezerwacji, 
                        id_turysty, 
                        id_noclegu, 
                        ocena, 
                        komentarz, 
                        data_dodania, 
                        czy_edytowana
                    )
                    VALUES (:rid, :uid, :pid, :r, :c, GETDATE(), 0)
                """),
                {
                    "rid": rid,
                    "uid": uid,
                    "pid": pid,
                    "r": rate,
                    "c": comment
                }
            )
            s.commit()
        return True, "Opinia została pomyślnie dodana!"
    except Exception as e:
        return False, str(e)