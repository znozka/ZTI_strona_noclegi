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