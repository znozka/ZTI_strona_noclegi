# import pandas as pd
# import numpy as np
# import random
# import time
# from datetime import date, timedelta
# from sqlalchemy import create_engine, text

# # 1. Konfiguracja połączenia do Azure SQL
# url = "mssql+pyodbc://Zuza:haslo.Admin@database-zti.database.windows.net:1433/NoclegiDB?driver=ODBC+Driver+18+for+SQL+Server"
# engine = create_engine(
#     url,
#     pool_pre_ping=True,
#     pool_recycle=1800
# )

# # --- DEFINICJA BEZPIECZNEJ FUNKCJI ZAPISUJĄCEJ BATCHE ---
# def zapisz_tabele_identity_fast(df, nazwa_tabeli):
#     if df.empty:
#         return

#     cols = list(df.columns)
#     col_string = ", ".join(cols)
#     placeholders = ", ".join(["?"] * len(cols))

#     sql = f"""
#     INSERT INTO {nazwa_tabeli} ({col_string})
#     VALUES ({placeholders})
#     """

#     dane = [tuple(x) for x in df.to_numpy()]
#     batch_size = 1000  
#     max_retries = 3     

#     print(f"\nRozpoczynam wgrywanie danych do {nazwa_tabeli} (łącznie: {len(dane)} rekordów)...")

#     for i in range(0, len(dane), batch_size):
#         batch = dane[i:i + batch_size]
#         print(f"{nazwa_tabeli}: zapis batcha {i} / {len(dane)}")

#         for attempt in range(1, max_retries + 1):
#             conn = None
#             try:
#                 conn = engine.raw_connection()
#                 cursor = conn.cursor()

#                 # Włączamy IDENTITY_INSERT w obrębie tej sesji
#                 cursor.execute(f"SET IDENTITY_INSERT {nazwa_tabeli} ON")
#                 cursor.executemany(sql, batch)
#                 cursor.execute(f"SET IDENTITY_INSERT {nazwa_tabeli} OFF")
                
#                 conn.commit()
#                 conn.close()
#                 break 

#             except Exception as e:
#                 print(f" OSTRZEŻENIE: Błąd batcha {i} (Próba {attempt}/{max_retries}): {e}")
#                 if conn:
#                     try:
#                         conn.rollback()
#                         conn.close()
#                     except Exception:
#                         pass 
                
#                 if attempt < max_retries:
#                     time.sleep(5)  
#                 else:
#                     print(f" KRYTYCZNY BŁĄD: Batch {i} nie mógł zostać zapisany.")
#                     raise e  

#     print(f" Sukces! Wgrano wszystkie dane do tabeli {nazwa_tabeli}")


# print("Pobieranie danych o noclegach z bazy...")
# df_noclegi = pd.read_sql_query("SELECT id_noclegu, cena_za_noc, srednia_ocena FROM noclegi", engine)

# ## --- 2. DYNAMICZNE GENEROWANIE REZERWACJI I OPINII ---
# print("Generowanie nowych rezerwacji i opinii...")

