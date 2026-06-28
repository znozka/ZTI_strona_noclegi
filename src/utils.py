import requests
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
    msg["From"] = smtp_user
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