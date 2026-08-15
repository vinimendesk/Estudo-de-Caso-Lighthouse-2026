import streamlit as st


# configuração da aplicação
st.set_page_config(
    page_title="LH Nautical | Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# páginas disponíveis
pages = {
    "Dashboard": [
        st.Page(
            "pages/Visao_Geral.py",
            title="Visão Geral",
            default=True,
        ),
        st.Page(
            "pages/2_Clientes.py",
            title="Clientes",
        ),
        st.Page(
            "pages/3_Produtos.py",
            title="Produtos",
        ),
        st.Page(
            "pages/4_Demanda.py",
            title="Demanda",
        ),
    ]
}


# navegação
pg = st.navigation(
    pages,
    position="top",
)


# execução da página selecionada
pg.run()