# baza_komentarzy = {
#     5: [
#         "Fantastyczne miejsce! Czysto, nowocześnie i w świetnej lokalizacji. Bardzo polecam!",
#         "Wszystko na najwyższym poziomie. Przesympatyczna obsługa i wyjątkowy komfort.",
#         "Cudowny pobyt, pokoje lśnią czystością, na pewno wrócimy tu ponownie!",
#         "Rewelacja! Standard przewyższył nasze oczekiwania. Blisko do największych atrakcji.",
#         "Doskonałe wyposażenie, wygodne łóżka i bardzo pomocny właściciel.",
#         "Niesamowity widok z okna i pyszne, urozmaicone śniadania. Magiczne miejsce!",
#         "Spokojna okolica, wysoki standard wykończenia i dbałość o każdy detal. 10/10!",
#         "Idealne miejsce na odpoczynek. Cisza, spokój, a obsługa reaguje na każdą prośbę.",
#         "Stosunek jakości do ceny rewelacyjny. Standard hotelowy w cenie apartamentu.",
#         "Z czystym sumieniem polecam każdemu. Najlepszy nocleg, w jakim dotychczas byłam."
#     ],
#     4: [
#         "Bardzo ładny obiekt, dobre warunki i miła obsługa. Mały minus za słabe Wi-Fi.",
#         "Komfortowy pobyt, dobra lokalizacja. Wszystko zgodne z opisem w ofercie.",
#         "Czysto i przyjemnie. Standard adekwatny do ceny, jesteśmy zadowoleni.",
#         "Dobra baza wypadowa na zwiedzanie miasta. Pokój schludny, obsługa bez zarzutu.",
#         "Spędziliśmy tu miły weekend. Śniadania smaczne, parking na duży plus.",
#         "Mieszkanie dobrze wyposażone, ładny design, choć łazienka mogłaby być ciut większa.",
#         "Wszystko w porządku, bezproblemowe zameldowanie i dobra komunikacja z gospodarzem.",
#         "Lokalizacja super, wszędzie blisko. Pokój ładny, ale materac trochę za miękki.",
#         "Bardzo przyjemne miejsce, urządzane ze smakiem. Drobne niedociągnięcia z czystością.",
#         "Udany pobyt. Dobra kawa w cenie, obsługa bardzo się stara, drobne minusy za akustykę."
#     ],
#     3: [
#         "Przeciętny standard. Lokalizacja w porządku, ale pokoje wymagają lekkiego odświeżenia.",
#         "Mogłoby być lepiej. Obsługa poprawna, jednak czystość pozostawia trochę do życzenia.",
#         "Nocleg w porządku jako baza wypadowa, ale brakuje podstawowych udogodnień.",
#         "Pokój dość mały, akustyka budynku słaba – słychać sąsiadów. Przeciętnie.",
#         "Cena atrakcyjna, ale komfort pozostawia sporo do życzenia. Na jedną noc ujdzie.",
#         "Lokalizacja świetna, ale sam obiekt najlepsze lata ma już za sobą. Średni komfort.",
#         "Obsługa była miła, ale stan techniczny pokoju (skrzypiące drzwi, urwana roleta) na minus.",
#         "Zdjęcia wyglądały na nieco nowocześniejsze. Zwykły, poprawny nocleg bez rewelacji.",
#         "Niby wszystko jest, ale czuut oszczędność na ogrzewaniu i wyposażeniu kuchni.",
#         "Brakowało mi ręczników i mydła w łazience. Sam pokój ujdzie, jeśli tylko tam śpisz."
#     ],
#     2: [
#         "Niestety nie polecam. Słaby kontakt z obsługą, a warunki na miejscu rozczarowujące.",
#         "Obiekt zaniedbany. Hałas z ulicy uniemożliwiał odpoczynek. Standard bardzo niski.",
#         "W pokoju było zimno, a łazienka domaga się natychmiastowego remontu.",
#         "Pokoje zupełnie niezgodne z opisem. Zapach wilgoci był nie do zniesienia.",
#         "Bardzo nieprofesjonalne podejście do klienta. Odradzam, szkoda nerwów i pieniędzy.",
#         "Cena nieadekwatna do tragicznych warunków. Brak prywatności i stare wyposażenie.",
#         "Dookoła brudno, kurz na meblach i plamy na wykładzinie. Nie odważyliśmy się tam zostać.",
#         "Część urządzeń w pokoju nie działała (TV, czajnik). Rezydent zignorował nasze zgłoszenie.",
#         "Lokalizacja to jedyny plus, reszta to nieporozumienie. Bardzo niski poziom usług.",
#         "Właściciel niesympatyczny i problematyczny. Warunki sanitarne mocno wątpliwe."
#     ],
#     1: [
#         "Tragedia. Zdjęcia nie odzwierciedlają rzeczywistości. Brudno i nieprzyjemnie.",
#         "Najgorsze doświadczenie noclegowe. Omijać to miejsce z daleka!",
#         "Brak ciepłej wody, brudna pościel i zerowy kontakt z obsługą. Koszmar.",
#         "Zostaliśmy oszukani. Obiekt wygląda jak ruina, warunki urągające jakimkolwiek standardom.",
#         "Karaluchy w pokoju i grzyb pod prysznicem. Natychmiast zażądaliśmy zwrotu pieniędzy.",
#         "Nie zostaliśmy wpuszczeni do obiektu mimo opłaconej rezerwacji. Telefon milczał.",
#         "Skandaliczne warunki. Pościel była nieświeża, a w pokoju śmierdziało dymem papierosowym.",
#         "Strata czasu i pieniędzy. Standard gorszy niż w najtańszym schronisku, syf i malaria.",
#         "Niebezpieczna okolica, brak zamków w drzwiach wewnętrznych. Uciekliśmy stamtąd po godzinie.",
#         "Totalne dno. Nigdy w życiu nie spotkałem się z takim syfem i chamstwem ze strony obsługi."
#     ]
# }

# nowe_rezerwacje = []
# nowe_opinie = []
# slownik_liczby_opinii = {}

# id_sztucznego_turysty = 1 
# id_rezerwacji_counter = 1
# id_opinii_counter = 1

# for idx, nocleg in df_noclegi.iterrows():
#     id_noclegu = int(nocleg['id_noclegu'])
    
#     try:
#         srednia_ocena = float(nocleg['srednia_ocena']) if pd.notna(nocleg['srednia_ocena']) else 4.0
#     except (ValueError, TypeError):
#         srednia_ocena = 4.0
        
#     wylosowana_liczba_opinii = random.randint(5, 209)
#     slownik_liczby_opinii[id_noclegu] = wylosowana_liczba_opinii
    
#     if srednia_ocena >= 4.5:
#         baza_ocen = [5, 5, 5, 4, 5]
#     elif srednia_ocena >= 3.5:
#         baza_ocen = [4, 4, 5, 4, 3]
#     elif srednia_ocena >= 2.5:
#         baza_ocen = [3, 3, 4, 3, 2]
#     else:
#         baza_ocen = [2, 1, 2, 3, 1]
        
#     dostepne_teksty = {ocena: list(komentarze) for ocena, komentarze in baza_komentarzy.items()}
#     licznik_tekstowych_komentarzy = 0
    
#     for _ in range(wylosowana_liczba_opinii):
#         ocena_opinii = random.choice(baza_ocen)
#         komentarz = None
        
#         if licznik_tekstowych_komentarzy < 50 and dostepne_teksty[ocena_opinii]:
#             wylosowany_indeks = random.randint(0, len(dostepne_teksty[ocena_opinii]) - 1)
#             komentarz = dostepne_teksty[ocena_opinii].pop(wylosowany_indeks)
#             licznik_tekstowych_komentarzy += 1
            
