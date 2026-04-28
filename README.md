# ZTI_strona_noclegi
Web app created as an university project for subject "Zaawansowane techniki internetowe".

Jak odpalić środowisko:
```{bash}
conda env create -f environment.yml
conda activate ZTI
```

Aktualizacja środowiska po dodaniu nowej biblioteki:
```{bash}
conda env update -f environment.yml --prune
```

## Struktura projektu

- **`app.py`** - strona główna
- **`.streamlit/`** - konfiguracja lokalna
  - `secrets.toml` - dane logowania do bazy (gitignore)
  - `config.toml` - ustawienia motywu
- **`pages/`** - folder na podstrony
- **`src/`**
  - `database.py` - funkcje do komunikacji z Azure
- **`assets/`** - pliki statyczne
  - `css/style.css` - niestandardowe css
  - `images/` - folder na zdjęcia (może tymczasowo)
- **`environment.yml`** - plik do tworzenia środowiska
