-- Comando SQL utilizado plo DBaver.
SELECT
    (SELECT COUNT(*) FROM main.customers) +
    (SELECT COUNT(*) FROM main.orders) +
    (SELECT COUNT(*) FROM main.order_items) +
    (SELECT COUNT(*) FROM main.payments) AS total_linhas;