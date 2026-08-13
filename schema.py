# Importar bibliotecas necessárias.
import os
import re
import csv
import datetime

# Caminho com o diretório dos csv
input = r"C:\Users\vini7\Desktop\Arquivos Python\Estudo de Caso Lighthouse 2026\Estudo-de-Caso-Lighthouse-2026\data"
# Caminho para salvar o arquivo sql
output = r"C:\Users\vini7\Desktop\Arquivos Python\Estudo de Caso Lighthouse 2026\Estudo-de-Caso-Lighthouse-2026\sql\questao_2-schema.sql"

#Função para determinar o delimitador

# Função para recupera todos os csv
def get_csv(directory):

    return (
        # Concatena o caminho do directory junto com o csv
        os.path.join(directory, csv)
        # Loop para recuperar cada csv
        for csv in os.listdir(directory)
        # Se o arquivo for do tipo csv, ele será retornado pelo função
        if csv.lower().endswith(".csv")
    )

# Função para normalizar o nome da tabela.
def normalize_identifier(table_name):
    # Remover espaços em banco.
    table_name = table_name.strip()

    # Expressão regular para substituir qualquer caractere que não seja número ou letra por _
    table_name = re.sub(r"[^a-zA-Z0-9_]+", "-", table_name)

    # Converte múltiplos _ por somente um _ em sequência elimina o _ das pontas; Tudo em letra minúscula.
    table_name = re.sub(r"_", "_", table_name).strip("_").lower()

    # Verifica se o nome da tabela começa com um número, se verdadeiro, adiciona _ no começo do nome.
    if table_name[0].isdigit():
        table_name = "_" + table_name

    return table_name

# Função para detectar qual o delimitador do csv.
def detect_delimiter(path):

    # Abri o csv em modo de leitura
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        csv_file = f.read()

        try:
            # Retorna o delimitar encontrado no csv.
            return csv.Sniffer().sniff(csv_file, delimiters=",;|\t").delimiter
        except csv.Error:
            # Em caso de erro, retorna a vírgula como separador padrão.
            return ","

# Inferência de tipo para boolean
def is_boolean(value):
    # Verifica se o valor apresenta texto que indicam valors booleanos
    return value.strip().lower() in {"true", "false", "t", "f", "yes", "no"}

# Inferência de tipo para decimal
def is_decimal(value):
    # Verifica se o texto apresenta casas decimais
    return bool(re.fullmatch(r"[+-]?(?:\d+\.\d+|\d+)", value))

# Infrência de tipo para inteiro
def is_integer(value):
    # Verifica se o texto ´um número inteiro (sem casas decimais)
    return bool(re.fullmatch(r"[+-]?\d+", value))

# Inferência de tipo para datetime
def is_datetime(value):
    # Remover espaços vazios
    value = value.strip()

    # Tupla com os formatos d data e hora
    formats = (
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f"
    )

    # Percorre todos os formatos datetime
    for fmt in formats:
        try:
            # Tenta converter o texto em data de acordo com os formatos
            datetime.datetime.strptime(value, fmt)
            return True
        except ValueError:
            # Se ocorrrer erro durante a conversão, passe para o próximo valor
            pass

    return False

# Função para a inferência de dados.
def infer_column_type(column, values):

    # Remove valores nulos, "" e espaços das valores de cada coluna
    non_empty = [v.strip() for v in values if v is not None and v.strip() != ""]

    # Se a coluna não conter dados, coloque como padrão o tipo String.
    if not non_empty:
        return "TEXT"

    # nome das colunas como minúsculo.
    name = column.lower()

    # Boolean
    if all(is_boolean(v) for v in non_empty):
        return "BOOLEAN"

    # Datetime
    if all(is_datetime(v) for v in non_empty):
        return "TIMESTAMP"

    # Colunas que podem se encaixar em outros dados, mas devem ser texto.
    text = {
        "postal", "zip", "cep", "phone", "telefone", "tax_id",
        "cpf", "cnpj", "document", "registration", "code",
        "order_number"
    }

    # Verifica se o nome da coluna possui qualquer elemento presente em text
    if any(txt in name for txt in text):
        return "TEXT"

    # Se a coluna for id
    if name == "id" or name.endswith("_id"):
        if all(is_integer(v) for v in non_empty):
            return "BIGINT"

    # Colunas com valores decimais
    decimal = (
        "amount", "price", "total", "subtotal", "discount",
        "value", "valor", "cost", "tax", "rate"
    )

    if any(dcm in name for dcm in decimal):
        if all(is_decimal(v) for v in non_empty):
            return "NUMERIC(18,2)"

    # Inteiros 
    if all(is_integer(v) for v in non_empty):
        return "BIGINT"

    # Decimais 
    if all(is_decimal(v) for v in non_empty):
        return "NUMERIC(18,6)"

    return "TEXT"



