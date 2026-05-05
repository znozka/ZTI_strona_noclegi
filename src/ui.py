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
    button_href = "/?page=konto" if user_name else "/?page=login"

    st.markdown(
        f"""
        <div class="page-header">
            <a href="/" class="page-nav-link" target="_self">{label}</a>
            <a href="{button_href}" class="page-action-button" target="_self">{button_label}</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
