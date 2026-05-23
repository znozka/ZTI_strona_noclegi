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

    user_name = st.session_state.get("user_name")
    button_label = "Moje konto" if user_name else "Zaloguj się"
    target_page = "pages/konto.py" if user_name else "pages/login.py"

    col_logo, col_spacer, col_btn = st.columns([1, 4, 1])

    with col_logo:
        st.markdown(f'<a href="/" class="page-nav-link" target="_self">{label}</a>', unsafe_allow_html=True)

    with col_btn:
        if st.button(button_label, key="header_nav_btn", use_container_width=True):
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