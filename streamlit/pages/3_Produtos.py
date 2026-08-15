import sys
from pathlib import Path

import streamlit as st
import pandas as pd


# caminho da aplicação
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from database import query


# título
st.title("Análise de Produtos")

st.caption(
    "Desempenho de vendas, rentabilidade e identificação de produtos com prejuízo"
)


# período disponível
periodo = query("""
    SELECT
        MIN(placed_at)::DATE AS data_min,
        MAX(placed_at)::DATE AS data_max
    FROM orders
    WHERE status IN ('paid', 'confirmed')
""")


data_min = periodo.loc[0, "data_min"]
data_max = periodo.loc[0, "data_max"]


# filtro de período
intervalo = st.date_input(
    "Período",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max,
)


if len(intervalo) != 2:
    st.warning("Selecione uma data inicial e uma data final.")
    st.stop()


data_inicio = intervalo[0]
data_fim = intervalo[1]


# filtro de categoria
categorias = query("""
    SELECT
        id,
        name
    FROM categories
    ORDER BY name
""")


categoria_selecionada = st.selectbox(
    "Categoria",
    ["Todas"] + categorias["name"].tolist()
)


# filtro de categoria
filtro_categoria = ""

if categoria_selecionada != "Todas":
    filtro_categoria = f"""
        AND c.name = '{categoria_selecionada.replace("'", "''")}'
    """


# base de produtos
produtos = query(f"""
    SELECT
        p.id AS product_id,
        p.name AS produto,
        c.name AS categoria,

        SUM(oi.quantity) AS quantidade,

        SUM(oi.line_total) AS faturamento,

        SUM(
            oi.quantity * pv.cost_price
        ) AS custo,

        SUM(
            oi.line_total -
            (oi.quantity * pv.cost_price)
        ) AS lucro

    FROM orders o

    INNER JOIN order_items oi
        ON oi.order_id = o.id

    INNER JOIN product_variants pv
        ON pv.id = oi.product_variant_id

    INNER JOIN products p
        ON p.id = pv.product_id

    INNER JOIN categories c
        ON c.id = p.category_id

    WHERE o.status IN ('paid', 'confirmed')

      AND o.placed_at::DATE
          BETWEEN '{data_inicio}' AND '{data_fim}'

      {filtro_categoria}

    GROUP BY
        p.id,
        p.name,
        c.name
""")


# margem dos produtos
produtos["margem"] = (
    produtos["lucro"]
    / produtos["faturamento"]
).fillna(0)


# métricas gerais
faturamento = produtos["faturamento"].sum()

lucro = produtos["lucro"].sum()

quantidade = produtos["quantidade"].sum()

produtos_vendidos = len(produtos)

produtos_prejuizo = (
    produtos["lucro"] < 0
).sum()


# margem geral
margem = (
    lucro / faturamento
    if faturamento > 0
    else 0
)





st.metric(
    "Produtos vendidos",
    f"{produtos_vendidos:,.0f}".replace(",", ".")
)

st.divider()


# produtos mais vendidos
st.subheader("Produtos mais vendidos")


top_vendidos = (
    produtos
    .sort_values(
        "quantidade",
        ascending=False
    )
    .head(10)
    .copy()
)


col1, col2 = st.columns([1.5, 1])


with col1:

    grafico_vendidos = (
        top_vendidos[
            ["produto", "quantidade"]
        ]
        .sort_values("quantidade")
        .set_index("produto")
    )

    st.bar_chart(
        grafico_vendidos
    )


with col2:

    tabela_vendidos = top_vendidos[
        [
            "produto",
            "categoria",
            "quantidade",
            "faturamento",
        ]
    ].copy()

    tabela_vendidos.columns = [
        "Produto",
        "Categoria",
        "Itens",
        "Faturamento",
    ]

    st.dataframe(
        tabela_vendidos,
        use_container_width=True,
        hide_index=True,
    )


st.divider()


# produtos mais lucrativos
st.subheader("Produtos mais lucrativos")


top_lucrativos = (
    produtos
    .sort_values(
        "lucro",
        ascending=False
    )
    .head(10)
    .copy()
)


col1, col2 = st.columns([1.5, 1])


with col1:

    grafico_lucrativos = (
        top_lucrativos[
            ["produto", "lucro"]
        ]
        .sort_values("lucro")
        .set_index("produto")
    )

    st.bar_chart(
        grafico_lucrativos
    )


with col2:

    tabela_lucrativos = top_lucrativos[
        [
            "produto",
            "categoria",
            "faturamento",
            "custo",
            "lucro",
            "margem",
        ]
    ].copy()

    tabela_lucrativos["margem"] = (
        tabela_lucrativos["margem"] * 100
    ).round(2)

    tabela_lucrativos.columns = [
        "Produto",
        "Categoria",
        "Faturamento",
        "Custo",
        "Lucro",
        "Margem (%)",
    ]

    st.dataframe(
        tabela_lucrativos,
        use_container_width=True,
        hide_index=True,
    )


st.divider()

# quantidade de itens por categoria
st.subheader("Quantidade de itens por categoria")


categorias_volume = query(f"""
    SELECT
        c.name AS categoria,
        SUM(oi.quantity) AS quantidade

    FROM orders o

    INNER JOIN order_items oi
        ON oi.order_id = o.id

    INNER JOIN product_variants pv
        ON pv.id = oi.product_variant_id

    INNER JOIN products p
        ON p.id = pv.product_id

    INNER JOIN categories c
        ON c.id = p.category_id

    WHERE o.status IN ('paid', 'confirmed')

      AND o.placed_at::DATE
          BETWEEN '{data_inicio}' AND '{data_fim}'

    GROUP BY c.name
    ORDER BY quantidade DESC
""")


st.bar_chart(
    categorias_volume.set_index("categoria")
)