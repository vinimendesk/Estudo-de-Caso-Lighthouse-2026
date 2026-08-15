-- Questão 5 - Dimensão de calendário

WITH calendario AS (
	SELECT
		-- conversão de data para o tipo DATE
		data::DATE AS data,
		-- retorna o dia da semana de data como um tipo inteiro
		EXTRACT(ISODOW FROM data)::INTEGER AS numero_dia_semana,
		-- converte o número retornado em textos do dia da semana.
		CASE EXTRACT(ISODOW FROM data)::INTEGER
			WHEN 1 THEN 'Segunda-feira'
			WHEN 2 THEN 'Terça-feira'
			WHEN 3 THEN 'Quarta-feira'
			WHEN 4 THEN 'Quinta-feira'
			WHEN 5 THEN 'Sexta-feira'
			WHEN 6 THEN 'Sábado'
			WHEN 7 THEN 'Domingo'
		END AS dia_semana
	-- Gera uma sequência de datas começando na menor data até a data atual, avançando em intervalos de 1 dia
	FROM generate_series(
			-- retorna a menor data registrada nos pedidos
			(SELECT MIN(placed_at)::DATE FROM orders),
			-- retorna a data atual
			CURRENT_DATE,
			-- intervalo de 1 dia
			INTERVAL '1 day'
		) AS t(data)
	),

-- Retorna o somatória das vendas diárias.
vendas_diarias AS (
	SELECT
		placed_at::DATE AS data,
		SUM(total) AS venda_diaria
	FROM orders
	WHERE channel = 'pos'
	GROUP BY placed_at::DATE
)

SELECT 
	c.dia_semana,
	-- Calcula a media de vendas
	AVG(COALESCE(v.venda_diaria, 0)) AS media_vendas
FROM calendario AS c
-- Retorna todas as datas com ou sem venda
LEFT JOIN vendas_diarias AS v
	ON c.data = v.data
GROUP BY 
	c.numero_dia_semana,
	c.dia_semana
ORDER BY
	c.numero_dia_semana