#         cena = float(nocleg['cena_za_noc']) if pd.notna(nocleg['cena_za_noc']) else 150.0
        
#         dni_wstecz = random.randint(15, 60)
#         data_pszt = date.today() - timedelta(days=dni_wstecz)
#         dlugosc_pobytu = random.randint(1, 7)
#         data_out = data_pszt + timedelta(days=dlugosc_pobytu)
        
#         nowe_rezerwacje.append({
#             "id_rezerwacji": id_rezerwacji_counter,
#             "id_turysty": id_sztucznego_turysty,
#             "id_noclegu": id_noclegu,
#             "data_zameldowania": data_pszt,
#             "data_wymeldowania": data_out,
#             "liczba_gosci": random.randint(2, 4),
#             "calkowita_cena": cena * dlugosc_pobytu,
#             "status": "zakonczona",
#             "data_utworzenia": pd.Timestamp(data_pszt) - pd.Timedelta(days=14)
#         })
        
#         nowe_opinie.append({
#             "id_opinii": id_opinii_counter,
#             "id_rezerwacji": id_rezerwacji_counter,
#             "id_turysty": id_sztucznego_turysty,
#             "id_noclegu": id_noclegu,
#             "ocena": ocena_opinii,
#             "komentarz": komentarz,  
#             "data_dodania": pd.Timestamp(data_out) + pd.Timedelta(days=random.randint(1, 3)),
#             "data_modyfikacji": None,
#             "czy_edytowana": 0
#         })
        
#         id_rezerwacji_counter += 1
#         id_opinii_counter += 1

# df_rezerwacje = pd.DataFrame(nowe_rezerwacje)
# df_opinie_nowe = pd.DataFrame(nowe_opinie)

# # Generowanie powiązanych płatności
# nowe_platnosci = []
# for idx, rez in df_rezerwacje.iterrows():
#     nowe_platnosci.append({
#         "id_platnosci": rez['id_rezerwacji'],
#         "id_rezerwacji": rez['id_rezerwacji'],
#         "id_transakcji_zewnetrznej": f"PAY-{random.randint(100000, 999999)}",
#         "metoda_platnosci": "karta",
#         "kwota": rez['calkowita_cena'],
#         "status": "sukces",
#         "data_platnosci": rez['data_utworzenia'] + pd.Timedelta(minutes=5)
#     })
# df_platnosci = pd.DataFrame(nowe_platnosci)


# # --- 3. CZYSZCZENIE I ZAPIS TABEL ---
# print("Modyfikacja bazy danych Azure SQL...")
# tabele_do_czyszczenia = ["historia_opinii", "opinie", "platnosci", "rezerwacje"]

# with engine.begin() as sql_conn:
#     for t in tabele_do_czyszczenia:
#         sql_conn.execute(text(f"DELETE FROM {t}"))
#         print(f"Wyczyszczono tabelę: {t}")


# # --- PRZYGOTOWANIE TYPÓW DANYCH POD STRUKTURĘ SQL SERVER ---
# print("\nFormatowanie typów danych DataFrame...")

# # 1. Tabela: rezerwacje
# df_rezerwacje['id_rezerwacji'] = df_rezerwacje['id_rezerwacji'].astype(int)
# df_rezerwacje['id_turysty'] = df_rezerwacje['id_turysty'].astype(int)
# df_rezerwacje['id_noclegu'] = df_rezerwacje['id_noclegu'].astype(int)
# df_rezerwacje['liczba_gosci'] = df_rezerwacje['liczba_gosci'].astype(int)
# df_rezerwacje['data_zameldowania'] = df_rezerwacje['data_zameldowania'].astype(str)
# df_rezerwacje['data_wymeldowania'] = df_rezerwacje['data_wymeldowania'].astype(str)

# # 2. Tabela: platnosci
# df_platnosci['id_platnosci'] = df_platnosci['id_platnosci'].astype(int)
# df_platnosci['id_rezerwacji'] = df_platnosci['id_rezerwacji'].astype(int)  # Poprawiona literówka

# # 3. Tabela: opinie
# df_opinie_nowe['id_opinii'] = df_opinie_nowe['id_opinii'].astype(int)
# df_opinie_nowe['id_rezerwacji'] = df_opinie_nowe['id_rezerwacji'].astype(int)
# df_opinie_nowe['id_turysty'] = df_opinie_nowe['id_turysty'].astype(int)
# df_opinie_nowe['id_noclegu'] = df_opinie_nowe['id_noclegu'].astype(int)
# df_opinie_nowe['ocena'] = df_opinie_nowe['ocena'].astype(int)
# df_opinie_nowe['czy_edytowana'] = df_opinie_nowe['czy_edytowana'].astype(int)

# # Konwersja na natywne obiekty Pythona (zamiana NaN/NaT na czyste None dla SQL Server)
# df_rezerwacje = df_rezerwacje.astype(object).where(df_rezerwacje.notnull(), None)
# df_platnosci = df_platnosci.astype(object).where(df_platnosci.notnull(), None)
# df_opinie_nowe = df_opinie_nowe.astype(object).where(df_opinie_nowe.notnull(), None)