# Função para retornar todas as colunas e sua respectiva tipagem
def read_csv_schema(path):

    # Detecta o delimitador do arquivo csv
    delimiter = detect_delimiter(path)

    # Abre o csv em modo de leitura
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        # Converte o csv em um dicionário
        reader = csv.DictReader(f, delimiter=delimiter)

        # Retorna o nome das colunas no dicionário.
        columns = reader.fieldnames
        # Normaliza o nome das colunas
        columns_normalize = [normalize_identifier(c) for c in columns]

        # Lista vazia com as colunas de nome único
        unique_columns = []
        # Dicionário para realizar a contagem de ocorrência de cada coluna.
        counts = {}

        # Retorna cada coluna normalizada
        for column in columns_normalize:
            # Realiza a contagem de ocorrências de cada coluna
            counts[column] = counts.get(column, 0) + 1
            if counts[column] == 1:
                # Se a coluna só apareceu uma vez na contagem, adiciona na lista de colunas únicas
                unique_columns.append(column)
            else:
                # Caso contrário, adiciona um número depois do nome
                unique_columns.append(f"{column}_{counts[column]}")

        # Dicinário vazio contendo o nome das colunas como chave.
        values_by_column = {column: [] for column in unique_columns}

        # Retorna cada linha do csv.
        for row in reader:
            # Faz o agrupamnto das colunas iniciais com as colunas normalizadas.
            for original, normalized in zip(columns, columns_normalize):
                # Adiciona cada linha ao dicionário com as colunas normalizadas.
                values_by_column[normalized].append(row.get(original, ""))

        # Retorna o tipagem dos dados de cada coluna
        types = {
            # Realiza a inferência de dados para cada coluna.
            column: infer_column_type(column, values)
            for column, values in values_by_column.items()
        }

    return unique_columns, types

# Função que poem o nome da tabela entre aspas.
def quote_identifier(table_name):
    return '"' + table_name.replace('"', '""') + '"'

# Função gerar código SQL de criação de tabela.
def build_create_table(path):

    # Busca o nome do arquivo csv
    base_name = os.path.splitext(os.path.basename(path))[0]
    # Normaliza o nome do arquivo para um padrão aceitável em PostgreSQl.
    table_name = normalize_identifier(base_name)

    # Retorna as colunas e tipagem da coluna
    columns, types = read_csv_schema(path)

    # Cria a linha de criação da tabela
    lines = [f"CREATE TABLE IF NOT EXISTS {quote_identifier(table_name)} ("]

    # Lista para armazenar o texto para a criação de cada coluna.
    column_definitions = []

    # Percorre cada coluna
    for column in columns:
        # Texto com o nome e a tipagem da coluna.
        definition = f"    {quote_identifier(column)} {types[column]}"

        # Se a coluna for um id, define-a como chave primária
        if column == "id":
            # Adiciona o txxto de chave primária ao rexto final
            definition += " PRIMARY KEY"

        # Adiciona a linha da coluna 
        column_definitions.append(definition)

    # Adiciona uma vírgula para separar cada comando
    lines.append(",\n".join(column_definitions))
    # Fecha parenteses 
    lines.append(");")

    return "\n".join(lines)

# Função principal
def main():

    # Leitura do csv.
    csv_files = get_csv(input)

    # Se não achar csv, lançe uma exeção
    if not csv_files:
        raise FileNotFoundError(
            f"Nenhum arquivo CSV encontrado."
        )

    # Texto a ser inserido no SQL
    sql_text = [
        "-- Questao 2 Schema",
    ]

    # Retorna o caminho de cada arquivo csv
    for path in csv_files:
        # Adiciona o nome do arquivo csv no texto
        sql_text.append(f"-- {os.path.basename(path)}")
        # Adiciona o SQL da criação da tabela no texto
        sql_text.append(build_create_table(path))
        # Adiciona um espaço
        sql_text.append("")

    # Salva o comando SQL em um arquivo sql.
    with open(output, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(sql_text))

    print(f"Schema criado com sucesso")

if __name__ == "__main__":
    main()