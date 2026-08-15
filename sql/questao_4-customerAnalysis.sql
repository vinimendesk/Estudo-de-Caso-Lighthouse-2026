-- questao 4

WITH cliente_faturamento AS (
    SELECT
        customer_id,
        SUM(total) AS faturamento_total,
        COUNT(id) AS frequencia,
        SUM(total) / COUNT(id) AS ticket_medio
    FROM main.orders
    GROUP BY customer_id
),

cliente_categorias AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT p.category_id) AS diversidade_categorias
    FROM main.orders o
    INNER JOIN main.order_items oi
        ON oi.order_id = o.id
    INNER JOIN main.product_variants pv
        ON pv.id = oi.product_variant_id
    INNER JOIN main.products p
        ON p.id = pv.product_id
    GROUP BY o.customer_id
),

top_10 AS (
    SELECT
        cf.customer_id
    FROM cliente_faturamento cf
    INNER JOIN cliente_categorias cc
        ON cc.customer_id = cf.customer_id
    WHERE cc.diversidade_categorias >= 13
    ORDER BY
        cf.ticket_medio DESC,
        cf.customer_id ASC
    LIMIT 10
)

SELECT
    c.id AS category_id,
    c.name AS category_name,
    SUM(oi.quantity) AS quantidade_itens
FROM top_10 t
INNER JOIN main.orders o
    ON o.customer_id = t.customer_id
INNER JOIN main.order_items oi
    ON oi.order_id = o.id
INNER JOIN main.product_variants pv
    ON pv.id = oi.product_variant_id
INNER JOIN main.products p
    ON p.id = pv.product_id
INNER JOIN main.categories c
    ON c.id = p.category_id
GROUP BY
    c.id,
    c.name
ORDER BY
    quantidade_itens DESC;