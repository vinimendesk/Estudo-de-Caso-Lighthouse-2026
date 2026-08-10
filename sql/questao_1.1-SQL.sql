-- Parte 1 - Visão geral da tabela orders
-- Quantidade total de linhas
SELECT count(*) AS total_linhas
FROM orders;

-- Quantidade total de colunas
SELECT * 
from orders;

-- Intervalo de datas analisadas
-- Notar a existência de pedidos criados em datas questionáveis (criados depois de 2016-08-10)
SELECT 
	MIN(created_at) AS data_minina,
    MAX(created_at) as data_máxima
FROM orders;

-- Parte 2 - Análise de valores númericos 
-- Valor mínimo, máximo e médio
SELECT 
	MIN(total) AS valor_minimo,
    MAX(total) as valor_maximo,
    avg(total) as valor_medio
from orders;

-- Realizei toda a análise exploratório em um notebook python, contendo gráficos e explicações. 
-- Criei esse arquivo SQL para entregar a Questão 1.1 - SQL.
