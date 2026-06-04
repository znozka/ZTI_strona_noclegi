# import pyodbc
# import sys
# import csv  # Dodany moduł do obsługi zapisu CSV

# # =========================================================================
# # KONFIGURACJA POŁĄCZENIA
# # =========================================================================
# CONNECTION_STRING = (
#     "DRIVER={ODBC Driver 18 for SQL Server};"
#     "SERVER=database-zti.database.windows.net,1433;"
#     "DATABASE=NoclegiDB_2026-05-26T20-19Z;"
#     "UID=Zuza;"
#     "PWD=haslo.Admin;"
#     "Encrypt=yes;"
#     "TrustServerCertificate=yes;"
# )

# # =========================================================================
# # DEFINICJA 10 UNIKALNYCH OPISÓW
# # =========================================================================
# OPISY = {
#     "tani_standard": (
#         "Przytulny i funkcjonalny pokój stworzony z myślą o osobach szukających budżetowego noclegu w świetnej lokalizacji. "
#         "Wnętrze wyposażone jest w wygodne łóżko, kompaktowe biurko do pracy oraz stały dostęp do szybkiego Internetu. "
#         "Do dyspozycji gości pozostaje w pełni wyposażona, współdzielona kuchnia oraz nowoczesny węzeł sanitarny. "
#         "Idealny wybór dla studentów, backpackerów oraz osób podróżujących w celach biznesowych."
#     ),
#     "tani_rustykalny": (
#         "Prosty, klimatyczny obiekt otoczony naturą, idealny na spokojny wypoczynek z dala od miejskiego zgiełku. "
#         "Wnętrze urządzone zostało w tradycyjnym stylu z przewagą drewnianych elementów, co zapewnia domową atmosferę. "
#         "Na zewnątrz znajduje się dedykowane miejsce na ognisko, grill oraz przestronny ogród do rekreacji. "
#         "To doskonała opcja dla miłośników pieszych wycieczek i osób poszukujących oszczędności."
#     ),
#     "tani_miejski": (
#         "Ekonomiczny apartament zlokalizowany w bezpośrednim sąsiedztwie kluczowych punktów komunikacyjnych miasta. "
#         "Mieszkanie posiada podstawowy aneks kuchenny, prywatną łazienkę oraz komfortową przestrzeń wypoczynkową. "
#         "W pobliżu znajdują się liczne sklepy spożywcze, klimatyczne kawiarnie oraz parki miejskie. "
#         "Sprawdzi się idealnie jako baza wypadowa na intensywne, weekendowe zwiedzanie okolicy."
#     ),
#     "sredni_apartament": (
#         "Nowoczesny apartament o podwyższonym standardzie, urządzony przez profesjonalnego projektanta wnętrz. "
#         "Do dyspozycji gości oddajemy przestronny salon z telewizorem, osobną sypialnię oraz kompletnie wyposażoną kuchnię. "
#         "Z dużych okien roztacza się ładny widok na architekturę, a klimatyzacja zapewnia komfort w upalne dni. "
#         "Obiekt jest doskonałym wyborem zarówno dla par, jak i rodzin szukających wygody w rozsądnej cenie."
#     ),
#     "sredni_domek": (
#         "Komfortowy dom wakacyjny, łączący nowoczesne udogodnienia z bliskością naturalnego krajobrazu. "
#         "Obiekt oferuje przestronny taras z meblami ogrodowymi, idealny na poranną kawę lub wieczorny relaks. "
#         "Wewnątrz znajduje się przytulny salon z kominkiem, nowoczesna łazienka oraz bezpieczny kącik zabaw dla dzieci. "
#         "Świetna opcja na dłuższy urlop dla grupy znajomych bądź rodzin wielodzietnych."
#     ),
#     "sredni_pensjonat": (
#         "Kameralny obiekt noclegowy oferujący gościom wysoki poziom prywatności oraz niezwykle ciepłą atmosferę. "
#         "Każdy pokój posiada własną łazienkę, balkon, lodówkę oraz zestaw do parzenia kawy i herbaty. "
#         "Na terenie posesji dostępny jest monitorowany parking oraz zamykana przechowalnia na rowery i narty. "
#         "W cenie pobytu goście mogą korzystać ze wspólnej strefy wypoczynkowej oraz tarasu widokowego."
#     ),
#     "premium_apartament": (
#         "Ekskluzywny penthouse zlokalizowany w najbardziej prestiżowej dzielnicy, oferujący zapierający dech w piersiach widok. "
#         "Wnętrze wykończono najwyższej jakośći materiałami, takimi jak naturalny marmur oraz egzotyczne drewno. "
#         "Goście mają do dyspozycji prywatne jacuzzi na tarasie, system inteligentnego domu oraz dostęp do strefy wellness w budynku. "
#         "To propozycja dla najbardziej wymagających klientów, oczekujących bezkompromisowego luksusu."
#     ),
#     "premium_willa": (
#         "Luksusowa rezydencja z prywatnym, podgrzewanym basenem zlokalizowana w pierwszej linii brzegowej. "
#         "Nieruchomość oferuje monumentalny salon z panoramicznymi oknami, strefę kinową oraz profesjonalną kuchnię szefa kuchni. "
#         "Otaczający willę ogród zapewnia pełną intymność, a taras rekreacyjny pozwala na organizację eleganckich przyjęć. "
#         "Niezrównany standard wykończenia gwarantuje niezapomniane wrażenia z pobytu o każdej porze roku."
#     ),
#     "premium_hotel": (
#         "Unikalny obiekt butikowy, w którym historyczna architektura łączy się z ultranowoczesnym designem. "
#         "Pokoje oferują spersonalizowany serwis, najwyższej klasy pościel antyalergiczną oraz luksusowe kosmetyki w łazienkach. "
#         "Na miejscu działa nagradzana restauracja serwująca dania kuchni lokalnej w nowoczesnym wydaniu. "
#         "Dedykowany konsjerż pozostaje do stałej dyspozycji gości, dbając o realizację wszelkich indywidualnych życzeń."
#     )
# }

