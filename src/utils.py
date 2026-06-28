import requests
import time
import os
from io import BytesIO
from PIL import Image, ImageOps
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
    return None

def send_system_email(to_email, subject, html_content):
    # Funkcja uniwersalna do wysyłania e-maili systemowych z wykorzystaniem danych z secrets.toml
    smtp_server = st.secrets["email"]["smtp_server"]
    smtp_port = st.secrets["email"]["smtp_port"]
    smtp_user = st.secrets["email"]["smtp_user"]
    smtp_password = st.secrets["email"]["smtp_password"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"InnSight <{smtp_user}>"
    msg["To"] = to_email

    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Błąd wysyłania maila ({subject}): {e}")
        return False

def send_reset_email(to_email, user_id):
    # Pobieranie danych z secrets
    smtp_server = st.secrets["email"]["smtp_server"]
    smtp_port = st.secrets["email"]["smtp_port"]
    smtp_user = st.secrets["email"]["smtp_user"]
    smtp_password = st.secrets["email"]["smtp_password"]
    

    reset_url = f"http://localhost:8501/nowe_haslo?user_id={user_id}"
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Odzyskiwanie hasła - InnSight"
    msg["From"] = f"InnSight <{smtp_user}>"
    msg["To"] = to_email
    html = f"""
    <html>
      <body>
        <h2>Cześć!</h2>
        <p>Otrzymaliśmy prośbę o zresetowanie hasła do Twojego konta.</p>
        <p>Kliknij w poniższy link, aby ustawić nowe hasło (link jest aktywny):</p>
        <p><a href="{reset_url}" style="background-color: #0066cc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Resetuj hasło</a></p>
        <br>
        <p>Jeśli to nie Ty wysyłałeś/-aś prośbę, po prostu zignoruj tę wiadomość.</p>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(html, "html"))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Błąd wysyłania maila: {e}")
        return False
    
def send_booking_created_email(to_email, id_rezerwacji, nazwa_obiektu, kwota):
    subject = f"Potwierdzenie rezerwacji #{id_rezerwacji} - Oczekuje na płatność"
    html = f"""
    <html>
        <body style="font-family: sans-serif; color: #333;">
            <h2>Dziękujemy za dokonanie rezerwacji!</h2>
            <p>Twoje zgłoszenie dla obiektu <b>{nazwa_obiektu}</b> zostało pomyślnie zarejestrowane w systemie.</p>
            <hr style="border: 0; border-top: 1px solid #eee;">
            <p><b>Numer rezerwacji:</b> #{id_rezerwacji}</p>
            <p><b>Kwota do zapłaty:</b> {kwota:.2f} PLN</p>
            <p><b>Status:</b> Oczekuje na płatność</p>
            <hr style="border: 0; border-top: 1px solid #eee;">
            <p>Pamiętaj, aby dokończyć płatność w aplikacji!</p>
        </body>
    </html>
    """
    return send_system_email(to_email, subject, html)

def send_payment_email(to_email, id_rezerwacji, kwota, id_transakcji):
    subject = f"Płatność zaakceptowana dla rezerwacji #{id_rezerwacji}"
    html = f"""
    <html>
        <body style="font-family: sans-serif; color: #333;">
            <h2 style="color: #2e7d32;">Płatność zakończona sukcesem!</h2>
            <p>Otrzymaliśmy Twoją płatność za rezerwację numer <b>#{id_rezerwacji}</b>.</p>
            <div style="background-color: #f1f8e9; padding: 15px; border-radius: 8px; border: 1px solid #c5e1a5;">
                <p style="margin: 4px 0;"><b>Kwota:</b> {kwota:.2f} PLN</p>
                <p style="margin: 4px 0;"><b>Metoda płatności:</b> BLIK</p>
                <p style="margin: 4px 0;"><b>Identyfikator transakcji:</b> {id_transakcji}</p>
            </div>
            <p>Twoja rezerwacja zmieniła status na <b>potwierdzona</b>. Życzymy udanego pobytu!</p>
            <br>
            <p>Pozdrawiamy,<br>Zespół InnSight</p>
      </body>
    </html>
    """
    return send_system_email(to_email, subject, html)



def get_ai_credentials():
    hint = None
    if isinstance(st.secrets, dict):
        hint = st.secrets.get("AI_PROVIDER") or st.secrets.get("OPENAI_API_PROVIDER") or st.secrets.get("provider")
        if isinstance(hint, str):
            hint = hint.lower().strip()

    if "openai" in st.secrets and isinstance(st.secrets["openai"], dict):
        api_key = st.secrets["openai"].get("api_key")
        if api_key:
            return {
                "provider": "openai",
                "api_key": api_key,
                "model": st.secrets["openai"].get("model", "gpt-3.5-turbo"),
                "source": "st.secrets[openai]",
            }

    if "OPENROUTER_API_KEY" in st.secrets:
        return {
            "provider": "openrouter",
            "api_key": st.secrets["OPENROUTER_API_KEY"],
            "model": st.secrets.get("OPENROUTER_MODEL", "openai/gpt-oss-120b:free"),
            "source": "st.secrets[OPENROUTER_API_KEY]",
        }

    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
        hf_model = st.secrets.get("HUGGINGFACE_MODEL")
        if isinstance(api_key, str) and api_key.startswith("sk-or-"):
            return {
                "provider": "openrouter",
                "api_key": api_key,
                "model": st.secrets.get("OPENROUTER_MODEL", "openai/gpt-oss-120b:free"),
                "source": "st.secrets[OPENAI_API_KEY]",
            }
        if isinstance(api_key, str) and (api_key.startswith("hf_") or hf_model is not None or hint == "huggingface"):
            return {
                "provider": "huggingface",
                "api_key": api_key,
                "model": st.secrets.get("HUGGINGFACE_MODEL", "google/gemma-4-31b-it:free"),
                "source": "st.secrets[OPENAI_API_KEY]",
            }
        return {
            "provider": "openai",
            "api_key": api_key,
            "model": "gpt-3.5-turbo",
            "source": "st.secrets[OPENAI_API_KEY]",
        }

    if "api_keys" in st.secrets:
        api_hint = st.secrets.api_keys.get("AI_PROVIDER") or st.secrets.api_keys.get("OPENAI_API_PROVIDER") or st.secrets.api_keys.get("provider")
        if isinstance(api_hint, str):
            api_hint = api_hint.lower().strip()
        hf_model = st.secrets.api_keys.get("HUGGINGFACE_MODEL")

        api_key = st.secrets.api_keys.get("OPENROUTER_API_KEY")
        if api_key:
            return {
                "provider": "openrouter",
                "api_key": api_key,
                "model": st.secrets.api_keys.get("OPENROUTER_MODEL", "openai/gpt-oss-120b:free"),
                "source": "st.secrets.api_keys[OPENROUTER_API_KEY]",
            }

        api_key = st.secrets.api_keys.get("OPENAI_API_KEY")
        if api_key:
            if isinstance(api_key, str) and api_key.startswith("sk-or-"):
                return {
                    "provider": "openrouter",
                    "api_key": api_key,
                    "model": st.secrets.api_keys.get("OPENROUTER_MODEL", "openai/gpt-oss-120b:free"),
                    "source": "st.secrets.api_keys[OPENAI_API_KEY]",
                }
            if isinstance(api_key, str) and (api_key.startswith("hf_") or hf_model is not None or api_hint == "huggingface" or hint == "huggingface"):
                return {
                    "provider": "huggingface",
                    "api_key": api_key,
                    "model": st.secrets.api_keys.get("HUGGINGFACE_MODEL", "google/gemma-4-31b-it:free"),
                    "source": "st.secrets.api_keys[OPENAI_API_KEY]",
                }
            return {
                "provider": "openai",
                "api_key": api_key,
                "model": "gpt-3.5-turbo",
                "source": "st.secrets.api_keys[OPENAI_API_KEY]",
            }
        api_key = st.secrets.api_keys.get("OPENAI_API_KEY_OPENAI")
        if api_key:
            if isinstance(api_key, str) and api_key.startswith("sk-or-"):
                return {
                    "provider": "openrouter",
                    "api_key": api_key,
                    "model": st.secrets.api_keys.get("OPENROUTER_MODEL", "openai/gpt-oss-120b:free"),
                    "source": "st.secrets.api_keys[OPENAI_API_KEY_OPENAI]",
                }
            if isinstance(api_key, str) and (api_key.startswith("hf_") or hf_model is not None or api_hint == "huggingface" or hint == "huggingface"):
                return {
                    "provider": "huggingface",
                    "api_key": api_key,
                    "model": st.secrets.api_keys.get("HUGGINGFACE_MODEL", "google/gemma-4-31b-it:free"),
                    "source": "st.secrets.api_keys[OPENAI_API_KEY_OPENAI]",
                }
            return {
                "provider": "openai",
                "api_key": api_key,
                "model": "gpt-3.5-turbo",
                "source": "st.secrets.api_keys[OPENAI_API_KEY_OPENAI]",
            }
        api_key = st.secrets.api_keys.get("api_key")
        if api_key:
            if isinstance(api_key, str) and api_key.startswith("sk-or-"):
                return {
                    "provider": "openrouter",
                    "api_key": api_key,
                    "model": st.secrets.api_keys.get("OPENROUTER_MODEL", "openai/gpt-oss-120b:free"),
                    "source": "st.secrets.api_keys[api_key]",
                }
            if isinstance(api_key, str) and (api_key.startswith("hf_") or hf_model is not None or api_hint == "huggingface" or hint == "huggingface"):
                return {
                    "provider": "huggingface",
                    "api_key": api_key,
                    "model": st.secrets.api_keys.get("HUGGINGFACE_MODEL", "google/gemma-4-31b-it:free"),
                    "source": "st.secrets.api_keys[api_key]",
                }
            return {
                "provider": "openai",
                "api_key": api_key,
                "model": "gpt-3.5-turbo",
                "source": "st.secrets.api_keys[api_key]",
            }

    if "huggingface" in st.secrets and isinstance(st.secrets["huggingface"], dict):
        api_key = st.secrets["huggingface"].get("api_key")
        if api_key:
            return {
                "provider": "huggingface",
                "api_key": api_key,
                "model": st.secrets["huggingface"].get("model", "google/gemma-4-31b-it:free"),
                "source": "st.secrets[huggingface]",
            }

    if "HUGGINGFACE_API_KEY" in st.secrets:
        return {
            "provider": "huggingface",
            "api_key": st.secrets["HUGGINGFACE_API_KEY"],
            "model": st.secrets.get("HUGGINGFACE_MODEL", "google/gemma-4-31b-it:free"),
            "source": "st.secrets[HUGGINGFACE_API_KEY]",
        }

    if "api_key" in st.secrets and isinstance(st.secrets["api_key"], str) and st.secrets["api_key"].startswith("hf_"):
        return {
            "provider": "huggingface",
            "api_key": st.secrets["api_key"],
            "model": st.secrets.get("HUGGINGFACE_MODEL", "google/gemma-4-31b-it:free"),
            "source": "st.secrets[api_key]",
        }

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        if api_key.startswith("hf_"):
            return {
                "provider": "huggingface",
                "api_key": api_key,
                "model": os.environ.get("HUGGINGFACE_MODEL", "google/gemma-4-31b-it:free"),
                "source": "env[OPENAI_API_KEY]",
            }
        return {
            "provider": "openai",
            "api_key": api_key,
            "model": "gpt-3.5-turbo",
            "source": "env[OPENAI_API_KEY]",
        }
    api_key = os.environ.get("OPENAI_API_KEY_OPENAI")
    if api_key:
        if api_key.startswith("hf_"):
            return {
                "provider": "huggingface",
                "api_key": api_key,
                "model": os.environ.get("HUGGINGFACE_MODEL", "google/gemma-4-31b-it:free"),
                "source": "env[OPENAI_API_KEY_OPENAI]",
            }
        return {
            "provider": "openai",
            "api_key": api_key,
            "model": "gpt-3.5-turbo",
            "source": "env[OPENAI_API_KEY_OPENAI]",
        }
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    if api_key:
        return {
            "provider": "huggingface",
            "api_key": api_key,
            "model": os.environ.get("HUGGINGFACE_MODEL", "google/gemma-4-31b-it:free"),
            "source": "env[HUGGINGFACE_API_KEY]",
        }
    return None


def generuj_plan_wycieczki_ai(destination, origin, start_date, end_date, trip_type):
    credentials = get_ai_credentials()
    if not credentials:
        st.session_state["openai_api_source"] = None
        st.session_state["openai_error"] = None
        return None

    provider = credentials["provider"]
    api_key = credentials["api_key"]
    model = credentials.get("model")
    st.session_state["openai_api_source"] = credentials["source"]
    st.session_state["openai_error"] = None

    system_prompt = (
        "Jesteś asystentem podróży. Przygotuj plan wycieczki dla użytkownika, włączając atrakcje, dojazd, czas trwania i praktyczne informacje. "
        "Użyj zwięzłego, przyjaznego stylu."
    )

    user_prompt = (
        f"Przygotuj plan wycieczki do {destination} z miejsca {origin}. "
        f"Termin: {start_date} - {end_date}. "
        f"Rodzaj wycieczki: {trip_type}. "
        "Podaj listę atrakcji, orientacyjny czas trwania, sposób dojazdu i krótkie wskazówki dotyczące każdego dnia. "
        "Nie używaj kodu ani formatowania JSON, tylko zwykły tekst."
    )

    if provider == "openai":
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.8
        }

        attempt = 0
        max_attempts = 5
        base_wait = 5  # 5 sekund na początek, będzie rosnąć exponentially
        
        while attempt < max_attempts:
            try:
                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=20)
                
                if response.status_code == 429:
                    attempt += 1
                    if attempt < max_attempts:
                        wait = base_wait * (2 ** (attempt - 1))
                        st.session_state["openai_error"] = f"Rate limit osiągnięty. Próba {attempt}/{max_attempts} - czekam {wait}s..."
                        time.sleep(wait)
                        continue
                    else:
                        st.session_state["openai_error"] = "429 Too Many Requests - spróbuj ponownie za chwilę lub zmniejsz liczbę żądań."
                        return None
                
                response.raise_for_status()
                result = response.json()
                st.session_state["openai_error"] = None
                return result["choices"][0]["message"]["content"].strip()
                
            except requests.exceptions.HTTPError as e:
                st.session_state["openai_error"] = str(e)
                if hasattr(response, 'status_code') and response.status_code == 429:
                    attempt += 1
                    if attempt < max_attempts:
                        wait = base_wait * (2 ** (attempt - 1))
                        time.sleep(wait)
                        continue
                    else:
                        st.session_state["openai_error"] = "429 Too Many Requests - spróbuj ponownie za chwilę."
                        return None
                print(f"OpenAI request failed: {e}")
                return None
            except Exception as e:
                st.session_state["openai_error"] = str(e)
                print(f"OpenAI request failed: {e}")
                return None
        
        st.session_state["openai_error"] = "429 Too Many Requests - spróbuj ponownie za chwilę."
        return None

    if provider == "huggingface":
        model_name = model
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": f"{system_prompt}\n{user_prompt}",
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.8,
                "return_full_text": False
            }
        }

        try:
            response = requests.post(f"https://api-inference.huggingface.co/models/{model_name}", headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            if isinstance(result, dict) and result.get("error"):
                st.session_state["openai_error"] = result.get("error")
                return None
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            if isinstance(result, dict) and "generated_text" in result:
                return result.get("generated_text", "").strip()
            return None
        except Exception as e:
            st.session_state["openai_error"] = str(e)
            print(f"Hugging Face request failed: {e}")
            return None

    if provider == "openrouter":
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.8
        }

        attempt = 0
        max_attempts = 5
        base_wait = 5
        
        while attempt < max_attempts:
            try:
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
                
                if response.status_code == 429:
                    attempt += 1
                    if attempt < max_attempts:
                        wait = base_wait * (2 ** (attempt - 1))
                        st.session_state["openai_error"] = f"Rate limit osiągnięty. Próba {attempt}/{max_attempts} - czekam {wait}s..."
                        time.sleep(wait)
                        continue
                    else:
                        st.session_state["openai_error"] = "429 Too Many Requests - spróbuj ponownie za chwilę lub zmniejsz liczbę żądań."
                        return None
                
                response.raise_for_status()
                result = response.json()
                st.session_state["openai_error"] = None
                return result["choices"][0]["message"]["content"].strip()
                
            except requests.exceptions.HTTPError as e:
                st.session_state["openai_error"] = str(e)
                if hasattr(response, 'status_code') and response.status_code == 429:
                    attempt += 1
                    if attempt < max_attempts:
                        wait = base_wait * (2 ** (attempt - 1))
                        time.sleep(wait)
                        continue
                    else:
                        st.session_state["openai_error"] = "429 Too Many Requests - spróbuj ponownie za chwilę."
                        return None
                print(f"OpenRouter request failed: {e}")
                return None
            except Exception as e:
                st.session_state["openai_error"] = str(e)
                print(f"OpenRouter request failed: {e}")
                return None
        
        st.session_state["openai_error"] = "429 Too Many Requests - spróbuj ponownie za chwilę."
        return None

    return None