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
    # USUNIĘTO text(...) – przekazujemy czysty string
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
    
import pandas as pd
def get_user_reservations(user_id, conn):
    query = """
    SELECT id_rezerwacji, nazwa, data_zameldowania, data_wymeldowania, status, calkowita_cena
    FROM rezerwacje
    WHERE id_turysty = ?
    """
    # W conn.query przekazujemy tylko zapytanie i parametry (bez przekazywania samego obiektu conn)
    return conn.query(query, params=[user_id])

def get_user_opinions(user_id, conn):
    query = "SELECT * FROM opinie WHERE id_turysty = ?"
    return conn.query(query, params=[user_id])

def can_edit_opinion(opinion_id, user_id, conn):
    query = "SELECT id_opinii FROM opinie WHERE id_opinii = ? AND id_turysty = ?"
    result = conn.query(query, params=[opinion_id, user_id])
    return not result.empty

def update_opinion(opinion_id, new_rating, new_comment, conn):
    with conn.session as s:
        s.execute(
            "UPDATE opinie SET ocena = ?, komentarz = ?, data_modyfikacji = GETDATE(), czy_edytowana = 1 WHERE id_opinii = ?",
            (new_rating, new_comment, opinion_id)
        )
        s.commit()

def delete_opinion(opinion_id, conn):
    with conn.session as s:
        s.execute("DELETE FROM opinie WHERE id_opinii = ?", (opinion_id,))
        s.commit()

def get_user_profile(user_id, conn):
    query = "SELECT imie, nazwisko, telefon, email FROM uzytkownicy WHERE id_uzytkownika = ?"
    result = conn.query(query, params=[user_id])
    if not result.empty:
        # Konwersja wiersza DataFrame na słownik
        return result.iloc[0].to_dict()
    return None

def update_user_info(user_id, imie, nazwisko, telefon, conn):
    with conn.session as s:
        s.execute(
            "UPDATE uzytkownicy SET imie = ?, nazwisko = ?, telefon = ? WHERE id_uzytkownika = ?",
            (imie, nazwisko, telefon, user_id)
        )
        s.commit()

def verify_and_update_password(user_id, old_pass, new_pass, conn):
    # Pobieramy hasło bezpośrednio przez query
    query = "SELECT haslo_hash FROM uzytkownicy WHERE id_uzytkownika = ?"
    result = conn.query(query, params=[user_id])
    
    if not result.empty:
        stored_hash = result.iloc[0]['haslo_hash']
        if stored_hash == old_pass:  # Pamiętaj o użyciu bcrypt w przyszłości!
            with conn.session as s:
                s.execute("UPDATE uzytkownicy SET haslo_hash = ? WHERE id_uzytkownika = ?", (new_pass, user_id))
                s.commit()
            return True
    return False