# # =========================================================================
# # LOGIKA DOPASOWANIA OPISU
# # =========================================================================
# def dobierz_opis(typ_obiektu, cena):
#     typ_obiektu_lower = str(typ_obiektu).lower()
    
#     if cena < 150:
#         if "dom" in typ_obiektu_lower or "działk" in typ_obiektu_lower or "agrotur" in typ_obiektu_lower:
#             return OPISY["tani_rustykalny"]
#         elif "apartament" in typ_obiektu_lower or "mieszkanie" in typ_obiektu_lower:
#             return OPISY["tani_miejski"]
#         else:
#             return OPISY["tani_standard"]
#     elif cena >= 500:
#         if "apartament" in typ_obiektu_lower or "penthouse" in typ_obiektu_lower:
#             return OPISY["premium_apartament"]
#         elif "dom" in typ_obiektu_lower or "willa" in typ_obiektu_lower or "rezydencja" in typ_obiektu_lower:
#             return OPISY["premium_willa"]
#         else:
#             return OPISY["premium_hotel"]
#     else:
#         if "apartament" in typ_obiektu_lower or "mieszkanie" in typ_obiektu_lower:
#             return OPISY["sredni_apartament"]
#         elif "dom" in typ_obiektu_lower or "domek" in typ_obiektu_lower:
#             return OPISY["sredni_domek"]
#         else:
#             return OPISY["sredni_pensjonat"]

# # =========================================================================
# # GŁÓWNY PROCES (POBRANIE + ZAPIS DO CSV + AKTUALIZACJA)
# # =========================================================================
# def uruchom_naprawe_bazy():
#     print("Inicjalizacja połączenia z bazą danych Azure SQL...")
#     connection = None
    
#     try:
#         connection = pyodbc.connect(CONNECTION_STRING)
#         cursor = connection.cursor()
        
#         connection.autocommit = False
        
#         print("\n--- ETAP 1: POBIERANIE AKTUALNEGO STANU TABELI 'NOCLEGI' ---")
#         cursor.execute("SELECT id_noclegu, nazwa, typ_obiektu, cena_za_noc, opis FROM noclegi")
#         noclegi_w_bazie = cursor.fetchall()
        
#         print(f"Pobrano pomyślnie {len(noclegi_w_bazie)} rekordów.")
        
#         if len(noclegi_w_bazie) == 0:
#             print("Brak danych w tabeli 'noclegi'. Przerywam działanie skryptu.")
#             return

