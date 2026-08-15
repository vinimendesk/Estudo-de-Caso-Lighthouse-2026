import sys
from pathlib import Path

import streamlit as st
import pandas as pd


# importação do banco
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import query


st.title("Análise de Clientes")

st.caption(
    "Perfil de valor, frequência e concentração da carteira de clientes"
)


# filtros

periodo = query("""
    SELECT
        MIN(placed_at)::DATE AS data_min,
        MAX(placed_at)::DATE AS data_max
    FROM orders
    WHERE status IN ('paid', 'confirmed')
""")


data_min = periodo.loc[0, "data_min"]
data_max = periodo.loc[0, "data_max"]


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


# Base de Clientes
clientes = query(f"""
    SELECT
        c.id AS customer_id,

        COALESCE(
            c.trade_name,
            c.legal_name
        ) AS cliente,

        COUNT(DISTINCT o.id) AS pedidos,

        SUM(oi.quantity) AS itens,

        SUM(oi.line_total) AS faturamento,

        SUM(
            oi.line_total -
            (oi.quantity * pv.cost_price)
        ) AS lucro

    FROM orders o

    INNER JOIN customers c
        ON c.id = o.customer_id

    INNER JOIN order_items oi
        ON oi.order_id = o.id

    INNER JOIN product_variants pv
        ON pv.id = oi.product_variant_id

    WHERE o.status IN ('paid', 'confirmed')

      AND o.placed_at::DATE
          BETWEEN '{data_inicio}' AND '{data_fim}'

    GROUP BY
        c.id,
        c.trade_name,
        c.legal_name
""")


# Métricas derivadas

clientes["ticket_medio"] = (
    clientes["faturamento"]
    / clientes["pedidos"]
)


clientes["margem"] = (
    clientes["lucro"]
    / clientes["faturamento"]
).fillna(0)


clientes["faturamento_acumulado"] = (
    clientes["faturamento"]
    .sort_values(ascending=False)
    .cumsum()
)


faturamento_total = clientes["faturamento"].sum()


clientes["participacao"] = (
    clientes["faturamento"]
    / faturamento_total
).fillna(0)


clientes["participacao_acumulada"] = (
    clientes["participacao"]
    .sort_values(ascending=False)
    .cumsum()
)


# KPIs

quantidade_clientes = len(clientes)

faturamento = clientes["faturamento"].sum()

lucro = clientes["lucro"].sum()

pedidos = clientes["pedidos"].sum()

ticket_medio = (
    faturamento / pedidos
    if pedidos > 0
    else 0
)

st.divider()


# Top 10 clientes por lucro
st.subheader("Top 10 clientes por lucro")


top_lucro = (
    clientes
    .sort_values("lucro", ascending=False)
    .head(10)
    .copy()
)


col1, col2 = st.columns([1.5, 1])


with col1:

    grafico_lucro = (
        top_lucro[
            ["cliente", "lucro"]
        ]
        .sort_values("lucro")
        .set_index("cliente")
    )

    st.bar_chart(
        grafico_lucro
    )


with col2:

    tabela_lucro = top_lucro[
        [
            "cliente",
            "faturamento",
            "lucro",
            "pedidos",
            "ticket_medio",
            "margem",
        ]
    ].copy()

    tabela_lucro["faturamento"] = (
        tabela_lucro["faturamento"]
        .round(2)
    )

    tabela_lucro["lucro"] = (
        tabela_lucro["lucro"]
        .round(2)
    )

    tabela_lucro["ticket_medio"] = (
        tabela_lucro["ticket_medio"]
        .round(2)
    )

    tabela_lucro["margem"] = (
        tabela_lucro["margem"] * 100
    ).round(2)

    tabela_lucro.columns = [
        "Cliente",
        "Faturamento",
        "Lucro",
        "Pedidos",
        "Ticket médio",
        "Margem (%)",
    ]

    st.dataframe(
        tabela_lucro,
        use_container_width=True,
        hide_index=True,
    )


st.divider()


# Ranking de Clientes
st.subheader("Ranking de clientes")

ranking = (
    clientes
    .sort_values(
        "faturamento",
        ascending=False
    )
    .reset_index(drop=True)
)


ranking.index += 1

ranking_display = ranking[
    [
        "cliente",
        "faturamento",
        "lucro",
        "pedidos",
        "itens",
        "ticket_medio",
        "margem",
    ]
].copy()


ranking_display.columns = [
    "Cliente",
    "Faturamento",
    "Lucro",
    "Pedidos",
    "Itens",
    "Ticket médio",
    "Margem (%)",
]


ranking_display["Margem (%)"] = (
    ranking_display["Margem (%)"] * 100
).round(2)


st.dataframe(
    ranking_display,
    use_container_width=True,
    height=400,
)


st.divider()


# Distribuição de Faturamento
st.subheader("Distribuição do faturamento por cliente")


distribuicao = (
    clientes
    .sort_values(
        "faturamento",
        ascending=False
    )
    .head(20)
    .copy()
)


distribuicao["cliente"] = (
    distribuicao["cliente"]
    .astype(str)
)


grafico_distribuicao = (
    distribuicao[
        ["cliente", "faturamento"]
    ]
    .sort_values("faturamento")
    .set_index("cliente")
)


st.bar_chart(
    grafico_distribuicao
)


st.caption(
    "Exibidos os 20 clientes com maior faturamento."
)


st.divider()


# Clientes com maior volume

st.subheader("Clientes com maior volume de compras")


volume = (
    clientes
    .sort_values(
        "itens",
        ascending=False
    )
    .head(10)
)


st.dataframe(
    volume[
        [
            "cliente",
            "itens",
            "pedidos",
            "faturamento",
            "ticket_medio",
        ]
    ].rename(
        columns={
            "cliente": "Cliente",
            "itens": "Itens",
            "pedidos": "Pedidos",
            "faturamento": "Faturamento",
            "ticket_medio": "Ticket médio",
        }
    ),
    use_container_width=True,
    hide_index=True,
)


st.divider()


# Concentração

st.subheader("Análise de concentração do faturamento")


clientes_concentracao = (
    clientes
    .sort_values(
        "faturamento",
        ascending=False
    )
    .reset_index(drop=True)
)


clientes_concentracao["participacao"] = (
    clientes_concentracao["faturamento"]
    / faturamento
)


clientes_concentracao["participacao_acumulada"] = (
    clientes_concentracao["participacao"]
    .cumsum()
)


clientes_concentracao["cliente_rank"] = (
    clientes_concentracao.index + 1
)


col1, col2, col3 = st.columns(3)


for col, percentual in zip(
    [col1, col2, col3],
    [0.10, 0.20, 0.50]
):

    quantidade = max(
        1,
        round(
            len(clientes_concentracao)
            * percentual
        )
    )

    concentracao = (
        clientes_concentracao
        .head(quantidade)["faturamento"]
        .sum()
        / faturamento
    )

    with col:
        st.metric(
            f"Top {percentual:.0%}",
            f"{concentracao:.1%}"
        )


# Curva de concentração

curva = clientes_concentracao[
    [
        "cliente_rank",
        "participacao_acumulada",
    ]
].copy()


curva = curva.set_index(
    "cliente_rank"
)


st.line_chart(
    curva
)


st.caption(
    "A curva mostra quanto do faturamento acumulado "
    "é concentrado nos clientes de maior valor."
)