from typing import Tuple


def build_map_query(search_city: str, selected_id: int | None = None) -> Tuple[str, dict]:
    """Buduje zapytanie do mapy dla strony szczegółów noclegu.

    Gdy nie podano miasta, zwraca wszystkie noclegi z koordynatami, aby na mapie
    widoczne były także pozostałe obiekty jako szare markery.
    """
    city = (search_city or "").strip()

    if city:
        return (
            """
            SELECT id_noclegu, nazwa, lokalizacja_miasto, lokalizacja_adres, szerokosc_geo, dlugosc_geo
            FROM noclegi
            WHERE lokalizacja_miasto LIKE :miasto
              AND szerokosc_geo IS NOT NULL
              AND dlugosc_geo IS NOT NULL
            """,
            {"miasto": f"%{city}%"},
        )

    return (
        """
        SELECT id_noclegu, nazwa, lokalizacja_miasto, lokalizacja_adres, szerokosc_geo, dlugosc_geo
        FROM noclegi
        WHERE szerokosc_geo IS NOT NULL
          AND dlugosc_geo IS NOT NULL
        """,
        {},
    )