#         # -----------------------------------------------------------------
#         # NOWOŚĆ: ZAPIS KOPII ZAPASOWEJ DO PLIKU CSV
#         # -----------------------------------------------------------------
#         nazwa_pliku_kopii = "kopia_noclegi_przed_zmiana.csv"
#         print(f"Zapisywanie kopii zapasowej danych do pliku: {nazwa_pliku_kopii}...")
        
#         with open(nazwa_pliku_kopii, mode='w', encoding='utf-8', newline='') as plik_csv:
#             writer = csv.writer(plik_csv, delimiter=';')
#             # Zapis nagłówków kolumn
#             writer.writerow(['id_noclegu', 'nazwa', 'typ_obiektu', 'cena_za_noc', 'stary_opis'])
#             # Zapis wszystkich wierszy
#             for row in noclegi_w_bazie:
#                 writer.writerow([row[0], row[1], row[2], row[3], row[4]])
                
#         print("Kopia zapasowa została bezpiecznie zapisana na Twoim dysku!")

#         print("\nPodgląd obecnych rekordów w bazie (pierwsze 5):")
#         print("-" * 90)
#         for row in noclegi_w_bazie[:5]:
#             id_n, nazwa, typ, cena, stary_opis = row
#             stary_opis_short = (str(stary_opis)[:40] + "...") if stary_opis else "[NULL / PUSTY]"
#             print(f"ID: {id_n} | Nazwa: {nazwa[:20]}... | Typ: {typ} | Cena: {cena} zł | Obecny opis: {stary_opis_short}")
#         print("-" * 90)
            
#         # -----------------------------------------------------------------
#         # ETAP 2: AKTUALIZACJA KOLUMNY OPIS
#         # -----------------------------------------------------------------
#         print("\n--- ETAP 2: ROZPOCZYNANIE BEZPIECZNEJ MODYFIKACJI OPISÓW ---")
#         modyfikowane_rekordy = 0
#         update_query = "UPDATE noclegi SET opis = ? WHERE id_noclegu = ?"
        
#         for index, row in enumerate(noclegi_w_bazie, start=1):
#             id_noclegu = row[0]
#             typ_obiektu = row[2]
#             cena_za_noc = float(row[3])
            
#             nowy_opis = dobierz_opis(typ_obiektu, cena_za_noc)
            
#             cursor.execute(update_query, (nowy_opis, id_noclegu))
#             modyfikowane_rekordy += 1
            
#             if index % 5 == 0 or index == len(noclegi_w_bazie):
#                 print(f"Przygotowano modyfikację dla: {index}/{len(noclegi_w_bazie)} obiektów...")

#         print("\nWszystkie opisy wygenerowane pomyślnie w pamięci podręcznej.")
#         print("Zatwierdzanie zmian w bazie Azure SQL (COMMIT)...")
#         connection.commit()
#         print(f"Sukces! Zaktualizowano kolumnę 'opis' dla {modyfikowane_rekordy} rekordów.")

#     except pyodbc.Error as sql_error:
#         print(f"\n[BŁĄD SQL]: Coś poszło nie tak z zapytaniem.", file=sys.stderr)
#         print(f"Szczegóły: {sql_error}", file=sys.stderr)
#         if connection:
#             print("Wycofywanie zmian w bazie (ROLLBACK)...", file=sys.stderr)
#             connection.rollback()
            
#     except Exception as e:
#         print(f"\n[BŁĄD APLIKACJI]: {e}", file=sys.stderr)
#         if connection:
#             print("Wycofywanie zmian w bazie (ROLLBACK)...", file=sys.stderr)
#             connection.rollback()

#     finally:
#         if connection:
#             cursor.close()
#             connection.close()
#             print("\nPołączenie z bazą danych zostało zamknięte.")

# if __name__ == "__main__":
#     uruchom_naprawe_bazy()import pyodbc
import pyodbc
import sys
import csv
import random

# =========================================================================
# KONFIGURACJA POŁĄCZENIA
# =========================================================================
CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=database-zti.database.windows.net,1433;"
    "DATABASE=NoclegiDB_2026-05-26T20-19Z;"
    "UID=Zuza;"
    "PWD=haslo.Admin;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

