from datetime import datetime
import os

# Folder główny projektu
PROJECT_DIR = r"C:\Users\edyta\Documents\GitHub\ZTI_strona_noclegi"

# Pobranie aktualnej daty w formacie RRRR-MM-DD
current_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

# Nazwa pliku wynikowego z datą na końcu
OUTPUT_FILE = f"kod_projektu_{current_date}.txt"

# Rozszerzenia plików, które chcemy kopiować
ALLOWED_EXTENSIONS = [".py", ".css"]

# Foldery do pominięcia
IGNORE_FOLDERS = ["__pycache__", ".git", ".venv", "env"]

# Pliki do pominięcia
# dynamicznie dodajemy również nasz nowy plik wyjściowy, aby skrypt nie próbował czytać samego siebie
IGNORE_FILES = [
    OUTPUT_FILE,
    "kod_projektu.txt",
    "db_fixer.py",
    "ZapisDoTxt.py",
    "reset_bazy.py",
    "test_api_nocleg.py",
    "BazaDanychBudowa.txt",
]


def should_include_file(filename):
    return any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS)


with open(OUTPUT_FILE, "w", encoding="utf-8") as output:

    for root, dirs, files in os.walk(PROJECT_DIR):

        # Pomijanie folderów
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]

        for file in files:

            if file in IGNORE_FILES:
                continue

            if not should_include_file(file):
                continue

            filepath = os.path.join(root, file)

            # Ścieżka względna względem projektu
            relative_path = os.path.relpath(filepath, PROJECT_DIR)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Nagłówek pliku
                output.write("\n")
                output.write("=" * 80 + "\n")
                output.write(f"PLIK: {relative_path}\n")
                output.write("=" * 80 + "\n\n")

                # Zawartość pliku
                output.write(content)
                output.write("\n\n")

                print(f"Dodano: {relative_path}")

            except Exception as e:
                print(f"Błąd przy pliku {relative_path}: {e}")

print(f"\nGotowe. Kod zapisano do pliku: {OUTPUT_FILE}")