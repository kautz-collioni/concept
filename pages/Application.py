import streamlit as st
import base64
import streamlit.components.v1 as components
from streamlit.components.v1 import html
import time
import Conector as con

# ========================= 1. PAGE CONFIGURATION AND STYLE LOADING =========================
st.set_page_config(
    page_title = "Relatório Integrado | Kautz-Collioni & Cia.",
    layout = "wide",
    initial_sidebar_state = "expanded",
)

hide_st_style = '''
<style>
    div[class^="_hostedName"] {
        visibility: hidden;
    }
</style>
'''
st.markdown(hide_st_style, unsafe_allow_html=True)

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
    st.switch_page("Login.py")

# Controls the current section in the main application
if 'current_section' not in st.session_state:
    st.session_state.current_section = "Introdução"

# ======================== 3. LOGOUT FUNCTION ========================

def back_to_login():
    keys_to_preserve = ['logged_in', 'current_section']
    keys_to_delete = [key for key in st.session_state.keys() if key not in keys_to_preserve]
    for key in keys_to_delete:
        del st.session_state[key]
    st.session_state.logged_in = False
    st.switch_page("Login.py")

# ======================== 3. HOMEPAGE FUNCTION ========================

def go_to_homepage():
    st.session_state.current_section = "Introdução"

# ======================== 4. MAIN APPLICATION ========================