# =========================================================================
# DEFINICJA 30 UNIKALNYCH OPISÓW (KAŻDY PO 3 ZDANIA)
# =========================================================================
OPISY = {
    # --- OBIEKTY Z NISKĄ/PRZECIĘTNĄ OCENĄ ("tanie" / budżetowe podejście) ---
    "tani_hotel": "Prosty i budżetowy hotel oferujący podstawowe pokoje dla niewymagających podróżnych. Wnętrza wyposażone są w standardowe meble, mały telewizor oraz bezpłatny dostęp do sieci Wi-Fi. Lokalizacja przy arterii komunikacyjnej ułatwia szybki dojazd do różnych części miasta.",
    "tani_apartament": "Ekonomiczny apartament zlokalizowany w bloku mieszkalnym blisko centrum. Mieszkanie posiada podstawowy aneks kuchenny, skromną łazienkę oraz łóżko sypialniane. To świetna opcja dla osób szukających oszczędności i niezależności podczas krótkiego pobytu.",
    "tani_bb": "Skromny obiekt typu Bed and Breakfast oferujący nocleg w niewygórowanej cenie. Rano serwowane jest proste, klasyczne śniadanie kontynentalne w formie małego bufetu. Pokoje są niewielkie, ale zapewniają wszystko co niezbędne do odpoczynku po całym dniu.",
    "tani_schronisko": "Klasyczne schronisko z wieloosobowymi pokojami i niesamowitym, turystycznym klimatem. Do dyspozycji gości pozostaje wspólna kuchnia turystyczna oraz ogólnodostępny węzeł sanitarny. Idealny wybór dla pasjonatów wędrówek, którzy cenią atmosferę wyżej niż luksusy.",
    "tani_wynajem": "Prosty domek letniskowy na wynajem, zlokalizowany w cichej i zielonej okolicy. Obiekt oferuje podstawowe wyposażenie kuchenne, skromny salon oraz miejsce do biesiadowania na świeżym powietrwiu. Dobra, budżetowa opcja na weekendowy wypad ze znajomymi na łono natury.",

    # --- OBIEKTY ZE ŚREDNIĄ/DOBRĄ OCENĄ ---
    "sredni_hotel": "Komfortowy, trzygwiazdkowy hotel oferujący wysoki standard obsługi oraz nowoczesne wnętrza. Pokoje wyposażone są w wygodne łóżka, klimatyzację, minibary oraz przestronne biurka do pracy. Na miejscu działa restauracja serwująca urozmaicone śniadania i dania kuchni lokalnej.",
    "sredni_apartament": "Nowoczesny apartament o podwyższonym standardzie, kompleksowo urządzony przez architekta. Z dużych okien roztacza się przyjemny widok na miasto, a aneks kuchenny posiada pełne wyposażenie AGD. Obiekt gwarantuje pełną prywatność i domową atmosferę w podróży.",
    "sredni_bb": "Urokliwy i przytulny obiekt B&B prowadzony przez niezwykle gościnnych właścicieli. Każdego ranka goście mogą delektować się pysznym, domowym śniadaniem przygotowywanym z lokalnych produktów. Pokoje mają unikalny wystrój i zapewniają doskonałe warunki do relaksu.",
    "sredni_schronisko": "Zadbany i świetnie zlokalizowany obiekt schroniskowy o bardzo dobrych opiniach. Oferuje czyste pokoje prywatne oraz mniejsze sale wieloosobowe z wygodnymi materacami. Na miejscu działa klimatyczna jadalnia serwująca smaczne, ciepłe posiłki regeneracyjne.",
    "sredni_wynajem": "Komfortowy dom wakacyjny na wynajem, idealny na dłuższy urlop w gronie rodziny. Obiekt oferuje przestronny salon z kominkiem, nowoczesną łazienka oraz ogrodzoną strefę rekreacyjną. Na tarasie znajdują się meble ogrodowe, które zachęcają do wypoczynku na słońcu.",

    # --- OBIEKTY Z NAJWYŻSZĄ OCENĄ (Premium / Doskonałe opinie) ---
    "premium_hotel": "Ekskluzywny hotel butikowy, który zachwyca unikalnym designem i spersonalizowaną obsługą. Pokoje oferują najwyższej klasy pościel antyalergiczną, marmurowe łazienki oraz luksusowe kosmetyki. Dedykowany konsjerż pozostaje do stałej dyspozycji gości, dbając o każdy detal pobytu.",
    "premium_apartament": "Luksusowy penthouse w prestiżowym apartamentowcu, oferujący zapierający dech w piersiach widok na panoramę. Wnętrze wykończono materiałami premium, takimi jak egzotyczne drewno, i wyposażono w system inteligentnego domu. Do dyspozycji gości jest prywatny taras z całorocznym jacuzzi.",
    "premium_bb": "Wyjątkowy, elitarny obiekt pensjonatowy B&B, który gwarantuje absolutnie bezkompromisowy standard wypoczynku. Śniadania premium przygotowywane se przez szefa kuchni na indywidualne zamówienie z ekologicznych składników. Przepiękny, otaczający ogród zapewnia gościom pełną intymność i ciszę.",
    "premium_schronisko": "Nowoczesny, górski resort schroniskowy, który redefiniuje pojęcie wypoczynku w sercu natury. Obiekt łączy tradycyjną architekturę z luksusowymi udogodnieniami, takimi jak przeszklona sauna z widokiem na góry. Pokoje wykończone w drewnie posiadają prywatne, luksusowe łazienki.",
    "premium_wynajem": "Prestiżowa willa wakacyjna na wyłączność, wyposażona w prywatny, podgrzewany basen zewnętrzny. Monumentalne, panoramiczne okna salonu otwierają się na niesamowity krajobraz, zapewniając stały kontakt z naturą. To idealne miejsce dla najbardziej wymagających klientów szukających luksusowej oazy spokoju.",

    # --- REZERWOWE OPISY OGÓLNE (w razie braku precyzyjnego dopasowania typu) ---
    "ogolny_tani": "Przytulny i funkcjonalny obiekt stworzony z myślą o osobach szukających budżetowego noclegu. Wnętrze wyposażone jest w podstawowe meble oraz stały dostęp do bezprzewodowego Internetu. Dobry wybór dla podróżnych, dla których priorytetem jest atrakcyjna cena.",
    "ogolny_sredni": "Komfortowe miejsce noclegowe oferujące gościom świetną relację jakości do ceny. Obiekt zapewnia czyste, dobrze wyposażone pokoje oraz przyjazną obsługę dbającą o komfort pobytu. Sprawdzi się idealnie zarówno podczas wyjazdu turystycznego, jak i służbowego.",
    "ogolny_premium": "Ekskluzywna przestrzeń noclegowa stworzona z myślą o najbardziej wymagających gościach. Najwyższy standard wykończenia wnętrz łączy się tutaj z nienagannym podejściem do obsługi klienta. Każda chwila spędzona w tym miejscu gwarantuje niezapomniane, luksusowe wrażenia."
}

