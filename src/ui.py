import streamlit as st
from pathlib import Path


CSS_FILE = Path(__file__).resolve().parents[1] / "assets" / "css" / "style.css"


def load_app_styles() -> None:
    """Load shared application CSS from assets/css/style.css."""
    if CSS_FILE.exists():
        st.markdown(
            f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )

def render_page_header(label: str = "InnSight") -> None:
    """Render the fixed app header."""
    load_app_styles()

    def clear_search_state() -> None:
        for key in [
            "search_clicked",
            "search_miejsce",
            "search_data_od",
            "search_data_do",
            "search_osoby",
            "filters_version",
            "selected_nocleg_id",
        ]:
            if key in st.session_state:
                del st.session_state[key]

        for param in [
            "miejsce",
            "data_od",
            "data_do",
            "osoby",
            "clicked",
            "sort",
            "cena_min",
            "cena_max",
            "f_hotel",
            "f_apartament",
            "f_b_and_b",
            "f_schronisko",
            "f_wynajem",
            "f_p_darmowy",
            "f_p_platny",
            "f_p_brak",
            "u_jacuzzi",
            "u_basen",
            "u_spa",
            "u_kuchnia",
            "id",
        ]:
            if param in st.query_params:
                del st.query_params[param]

    user_name = st.session_state.get("user_name")
    button_label = "Moje konto" if user_name else "Zaloguj się"
    target_page = "pages/konto.py" if user_name else "pages/login.py"

    col_logo, col_spacer, col_btn = st.columns([1, 4, 1])
    
    with col_logo:
        # Samo logo
        st.image("assets/images/logo.svg", width=150) 
        
        # Pusty przycisk z kluczem, który stworzy klasę st-key-logo_btn
        if st.button("", key="logo_btn"):
            clear_search_state()
            st.switch_page("app.py")

    # --- TUTAJ WRACA PRZYCISK LOGOWANIA ---
    with col_btn:
        if st.button(button_label, key="header_login_btn", use_container_width=True):
            st.switch_page(target_page)
            
def render_page_footer() -> None:
    """Render the fixed app footer component."""
    load_app_styles() 
    
    st.markdown(
        """
        <div class="custom-footer">
            <a href="#">Regulamin</a>
            <a href="#">Pomoc</a>
            <a href="#">Kontakt z biurem obsługi klienta</a>
            <a href="#">Informacje o platformie</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
