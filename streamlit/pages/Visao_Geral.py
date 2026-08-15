import streamlit as st
import pandas as pd

import sys
from pathlib import Path

import streamlit as st
import pandas as pd

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from database import query

st.title("Visão Geral")
st.caption(
    "Principais indicadores e desempenho comercial da LH Nautical"
)


# Filtros
periodo = query("""
    SELECT
        MIN(placed_at)::DATE AS data_min,
        MAX(placed_at)::DATE AS data_max
    FROM orders
    WHERE status IN ('paid', 'confirmed')
""")

data_min = periodo.loc[0, "data_min"]
data_max = periodo.loc[0, "data_max"]


col1, col2 = st.columns([2, 1])

with col1:
    intervalo = st.date_input(
        "Período",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max,
    )

with col2:
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


# Verificação do período
if len(intervalo) != 2:
    st.warning("Selecione uma data inicial e uma data final.")
    st.stop()


data_inicio = intervalo[0]
data_fim = intervalo[1]


# Filtro de categoria
filtro_categoria = ""

if categoria_selecionada != "Todas":
    filtro_categoria = f"""
        AND c.name = '{categoria_selecionada.replace("'", "''")}'
    """


# KPIs
kpis = query(f"""
    SELECT
        COALESCE(SUM(oi.line_total), 0) AS faturamento,

        COALESCE(
            SUM(
                oi.line_total -
                (oi.quantity * pv.cost_price)
            ),
            0
        ) AS lucro,

        COUNT(DISTINCT o.id) AS pedidos,

        COALESCE(SUM(oi.quantity), 0) AS itens,

        COUNT(DISTINCT o.customer_id) AS clientes

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
      AND o.placed_at::DATE BETWEEN '{data_inicio}' AND '{data_fim}'
      {filtro_categoria}
""")


faturamento = kpis.loc[0, "faturamento"]
lucro = kpis.loc[0, "lucro"]
pedidos = kpis.loc[0, "pedidos"]
itens = kpis.loc[0, "itens"]
clientes = kpis.loc[0, "clientes"]

ticket_medio = (
    faturamento / pedidos
    if pedidos > 0
    else 0
)


# Cards

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        "Faturamento",
        f"R$ {faturamento:,.2f}".replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

with col2:
    st.metric(
        "Lucro",
        f"R$ {lucro:,.2f}".replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

with col3:
    st.metric(
        "Pedidos",
        f"{pedidos:,.0f}".replace(",", ".")
    )

with col4:
    st.metric(
        "Itens vendidos",
        f"{itens:,.0f}".replace(",", ".")
    )

with col5:
    st.metric(
        "Clientes",
        f"{clientes:,.0f}".replace(",", ".")
    )

with col6:
    st.metric(
        "Ticket médio",
        f"R$ {ticket_medio:,.2f}".replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


st.divider()


# Evolução Vendas

st.subheader("Evolução das vendas")

vendas_tempo = query(f"""
    SELECT
        o.placed_at::DATE AS data,
        SUM(oi.line_total) AS faturamento,
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
      AND o.placed_at::DATE BETWEEN '{data_inicio}' AND '{data_fim}'
      {filtro_categoria}

    GROUP BY o.placed_at::DATE
    ORDER BY data
""")


st.line_chart(
    vendas_tempo.set_index("data")[["faturamento", "lucro"]]
)


st.divider()


# Faturamento por categoria
col1, col2 = st.columns(2)


with col1:

    st.subheader("Faturamento por categoria")

    faturamento_categoria = query(f"""
        SELECT
            c.name AS categoria,
            SUM(oi.line_total) AS faturamento

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
          AND o.placed_at::DATE BETWEEN '{data_inicio}' AND '{data_fim}'

        GROUP BY c.name
        ORDER BY faturamento DESC
    """)

    st.bar_chart(
        faturamento_categoria.set_index("categoria")
    )


# Top 10 Produtos
with col2:

    st.subheader("Top 10 produtos")

    top_produtos = query(f"""
        SELECT
            p.name AS produto,
            SUM(oi.line_total) AS faturamento

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
          AND o.placed_at::DATE BETWEEN '{data_inicio}' AND '{data_fim}'
          {filtro_categoria}

        GROUP BY p.id, p.name
        ORDER BY faturamento DESC
        LIMIT 10
    """)

    st.bar_chart(
        top_produtos.set_index("produto")
    )


st.divider()


# Vendas por dia da semana

st.subheader("Média de vendas por dia da semana")

st.caption(
    "Canal POS. Dias sem venda são considerados como R$ 0."
)


vendas_semana = query(f"""
    WITH calendario AS (
        SELECT
            data::DATE AS data,
            EXTRACT(ISODOW FROM data)::INTEGER
                AS numero_dia_semana,

            CASE EXTRACT(ISODOW FROM data)::INTEGER
                WHEN 1 THEN 'Segunda-feira'
                WHEN 2 THEN 'Terça-feira'
                WHEN 3 THEN 'Quarta-feira'
                WHEN 4 THEN 'Quinta-feira'
                WHEN 5 THEN 'Sexta-feira'
                WHEN 6 THEN 'Sábado'
                WHEN 7 THEN 'Domingo'
            END AS dia_semana

        FROM generate_series(
            '{data_inicio}'::DATE,
            '{data_fim}'::DATE,
            INTERVAL '1 day'
        ) AS t(data)
    ),

    vendas_diarias AS (
        SELECT
            placed_at::DATE AS data,
            SUM(total) AS venda_diaria

        FROM orders

        WHERE channel = 'pos'
          AND status IN ('paid', 'confirmed')
          AND placed_at::DATE BETWEEN
              '{data_inicio}' AND '{data_fim}'

        GROUP BY placed_at::DATE
    )

    SELECT
        c.numero_dia_semana,
        c.dia_semana,

        AVG(
            COALESCE(v.venda_diaria, 0)
        ) AS media_vendas

    FROM calendario c

    LEFT JOIN vendas_diarias v
        ON c.data = v.data

    GROUP BY
        c.numero_dia_semana,
        c.dia_semana

    ORDER BY c.numero_dia_semana
""")


st.bar_chart(
    vendas_semana.set_index("dia_semana")["media_vendas"]
)