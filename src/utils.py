import requests
from io import BytesIO
from PIL import Image, ImageOps
import streamlit as st

@st.cache_data(ttl=600)
def wyswietl_zdjecie(url, szerokosc=400, wysokosc=250):
    """
    Pobiera zdjęcie w tle i przycina je centralnie (jak object-fit: cover)
    do podanych wymiarów, eliminując błędy układu (pionowe zdjęcia).
    """
    if not url:
        return None
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            
            # Konwersja do RGB (na wypadek gdyby zdjęcie miało format RGBA/PNG z przezroczystością)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
                
            # Magiczna funkcja - przycina obrazek centralnie do idealnych proporcji
            img_przyciete = ImageOps.fit(img, (szerokosc, wysokosc), centering=(0.5, 0.5))
            return img_przyciete
    except Exception:
        pass
    return None  # Zwraca None, jeśli zdjęcie jest uszkodzone lub nie istnieje
