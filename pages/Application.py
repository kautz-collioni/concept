import streamlit as st
import base64
import Conector as con

# ========================= 1. PAGE CONFIGURATION AND STYLE LOADING =========================
st.set_page_config(
    page_title = "Relatório Integrado | Kautz-Collioni & Cia.",
    layout = "wide",
    initial_sidebar_state = "expanded",
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
    st.switch_page("Login.py")

# Controls the current section in the main application
if 'current_section' not in st.session_state:
    st.session_state.current_section = "Introdução"

# ======================== 3. LOGOUT FUNCTION ========================

def back_to_login():
    keys_to_preserve = ['logged_in', 'current_section']  # Não preserve nenhum estado ao sair
    keys_to_delete = [key for key in st.session_state.keys() if key not in keys_to_preserve]
    for key in keys_to_delete:
        del st.session_state[key]
    st.session_state.logged_in = False
    st.switch_page("Login.py")

# ======================== 4. MAIN APPLICATION ========================

def main_app():
    # Sidebar page Config
    st.set_page_config(initial_sidebar_state="expanded")
    # Load main application CSS
    load_css("styles/common_style.css")
    load_css("styles/sidebar_style.css")

    # Main application title
    st.markdown("""
        <style>
        .app-title {
            text-align: center;
            font-size: 46px;
            font-weight: 700;
            color: #30333e;
            margin-bottom: 1rem;
        }
        </style>
        <div class="app-title">Porsche Brasil</div>
    """, unsafe_allow_html = True)
    st.markdown("---")

    with st.sidebar:
        # Loading the sidebar header logo
        try:
            with open("media/Cabecalho.svg", "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode()
            st.markdown(
                f"""
                <div class="logo-container" style='text-align: center; margin-bottom: -15rem; z-index: 1; margin-top: -1rem;'>
                    <img src='data:image/svg+xml;base64,{image_base64}' style='width: 100%; height: 60%; pointer-events: none; user-select: none; -webkit-user-drag: none;' draggable='false; margin-bottom: -15rem; top: -4rem; position: relative; padding-bottom: 0rem; z-index: 1;'>
                </div>
                """,
                unsafe_allow_html = True
            )
        except Exception as e:
            st.error(f"Erro ao carregar a imagem: {e}")
            st.markdown("<h4>Kautz-Collioni & Cia.</h4>", unsafe_allow_html=True)

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
        st.header("Amostra dos Dados")
        st.markdown("Qual é a fundamentação do estudo?")
        st.dataframe(database.sample(25))

    # Section: Análise Exploratória
    elif st.session_state.current_section == "Análise Exploratória":
        st.header("Análise Exploratória")
        st.subheader("Relação entre Quantidade Vendida e Preço por Item de Café (Demandas inversas)")
        st.plotly_chart(con.figure1, use_container_width=True)
        st.subheader("Distribuições de Preços")
        st.plotly_chart(con.figure2, use_container_width=True)
        st.subheader("Análise Exploratória — Receitas Acumuladas")
        st.plotly_chart(con.figure4, use_container_width=True)
        st.subheader("Análise Exploratória — Receitas Diárias")
        st.plotly_chart(con.figure5, use_container_width=True)
        st.subheader("Análise Exploratória — Receita por Dia da Semana")
        st.plotly_chart(con.figure6, use_container_width=True)
        st.subheader("Análise Exploratória — Participação na Receita (Semanal)")
        st.plotly_chart(con.figure7, use_container_width=True)

    # Section: Elasticidades
    elif st.session_state.current_section == "Elasticidades":
        st.header("Elasticidades")
        st.subheader("Elasticidades-preço da Demanda Atuais")
        st.plotly_chart(con.figure3, use_container_width=True)
        st.subheader("Elasticidades-preço nos Pontos Ótimos")
        st.plotly_chart(con.figure9, use_container_width=True)

    # Section: Forecasting
    elif st.session_state.current_section == "Forecasting":
        st.header("Forecasting e Relacionados")
        st.subheader("Otimização de Preços Usando Modelos Aditivos Generalizados (GAM)")
        st.plotly_chart(con.figure8, use_container_width=True)

    # Section: Gerencial
    elif st.session_state.current_section == "Gerencial":
        st.subheader("Fluxo de caixa")
        st.text("Esse é o fluxo dos últimos x períodos.")
        st.plotly_chart(con.figure11, use_container_width=True)
        st.markdown("---")
        st.subheader("Liquidez")
        st.text("Aqui mostra a capacidade de liquidar as suas dívidas(passivos).")
        st.plotly_chart(con.figure12, use_container_width=True)
        st.markdown("---")
        st.subheader("Fluxo de Caixa Projetado")
        st.text("Projeção do resultado da empresa pelos próximos x períodos")
        st.table(con.projected_cash_flow)
        st.markdown("---")
        st.subheader("Controle Gerencial de Estoques por Produto")
        st.plotly_chart(con.figure13, use_container_width=True)

    # Section: Decomposição
    elif st.session_state.current_section == "Decomposição":
        st.header("Decomposição de Séries")
        st.subheader("Decomposição: Tendência, Sazonalidade e Resíduo")
        st.plotly_chart(con.figure10, use_container_width=True)

    # Section: Entregáveis
    elif st.session_state.current_section == "Entregáveis":
        st.header("Entregáveis")
        st.dataframe(con.comparison_table)

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
                        font-size: 1rem;
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
            st.image("media/avatar1.jpeg", use_container_width=True)          
            st.markdown("Sócio / Diretor &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Economista")
            
            icon_col1, icon_col2, icon_col3 = st.columns(3)
            
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

        with col2:
            st.markdown("#### Gustavo Collioni")
            st.image("media/avatar2.jpg", use_container_width=True)
            st.markdown("Sócio / Diretor &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Economista")

            icon_col4, icon_col5, icon_col6 = st.columns(3)

            with icon_col4:
                st.markdown("""
                            <a class="social-icon" href="https://wa.me/5551982765730" target="_blank">
                                <i class="fa-brands fa-whatsapp"></i>
                            <span class="social-text"> WhatsApp </span></a>""", unsafe_allow_html=True)
                
            with icon_col5:
                st.markdown(f"""
                            <a class="social-icon" href="mailto:gustavo@kautz-collioni.com.br">
                                <i class="fa-solid fa-at"></i>
                            <span class="social-text"> Email </span> </a>""", unsafe_allow_html=True)
                
            with icon_col6:
                st.markdown("""
                            <a class="social-icon" href="https://www.linkedin.com/in/gustavo-collioni" target="_blank">
                                <i class="fa-brands fa-linkedin"></i>
                            <span class="social-text"> LinkedIn </span> </a>""", unsafe_allow_html=True)

    st.markdown("---")
   
    # Footer
    st.markdown(
        """
        <div style="width:100%; text-align:center; font-size:12px; color:#999999; margin-top:1rem; padding:1rem 0;">
        Elaboração realizada por Kautz-Collioni & Cia. Replicação desautorizada sem pedido prévio. | 
        E-mail: suporte@kautz.collioni_cia.com.br. |
        Telefone: (51) 9 8276-5730.
        </div>
        """,
        unsafe_allow_html=True
    )

# ======================== 5. MAIN CONTROLLER ========================

if st.session_state.get('logged_in', False):
    main_app()
else:

    st.switch_page("Login.py")
