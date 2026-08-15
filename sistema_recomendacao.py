# Questão 7.

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# endereço atual
base = r"C:\Users\vini7\Desktop\Arquivos Python\Estudo de Caso Lighthouse 2026\Estudo-de-Caso-Lighthouse-2026\data"

# Carrega cada csv
orders = pd.read_csv(base + r"\orders.csv")
order_items = pd.read_csv(base + r"\order_items.csv")
products = pd.read_csv(base + r"\products.csv")
product_variants = pd.read_csv(base + r"\product_variants.csv")

# Dataset unificado com todos os dados necessários
dataset = (
    order_items
    .merge(
        product_variants,
        left_on="product_variant_id",
        right_on="id",
        how="inner"
    )
    .merge(
        products,
        left_on="product_id",
        right_on="id",
        how="inner"
    )
    .drop(columns="id")
    .merge(
        orders,
        left_on="order_id",
        right_on="id",
        how="inner"
    )
    .drop(columns="id")
)


# # Selecionando somente vendas pagas e confirmadas
dataset = dataset [
    dataset["status"].isin(["paid", "confirmed"])
]

# Mantém somente a coluna de cliente e produto e remove duplicadas
compras = dataset[
    ["customer_id", "product_id"]
].drop_duplicates()

# Matriz Usuário x Produto
matriz = pd.crosstab(
    compras["customer_id"],
    compras["product_id"]
)

# Faz a transposição da matriz
matriz_produtos = matriz.T

# Calcula a similaridade de cosseno
similarity = cosine_similarity(matriz_produtos)

# Criação de um dataframe com as similaridades
similarity_df = pd.DataFrame(
    similarity,
    index = matriz_produtos.index,
    columns= matriz_produtos.index
)

# Retorna somente o Motor de Popa 1949
motor_de_popa = products.loc[
    products["name"] == "Motor de Popa 1949",
    "id"
].iloc[0]

# Retorna os produtos similares em ordem de maior similaridade, excluindo o próprio motor_de_popa 
ranking = similarity_df[motor_de_popa].sort_values(ascending = False).drop(motor_de_popa)

# dataset com ID e nome dos produtos para cruzar com o dataset ranking
products_name = products[
    ["id", "name"]
].drop_duplicates().set_index("id")

# Retorna 
products_name_ranking = products_name.loc[ranking.index].copy()
products_name_ranking["similaridade"] = ranking.values

print(products_name_ranking)