# =========================================================================
# LOGIKA DOPASOWANIA OPISU (PO OCENIE I TYPIE NOCLEGU)
# =========================================================================
def dobierz_opis(typ_obiektu, ocena):
    typ = str(typ_obiektu).lower()
    
    # Progi dla skali 1-10
    if ocena >= 8.5:
        poka = "premium"
    elif ocena < 6.5:
        poka = "tani"
    else:
        poka = "sredni"
        
    # Dopasowanie na podstawie typu noclegu
    if "hotel" in typ:
        return OPISY[f"{poka}_hotel"]
    elif "apartament" in typ or "apartment" in typ or "mieszkanie" in typ:
        return OPISY[f"{poka}_apartament"]
    elif "b&b" in typ or "bed and breakfast" in typ or "pensjonat" in typ or "pokój" in typ or "pokoj" in typ:
        return OPISY[f"{poka}_bb"]
    elif "schronisk" in typ:
        return OPISY[f"{poka}_schronisko"]
    elif "wynajem" in typ or "wakacyj" in typ or "domek" in typ or "willa" in typ or "chata" in typ or "dom" in typ:
        return OPISY[f"{poka}_wynajem"]
    else:
        return OPISY[f"ogolny_{poka}"]

# =========================================================================
# GŁÓWNY PROCES (POBRANIE + ZAPIS DO CSV + AKTUALIZACJA)
# =========================================================================
def uruchom_naprawe_bazy():
    print("Inicjalizacja połączenia z bazą danych Azure SQL...")
    connection = None
    
    try:
        connection = pyodbc.connect(CONNECTION_STRING)
        cursor = connection.cursor()
        
        connection.autocommit = False
        
        print("\n--- ETAP 1: POBIERANIE AKTUALNEGO STANU TABELI 'NOCLEGI' ---")
        # ZMIANA: Pobieramy kolumnę 'srednia_ocena' zgodnie ze strukturą bazy
        cursor.execute("SELECT id_noclegu, nazwa, typ_obiektu, srednia_ocena, opis FROM noclegi")
        noclegi_w_bazie = cursor.fetchall()
        
        print(f"Pobrano pomyślnie {len(noclegi_w_bazie)} rekordów.")
        
        if len(noclegi_w_bazie) == 0:
            print("Brak danych w tabeli 'noclegi'. Przerywam działanie skryptu.")
            return

        # Zapis kopii zapasowej do pliku CSV
        nazwa_pliku_kopii = "kopia_noclegi_przed_zmiana.csv"
        print(f"Zapisywanie kopii zapasowej danych do pliku: {nazwa_pliku_kopii}...")
        
        with open(nazwa_pliku_kopii, mode='w', encoding='utf-8', newline='') as plik_csv:
            writer = csv.writer(plik_csv, delimiter=';')
            writer.writerow(['id_noclegu', 'nazwa', 'typ_obiektu', 'srednia_ocena', 'stary_opis'])
            for row in noclegi_w_bazie:
                writer.writerow([row[0], row[1], row[2], row[3], row[4]])
                
        print("Kopia zapasowa została bezpiecznie zapisana na Twoim dysku!")

        print("\nPodgląd obecnych rekordów w bazie (pierwsze 5):")
        print("-" * 90)
        for row in noclegi_w_bazie[:5]:
            id_n, nazwa, typ, ocena_val, stary_opis = row
            stary_opis_short = (str(stary_opis)[:40] + "...") if stary_opis else "[NULL / PUSTY]"
            print(f"ID: {id_n} | Nazwa: {nazwa[:20]}... | Typ: {typ} | Śr. ocena: {ocena_val} | Obecny opis: {stary_opis_short}")
        print("-" * 90)
            
        # ETAP 2: AKTUALIZACJA KOLUMNY OPIS
        print("\n--- ETAP 2: ROZPOCZYNANIE BEZPIECZNEJ MODYFIKACJI OPISÓW ---")
        modyfikowane_rekordy = 0
        update_query = "UPDATE noclegi SET opis = ? WHERE id_noclegu = ?"
        
        for index, row in enumerate(noclegi_w_bazie, start=1):
            id_noclegu = row[0]
            typ_obiektu = row[2]
            
            # Bezpieczna obsługa wartości NULL w bazie danych
            try:
                ocena = float(row[3]) if row[3] is not None else 7.5
            except ValueError:
                ocena = 7.5
            
            nowy_opis = dobierz_opis(typ_obiektu, ocena)
            
            cursor.execute(update_query, (nowy_opis, id_noclegu))
            modyfikowane_rekordy += 1
            
            if index % 5 == 0 or index == len(noclegi_w_bazie):
                print(f"Przygotowano modyfikację dla: {index}/{len(noclegi_w_bazie)} obiektów...")

        print("\nWszystkie opisy wygenerowane pomyślnie w pamięci podręcznej.")
        print("Zatwierdzanie zmian w bazie Azure SQL (COMMIT)...")
        connection.commit()
        print(f"Sukces! Zaktualizowano kolumnę 'opis' dla {modyfikowane_rekordy} rekordów.")

    except pyodbc.Error as sql_error:
        print(f"\n[BŁĄD SQL]: Coś poszło nie tak z zapytaniem.", file=sys.stderr)
        print(f"Szczegóły: {sql_error}", file=sys.stderr)
        if connection:
            print("Wycofywanie zmian w bazie (ROLLBACK)...", file=sys.stderr)
            connection.rollback()
            
    except Exception as e:
        print(f"\n[BŁĄD APLIKACJI]: {e}", file=sys.stderr)
        if connection:
            print("Wycofywanie zmian w bazie (ROLLBACK)...", file=sys.stderr)
            connection.rollback()

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("\nPołączenie z bazą danych zostało zamknięte.")

if __name__ == "__main__":
    uruchom_naprawe_bazy()