# # --- URUCHOMIENIE FUNKCJI ZAPISUJĄCEJ BATCHE ---
# zapisz_tabele_identity_fast(df_rezerwacje, "rezerwacje")
# zapisz_tabele_identity_fast(df_platnosci, "platnosci")
# zapisz_tabele_identity_fast(df_opinie_nowe, "opinie")


# # --- 4. AKTUALIZACJA POLA 'liczba_opinii' ORAZ 'srednia_ocena' W NOCLEGACH ---
# print("\nAktualizacja statystyk (liczba i średnia ocen) w tabeli 'noclegi'...")

# df_statystyki = df_opinie_nowe.groupby('id_noclegu').agg(
#     nowa_liczba=('ocena', 'count'),
#     nowa_srednia=('ocena', 'mean')
# ).reset_index()

# with engine.begin() as sql_conn:
#     for idx, row in df_statystyki.iterrows():
#         sql_conn.execute(
#             text("""
#                 UPDATE noclegi 
#                 SET liczba_opinii = :liczba, 
#                     srednia_ocena = :srednia 
#                 WHERE id_noclegu = :id
#             """),
#             {
#                 "liczba": int(row['nowa_liczba']), 
#                 "srednia": round(float(row['nowa_srednia']), 2), 
#                 "id": int(row['id_noclegu'])
#             }
#         )

# print("\n[SUKCES] Dane zostały poprawnie i szybko zaktualizowane!")

import pandas as pd
import numpy as np
import random
import time
from datetime import date, timedelta
from sqlalchemy import create_engine, text

# 1. Konfiguracja połączenia do Azure SQL
url = "mssql+pyodbc://Zuza:haslo.Admin@database-zti.database.windows.net:1433/NoclegiDB?driver=ODBC+Driver+18+for+SQL+Server"
engine = create_engine(
    url,
    pool_pre_ping=True,
    pool_recycle=1800
)

# --- DEFINICJA BEZPIECZNEJ FUNKCJI ZAPISUJĄCEJ BATCHE ---
def zapisz_tabele_identity_fast(df, nazwa_tabeli):
    if df.empty:
        return

    cols = list(df.columns)
    col_string = ", ".join(cols)
    placeholders = ", ".join(["?"] * len(cols))

    sql = f"""
    INSERT INTO {nazwa_tabeli} ({col_string})
    VALUES ({placeholders})
    """

    dane = [tuple(x) for x in df.to_numpy()]
    batch_size = 1000  
    max_retries = 3     

    print(f"\nRozpoczynam wgrywanie danych do {nazwa_tabeli} (łącznie: {len(dane)} rekordów)...")

    for i in range(0, len(dane), batch_size):
        batch = dane[i:i + batch_size]
        print(f"{nazwa_tabeli}: zapis batcha {i} / {len(dane)}")

        for attempt in range(1, max_retries + 1):
            conn = None
            try:
                conn = engine.raw_connection()
                cursor = conn.cursor()

                cursor.execute(f"SET IDENTITY_INSERT {nazwa_tabeli} ON")
                cursor.executemany(sql, batch)
                cursor.execute(f"SET IDENTITY_INSERT {nazwa_tabeli} OFF")
                
                conn.commit()
                conn.close()
                break 

            except Exception as e:
                print(f" OSTRZEŻENIE: Błąd batcha {i} (Próba {attempt}/{max_retries}): {e}")
                if conn:
                    try:
                        conn.rollback()
                        conn.close()
                    except Exception:
                        pass 
                
                if attempt < max_retries:
                    time.sleep(5)  
                else:
                    print(f" KRYTYCZNY BŁĄD: Batch {i} nie mógł zostać zapisany.")
                    raise e  

    print(f" Sukces! Wgrano wszystkie dane do tabeli {nazwa_tabeli}")


print("Pobieranie danych o noclegach z bazy...")
df_noclegi = pd.read_sql_query("SELECT id_noclegu, cena_za_noc, srednia_ocena FROM noclegi", engine)

## --- 2. DYNAMICZNE GENEROWANIE REZERWACJI I OPINII ---
print("Generowanie nowych rezerwacji i opinii...")

