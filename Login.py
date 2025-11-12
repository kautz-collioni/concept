import streamlit as st
import time
import base64

# ========================= 1. PAGE CONFIGURATION AND STYLE LOADING =========================
st.set_page_config(
    page_title = "Área de Acesso | Kautz-Collioni & Cia.",
    layout = "wide",
    initial_sidebar_state = "collapsed",
)

def load_css(file_name):
    try:
        with open(file_name, encoding = 'utf-8') as f:
            st.markdown(f'''<style>{f.read()}</style>''', unsafe_allow_html = True)
    except FileNotFoundError:
        pass

# ======================== 2. SESSION STATE INITIALIZATION ========================

# Controls the user's login state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Controls the current section in the main application
if 'current_section' not in st.session_state:
    st.session_state.current_section = "Introdução"

# ======================== 3. LOGIN PAGE ========================

def login_page():
    # Sidebar page Config
    st.set_page_config(initial_sidebar_state="collapsed")

    load_css("styles/common_style.css")
    load_css("styles/login_style.css")

    # Logo loading
    try:
        with open("media/Cabeçalho Escuro - Streamlit.png", "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()
        
        st.markdown(
            f"""
            <div style='text-align: center; margin-bottom: 1rem;'>
                <img src='data:image/png;base64,{image_base64}' style='width: 70%;
                                                                        min-width: 300px;
                                                                        height: auto; 
                                                                        pointer-events: none; 
                                                                        user-select: none; 
                                                                        -webkit-user-drag: none;
                                                                        'draggable='false'>
            </div>
            """,
            unsafe_allow_html = True
        )
    except FileNotFoundError:
        st.markdown('<div class="login-logo"><h2>Kautz-Collioni & Cia.</h2></div>', unsafe_allow_html = True)

    # Login form
    username = st.text_input("Usuário", key = "user_login", on_change=lambda: None)
    password = st.text_input("Senha", type = "password",  on_change=lambda: None)

    # Login button
    if st.button("Entrar", key = "login_btn", use_container_width = True):
        if username == "João Silva" and password == "123456":  # Credentials
            st.success("Bem-vindo!")
            time.sleep(1)
            st.session_state.logged_in = True
            st.session_state.username = username
            st.switch_page("pages/Application.py")
        else:
            st.error("Usuário ou senha incorretos!")
    
    # Footer
    st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
    st.markdown('---')

    st.markdown(
        """
        <div style="width:100%; text-align:center; font-size:12px; color:#999999;">
        Todos os direitos reservados © 2025 | Kautz-Collioni & Cia.
        </div>
        """,
        unsafe_allow_html = True
    )

# ======================== 4. MAIN CONTROLLER ========================

if not st.session_state.get('logged_in', False):
    login_page()
else:
    st.switch_page("pages/Application.py")