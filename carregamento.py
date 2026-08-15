# Questão 3.
import duckdb
from pathlib import Path

# Retorna o diretório atual
BASE = Path(__file__).parent
# Definição do arquivo do banco de dados
DB = BASE / "lh_nautical.duckdb"
# Caminho com os dados CSV
DADOS = BASE / "data"
# Caminho com o schema
SCHEMA = BASE / "sql"

# Cria o arquivo e cria conexão com o banco de dados.
con = duckdb.connect(DB)

# Cria as tabelas com o schema da questão 2 e faz a leitura do comando.
con.execute((SCHEMA / "questao_2-schema.sql").read_text(encoding="utf-8"))

# Percorre todos os csv dentro da pasta data
for csv in DADOS.glob("*.csv"):
    # Realiza a limpeza do nome da tabela.
    tabela = csv.stem

    print(f"Carregando {csv.name}...")

    # Insere os valores do csv na tabela correspondente.
    con.execute(f"""
        INSERT INTO "{tabela}"
        SELECT *
        FROM read_csv(
            '{csv.as_posix()}',
            header = true
        )
    """)

    # Retorna a quantidade de linhas da tabela
    quantidade = con.execute(
        f'SELECT COUNT(*) FROM "{tabela}"'
    ).fetchone()[0]

    print(f"  {quantidade} registros")

# Fecha a conexão com o DuckDB
con.close()

print("\nCarregamento concluído")

# Somatório das linhas das tabelas customers, orders, ordr_items e payments - 251864
""" 
-- Comando SQL utilizado plo DBaver.
SELECT
    (SELECT COUNT(*) FROM main.customers) +
    (SELECT COUNT(*) FROM main.orders) +
    (SELECT COUNT(*) FROM main.order_items) +
    (SELECT COUNT(*) FROM main.payments) AS total_linhas;
"""