baza_komentarzy = {
    5: [
        "Fantastyczne miejsce! Czysto, nowocześnie i w świetnej lokalizacji. Bardzo polecam!",
        "Wszystko na najwyższym poziomie. Przesympatyczna obsługa i wyjątkowy komfort.",
        "Cudowny pobyt, pokoje lśnią czystością, na pewno wrócimy tu ponownie!",
        "Rewelacja! Standard przewyższył nasze oczekiwania. Blisko do największych atrakcji.",
        "Doskonałe wyposażenie, wygodne łóżka i bardzo pomocny właściciel.",
        "Niesamowity widok z okna i pyszne, urozmaicone śniadania. Magiczne miejsce!",
        "Spokojna okolica, wysoki standard wykończenia i dbałość o każdy detal. 10/10!",
        "Idealne miejsce na odpoczynek. Cisza, spokój, a obsługa reaguje na każdą prośbę.",
        "Stosunek jakości do ceny rewelacyjny. Standard hotelowy w cenie apartamentu.",
        "Z czystym sumieniem polecam jedemau. Najlepszy nocleg, w jakim dotychczas byłam."
    ],
    4: [
        "Bardzo ładny obiekt, dobre warunki i miła obsługa. Mały minus za słabe Wi-Fi.",
        "Komfortowy pobyt, dobra lokalizacja. Wszystko zgodne z opisem w ofercie.",
        "Czysto i przyjemnie. Standard adekwatny do ceny, jesteśmy zadowoleni.",
        "Dobra baza wypadowa na zwiedzanie miasta. Pokój schludny, obsługa bez zarzutu.",
        "Spędziliśmy tu miły weekend. Śniadania smaczne, parking na duży plus.",
        "Mieszkanie dobrze wyposażone, ładny design, choć łazienka mogłaby być ciut większa.",
        "Wszystko w porządku, bezproblemowe zameldowanie i dobra komunikacja z gospodarzem.",
        "Lokalizacja super, wszędzie blisko. Pokój ładny, ale materac trochę za miękki.",
        "Bardzo przyjemne miejsce, urządzane ze smakiem. Drobne niedociągnięcia z czystością.",
        "Udany pobyt. Dobra kawa w cenie, obsługa bardzo się stara, drobne minusy za akustykę."
    ],
    3: [
        "Przeciętny standard. Lokalizacja w porządku, ale pokoje wymagają lekkiego odświeżenia.",
        "Mogłoby być lepiej. Obsługa poprawna, jednak czystość pozostawia trochę do życzenia.",
        "Nocleg w porządku jako baza wypadowa, ale brakuje podstawowych udogodnień.",
        "Pokój dość mały, akustyka budynku słaba – słychać sąsiadów. Przeciętnie.",
        "Cena atrakcyjna, ale komfort pozostawia sporo do życzenia. Na jedną noc ujdzie.",
        "Lokalizacja świetna, ale sam obiekt najlepsze lata ma już za sobą. Średni komfort.",
        "Obsługa była miła, ale stan techniczny pokoju (skrzypiące drzwi, urwana roleta) na minus.",
        "Zdjęcia wyglądały na nieco nowocześniejsze. Zwykły, poprawny nocleg bez rewelacji.",
        "Niby wszystko jest, ale czuut oszczędność na ogrzewaniu i wyposażeniu kuchni.",
        "Brakowało mi ręczników i mydła w łazience. Sam pokój ujdzie, jeśli tylko tam śpisz."
    ],
    2: [
        "Niestety nie polecam. Słaby kontakt z obsługą, a warunki na miejscu rozczarowujące.",
        "Obiekt zaniedbany. Hałas z ulicy uniemożliwiał odpoczynek. Standard bardzo niski.",
        "W pokoju było zimno, a łazienka domaga się natychmiastowego remontu.",
        "Pokoje zupełnie niezgodne z opisem. Zapach wilgoci był nie do zniesienia.",
        "Bardzo nieprofesjonalne podejście do klienta. Odradzam, szkoda nerwów i pieniędzy.",
        "Cena nieadekwatna do tragicznych warunków. Brak prywatności i stare wyposażenie.",
        "Dookoła brudno, kurz na meblach i plamy na wykładzinie. Nie odważyliśmy się tam zostać.",
        "Część urządzeń w pokoju nie działała (TV, czajnik). Rezydent zignorował nasze zgłoszenie.",
        "Lokalizacja to jedyny plus, reszta to nieporozumienie. Bardzo niski poziom usług.",
        "Właściciel niesympatyczny i problematyczny. Warunki sanitarne mocno wątpliwe."
    ],
    1: [
        "Tragedia. Zdjęcia nie odzwierciedlają rzeczywistości. Brudno i nieprzyjemnie.",
        "Najgorsze doświadczenie noclegowe. Omijać to miejsce z daleka!",
        "Brak ciepłej wody, brudna pościel i zerowy kontakt z obsługą. Koszmar.",
        "Zostaliśmy oszukani. Obiekt wygląda jak ruina, warunki urągające jakimkolwiek standardom.",
        "Karaluchy w pokoju i grzyb pod prysznicem. Natychmiast zażądaliśmy zwrotu pieniędzy.",
        "Nie zostaliśmy wpuszczeni do obiektu mimo opłaconej rezerwacji. Telefon milczał.",
        "Skandaliczne warunki. Pościel była nieświeża, a w pokoju śmierdziało dymem papierosowym.",
        "Strata czasu i pieniędzy. Standard gorszy niż w najtańszym schronisku, syf i malaria.",
        "Niebezpieczna okolica, brak zamków w drzwiach wewnętrznych. Uciekliśmy stamtąd po godzinie.",
        "Totalne dno. Nigdy w życiu nie spotkałem się z takim syfem i chamstwem ze strony obsługi."
    ]
}

nowe_rezerwacje = []
nowe_opinie = []
slownik_liczby_opinii = {}

id_sztucznego_turysty = 1 
id_rezerwacji_counter = 1
id_opinii_counter = 1

