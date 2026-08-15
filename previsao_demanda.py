# Questão 6.

import pandas as pd

# endereço atual
base = r"C:\Users\vini7\Desktop\Arquivos Python\Estudo de Caso Lighthouse 2026\Estudo-de-Caso-Lighthouse-2026\data"

# Carrega cada csv
orders = pd.read_csv(base + r"\orders.csv")
order_items = pd.read_csv(base + r"\order_items.csv")
products = pd.read_csv(base + r"\products.csv")
product_variants = pd.read_csv(base + r"\product_variants.csv")

# Dataset unificado com todos os dados necesários
dataset = (
    # order_items -> product_variants
    order_items
    .merge(
        product_variants,
        left_on = "product_variant_id",
        right_on = "id",
        how = "inner",
        # suffixes = ("_item", "_variant")
    )# .drop(columns = "id")
    # product_variants -> product
    .merge(
        products,
        left_on = "product_id",
        right_on = "id",
        how = "inner",
        # suffixes = ("_variant", "_product") 
    ).drop(columns = "id")
    # product -> order
    .merge(
        orders,
        left_on = "order_id",
        right_on = "id",
        how = "inner",
        # suffixes = ("_item", "_order") 
    ).drop(columns = "id")
)

# Convertendo placed_at para datetime
dataset["placed_at"] = pd.to_datetime(dataset["placed_at"])

# Selecionando vendas pagas e confirmadas da Bússola de Bordo 702
dataset = dataset[
    (dataset["name"] == "Bússola de Bordo 702") &
    (dataset["status"] .isin(["paid", "confirmed"])
     ).copy()
]

# Criando a coluna mês
dataset["mes"] = dataset["placed_at"].dt.to_period("M")

# Agrupamento de vendas por mes
vendas_mensais = (
    dataset.groupby("mes", as_index = False)["quantity"]
    .sum()
    .rename(columns={"quantity": "vendas"})
)

# Criação do calendário mensal
data_inicio = vendas_mensais["mes"].min()

calendario = pd.period_range(
    start = data_inicio,
    end = pd.Period("2026-03", freq = "M"),
    freq = "M"
)

serie = pd.DataFrame({"mes": calendario})

# Realiza LEFT JOIN das datas com a vendas, substituindo valores nulos por 0 (datas sem venda)
serie = serie.merge(vendas_mensais, on = "mes", how = "left")
serie["vendas"] = serie["vendas"].fillna(0)

# Dados para treino 
treino = serie[serie["mes"] <= pd.Period("2025-12", freq = "M")].copy()

# Dados para teste
teste = serie[
    (serie["mes"] >= pd.Period("2026-01", freq = "M")) &
    (serie["mes"] <= pd.Period("2026-03", freq = "M"))
].copy()

# Média móvel dos três meses anteriores
serie["previsao"] = (
    serie["vendas"].shift(1).rolling(window = 3).mean()
)

# Resultado da previsão
resultado = serie[
    (serie["mes"] >= pd.Period("2026-01", freq = "M")) &
    (serie["mes"] <= pd.Period("2026-03", freq = "M"))
]

# Cálculo do erro absoluto
resultado["erro_absoluto"] = (
    resultado["vendas"] - resultado["previsao"]
).abs()

# MAE
mae = resultado["erro_absoluto"].mean()

# Soma das previsões do primeiro trimestre
soma_previsoes = resultado["previsao"].sum()
soma_previsoes_inteira = round(soma_previsoes)

print("Previsao de Demanda do Produto Bussola de Bordo 702")
print("\nResultados: ")
print(resultado[["mes", "vendas", "previsao", "erro_absoluto"]].to_string(index = False))
print(f"\nMAE: {mae:.2f} unidades")
print(f"soma das previsoes: {soma_previsoes_inteira} unidades")

