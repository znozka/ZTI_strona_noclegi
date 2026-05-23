import requests
import pandas as pd
import bcrypt
from sqlalchemy import text

def get_user_by_email(conn, email):
    """
    Pobiera dane użytkownika z bazy Azure SQL na podstawie adresu e-mail.
    Zwraca obiekt wiersza (np. z polami id_uzytkownika, imie, haslo_hash, rola)
    lub None, jeśli użytkownik nie istnieje.
    """
    query = text("""
        SELECT id_uzytkownika, email, haslo_hash, imie, nazwisko, rola 
        FROM uzytkownicy 
        WHERE email = :email
    """)

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