for idx, nocleg in df_noclegi.iterrows():
    id_noclegu = int(nocleg['id_noclegu'])
    
    wylosowana_liczba_opinii = random.randint(5, 209)
    slownik_liczby_opinii[id_noclegu] = wylosowana_liczba_opinii
    
    # --- NOWA LOGIKA KONTROLI ROZKŁADU OCEN ---
    # Losujemy profil dla konkretnego obiektu na podstawie podanych wag globalnych.
    # Zapewni to proporcje: 10% (ocena 1), 40% (oceny 2-3), 50% (oceny 4-5).
    typ_obiektu = random.choices(
        population=['bardzo_slaby', 'sredni', 'dobry_bardzo_dobry'],
        weights=[0.10, 0.40, 0.50],
        k=1
    )[0]
    
    if typ_obiektu == 'dobry_bardzo_dobry':
        baza_ocen = [4, 4, 5, 5, 4]  # Średnia powyżej 4
    elif typ_obiektu == 'sredni':
        baza_ocen = [2, 3, 3, 4, 2]  # Średnia między 2 a 4
    else:
        baza_ocen = [1, 1, 2, 1, 2]  # Średnia poniżej 2
        
    dostepne_teksty = {ocena: list(komentarze) for ocena, komentarze in baza_komentarzy.items()}
    licznik_tekstowych_komentarzy = 0
    
    for _ in range(wylosowana_liczba_opinii):
        ocena_opinii = random.choice(baza_ocen)
        komentarz = None
        
        if licznik_tekstowych_komentarzy < 50 and dostepne_teksty[ocena_opinii]:
            wylosowany_indeks = random.randint(0, len(dostepne_teksty[ocena_opinii]) - 1)
            komentarz = dostepne_teksty[ocena_opinii].pop(wylosowany_indeks)
            licznik_tekstowych_komentarzy += 1
            
        cena = float(nocleg['cena_za_noc']) if pd.notna(nocleg['cena_za_noc']) else 150.0
        
        dni_wstecz = random.randint(15, 60)
        data_pszt = date.today() - timedelta(days=dni_wstecz)
        dlugosc_pobytu = random.randint(1, 7)
        data_out = data_pszt + timedelta(days=dlugosc_pobytu)
        
        nowe_rezerwacje.append({
            "id_rezerwacji": id_rezerwacji_counter,
            "id_turysty": id_sztucznego_turysty,
            "id_noclegu": id_noclegu,
            "data_zameldowania": data_pszt,
            "data_wymeldowania": data_out,
            "liczba_gosci": random.randint(2, 4),
            "calkowita_cena": cena * dlugosc_pobytu,
            "status": "zakonczona",
            "data_utworzenia": pd.Timestamp(data_pszt) - pd.Timedelta(days=14)
        })
        
        nowe_opinie.append({
            "id_opinii": id_opinii_counter,
            "id_rezerwacji": id_rezerwacji_counter,
            "id_turysty": id_sztucznego_turysty,
            "id_noclegu": id_noclegu,
            "ocena": ocena_opinii,
            "komentarz": komentarz,  
            "data_dodania": pd.Timestamp(data_out) + pd.Timedelta(days=random.randint(1, 3)),
            "data_modyfikacji": None,
            "czy_edytowana": 0
        })
        
        id_rezerwacji_counter += 1
        id_opinii_counter += 1

df_rezerwacje = pd.DataFrame(nowe_rezerwacje)
df_opinie_nowe = pd.DataFrame(nowe_opinie)

# Generowanie powiązanych płatności
nowe_platnosci = []
for idx, rez in df_rezerwacje.iterrows():
    nowe_platnosci.append({
        "id_platnosci": rez['id_rezerwacji'],
        "id_rezerwacji": rez['id_rezerwacji'],
        "id_transakcji_zewnetrznej": f"PAY-{random.randint(100000, 999999)}",
        "metoda_platnosci": "karta",
        "kwota": rez['calkowita_cena'],
        "status": "sukces",
        "data_platnosci": rez['data_utworzenia'] + pd.Timedelta(minutes=5)
    })
df_platnosci = pd.DataFrame(nowe_platnosci)


# --- 3. CZYSZCZENIE I ZAPIS TABEL ---
print("Modyfikacja bazy danych Azure SQL...")
tabele_do_czyszczenia = ["historia_opinii", "opinie", "platnosci", "rezerwacje"]

with engine.begin() as sql_conn:
    for t in tabele_do_czyszczenia:
        sql_conn.execute(text(f"DELETE FROM {t}"))
        print(f"Wyczyszczono tabelę: {t}")


# --- PRZYGOTOWANIE TYPÓW DANYCH POD STRUKTURĘ SQL SERVER ---
print("\nFormatowanie typów danych DataFrame...")

# 1. Tabela: rezerwacje
df_rezerwacje['id_rezerwacji'] = df_rezerwacje['id_rezerwacji'].astype(int)
df_rezerwacje['id_turysty'] = df_rezerwacje['id_turysty'].astype(int)
df_rezerwacje['id_noclegu'] = df_rezerwacje['id_noclegu'].astype(int)
df_rezerwacje['liczba_gosci'] = df_rezerwacje['liczba_gosci'].astype(int)
df_rezerwacje['data_zameldowania'] = df_rezerwacje['data_zameldowania'].astype(str)
df_rezerwacje['data_wymeldowania'] = df_rezerwacje['data_wymeldowania'].astype(str)

# 2. Tabela: platnosci
df_platnosci['id_platnosci'] = df_platnosci['id_platnosci'].astype(int)
df_platnosci['id_rezerwacji'] = df_platnosci['id_rezerwacji'].astype(int)  

