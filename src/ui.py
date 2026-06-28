import streamlit as st
from pathlib import Path
import extra_streamlit_components as stx

CSS_FILE = Path(__file__).resolve().parents[1] / "assets" / "css" / "style.css"

def load_app_styles() -> None:
    """Load shared application CSS from assets/css/style.css."""
    if CSS_FILE.exists():
        st.markdown(
            f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True,
        )

# Dodajemy drugi parametr jawny is_auth_page z domyślną wartością False
def render_page_header(label: str = "InnSight", is_konto_page: bool = False, is_auth_page: bool = False) -> None:
    """Render the fixed app header."""
    load_app_styles()

    def clear_search_state() -> None:
        for key in [
            "search_clicked", "search_miejsce", "search_data_od", "search_data_do", "search_osoby", "filters_version", "selected_nocleg_id",
        ]:
            if key in st.session_state:
                del st.session_state[key]

        for param in [
            "miejsce", "data_od", "data_do", "osoby", "clicked", "sort", "cena_min", "cena_max", "f_hotel", "f_apartament", "f_b_and_b", 
            "f_schronisko", "f_wynajem", "f_p_darmowy", "f_p_platny", "f_p_brak", "u_jacuzzi", "u_basen", "u_spa", "u_kuchnia", "id",
        ]:
            if param in st.query_params:
                del st.query_params[param]

    user_name = st.session_state.get("user_name")

    # Dodane dwie węższe kolumny na nowe przyciski na końcu paska
    col_logo, col_spacer, col_login = st.columns([1, 2.5, 0.5])
    # col_logo, col_spacer, col_login, col_db = st.columns([1, 2.5, 0.5, 0.5])
    
    with col_logo:
        st.image("assets/images/logo.svg", width=150) 
        
        # Pusty przycisk z kluczem, który stworzy klasę st-key-logo_btn
        if st.button("", key="logo_btn"):
            clear_search_state()
            st.switch_page("app.py")

    # Przycisk w col_login renderuje się tylko wtedy, gdy NIE jesteśmy na stronie auth
    if not is_auth_page:
        with col_login:
            # Korzystamy z przekazanego parametru is_konto_page
            if is_konto_page and user_name:
                if st.button("⏻  Wyloguj", key="header_logout_btn", width='stretch', type = "primary"):
                    cookie_manager = stx.CookieManager(key="header_cookie_saver")
                    cookie_manager.set("user_id", "", key="header_logout_uid")
                    cookie_manager.set("user_name", "", key="header_logout_name")
                    cookie_manager.set("user_role", "", key="header_logout_role")

                    for key in ["user_id", "user_name", "user_role", "active_section"]:
                        st.session_state.pop(key, None)

                    st.success("Wylogowano pomyślnie!")
                    st.switch_page("app.py")
            else:
                button_label = "Moje konto" if user_name else "Zaloguj się"
                target_page = "pages/konto.py" if user_name else "pages/login.py"
                
                if st.button(button_label, key="header_login_btn", width='stretch', type="primary"):
                    if not user_name:
                        st.session_state["going_to_login"] = True
                    st.switch_page(target_page)

    # with col_db:
    #     if st.button("tabele", key="header_db_btn", width='stretch'):
    #         st.switch_page("pages/db_tables.py")
            
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
