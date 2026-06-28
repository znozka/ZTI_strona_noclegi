import pyodbc
import numpy as np  # Wymaga: pip install numpy

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=database-zti.database.windows.net,1433;"
    "DATABASE=NoclegiDB_2026-05-26T20-19Z;"
    "UID=Zuza;"
    "PWD=haslo.Admin;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

PRZYPISANIE_OPISOW = {
    "HOTEL": [
        "Hotel budżetowy - idealny na krótki przystanek w podróży. Oferuje niezbędne minimum w bardzo atrakcyjnej cenie. To świetny wybór dla osób, które większość czasu spędzają na zwiedzaniu.",
        "Ekonomiczny hotel z podstawowym wyposażeniem dla każdego. Pokoje są czyste i funkcjonalne, zapewniając spokojny sen. Lokalizacja pozwala na łatwy dostęp do głównych tras komunikacyjnych.",
        "Komfortowy hotel w przystępnej cenie, blisko centrum. Obiekt wyróżnia się bardzo dobrą obsługą oraz wygodnymi łóżkami. Goście docenią szybki dojazd do najważniejszych punktów miasta.",
        "Stylowy obiekt hotelowy zapewniający dobry standard wypoczynku. Wnętrza zostały zaprojektowane z myślą o funkcjonalności i estetyce. Idealne miejsce dla osób ceniących dobrą relację jakości do ceny.",
        "Hotel o standardzie biznesowym z szybkim Wi-Fi. Pokoje wyposażone są w wygodne biurka do pracy. Dodatkowym atutem jest dostęp do sali konferencyjnej oraz cichej strefy wypoczynku.",
        "Miejsce łączące elegancję z nowoczesnymi udogodnieniami. Każdy pokój posiada klimatyzację oraz przestronną łazienkę. Hotel znajduje się w spokojnej okolicy, co gwarantuje udany relaks.",
        "Wysokiej klasy hotel z profesjonalną obsługą i komfortem. Przestronne wnętrza zostały wykończone z dbałością o każdy szczegół. Do dyspozycji gości pozostaje strefa fitness oraz wyśmienita restauracja.",
        "Luksusowy obiekt z pełną gamą usług dla wymagających. Oferuje dostęp do całodobowej recepcji oraz usług concierge. To doskonałe miejsce dla osób szukających wytchnienia w centrum wydarzeń.",
        "Ekskluzywny hotel ze strefą SPA i widokiem na miasto. Goście mogą korzystać z sauny oraz basenu po męczącym dniu. Wysoki standard usług gwarantuje pełne zadowolenie nawet najbardziej wymagających osób.",
        "Prestiżowy hotel premium - kwintesencja luksusu i wygody. Indywidualne podejście do gościa sprawia, że każdy pobyt staje się wyjątkowy. Obiekt zapewnia prywatność oraz dostęp do najnowocześniejszych udogodnień."
    ],
    "APARTAMENT": [
        "Prosta kawalerka dla osób szukających noclegu w niskiej cenie. Mieszkanie posiada podstawowy aneks kuchenny oraz wygodne miejsce do spania. Idealne rozwiązanie na szybki wyjazd w pojedynkę.",
        "Przytulne studio z dostępem do wszystkich niezbędnych sprzętów. Jasne wnętrza sprawiają, że pobyt jest bardzo przyjemny. Obiekt znajduje się blisko przystanków transportu publicznego.",
        "Funkcjonalne mieszkanie w świetnej lokalizacji miejskiej. W pobliżu znajdziesz liczne kawiarnie i sklepy spożywcze. To doskonała baza wypadowa do poznawania lokalnych atrakcji.",
        "Jasne wnętrza w nowoczesnym stylu, idealne na krótki pobyt. Apartament jest w pełni wyposażony, włączając w to naczynia i sprzęt AGD. Panuje tu cisza, która sprzyja wieczornemu odpoczynkowi.",
        "Apartament o wysokim standardzie, zaprojektowany dla wygody. Przemyślany układ pomieszczeń pozwala na komfortowy wypoczynek po całym dniu. Z okien rozpościera się widok na spokojną część miasta.",
        "Przestronne mieszkanie blisko głównych atrakcji turystycznych. Duży salon zachęca do relaksu przy dobrej książce. To idealny wybór dla osób planujących dłuższy pobyt w mieście.",
        "Elegancki apartament z tarasem i pięknym widokiem. Nowoczesne meble dodają wnętrzom niepowtarzalnego charakteru. To świetne miejsce na wieczorny relaks z kieliszkiem wina w dłoni.",
        "Apartament typu premium z designerskim wykończeniem. Wnętrze zdobią unikalne dodatki oraz wysokiej jakości materiały. Zapewniamy pełną prywatność oraz dostęp do szybkiego internetu.",
        "Luksusowy apartament dla wymagających klientów biznesowych. Wyposażony w profesjonalne stanowisko do pracy oraz ekspres do kawy. Lokalizacja w prestiżowej dzielnicy zapewnia szybki dojazd do biurowców.",
        "Ekskluzywny apartament z pełnym serwisem i prywatnością. Codzienna obsługa dba o czystość i komfort na najwyższym poziomie. To idealna przystań dla osób ceniących spokój i luksus."
    ],
    "BOUTIQUE": [
        "Mały, kameralny obiekt dla szukających ciszy i spokoju. Każdy pokój został urządzony w unikalnym, indywidualnym stylu. Idealna propozycja dla osób unikających dużych sieci hotelowych.",
        "Miejsce z klimatem, oferujące miłą obsługę w niskiej cenie. Panuje tu ciepła, niemal rodzinna atmosfera sprzyjająca odpoczynkowi. To świetna alternatywa dla typowych obiektów turystycznych.",
        "Butikowy obiekt z indywidualnym podejściem do każdego gościa. Personel z przyjemnością doradzi, gdzie warto zjeść lub co warto zwiedzić. Poczujesz się tutaj jak prawdziwy gość, a nie klient.",
        "Artystyczny hotelik z unikalnym wystrojem wnętrz. Każdy detal został przemyślany i dopasowany do charakteru budynku. To miejsce stworzone dla osób kochających piękno i oryginalność.",
        "Obiekt łączący nowoczesny design z domową atmosferą. Wnętrza są jasne, przestronne i bardzo przyjazne. Idealnie sprawdzi się na romantyczny wyjazd we dwoje.",
        "Wyjątkowe miejsce dla koneserów niebanalnych wnętrz. Każdy pokój posiada własną historię i duszę, co czyni pobyt niezapomnianym. To lokalizacja, która inspiruje i odpręża.",
        "Butikowy luksus, gdzie każdy detal ma swoje znaczenie. Wyselekcjonowane meble i dodatki tworzą spójną całość. Goście mogą liczyć na dyskrecję oraz obsługę na najwyższym poziomie.",
        "Ekskluzywna przestrzeń butikowa z indywidualnym stylem. Obiekt oferuje kameralną strefę relaksu oraz wyśmienite śniadania. To idealny wybór dla osób szukających luksusu w mniejszym wydaniu.",
        "Miejsce dla wymagających gości szukających inspiracji. Unikalny koncept hotelu sprawia, że każdy powrót jest wyjątkowy. Cisza i spokój są tutaj gwarantowane przez cały pobyt.",
        "Prestiżowy butik - unikalny komfort na najwyższym poziomie. Połączenie wyszukanej estetyki z dbałością o potrzeby gości. To miejsce, do którego chce się wracać przy każdej okazji."
    ],
    "WYNAJEM WAKACYJNY": [
        "Prosty dom letniskowy blisko natury na każdą kieszeń. Posiada bezpośredni dostęp do lasu i terenów spacerowych. Idealne miejsce dla osób chcących uciec od zgiełku miasta.",
        "Przytulna chatka wakacyjna oferująca spokój i relaks. Wyposażona w podstawowy sprzęt niezbędny podczas wakacji. To świetna baza wypadowa na piesze wędrówki po okolicy.",
        "Domek z dostępem do ogrodu, idealny na weekendowy wypad. Przestrzeń wokół pozwala na swobodną zabawę i wypoczynek na świeżym powietrzu. Dostępne są wszystkie niezbędne naczynia kuchenne.",
        "Wypoczynkowa oaza z miejscem na grilla i odpoczynek. Teren jest ogrodzony, co zapewnia bezpieczeństwo podczas pobytu. To doskonałe miejsce dla rodzin z dziećmi szukających wytchnienia.",
        "Przestronny dom wakacyjny dla rodziny w dobrej cenie. Kilka sypialni pozwala na komfortowy wypoczynek wielu osobom. Bliskość jeziora zachęca do aktywnego spędzania czasu na zewnątrz.",
        "Dom z tarasem, doskonałe miejsce na letnie biesiadowanie. Wieczory przy grillu staną się niezapomnianym wspomnieniem z wyjazdu. Obiekt jest w pełni wyposażony i gotowy do zamieszkania.",
        "Wysokiej klasy dom wakacyjny w zacisznej okolicy. Nowoczesne wykończenie łączy się z naturalnymi materiałami. To idealna propozycja dla osób ceniących wysoki standard wypoczynku.",
        "Wakacyjna rezydencja z pełnym dostępem do infrastruktury. Obiekt posiada prywatny dostęp do plaży oraz sprzęt rekreacyjny. Zapewniamy pełen komfort oraz swobodę, jak we własnym domu.",
        "Luksusowy dom letniskowy z prywatną strefą relaksu. Goście mogą korzystać z jacuzzi oraz przestronnej sauny. To najwyższy poziom wypoczynku w otoczeniu pięknej przyrody.",
        "Ekskluzywna willa wakacyjna - wypoczynek premium. Wyjątkowy design oraz najwyższa jakość wykończenia zachwycą każdego gościa. To miejsce stworzone dla osób szukających spokoju w wielkim stylu."
    ],
    "B&B": [
        "Proste miejsce na nocleg z dostępem do podstawowego śniadania. Pokoje są czyste i utrzymane w minimalistycznym stylu. Idealny przystanek dla osób w trasie, które cenią funkcjonalność.",
        "Przytulne B&B dla osób podróżujących w budżetowy sposób. Rano serwowane są świeże i pożywne posiłki dla gości. To miejsce, w którym poczujesz gościnność w niskiej cenie.",
        "Gościnny pensjonat z domową atmosferą i pyszną kawą. Właściciele dbają o to, by każdy gość czuł się tutaj wyjątkowo. Idealne rozwiązanie na krótki pobyt w miłej okolicy.",
        "Kameralny obiekt ceniony za miłą i pomocną obsługę. Pokoje są jasne i wyposażone w najpotrzebniejsze meble. To doskonały wybór dla turystów ceniących spokój i prostotę.",
        "B&B z tradycją, gdzie poczujesz się jak w domu. Właściciele chętnie dzielą się historią regionu i polecają najlepsze trasy. Poranne śniadania bazują na lokalnych, świeżych produktach.",
        "Miejsce słynące z domowych śniadań i serdeczności. Każdy poranek zaczyna się od wspólnego posiłku w przyjemnej jadalni. Lokalizacja sprzyja spacerom i poznawaniu okolicy.",
        "Pensjonat o podwyższonym standardzie z dużą wygodą. Wnętrza są urządzone z dbałością o estetykę i komfortowy sen. To propozycja dla osób szukających czegoś więcej niż standardowy nocleg.",
        "Ekskluzywne B&B łączące domowy klimat z luksusem. Wysokiej jakości pościel oraz wyśmienita kuchnia to nasze znaki rozpoznawcze. Zapewniamy obsługę na najwyższym poziomie.",
        "Wysokiej klasy pensjonat dla najbardziej wymagających. Każdy pokój posiada własną łazienkę oraz nowoczesne wyposażenie. To miejsce, gdzie elegancja spotyka się z domowym ciepłem.",
        "Prestiżowe B&B - połączenie elegancji i domowego ciepła. Wyjątkowa lokalizacja w samym sercu miasta ułatwia zwiedzanie. Śniadania to prawdziwa uczta dla podniebienia."
    ]
}