# 3. Tabela: opinie
df_opinie_nowe['id_opinii'] = df_opinie_nowe['id_opinii'].astype(int)
df_opinie_nowe['id_rezerwacji'] = df_opinie_nowe['id_rezerwacji'].astype(int)
df_opinie_nowe['id_turysty'] = df_opinie_nowe['id_turysty'].astype(int)
df_opinie_nowe['id_noclegu'] = df_opinie_nowe['id_noclegu'].astype(int)
df_opinie_nowe['ocena'] = df_opinie_nowe['ocena'].astype(int)
df_opinie_nowe['czy_edytowana'] = df_opinie_nowe['czy_edytowana'].astype(int)

# Konwersja na natywne obiekty Pythona (zamiana NaN/NaT na czyste None dla SQL Server)
df_rezerwacje = df_rezerwacje.astype(object).where(df_rezerwacje.notnull(), None)
df_platnosci = df_platnosci.astype(object).where(df_platnosci.notnull(), None)
df_opinie_nowe = df_opinie_nowe.astype(object).where(df_opinie_nowe.notnull(), None)


# --- URUCHOMIENIE FUNKCJI ZAPISUJĄCEJ BATCHE ---
zapisz_tabele_identity_fast(df_rezerwacje, "rezerwacje")
zapisz_tabele_identity_fast(df_platnosci, "platnosci")
zapisz_tabele_identity_fast(df_opinie_nowe, "opinie")


# --- 4. AKTUALIZACJA POLA 'liczba_opinii' ORAZ 'srednia_ocena' W NOCLEGACH ---
print("\nAktualizacja statystyk (liczba i średnia ocen) w tabeli 'noclegi'...")

df_statystyki = df_opinie_nowe.groupby('id_noclegu').agg(
    nowa_liczba=('ocena', 'count'),
    nowa_srednia=('ocena', 'mean')
).reset_index()

with engine.begin() as sql_conn:
    for idx, row in df_statystyki.iterrows():
        sql_conn.execute(
            text("""
                UPDATE noclegi 
                SET liczba_opinii = :liczba, 
                    srednia_ocena = :srednia 
                WHERE id_noclegu = :id
            """),
            {
                "liczba": int(row['nowa_liczba']), 
                "srednia": round(float(row['nowa_srednia']), 2), 
                "id": int(row['id_noclegu'])
            }
        )

print("\n[SUKCES] Dane zostały poprawnie i szybko zaktualizowane!")



# (ZTI) PS C:\Users\edyta\Desktop\ZTI_strona_noclegi> python c:/Users/edyta/Desktop/ZTI_strona_noclegi/db_fixer.py
# Pobieranie danych o noclegach z bazy...
# Generowanie nowych rezerwacji i opinii...
# Modyfikacja bazy danych Azure SQL...
# Wyczyszczono tabelę: historia_opinii
# Wyczyszczono tabelę: opinie
# Wyczyszczono tabelę: platnosci
# Wyczyszczono tabelę: rezerwacje

# Formatowanie typów danych DataFrame...

# Rozpoczynam wgrywanie danych do rezerwacje (łącznie: 16975 rekordów)...
# rezerwacje: zapis batcha 0 / 16975
# rezerwacje: zapis batcha 1000 / 16975
# rezerwacje: zapis batcha 2000 / 16975
# rezerwacje: zapis batcha 3000 / 16975
# rezerwacje: zapis batcha 4000 / 16975
# rezerwacje: zapis batcha 5000 / 16975
# rezerwacje: zapis batcha 6000 / 16975
# rezerwacje: zapis batcha 7000 / 16975
# rezerwacje: zapis batcha 8000 / 16975
# rezerwacje: zapis batcha 9000 / 16975
# rezerwacje: zapis batcha 10000 / 16975
# rezerwacje: zapis batcha 11000 / 16975
# rezerwacje: zapis batcha 12000 / 16975
# rezerwacje: zapis batcha 13000 / 16975
# rezerwacje: zapis batcha 14000 / 16975
# rezerwacje: zapis batcha 15000 / 16975
# rezerwacje: zapis batcha 16000 / 16975
#  Sukces! Wgrano wszystkie dane do tabeli rezerwacje