def main_app():
    # Load main application CSS
    load_css("styles/common_style.css")
    load_css("styles/sidebar_style.css")


    print_button = """
    <style>
    button.print-button {
        padding: 10px 15px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        background-color: transparent;
        color: #212529;
        border: none;
        border-radius: 0.25rem;
        font-family: Source Sans Pro, sans-serif;
        text-decoration: none;
        transition: background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        outline: none;
    }

    button.print-button:hover {
        background-color: #e9ecef;
        border-color: #ced4da;
    }

    button.print-button:active {
        background-color: #a6a5a5;
        border-color: #ced4da; /* Ajusta a cor da borda */
        color: #212529;
        box-shadow: inset 0 3px 5px rgba(0, 0, 0, 0.125);
    }

    @media print {
        .print-button {
            display: none !important;
        }

        .graph-container {
            page-break-inside: avoid;
            break-inside: avoid-page;
        }
    }
    </style>

    <script>
        function printReport() {
            const expandedSidebar = window.parent.document.querySelector('section[data-testid="stSidebar"][aria-expanded="true"]');

            const sidebarToggle = window.parent.document.querySelector('div[data-testid="stSidebarCollapseButton"] > button');

            if (expandedSidebar && sidebarToggle) {
                sidebarToggle.closest('button').click();
            }
            
            setTimeout(() => {
                top.window.print();
            }, 500);
        }
    </script>

    <button 
        onclick="printReport();" 
        class="print-button"
    >
        Imprimir
    </button>
    """
    components.html(print_button, height=80)

    # Main application title
    st.markdown("""<div class="app-title">Porsche Brasil</div>""", unsafe_allow_html = True)

    st.markdown("---")

    with st.sidebar:
        # Loading the sidebar header logo
        try:
            with open("media/Cabecalho.svg", "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode()
            st.markdown(
                f"""
                <div class="logo-container" style='text-align: center; margin-bottom: -15rem; z-index: 1; margin-top: -4rem; cursor : pointer;'>
                        <img src='data:image/svg+xml;base64,{image_base64}' style='width: 100%; height: 60%; pointer-events: none; user-select: none; -webkit-user-drag: none;' draggable='false; margin-bottom: -15rem; top: -4rem; position: relative; padding-bottom: 0rem; z-index: 1;'>
                </div>

                """,
                unsafe_allow_html = True
            )
            st.markdown("""
                <style>
                    .invisible-btn {
                        width: 100%; 
                        height: 60%; 
                        pointer-events: none; 
                        user-select: none; 
                        -webkit-user-drag: none;
                        position: relative; 
                        z-index: 1; 
                        margin-bottom: -15rem; 
                        margin-top: -4rem;
                        padding-bottom: 0rem;
                    }
                </style>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Erro ao carregar a imagem: {e}")
            st.markdown("<h4>Kautz-Collioni & Cia.</h4>", unsafe_allow_html=True)
        
        st.button("Botão Invisível", key="invisible_btn", on_click=go_to_homepage, use_container_width=True)

        # User greeting
        st.markdown(f'<div class="user-greeting">Olá, {st.session_state.username}!</div>', unsafe_allow_html=True)
        
        # Navigation menu - Sidebar buttons
        sidebar_options = ["Introdução", "Análise Exploratória", "Elasticidades", "Forecasting", "Gerencial", "Decomposição", "Entregáveis", "Contato"]
        
        try:
            current_index = sidebar_options.index(st.session_state.current_section)
        except ValueError:
            current_index = 0

        section = st.radio(
            "Navegação", 
            sidebar_options, 
            index=current_index,
            key="nav_radio", 
            label_visibility="collapsed"
        )

        if section != st.session_state.current_section:
            st.session_state.current_section = section
            st.rerun()
       
        # Exit button - Logout
        st.button("Sair", key="logout_btn", on_click=back_to_login, use_container_width=True)

        # Sidebar footer
        st.markdown(
            '<div class="sidebar-footer">Todos os direitos reservados © 2025 | Kautz-Collioni & Cia.</div>',
            unsafe_allow_html=True
        )

    database = con.database_revenue

    # ======================== APP SECTIONS ========================

    # Section: Introdução
    if st.session_state.current_section == "Introdução":
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.markdown("Qual é a fundamentação do estudo?")
        st.dataframe(database.sample(25).style.format({
                                                "date": "{:%d/%m/%Y}",
                                                "price": "{:,.2f}"}, thousands=".", decimal=","),
                                                hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Section: Análise Exploratória
    elif st.session_state.current_section == "Análise Exploratória":
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.subheader("Relação entre Quantidade Vendida e Preço por Item de Café (Demandas inversas)")
        st.plotly_chart(con.figure1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.subheader("Distribuições de Preços")
        st.plotly_chart(con.figure2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.subheader("Análise Exploratória — Receitas Acumuladas")
        st.plotly_chart(con.figure4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.subheader("Análise Exploratória — Receitas Diárias")
        st.plotly_chart(con.figure5, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.subheader("Análise Exploratória — Receita por Dia da Semana")
        st.plotly_chart(con.figure6, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.subheader("Análise Exploratória — Participação na Receita (Semanal)")
        st.plotly_chart(con.figure7, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Section: Elasticidades
    elif st.session_state.current_section == "Elasticidades":
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.subheader("Elasticidades-preço da Demanda Atuais")
        st.plotly_chart(con.figure3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.subheader("Elasticidades-preço nos Pontos Ótimos")
        st.plotly_chart(con.figure9, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Section: Forecasting
    elif st.session_state.current_section == "Forecasting":
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.subheader("Otimização de Preços Usando Modelos Aditivos Generalizados (GAM)")
        st.plotly_chart(con.figure8, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Section: Gerencial
    elif st.session_state.current_section == "Gerencial":
        st.subheader("Fluxo de caixa")
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.text("Esse é o fluxo dos últimos x períodos.")
        st.plotly_chart(con.figure11, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("Liquidez")
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.text("Aqui mostra a capacidade de liquidar as suas dívidas(passivos).")
        st.plotly_chart(con.figure12, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.subheader("Fluxo de Caixa Projetado")
        st.text("Projeção do resultado da empresa pelos próximos x períodos")
        st.table(con.projected_cash_flow)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.subheader("Controle Gerencial de Estoques por Produto")
        st.plotly_chart(con.figure13, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Section: Decomposição
    elif st.session_state.current_section == "Decomposição":
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.subheader("Decomposição: Tendência, Sazonalidade e Resíduo")
        st.plotly_chart(con.figure10, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Section: Entregáveis
    elif st.session_state.current_section == "Entregáveis":
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.dataframe(con.comparison_table, hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([8,1])
        with col2:
            st.download_button(
                label="Baixar",
                data=con.buffer_excel_formatted(con.comparison_table),
                file_name="Projeções.xlsx",
                mime="text/csv",
                )

    # Section: Contato
    elif st.session_state.current_section == "Contato":
        st.header("Nossa Equipe")
        st.markdown("""
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
                <style> 
                    [data-testid="stImage"] img {
                        width: 50% !important;
                        height: auto;
                        display: block;
                        border-radius: 50%;
                        object-fit: cover;
                        aspect-ratio: 1 / 1;}
                    a {
                        color: inherit !important; 
                        text-decoration: none !important;
                    }

                    a:hover {
                        color: inherit !important;
                        text-decoration: none !important; 
                    }

                    .social-icon {
                        font-size: 1.5rem;
                        color: inherit;
                        text-decoration: none;
                        transition: color 0.3s ease;
                        margin-right: 0.5rem;
                    }

                    .social-text {
                        font-size: 0.8rem;
                        margin-left: 0.5rem;
                    }

                    .social-icon:hover {
                        color: #0077b5;
                    }
                </style>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Bernardo Kautz")
            st.image("media/BernardoKautz.jpg", use_container_width=True)          
            st.markdown("Sócio-diretor &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Economista")
            st.text("Financista, mestrando em Economia Aplicada na Universidade de São Paulo (USP), com experiência profissional em captação de recursos à inovação e pesquisa acadêmica.")
            icon_col1, icon_col2, icon_col3, icon_col4 = st.columns(4)
            
            with icon_col1:
                st.markdown("""
                            <a class="social-icon" href="https://wa.me/555496781573" target="_blank">
                                <i class="fa-brands fa-whatsapp"></i>
                            <span class="social-text"> WhatsApp </span></a>""", unsafe_allow_html=True)
                
            with icon_col2:
                st.markdown(f"""
                            <a class="social-icon" href="mailto:bernardo@kautz-collioni.com.br">
                                <i class="fa-solid fa-at"></i>
                            <span class="social-text"> Email </span> </a>""", unsafe_allow_html=True)
                
            with icon_col3:
                st.markdown("""
                            <a class="social-icon" href="https://www.linkedin.com/in/bernardo-kautz" target="_blank">
                                <i class="fa-brands fa-linkedin"></i>
                            <span class="social-text"> LinkedIn </span> </a>""", unsafe_allow_html=True)
            with icon_col4:
                st.markdown(" ")

        with col2:
            st.markdown("#### Gustavo A. Collioni")
            st.image("media/GustavoCollioni.jpg", use_container_width=True)
            st.markdown("Sócio-diretor &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Economista")
            st.text("Financista, mestrando em Desenvolvimento Regional na Pontifícia Universidade Católica do Rio Grande do Sul (PUCRS), certificado como especialista em investimentos, com experiência profissional em gestão de patrimônio.")

            icon_col5, icon_col6, icon_col7, icon_col8 = st.columns(4)

            with icon_col5:
                st.markdown("""
                            <a class="social-icon" href="https://wa.me/5551982765730" target="_blank">
                                <i class="fa-brands fa-whatsapp"></i>
                            <span class="social-text"> WhatsApp </span></a>""", unsafe_allow_html=True)
                
            with icon_col6:
                st.markdown(f"""
                            <a class="social-icon" href="mailto:gustavo@kautz-collioni.com.br">
                                <i class="fa-solid fa-at"></i>
                            <span class="social-text"> Email </span> </a>""", unsafe_allow_html=True)
                
            with icon_col7:
                st.markdown("""
                            <a class="social-icon" href="https://www.linkedin.com/in/gustavo-collioni" target="_blank">
                                <i class="fa-brands fa-linkedin"></i>
                            <span class="social-text"> LinkedIn </span> </a>""", unsafe_allow_html=True)
            with icon_col8:
                st.markdown(" ")

    st.markdown("---")
   
    # Footer
    st.markdown(
        """
        <div style="width:100%; text-align:center; font-size:12px; color:#999999; margin-top:1rem; padding:1rem 0;">
        E-mail: suporte@kautz.collioni_cia.com.br. | Telefone: (54) 9 9678-1573.
        </div>
        """,
        unsafe_allow_html=True
    )

# ======================== 5. MAIN CONTROLLER ========================

if st.session_state.get('logged_in', False):
    main_app()
else:
    st.switch_page("Login.py")