def get_dynamic_brackets(ceny):
    """Wyznacza 10 punktów granicznych (decyli) dla podanej listy cen."""
    # Tworzy 11 punktów, które dzielą dane na 10 przedziałów
    return np.percentile(ceny, np.linspace(0, 100, 11))

def find_bracket_index(cena, brackets):
    """Zwraca indeks przedziału (0-9) na podstawie wyliczonych granic."""
    for i in range(10):
        if brackets[i] <= cena <= brackets[i+1]:
            return i
    return 9 # Dla najwyższej ceny

def popraw_opisy():
    conn = pyodbc.connect(CONNECTION_STRING)
    cursor = conn.cursor()
    
    # 1. Pobranie danych
    cursor.execute("SELECT id_noclegu, typ_obiektu, cena_za_noc FROM noclegi")
    rows = cursor.fetchall()
    
    # --- ZMIANA TUTAJ: Konwersja na float ---
    # Używamy float(row.cena_za_noc), aby uniknąć problemów z Decimal
    wszystkie_ceny = [float(row.cena_za_noc) for row in rows]
    # ----------------------------------------
    
    # Wyliczamy granice 10 przedziałów
    brackets = get_dynamic_brackets(wszystkie_ceny)
    print(f"Wyznaczone progi cenowe (decyle): {np.round(brackets, 2)}")
    
    # 3. Aktualizacja opisów
    print("Aktualizowanie opisów na podstawie wyliczonych przedziałów...")
    for id_noclegu, typ, cena in rows:
        # Konwertujemy również pojedynczą cenę przy porównywaniu
        idx = find_bracket_index(float(cena), brackets)
        
        # Pobranie opisu ze słownika
        nowy_opis = PRZYPISANIE_OPISOW.get(typ.upper(), ["Opis standardowy"] * 10)[idx]
        
        cursor.execute("UPDATE noclegi SET opis = ? WHERE id_noclegu = ?", (nowy_opis, id_noclegu))
    
    conn.commit()
    conn.close()
    print("Gotowe! Opisy dopasowane dynamicznie do rozkładu cen.")

if __name__ == "__main__":
    popraw_opisy()