# Rozpoczynam wgrywanie danych do platnosci (łącznie: 16975 rekordów)...
# platnosci: zapis batcha 0 / 16975
# platnosci: zapis batcha 1000 / 16975
# platnosci: zapis batcha 2000 / 16975
# platnosci: zapis batcha 3000 / 16975
# platnosci: zapis batcha 4000 / 16975
# platnosci: zapis batcha 5000 / 16975
# platnosci: zapis batcha 6000 / 16975
# platnosci: zapis batcha 7000 / 16975
# platnosci: zapis batcha 8000 / 16975
# platnosci: zapis batcha 9000 / 16975
# platnosci: zapis batcha 10000 / 16975
# platnosci: zapis batcha 11000 / 16975
# platnosci: zapis batcha 12000 / 16975
# platnosci: zapis batcha 13000 / 16975
#  OSTRZEŻENIE: Błąd batcha 13000 (Próba 1/3): ('08S01', '[08S01] [Microsoft][ODBC Driver 18 for SQL Server]TCP Provider: Próba połączenia nie powiodła się, ponieważ połączona strona nie odpowiedziała poprawnie po ustalonym okresie czasu lub utworzone połączenie nie powiodło się, ponieważ połączony host nie odpowiedział.\r\n (10060) (SQLExecDirectW); [08S01] [Microsoft][ODBC Driver 18 for SQL Server]Communication link failure (10060)')
#  OSTRZEŻENIE: Błąd batcha 13000 (Próba 2/3): ('08001', '[08001] [Microsoft][ODBC Driver 18 for SQL Server]SSL Provider: Próba połączenia nie powiodła się, ponieważ połączona strona nie odpowiedziała poprawnie po ustalonym okresie czasu lub utworzone połączenie nie powiodło się, ponieważ połączony host nie odpowiedział.\r\n (10060) (SQLDriverConnect); [08001] [Microsoft][ODBC Driver 18 for SQL Server]Client unable to establish connection. For solutions related to encryption errors, see https://go.microsoft.com/fwlink/?linkid=2226722 (10060)')
#  OSTRZEŻENIE: Błąd batcha 13000 (Próba 3/3): ('42000', "[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Cannot open server 'database-zti' requested by the login. Client with IP address '37.31.42.52' is not allowed to access the server.  To enable access, use the Azure Management Portal or run sp_set_firewall_rule on the master database to create a firewall rule for this IP address or address range.  It may take up to five minutes for this change to take effect. (40615) (SQLDriverConnect); [42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Cannot open server 'database-zti' requested by the login. Client with IP address '37.31.42.52' is not allowed to access the server.  To enable access, use the Azure Management Portal or run sp_set_firewall_rule on the master database to create a firewall rule for this IP address or address range.  It may take up to five minutes for this change to take effect. (40615)")
#  KRYTYCZNY BŁĄD: Batch 13000 nie mógł zostać zapisany.
# Traceback (most recent call last):
#   File "c:\Users\edyta\Desktop\ZTI_strona_noclegi\db_fixer.py", line 580, in <module>
#     zapisz_tabele_identity_fast(df_platnosci, "platnosci")
#   File "c:\Users\edyta\Desktop\ZTI_strona_noclegi\db_fixer.py", line 371, in zapisz_tabele_identity_fast
#     raise e  
#     ^^^^^^^
#   File "c:\Users\edyta\Desktop\ZTI_strona_noclegi\db_fixer.py", line 347, in zapisz_tabele_identity_fast
#     conn = engine.raw_connection()
#            ^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\edyta\miniconda3\envs\ZTI\Lib\site-packages\sqlalchemy\engine\base.py", line 3317, in raw_connection
#     return self.pool.connect()
#            ^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\edyta\miniconda3\envs\ZTI\Lib\site-packages\sqlalchemy\pool\base.py", line 448, in connect
#     return _ConnectionFairy._checkout(self)
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\edyta\miniconda3\envs\ZTI\Lib\site-packages\sqlalchemy\pool\base.py", line 1272, in _checkout
#     fairy = _ConnectionRecord.checkout(pool)
#             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\edyta\miniconda3\envs\ZTI\Lib\site-packages\sqlalchemy\pool\base.py", line 717, in checkout
#     with util.safe_reraise():
#          ^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\edyta\miniconda3\envs\ZTI\Lib\site-packages\sqlalchemy\util\langhelpers.py", line 121, in __exit__
#     raise exc_value.with_traceback(exc_tb)
#   File "C:\Users\edyta\miniconda3\envs\ZTI\Lib\site-packages\sqlalchemy\pool\base.py", line 715, in checkout
#     dbapi_connection = rec.get_connection()
#                        ^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\edyta\miniconda3\envs\ZTI\Lib\site-packages\sqlalchemy\pool\base.py", line 837, in get_connection
#     self.__connect()
#   File "C:\Users\edyta\miniconda3\envs\ZTI\Lib\site-packages\sqlalchemy\pool\base.py", line 900, in __connect
#     with util.safe_reraise():
#          ^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\edyta\miniconda3\envs\ZTI\Lib\site-packages\sqlalchemy\util\langhelpers.py", line 121, in __exit__
#     raise exc_value.with_traceback(exc_tb)
#   File "C:\Users\edyta\miniconda3\envs\ZTI\Lib\site-packages\sqlalchemy\pool\base.py", line 896, in __connect
#     self.dbapi_connection = connection = pool._invoke_creator(self)
#                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\edyta\miniconda3\envs\ZTI\Lib\site-packages\sqlalchemy\engine\create.py", line 667, in connect
#     return dialect.connect(*cargs_tup, **cparams)
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\edyta\miniconda3\envs\ZTI\Lib\site-packages\sqlalchemy\engine\default.py", line 630, in connect
#     return self.loaded_dbapi.connect(*cargs, **cparams)  # type: ignore[no-any-return]  # NOQA: E501
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# pyodbc.ProgrammingError: ('42000', "[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Cannot open server 'database-zti' requested by the login. Client with IP address '37.31.42.52' is not allowed to access the server.  To enable access, use the Azure Management Portal or run sp_set_firewall_rule on the master database to create a firewall rule for this IP address or address range.  It may take up to five minutes for this change to take effect. (40615) (SQLDriverConnect); [42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Cannot open server 'database-zti' requested by the login. Client with IP address '37.31.42.52' is not allowed to access the server.  To enable access, use the Azure Management Portal or run sp_set_firewall_rule on the master database to create a firewall rule for this IP address or address range.  It may take up to five minutes for this change to take effect. (40615)")
# (ZTI) PS C:\Users\edyta\Desktop\ZTI_strona_noclegi> 