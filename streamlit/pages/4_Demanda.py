import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# caminho da aplicação
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from database import query

# título
st.title("Análise de Demanda")

st.caption(
    "Comportamento temporal das vendas, padrões semanais e previsão de demanda"
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


# vendas diárias
vendas_diarias = query(f"""
    SELECT
        placed_at::DATE AS data,
        SUM(total) AS faturamento,
        COUNT(DISTINCT id) AS pedidos

    FROM orders

    WHERE status IN ('paid', 'confirmed')

      AND placed_at::DATE
          BETWEEN '{data_inicio}' AND '{data_fim}'

    GROUP BY placed_at::DATE

    ORDER BY data
""")


# calendário completo
calendario = query(f"""
    SELECT
        data::DATE AS data,

        EXTRACT(
            ISODOW FROM data
        )::INTEGER AS numero_dia_semana,

        CASE EXTRACT(
            ISODOW FROM data
        )::INTEGER
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
""")


# combinação do calendário com as vendas
demanda_diaria = calendario.merge(
    vendas_diarias,
    on="data",
    how="left"
)


# preenchimento dos dias sem venda
demanda_diaria["faturamento"] = (
    demanda_diaria["faturamento"]
    .fillna(0)
)


demanda_diaria["pedidos"] = (
    demanda_diaria["pedidos"]
    .fillna(0)
)


# vendas médias por dia da semana
media_semana = (
    demanda_diaria
    .groupby(
        [
            "numero_dia_semana",
            "dia_semana"
        ],
        as_index=False
    )
    .agg(
        media_faturamento=(
            "faturamento",
            "mean"
        ),
        media_pedidos=(
            "pedidos",
            "mean"
        )
    )
    .sort_values(
        "numero_dia_semana"
    )
)


# quantidade de dias por semana
media_semana["dias_analisados"] = (
    demanda_diaria
    .groupby(
        [
            "numero_dia_semana",
            "dia_semana"
        ]
    )
    .size()
    .values
)


# indicadores
faturamento_total = (
    demanda_diaria["faturamento"].sum()
)


pedidos_total = (
    demanda_diaria["pedidos"].sum()
)


dias_analisados = len(
    demanda_diaria
)


dias_com_venda = (
    demanda_diaria["faturamento"] > 0
).sum()


dias_sem_venda = (
    demanda_diaria["faturamento"] == 0
).sum()


media_diaria = (
    faturamento_total / dias_analisados
    if dias_analisados > 0
    else 0
)


# cards
col3, col4, col5 = st.columns(3)


with col3:
    st.metric(
        "Dias analisados",
        f"{dias_analisados:,.0f}".replace(",", ".")
    )


with col4:
    st.metric(
        "Dias com venda",
        f"{dias_com_venda:,.0f}".replace(",", ".")
    )


with col5:
    st.metric(
        "Dias sem venda",
        f"{dias_sem_venda:,.0f}".replace(",", ".")
    )


st.divider()


# evolução do faturamento
st.subheader("Evolução diária do faturamento")


evolucao = (
    demanda_diaria[
        ["data", "faturamento"]
    ]
    .set_index("data")
)


st.line_chart(
    evolucao
)


st.divider()


# média de vendas por dia da semana
st.subheader("Média de vendas por dia da semana")


grafico_semana = (
    media_semana[
        [
            "dia_semana",
            "media_faturamento"
        ]
    ]
    .set_index("dia_semana")
)


st.bar_chart(
    grafico_semana
)


st.caption(
    "A média considera todos os dias do período, inclusive aqueles sem vendas."
)


st.dataframe(
    media_semana[
        [
            "dia_semana",
            "media_faturamento",
            "media_pedidos",
            "dias_analisados",
        ]
    ].rename(
        columns={
            "dia_semana": "Dia da semana",
            "media_faturamento": "Faturamento médio",
            "media_pedidos": "Pedidos médios",
            "dias_analisados": "Dias analisados",
        }
    ),
    use_container_width=True,
    hide_index=True,
)


st.divider()


# produtos mais demandados
st.subheader("Produtos mais demandados")


produtos_demanda = query(f"""
    SELECT
        p.name AS produto,
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

    GROUP BY
        p.name,
        c.name

    ORDER BY
        quantidade DESC

    LIMIT 10
""")


col1, col2 = st.columns([1.5, 1])


with col1:

    grafico_demanda = (
        produtos_demanda[
            [
                "produto",
                "quantidade"
            ]
        ]
        .sort_values("quantidade")
        .set_index("produto")
    )

    st.bar_chart(
        grafico_demanda
    )


with col2:

    st.dataframe(
        produtos_demanda.rename(
            columns={
                "produto": "Produto",
                "categoria": "Categoria",
                "quantidade": "Itens vendidos",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


st.divider()


# média móvel do faturamento
st.subheader("Tendência da demanda")


tendencia = demanda_diaria[
    [
        "data",
        "faturamento"
    ]
].copy()


tendencia["media_movel_7_dias"] = (
    tendencia["faturamento"]
    .rolling(
        window=7,
        min_periods=1
    )
    .mean()
)


tendencia = tendencia.set_index("data")


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=tendencia.index,
        y=tendencia["faturamento"],
        mode="lines",
        name="Faturamento diário"
    )
)

fig.add_trace(
    go.Scatter(
        x=tendencia.index,
        y=tendencia["media_movel_7_dias"],
        mode="lines",
        name="Tendência - média móvel 7 dias",
        line=dict(
            color="red",
            width=3
        )
    )
)

fig.update_layout(
    xaxis_title="Data",
    yaxis_title="Faturamento",
    legend_title="Indicador",
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


st.caption(
    "A média móvel de 7 dias suaviza oscilações diárias e facilita a identificação da tendência."
)


st.divider()


# previsão simples de demanda
st.subheader("Previsão de demanda")


st.caption(
    "Estimativa baseada na média móvel dos últimos 7 dias."
)


ultimos_dias = demanda_diaria.tail(7)


previsao_faturamento = (
    ultimos_dias["faturamento"].mean()
)


previsao_pedidos = (
    ultimos_dias["pedidos"].mean()
)


col1, col2, col3 = st.columns(3)


with col1:
    st.metric(
        "Previsão de faturamento diário",
        f"R$ {previsao_faturamento:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


with col2:
    st.metric(
        "Previsão de pedidos diários",
        f"{previsao_pedidos:,.1f}"
        .replace(".", ",")
    )


with col3:
    st.metric(
        "Janela utilizada",
        "7 dias"
    )